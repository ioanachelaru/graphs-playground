# Graph-based method-level defect prediction: reading notes (track 'Graph method-level')

Scope: 10 assigned papers. Access: 5 read in full, 4 abstract/landing page only, 1 metadata only (TFDP). Statements about the abstract-only papers are provisional. Section/table/figure references point to the source paper.

## Summary table

| Paper | Access | Granularity | Cross-version (method level)? | Graph | Split |
|---|---|---|---|---|---|
| BugPre 2023 | full | function (file labels) | nominal N->N+1; file-level labels | AST+CFG+data-flow, GCN | release N -> N+1, changed funcs only |
| BiPDG-DP 2026 | abstract | method | unknown (likely 32-release benchmark) | method PDG, masked attention | unknown |
| Yang MCN 2023 | full | method | no | call graph, node2vec+metrics, RF | random 2:1 x30 |
| TSASS 2022 | full | call sequence/method | no | call graph -> sequences | random 4:1 |
| FINDGATE 2023 | full | function + line (vuln) | no | AST+CFG+DFG+call, masked attention | random 8:1:1 Big-Vul |
| DIDP 2025 | full | file + statement | file/line: yes; method: no | file PDG + Doc2vec, IB-GNN | release-ordered |
| TFDP 2026 | none | unknown | unknown | AST + PDG (title) | unknown |
| FPGR 2026 | abstract | file/class | file-level yes (weak) | AST GNN + class-dependency GAT | WV + CV |
| Graph code semantics 2025 | abstract | file (method graphs aggregated) | unknown | method CFG/PDG via TinyPDG | unknown |
| Augmented-CPG 2021 | abstract | defect regions | unknown | AST+CFG+DFG+call, GNN | unknown |

## BugPre 2023 (10.1007/s40747-022-00848-w)
- **Citation.** Wang Z, Tong W, Li P, Ye G, Chen H, Gong X, Tang Z. BugPre: an intelligent software version-to-version bug prediction system using graph convolutional neural networks. Complex & Intelligent Systems 9:3835-3855 (2023; online Aug 2022).
- **Access.** full_text
- **Task and granularity.** Binary defective/clean classification of Java methods (functions). At prediction time only the changed functions and the functions affected by them (variable-propagation-tree change-impact analysis, VPT-CIA) of the new release are scored (System overview; Changed code generation).
- **Language and data.** Java. Dataset 1: Hadoop, Lucene, Log4j, Ant adjacent-version pairs, used for the invalid-code filtering experiment (Table 7). Dataset 2: NanoXML, JUnit, HttpCore, Heritrix, used for the CIA experiment (Table 8). Dataset 3: PROMISE, 6 projects / 20 releases (Camel 1.0-1.6, Ivy 1.1-2.0, Log4j 1.0-1.2, Xalan 2.4-2.6, Lucene 2.0-2.4, Ant 1.4-1.7). Table 5 counts are Java files. Dataset 4: Kafka 2.5.0/2.6.1/2.7.0 and Druid 0.19.0/0.20.0/0.22.x (Fig. 11).
- **Representation.** Per-method JavaParser AST with added NextExec control-flow edges (if/loop/sequential rules, Fig. 2) and VarDefinition/VarUse/VarModify data-flow edges. There are no call edges; call counts are a node feature. Node features: 8 statistical features (Table 1: in/out degree, nuMethodCalled, isControlNode, ...) and 6 version-change/process features (Table 2: NR, NDC, NML, NDPV = defects in previous version, MTPV, IBPV = buggy in previous version).
- **Model.** Graph convolutional network (GCNN; input/hidden/output layers with a softmax output; System design, Training model). Layer count and hyperparameters were not reported in the parts read.
- **Baselines.** LR, TNB, SVM and DT on PROMISE static metrics (Fig. 9). DBN and TCNN on AST token vectors, evaluated on the same VPT test subset (Fig. 10). Reported F1 values of the CVDP methods DS3, WGNCS and HALKP (Table 9). ADCNN (CPDP) is mentioned in the text only. The CIA baselines are InfluenceCIA and VM-CIA (Table 8, Fig. 8).
- **Evaluation setup.** Training data are all labelled data of release N, split 8:2 into train and validation. The test data are the next adjacent release, restricted to the VPT impact set (e.g., Camel 1.0 -> 1.2; section 'Efficiency of defect detection based on GCNN'). Metrics are precision, recall and F1 only. PofB20 was explicitly not used because only changed code is tested. There was a single run, with no statistical tests.
- **Cross-version.** Yes, nominally: release N -> N+1 (adjacent) within a project, at function level (Efficiency of defect detection based on GCNN; Fig. 1). However, the PROMISE ground truth is per Java file ('each java file enables it to be easily labeled'), and the paper never states how method labels were derived from it. The test set is only the changed or impacted functions, not the whole release.
- **Graph-based.** Yes. Intra-procedural AST+CFG+data-flow graph (a hand-built PDG-like graph, not Joern/Soot) built with JavaParser. Edge types: AST NextToken, NextExec (control flow), VarDefinition, VarUse, VarModify. The GNN is a GCN. A separate graph is used for change detection: random-walk AST graph matching (similarity threshold calibrated on Camel/Ant/Xalan, Table 3) plus the VPT.
- **Duplication / leakage handling.** No explicit de-duplication or leakage analysis. Restricting the test set to changed or impacted functions incidentally removes most unchanged methods, so it partly controls carry-over leakage. However: (a) 'impacted' functions can be textually unchanged, (b) training uses all of release N, and (c) the CIA similarity threshold was calibrated on Ant and Xalan, which are also evaluation projects (Table 3).
- **Label source and noise.** Commit-message keywords ('fix', 'defect', 'bug') identify fixed code in the next version (Data processing). The PROMISE experiments use file-level bug marks. The authors acknowledge keyword labelling as a threat (Limitation and discussion). There is no SZZ, no handling of tangled commits, and no validation of labels.
- **Metrics and key results.** GCNN average precision 67.5% (5.7-22.3 points above the four ML models) and average recall 71.8% (about 20-30 points higher) (Fig. 9, text). Table 9 average F1 is 0.6721 (Camel 0.6387, Ivy 0.7205, Log4j 0.6685, Xalan 0.7103, Ant 0.6227) vs DS3 0.3708, WGNCS 0.4986, HALKP 0.4483. AST pruning raised precision by an average of 2.6% and recall by 17.7% (Fig. 6, text). DBN/TCNN average precision >57% and recall >59% (Fig. 10, text).
- **Stated limitations.** Keyword-based labelling; Java-only (claimed extensible); insufficient historical data in early versions (Limitation and discussion).
- **Critical assessment.** (1) Granularity and label mismatch: the method-level claims rest on PROMISE file-level labels, and the propagation of file labels to methods is not described. Labels are therefore likely noisy (all methods of a buggy file, or keyword-matched fragments). (2) Table 9 is not a like-for-like comparison. BugPre is scored only on its own CIA-selected subset, while DS3/WGNCS/HALKP numbers appear to come from different setups on whole releases. The table also labels the method 'DefectPre'. (3) The process features NDPV/IBPV encode defect history and are strong predictors on their own. There is no ablation separating graph structure from these features, so the graph contribution is unidentified. (4) Only threshold-dependent P/R/F1 on an undescribed test-class ratio; no AUC, MCC or effort-aware metrics; no repetitions or significance tests. (5) The recall formula is printed as TP/(TP+TN). (6) Leakage is reduced in practice by testing only changed code, but this is not framed or quantified, and training/test overlap of impacted-but-unchanged functions is unknown.
- **Relevance to project.** This is the closest design to the project's goal (cross-version, function-level, CFG+data-flow graph, GCN). Its 'test only changed/impacted methods' protocol can serve as a reference variant of the project's leakage control (changed-only vs all methods). Its reported numbers are not usable as a benchmark because of file-level labels and the non-comparable Table 9.

