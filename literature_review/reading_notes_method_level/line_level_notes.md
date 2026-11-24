# Line-level defect prediction: graph-based and cross-version notes

Scope: 11 papers assigned to the 'Line-level graphs' track. Full text read: LineFlowDP (10.1007/s10664-023-10439-z), Zhou et al. 2024 (10.1002/smr.2696, author copy), and the Bugsplorer arXiv preprint (2312.11889) as an additional paper. The other 9 assigned papers are based on abstracts, abstract fragments, or secondary descriptions only, so their entries are provisional.


## Pornprasit C., Tantithamthavorn C. (2023). DeepLineDP: Towards a Deep Learning Approach for Line-Level Defect Prediction. IEEE TSE 49(1):84-98.
DOI: 10.1109/tse.2022.3144348

- **access**: abstract_only
- **task and granularity**: File-level classification plus line-level risk ranking inside predicted-defective files (attention scores aggregated per line). Practitioner survey (36 respondents) motivates line level.
- **language and data**: Java; Line-DP benchmark of Wattanakriengkrai et al. 2020 (TSE): 9 Apache Java projects, 32 releases (ActiveMQ 5.0.0/5.1.0/5.2.0/5.3.0/5.8.0, Camel, Derby, Groovy, HBase, Hive, JRuby, Lucene, Wicket); affected-version (JIRA) file labels, defective lines = lines deleted/modified by post-release bug-fix commits (abstract: 32 releases of 9 projects; dataset identity confirmed via Zhou et al. 2024, smr.2696, Table 2).
- **representation**: Token sequences of each line (word2vec-style token embeddings); hierarchical token->line->file encoding.
- **model**: Hierarchical attention network: Bi-GRU over tokens with token attention, Bi-GRU over lines with line attention (per abstract and secondary descriptions in smr.2696 Sec. 2, arXiv 2312.11889 Sec. related work). Line score = token attention aggregated per line (k=1,500 tokens reported in smr.2696 Sec. 2).
- **baselines**: File level: BoW, DBN, CNN, Bi-LSTM; line level: n-gram, ErrorProne, random forest/LineDP (as reported secondarily in smr.2696 Sec. 2).
- **evaluation setup**: Per secondary description (smr.2696 Sec. 4.x 'DeepLineDP evaluation'; LineFlowDP Sec. 5.1): release 1 = training, release 2 = validation, releases 3..n = test, giving 14 test releases. Also a cross-project transfer experiment (abstract).
- **cross version**: Yes at file and line level: train on the oldest release, validate on the second, test on later releases (secondary sources: Zhou et al. 2024 smr.2696 evaluation section; Yang et al. 2024 LineFlowDP Sec. 5.1). Not method level. Not N->N+1; later test releases are several versions away.
- **graph based**: No. Sequence/attention model; no AST/CFG/PDG.
- **duplication or leakage handling**: Not determinable from abstract. No secondary source reports removal of unchanged files/lines across releases.
- **label source and noise**: Affected-version file labels and bug-fix-diff line labels from the Line-DP dataset (Zhou et al. 2024 threats section). Line labels only mark lines removed/changed by the fix, so lines that were defective but not touched are labelled clean.
- **metrics and key results**: Abstract: 17%-37% more accurate than file-level approaches; 47%-250% more cost-effective than line-level approaches (Recall@Top20%LOC, Effort@Top20%Recall, IFA). Independent replication: Zhou et al. 2024 (smr.2696, Sec. 6.1) found that the original R evaluation script counted comment lines in the file LOC denominator, inflating Recall@Top20%LOC and Effort@Top20%Recall; after correction DeepLineDP ranks below all three GLANCE variants on Recall@Top20%LOC (smr.2696 Fig. 4) and Effort@Top20%Recall (median ~0.266 vs ~0.175 for GLANCE-EA/MD, smr.2696 Sec. 5.2).
- **stated limitations**: Not available (abstract only).
- **critical assessment**: Most-cited line-level DL baseline, but its line-level gains are not robust: an independent replication with the original code attributes part of the reported effect to an evaluation-script error (comment lines in the denominator) and finds a size/complexity heuristic (GLANCE) is better. Single fixed train release; one random seed per configuration (not verifiable here). Line-level labels inherit bug-fix-diff noise. File-level AUC comparisons against weak 2017-2018 baselines.
- **relevance to project**: Reference baseline for line-level SDP; its protocol (oldest release train -> later releases test) is the de facto 'cross-version' protocol of the line-level literature, and ActiveMQ 5.0.0-5.8.0 are the same releases this project uses. The evaluation-bug finding shows why the project must re-implement metrics and verify denominators.

