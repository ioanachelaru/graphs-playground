# Cross-version methods: reading notes (method-level defect prediction review)

Scope: 8 assigned CVDP papers plus 5 added papers (Chowdhury 2024, Onet-Marian & Hotea 2025, Line-DP 2020/22, BugPre 2023, DI-GNN 2025).
Access: full text for Kabir 2023, Chowdhury 2024, Onet-Marian & Hotea 2025, Line-DP, BugPre, DI-GNN; preprint for Bangash 2020 and Cohen 2022; **abstract only** for Amasaki 2020, HALKP 2018, TSTSS 2019, Yang & Wen 2018, Wu 2026. Assessments of abstract-only papers are provisional.

## Summary table

| Paper | Access | Granularity | Cross-version split | Graph | Dedup/leakage control |
|---|---|---|---|---|---|
| Amasaki S. (2020) | abstract_only | Binary defect-proneness prediction of modules in a later… | Yes, release-based CVDP (older release(s) -> target release), but at… | No. | Not determinable from abstract. No indication that… |
| Xu Z., Liu J., Luo X., Zhang T. (2018) | abstract_only | Binary CVDP at module (class/file) level. Not method level. | Partly. Train on version N plus queried labels from version N+1, test… | No. | None reported. Kernel PCA is fitted on labelled and… |
| Xu Z., Li S., Luo X., Liu J., Zhang T., Tang Y., Xu J., Yuan P., Keung J. (2019) | abstract_only | Binary CVDP at module (class) level; not method level. | Yes, N -> N+1 at module/class level; not method level. | No. | None. Stage 2 uses the unlabeled current-version… |
| Yang X., Wen W. (2018) | abstract_only | Defect-count regression for ranking modules in the next… | Yes, N -> N+1, class level; not method level. | No. | None reported. |
| Kabir M.A., Rehman A.U., Islam M.M.M., Ali N., Baptista M.L. (2023) | full_text | Concept-drift (CD) detection across chronologically ordered… | Yes, release N (or window) -> N+1, chronological, for prop (class… | No. | None. Sec. 3.1 notes that current versions 'inherit… |
| Wu W., Ren X., Liu X., Xie W., Ye H., Huang B., Yang X., Yin L., Ping G. (2026) | abstract_only | Binary CVDP of modules; granularity not stated in abstract… | Yes, version -> later version per abstract; granularity not stated;… | No (per abstract). | None stated. The selection rule keeps the source… |
| Bangash A.A., Sahar H., Hindle A., Ali K. (2020) | preprint | Re-evaluation of 5 CPDP techniques (Amasaki15, Watanabe08,… | Time-aware but cross-project: no test-project versions in training… | No. | Gap bucket between train and test to limit label… |
| Cohen M., Rokach L., Puzis R. (2022) | preprint | Binary CVDP at class (module) level: train on V0, predict… | Yes, release N -> next available release (24 pairs), class level. Not… | Yes. Class Dependency Network extracted with… | None. Alignment relies on classes that exist and keep… |
| Chowdhury S., Uddin G., Hemmati H., Holmes R. (2024) | full_text | Method-level bug prediction (MLBP). Re-evaluates existing… | Yes for the Shippey data (all releases < x -> release x, method… | No. | Identifies leakage in the Mo et al. data set: change… |
| Onet-Marian Z., Hotea D.-L. (Miholca) | full_text | Analysis of train-test overlap in CVDP and its effect on… | Yes, N -> N+1 at class level. Not method level. | No. | This is the paper's subject. Common classes are… |
| Wattanakriengkrai S., Thongtanunam P., Tantithamthavorn C., Hata H., Matsumoto K. (2020/2022) | full_text | File-level defect model (token bag-of-words) plus LIME to… | Yes, release k-1 -> k, at file and line level (Sec. 6.5). | No. | None. Unchanged files appear in both releases. With… |
| Wang Z., Tong W., Li P., Ye G., Chen H., Gong X., Tang Z. (2023) | full_text | CVDP restricted to changed and change-impacted functions of… | Yes, N -> N+1. Test units are changed/impacted functions of N+1, so… | Yes. AST + CFG + data-flow + call edges per… | Only changed and impacted functions are predicted, so… |
| Yang F., Zhong F., Wei X., Zeng G. (2025) | full_text | File-level defect prediction plus statement-level risk… | Yes for file level (version N -> N+1, Sec. 5.1). Statement level… | Yes. PDG (CDG + DDG). The extraction tool… | None. Slicing is applied only to training files (Sec.… |

## Per-paper notes

### 1. Amasaki S. (2020). Cross-version defect prediction: use historical data, cross-project data, or both? Empirical Software Engineering 25(2):1573-1595.

- **DOI:** 10.1007/s10664-019-09777-8
- **Access:** abstract_only
- **Task and granularity:** Binary defect-proneness prediction of modules in a later release. Module granularity is not stated in the material available; the data is described by citing work as the SEACRAFT/Jureczko class-level sets (Onet-Marian & Hotea 2025, Sec. 3.2). Not method level.
- **Language and data:** Java class-level Jureczko/PROMISE releases (per citing work). The PROMISE'18 predecessor (10.1145/3273934.3273938) used 11 projects with 3-5 versions each and 20 CPDP techniques (as summarised in Cohen et al. 2022, Sec. 2.1). Exact EMSE data set not verified.
- **Representation:** Static code metrics (class-level), inferred from data set; not verified.
- **Model:** CPDP techniques from the CrossPare benchmark, applied to CVDP training data (per Springer abstract snippet and ResearchGate figure captions 'Baseline approaches in CrossPare', 'Classifiers for CPDP approaches in CrossPare').
- **Baselines:** ASIS (training on raw older release data) under different scenarios; a ResearchGate table caption refers to 'final rank list of approaches better than ASIS (SFV)'. Citing work names the scenarios SFV (single farthest version), SPV (single prior version), APV (all prior versions).
- **Evaluation setup:** Release-based: train on older release(s) of the same project, optionally plus cross-project data, test on the next release. Scenario details from abstract snippets and citing works only.
- **Cross-version (method/function/line?):** Yes, release-based CVDP (older release(s) -> target release), but at class/module level, not method/function/line level. Exact split details not read.
- **Graph-based:** No.
- **Duplication / leakage handling:** Not determinable from abstract. No indication that unchanged/duplicate classes across releases were removed.
- **Label source and noise:** Not determinable from abstract; Jureczko labels are post-release defect counts mapped to classes.
- **Metrics and key results:** Abstract (Springer page): the latest prior release was the best training choice; some CPDP approaches could improve CVDP; older releases brought no clear benefit when the latest release is available; with no CVDP data, CPDP data could give quality predictions. Numeric results not available to me.
- **Stated limitations:** Not available (abstract only).
- **Critical assessment:** Its main conclusion (use the latest prior release) is now a de facto default in CVDP (e.g. Bangash/Amasaki citations; Onet-Marian & Hotea 2025 Sec. 2). Onet-Marian & Hotea show that the most recent prior release is also the one with the most identical instances, so 'latest release is best' may partly reflect train-test overlap rather than better generalisation. This was not checked by Amasaki as far as the abstract shows. Class-level metric data only.
- **Relevance to project:** Supports using release N to predict N+1 as the default scenario, and offers SFV/SPV/APV as named training-window variants. The finding should be re-tested on Django/ActiveMQ after removing unchanged methods.

### 2. Xu Z., Liu J., Luo X., Zhang T. (2018). Cross-version defect prediction via hybrid active learning with kernel principal component analysis. SANER 2018, pp. 209-220.

- **DOI:** 10.1109/saner.2018.8330210
- **Access:** abstract_only
- **Task and granularity:** Binary CVDP at module (class/file) level. Not method level.
- **Language and data:** 31 versions of 10 projects (abstract); a citing survey states the data is from the MORPH data sets (IOP 2020 survey snippet), i.e. PROMISE/Jureczko Java class-level metrics.
- **Representation:** Static code metrics, mapped with kernel PCA.
- **Model:** Two phases: (1) hybrid active learning picks informative and representative unlabeled modules of the current version, queries their labels and merges them with the prior-version training set; (2) kernel PCA maps both versions to a non-linear feature space; then a standard classifier.
- **Baselines:** 'Nearly all baseline methods' (abstract); variants HAL and HALPCA are named in a ResearchGate preview. Exact list not read.
- **Evaluation setup:** Prior version + actively-labelled part of current version -> remaining unlabeled modules of the current version (abstract; Onet-Marian & Hotea 2025 Sec. 2).
- **Cross-version (method/function/line?):** Partly. Train on version N plus queried labels from version N+1, test on the rest of N+1. This is not a clean N -> N+1 split; class/module level only.
- **Graph-based:** No.
- **Duplication / leakage handling:** None reported. Kernel PCA is fitted on labelled and unlabeled data of both versions (transductive), so test-set feature information enters the representation.
- **Label source and noise:** PROMISE/Jureczko labels (inferred from data source); oracle labels for queried modules are assumed to be correct.
- **Metrics and key results:** Average F-measure 0.480, g-mean 0.592, Balance 0.580 over the cross-version pairs (abstract).
- **Stated limitations:** Not available (abstract only).
- **Critical assessment:** Active learning labels part of the target release, which uses future labels that are not available at release time (Onet-Marian & Hotea 2025 Sec. 2 make the same point). Transductive KPCA uses the test features. Only threshold-dependent metrics (F, g-mean, Balance) are reported. These numbers are later quoted as baselines in BugPre Table 9, apparently copied rather than re-run.
- **Relevance to project:** Low. It is an example of a protocol that should be avoided, because labels from the test release enter training.

### 3. Xu Z., Li S., Luo X., Liu J., Zhang T., Tang Y., Xu J., Yuan P., Keung J. (2019). TSTSS: A two-stage training subset selection framework for cross version defect prediction. Journal of Systems and Software 154:59-78.

- **DOI:** 10.1016/j.jss.2019.03.027
- **Access:** abstract_only
- **Task and granularity:** Binary CVDP at module (class) level; not method level.
- **Language and data:** 50 cross-version pairs (abstract); per Cohen et al. 2022 Sec. 2.1, static metrics only. Projects not verified.
- **Representation:** Static code metrics.
- **Model:** Stage 1: sparse modeling representative selection (SMRS) picks prior-version modules that reconstruct the prior version. Stage 2: dissimilarity-based sparse subset selection (DS3) refines them to represent the current version's modules. Classifier: a weighted extreme learning machine.
- **Baselines:** 11 baseline methods (abstract), including the DS3-only approach (Xu et al. 2018, 10.1145/3196321.3196331) per Cohen et al. Sec. 2.1.
- **Evaluation setup:** Prior version (subset) -> current version; 50 pairs, 6 indicators (abstract). Cohen et al. state that both classification and effort-aware measures were used.
- **Cross-version (method/function/line?):** Yes, N -> N+1 at module/class level; not method level.
- **Graph-based:** No.
- **Duplication / leakage handling:** None. Stage 2 uses the unlabeled current-version features to choose training data (transductive). This selects training modules close to test modules and so may favour unchanged duplicates.
- **Label source and noise:** Not determinable from abstract.
- **Metrics and key results:** TSTSS 'can efficiently improve the CVDP performance compared with 11 baseline methods' (abstract); no numbers available.
- **Stated limitations:** Not available (abstract only).
- **Critical assessment:** Similarity-driven selection of training data is the mechanism that Onet-Marian & Hotea 2025 identify as inflating CVDP evaluation: matching training data to the test distribution favours identical carried-over instances. Without de-duplication, the gains cannot be separated from memorisation.
- **Relevance to project:** Use it as a strong but leakage-prone CVDP baseline family (SMRS/DS3). Any re-implementation on Django/ActiveMQ should report results with and without unchanged methods.

### 4. Yang X., Wen W. (2018). Ridge and Lasso Regression Models for Cross-Version Defect Prediction. IEEE Transactions on Reliability 67(3):885-896.

- **DOI:** 10.1109/tr.2018.2847353
- **Access:** abstract_only
- **Task and granularity:** Defect-count regression for ranking modules in the next version (class level, PROMISE). Not method level.
- **Language and data:** 11 PROMISE projects with 41 versions (abstract); Java class-level metrics.
- **Representation:** Static code metrics.
- **Model:** Ridge regression (RR) and lasso regression (LAR).
- **Baselines:** Linear regression, negative binomial regression, and the two best methods from the authors' previous study (abstract).
- **Evaluation setup:** Train on previous version, predict the next version (abstract).
- **Cross-version (method/function/line?):** Yes, N -> N+1, class level; not method level.
- **Graph-based:** No.
- **Duplication / leakage handling:** None reported.
- **Label source and noise:** PROMISE defect counts; not discussed in abstract.
- **Metrics and key results:** Severe multicollinearity exists; RR and LAR beat LR and NBR for CVDP; RR is comparable to the previous best methods with lower training time (abstract). Ranking metric not stated in abstract.
- **Stated limitations:** Not available (abstract only).
- **Critical assessment:** Simple and well-motivated baseline. For ranking by defect count, carried-over classes with stable counts would make the ranking easy; this is not controlled. Not relevant to graphs.
- **Relevance to project:** Indicates that regularised linear models on metrics are a cheap baseline for effort-aware ranking. This matters if SonarQube metrics are used as the baseline.

### 5. Kabir M.A., Rehman A.U., Islam M.M.M., Ali N., Baptista M.L. (2023). Cross-Version Software Defect Prediction Considering Concept Drift and Chronological Splitting. Symmetry 15(10):1934.

- **DOI:** 10.3390/sym15101934
- **Access:** full_text
- **Task and granularity:** Concept-drift (CD) detection across chronologically ordered versions, using the error rate of a Naive Bayes defect classifier. The prop sets are class level. The JM set (NASA metrics, Table 3) is function/module level, but its 'versions' are not real releases (see critique).
- **Language and data:** 30 versions of 7 projects from SEACRAFT (Sec. 3.1, Table 1): prop-1..prop-5 and prop-42 (Jureczko proprietary Java, 20 OO metrics, Table 2) and jm with 'versions' 1, 1.2, 1.3 (21 NASA metrics, Table 3).
- **Representation:** Static code metrics (CK/OO metrics for prop; McCabe/Halstead for jm).
- **Model:** Naive Bayes as single base learner (Sec. 3.5). CDD framework: data streams -> CD/warning/control flags -> adaptation (Sec. 3.2-3.3). Chi-square with Yates correction, Cliff's delta, Nemenyi test.
- **Baselines:** No competing predictors; the three window strategies are compared with each other: window-of-size-n (all history), size-1, size-2 (Sec. 3.3, 3.5).
- **Evaluation setup:** Chronological splitting: train on the previous window, test on the next version, rolling forward (Sec. 3.5, prop-1 example). Metrics: error rate (1 - accuracy) and pf (Sec. 3.5).
- **Cross-version (method/function/line?):** Yes, release N (or window) -> N+1, chronological, for prop (class level). jm is function level, but its 'versions' 1/1.2/1.3 are not documented releases. Not a method-level CVDP study.
- **Graph-based:** No.
- **Duplication / leakage handling:** None. Sec. 3.1 notes that current versions 'inherit many modules from the prior versions' but does nothing about it. Table 1 shows jm 1 and jm 1.3 with identical statistics (7782 modules, 1672 faulty, 21.49%, same skew/kurtosis), which suggests a duplicated data set.
- **Label source and noise:** Uses SEACRAFT labels as given; no discussion of label noise.
- **Metrics and key results:** Table 8 (window-of-size-1): significant CD (p<0.05) for prop-1 44->92 (p=0.026) and 92->128 (p=0.027), prop-2 245 (p=0.050), prop-4 347 (p=0.030), prop-5 40 (p=0.046), prop-42 453 (p=0.045), jm 1->1.2 (p=0.033). Table 9: these pairs have large Cliff's delta (0.437-0.497); window-of-size-1 gives the largest effect for CD detection (delta>=0.427, Sec. 4). The headline claim is an 'exponential increase in error-rate' with CD (abstract, Sec. 4).
- **Stated limitations:** CDD requires class labels in the test data (Sec. 6, External validity). Single learner NB is a potential bias (Sec. 6, Internal validity).
- **Critical assessment:** (1) Drift is detected from test-set error, so labels of the future release are needed; it cannot be used for prospective decisions (the authors acknowledge this). (2) Only accuracy-based error rate and pf are used, on data with 2-36% defects; no AUC/MCC. (3) The JM 'versions' look like re-cuts of the same NASA JM1 data (identical rows for 1 and 1.3 in Table 1), so the jm CVDP result is not credible. (4) Significance flags are inconsistent: prop-42 453->454 has p=0.065 in Table 9 but is listed as significant, and prop-2 245 has p=0.050. (5) A single NB learner. (6) No handling of carried-over modules, so 'drift' mixes real change with label flips on unchanged modules.
- **Relevance to project:** Gives terminology (window-of-size-1/2/n, full- vs no-memory) for multi-release training on Django's 24 releases. The evidence that window-1 is best is weak. A drift analysis should use labels-free distribution tests on features (e.g. graph statistics) instead.

### 6. Wu W., Ren X., Liu X., Xie W., Ye H., Huang B., Yang X., Yin L., Ping G. (2026). A novel cross version software defect prediction method based on adversarial validation strategy. Array, 101239.

- **DOI:** 10.1016/j.array.2026.101239
- **Access:** abstract_only
- **Task and granularity:** Binary CVDP of modules; granularity not stated in abstract (likely file/class level given baselines TSTSS/SMRS/DS3). Not shown to be method level.
- **Language and data:** 27 groups of open-source datasets (abstract). Specific data not verified.
- **Representation:** Not stated in abstract (presumably static metrics).
- **Model:** AVDP: an adversarial-validation binary classifier separates source (old version) from target (new version) instances; source samples with highest 'target-likeness' probability are retained; a supervised classifier is trained on the refined set (abstract).
- **Baselines:** TSTSS, SMRS, DS3 and state-of-the-art classifiers (abstract).
- **Evaluation setup:** Source version(s) -> target version; AUC, MCC, F-measure; Scott-Knott ESD (abstract).
- **Cross-version (method/function/line?):** Yes, version -> later version per abstract; granularity not stated; not shown to be method level.
- **Graph-based:** No (per abstract).
- **Duplication / leakage handling:** None stated. The selection rule keeps the source samples most similar to the target distribution, which favours unchanged/duplicated modules that also appear in the test version.
- **Label source and noise:** Not determinable from abstract.
- **Metrics and key results:** Abstract claims efficacy over TSTSS, SMRS and DS3 in mitigating concept drift; no numbers available. Full text (CC BY-NC, Elsevier) was not retrievable without an Elsevier API key.
- **Stated limitations:** Not available (abstract only).
- **Critical assessment:** Uses the unlabeled target features in training-set selection (transductive). It shares the main risk of TSTSS/DS3: keeping training instances indistinguishable from test instances favours identical carried-over modules, which Onet-Marian & Hotea 2025 show inflates CVDP metrics. The reported MCC/AUC (an improvement over F1-only papers) cannot be read as generalisation without a de-duplicated evaluation.
- **Relevance to project:** Adversarial validation is a cheap diagnostic. Training a classifier to separate release N from N+1 methods quantifies shift and can flag near-duplicates (AUC near 0.5 means the releases cannot be told apart). Use it as a diagnostic, not as a training-set filter.

### 7. Bangash A.A., Sahar H., Hindle A., Ali K. (2020). On the time-based conclusion stability of cross-project defect prediction models. Empirical Software Engineering 25:5047-5083 (arXiv:1911.06348v3).

- **DOI:** 10.1007/s10664-020-09878-9
- **Access:** preprint
- **Task and granularity:** Re-evaluation of 5 CPDP techniques (Amasaki15, Watanabe08, CamargoCruz09, Nam15, Ma12; Sec. 4.1) under time-aware splits; class level.
- **Language and data:** 'FilterJureczko': 33 versions of 14 open-source Java projects with 20 static product metrics, class level (Sec. 4.2), spanning Nov 1999-Feb 2009 (Sec. 4.3).
- **Representation:** Static product metrics.
- **Model:** C4.5 decision tree in Weka after each technique's data treatment (Sec. 4.5).
- **Baselines:** 'HerboldMethod', the time-agnostic re-implementation of Herbold et al. 2018 benchmark (Sec. 5.2, Table 10).
- **Evaluation setup:** Releases sorted by date into 6-month buckets; split points divide past/future; one bucket gap between train and test 'to reduce the possible chances of time-travel' (Sec. 3.4). Four configurations CC/IC/CI/II with window sizes 1-19/1-18 (Sec. 4.4); strict CPDP (no test project in train). About 18,000 Tr-Test pairs per technique (Sec. 4.4).
- **Cross-version (method/function/line?):** Time-aware but cross-project: no test-project versions in training (Sec. 4.4). So not CVDP in the within-project sense; class level only.
- **Graph-based:** No.
- **Duplication / leakage handling:** Gap bucket between train and test to limit label time-travel (Sec. 3.4). Strict project exclusion removes cross-version duplicates by construction.
- **Label source and noise:** Jureczko class-level defect counts; noise not studied; Sec. 6.2 lists noise as a possible factor.
- **Metrics and key results:** F-score, AUC, MCC, G-measure (Table 10). Example (Table 10, all configurations vs HerboldMethod): Nam15 F 0.487 vs 0.492, MCC 0.230 vs 0.235, AUC 0.637 vs 0.641; CamargoCruz09 MCC 0.116 vs -0.086, AUC 0.553 vs 0.468. Differences are statistically significant (Wilcoxon) but have small/negligible Cliff's delta (Sec. 5.2). F-score for a fixed window varies 0.2-0.6 and occasionally 0.8 (Sec. 6.2, Fig. 10). Technique ranks change across split points (Fig. 9).
- **Stated limitations:** Uneven spread of projects over time (Xerces early, Camel late); smaller subsets increased SD (Sec. 6.2.1, Table 13); possible effects of data size and imbalance (Sec. 6.2.2-6.2.3); limited data set.
- **Critical assessment:** Methodologically sound on time ordering (gap bucket, no future data). Internal inconsistencies: '18 buckets' (Sec. 4.3) vs Fig. 2 caption '19 time buckets'; '~18,000 Tr-Test pairs per technique' (Sec. 4.4) vs '976 separate defect prediction models' per technique (Sec. 4.5). Absolute performance is weak overall (AUC 0.55-0.64). The paper shows that rankings depend on the time window but does not separate time effects from the project-mix confound, as the authors admit. Class level only.
- **Relevance to project:** The strongest template for time-aware protocol design: date-ordered buckets, a gap release between train and test to let SZZ labels mature, and reporting variance across many split points rather than one pair. With 24 Django releases, results should be reported as distributions over N -> N+1 (or N -> N+2 with a gap) pairs.

### 8. Cohen M., Rokach L., Puzis R. (2022). Cross Version Defect Prediction with Class Dependency Embeddings. arXiv:2212.14404 (preprint submitted to Expert Systems with Applications).

- **DOI:** 10.48550/arxiv.2212.14404
- **Access:** preprint
- **Task and granularity:** Binary CVDP at class (module) level: train on V0, predict defective classes in V1 (Sec. 3.1). Not method level.
- **Language and data:** 9 Java projects (Camel, JEdit, Log4J, Lucene, POI, Synapse, Velocity, Xalan, Xerces), 24 consecutive version pairs (Table 3), Jureczko metrics (Sec. 4). Source code of each version, including tests, downloaded to build the graph (Sec. 4). Only classes with both metrics and an embedding are kept (Sec. 4, Table 4: e.g. Camel avg |V| 1312, |V∩MDS| 664, 19.7% defective).
- **Representation:** 20 static code metrics (Table 1) concatenated with 32-d node embeddings of the class dependency network (Sec. 3.6, 4).
- **Model:** Random Forest (30 repetitions; Sec. 3.6); a logistic-regression meta-model over the LINE and node2vec models (Sec. 5.0.2).
- **Baselines:** Static metrics only; embeddings without alignment; linear-regression alignment; random-anchor alignment (Sec. 4.0.1-4.0.5).
- **Evaluation setup:** Consecutive version pairs from the data set (sometimes large version jumps, Sec. 4). AUC and F1, Wilcoxon signed-rank (Sec. 4).
- **Cross-version (method/function/line?):** Yes, release N -> next available release (24 pairs), class level. Not method/function/line level.
- **Graph-based:** Yes. Class Dependency Network extracted with the authors' own Java source parser, two passes over ASTs (Sec. 3.3). 10 typed edges: Extends, Implements, Return Type, Variable, Class Member, Object Instantiation, Annotation, Parameter, Static Class Member, Static Method Call (Table 2). The graph is reduced to a directed, untyped, unweighted graph for embedding (Sec. 3.4). node2vec (p=q=1) and LINE (2nd order), dim 32 (Sec. 4). No GNN. Embeddings of V1 are aligned to V0 by orthogonal Procrustes or linear regression, using anchor classes present in both versions, chosen by KNN-neighbourhood overlap or graph-neighbour Jaccard-like score (Sec. 3.5).
- **Duplication / leakage handling:** None. Alignment relies on classes that exist and keep the same neighbourhood in both versions (the anchors), which are the unchanged/duplicate classes. Their training labels transfer directly to the test release.
- **Label source and noise:** Jureczko labels as provided; not discussed.
- **Metrics and key results:** Meta-model improves AUC by 4.7% over the static-metrics baseline, p<0.002 (abstract, Sec. 5.0.2). Best single models: LINE + orthogonal + graph-similarity anchors (p=0.01), node2vec + orthogonal + KNN anchors (p<0.043) (Sec. 5.0.1). F1 within about ±0.5% of baseline (Sec. 5.0.1); not significant (Sec. 7.1). Per-project values only in Figures 3-8 (not extracted).
- **Stated limitations:** Only AUC and F1; slight F1 decrease (Sec. 7.1). One data set (Jureczko), Java only (Sec. 7.2). Single old version only; MOV left for future work (Sec. 8).
- **Critical assessment:** (1) Model selection on the test pairs: the 'best' configurations (embedding x alignment x anchor method x number of anchors, K) are picked by test AUC (Sec. 5.0.1, 5.0.3-5.0.4, Figs. 5-6), and the meta-model combines these best configurations. The 4.7% gain is therefore optimistic. (2) No F1 gain, so the AUC gain does not translate to the threshold-based decision. (3) Restricting to classes that have an embedding changes the population and defect rates (Table 4, e.g. Lucene 55.5%, Velocity 59% defective). (4) Duplicate/unchanged classes are not controlled, and they are exactly what the alignment relies on. (5) Graph is inter-class, not intra-method CFG/DDG.
- **Relevance to project:** This is the only CVDP paper in this set that explicitly handles the problem that graph embeddings learnt separately per release are not comparable. For Joern CFG/DDG embeddings (graph2vec, or GNNs trained per release), either train one encoder on release N and apply it inductively to N+1, or align the embedding spaces. Note that alignment anchors are unchanged methods and so must be excluded from the test set.

### 9. Chowdhury S., Uddin G., Hemmati H., Holmes R. (2024). Method-level Bug Prediction: Problems and Promises. ACM Transactions on Software Engineering and Methodology 33(4).

- **DOI:** 10.1145/3640331
- **Access:** full_text
- **Task and granularity:** Method-level bug prediction (MLBP). Re-evaluates existing MLBP models in time-sensitive scenarios (RQ1) and explores four improvement avenues (RQ2-RQ5). Method level.
- **Language and data:** Three public Java method-level data sets: Ferenc et al., Shippey et al., Mo et al. (Sec. 3.1, Table 1). A new data set of 774,051 Java methods from 49 projects, of which 146,749 are getters/setters (Sec. 3.2, Table 2), with method histories from CodeShovel (Sec. 3.2.2).
- **Representation:** Code metrics (size, McCabe, readability, fan-out, maintainability index) for the new data set (Sec. 3.2.2); original features for the public sets.
- **Model:** Weka classifiers as in the original studies (Random Forest, Random Tree, SimpleLogistic, DecisionTable etc.; Tables 3-5).
- **Baselines:** The originally reported 10-fold cross-validation results (Tables 3-5).
- **Evaluation setup:** Three realistic scenarios (Sec. 4): (i) cross-project; (ii) cross + past; (iii) only past. For Shippey (which has release numbers), all releases before x train and release x tests. For Ferenc, the first half of the project lifetime trains and the second half tests (Fig. 1 caption). The Mo set lacks time information, so only scenario i (Fig. 3).
- **Cross-version (method/function/line?):** Yes for the Shippey data (all releases < x -> release x, method level; Sec. 4). The Ferenc data uses a time split (first half -> second half of lifetime), method level. RQ2-RQ5 analyses on the new data set are distributional or single-scenario, not release-to-release prediction.
- **Graph-based:** No.
- **Duplication / leakage handling:** Identifies leakage in the Mo et al. data set: change counts over the whole method lifetime act as future information (Sec. 4). Uses CodeShovel to track method versions; labels per method version (Sec. 5.1). Does not de-duplicate unchanged methods between train and test releases.
- **Label source and noise:** RQ2 compares a 'traditional' keyword-based labelling (Ray et al. keywords) with an 'accurate' one. In the accurate set, a method is buggy only if it is the sole method changed in a commit with a bug word and a fix word in the same sentence. A method version is not buggy only if unchanged for at least 2 years with no later bug/fix-keyword commit (Sec. 5.1). About 60% of bug-fix commits modify more than one method and over 15% modify at least 10 (Fig. 4).
- **Metrics and key results:** RQ1: Ferenc scenario i, precision about 0.37 or less and F1 about 0.50 or less for 80% of projects (Fig. 1). Shippey scenario i, precision about 0.13 and F1 about 0.25; scenarios ii/iii somewhat better but far below CV (Fig. 2, Table 4). RQ2: in the traditional data, the size effect between buggy and clean methods is negligible in 30.61% (15) of projects; in the accurate data it is large in 97.67% (Sec. 5.1, Table 6; 6 projects excluded for fewer than 10 buggy samples). RQ3: bug-proneness decays with method age. RQ4: training-project selection matters. RQ5: model small and large methods separately (Sec. 5.2-5.4 summaries).
- **Stated limitations:** Only three public MLBP data sets exist; all Java (Sec. 7). Keyword choice and CodeShovel string matching (problematic for overloading) threaten construct validity. Bug age is approximated by fix time (Sec. 7).
- **Critical assessment:** RQ1 is strong evidence that method-level results collapse under time-aware evaluation. RQ2's claimed improvement is shown only through univariate Cliff's delta between groups, not through a time-aware predictive model. The 'accurate' set is also highly selective: it drops multi-method fixes and requires clean methods to be stable for 2 years. That condition correlates with small, simple methods, so the size separation is partly built in. Scenario ii/iii for Ferenc uses a lifetime half-split rather than releases. No de-duplication of unchanged methods across the split. Getters/setters (19%) are kept, which inflates the easy-negative pool.
- **Relevance to project:** Highly relevant. It supports the project's leakage angle, gives SZZ/tangled-fix noise statistics for method-level labels, and suggests age and size stratification as controls. Its unchanged-for-2-years rule is a usable conservative negative label for Django methods. Report results separately for small vs large methods.

### 10. Onet-Marian Z., Hotea D.-L. (Miholca) (2025). Cross-Version Defect Prediction: Does Excessive Train-Test Similarity Affect the Reliability of Evaluation? ENASE 2025, pp. 304-315.

- **DOI:** 10.5220/0013481700003928
- **Access:** full_text
- **Task and granularity:** Analysis of train-test overlap in CVDP and its effect on measured performance; class level.
- **Language and data:** All SEACRAFT sets with at least two versions and class names: 11 systems, 39 versions, 28 consecutive pairs (Table 1, Sec. 3.2): camel, jedit, forrest, ivy, log4j, lucene, poi, synapse, velocity, xalan, xerces; 20 Jureczko metrics.
- **Representation:** 20 OO metrics.
- **Model:** Random Forest, AdaBoost, XGBoost with default hyperparameters; number of trees = min(100, n_train/4); 30 runs (Sec. 3.4).
- **Baselines:** Not a method comparison; compares test subsets (Sec. 3.4).
- **Evaluation setup:** Train on version v1; test on (1) v1 itself, (2) all of v2, (3) common classes with changed label, (4) common classes with same label, (5) new classes (Sec. 3.4). AUC and MCC.
- **Cross-version (method/function/line?):** Yes, N -> N+1 at class level. Not method level.
- **Graph-based:** No.
- **Duplication / leakage handling:** This is the paper's subject. Common classes are matched by fully qualified name (short name for ivy) (Sec. 3.3); identical feature vectors, cosine distances and nearest neighbours are measured, and test sets are stratified by changed/unchanged label.
- **Label source and noise:** SEACRAFT labels (defect count binarised). Identical vectors with changed labels may be label errors or metrics insensitive to change (Sec. 4.1).
- **Metrics and key results:** RQ1 (Sec. 4.1): on average 72% (median 79%) of v2 classes also exist in v1; 13 pairs above 80%. Of common classes, 65% (mean) keep their label; mean 35% (median 31%) have identical feature vectors, about 80% for poi 2.0-2.5 and xerces 1.2-1.3/1.3-1.4. Median cosine distance is near 0; only 101 of 8608 common classes are above 0.1. For a median 73% of common classes, the nearest neighbour in v1 is the same-named class. RQ2 (Sec. 4.2): MCC on all of v2 ranges -0.157 to 0.54 (RF), -0.23 to 0.43 (AdaBoost), 0 to 0.55 (XGBoost). Same-label common classes score like training data; changed-label classes have mostly negative MCC (RF minimum -0.98; XGBoost -0.95 to 0). Performance on v2 correlates about +0.5 with % common classes and about -0.5 with % changed-label classes (Fig. 11).
- **Stated limitations:** Randomness (30 runs); generalisation to other models/data; only AUC and MCC; reliance on data set labels (Sec. 5).
- **Critical assessment:** Clear and directly relevant evidence, with sensible metrics (MCC, AUC). Limitations: (1) identity is defined on metric vectors, not on code, so 'identical' may hide code changes. (2) Matching by name ignores renames (ivy handled ad hoc). (3) Default hyperparameters. (4) Correlations over 28 pairs only; no proposed corrected protocol. (5) Class level only; the effect at method level, where many more units are unchanged, is untested.
- **Relevance to project:** Core reference for the leakage argument. Adopt its stratified evaluation (new / unchanged-same-label / changed-label methods) for Django and ActiveMQ. Extend it with code-level identity (normalised method body hash, or Joern graph isomorphism hash) instead of metric-vector identity.

### 11. Wattanakriengkrai S., Thongtanunam P., Tantithamthavorn C., Hata H., Matsumoto K. (2020/2022). Predicting Defective Lines Using a Model-Agnostic Technique (Line-DP). IEEE Transactions on Software Engineering 48(5):1480-1496.

- **DOI:** 10.1109/tse.2020.3023177
- **Access:** full_text
- **Task and granularity:** File-level defect model (token bag-of-words) plus LIME to rank risky tokens; lines containing risky tokens are predicted defective. Line level (and file level).
- **Language and data:** 32 releases of 9 Apache Java systems from Yatish et al.'s affected-version data set (Sec. 6.1), including ActiveMQ 5.0.0/5.1.0/5.2.0/5.3.0/5.8.0. These are the same ActiveMQ releases used in this project.
- **Representation:** Code-token frequency vectors (file level).
- **Model:** Logistic regression file-level model + LIME (Line-DP).
- **Baselines:** Random guessing, PMD, ErrorProne, NLP n-gram approach, two traditional model-interpretation approaches (LR, RF) (Sec. 6.3).
- **Evaluation setup:** Within-release: stratified 10x10-fold CV. Cross-release: train on release k-1, test on release k for every consecutive pair; 23 pairs (Sec. 6.5 'Validation Settings').
- **Cross-version (method/function/line?):** Yes, release k-1 -> k, at file and line level (Sec. 6.5).
- **Graph-based:** No.
- **Duplication / leakage handling:** None. Unchanged files appear in both releases. With affected-version labelling, a bug affecting releases k-1 and k labels the same unchanged file (and lines) defective in both, so the test label can be memorised.
- **Label source and noise:** Bug reports (JIRA, type Bug, affecting the studied release, closed/fixed); fix commits found by issue ID in the commit message. Lines modified by fix commits that exist in the release are defective (Sec. 6.2). The authors acknowledge that fixes not referencing an ID are missed (Sec. 8.2).
- **Metrics and key results:** Cross-release: median recall 0.62, false alarm 0.48 (Sec. 9). Top-20%LOC recall 27% cross-release vs 17-22% for baselines (Sec. 9). Recall 18-6,691% higher than baselines cross-release (Table 2 discussion). Average computation time 8.46 s cross-release (Sec. 1/abstract).
- **Stated limitations:** Missing defective lines from fixes without bug IDs (Sec. 8.2). Single coder for defect categorisation (agreement 0.86/0.81 on a subset). Nine systems only.
- **Critical assessment:** High recall comes with a high false-alarm rate (about 0.47-0.48); the median number of predicted defective lines (90-92 per file) is much higher than for baselines (0-77), which favours recall (Table 2 discussion). Line labels count all lines touched by fixes, including tangled edits. No control for unchanged files carrying the same affected-version label across k-1 and k. Static-analysis baselines are weak comparators.
- **Relevance to project:** Directly relevant: the ActiveMQ releases match. It is the reference cross-release protocol and line-level baseline (and DeepLineDP extends it). The leakage issue of affected-version labels on unchanged code applies directly to this project's ActiveMQ method labels.

### 12. Wang Z., Tong W., Li P., Ye G., Chen H., Gong X., Tang Z. (2023). BugPre: an intelligent software version-to-version bug prediction system using graph convolutional neural networks. Complex & Intelligent Systems 9:3835-3855.

- **DOI:** 10.1007/s40747-022-00848-w
- **Access:** full_text
- **Task and granularity:** CVDP restricted to changed and change-impacted functions of the current version, found by variable-propagation-tree (VPT) change-impact analysis. Function-level graphs; the label granularity for the main evaluation comes from PROMISE file labels (see critique).
- **Language and data:** Java. Dataset 1: 8 versions of 4 Apache projects (Hadoop, Lucene, Log4j, Ant) for AST-pruning analysis. Dataset 2: NanoXML, JUnit, HttpCore, Heritrix (3 releases each) for impact analysis. Dataset 3: 6 PROMISE projects, 20 releases (Table 5) for the classifier comparison. Dataset 4: Kafka (2.5.0, 2.6.1, 2.7.0) and Druid (0.19.0, 0.20.0, 0.22.1) (Sec. 'Data sets').
- **Representation:** Per-function graph: AST enriched with control-flow, data-flow and function-call edges (Algorithm functions buildControlFlow/buildDataFlow/buildFunCall). 14 node features (Fig. 1). Built with JavaParser and GumTree-Spoon for diffs.
- **Model:** Graph convolutional neural network with tanh/MLP update and softmax output (Eqs. 1-3).
- **Baselines:** LR, Transfer NB, SVM, DT on PROMISE metrics; DBN and TCNN on AST tokens; DS3, WGNCS, HALKP and the CPDP method ADCNN by F1 (Table 9).
- **Evaluation setup:** Train on prior version (8:2 train/validation split within it), test on adjacent next version, e.g. Camel 1.0 -> 1.2 (Sec. 'Efficiency of defect detection'). Precision, recall, F1. PofB20 not applicable because only changed code is tested.
- **Cross-version (method/function/line?):** Yes, N -> N+1. Test units are changed/impacted functions of N+1, so it is partly function level, but the PROMISE ground truth is file level. How function labels are derived is not explained in the sections read.
- **Graph-based:** Yes. AST + CFG + data-flow + call edges per function; GCN classifier; no Joern (own JavaParser-based pipeline).
- **Duplication / leakage handling:** Only changed and impacted functions are predicted, so unchanged code is excluded from the test set by design. This is the only paper here that structurally avoids unchanged-module leakage, though the authors frame it as an efficiency feature rather than a leakage control.
- **Label source and noise:** Training labels from bug-fix commit logs (system overview) and PROMISE file labels (Dataset 3). Label noise not discussed.
- **Metrics and key results:** GCNN average precision 67.5% (5.7-22.3 points above ML baselines) and recall 71.8% over six PROMISE projects (Fig. 9 text). Table 9 average F1 0.6721 vs DS3 0.3708, WGNCS 0.4986, HALKP 0.4483. AST pruning raised recall by an average of 17.7% (Fig. 6 text).
- **Stated limitations:** Java only. Insufficient historical data early in a project ('Limitation and discussion').
- **Critical assessment:** (1) The label-granularity mismatch (file labels, function graphs) is unexplained. (2) Recall is defined as TP/(TP+TN) in the text, which is a typo or an error. (3) Table 9 labels the proposed method 'DefectPre' and appears to quote baseline F1 values from other papers, evaluated on all modules rather than the changed subset; the comparison is not like for like. (4) F1/precision/recall only, with no MCC/AUC or effort-aware metrics, and no repeated runs or statistical tests. (5) Restricting the test set to changed code changes the base rate, so it is not comparable with full-release CVDP.
- **Relevance to project:** The closest existing work to the project's design (function-level CFG + data-flow graphs, version-to-version). Its 'predict only changed or impacted methods' framing is a principled leakage control worth adopting as one evaluation stratum. Its weak evaluation leaves room for a rigorous replication with Joern CFG+DDG on Django/ActiveMQ.

### 13. Yang F., Zhong F., Wei X., Zeng G. (2025). A Fine-Grained Defect Prediction Method Based on Drift-Immune Graph Neural Networks (DIDP/DI-GNN). Computers, Materials & Continua 82(2):3563-3590.

- **DOI:** 10.32604/cmc.2024.057697
- **Access:** full_text
- **Task and granularity:** File-level defect prediction plus statement-level risk ranking within predicted-defective files.
- **Language and data:** File level: 9 PROMISE Java projects. Statement level: Wattanakriengkrai et al. (Line-DP) data set, 32 releases of 9 systems including ActiveMQ 5.0.0-5.8.0 (Sec. 4.2, Tables 1-2).
- **Representation:** Program dependence graph per file (control- and data-dependence edges); statement nodes embedded into 100-d vectors. In training (statement-level experiments), backward slicing (control+data) and forward slicing (data only) from labelled defective statements (Sec. 3.1, 4).
- **Model:** DI-GNN: an information-bottleneck GNN that selects a label-relevant subgraph to be robust to distribution shift; Adam lr 0.001, batch 128, dropout 0.1; other hyperparameters by grid search (Sec. 4).
- **Baselines:** File level: DBN, DTLDP, MFGNN, ACGDP, DHCNN, BN, CNN, Seml, BugContext, LSTM (Sec. 5.1). Statement level: IVDetect* (modified), LineVD, ErrorProne (Sec. 5.2).
- **Evaluation setup:** WPDP: previous version trains/validates, next version tests (e.g. xalan-2.4 -> 2.5) (Sec. 5.1); also CPDP. Statement level: effort-aware Recall@Top20%LOC, Effort@Top20%Recall, IFA (Sec. 4.3). The split used for the statement-level experiments is not explicitly described in the sections read.
- **Cross-version (method/function/line?):** Yes for file level (version N -> N+1, Sec. 5.1). Statement level presumably the same, but not confirmed in the text read. No method-level evaluation.
- **Graph-based:** Yes. PDG (CDG + DDG). The extraction tool was not identified in the sections read. Information-bottleneck GNN with subgraph selection.
- **Duplication / leakage handling:** None. Slicing is applied only to training files (Sec. 3.1), which is correct. Unchanged files across versions are not controlled. Grid-search data split is unspecified.
- **Label source and noise:** PROMISE file labels; Line-DP line labels. The authors note possible mislabelling (Sec. 7.1).
- **Metrics and key results:** Statement level medians (Table 7): Recall@Top20%LOC 0.377 vs LineVD 0.308, IVDetect* 0.292, ErrorProne 0.079. Effort@Top20%Recall 0.175 vs 0.195/0.210/0.525. IFA 69, best (Table 8). File level: 'competitive' AUC/F1, ranking close to DHCNN and ACGDP by Scott-Knott ESD (answer to RQ1).
- **Stated limitations:** Possible mislabelling; baseline re-implementation differences; Java only; not applicable to JIT; retraining still needed under strong drift (Sec. 6-7).
- **Critical assessment:** 'Drift-immune' is not tested against a drift measure; at file level it does not beat DHCNN/ACGDP. Grid search without a stated held-out split risks tuning on the test release. The modified IVDetect* baseline was built by the authors. Effort-aware metrics are a plus. Unchanged files between ActiveMQ releases can inflate both file- and statement-level scores.
- **Relevance to project:** Uses PDG (CFG+DDG) graphs on the same ActiveMQ line-level data, with cross-version file-level training. It is the nearest graph baseline for the project's Joern CFG/DDG representation, and its slicing-around-defective-statements idea could focus method graphs.

## Theme synthesis

1. Method-level cross-version evidence is thin and negative. None of the eight assigned CVDP papers works at method/function level: Amasaki, HALKP, TSTSS, Yang & Wen, Kabir (prop), Cohen and probably Wu are class/file level, and Bangash is cross-project. The only release-based method-level evaluations found are Chowdhury et al. 2024 (Shippey data: releases < x -> x) and Pascarella et al. 2018/2020 (abstract only). In both, performance collapses compared with cross-validation, with precision about 0.13 and F1 about 0.25 for cross-project on Shippey (Chowdhury Fig. 2). BugPre predicts on changed functions version-to-version, but its labels appear to be file level.

2. Train-test overlap is pervasive and mostly ignored. Onet-Marian & Hotea 2025 measured on the standard SEACRAFT pairs that 72% of next-version classes already exist (median 79%). About 35% of those have identical metric vectors. Models score like training accuracy on unchanged-label classes and have mostly negative MCC on classes whose label flipped. This matches Liu et al. 2024 (smr.2715, abstract only) for WPDP. Several popular CVDP methods (TSTSS/DS3, AVDP, Amasaki's 'latest release is best', Cohen's anchor-based alignment, HALKP's active labelling) increase train-test similarity by design, so their reported gains are confounded with memorisation of carried-over modules. BugPre is the only paper that excludes unchanged code from the test set, though as an efficiency feature.

3. Protocol flaws recur. (a) Transductive use of test-release features: TSTSS, AVDP, HALKP-KPCA, Cohen alignment. (b) Test-release labels in training: HALKP active learning; Kabir's drift detector needs test labels. (c) Hyperparameter or configuration selection on the test pairs: Cohen; DI-GNN grid search with an unstated split. (d) F1/precision/recall-only reporting: BugPre, HALKP; Cohen gets an AUC gain with no F1 gain. (e) Baselines copied from other papers: BugPre Table 9. (f) Questionable data: Kabir's JM 'versions' with identical statistics. Bangash is the best methodological model: date-ordered buckets, a gap between train and test to let labels mature, many split points, and F/AUC/MCC/G reported.

4. Label noise is a first-order problem at method level. Chowdhury: about 60% of bug-fix commits touch more than one method and over 15% touch at least 10 (Fig. 4). Keyword-based fix detection has many false positives, and young methods are labelled clean before bugs surface. With affected-version labelling (Line-DP/Yatish data, which includes the ActiveMQ releases used here), one bug spanning releases k-1 and k labels the same unchanged file or lines defective in both, which creates direct label leakage across the release split.

5. Graph-based CVDP is rare and weakly evaluated. Graph papers in this set: Cohen (class dependency network + node2vec/LINE + Procrustes alignment, class level), BugPre (AST+CFG+DFG+call edges per function, GCN), DI-GNN (PDG = CDG+DDG, information-bottleneck GNN, file + statement level on the Line-DP ActiveMQ data). None de-duplicates, none reports MCC with variance over many release pairs, and none compares against strong text baselines (doc2vec/CodeBERT) under the same split. Cohen shows that per-release unsupervised graph embeddings need alignment (or an inductive encoder trained once) to be comparable across releases.

6. Implications for this project. (i) Evaluate Django (24 releases) and ActiveMQ (5 releases) as N -> N+1, and optionally N -> N+2 with a gap release (Bangash). Report distributions over pairs with MCC, AUC and effort-aware measures. (ii) Stratify the test release into new, modified, and unchanged methods (identity via a normalised body hash or Joern graph hash, not metrics), as in Onet-Marian & Hotea. Report the headline on new+modified methods and the changed-label subset; keep the unchanged stratum as a leakage diagnostic. (iii) Train graph encoders inductively on release N only; if using unsupervised per-release embeddings, align without letting test-release unchanged methods act as labelled anchors. (iv) Control label noise: exclude or flag tangled fix commits and young methods (Chowdhury's 2-year rule as a sensitivity analysis), and avoid affected-version label carry-over on unchanged code. (v) Use adversarial validation (Wu 2026) as a shift diagnostic, not as a training filter.

Access caveat: Amasaki 2020, HALKP, TSTSS, Yang & Wen and Wu 2026 were read as abstracts only, so their assessments are provisional.

## Additional papers found

- 10.1109/saner.2018.8330264 - Pascarella, Palomba, Bacchelli 2018 'Re-evaluating method-level bug prediction' (SANER). Method-level, release-by-release evaluation drops to near-random (abstract; DOI verified via OpenAlex; full text not retrieved).
- 10.1016/j.jss.2019.110493 - Pascarella et al. 2020 'On the performance of method-level bug prediction: A negative result' (JSS). Extended version of the above (abstract; DOI verified).
- 10.1002/smr.2715 - Liu et al. 2024 'Unveiling the impact of unchanged modules across versions on the evaluation of within-project defect prediction models' (JSEP). 481 target versions from 62 projects; unchanged modules inflate WPDP performance values (abstract; DOI verified).
- 10.1109/access.2020.3001440 - Zhang J. et al. 2020 'CDS: A Cross-Version Software Defect Prediction Model with Data Selection' (IEEE Access). Treats instances that exist in previous versions separately from new ones (described in Onet-Marian & Hotea 2025 Sec. 2; DOI verified).
- 10.1109/tse.2022.3144348 - Pornprasit & Tantithamthavorn 2022 'DeepLineDP' (TSE). File- and line-level, 32 releases of 9 systems incl. ActiveMQ, cross-release; hierarchical attention, not graph (abstract; DOI verified).
- 10.1145/3196321.3196331 - Xu et al. 2018 'Cross version defect prediction with representative data via sparse subset selection' (ICPC; DS3 baseline; DOI verified).
- 10.1016/j.ins.2021.05.008 - Zhang N. et al. 2021 'WGNCS: robust hybrid cross-version defect model' (Information Sciences; DOI verified).
- 10.1016/j.infsof.2022.106939 - Zhao et al. 2022 'ST-TLF: Cross-version defect prediction framework based transfer learning' (IST; DOI verified).
- 10.1016/j.asoc.2021.107870 - Kabir et al. 2021 'Inter-release defect prediction with feature selection using temporal chunk-based learning' (ASOC; DOI verified).
- 10.1145/3273934.3273938 - Amasaki 2018 PROMISE 'Cross-version defect prediction using cross-project defect prediction approaches: does it work?' (predecessor of the EMSE 2020 paper; DOI verified).
- 10.1109/tse.2019.2892959 - Qu et al. 2019 'Using K-core decomposition on class dependency networks to improve bug prediction' (TSE; graph-based, IVDP and CVDP, effort-aware; DOI verified).
- 10.1145/3238147.3240469 - Qu et al. 2018 'node2defect: using network embedding to improve software defect prediction' (ASE; class dependency network embedding, within-version; DOI verified).
- 10.1109/esem.2011.30 - Premraj & Herzig 2011 'Network versus code metrics to predict defects: a replication study' (network metrics gave no added value in the forward-release setting; DOI verified).
- arXiv:2511.22726 - 'The Repeat Offenders: Characterizing and Predicting Extremely Bug-Prone Source Methods' (method-level; found via arXiv search, not read; DOI not verified).
- Zenodo record 24207888 - 'DjangoDefects: A Multi-Granularity SZZ-Labeled Defect Dataset for Python' (24 Django releases 1.0-5.2, method-level 169,744 instances, 9.8% buggy; matches this project's Django scope; not a paper, not verified further).
- 10.1109/tse.2020.3131950 - 'Revisiting the Impact of Dependency Network Metrics on Software Defect Prediction' (TSE 2021; graph metrics; found via OpenAlex, not read).