## BiPDG-DP 2026 (10.1002/smr.70115)
- **Citation.** Lin J-R, Huang C-Y, Fang C-C. Bidirectional Program Dependency-Guided Attention for Improved Method-Level Software Defect Prediction (BiPDG-DP). Journal of Software: Evolution and Process (2026), e70115.
- **Access.** abstract_only
- **Task and granularity.** Method-level SDP (abstract). Line localisation is suggested by citing snippets ('locating suspect lines of code when making method-level defect predictions', ResearchGate citation context; unverified).
- **Language and data.** Java; '32 releases of nine Java projects' (abstract). This matches the size of the Wattanakriengkrai et al./DeepLineDP line-level benchmark (9 projects, 32 releases), which suggests that dataset was reused. This is an inference, not verified.
- **Representation.** Method-level PDG with control and data dependencies, used in both directions (source-to-target and target-to-source) (abstract). Citing snippets indicate GraphCodeBERT-style attention masks per dependency type and direction, with CLS/SEP nodes attending globally (unverified).
- **Model.** Hierarchical Transformer language model with program-dependency-guided (masked) self-attention (abstract).
- **Baselines.** Not stated in the abstract.
- **Evaluation setup.** Not available. The abstract reports non-effort-aware and effort-aware metrics.
- **Cross-version.** Unknown (abstract only). If the 9-project/32-release benchmark was used with its standard protocol (train on the oldest release, validate on the next, test on later releases), it would be cross-version at method level, but this is unverified.
- **Graph-based.** Yes. The PDG (control and data dependence) at method level is used to guide attention rather than as GNN input. Construction tool unknown.
- **Duplication / leakage handling.** Unknown.
- **Label source and noise.** Unknown. If the DeepLineDP-style dataset was used, labels come from post-release bug-fix commits linked to issues (an SZZ-like line mapping), which have known noise. Unverified.
- **Metrics and key results.** Relative improvements of 11.8%-35.7% (non-effort-aware) and 14.2%-218.5% (effort-aware) over baselines (abstract). Absolute values are unavailable.
- **Stated limitations.** Unavailable.
- **Critical assessment.** Cannot be assessed beyond the abstract. Large relative effort-aware gains (up to 218.5%) usually indicate weak baselines on effort-aware metrics or very low baseline values, and the absolute numbers are needed. The key questions are whether testing is release-based and whether unchanged methods carried across the 32 releases are controlled. Priority for full-text retrieval: the paper is listed as 'full-text available' on ResearchGate (not accessible from this sandbox).
- **Relevance to project.** High in principle: method-level, PDG with control and data dependence, likely multi-release Java data overlapping the ActiveMQ releases the project uses (if it is the Wattanakriengkrai dataset). It is a strong candidate baseline design (dependency-masked Transformer, comparable to GraphCodeBERT).

