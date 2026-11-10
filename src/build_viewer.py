"""Build a single-page HTML viewer for all graphs of a Django version.

Usage:
    python src/build_viewer.py --versions 1.0

Reads  output/django-<version>/graphs.jsonl
Writes output/django-<version>/viewer.html   (open in a browser; needs internet for the
       Cytoscape.js / dagre scripts loaded from unpkg.com)

Left: searchable list of all functions (filter by file path or qualified name).
Right: the selected function's CFG (solid edges, top-down flowchart layout) and/or DFG
(dashed orange def->use edges labelled with the variable). The URL hash (#index) links
directly to a function.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Django __VERSION__ graphs</title>
<script src="https://unpkg.com/cytoscape@3.30.2/dist/cytoscape.min.js"></script>
<script src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"></script>
<script src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script>
<style>
 body{margin:0;font-family:Segoe UI,Arial,sans-serif;font-size:13px;display:flex;height:100vh}
 #side{width:380px;border-right:1px solid #ccc;display:flex;flex-direction:column}
 #side input{margin:8px;padding:6px;font-size:13px}
 #count{margin:0 8px 4px;color:#666}
 #list{overflow-y:auto;flex:1}
 .item{padding:3px 8px;cursor:pointer;border-bottom:1px solid #f0f0f0}
 .item:hover{background:#eef4ff}.item.sel{background:#d6e4ff}
 .item .q{font-weight:600}.item .f{color:#777;font-size:11px}
 .err{color:#c00}
 #main{flex:1;display:flex;flex-direction:column}
 #bar{padding:6px 10px;border-bottom:1px solid #ccc}
 #bar label{margin-right:12px}
 #info{color:#333;margin-top:4px}
 #cy{flex:1}
</style></head><body>
<div id="side">
 <input id="q" placeholder="filter: file path or Class.method  (e.g. models/base.py save)">
 <div id="count"></div><div id="list"></div>
</div>
<div id="main">
 <div id="bar">
  <b>Django __VERSION__</b> &nbsp;
  <label><input type="radio" name="mode" value="both" checked> CFG + DFG</label>
  <label><input type="radio" name="mode" value="cfg"> CFG only</label>
  <label><input type="radio" name="mode" value="dfg"> DFG only</label>
  <div id="info">Select a function on the left.</div>
 </div>
 <div id="cy"></div>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const G = JSON.parse(document.getElementById('data').textContent);
const listEl = document.getElementById('list'), countEl = document.getElementById('count');
const KIND_COLOR = {ENTRY:'#9be29b', EXIT:'#f3a3a3', if:'#ffe08a', elif:'#ffe08a',
  for:'#a8d8ff', while:'#a8d8ff', try:'#e0c8ff', except:'#e0c8ff', finally:'#e0c8ff',
  with:'#c8f0e8', return_statement:'#ffc9a8', raise_statement:'#ffb0b0'};
let current = -1, cy = null;

function renderList(filter){
  const terms = filter.toLowerCase().split(/\s+/).filter(Boolean);
  listEl.innerHTML = ''; let n = 0; const frag = document.createDocumentFragment();
  G.forEach((g, i) => {
    const hay = (g.filepath + ' ' + g.qualname).toLowerCase();
    if (terms.some(t => !hay.includes(t))) return;
    n++;
    const d = document.createElement('div'); d.className = 'item' + (i === current ? ' sel' : '');
    d.innerHTML = '<div class="q' + (g.has_parse_error ? ' err' : '') + '">' + esc(g.qualname) +
      '</div><div class="f">' + esc(g.filepath) + ':' + g.line_start + '</div>';
    d.onclick = () => { location.hash = i; };
    frag.appendChild(d);
  });
  listEl.appendChild(frag);
  countEl.textContent = n + ' of ' + G.length + ' functions';
}
function esc(s){ return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function mode(){ return document.querySelector('input[name=mode]:checked').value; }

function show(i){
  const g = G[i]; if (!g) return; current = i;
  renderList(document.getElementById('q').value);
  const els = [];
  g.nodes.forEach(n => {
    let lab = (n.kind === 'ENTRY' || n.kind === 'EXIT') ? n.kind : ('L' + n.line + ': ' + n.text);
    if (n.kind === 'ENTRY' && n.defs.length) lab += '\nparams: ' + n.defs.join(', ');
    els.push({group:'nodes', data:{id:'n'+n.id, label:lab, color:KIND_COLOR[n.kind] || '#eeeeee',
      tip:'defs: ' + n.defs.join(', ') + '\nuses: ' + n.uses.join(', ')}});
  });
  const m = mode();
  if (m !== 'dfg') g.cfg_edges.forEach((e, k) => els.push({group:'edges', classes:'cfg',
      data:{id:'c'+k, source:'n'+e[0], target:'n'+e[1], label:e[2]}}));
  if (m !== 'cfg') g.dfg_edges.forEach((e, k) => els.push({group:'edges', classes:'dfg',
      data:{id:'d'+k, source:'n'+e[0], target:'n'+e[1], label:e[2]}}));
  // layout always uses CFG edges so node positions stay the same across modes
  const layoutEdges = g.cfg_edges.map((e, k) => ({group:'edges', classes:'layout',
      data:{id:'l'+k, source:'n'+e[0], target:'n'+e[1]}}));
  if (cy) cy.destroy();
  cy = cytoscape({container: document.getElementById('cy'), elements: els.concat(layoutEdges),
    wheelSensitivity: 0.3,
    style: [
      {selector:'node', style:{'shape':'round-rectangle', 'background-color':'data(color)',
        'border-width':1, 'border-color':'#888', 'label':'data(label)', 'text-wrap':'wrap',
        'text-max-width':340, 'font-size':10, 'font-family':'Consolas, monospace',
        'text-valign':'center', 'padding':6,
        'width': n => Math.min(360, 6.2 * Math.max(...n.data('label').split('\n').map(s => s.length)) + 16),
        'height': n => 14 * n.data('label').split('\n').length + 8}},
      {selector:'edge', style:{'curve-style':'bezier', 'target-arrow-shape':'triangle',
        'arrow-scale':0.8, 'width':1.4, 'label':'data(label)', 'font-size':9,
        'text-background-color':'#fff', 'text-background-opacity':0.8}},
      {selector:'edge.cfg', style:{'line-color':'#555', 'target-arrow-color':'#555'}},
      {selector:'edge.dfg', style:{'line-color':'#e67e22', 'target-arrow-color':'#e67e22',
        'line-style':'dashed', 'color':'#b35900'}},
      {selector:'edge.layout', style:{'display':'none'}}
    ]});
  cy.elements('node, edge.layout').layout({name:'dagre', rankDir:'TB', nodeSep:25, rankSep:35}).run();
  cy.fit(undefined, 20);
  cy.on('mouseover', 'node', ev => { document.getElementById('info').textContent =
      base + '   |   ' + ev.target.data('tip').replace('\n', '   '); });
  cy.on('mouseout', 'node', () => { document.getElementById('info').textContent = base; });
  const base = g.qualname + '  (' + g.filepath + ':' + g.line_start + '-' + g.line_end + ')   ' +
    g.nodes.length + ' nodes, ' + g.cfg_edges.length + ' CFG edges, ' + g.dfg_edges.length +
    ' DFG edges' + (g.free_vars.length ? ', free vars: ' + g.free_vars.join(', ') : '') +
    (g.has_parse_error ? '   [PARSE ERROR]' : '');
  document.getElementById('info').textContent = base;
}
document.getElementById('q').addEventListener('input', e => renderList(e.target.value));
document.querySelectorAll('input[name=mode]').forEach(r => r.onchange = () => { if (current >= 0) show(current); });
window.addEventListener('hashchange', () => show(parseInt(location.hash.slice(1))));
renderList('');
if (location.hash) show(parseInt(location.hash.slice(1)));
</script></body></html>
"""

KEEP = ("filepath", "qualname", "line_start", "line_end", "has_parse_error",
        "cfg_edges", "dfg_edges", "free_vars")
NODE_KEEP = ("id", "kind", "line", "text", "defs", "uses")


def build(version):
    out = OUTPUT / f"django-{version}"
    src = out / "graphs.jsonl"
    if not src.exists():
        raise SystemExit(f"missing {src}; run src/build_graphs.py --versions {version} first")
    graphs = []
    with open(src, encoding="utf8") as fh:
        for line in fh:
            g = json.loads(line)
            rec = {k: g[k] for k in KEEP}
            rec["nodes"] = [{k: n[k] for k in NODE_KEEP} for n in g["nodes"]]
            graphs.append(rec)
    graphs.sort(key=lambda g: (g["filepath"], g["line_start"]))
    data = json.dumps(graphs, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.replace("__VERSION__", version).replace("__DATA__", data)
    (out / "viewer.html").write_text(html, encoding="utf8")
    print(f"[done] {out / 'viewer.html'} ({len(graphs)} functions, {len(html) / 1e6:.1f} MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versions", nargs="+", required=True)
    for v in ap.parse_args().versions:
        build(v)


if __name__ == "__main__":
    main()