## Guo Z., Liu S., Liu X., Lai W., Ma M., Zhang X., Ni C., Yang Y., Li Y., Chen L., Zhou G., Zhou Y. (2023). Code-line-level Bugginess Identification: How Far have We Come, and How Far have We Yet to Go? ACM TOSEM 32(4):102, 1-55.
DOI: 10.1145/3582572

- **access**: abstract_only
- **task and granularity**: Two-stage code-line-level bugginess identification (CLBI): file-level classifier, then ranking of lines inside predicted-defective files.
- **language and data**: Java; newly collected dataset of 19 Apache projects with 142 releases (abstract; ACM landing-page snippet).
- **representation**: Hand-crafted line features: number of tokens (NT), number of function calls (NFC), control-statement indicator (CE) (ACM page snippet; smr.2696 Sec. 2).
- **model**: GLANCE heuristic with three file-level stages: ManualDown (MD, unsupervised, size-based), effort-aware ManualDown (EA), logistic regression (LR). Line score combines NT and NFC; top k=50% of lines labelled buggy by default (ACM snippet).
- **baselines**: NLP-based (n-gram, LineDP), model-interpretation-based (LIME/random forest), and static analysis tools (PMD, CheckStyle) (abstract; ACM 10.1145/3707456 snippet).
- **evaluation setup**: Per Zhou et al. 2024 (smr.2696 evaluation section): sliding-window release i -> release i+1. 8 performance indicators (abstract).
- **cross version**: Yes, release i -> release i+1 at file and line level (protocol as described by Zhou et al. 2024, smr.2696). Not method level. Full text not read, so exact pairing on the 142 releases is unverified.
- **graph based**: No. Line features only (control-statement indicator approximates control-flow importance without a graph).
- **duplication or leakage handling**: Unknown (abstract only). GLANCE-MD/EA are unsupervised, so they are immune to train/test duplicate leakage by construction.
- **label source and noise**: Collected 'following and improving' the Line-DP data-collection process (ACM snippet); details unverified.
- **metrics and key results**: GLANCE comparable or superior to SOTA CLBI approaches and static tools on 8 indicators (abstract). Numeric values not read.
- **stated limitations**: Not available (abstract only).
- **critical assessment**: The key methodological contribution of the line-level field: a trivial, training-free heuristic matches learned models, which indicates that size/complexity confounds most line-level results. Full protocol and numbers not verified here.
- **relevance to project**: GLANCE (and size-only ManualDown) should be a mandatory baseline for any graph-based method-level model in this project: CFG/DDG size correlates with LOC and complexity, so a graph model must beat a size heuristic to show structure adds information.

## Yang F., Zhong F., Zeng G., Xiao P., Zheng W. (2024). LineFlowDP: A Deep Learning-Based Two-Phase Approach for Line-Level Defect Prediction. Empirical Software Engineering 29:50.
DOI: 10.1007/s10664-023-10439-z

