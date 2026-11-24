"""GraphCodeBERT method embeddings (code tokens + data flow), one vector per method.

Mirrors the colleague's CodeBERT pipeline (hria-sdp-methodlevel-codebert):
same input CSVs (<project>-<version>_with_ids.csv), same instance ids and order,
masked mean pooling, no L2 normalisation, output embeddings/<project>/<version>/
{embeddings.npy, ids.json}. Input construction follows Microsoft's official
GraphCodeBERT clone-detection code (code_length=512, data_flow_length=128):
up to 509 code tokens plus up to 128 data-flow nodes, nodes get position id 0
and a graph-guided attention mask.

Usage:
  python graphcodebert/embed.py --data-dir <hria repo>/data --out-dir graphcodebert/embeddings \
      --project django --versions 4.2
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from tree_sitter import Language, Parser
import tree_sitter_java as tsj
import tree_sitter_python as tsp
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gcb_parser import (DFG_java, DFG_python, index_to_code_token,  # noqa: E402
                        remove_comments_and_docstrings, tree_to_token_index)

MODEL = "microsoft/graphcodebert-base"
CODE_LENGTH, DFG_LENGTH = 512, 128
LANG = {"django": "python", "activemq": "java"}
PARSERS = {"python": (Parser(Language(tsp.language())), DFG_python),
           "java": (Parser(Language(tsj.language())), DFG_java)}


def extract_dataflow(code, lang):
    """Official GraphCodeBERT extract_dataflow; returns tokens, dfg, status flags."""
    stats = {"comments_stripped": True, "dfg_error": False}
    try:
        code = remove_comments_and_docstrings(code, lang)
    except Exception:
        stats["comments_stripped"] = False
    parser, dfg_fn = PARSERS[lang]
    root = parser.parse(bytes(code, "utf8")).root_node
    stats["parse_error"] = bool(root.has_error)
    tokens_index = tree_to_token_index(root)
    lines = code.split("\n")
    code_tokens = [index_to_code_token(x, lines) for x in tokens_index]
    index_to_code = {idx: (i, c) for i, (idx, c) in enumerate(zip(tokens_index, code_tokens))}
    try:
        dfg, _ = dfg_fn(root, index_to_code, {})
    except Exception:
        dfg, stats["dfg_error"] = [], True
    dfg = sorted(dfg, key=lambda x: x[1])
    keep = set()
    for d in dfg:
        if d[-1]:
            keep.add(d[1])
        keep.update(d[-1])
    return code_tokens, [d for d in dfg if d[1] in keep], stats


def build_features(code, lang, tok):
    """Official convert_examples_to_features for one function (unpadded)."""
    code_tokens, dfg, stats = extract_dataflow(code, lang)
    code_tokens = [tok.tokenize("@ " + x)[1:] if i != 0 else tok.tokenize(x)
                   for i, x in enumerate(code_tokens)]
    ori2cur = {-1: (0, 0)}
    for i in range(len(code_tokens)):
        ori2cur[i] = (ori2cur[i - 1][1], ori2cur[i - 1][1] + len(code_tokens[i]))
    flat = [y for x in code_tokens for y in x]
    stats["n_code_subtokens"] = len(flat)
    stats["n_dfg_nodes"] = len(dfg)
    flat = flat[:CODE_LENGTH + DFG_LENGTH - 3 - min(len(dfg), DFG_LENGTH)][:512 - 3]
    stats["code_truncated"] = len(flat) < stats["n_code_subtokens"]
    src = [tok.cls_token] + flat + [tok.sep_token]
    ids = tok.convert_tokens_to_ids(src)
    pos = [i + tok.pad_token_id + 1 for i in range(len(src))]
    dfg = dfg[:CODE_LENGTH + DFG_LENGTH - len(src)]
    stats["dfg_truncated"] = len(dfg) < stats["n_dfg_nodes"]
    ids += [tok.unk_token_id] * len(dfg)
    pos += [0] * len(dfg)
    rev = {x[1]: i for i, x in enumerate(dfg)}
    dfg_to_dfg = [[rev[i] for i in x[-1] if i in rev] for x in dfg]
    dfg_to_code = [(ori2cur[x[1]][0] + 1, ori2cur[x[1]][1] + 1) for x in dfg]
    return ids, pos, dfg_to_code, dfg_to_dfg, stats


def collate(feats, pad_id):
    """Pad a batch and build the graph-guided attention mask (official __getitem__)."""
    L = max(len(f[0]) for f in feats)
    B = len(feats)
    ids = torch.full((B, L), pad_id, dtype=torch.long)
    pos = torch.full((B, L), pad_id, dtype=torch.long)
    mask = torch.zeros((B, L, L), dtype=torch.bool)
    for b, (i, p, d2c, d2d, _) in enumerate(feats):
        n = len(i)
        ids[b, :n] = torch.tensor(i)
        pos[b, :n] = torch.tensor(p)
        node_index = sum(x > 1 for x in p)
        mask[b, :node_index, :node_index] = True
        for k, t in enumerate(i):
            if t in (0, 2):  # <s>, </s> attend to everything
                mask[b, k, :n] = True
        for k, (a, c) in enumerate(d2c):
            if a < node_index and c < node_index:
                mask[b, k + node_index, a:c] = True
                mask[b, a:c, k + node_index] = True
        for k, nodes in enumerate(d2d):
            for a in nodes:
                if a + node_index < n:
                    mask[b, k + node_index, a + node_index] = True
    return ids, pos, mask


@torch.inference_mode()
def embed_batch(model, ids, pos, mask):
    """Official GraphCodeBERT forward (node embeddings = mean of their code tokens)."""
    nodes_mask = pos.eq(0)
    token_mask = pos.ge(2)
    emb = model.embeddings.word_embeddings(ids)
    n2t = nodes_mask[:, :, None] & token_mask[:, None, :] & mask
    n2t = n2t / (n2t.sum(-1) + 1e-10)[:, :, None]
    avg = torch.einsum("abc,acd->abd", n2t, emb)
    emb = emb * (~nodes_mask)[:, :, None] + avg * nodes_mask[:, :, None]
    # transformers>=5 no longer expands a 3D mask; pass the equivalent additive 4D mask
    # (what older versions built from GraphCodeBERT's 3D mask internally).
    add_mask = (~mask[:, None, :, :]).to(emb.dtype) * torch.finfo(emb.dtype).min
    hidden = model(inputs_embeds=emb, attention_mask=add_mask, position_ids=pos,
                   token_type_ids=torch.zeros_like(pos)).last_hidden_state
    valid = pos.ne(1).float()[:, :, None]  # all non-padding positions (code + nodes)
    return (hidden * valid).sum(1) / valid.sum(1).clamp(min=1e-9)


def run_version(project, version, data_dir, out_dir, tok, model, batch_size, overwrite):
    out = Path(out_dir) / project / version
    if (out / "embeddings.npy").exists() and not overwrite:
        print(f"skip {project}-{version} (exists)")
        return
    df = pd.read_csv(Path(data_dir) / project / f"{project}-{version}_with_ids.csv")
    codes = df["source_code"].fillna("").astype(str).tolist()
    ids_list = df["instance_id"].astype(str).tolist()
    lang = LANG[project]
    t0 = time.time()
    feats = [build_features(c, lang, tok) for c in codes]
    t_feat = time.time() - t0
    order = sorted(range(len(feats)), key=lambda k: len(feats[k][0]))  # length-bucketed batches
    vecs = np.zeros((len(feats), model.config.hidden_size), dtype=np.float32)
    t1 = time.time()
    for s in range(0, len(order), batch_size):
        idx = order[s:s + batch_size]
        ids, pos, mask = collate([feats[k] for k in idx], tok.pad_token_id)
        vecs[idx] = embed_batch(model, ids, pos, mask).numpy()
        if (s // batch_size) % 20 == 0:
            print(f"  {project}-{version}: {s + len(idx)}/{len(order)}", flush=True)
    t_emb = time.time() - t1
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "embeddings.npy", vecs)
    (out / "ids.json").write_text(json.dumps(ids_list), encoding="utf-8")
    st = pd.DataFrame([f[4] for f in feats])
    st.insert(0, "instance_id", ids_list)
    st.insert(1, "label", df["label"].tolist())
    st.to_csv(out / "input_stats.csv", index=False)
    manifest = {
        "project": project, "version": version, "model": MODEL, "n_methods": len(feats),
        "code_length": CODE_LENGTH, "data_flow_length": DFG_LENGTH,
        "pooling": "mean over all non-padding positions (code tokens, <s>, </s>, data-flow nodes)",
        "normalized": False, "comments_and_docstrings": "removed (official GraphCodeBERT preprocessing)",
        "n_code_truncated": int(st.code_truncated.sum()), "n_dfg_truncated": int(st.dfg_truncated.sum()),
        "n_no_dataflow": int((st.n_dfg_nodes == 0).sum()), "n_dfg_error": int(st.dfg_error.sum()),
        "n_parse_error": int(st.parse_error.sum()), "n_comment_strip_failed": int((~st.comments_stripped).sum()),
        "seconds_features": round(t_feat, 1), "seconds_embedding": round(t_emb, 1),
        "torch": torch.__version__, "threads": torch.get_num_threads(),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent / "embeddings"))
    ap.add_argument("--project", required=True, choices=sorted(LANG))
    ap.add_argument("--versions", nargs="+", required=True)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--model", default=MODEL,
                    help="HF model id or local folder with the graphcodebert-base files")
    a = ap.parse_args()
    if a.threads:
        torch.set_num_threads(a.threads)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModel.from_pretrained(a.model, attn_implementation="eager").eval()
    for v in a.versions:
        run_version(a.project, v, a.data_dir, a.out_dir, tok, model, a.batch_size, a.overwrite)


if __name__ == "__main__":
    main()
