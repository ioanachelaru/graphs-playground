# GraphCodeBERT method embeddings

Frozen [GraphCodeBERT](https://arxiv.org/abs/2009.08366) (`microsoft/graphcodebert-base`) embeddings, one vector per method. Each method is encoded from its code tokens and its variable-level data flow.

The run mirrors the method-level CodeBERT pipeline in [hria-sdp-methodlevel-codebert](https://github.com/anamariabriciu/hria-sdp-methodlevel-codebert):

- same input CSVs (`data/<project>/<project>-<version>_with_ids.csv`);
- same `instance_id` order;
- masked mean pooling, no normalisation;
- same output layout.

## Files

| Path | What it is |
|---|---|
| `embed.py` | The embedding script |
| `gcb_parser/` | Data-flow extraction (`DFG.py`, `utils.py`) copied from Microsoft's [CodeBERT repo](https://github.com/microsoft/CodeBERT/tree/master/GraphCodeBERT/clonedetection/parser), MIT licence (`gcb_parser/LICENSE`) |
| `embeddings/<project>/<version>/embeddings.npy` | `N × 768` float32, rows in the order of `ids.json` |
| `embeddings/<project>/<version>/ids.json` | `instance_id` per row (identical to the CodeBERT run) |
| `embeddings/<project>/<version>/input_stats.csv` | Per method: code sub-tokens, data-flow nodes, truncation, parse/extraction flags, label |
| `embeddings/<project>/<version>/manifest.json` | Settings, counts and timings for the version |

## How the input is built

The input follows Microsoft's official clone-detection code:

- Settings are `code_length=512` and `data_flow_length=128`.
- **Code tokens:** up to 509.
- **Data-flow nodes:** up to 128. They take position id 0, so they don't use up the code-token budget.
- **Attention:** a graph-guided mask lets each data-flow node see only its own code tokens and the variables it comes from.

Differences from the CodeBERT run:

1. Comments and docstrings are removed before encoding. This is GraphCodeBERT's official preprocessing.
2. Mean pooling covers all non-padding positions: code tokens, `<s>`, `</s>` and the data-flow nodes.
3. `transformers` 5 no longer accepts the 3-D mask, so it is passed as the equivalent additive 4-D mask.

**Checks:**
- For a method without data flow, the output equals a plain forward pass (max diff 7e-7).
- Batched and single-method results are identical.

## Run

Use an environment with `torch`, `transformers`, `pandas`, `tree-sitter`, `tree-sitter-python` and `tree-sitter-java`.

```bash
python graphcodebert/embed.py \
  --data-dir ../hria-sdp-methodlevel-codebert/data \
  --project django --versions 4.2 5.0 \
  --model microsoft/graphcodebert-base   # or a local folder with the model files
```

Versions that already have output are skipped unless `--overwrite` is given.

## Django 4.2 pilot

| Item | Value |
|---|---|
| Methods | 8,817 |
| Methods with no data flow | 521 |
| Data-flow extraction failed | 28 |
| Code truncated at the token limit | 177: 12.3% of buggy vs 1.6% of clean methods |
| Embedding time on CPU (12 threads) | 23 min |
| Top-10 nearest-neighbour overlap with CodeBERT (1,000 sampled methods) | 0.25 |