- **access**: full_text
- **task and granularity**: Two phases: file-level graph classification (Sec. 3.2), then line ranking inside predicted-defective files (Sec. 3.3).
- **language and data**: Java;  Line-DP benchmark, 32 releases of 9 projects (Sec. 4.2, Table 1), incl. ActiveMQ 5.0.0, 5.1.0, 5.2.0, 5.3.0, 5.8.0.
- **representation**: Per-file refined program dependence graph (PDG): node types variable-definition / condition / execution; control-flow edges split into True / False / Next, plus data-flow edges (Sec. 3.1, Fig. 2). Each node's line text is extended with backward data flow, backward control flow, forward control flow and forward data flow lines (Sec. 3.1.1, Figs. 3-4), then embedded with Doc2Vec (dim 100, trained per project; Sec. 3.1.2, Sec. 4).
- **model**: Relational GCN (R-GCN) with global mean pooling + FC + sigmoid for file classification (Sec. 3.2, Eq. 4). Line ranking: GNNExplainer minimal subgraph, then risk score = normalised degree + Katz + closeness centrality (Sec. 3.3, Eqs. 5-11). 1000 epochs, Adam, BCE (Sec. 4).
- **baselines**: File level (Sec. 5.1): IVDetect, DeepLineDP, BoW+LR+SMOTE, DBN, CNN, Bi-LSTM, CodeT5, DeepBugs, LineVD. Line level (Sec. 5.2): N-gram, ErrorProne, LineVD, DeepLineDP. No GLANCE.
- **evaluation setup**: Release 1 train, release 2 validation, remaining releases test; 14 test releases (Sec. 5.1). Hyperparameters tuned over lr {0.01,0.001,0.0001}, batch {64,128,256}, dropout {0,0.2,0.5}, hidden {32,64,128} with early stopping on validation loss (Sec. 7.1). ScottKnott ESD across releases (Sec. 5.1).
- **cross version**: Yes at file and line level (Sec. 5.1): oldest release -> later releases (e.g., ActiveMQ 5.0.0 train, 5.1.0 val, 5.2.0/5.3.0/5.8.0 test, Table 2). Authors state they 'only validate LineFlowDP on cross-version SDP' (Sec. 7.2). Not method level.
- **graph based**: Yes: refined PDG (control-flow True/False/Next + data-flow edges; 3 node types) per file, R-GCN, GNNExplainer + SNA centrality. PDG extracted 'with the method of Nguyen et al. 2022' (Sec. 3.1); the extraction tool is not named in the text read. Graph is file level (file = one graph).
- **duplication or leakage handling**: None reported. No removal of files unchanged between training and test releases; Doc2Vec is trained 'on the corpus of each project' (Sec. 3.1.2) without stating that test releases are excluded, a possible transductive leak.
- **label source and noise**: Inherited from Line-DP dataset (Sec. 4.2); no discussion of SZZ/fix-diff label noise in threats (Sec. 7).
- **metrics and key results**: File level medians over 14 test releases (Sec. 5.1, Tables 2-3): AUC 0.800 vs DeepLineDP 0.816 (same ScottKnott rank); BA 0.657 vs DeepLineDP 0.577; GM 0.651 vs 0.507. ActiveMQ AUC: 5.2.0 0.872, 5.3.0 0.846, 5.8.0 0.804 (Table 2). Line level medians (Sec. 5.2): Recall@Top20%LOC 0.398 (DeepLineDP 0.314, LineVD 0.351, N-gram 0.151, ErrorProne 0.079); Effort@Top20%Recall 0.131 (DeepLineDP 0.133); IFA median 96, worse than LineVD, N-gram and DeepLineDP.
- **stated limitations**: Manual hyperparameter search costly (Sec. 7.1); Java-only, cross-version only; may not transfer to cross-project or JIT because commits do not form full PDGs (Sec. 7.2); LOC as effort proxy; limited metric set (Sec. 7.3).
- **critical assessment**: (1) No GLANCE/size baseline, and DeepLineDP numbers are likely produced with the original evaluation script whose LOC denominator Zhou et al. 2024 showed to be inflated; whether LineFlowDP's own denominator excludes comment and non-PDG lines is not stated, so the line-level comparison may not be like-for-like. (2) Many baselines have median BA < 0.5 (e.g., DBN 0.420, BoW 0.428; Sec. 5.1), i.e., worse than chance, indicating mis-thresholded or poorly reproduced baselines. (3) AUC is not better than DeepLineDP. (4) IFA median 96 means many clean lines are inspected before the first defect in a file. (5) Hyperparameters chosen on release 2, a single train release; no variance across seeds. (6) No duplicate/unchanged-file control. (7) Graph ablation compares flow extension vs no/contextual extension (RQ3), but there is no non-graph model on the same Doc2Vec features, so the contribution of the R-GCN itself is not isolated.
- **relevance to project**: Closest design to this project: Doc2Vec node features + PDG (CFG + data-dependence) + relational GNN, on the same ActiveMQ releases. Its file-level ActiveMQ AUCs (0.80-0.87) are a reference point, but the project should re-evaluate with method-level graphs, unchanged-method removal and GLANCE/size baselines. The R-GCN with typed CFG/DDG edges is directly reproducible with Joern output.