## Yang MCN 2023 (10.1109/access.2023.3239266)
- **Citation.** Yang F, Xu H, Xiao P, Zhong F, Zeng G. A Method-Level Defect Prediction Approach Based on Structural Features of Method-Calling Network. IEEE Access 11 (2023).
- **Access.** full_text
- **Task and granularity.** Binary method-level defect prediction (Sec. III).
- **Language and data.** Java. 13 projects (one version each) from Shippey et al.'s method-level dataset (ELFF), e.g., EclEmma, HtmlUnit, Jmol, OmegaT, Saros, UNICORE, JMRI, JPPF, DrJava, GenoViz, CDK, JUMP, jTDS (Sec. IV.A, Table 3). Only methods present in both the MCN and the dataset are used.
- **Representation.** Method-calling network (MCN) built from bytecode with ASM ClassReader (Alg. 1), treated as undirected. Features: node2vec embedding, dim 32, default p/q (NEM); 53 network metrics (36 ego, 17 global; Table 2); 20 method code metrics (size, CC, Halstead; Table 1).
- **Model.** Random forest on the concatenated features (NENCM). Training data are randomly oversampled to 1:1 (Sec. III.C).
- **Baselines.** node2defect (NEM+CM, i.e., NECM), CM, EN, GN, NM, NENM, and node2vec DFS/BFS variants (RQ2; Table 8).
- **Evaluation setup.** Random 2:1 train/test split repeated 30 times, following Qu et al. (Sec. IV.D). Metrics: AUC, MCC, F1, precision, recall, PF, PofB20, Precision@20%. Wilcoxon signed-rank test and Cliff's delta (Sec. IV.E).
- **Cross-version.** No. A random within-version split. Cross-version is listed as future work (Sec. VI).
- **Graph-based.** Yes, at inter-procedural level: a method call graph from bytecode. node2vec embeddings and network-centrality metrics are fed to RF, with no GNN. No CFG/PDG.
- **Duplication / leakage handling.** None. node2vec is fit transductively on the whole MCN, including test methods (unsupervised, so label leakage is limited). Random splits put methods of the same class/file in both train and test.
- **Label source and noise.** Labels are inherited from the Shippey et al. dataset. Label noise is not discussed.
- **Metrics and key results.** NENCM improves AUC by 2.5%-6.7% and MCC by 13%-178.4% over baselines (Table 6, Sec. IV.F). It has the highest AUC on 10/13 and highest MCC on 11/13 projects (Tables 4-5). Gains are significant for PofB20 and Precision@20% (Table 7). Per-project numeric values are embedded as images in the PDF and were not extracted. The authors state the non-effort-aware improvement 'is not so significant' (RQ1 answer).
- **Stated limitations.** node2vec parameters are set manually; external validity is limited to 13 Java systems (Sec. V).
- **Critical assessment.** This is a within-version random-split study at method level. Pascarella et al. 2018/2020 showed that this setting inflates method-level results compared with a realistic time-aware evaluation. The AUC gain over code metrics alone is small (2.5-6.7%). The large relative MCC gains start from low baselines. There is no cross-version check, no de-duplication, and a single classifier (RF) without tuning. The call-graph view is complementary to intra-procedural CFG/DDG and cheap to compute.
- **Relevance to project.** Moderate. It is evidence that call-graph/network metrics add a small amount to method-level code metrics within a version. Call-graph metrics could serve as an extra structural baseline or feature group for Django/ActiveMQ, but the paper offers no cross-version evidence.

## TSASS 2022 (10.1155/2022/4311548)
- **Citation.** Yang F, Huang Y, Xu H, Xiao P, Zheng W. Fine-Grained Software Defect Prediction Based on the Method-Call Sequence. Computational Intelligence and Neuroscience 2022, Article 4311548 (PMC9365544).
- **Access.** full_text
- **Task and granularity.** Regression of defect density for 'method-call sequences' (random-walk paths through the call graph). The label is the mean of member-method labels (Sec. 3.2, Eq. 2). Comparisons are with class-level and method-level regressors.
- **Language and data.** Java. 10 project-versions of the ELFF dataset (Shippey et al. 2016): EclEmma 2.1, HtmlUnit 2008/2010, Jmol 9/10, OmegaT 3.5/3.6, Saros 1.0.6, Unicore 1.4/1.6 (Table 1, method defect rate 1.38%-9.98%; sequence stats in Table 2).
- **Representation.** Call graph from bytecode with ASM, then random walks to call sequences (Sec. 3.2, Eq. 1). Each method is parsed with javalang to an AST, flattened by DFS to tokens, one-hot encoded, and concatenated along the call sequence.
- **Model.** TSASS: Transformer encoder, global average pooling, and a sigmoid output trained with Smooth L1 loss, Adam and warmup (Sec. 3.4). Best hyperparameters: 2 heads, 1 encoder layer, FFN 1024, embedding 256, batch 128 (Sec. 6.2.4).
- **Baselines.** Seml (CBOW+LSTM) and DP-ARNN, both reimplemented in TensorFlow and converted to density regression (Sec. 4.4, 6.2.1). TSASS is also applied at class level and method level.
- **Evaluation setup.** Random over-sampling, then under-sampling to 1:1, then a random 4:1 train/test split per project (Sec. 5.1). Metrics: MAE and MSE only. Hyperparameters were tuned on HtmlUnit 2008, Unicore 1.4 and Unicore 1.6 by MAE (Sec. 6.2.4), which are evaluation projects; no separate validation set is described.
- **Cross-version.** No. A random within-version split, although some projects have two versions available (e.g., OmegaT 3.5/3.6).
- **Graph-based.** Partly. A call graph is used only to generate sequences; learning is sequence-based (Transformer over AST tokens). There is no GNN, CFG or PDG; CFG is listed as future work (Sec. 6.1).
- **Duplication / leakage handling.** None, and the design is leakage-prone: (a) resampling is described before the split, so duplicated minority samples can appear in both train and test; (b) random-walk sequences share member methods, so the same method bodies appear in train and test sequences; (c) hyperparameters were selected on evaluation projects.
- **Label source and noise.** Method labels come from ELFF (Shippey et al.). Sequence labels are averages of method labels, a derived and smoothed target.
- **Metrics and key results.** Average MAE: sequence 0.095 vs class 0.158; MSE 0.0254 vs 0.0487 (Table 3). Method-level beats sequence-level on MAE: 0.051 vs 0.095 (Table 4). The authors still call sequences more 'stable' because MSE is 0.0254 vs 0.0429. Model comparison: TSASS MAE 0.095 vs Seml 0.155 and DP-ARNN 0.312 (Table 5). Comparison of whole methods: Seml 0.175, DP-ARNN 0.177 (Table 6).
- **Stated limitations.** Reimplemented baselines; ELFF Java-only; MAE/MSE not the only possible metrics; hyperparameter selection (Sec. 6.2).
- **Critical assessment.** (1) MAE/MSE are not comparable across granularities with different label distributions: sequence labels are averages with defect rates up to 35.6% (Table 2), while method labels are binary with 1-10% defect rates. (2) The paper's own Table 4 contradicts its headline claim, since method-level MAE is lower. (3) Resampling before splitting and sequence overlap make test leakage very likely. (4) Tuning on test projects. (5) No classification or ranking metrics, so results cannot be compared with SDP work. The paper cites Pascarella et al. that realistic method-level evaluation falls to near-random, but does not apply such an evaluation.
- **Relevance to project.** Low as evidence. It is useful mainly as an example of the leakage patterns the project aims to control (overlapping units, resampling before splitting, tuning on test data).

