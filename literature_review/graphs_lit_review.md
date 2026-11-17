# Graph representations for software defect prediction

Graph representations of code have been used for defect prediction in two very different senses. Inter-module dependency graphs describe how files or classes relate. Intra-procedural program graphs (ASTs, control flow graphs, code property graphs) describe how a single unit of code computes. Both lines report gains over hand-crafted metrics. The strongest evidence, however, comes from studies that tightened the evaluation, and these show that much of the reported advantage shrinks or vanishes under realistic settings: forward-release prediction, de-duplicated data, realistic labels. For a cross-version study on Django and ActiveMQ, the most defensible contribution is therefore not another GNN architecture. It is a careful comparison of graph features against metric and text baselines under leakage-controlled cross-version evaluation, which the graph-based defect prediction literature has barely done.

## 1. Bottom line

1. **Representation evidence is real, defect-prediction evidence is weak.** Studies outside SDP that control for other factors show that explicit data-flow edges carry signal beyond syntax. In SDP itself, every graph model we read was evaluated on a few small PROMISE version pairs, with best-of-N or test-tuned settings, F1 as the main metric, and no variance. None of those evaluations removed duplicated or unchanged code.
2. **Graph gains shrink under realistic evaluation.** Network metrics beat code metrics under random splits, but the difference is no longer significant under forward-release or cross-project prediction ([Premraj & Herzig 2011](https://doi.org/10.1109/esem.2011.30)). In vulnerability detection, the graph component of strong models adds only about 2–6 F1 points, and much of the headline gain comes from resampling, function-level context or leakage ([Chakraborty et al. 2022](https://doi.org/10.1109/tse.2021.3087402); [Hin et al. 2022](https://doi.org/10.1145/3524842.3527949); [Ding et al. 2025](https://doi.org/10.1109/icse55347.2025.00038)).
3. **No study we found tests graph models for cross-version defect prediction with unchanged or duplicate code controlled for.** None compares CFG with DDG with CFG+DDG under such a protocol, and none uses Python on real release history. These three gaps are exactly where this project's Joern graphs, the Django and ActiveMQ releases, and the leakage question fit.

## 2. What was read

Five reading tracks covered 39 papers. **26 were read in full text, 12 only at abstract level, and 1 could not be found.** Some full texts were preprints rather than the final versions: Phan 2017, Dam 2019, Devign v1, ReVeal 2020, Allamanis 2019, Croft, PrimeVul, IVDetect and LineVD (arXiv), and Jimenez (author copy). Any statement about an abstract-only paper is **provisional**. The abstract-only papers are:

- Xu 2020, ACGDP, Gupta 2022, node2defect, GCN2defect, CFG2AT, MVHR-DP, SeDPGK
- DH-CNN, DeepLineDP, Yamaguchi 2014 (CPG)
- Liu 2024 (unchanged modules)

Zhou 2022 (IST) could not be found. Per-paper extraction notes, with table and section references for every number, are in `reading_notes/`:

| Track | Notes file |
|---|---|
| Dependency/network graphs | [network_graphs_notes.md](reading_notes/network_graphs_notes.md) |
| AST, token and CodeBERT SDP | [dl_ast_codebert_notes.md](reading_notes/dl_ast_codebert_notes.md) |
| GNNs on intra-procedural graphs | [gnn_intraprocedural_graphs_notes.md](reading_notes/gnn_intraprocedural_graphs_notes.md) |
| Graph SDP and foundations (CPG, GGNN, Devign, GraphCodeBERT) | [graph_sdp_foundations_notes.md](reading_notes/graph_sdp_foundations_notes.md) |
| Evaluation validity and leakage | [evaluation_validity_notes.md](reading_notes/evaluation_validity_notes.md) |

## 3. Dependency (inter-module) networks

[Zimmermann & Nagappan 2008](https://doi.org/10.1145/1368088.1368161) computed network centralities on a Windows Server 2003 dependency graph. They report higher recall than complexity metrics at similar precision. Escrow recall was 0.60 for network metrics versus 0.30 for complexity metrics (Table 3). However, their own correlations show complexity metrics at least as strongly associated with defects (Table 4: TotalLines ρ = .516 vs. network up to .466). The evaluation used a single proprietary release and 50 random 2/3–1/3 splits.

[Premraj & Herzig 2011](https://doi.org/10.1109/esem.2011.30) is the most informative paper in this track. They replicated the setup on JRuby, ArgoUML and Eclipse. Under stratified random holdout, network metrics won everywhere. Under forward-release prediction (older release → next) and cross-project prediction, they found **no statistically significant difference** between network, code and combined metrics (Sec. VII–VIII). The caveat is low power: there are only three forward pairs, and "no significant difference" does not establish equivalence. [Tosun et al. 2009](https://doi.org/10.1145/1540438.1540446) point the same way. In the Eclipse cross-release Naive Bayes setup, network metrics alone were worse than code metrics on every averaged measure (Table 5, balance 59 vs. 66).

The learned-embedding successors do not engage with this result:

- **node2defect** ([Qu et al. 2018](https://doi.org/10.1145/3238147.3240469)) and **GCN2defect** ([Zeng et al. 2021](https://doi.org/10.1109/issre52982.2021.00020)) were assessed from abstracts only. Both report F-measure gains only, of 9.15% and 6.84–23.85% respectively.
- **DeMuVGN** ([Qiao et al. 2024](https://doi.org/10.48550/arxiv.2410.19550); v1 read, v2 is a withdrawal notice) uses ActiveMQ 5.0.0/5.1.0/5.2.0/5.3.0/5.8.0. These are **the same five releases as this project**. However, it evaluates only with transductive random node splits within a version, plus cross-project transfer, and never cross-version. Its developer view is built from defect-report assignees, which is a plausible label-leakage path. Its F1 values are inconsistent with its own recall values: HBase-0.95.0 reports recall 0.605 with F1 0.993, while the maximum F1 attainable at that recall is about 0.754.
- [Bryan & Moriano 2023](https://doi.org/10.1371/journal.pone.0284077) (JIT, also includes ActiveMQ) report +152% F1. Their MCC moves only from 0.5141 to 0.5316 (Table 4), on a single random, non-chronological split against a baseline quoted from another paper rather than re-run.
- [Cohen et al. 2022](https://doi.org/10.48550/arxiv.2212.14404) (abstract only) is the one cross-version network-embedding study found. It aligns class-dependency embeddings across 24 release pairs and reports +4.7% AUC. It does not mention duplicates or unchanged code.

**Takeaway.** The more sophisticated the graph model, the weaker the evaluation protocol. These are inter-module graphs, so they set expectations but do not answer the question for function-internal CFG/DDG structure.

## 4. AST, token and CodeBERT defect prediction (the "semantic features" baseline line)

[Wang et al. 2016](https://doi.org/10.1145/2884781.2884804) set the template that later papers reuse:

- AST-token sequences from PROMISE Java projects
- an older → newer version split (16 pairs), called "within-project"
- F1 compared against 20 PROMISE metrics

They report average F1 of 64.1 vs. 49.9 for metrics (ADTree, Table 2). Hyperparameters were chosen on evaluation pairs (Sec. 4.4), and only P/R/F1 are reported.

The same template carries through the follow-up papers:

- **DP-CNN** ([Li et al. 2017](https://doi.org/10.1109/qrs.2017.42)) reports average F1 0.608 vs. 0.524 for a single LR on metrics, over 7 pairs. It was tuned on 3 of those test pairs (Sec. IV-F). Its re-implemented DBN numbers for identical pairs differ from Wang's: lucene 2.0→2.2 gives 0.758 here vs. 65.1 in Wang.
- **Dam et al.** ([2019](https://doi.org/10.1109/msr.2019.00017), read via arXiv 1802.00921) report AUC 0.98. That result comes from random 10-fold CV on labels produced by a static analyser. On real PROMISE labels the same model reaches about 0.6 AUC, with F1 17% lower than DBN.
- **CodeBERT for SDP** ([Pan et al. 2021](https://doi.org/10.3390/app11114793)) tunes and early-stops on the test set and reports best-of-runs (Sec. 4.6, 5.1). Its only baseline is RANDOM. Its plain fine-tuned average F1 of 0.565 is below DP-CNN's 0.608 on the same 7 pairs. This cross-paper comparison is indicative only. Prompt variants that add words like "bug" or "error" improve results, which is consistent with shortcut learning.

The two surveys add context:

- [Giray et al. 2023](https://doi.org/10.1016/j.jss.2022.111537) covers 102 studies up to 2021. F1 is used in 68% of them, MCC in 20 studies and effort-aware measures in 13. Only 10 studies are cross-version, and only 11% of studies share both data and scripts. CFG/PDG/DFG representations are rare.
- [Li et al. 2024](https://doi.org/10.1007/s10515-024-00424-1) is a position paper. It recommends multi-representation fusion and MCC/AUC with effort-aware metrics, but is silent on leakage.
- Two relevant papers were readable only from abstracts. **DH-CNN** ([Abdu et al. 2024](https://doi.org/10.1109/tr.2024.3354965)) fuses AST-word2vec with CFG+DDG-node2vec features, the closest design to this project. **DeepLineDP** ([Pornprasit & Tantithamthavorn 2023](https://doi.org/10.1109/tse.2022.3144348)) has a public dataset including the same 5 ActiveMQ releases, with an oldest-train / next-validation / rest-test protocol (per its README).

**Takeaway.** None of these papers mentions unchanged files between consecutive versions, even though the split places mostly identical code in train and test. Their absolute numbers are also biased by test-set tuning.

## 5. GNNs on intra-procedural program graphs for SDP

| Paper | Graph | Data / split | Headline vs. strongest baseline | Main problems |
|---|---|---|---|---|
| [Phan et al. 2017](https://doi.org/10.1109/ictai.2017.00019) | CFG over g++ **assembly** | CodeChef C/C++ submissions; one random 3:1:1 split | Acc. +1.2 to +12.4 pts over AST models (Table III) | Program-correctness task, not SDP; likely near-duplicate resubmissions |
| [Šikić et al. 2022](https://doi.org/10.1109/access.2022.3144598) | AST, 39 node types, one-hot, per file | 7 PROMISE pairs, N → N+1 | Mean AUC 0.68 vs. LR 0.63/RF 0.61; F1 0.61 vs. 0.51/0.48 (Table 4) | RF AUC 0.50 ± 0.00 on xerces (under-configured); SOTA numbers copied; type-only features make unchanged files identical across versions |
| [Zhao et al. 2021 (MFGNN)](https://doi.org/10.1016/j.jss.2021.111108) | Inter-procedural CFG over Jimple/LLVM IR + reaching-def data-flow, 7 edge types, GAT | 14 PROMISE pairs, cross-version | F1 52.9 / AUC 71.5 vs. RF 46.4 / 68.2 (Table 4) | Best-of-N for all methods, no variance; 1,395 files dropped (Soot failures) |
| [Wang et al. 2023 (BugPre)](https://doi.org/10.1007/s40747-022-00848-w) | Per-method AST + control-flow + def/use edges, GCN | PROMISE 6 projects / 20 releases, cross-version | Avg F1 0.672 vs. 0.499 (Table 9) | Test set = changed/impacted functions only, but baselines see whole releases; method graphs mapped to file labels; no code |
| [Gupta et al. 2022](https://doi.org/10.1109/access.2022.3213844) *(abstract)* | Python CFG, cognitive-weight node features, GCN | 320 student programs | "outperformed" NB/DT/SVM/RF | Only Python CFG-SDP paper found; toy dataset |
| [Xu et al. 2020](https://doi.org/10.1109/tr.2020.3040191), [ACGDP](https://doi.org/10.1109/tr.2022.3161581) *(abstract)* | AST subtrees / augmented CPG | unknown | no numbers | Graph regions selected using fix or defect-type information, a potential label-leakage path |
| [CFG2AT 2024](https://doi.org/10.1109/tr.2024.3503688), [MVHR-DP 2024](https://doi.org/10.1109/tr.2024.3393415), [SeDPGK 2024](https://doi.org/10.1016/j.infsof.2024.107510) *(abstract)* | CFG + attention; dependency hypergraph; program graph, semi-supervised | WPDP/CVDP/CPDP | CFG2AT (WPDP): +7.09–12.80% F1, +1.30–4.15% AUC, +6.78–17.54% MCC; relative gains only | Splits and duplicate handling unknown; MVHR-DP code is public |

The table leads to four conclusions:

1. The read SDP papers show graph models beating *weak* metric baselines by about 3–7 AUC points.
2. Not one of them reports MCC with variance across seeds, runs a statistical test against a tuned metric model, or compares against CodeBERT or doc2vec under the same split.
3. Only one paper, BugPre, restricts its test set to changed functions, and it does so for efficiency, not validity, which makes its baseline comparison unequal.
4. No paper pools per-function graphs into file labels in a documented way, and none uses function-level labels.

## 6. Foundations and what the ablations say about edge types

- **Code property graph** ([Yamaguchi et al. 2014](https://doi.org/10.1109/sp.2014.44), abstract only) is the AST+CFG+PDG data model that Joern implements. It is the representation this project already exports.
- **Typed program graphs + GGNN** ([Allamanis et al. 2018](https://arxiv.org/abs/1711.00740)): with syntax edges only, VarMisuse accuracy drops from 85.5 to 55.3 (Table 2), so semantic (data-flow) edges carry most of the signal. Accuracy drops from 85.5 (seen projects) to 78.2 (unseen projects), a project-leakage effect of 7–10 points. The paper reports that GCN underperformed GGNN.
- **Devign** ([Zhou et al. 2019](https://arxiv.org/abs/1909.03496), v1) builds Joern graphs (AST + CFG + three data-flow edge types) for function-level vulnerability detection. On the combined dataset, the composite graph scores F1 73.26 vs. CFG-only 71.27, i.e. single edge types come within about 1–2 points (Table 2). On Linux, Metrics+XGBoost reaches F1 79.14 vs. Devign's 84.97. Evaluation uses a random split with no de-duplication. Functions with more than 500 nodes were removed.
- **GraphCodeBERT** ([Guo et al. 2021](https://arxiv.org/abs/2009.08366)) adds a variable-level data-flow graph to a pre-trained transformer. Without data flow, code-search MRR falls from 0.713 to 0.693 (Table 5). Gains over CodeBERT are about 0.5–2 points. It supports Python and Java, which makes it the natural "pre-trained + DDG" baseline.
- **Vulnerability-detection GNN ablations**:
  - ReVeal (GGNN): removing the GGNN costs about 2 F1 points (41.25 → 39.09), SMOTE is worth about 19, and SVM on the same embeddings scores 39.85.
  - LineVD (Joern PDG): function-level gating moves F1 from 0.129 to 0.296; GAT over the PDG adds 0.064 on top; GCN over the same graph is worse than no GNN; data-dependence edges beat control-dependence only.
  - IVDetect: adding control then data dependencies raises AUC from 0.83 to 0.85 to 0.90. This is the strongest pro-graph evidence, but it comes from random, non-de-duplicated splits in a single run ([Li et al. 2021](https://doi.org/10.1145/3468264.3468597)).

**Consistent lessons for a GNN on the Joern graphs:**

1. Node content matters at least as much as edges. In MFGNN, replacing bag-of-words with AST-subtree node content raised accuracy from 63.8 to 71.5 (Table 7).
2. Data-flow edges help more than control-flow edges in LineVD and Allamanis. MFGNN's ablation found CFG-only better than DFG-only, so this should be tested rather than assumed.
3. Use typed edges with per-type messages (GGNN, R-GCN or GAT). Plain GCN repeatedly underperforms.
4. Always include a no-message-passing ablation (same node features, pooled), because the graph's own contribution is often small.

## 7. Evaluation validity: how much the protocol moves the numbers

- **Label timing.** In [Jimenez et al. 2019](https://doi.org/10.1145/3338906.3338941), vulnerability predictors drop from MCC 0.77/0.65/0.43 to 0.08/0.22/0.10 (Linux/OpenSSL/Wireshark) when training labels are restricted to what was known at release time. This matters for us: bug labels for older releases must not use fixes discovered after the test release.
- **Duplication.** [Allamanis 2019](https://doi.org/10.1145/3359591.3359735) measures 5–51% relative inflation from cross-set duplicates on code-ML tasks (Tables 3–4). He predicts that duplication can reorder models, because higher-capacity models memorise more. [Croft et al. 2023](https://doi.org/10.1109/icse48619.2023.00022) report MCC drops of 0–82% when test duplicates are removed (Table V). Most of those duplicates come from "updated code" across versions of the same repository. They also find 20–71% of vulnerable labels wrong. [Ding et al. 2025 (PrimeVul)](https://doi.org/10.1109/icse55347.2025.00038) find 0.6–18.9% exact-copy test leakage. Combining clean labels, de-duplication, a chronological commit-grouped split and a ~1:32 class ratio drops StarCoder2 from F1 68.26 to 3.09.
- **Unchanged modules in cross-version WPDP.** [Liu et al. 2024](https://doi.org/10.1002/smr.2715) (abstract only; 481 versions, 62 projects) report that removing unchanged modules significantly changes absolute performance but only slightly changes model rankings. This contrasts with Allamanis' prediction. The likely reason is that Liu studied classical learners on metrics, so the question remains open for CodeBERT and GNN models.
- **Strong simple baselines.** In [Zeng et al. 2021](https://doi.org/10.1145/3460319.3464819), a one-feature LR on lines added beats DeepJIT and CC2Vec: within-project AUC 0.7246 vs. 0.7065, cross-project 0.7246 vs. 0.6808. The released DeepJIT code effectively reduced code changes to placeholders.

## 8. Relevance to this project

The project already has the ingredients most papers lack:

- per-function Joern CPGs (CFG + DDG on a shared node set) for 22 Django and 5 ActiveMQ releases
- previous doc2vec, CodeBERT and SonarQube baselines on the same data
- an explicit research question about leakage from unchanged or duplicate code

That combination is not covered by any paper reviewed here. One concrete point of comparability: the ActiveMQ releases match the DeMuVGN and DeepLineDP datasets.

**Recommended protocol (synthesised from the papers above):**

1. **Splits.** Use forward-in-time release splits only: train on releases ≤ N, validate on N+1, test on N+2 (as in DeepLineDP). Never tune or early-stop on the test release.
2. **Labels.** Use as-of-release labels where possible (Jimenez). Document how function-level labels are joined to Joern methods (file + line-range overlap), and how files without functions are handled.
3. **Leakage control.** Classify every test function as *new*, *changed* or *unchanged*. Use normalised-code hash plus WL graph hash for exact duplicates, and Allamanis-style token Jaccard for near-duplicates. Report all metrics on (a) all functions and (b) new + changed functions only. Resolve label-conflicting duplicates (Croft).
4. **Baselines on the identical split.**
   - LOC-only, plus a kNN/memorisation probe that copies the label of the nearest training graph (Zeng; Allamanis)
   - SonarQube metrics with tuned RF/LR
   - doc2vec and CodeBERT
   - GraphCodeBERT as the pre-trained + data-flow baseline
5. **Graph ablations.** Hold node features fixed and vary only the edge sets: none, CFG only, DDG only, CFG + DDG.
6. **Graph models.** Start with cheap ones (graph metrics, WL / graph2vec embeddings), then a typed-edge GNN (R-GCN, GGNN or GAT) whose nodes carry node type plus subtoken or CodeBERT statement embeddings. Cap and report oversized graphs.
7. **Metrics.** MCC, ROC-AUC, PR-AUC and effort-aware measures (Popt, recall@20% LOC, IFA), with multiple seeds, spread, and paired statistical tests across the many available release pairs (far more than the 3–16 pairs used in the literature).
8. **The key analysis.** Check whether the ranking of metric, text-embedding and graph models changes between the all-functions and changed-only test sets. This tests Allamanis' prediction against Liu et al.'s finding, and no paper in this review has done it.

## 9. Limitations of this review

- 12 of 39 papers were assessed from abstracts only, mostly closed-access IEEE TR, IST and ASE papers. These include CFG2AT, MVHR-DP, DH-CNN and DeepLineDP, which are among the closest to this project. Their PDFs would let these entries be completed.
- Several papers were read as preprints, and the final versions may differ.
- Paper selection started from keyword searches plus citation chasing; it is not a systematic review.
- Numbers are as reported in the papers. Internal inconsistencies found by the readers are flagged in the notes, e.g. DeMuVGN F1/recall, Jimenez 1,898 vs. 1,593, LineVD duplicated table rows and Allamanis' VarNaming text vs. table.