## Yin et al. (2024/2025). Line-Level Defect Prediction by Capturing Code Contexts With Graph Convolutional Networks (LineDef). IEEE TSE. (Full author list not verified.)
DOI: 10.1109/tse.2024.3503723

- **access**: abstract_only
- **task and granularity**: Joint file-level classification and line-level risk ranking (abstract).
- **language and data**: 32 datasets across 9 projects (abstract), almost certainly the Line-DP Java benchmark (inferred from counts, unverified).
- **representation**: Token embeddings; line-level and token-level graphs built with a sliding window over the code (abstract) - adjacency by proximity, not program semantics.
- **model**: Graph convolutional layers + attention producing file labels and line risk scores (abstract).
- **baselines**: State-of-the-art file-level and line-level DP approaches (abstract; names not verified).
- **evaluation setup**: Not verifiable from abstract.
- **cross version**: Unknown from abstract; likely the Line-DP release protocol (unverified). Not method level.
- **graph based**: Yes, but graphs are sliding-window co-occurrence graphs over tokens and lines, not AST/CFG/PDG (abstract). GCN.
- **duplication or leakage handling**: Not reported in abstract.
- **label source and noise**: Not reported in abstract (Line-DP labels if that benchmark).
- **metrics and key results**: Balanced accuracy +15.61% to +45.20% vs file-level SOTA; cost-effectiveness +15.32% to +278% vs line-level SOTA (abstract).
- **stated limitations**: Not available.
- **critical assessment**: Relative improvements only; no absolute values or GLANCE comparison visible in the abstract. A sliding-window graph is a local-context model, so 'graph-based' here does not mean program-structure-based. Independent comparison (10.1145/3793302.3793359) ranks LineDef second behind Bugsplorer in one scenario (search snippet).
- **relevance to project**: Shows that 'graph' in the line-level literature often means a window graph; the project's Joern CFG/DDG graphs should be compared against such a window-graph control to show program semantics matter.

## H-LineDef: Hierarchical Heterogeneous Graph Attention Networks for Multi-Granularity Line-Level Defect Prediction (2026). ACM proceedings. (Authors not verified.)
DOI: 10.1145/3806980.3807100

- **access**: abstract_only
- **task and granularity**: Joint file-level classification and line-level localization (abstract).
- **language and data**: Java; 32 project versions of 9 open-source systems (abstract; Line-DP benchmark inferred).
- **representation**: GraphCodeBERT token encodings (code + data flow); two-layer heterogeneous program graph combining AST, CFG and DFG at token and line level (abstract).
- **model**: Relational graph attention network, multi-relation message passing; multi-task file/line heads (abstract).
- **baselines**: 'State-of-the-art baselines' (names not in abstract; LineDef implied by name).
- **evaluation setup**: Within-project and cross-project settings (abstract); release pairing not stated.
- **cross version**: Within-project setting on versioned data, probably release-based, but not stated in abstract. Not method level.
- **graph based**: Yes: AST + CFG + DFG heterogeneous graph, token and line layers, relational GAT (abstract). Tool not stated.
- **duplication or leakage handling**: Not reported in abstract.
- **label source and noise**: Not reported (Line-DP labels presumably).
- **metrics and key results**: Average file-level AUC 0.795; F1@Top20%LOC up to +7.65% over the strongest baselines (abstract).
- **stated limitations**: Not available.
- **critical assessment**: File-level AUC 0.795 is not higher than DeepLineDP's 0.816 or LineFlowDP's 0.800 median reported elsewhere on the same benchmark (LineFlowDP Sec. 5.1), though averages vs medians and test sets may differ. 'Up to' improvement indicates best case. Uses an unusual line metric (F1@Top20%LOC). No GLANCE.
- **relevance to project**: Closest in representation to the project (AST+CFG+DFG relational GNN with a pretrained code encoder); useful as a design reference, but evidence quality is unknown until full text is read.

## Xie Y., Tao H., Chen H., Wang P., Wu L., Zhang Z. (2027). Multi-relational Graph Neural Networks with sequential context fusion for line-level defect prediction (LineCodeGSeq). Information and Software Technology 201:108376.
DOI: 10.1016/j.infsof.2026.108376