## FINDGATE 2023 (10.1109/qrs60937.2023.00017)
- **Citation.** Xu J, Chen P, Yin B, Huang Z, Qiu Q. FINDGATE: Fine-grained Defect Prediction Based on a Heterogeneous Discrete Code Graph-guided Attention Transformer. Proc. IEEE QRS 2023, pp. 72-82.
- **Access.** full_text
- **Task and granularity.** Function-level binary classification, plus statement-level localisation derived from attention scores without statement labels in training (Sec. 3.4-3.5).
- **Language and data.** C/C++ vulnerability data: Big-Vul, using the LineVul 8:1:1 split, with HDCGs for 188,636 functions (Sec. 4.2). Not a release-based defect dataset. The tool supports Java, Python, C, C++, C# and Ruby via tree-sitter (Sec. 3.2).
- **Representation.** HDCG: the Augmented-CPG (from ACGDP) rebuilt on tree-sitter, with AST, DFG, CFG and call edges, collapsed onto leaf nodes and then onto BPE tokens (CodeSearchNet tokenizer). Adjacency matrices per edge type (Eq. 5).
- **Model.** GATE: a Transformer encoder (CodeT5 encoder defaults) with parallel graph-masked self-attention modules per edge type plus the original attention, combined by learnable weighted sum (Eq. 9-12), then a 2-layer MLP classifier. Trained for 10 epochs (Sec. 6.3). Statement scores come from summed attention rows aggregated token -> leaf -> statement (Eq. 13-15).
- **Baselines.** Function level (Table 1): LineVul, DeepDFA+LineVul, DeepDFA, DeepVD, Devign, IVDetect, ReVeal, SySeVR, VulDeePecker, DeepLineDP, Russell et al., LineDP. Line level: LineVul, DeepLineDP, JITLine, and a graph-only ablation (Table 2). The LineVul model was reused as trained by Fu et al. Results for non-reproducible models such as IVDetect were copied from papers (Sec. 6.3).
- **Evaluation setup.** Random 8:1:1 split; training and tuning on train/validation (Sec. 3.5). Function level: precision, recall, F1. Line level: Top-10 accuracy, IFA, total effort, Effort@20%Recall, Recall@1%LOC. Single run, no significance tests.
- **Cross-version.** No. A random function split of Big-Vul; no releases.
- **Graph-based.** Yes: an AST+CFG+DFG+call-edge code property graph. Instead of a GNN, the graph is used as attention masks in a Transformer.
- **Duplication / leakage handling.** None. Big-Vul with random splits is known to contain duplicates and label noise (Croft et al. ICSE 2023; PrimeVul/Ding et al. ICSE 2025 report large F1 drops after de-duplication and chronological splitting). FINDGATE inherits these issues.
- **Label source and noise.** Big-Vul CVE-fix commits: before-fix functions are labelled vulnerable, and changed lines give line labels. Known noise from tangled fix commits and duplicates is not discussed.
- **Metrics and key results.** Function-level P/R/F1 0.98/0.91/0.95 vs LineVul 0.97/0.86/0.92 and DeepDFA+LineVul 0.98/0.90/0.94 (Table 3). Line level: Top-10 accuracy 0.80 vs LineVul 0.65; IFA 5.48 vs 5.77; total effort 0.49 vs 0.52; graph-only ablation 0.48 Top-10 (Table 5). Effort@20%Recall 0.0088 vs 0.0107; Recall@1%LOC 0.22 vs 0.19 (Table 6).
- **Stated limitations.** Dataset choice (Big-Vul only); default CodeT5 hyperparameters; only 10 epochs; reliance on reimplementations and copied results (Sec. 6).
- **Critical assessment.** The gains over LineVul and DeepDFA+LineVul are 1-3 F1 points on a benchmark where F1 is near saturation (0.92-0.95). Such near-ceiling scores on Big-Vul random splits are now widely attributed to duplication and leakage. With a single run and no variance or significance tests, the differences are within plausible noise. The graph-only ablation is much weaker (Top-10 0.48), so most of the signal comes from the pretrained token attention, not the graph. The task is vulnerability detection, not post-release defect prediction.
- **Relevance to project.** Methodological relevance only. Graph-masked attention over CFG/DFG edges is a lightweight alternative to GNNs that can be added to a CodeBERT/CodeT5 baseline. Its tree-sitter Augmented-CPG supports Python, which is relevant for Django. Its results say nothing about cross-version behaviour.

