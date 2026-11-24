# Method-level defect prediction: in-depth review (focus: cross-version and graph-based)

*Based on 55 paper extractions by five reading tracks. Each number below comes from the paper's tables or text, with the section given in the reading notes. Entries marked (A) were read from the abstract only and are provisional. Entries marked (P) were read from a preprint or author copy.*

## 1. Bottom line

1. **There are almost no clean cross-version method-level studies.** Only [Pascarella et al. 2018](https://doi.org/10.1109/saner.2018.8330264) and [2020](https://doi.org/10.1016/j.jss.2019.110493) train on release r−1 and test on release r at method level, and they get **AUC 0.52–0.53**, i.e. close to chance (JSS Table 7). [Chowdhury et al. 2024](https://doi.org/10.1145/3640331) (P) evaluates three time-aware scenarios on Shippey's data. In the cross-project scenario (i) precision is about 0.13 and F1 about 0.25. The release-based scenarios, which use all earlier releases to predict release x (ii/iii), do somewhat better but stay far below cross-validation (Fig. 2, Table 4).
2. **Strong method-level results come from random cross-validation.** [Giger et al. 2012](https://doi.org/10.1145/2372251.2372285) reach AUC 0.95 (Table 4), Pascarella's own cross-validation replication reaches F 0.80–0.86, and Mo et al. 2021 (A) report AUC 0.74–0.90. In each case the process metrics and the labels come from the same time window.
3. **No graph-based method-level model has a clean release-to-release evaluation:**
   - [BugPre](https://doi.org/10.1007/s40747-022-00848-w) predicts N→N+1 on function graphs (AST+CFG+data-flow, GCN). Its labels are PROMISE file labels, and it does not explain how they are mapped to functions.
   - [BiPDG-DP](https://doi.org/10.1002/smr.70115) (A) uses method-level PDGs, but its split is unknown.
   - [Yang et al. 2023](https://doi.org/10.1109/access.2023.3239266) (call-graph embeddings) uses random within-version splits.
   - Graph models that do use release splits work at file or line level ([LineFlowDP](https://doi.org/10.1007/s10664-023-10439-z), [DIDP](https://doi.org/10.32604/cmc.2024.057697)).
4. **No study at any granularity that we read removes methods that are unchanged between training and test releases.** The size of the issue has been measured at class level. On standard cross-version pairs, a median of 79% of next-version classes already exist in the previous version, and about 35% have identical feature vectors ([Onet-Marian & Hotea 2025](https://doi.org/10.5220/0013481700003928), Sec. 4.1). For those classes the model scores close to its training accuracy, while MCC is mostly negative on classes whose label flipped.
5. **The project's design (Joern CFG+DDG, method level, release N→N+1, unchanged/duplicate methods controlled, Python and Java) is not covered by any paper reviewed.**

## 2. Coverage

The five tracks were: method-level core, datasets and labels, graph-based method-level, line-level graphs, and cross-version methods. Together they produced 55 extractions; some papers were read in more than one track. About 30 were read in full or as preprints and about 25 from abstracts or secondary sources only.

The papers read from abstracts or secondary sources only are:

- **Method-level and graph-based:** Hata 2012, Mo 2021 (fields taken from Chowdhury 2024's re-analysis), Jász 2024, BiPDG-DP, FPGR, ESWA graph-code-semantics, DSA augmented-CPG.
- **Line-level:** DeepLineDP, GLANCE, LineDef, H-LineDef, the multi-relational GNN paper, GNNLineDef, SLDeep, BugsplorerPy.
- **Datasets and cross-version:** PyTraceBugs, Ahluwalia 2019, Liu 2024, Zhang 2016, Amasaki 2020, HALKP, TSTSS, Yang & Wen 2018, AVDP 2026.
- **Metadata only:** TFDP.

Four of the graph papers come from one group (F. Yang, P. Xiao, W. Zheng): Yang 2023, the method-call-sequence paper, DIDP and LineFlowDP; TFDP likely too, by author overlap. The graph evidence is therefore less independent than the paper count suggests.

Per-paper notes are in `reading_notes_method_level/`:

| Track | Notes |
|---|---|
| Method-level core | [method_level_core_notes.md](reading_notes_method_level/method_level_core_notes.md) |
| Datasets and labels | [method_level_data_labels_notes.md](reading_notes_method_level/method_level_data_labels_notes.md) |
| Graph-based method-level | [graph_method_level_notes.md](reading_notes_method_level/graph_method_level_notes.md) |
| Line-level (incl. graphs) | [line_level_notes.md](reading_notes_method_level/line_level_notes.md) |
| Cross-version methods | [cross_version_notes.md](reading_notes_method_level/cross_version_notes.md) |

## 3. Method-level prediction: how the protocol decides the result

| Study | Split | Labels | Headline |
|---|---|---|---|
| [Giger et al. 2012](https://doi.org/10.1145/2372251.2372285) | Random 10-fold, one snapshot | Bug counts from the same window as the change metrics | RF change metrics AUC .95, P .84, R .88. Code metrics only: AUC .72 (Table 4) |
| [Pascarella et al. 2018](https://doi.org/10.1109/saner.2018.8330264) / [2020](https://doi.org/10.1016/j.jss.2019.110493) | (1) Giger-style replication; (2) **release r−1 → r** | Methods changed in ReLink-linked fix commits between releases | Replication F .80 / AUC .72–.73. **Release-based AUC .52–.53**, F .60–.62 with precision about .71, which tracks the base rate. Textual, smell and developer features do not help significantly |
| [Chowdhury et al. 2024](https://doi.org/10.1145/3640331) (P) | Random CV vs. three time-aware scenarios; Shippey data: releases < x → x | Keyword fix commits; tangled fixes studied | CV is reproduced (F about .68–.72). Ferenc data, scenario i: precision ≤ about .37 for 80% of projects. Shippey data, scenario i (cross-project): precision about .13, F1 about .25. Release-based scenarios ii/iii: somewhat better but far below CV (Fig. 2, Table 4) |
| Mo et al. 2021 (A, via Chowdhury) | Within-project; no timing information | — | AUC .74–.90 (ActiveMQ .87). Cross-project re-evaluation is lower |
| [Ferenc et al. 2020 (BugHunter)](https://doi.org/10.1016/j.jss.2020.110691) (P) | Random 10-fold over before- and after-fix snapshots | Fix commits, release-independent | Method level RF F .63 (Table 16) |
| [Friesen et al. 2025](https://doi.org/10.48550/arxiv.2511.22726) (P) | Leave-one-project-out, features at method creation, labels from the next 5 years | Three label definitions | Prevalence 0.04%–6.63% depending on the definition (Table 1). Precision < .25 for about 75% of projects |
| [Zenodo 2026 package](https://doi.org/10.5281/zenodo.20986662) (paper not found) | Commit-time 70/30 cut | Labels untangled with an LLM | MCC about .16–.26, PR-AUC about .15–.21 (results files) |
| [Niedermayr et al. 2019](https://doi.org/10.7717/peerj-cs.187) | Random 10-fold and leave-one-project-out | — | An inverse task (finding "too trivial to test" methods) works: fault density in the low-risk set is reduced by a median factor of 5.7 |

Four mechanisms inflate method-level results:

1. Process metrics computed over the same window as the labels.
2. Random CV that mixes releases, or the future with the past. Ferenc et al. (Array 2020) explicitly accept this.
3. Unchanged or identical methods appearing on both sides of the split. No study handles this. The Zenodo package de-duplicates embeddings by content hash, which itself shows that identical method bodies recur.
4. Tuning on test data, e.g. Chowdhury's RQ4 oracle subset selection.

## 4. Graph-based method- and fine-grained-level work

| Paper | Graph and model | Granularity / split | Result vs. strongest baseline | Main issues |
|---|---|---|---|---|
| [BugPre](https://doi.org/10.1007/s40747-022-00848-w) | AST+CFG+data-flow+call edges (JavaParser), GCN | Function; **N→N+1**; test = changed/impacted functions only | Avg F1 .672 vs. WGNCS .499 (Table 9, copied baselines) | File labels used for functions; F1/P/R only; no variance |
| [BiPDG-DP](https://doi.org/10.1002/smr.70115) (A) | Method PDG (control+data) guiding Transformer attention | Method; split unknown (probably the Line-DP releases) | +11.8–35.7% (non-effort), +14.2–218.5% (effort-aware), relative | Unverified |
| [Yang et al. 2023 (MCN)](https://doi.org/10.1109/access.2023.3239266) | Method call graph, node2vec + centrality, RF | Method; random within-version | AUC +2.5–6.7%, MCC +13–178% over code metrics | Transductive embeddings; cross-version left as future work |
| [Method-call sequence (TSASS) 2022](https://doi.org/10.1155/2022/4311548) | Call graph used to build sequences, Transformer | Method/sequence; random | MAE .095 vs .158 | Resamples before splitting; tuned on evaluation projects |
| [FINDGATE 2023](https://doi.org/10.1109/qrs60937.2023.00017) | AST+CFG+DFG+call graph as attention masks | Function (Big-Vul), random | F1 .95 vs. LineVul .92 | Vulnerability data; graph-only ablation much weaker |
| [DIDP 2024](https://doi.org/10.32604/cmc.2024.057697) | Statement PDG, information-bottleneck GNN | File N→N+1 and statement level | File AUC .685 vs. DHCNN .730 (n.s.); statement Recall@20%LOC .377 vs. LineVD .308 | Does not win cross-version at file level |
| [LineFlowDP 2024](https://doi.org/10.1007/s10664-023-10439-z) | Refined PDG, R-GCN + GNNExplainer | File/line; oldest release → later (ActiveMQ 5.0.0 train, 5.1.0 val, 5.2.0/5.3.0/5.8.0 test) | File AUC .800 vs. DeepLineDP .816 (same rank); ActiveMQ AUC .80–.87 (Table 2) | Baselines with balanced accuracy < .5 suggest a poor re-implementation; no GLANCE baseline |
| [Graph code semantics (ESWA 2025)](https://doi.org/10.1016/j.eswa.2025.129842) (A) | Method CFG and PDG (TinyPDG), CBOW + BiLSTM | Unknown | PDG > CFG | Unverified |

The pattern across this table:

- When the setting is harder (cross-version, a strong text baseline), graph gains are small or not significant.
- The pre-trained token signal dominates where it is tested (FINDGATE ablation).
- No paper isolates the graph's contribution against a non-graph model with the same node features.
- No paper uses Joern, and none uses Python on releases.

## 5. Line-level work: the nearest release-based benchmark

The Line-DP benchmark of [Wattanakriengkrai et al. 2022](https://doi.org/10.1109/tse.2020.3023177) covers 9 projects and 32 releases and **includes ActiveMQ 5.0.0–5.8.0, the releases this project uses**. Most line-level papers use it.

- **Splits:** Line-DP itself uses release k−1 → k. DeepLineDP and LineFlowDP train on the oldest release, validate on the second and test on the later ones.
- **Unchanged code is not controlled:** no paper read in full removes unchanged files or lines.
- **Label carry-over:** labels are based on affected versions, so a bug that spans releases k−1 and k marks the same unchanged code as defective in both. This leaks labels directly across the split (cross-version track, theme 4).
- **Simple baselines win:** the GLANCE heuristic ([Guo et al. 2023](https://doi.org/10.1145/3582572), A) matches or beats deep models ([Zhou et al. 2024](https://doi.org/10.1002/smr.2696)).
- **Metric bugs:** Zhou et al. found that DeepLineDP's evaluation script counted comment lines in the LOC denominator.

## 6. Cross-version defect prediction (CVDP) at file/class level

- **Data-selection and transfer methods.** These include [HALKP](https://doi.org/10.1109/saner.2018.8330210), [TSTSS](https://doi.org/10.1016/j.jss.2019.03.027), [AVDP](https://doi.org/10.1016/j.array.2026.101239), the "latest release is best" finding of [Amasaki 2020](https://doi.org/10.1007/s10664-019-09777-8), and the anchor alignment of [Cohen et al. 2022](https://doi.org/10.48550/arxiv.2212.14404). They make training data more similar to the test release by design. Given the overlap Onet-Marian & Hotea measured, their gains are confounded with memorising modules carried over unchanged.
- **Recurring protocol flaws:**
  - transductive use of test-release features (TSTSS, AVDP, KPCA, Cohen);
  - test-release labels used in training (HALKP's active learning, Kabir's drift detector);
  - configuration selected on test pairs (Cohen);
  - F1-only reporting.
- **A good protocol model** is [Bangash et al. 2020](https://doi.org/10.1007/s10664-020-09878-9): date-ordered buckets, a gap between training and testing so labels can mature, many split points, and F/AUC/MCC/G reported.
- **Label timing.** Most defects stay dormant for more than 20% of releases ([Ahluwalia et al. 2019](https://doi.org/10.1109/msr.2019.00019), A). Dormant defects cut recall by a median of about 90% relative. Dropping non-defective instances of the last training release recovers about 32% MCC ([Falessi et al. 2021](https://doi.org/10.1145/3467895), P, Tables 6 and 9).
- **Unchanged modules.** Removing them changes absolute scores significantly, but model rankings only slightly ([Liu et al. 2024](https://doi.org/10.1002/smr.2715), A).

## 7. Datasets with method-level labels

| Dataset | Language | Release-based? | Notes |
|---|---|---|---|
| ELFF ([Shippey et al. 2016](https://doi.org/10.1145/2961111.2962620)) | Java, 23 systems, multi-version | Yes, versions available | Link coverage about 41% on average (7.6–93.8%) |
| BugHunter ([Ferenc et al. 2020](https://doi.org/10.1016/j.jss.2020.110691)) | Java | No: before/after-fix snapshots | Random CV only |
| Chowdhury et al. 2024 | Java, 774,051 methods, 49 projects | Method histories | Basis of the LLM untangling work ([Opu et al. 2026](https://doi.org/10.1145/3793302.3793351), P) |
| [PyTraceBugs](https://doi.org/10.1109/apsec53868.2021.00022) (A) | Python | No | Traceback-exception snippets |
| Line-DP | Java, 32 releases incl. ActiveMQ | Yes | Line labels, from which method labels can be derived; affected-version carry-over (see §5) |

**No Python dataset has release-based method-level labels.**

## 8. Label noise at method level

- **Tangled fixes.** About 60% of fix commits touch more than one method, and over 15% touch at least 10 (Chowdhury, Fig. 4). Restricting positives to single-method fixes turns negligible metric differences into large ones (Table 6).
- **Positive-rate variation.** Depending on the label definition, the positive rate ranges from 0.04% to about 76% (Friesen Table 1; Pascarella 2020 Table 2). Results are not comparable without the definition and the base rate.
- **Metric choice under skew.** F-measure misleads when classes are imbalanced: Camel 1.0 has F .93–.95 with AUC .43–.49 ([Ferenc et al. 2020 SQJ](https://doi.org/10.1007/s11219-020-09515-0), Table 17).

## 9. Implications for this project

1. **Protocol.** Use release N → N+1 for every Django pair (24 releases) and every ActiveMQ pair (5 releases), optionally also N → N+2 with a gap release (Bangash). Report distributions over pairs with MCC, PR-AUC, ROC-AUC and effort-aware measures (Recall@20%LOC, IFA, Popt), across several seeds, with significance tests.
2. **Leakage strata.** Split each test release into new, modified and unchanged methods, identified by a normalised-body hash and a Joern graph hash rather than by metrics. Report the headline result on new + modified methods and on the label-flipped subset, and keep the unchanged stratum as a leakage diagnostic (as in Onet-Marian & Hotea). Also check whether model rankings change between strata (Liu 2024).
3. **Labels.**
   - State the label definition and the base rate per release.
   - Check sensitivity to single-method fixes vs. all fix-touched methods (Chowdhury).
   - Avoid affected-version carry-over onto unchanged code.
   - Treat the most recent releases as label-immature (Falessi).
   - Verify that the doc2vec-experiments labels and the Line-DP ActiveMQ labels agree.
4. **Baselines on the same split.**
   - size-only / GLANCE-style rules and a "trivial method" rule (Niedermayr);
   - code metrics (SonarQube), plus method age;
   - doc2vec and CodeBERT;
   - call-graph centrality / node2vec (MCN);
   - a graph-masked CodeBERT (FINDGATE / BiPDG-DP style).
5. **Graph ablations.** Hold node features fixed and vary only the structure: no edges, CFG only, DDG only, CFG+DDG. Train the graph encoder inductively on release N only, without per-release transductive embeddings.
6. **Comparability.** Report ActiveMQ results alongside the published file-level AUCs (LineFlowDP: .80–.87), keeping in mind that those results did not control for unchanged code.

## 10. Limitations

- About 25 of the 55 extractions are abstract-only. These include several closely related papers: BiPDG-DP, Hata 2012, Mo 2021, DeepLineDP, GLANCE, TSTSS and AVDP. PDFs would allow completing them.
- Chowdhury, BugHunter, Falessi, Opu and Friesen were read as preprints.
- Values shown only in figures are approximate.
- The 2026 Zenodo result comes from a replication package with no paper.
- Additional papers were found opportunistically, not through a systematic search.