- **access**: abstract_only
- **task and granularity**: End-to-end joint file-level and line-level defect prediction (abstract fragment via ScienceDirect citing page).
- **language and data**: Not available.
- **representation**: Fusion of semantic, sequential and structural information (abstract fragment).
- **model**: Multi-relational GNN with sequential context fusion (title); joint learning across file/line supervision (abstract fragment).
- **baselines**: Not available.
- **evaluation setup**: Within-project and cross-project scenarios (abstract fragment).
- **cross version**: Not determinable; within-project scenario stated, release pairing unknown. Not method level.
- **graph based**: Yes, multi-relational GNN (graph type not stated in available text).
- **duplication or leakage handling**: Not available.
- **label source and noise**: Not available.
- **metrics and key results**: Claims superior localization efficiency and lower inspection cost (abstract fragment); no numbers available.
- **stated limitations**: Not available.
- **critical assessment**: Only a partial abstract was accessible (CrossRef returned 502; Elsevier full text not accessible). No assessment possible beyond noting it continues the file+line multi-task GNN line on the same type of benchmark.
- **relevance to project**: Low until full text is read; a candidate for multi-relational edge typing.

## AI-Based Line-Level Defect Prediction Using a Hybrid GNN Framework for Large-Scale Python Projects (GNNLineDef) (2026). IEEE SCSE. (Authors not verified.)
DOI: 10.1109/scse70081.2026.11499924

- **access**: abstract_only
- **task and granularity**: Line-level defect prediction and ranking (abstract).
- **language and data**: Python; 'a subset of open-source Python repositories' under limited compute (abstract); dataset not named.
- **representation**: CodeBERT line embeddings; BiLSTM over line sequence; lightweight Code Property Graph (abstract).
- **model**: CodeBERT + BiLSTM + GAT over line-level CPG (abstract).
- **baselines**: Not stated in abstract.
- **evaluation setup**: Preliminary experiments; split not stated (abstract).
- **cross version**: Not stated; cross-project evaluation listed as future work (abstract). Not method level.
- **graph based**: Yes: lightweight Code Property Graph (AST/CFG/PDG union, construction tool not stated), GAT (abstract).
- **duplication or leakage handling**: Not stated.
- **label source and noise**: Not stated.
- **metrics and key results**: BalAcc 82%, Recall@20% 78%, Effort@20% 1% (abstract).
- **stated limitations**: Limited scale and compute; needs fine-tuning, optimized graph construction, cross-project evaluation, XAI (abstract).
- **critical assessment**: Preliminary conference work; numbers (Recall@20% 0.78 with Effort@20% 0.01) are far above Java Line-DP results and resemble Bugsplorer's Defectors numbers, which suggests an easier (likely random/file-mixed) split; no baselines visible. Treat as anecdotal.
- **relevance to project**: One of very few Python graph-based line-level papers; confirms the Python + CFG/DDG gap rather than filling it.

## Zhou et al. (2024). Deep learning or classical machine learning? An empirical study on line-level software defect prediction. Journal of Software: Evolution and Process 36(10):e2696.
DOI: 10.1002/smr.2696