## DIDP 2025 (10.32604/cmc.2024.057697)
- **Citation.** Yang F, Zhong F, Wei X, Zeng G. A Fine-Grained Defect Prediction Method Based on Drift-Immune Graph Neural Networks (DIDP). Computers, Materials & Continua 82(2), 2025 (DOI year 2024). Note: the first author is Fengyu Yang, not 'Wei et al.' as listed in the task.
- **Access.** full_text
- **Task and granularity.** File-level defect classification (graph classification), plus statement-level risk ranking inside predicted-defective files. Not method-level (Sec. 3.3-3.4).
- **Language and data.** Java. File level: PROMISE, 9 projects (ant, jedit, camel, log4j, xalan, synapse, lucene, poi, xerces; Table 1). Statement level: the Wattanakriengkrai et al. line-level dataset, 9 systems / 32 versions, including ActiveMQ 5.0.0, 5.1.0, 5.2.0, 5.3.0 and 5.8.0 (Table 2).
- **Representation.** File-level PDG with control and data dependencies (extraction tool not named). Node features are Doc2vec (PV-DM/PV-DBOW) embeddings of each statement, dim 100 (Sec. 3.2, Sec. 4). For statement-level training, PDGs of training files are sliced around defective lines (backward on control+data, forward on data only); the test set is not sliced (Sec. 3.1).
- **Model.** DI-GNN: a GSAT-style graph stochastic attention / information-bottleneck subgraph extractor plus predictor (Eq. 1). The GNN backbone type is not named. Statement risk is degree centrality within the extracted subgraph (Sec. 3.4). Adam lr 0.001, batch 128, dropout 0.1; other hyperparameters by grid search (Sec. 4).
- **Baselines.** File level: BN, Seml, CNN, DBN, BugContext, LSTM, DTLDP, MFGNN, ACGDP, DHCNN (Sec. 5.1). Statement level: ErrorProne, IVDetect* (adapted), LineVD (Sec. 5.2).
- **Evaluation setup.** File-level WPDP: previous release for training/validation, next release for testing (e.g., xalan 2.4 -> 2.5) (Sec. 5.1). CPDP: pairs (Tables 5-6). Statement level: test on the 3rd and later versions per project (Table 7, e.g., activemq-5.2.0/5.3.0/5.8.0). Statement CPDP uses the first version of other projects for training and the second for validation (Sec. 5.2(2)). Medians, Wilcoxon, Win/Tie/Loss, and Scott-Knott ESD.
- **Cross-version.** Yes at file level: release N -> N+1 on PROMISE (Sec. 5.1). Yes at statement (line) level on the Wattanakriengkrai dataset: train on earlier releases, test on later ones (Table 7). The authors call this 'WPDP'. It is not method level.
- **Graph-based.** Yes. Statement-level PDG (control and data dependence), with Doc2vec node features, a GSAT-like stochastic-attention GNN and an information-bottleneck subgraph. The PDG tool is unspecified.
- **Duplication / leakage handling.** None. Unchanged files and lines across releases are not handled. Training PDGs are sliced around defective lines only for defective training files, while test files are unsliced. This train/test distribution asymmetry may let the model exploit graph size or shape, a possible shortcut.
- **Label source and noise.** PROMISE file labels and Wattanakriengkrai line labels (post-release fix commits mapped to lines). The authors describe labels as 'obtained via manual statistics' and accept them as reliable (Sec. 7.1).
- **Metrics and key results.** File-level WPDP median AUC: DIDP 0.685 vs DHCNN 0.730 and ACGDP 0.678 (Table 3; p vs DHCNN 0.172). Median F1: DIDP 0.615 vs DHCNN 0.656 (Table 4). DIDP is second, not best (SK-ESD, Fig. 6). File-level CPDP: AUC 0.651 vs DHCNN 0.658 (p 0.766); F1 0.558 vs 0.550 (Tables 5-6). Statement-level median Recall@Top20%LOC 0.377 vs LineVD 0.308 (p 0.078), IVDetect* 0.292, ErrorProne 0.079. Effort@Top20%Recall 0.175 vs LineVD 0.195 (p 1.000). IFA 69 vs 128 (Table 7). ActiveMQ Recall@20%LOC: 0.421 (5.2.0), 0.435 (5.3.0), 0.391 (5.8.0) (Table 7).
- **Stated limitations.** Label quality; baseline reimplementation; only two datasets and Java; not applicable to JIT; model must still be updated under drift (Sec. 7).
- **Critical assessment.** (1) The 'drift-immune' claim is not tested directly. There is no comparison of the same model with and without the IB/stochastic attention across release gaps, and no drift measurement. (2) On file-level cross-version data DIDP does not beat DHCNN, and the differences vs the top baselines are non-significant (Tables 3-4). (3) The statement-level advantage over LineVD is non-significant on Recall@20%LOC (p=0.078) and Effort (p=1.0). (4) Slicing only training graphs creates a train/test mismatch. (5) The RQ2 answer text misreports CPDP ranges as WPDP ranges. (6) No de-duplication of files unchanged between releases. (7) The PDG tool and GNN backbone are unspecified, which hurts reproducibility.
- **Relevance to project.** High for data: it uses ActiveMQ 5.0.0/5.1.0/5.2.0/5.3.0/5.8.0, the same releases the project uses, with release-ordered training and testing. Its line-level numbers (Table 7) are a comparable reference point. It also shows a PDG+Doc2vec node-feature design that bridges the project's doc2vec baseline and graph models. It is file/line level, not function level.