- **access**: full_text
- **task and granularity**: Replication/comparison: DeepLineDP vs GLANCE (MD, EA, LR) at file and line level (Sec. 4.1 RQ1-RQ3).
- **language and data**: Java; Line-DP benchmark, same data as DeepLineDP (Table 2): 9 projects, 32 releases, 14 test releases.
- **representation**: DeepLineDP: token sequences; GLANCE: NT, NFC, CE line features (Sec. 2).
- **model**: Original DeepLineDP and GLANCE replication packages (threats section).
- **baselines**: The two approaches compared against each other; composite models (GLANCE file stage + DeepLineDP line stage, Table 8).
- **evaluation setup**: Releases ordered chronologically. DeepLineDP: release 1 train, release 2 validation, releases 3..n test. GLANCE: sliding window release i -> i+1. Same 14 test releases for both (evaluation section). ScottKnott ESD (Sec. 4.5). Manual analysis of ~370 sampled true-positive lines per model (Sec. 4).
- **cross version**: Yes, at file and line level; DeepLineDP oldest->later releases, GLANCE i->i+1 (evaluation section). Not method level. Training data differ between the two approaches (DeepLineDP uses release 1 only), which confounds the comparison slightly.
- **graph based**: No.
- **duplication or leakage handling**: Not addressed.
- **label source and noise**: Affected-version labels from Line-DP; construct-validity threat on mislabelled files/lines acknowledged (threats section).
- **metrics and key results**: File level: GLANCE-EA/MD top ScottKnott rank on AUC; DeepLineDP lowest BA rank (Sec. 5.1, Figs. 1-2). Line level: all GLANCE variants outrank DeepLineDP on Recall@Top20%LOC (Fig. 4); Effort@Top20%Recall ~0.175 for GLANCE-EA/MD vs 0.266 for DeepLineDP (Sec. 5.2); IFA mean (median) GLANCE-MD 33.607 (25.500) vs DeepLineDP 41.464 (33.750) (Sec. 5.2, Table 3). Original DeepLineDP evaluation script counted comment lines in the LOC denominator, inflating Recall@Top20%LOC and Effort@Top20%Recall (Sec. 6.1, Table 6). Composite medians: GLANCE-EA Recall@Top20%LOC 0.191 vs EA-DeepLineDP 0.092 (Table 8).
- **stated limitations**: Label accuracy of the dataset; implementation bias mitigated by using original code (threats section).
- **critical assessment**: Strong, practically important replication: exposes an evaluation bug in the most-cited baseline and shows a heuristic wins. Weaknesses: only one DL model; different training windows for the two methods; no duplicate control; no variance over seeds reported in what was read.
- **relevance to project**: Direct evidence that complex models on this benchmark (which includes ActiveMQ) can be beaten by size/complexity heuristics and that evaluation scripts must be audited. Supports including size-only and GLANCE-style baselines and auditing metric denominators in the project.

## An Empirical Study on Deep Learning-based Line-Level Software Defect Prediction (2026). ACM proceedings. (Authors not verified.)
DOI: 10.1145/3793302.3793359

- **access**: abstract_only
- **task and granularity**: Comparative empirical study of eight DL line-level models; effect of fusing handcrafted features (abstract).
- **language and data**: 32 benchmark datasets from nine projects' releases (abstract) - Line-DP Java benchmark (inferred).
- **representation**: Models include DeepLineDP, SyntaxLineDP, LineFlowDP, Bugsplorer, LineDef, BAFLineDP (parameter table in search snippet); handcrafted features fused via two strategies (abstract).
- **model**: Eight SOTA DL LLDP models re-run (abstract).
- **baselines**: The eight models against each other; handcrafted-feature fusion variants (abstract).
- **evaluation setup**: Cross-version and cross-project scenarios; AUC, Recall@Top20%LOC, Effort@Top20%Recall, IFA (abstract).
- **cross version**: Yes, a cross-version scenario is stated (abstract); exact release pairing not verified. Not method level.
- **graph based**: Includes graph-based models (LineFlowDP R-GCN on PDG; LineDef GCN) among those compared; the study itself is not graph-based.
- **duplication or leakage handling**: Not reported in abstract.
- **label source and noise**: Line-DP labels presumably.
- **metrics and key results**: Statistically significant differences among models; no model always best; Bugsplorer generally best except IFA; rankings inconsistent between cross-version and cross-project; handcrafted-feature fusion improves performance and fusion strategy matters (abstract). Search snippet: Bugsplorer rank 1, LineDef 2, BAFLineDP 3 in one scenario.
- **stated limitations**: Not available.
- **critical assessment**: Useful independent re-run of graph and non-graph models under a common protocol. Abstract does not mention GLANCE or the DeepLineDP evaluation-script bug; whether corrected metrics were used is unknown. Note that the graph models (LineFlowDP, LineDef) are not reported as the top performers.
- **relevance to project**: Evidence that, under a shared protocol, PDG-based R-GCN does not dominate sequence/transformer models, and that handcrafted metrics add value - consistent with the project's plan to compare CFG/DDG graphs against doc2vec/CodeBERT and SonarQube metrics.

## Majd A. et al. (2020). SLDeep: Statement-level software defect prediction using deep-learning model on static code features. Expert Systems with Applications (DOI 10.1016/j.eswa.2019.113156). Co-authors and volume not verified.
DOI: 10.1016/j.eswa.2019.113156

- **access**: abstract_only
- **task and granularity**: Statement-level fault-proneness classification (abstract).
- **language and data**: C/C++; 119,989 programs from Code4Bench, 2,356,458 LOC of which 292,064 faulty (abstract).
- **representation**: 32 statement-level static metrics (e.g., number of binary/unary operators) (abstract).
- **model**: LSTM (abstract).
- **baselines**: Not stated in abstract.
- **evaluation setup**: Train/test on Code4Bench (programming-contest submissions, many versions by thousands of developers); split not stated in abstract.
- **cross version**: No evidence of release-based evaluation; the data are contest programs, not software releases. Not method level.
- **graph based**: No.
- **duplication or leakage handling**: Not stated. Code4Bench contains multiple versions of the same solutions, so near-duplicate statements across train/test are likely under a random split.
- **label source and noise**: Faulty lines derived from Code4Bench version differences (abstract implies); details unverified.
- **metrics and key results**: Recall 0.979, precision 0.570, accuracy 0.702 (abstract).
- **stated limitations**: Not available.
- **critical assessment**: Faulty lines are ~12% of lines (292,064/2,356,458), far above real-project rates (<1% in Line-DP, Table 1 of LineFlowDP), so results do not transfer. Recall 0.979 with precision 0.570 suggests a near 'predict-defective' classifier. Claims of cross-project utility rest on dataset diversity, not on a cross-project split.
- **relevance to project**: Low; illustrates that statement-level results on contest code are not comparable to release-based project data.

## Adediran E. et al. (2024/2025). BugsplorerPy: A Language-Proficient Transformer Model for Accurate Line-Level Defect Prediction in Python. SSRN preprint.
DOI: 10.2139/ssrn.5269511

- **access**: abstract_only
- **task and granularity**: Line-level defect prediction in Python (title/abstract fragment).
- **language and data**: Python; Defectors dataset mentioned (University of Ibadan journal snippet); details unverified.
- **representation**: Python-specific hybrid tokenization; token- and line-level contexts (snippets).
- **model**: Transformer extending Bugsplorer (hierarchical transformer) with Python-specific adaptations; claims to address cross-file dependencies (abstract fragment).
- **baselines**: Bugsplorer and DeepJIT named as prior tools (abstract fragment).
- **evaluation setup**: Not available.
- **cross version**: Not determinable. Parent dataset Defectors offers random and time-wise splits (Bugsplorer arXiv 2312.11889, Sec. IV-A).
- **graph based**: No (transformer); 'cross-file dependencies' mechanism not verified.
- **duplication or leakage handling**: Not available.
- **label source and noise**: Defectors labels: developer-labelled bug-fixing commits, then SZZ-style defect-inducing lines (Bugsplorer Sec. IV-A).
- **metrics and key results**: Not available.
- **stated limitations**: Not available.
- **critical assessment**: Only abstract fragments via third-party pages; SSRN full text not retrievable. Cannot assess.
- **relevance to project**: Potentially relevant as a Python line-level baseline; parent model Bugsplorer is assessed in additional papers.