## TFDP 2026 (10.1016/j.jss.2026.112873)
- **Citation.** Zheng W, Xiong Z, Fan X, Pan H, Yang F, Xiao P. TFDP: A triple-Fusion model for software defect prediction with hierarchical AST and multiscale PDG encoding. Journal of Systems and Software 238 (2026) 112873.
- **Access.** not_found
- **Task and granularity.** Unknown. Neither the full text nor the abstract could be retrieved (closed access; OpenAlex, Semantic Scholar and Crossref return no abstract). The title indicates fusion of three feature sources: hierarchical AST, multiscale PDG, and probably traditional metrics (inference).
- **Language and data.** Unknown.
- **Representation.** Hierarchical AST encoding plus multiscale PDG encoding (title only).
- **Model.** Unknown ('triple-fusion').
- **Baselines.** Unknown.
- **Evaluation setup.** Unknown.
- **Cross-version.** Unknown; not determinable from the title.
- **Graph-based.** Yes per the title (PDG). Tool, edge types and GNN are unknown.
- **Duplication / leakage handling.** Unknown.
- **Label source and noise.** Unknown.
- **Metrics and key results.** Not available.
- **Stated limitations.** Not available.
- **Critical assessment.** Cannot be assessed. Authors overlap with the Nanchang Hangkong University group behind the method-call sequence paper (Yang F, Xiao P, Zheng W) and DIDP/MCN (Yang F). That group's prior protocols were random splits or file-level PROMISE, so a file-level PROMISE setup is plausible but unverified. Snippets on ResearchGate citation pages mentioning AST subgraphs of 'syntactic structure type nodes' and PDG/GCN fusion could not be reliably attributed to TFDP and were not used.
- **Relevance to project.** Unknown. Worth retrieving only if it reports release-based, function-level results with PDG; the title suggests file-level fusion.

## FPGR 2026 (10.1002/stvr.70032)
- **Citation.** Zhou X, Zhu X, Wang Y, Tian S, Wang J, Lai X, Li X. Software Defect Prediction Model Fusing File and Program Graph Representation (FPGR). Software Testing, Verification and Reliability 36(8), 2026, e70032.
- **Access.** abstract_only
- **Task and granularity.** File/class-level SDP (abstract; journal graphical abstract: 'file-level AST semantics with project-level class dependencies'). Not method level.
- **Language and data.** 14 open-source projects (abstract); language presumably Java (class dependencies), not stated.
- **Representation.** Two levels: a file-level GNN over each file's AST (per the graphical abstract) produces embeddings that initialise nodes of a project-level class-dependency graph.
- **Model.** File-level GNN, then a project-level 'defect-aware' GAT with category (class-label) weighting during message passing to address imbalance and heterophily (abstract).
- **Baselines.** Not stated in the abstract.
- **Evaluation setup.** Within-version and cross-version SDP (abstract). Details unavailable.
- **Cross-version.** Yes at file/class level, per the abstract. Not method level. The authors state cross-version performance is 'not particularly satisfactory', though comparable to existing methods.
- **Graph-based.** Yes: AST graphs per file and a class-dependency network across the project; GAT with class-aware weighting.
- **Duplication / leakage handling.** Unknown. The transductive project-level graph with label-aware weighting needs care: node labels used during message passing could leak in within-version settings if test nodes participate. Cannot be verified.
- **Label source and noise.** Unknown.
- **Metrics and key results.** Qualitative only: better within-version, only comparable cross-version (abstract).
- **Stated limitations.** Unsatisfactory cross-version performance; sensitivity to hyperparameters (abstract).
- **Critical assessment.** The abstract itself shows the familiar pattern: a graph model that wins within-version loses its advantage cross-version. This is consistent with within-version gains being partly driven by transductive or shared-structure effects. Without the full text, the leakage of label-aware message passing cannot be assessed.
- **Relevance to project.** Supporting evidence for the project's thesis that graph gains shrink under release-based evaluation. File/class level, so not directly comparable.

## Graph code semantics 2025 (10.1016/j.eswa.2025.129842)
- **Citation.** Tao H, Wang T, Geng Z, Niu X, Cao Q. Software defect prediction based on graph code semantics. Expert Systems with Applications 298 (2026) 129842.
- **Access.** abstract_only
- **Task and granularity.** File-level SDP. Method-level CFG/PDG embeddings are aggregated into Java file-level vectors (ScienceDirect landing-page abstract/highlights, via search snippet).
- **Language and data.** Java; datasets not visible in the accessible text.
- **Representation.** Per-method CFG and PDG from an 'improved TinyPDG'. The CFG/PDG corpus is trained with CBOW to obtain node, edge and adjacency information, then a BiLSTM. Method vectors are aggregated to the file level by weighted summation (W-CFG/W-PDG) or a linear fully connected layer (L-CFG/L-PDG), with a modified 'PNIAT' layer (landing-page text).
- **Model.** Feature extractor (CBOW + BiLSTM) followed by a QDA classifier (W-PDG-QDA best).
- **Baselines.** Traditional metrics, CNN, BiLSTM, DeepWalk, node2vec, GCN, GAT (landing-page text).
- **Evaluation setup.** Unknown.
- **Cross-version.** Unknown.
- **Graph-based.** Yes: method-level CFG and PDG via TinyPDG (Java). Embeddings come from CBOW over graph corpora plus a BiLSTM rather than message passing; GNNs (GCN/GAT) serve as baselines.
- **Duplication / leakage handling.** Unknown.
- **Label source and noise.** Unknown (likely PROMISE-style file labels; unverified).
- **Metrics and key results.** Qualitative: W-PDG-QDA, L-PDG-QDA and W-CFG-QDA beat all baselines; W-PDG-QDA is best; weighted sum beats linear aggregation; PDG beats CFG (landing-page text). No numbers available.
- **Stated limitations.** Unavailable.
- **Critical assessment.** An interesting data point is that PDG beats CFG in the same pipeline, but only qualitative claims are available. Using QDA as the final classifier on learned embeddings is unusual and sensitive to covariance estimation. The outcome depends heavily on the split protocol, which is unknown.
- **Relevance to project.** Moderate. It uses the same graph types the project extracts (method-level CFG vs PDG) and directly compares CFG vs PDG, which the project can replicate with Joern CFG vs CFG+DDG. Aggregating method vectors to the file level is the reverse of the project's direction.