## Theme synthesis
1. Protocol. Line-level papers almost all reuse the Line-DP Java benchmark (9 projects, 32 releases) and its release protocol: oldest release train, second release validation, later releases test (DeepLineDP via secondary sources; LineFlowDP Sec. 5.1; Zhou et al. 2024). This is cross-version, but at file and line level, never at method level, and test releases are often several versions after training rather than N->N+1. GLANCE uses i->i+1. None of the papers read in full removes files or lines unchanged between training and test releases, so the unchanged-code leakage this project studies is uncontrolled across the whole sub-field.
2. Evaluation reliability. Zhou et al. 2024 (smr.2696, Sec. 6.1) found that DeepLineDP's original evaluation script counted comment lines in the LOC denominator, inflating Recall@Top20%LOC and Effort@Top20%Recall. Later papers (LineFlowDP, Bugsplorer, LineDef, H-LineDef) compare against DeepLineDP numbers whose provenance is unclear. LineFlowDP reports baseline medians with BA < 0.5 (Sec. 5.1), which indicates poorly reproduced baselines. Bugsplorer reports Recall@Top20%LOC 0.985 on the Line-DP cross-release split versus 0.224 for DeepLineDP on the same split (arXiv 2312.11889, Table III), a gap large enough to warrant a check of the metric computation.
3. Simple baselines. GLANCE (size/complexity heuristic, partly unsupervised) matches or beats DL models (Guo et al. 2023 abstract; Zhou et al. 2024 Figs. 4-5). No graph-based line-level paper read in full (LineFlowDP) compares against GLANCE. Handcrafted-feature fusion improves DL models (10.1145/3793302.3793359 abstract).
4. Graph approaches. Program-structure graphs appear in LineFlowDP (refined PDG with typed control/data edges, R-GCN, GNNExplainer + centrality) and H-LineDef (AST+CFG+DFG heterogeneous relational GAT, GraphCodeBERT features; abstract only). LineDef's graphs are sliding-window graphs, not program graphs. In the independent comparison (3793302.3793359, abstract and snippet) the top model was a transformer (Bugsplorer), not a PDG/GCN model. Graph contribution is rarely isolated with a same-feature non-graph control.
5. Labels. All Java work inherits Line-DP labels: affected-version file labels and lines changed by bug-fix commits. Lines not touched by the fix are labelled clean; tangled fixes are not filtered. Python work uses Defectors (developer-labelled fixing commits plus SZZ-style inducing lines) or unnamed repositories.
6. Python. Only Bugsplorer (Defectors), BugsplorerPy and GNNLineDef target Python; none uses CFG/DDG graphs on releases; GNNLineDef is preliminary and has no visible baselines or split description.
7. Implications for this project: (a) the ActiveMQ 5.0.0->5.1.0->{5.2.0,5.3.0,5.8.0} protocol from LineFlowDP gives a published reference (file-level AUC 0.80-0.87, Table 2), but method-level, N->N+1, unchanged-method-filtered evaluation is a gap; (b) include size-only/GLANCE-style and metric baselines; (c) audit metric denominators; (d) isolate graph structure with a same-features non-graph control (e.g., doc2vec/CodeBERT node mean-pooling vs CFG/DDG R-GCN); (e) report MCC and effort-aware measures with variance across seeds.

## Additional papers found
- 10.48550/arXiv.2312.11889 - Mahbub P., Rahman M.M. (2024). Predicting Line-Level Defects by Capturing Code Contexts with Hierarchical Transformers (Bugsplorer). Read in full (arXiv). Hierarchical transformer; Defectors (Python, random and time-wise splits) and Line-DP cross-release/cross-project. Line-DP cross-release: BA 0.901, AuROC 0.920, Recall@20% 0.985, Effort@20% 0.037 vs DeepLineDP BA 0.538, Recall@20% 0.224 (Table III). Cross-release test set = latest release of each project, apparently one model pooled across projects (Sec. IV-A). Not graph-based.
- 10.1145/3707456 - Refining Code-Line-Level Bugginess Identification: Getting the Best of Both Worlds by Fusing Syntactic and Semantic Features (ACM TOSEM, 2025). Fuses GLANCE and DeepLineDP features. Not read.
- arXiv 2402.07132 - BAFLineDP: Code Bilinear Attention Fusion Framework for Line-Level Defect Prediction (2024). CodeBERT + Bi-GRU line context. Not read; arXiv ID verified via arXiv API.
- SyntaxLineDP: a Line-level Software Defect Prediction Model based on Extended Syntax Information (QRS 2023). Within-project results on Line-DP; DOI not verified.
- TRIA-LineDP: Telecontext-Enhanced Recursive Interactive Attention Fusion Method for Line-Level Defect Prediction (2024). DOI not verified.
- S0950584925003325 (Information and Software Technology, 2025) - Line-level defect prediction based on preceding line-aware and inter-line semantics enhancement. DOI not verified.
- Wattanakriengkrai S. et al. (2020). Predicting Defective Lines Using a Model-Agnostic Technique (LineDP), IEEE TSE - source of the Line-DP benchmark. DOI not verified here.
- Defectors: A Large, Diverse Python Dataset for Defect Prediction (MSR 2023) - Python line-level dataset with random and time-wise splits. DOI not verified here.
- Hin D. et al. (2022). LineVD: Statement-level vulnerability detection using graph neural networks (MSR 2022) - GNN on PDG statements, used as a baseline by LineFlowDP. DOI not verified here.
- JIT-Smart: A Multi-task Learning Framework for Just-in-Time Defect Prediction and Localization (10.1145/3643727, FSE 2024) - commit-level plus line localization.