## Augmented-CPG 2021 (10.1109/dsa52907.2021.00097)
- **Citation.** Xu J, Ai J, Shi T. Software Defect Prediction for Specific Defect Types based on Augmented Code Graph Representation. Proc. 8th Int. Conf. on Dependable Systems and Their Applications (DSA 2021), pp. 669-678.
- **Access.** abstract_only
- **Task and granularity.** Defect-type-specific prediction over 'defect region candidates' extracted from code (abstract). Granularity unclear: candidate regions or slices.
- **Language and data.** Unknown. The later ACGDP/FINDGATE papers describe the original Augmented-CPG generator as ANTLR-based and limited to compilable Java (FINDGATE Sec. 3.2), so Java is likely.
- **Representation.** Augmented-CPG: AST augmented with data dependence, control dependence and function-call edges (as described in the follow-up FINDGATE Sec. 3.2); defect-type-specific candidate-region extraction.
- **Model.** Graph neural network (type unknown).
- **Baselines.** Unknown.
- **Evaluation setup.** Unknown; experiments on three defect types (abstract).
- **Cross-version.** Unknown; likely no (type-specific detection).
- **Graph-based.** Yes: Augmented-CPG (AST+CFG/control dependence+DFG+call) with a GNN.
- **Duplication / leakage handling.** Unknown.
- **Label source and noise.** Unknown.
- **Metrics and key results.** Qualitative: 'can effectively predict specific types of defects' (abstract).
- **Stated limitations.** Unavailable.
- **Critical assessment.** Not assessable. This is the precursor of ACGDP (IEEE TR 2022, 10.1109/TR.2022.3161581) and FINDGATE, so its representation is documented there. Type-specific candidate extraction resembles vulnerability-slice approaches (SySeVR) more than release-based SDP.
- **Relevance to project.** Low directly. It is useful as the origin of the Augmented-CPG representation; the later tree-sitter version supports Python.

## Theme synthesis

Access: 5 of 10 papers were read in full (BugPre, Yang MCN, method-call sequence/TSASS, FINDGATE, DIDP). BiPDG-DP, FPGR, graph-code-semantics (ESWA) and Augmented-CPG (DSA) are abstract or landing-page only. TFDP has metadata only. Conclusions about those five are provisional.

1. Cross-version at method level is almost absent. Only BugPre claims release N -> N+1 at function level, and its PROMISE ground truth is file-level, with no description of how labels were propagated to methods. DIDP is release-based but at file and line level. BiPDG-DP probably uses the 9-project/32-release Wattanakriengkrai benchmark (release-ordered), but this is unverified. FPGR is cross-version at file/class level. The Yang MCN and TSASS method-level studies use random within-version splits. FINDGATE uses random splits of Big-Vul. None of the ten papers is a clean, function-level, release-to-release study with method labels derived from release-specific bug fixes.

2. Leakage and duplication controls are absent in all ten. No paper de-duplicates methods, files or functions unchanged between releases, or reports overlap between train and test. BugPre's 'test only changed/impacted functions' design is the only one that reduces carry-over leakage, and it does so as a side effect of an efficiency goal. Several protocols add leakage: TSASS resamples before splitting, uses overlapping call sequences and tunes on the evaluation projects; MCN fits node2vec transductively; DIDP slices training graphs only (train/test mismatch); FINDGATE uses random Big-Vul splits, known to contain duplicates.

3. Gains from graphs are small, or vanish under harder settings. DIDP does not beat DHCNN cross-version (AUC 0.685 vs 0.730; F1 0.615 vs 0.656; n.s.), and its line-level gain over LineVD is n.s. FINDGATE gains 1-3 F1 points over LineVul at ceiling, and its graph-only ablation is much weaker, so the pretrained token signal dominates. MCN adds 2.5-6.7% AUC over code metrics within version. FPGR's own abstract says cross-version performance is only comparable to prior methods. This matches the earlier project finding that network-metric gains disappear under forward-release splits (Premraj & Herzig 2011).

4. Graph types and tools. The intra-procedural graphs are an AST+CFG+data-flow graph hand-built with JavaParser (BugPre), a file PDG (DIDP, tool not named), method CFG/PDG via TinyPDG (ESWA), method PDG (BiPDG-DP), and AST+CFG+DFG+call via ANTLR, later tree-sitter (Augmented-CPG/FINDGATE). The inter-procedural graphs are call graphs from bytecode (MCN, TSASS) and class-dependency networks (FPGR). None of the papers uses Joern. Only FINDGATE's tree-sitter generator supports Python. All empirical studies are Java or C/C++, with no Python. Graphs are used through GCN (BugPre), GSAT-like IB-GNN (DIDP), GAT (FPGR), graph-masked Transformer attention (FINDGATE, BiPDG-DP), and graph embeddings fed to classical models (MCN RF; ESWA CBOW+BiLSTM+QDA).

5. Baselines and metrics are weak. No paper compares against CodeBERT/GraphCodeBERT fine-tuned at method level under the same split, except FINDGATE (LineVul = CodeBERT) on vulnerability data. Metric baselines are usually PROMISE file metrics. Reporting is often F1/P/R only (BugPre), or MAE/MSE (TSASS). MCC appears only in MCN, and effort-aware metrics in MCN, DIDP, FINDGATE and BiPDG-DP. Repeated runs and significance tests are missing in BugPre, TSASS and FINDGATE. Comparisons copied from other papers' numbers (BugPre Table 9; FINDGATE for IVDetect) are not like-for-like.

6. Label noise is unaddressed. Sources are commit-keyword labels (BugPre), PROMISE file labels pushed down to finer units (BugPre, DIDP file level), ELFF/Shippey method labels (MCN, TSASS), and CVE-fix labels (FINDGATE). None applies SZZ variants with tangled-commit filtering, and none estimates label noise.

7. Implications for the project. (a) A Joern CFG+DDG function-level model evaluated release N -> N+1 on Django and ActiveMQ, with explicit unchanged/duplicate-method handling, would fill a gap none of these papers covers. (b) DIDP's ActiveMQ 5.0.0-5.8.0 line-level results and the probable BiPDG-DP use of the same benchmark make ActiveMQ a natural point of comparison. Check whether the project's labels align with the Wattanakriengkrai dataset. (c) Report results on three test subsets (all methods; changed methods only, as in BugPre; new methods only) to quantify how much graph and baseline gains depend on carried-over methods. (d) Add two cheap structural comparators: call-graph centrality/node2vec (MCN) and CFG-vs-PDG ablation (ESWA). Also add a graph-masked attention variant of CodeBERT (FINDGATE/BiPDG-DP) as a strong hybrid baseline. (e) Use MCC and effort-aware metrics, with repeated seeds and significance tests.

Note: four of the ten papers (MCN, TSASS, DIDP, and TFDP by author overlap) come from one group (Nanchang Hangkong University; F. Yang, P. Xiao, W. Zheng), so the evidence is less independent than ten papers would suggest.

## Additional papers found

- Xu J, Ai J, Liu J, Shi T. ACGDP: An Augmented Code Graph-Based System for Software Defect Prediction. IEEE Trans. Reliability 71(2):850-864, 2022. DOI 10.1109/TR.2022.3161581 (verified from FINDGATE reference list). Graph-based (Augmented-CPG + GNN), file level; a strong baseline in DIDP Tables 3-6.
- Abdu A. et al. Software Defect Prediction Based on Deep Representation Learning of Source Code From Contextual Syntax and Semantic Graph (DHCNN). IEEE Trans. Reliability 2024. DOI 10.1109/TR.2024.3354965 (Crossref-verified). AST+CFG+DDG, file level; best cross-version baseline in DIDP. First author not checked against the record.
- Zhou C, He P, Zeng C, Ma J. Software defect prediction with semantic and structural information of codes based on graph neural networks. Information and Software Technology 152:107057, 2022. DOI 10.1016/j.infsof.2022.107057 (Crossref-verified).
- Wattanakriengkrai S, Thongtanunam P, Tantithamthavorn C, Hata H, Matsumoto K. Predicting Defective Lines Using a Model-Agnostic Technique (LineDP). IEEE TSE 2020. DOI 10.1109/TSE.2020.3023177 (from FINDGATE refs). Release-based line-level benchmark incl. ActiveMQ 5.0.0-5.8.0, the project's ActiveMQ releases.
- Pornprasit C, Tantithamthavorn C. DeepLineDP: Towards a Deep Learning Approach for Line-Level Defect Prediction. IEEE TSE 2023. DOI 10.1109/TSE.2022.3144348 (Crossref-verified). Release-ordered train/validation/test on the 9-project/32-release benchmark.
- Shippey T, Hall T, Counsell S, Bowes D. So You Need More Method Level Datasets for Your Software Defect Prediction? Voila! ESEM 2016. DOI 10.1145/2961111.2962620 (Crossref-verified). The ELFF method-level dataset used by MCN and TSASS.
- Qu Y. et al. node2defect: using network embedding to improve software defect prediction. ASE 2018. DOI 10.1145/3238147.3240469 (Crossref-verified). Class-dependency network embedding; baseline of MCN.
- Pascarella L, Palomba F, Bacchelli A. Re-evaluating method-level bug prediction. SANER 2018. DOI 10.1109/saner.2018.8330264 (Crossref-verified). Realistic, time-aware evaluation collapses method-level performance; cited by TSASS.
- Croft R, Babar MA, Kholoosi MM. Data Quality for Software Vulnerability Datasets. ICSE 2023. DOI 10.1109/ICSE48619.2023.00022 (Crossref-verified). Documents duplicates and label noise in Big-Vul etc., relevant to FINDGATE.
- Ding Y. et al. Vulnerability Detection with Code Language Models: How Far are We? (PrimeVul). ICSE 2025. DOI 10.1109/ICSE55347.2025.00038 (Crossref-verified). De-duplication plus chronological splits sharply reduce reported performance.
- Fu M, Tantithamthavorn C. LineVul: A Transformer-based Line-Level Vulnerability Prediction. MSR 2022. DOI 10.1145/3524842.3528452 (Crossref-verified).
- A Software Defect Prediction Method Using a Multivariate Heterogeneous Hybrid Deep Learning Algorithm (DP-MHHDL). CMC 82(2), 2025. DOI 10.32604/cmc.2024.058931 (Crossref-verified). File-level cross-version (previous -> next release); not read.
- Wang Y, Wang P, Tao H, Wang T, Geng Z, Xie Y. Cross-project defect prediction based on transfer graph convolutional network. Empirical Software Engineering 31:45, 2025/2026. DOI 10.1007/s10664-025-10783-2 (Crossref-verified). Same group as the ESWA graph-code-semantics paper.
- Steenhoek B. et al. DeepDFA: Dataflow analysis-guided efficient graph learning for vulnerability detection (ICSE 2024). DOI not verified. Data-flow-analysis GNN combined with LineVul; strong graph+Transformer baseline in FINDGATE.
- Gupta et al. Cognitive Complexity and Graph Convolutional Approach Over Control Flow Graph for Software Defect Prediction (IEEE Access 2022). DOI not verified. CFG + GCN.
- Phan AV, Nguyen ML, Bui LT. Convolutional Neural Networks over Control Flow Graphs for Software Defect Prediction (ICTAI 2017). DOI not verified. Early CFG-based SDP (DGCNN on assembly CFGs).