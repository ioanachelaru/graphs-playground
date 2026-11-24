# Method-level defect prediction: datasets and labels (reading notes)

Scope: 10 papers on datasets and label quality, focusing on cross-version (release-based) evaluation and graph-based approaches. Section/table references point to the read copy (full text or preprint). Papers marked abstract_only rest on the abstract (and, for Liu 2024, publisher figure captions seen in search results); statements about them are provisional.

## Access summary

| Paper | DOI | Access | Cross-version (granularity) | Graph-based |
|---|---|---|---|---|
| Shippey 2016 (ELFF) | 10.1145/2961111.2962620 | full_text | no evaluation (multi-version data) | no |
| Ferenc 2020 (BugHunter) | 10.1016/j.jss.2020.110691 | preprint | no (random 10-fold CV) | no |
| Ferenc 2020 (Unified) | 10.1007/s11219-020-09515-0 | full_text | no (class/file; random CV) | no |
| Akimova 2021 (PyTraceBugs) | 10.1109/apsec53868.2021.00022 | abstract_only | no (provisional) | no |
| Opu 2026 | 10.1145/3793302.3793351 | preprint | no | no |
| Ahluwalia 2019 | 10.1109/msr.2019.00019 | abstract_only | label analysis only (class) | no |
| Falessi 2021 | 10.1145/3467895 | preprint | yes (class) | no |
| Liu 2024 | 10.1002/smr.2715 | abstract_only | yes (module; provisional) | no |
| Zhang 2016/17 | 10.1109/tse.2016.2599161 | abstract_only | no (provisional) | no |
| Wattanakriengkrai 2020 | 10.1109/tse.2020.3023177 | full_text | yes (line, k-1 -> k) | no |

## Shippey 2016 (ELFF)

**Citation.** Shippey T., Hall T., Counsell S., Bowes D. (2016). So You Need More Method Level Datasets for Your Software Defect Prediction? Voilà! ESEM 2016, 12:1-12:6.  
**DOI.** 10.1145/2961111.2962620

- **Access.** full_text
- **Task and granularity.** Dataset paper (ELFF). Class- and method-level fault labels plus metrics per version; no prediction experiment.
- **Language and data.** Java, 23 SourceForge SVN projects selected from ~50,000 Boa (Sept 2013 SourceForge) candidates (Sec 3.1, Table 1 criteria: Java, SVN, defect-linking commits, SourceForge tracker, >=100 fixed defects). Fault data for 69 versions (Sec 4); abstract reports 138 fault+metric datasets (consistent with 69 versions x 2 levels; this mapping is my inference). Projects are 16-550 KLOC, 12 years old on average (Sec 4, Table 2).
- **Representation.** JHawk 5.0 class- and method-level code metrics (Sec 3.2). Chowdhury et al. 2024 (TOSEM) list 29 code metrics and 0 change metrics for this dataset; that count is not stated in the Shippey text.
- **Model.** None (dataset only).
- **Baselines.** None.
- **Evaluation setup.** No predictive evaluation. Descriptive statistics only: defect-link coverage per project (Table 2) and % faulty classes/methods for a random sample of the 69 versions (Table 3).
- **Cross-version?.** No evaluation, cross-version or otherwise. The data is multi-version (e.g., jmol 3/4/6/7, genoviz 5.4/6/6.1, drjava 01012008/01012009/01012010 in Table 3), so release N->N+1 method-level splits can be built from it. Some 'versions' are date snapshots, not releases (Sec 4: e.g. 01012008).
- **Graph-based?.** no
- **Duplication / leakage handling.** None discussed. Unchanged methods across versions are not identified.
- **Label source and noise.** Own SZZ implementation (DefectFinderELFF). It weights numbers in commit messages that exist in the defect database and handles the 'Fix for' prefix. The authors verified it separately by manually checking all defect links for Eclipse JDT 3.0 (Sec 3.2). A method is faulty at a snapshot if the snapshot falls between the SZZ insertion point and the fix (Sec 3.2). Defect-link coverage averages ~41%, from 7.59% (jEdit) to 93.84% (BRL-CAD) (Table 2, Sec 4). The authors acknowledge false negatives from unreported defects and cite Kim et al.'s <20% noise tolerance (Sec 3.2). Tangled changes are not handled.
- **Metrics and key results.** Faulty-method rate per version ranges from 0% (cdk 1, cdk 1.2, controltier 3.2) to 13.26% (jmol 6); faulty-class rate goes up to 42.35% (jmol 6) (Table 3). High link coverage does not imply many faults per version (Sec 4).
- **Stated limitations.** Unreported defects cause false negatives. Low link coverage weakens SZZ. Some projects lack clear releases, so date snapshots are used. BRL-CAD has no Java files in its latest release (Sec 4).
- **Critical assessment.** Useful as a source of method-level labels, but it has no evaluation, so there is no evidence of predictive usefulness. Labels come from SZZ with ~41% average link coverage, so false negatives are likely high, and several versions have 0-0.3% faulty methods (Table 3), which makes them unusable for training or testing. Tangled fixes and dormant defects are not handled. Releases are partly replaced by date snapshots, which complicates a release-based protocol. It is an SVN/SourceForge legacy corpus with metrics from one commercial tool (JHawk). Chowdhury et al. 2024 later used it for time-aware 'realistic' scenarios (per search snippet; not verified here).
- **Relevance to project.** Medium. It is one of the few public method-level Java multi-version datasets, so it could provide a third, external Java corpus for a release-based, de-duplicated evaluation. Source code is available, but SVN checkouts of 2013-era projects would be needed to run Joern. Low faulty rates in some versions argue for selecting only versions with enough positives.

## Ferenc 2020 (BugHunter)

**Citation.** Ferenc R., Gyimesi P., Gyimesi G., Tóth Z., Gyimóthy T. (2020). An automatically created novel bug dataset and its validation in bug prediction (BugHunter Dataset). Journal of Systems and Software 169, 110691. DOI verified via CrossRef; read from arXiv:2006.10158v1.  
**DOI.** 10.1016/j.jss.2020.110691

- **Access.** preprint
- **Task and granularity.** Dataset and binary bug prediction at file, class and method level.
- **Language and data.** Java, 15 GitHub projects (Table 14), nearly 10,000 bug-fixing commits analysed (Sec 5.11). Method level: 159,078 entries, of which 58,810 are faulty and 100,268 non-faulty, reported as ratio 0.59 (Table 14). Class: 84,562 entries. File: 70,088 entries.
- **Representation.** OpenStaticAnalyzer: 66 static source code metrics, 8 code duplication metrics, 35 code smell (rule violation) metrics (Table 14).
- **Model.** 11 Weka classifiers: NaiveBayes, NaiveBayesMultinomial, Logistic, SGD, SimpleLogistic, VotedPerceptron, DecisionTable, OneR, J48, RandomForest, RandomTree (Sec 6).
- **Baselines.** Its own traditional release-based GitHub Bug Dataset (Tóth et al. 2016) on the same 15 projects with the same metrics (Sec 6.3, Table 23). Class-level metrics vs method metrics projected to class level (RQ2).
- **Evaluation setup.** 10-fold cross-validation on each project and on the combined 'all' set (Sec 6). Random undersampling of the majority class, repeated and averaged (Sec 5.7). Duplicate-feature filtering is applied before learning (Sec 5.6). Friedman and Nemenyi tests across algorithms (Sec 6.1). Reports precision, recall and F-measure only.
- **Cross-version?.** no. Entries are pre-fix and post-fix snapshots of elements touched by bug fixes, 'regardless of release versions' (Abstract, Sec 5.2). Evaluation is random 10-fold CV, with no temporal or release split.
- **Graph-based?.** no. OpenStaticAnalyzer builds an internal graph of files, classes and methods (Sec 5.3), but only scalar metrics are used for learning.
- **Duplication / leakage handling.** Partial. Identical metric vectors with conflicting labels are filtered (Removal, Subtract, Single, GCF; Subtract chosen) (Sec 5.6, Tables 8-13). Without filtering, method-level F is 0.5317; with Subtract it is 0.5717; with Removal, 0.5773 (Table 8). Leakage of the same method's pre- and post-fix states, or of the same method across commits, into different CV folds is not addressed.
- **Label source and noise.** Bug-labelled GitHub issues with project-specific label sets, linked to fixing commits. The last commit before the first fix is the buggy state, and commits between fixes are also buggy. Changed elements are mapped through diff line ranges to OSA source positions by fully qualified name (Sec 5.2, 5.4). This is not SZZ: no fix-inducing commit is searched for. Manual validation was done on JUnit only: of 84 closed bugs, 37 are in the dataset, and 5 commit mismatches (comment-only changes) give 7 of 734 wrong entries, 0.95% (Sec 5.9, Table 15). Tangled fixes beyond comment-only changes are not handled. The non-buggy class is mostly post-fix states of the same elements, plus new methods created during fixes (Sec 5.8).
- **Metrics and key results.** Method level, all projects: RandomForest P 0.6335, R 0.6324, F 0.6319; J48 F 0.6119; RandomTree F 0.6110 (Table 16). The top five algorithms do not differ significantly (Table 29). Best per-project method-level F ranges from 0.7573 (antlr4, RF) to 0.5395 (ceylon-ide-eclipse) (Table 17). The traditional dataset gives higher F, by ~0.10 at method level, ~0.21 at class level and ~0.09 at file level. Method metrics projected to class level give F 0.7405 vs 0.7831 for the traditional dataset (Sec 6.3).
- **Stated limitations.** Matching was validated on JUnit only. Commit mismatches exist. Faultiness before the report and after the last fix is uncertain. Only one static analyser was used. Only 15 Java projects (Sec 7).
- **Critical assessment.** The task differs from release-based prediction. The negatives are mostly the fixed versions of the positives, so models learn to separate pre-fix from post-fix code among fix-touched elements, not to find defective methods among all methods. The class balance (0.59) is artificial, and results are not comparable with release-based studies. Random 10-fold CV over commit snapshots puts near-identical states of the same method in train and test. The need for conflict filtering (Sec 5.6) shows how many entries share identical feature vectors, yet duplicates with consistent labels across folds are not removed. Undersampling is described for 'the training process', and whether test folds were also balanced is not stated. Only F-measure, precision and recall are reported (no MCC/AUC, no effort-aware measures), and default Weka settings are used. The RQ3 claim that the traditional dataset is noisier is argued, not measured.
- **Relevance to project.** Medium-low for the main protocol, high as a warning. It shows that commit-level before/after datasets produce leakage-prone, non-release evaluations. It is a possible source of method-level Java labels, but the protocol would have to be rebuilt around releases.

## Ferenc 2020 (Unified)

**Citation.** Ferenc R., Tóth Z., Ladányi G., Siket I., Gyimóthy T. (2020). A public unified bug dataset for Java and its assessment regarding metrics and bug prediction. Software Quality Journal 28:1447-1506.  
**DOI.** 10.1007/s11219-020-09515-0

- **Access.** full_text
- **Task and granularity.** Dataset unification plus class- and file-level bug prediction. There is no method-level data: the text never mentions method level, and the abstract states class and file level.
- **Language and data.** Java. Five public datasets: PROMISE, Eclipse Bug Dataset, Bug Prediction Dataset, Bugcatchers, GitHub Bug Dataset (Sec 2.3). Re-analysed with OpenStaticAnalyzer 1.0 and merged on class names or file paths; 624 class elements dropped (Table 3). The merged set has 47,618 classes and 43,744 files (Abstract, Sec 5.3.2).
- **Representation.** Original metrics, OSA metrics, or both (Sec 5.3).
- **Model.** J48 (C4.5) with default parameters (Sec 5.3.1).
- **Baselines.** Original metric suites vs OSA vs merged suites (Table 17).
- **Evaluation setup.** (i) Within-project 10-fold CV per system, no balancing (Sec 5.3.1). (ii) 10-fold CV on the merged dataset (Sec 5.3.2). (iii) Train on one system, test on every other system of the same source dataset, as an NxN matrix (Sec 5.3.3). F-measure and AUC.
- **Cross-version?.** no as a designed protocol, and not at method level. Within-project results use 10-fold CV within one release. The NxN cross-system matrix for PROMISE includes different versions of the same project (e.g., Ant 1.3-1.7) in any direction with no chronological constraint, and only first versions are shown in Tables 20-21. Class/file level only.
- **Graph-based?.** no
- **Duplication / leakage handling.** None. The merged dataset pools multiple versions of the same projects (e.g., Ant 1.3-1.7, Xalan 2.4-2.7; Table 3) and evaluates with 10-fold CV, so unchanged classes appear in both train and test.
- **Label source and noise.** Labels are inherited 'as is' from the source datasets without validation (Sec 6). Known anomalies: Camel 1.4 has classes with LOC 0, and some datasets have >90% or <1% buggy classes (Sec 6), e.g. Log4J 1.2 at 92.20% (Table 17). The source datasets differ in pre/post-release labelling (Table 16). Name-matching heuristics associate bugs in nested classes with the wrong element (Sec 6).
- **Metrics and key results.** Merged dataset with J48 and 10-fold CV: F 0.818 (classes) and 0.755 (files); AUC 0.721 and 0.699 (Sec 5.3.2). Within-project AUCs are often 0.4-0.8, e.g. Camel 1.0 AUC 0.433-0.494 while F is 0.93-0.95 (Table 17). For PROMISE cross-system, average AUCs range 0.483-0.629, and models trained on systems with >70% buggy classes have average F <0.4 (Sec 5.3.3).
- **Stated limitations.** Source datasets accepted without validation. Some source versions could not be found. Old code was analysed against a newer Java standard. Name-matching heuristics have limits. Nested-class mismatch (Sec 6).
- **Critical assessment.** Valuable for metric harmonisation, weak for prediction claims. The design relies on F-measure on datasets with extreme and varying defect ratios, where high F with AUC near or below 0.5 (Camel 1.0) shows F is uninformative. Evaluation uses a single learner with defaults and random 10-fold CV. Pooling several versions of the same projects and then cross-validating guarantees duplicate leakage. Not method level.
- **Relevance to project.** Low for method-level work. Useful as a reference for metric-tool disagreement, i.e. the same metric name computed by different tools. That matters when comparing SonarQube metrics with Joern-derived features.

## Akimova 2021 (PyTraceBugs)

**Citation.** Akimova E. N. et al. (2021). PyTraceBugs: A Large Python Code Dataset for Supervised Machine Learning in Software Defect Prediction. APSEC 2021. Author list beyond the first author not verified.  
**DOI.** 10.1109/apsec53868.2021.00022

- **Access.** abstract_only
- **Task and granularity.** Function/method-level binary classification of buggy vs correct snippets, restricted to low-level bugs that raise exceptions reported in tracebacks (Abstract).
- **Language and data.** Python, GitHub repositories. 5.7 million correct snippets and 24 thousand buggy snippets. The most common bugs are missing attribute, empty object, index out of range, and encoding/decoding errors (Abstract).
- **Representation.** Pretrained BERT-like contextual embeddings (Abstract). Details unknown.
- **Model.** Binary classifier on BERT-like embeddings (Abstract). Architecture unknown.
- **Baselines.** Unknown (abstract only).
- **Evaluation setup.** Pre-defined train/validation/test split (Abstract). Split criterion unknown, whether random, by repository, or by time. Also applied to BugsInPy.
- **Cross-version?.** no (from the abstract: a fixed train/val/test split of snippets, with no release-based protocol mentioned). Provisional, since the full text was not read.
- **Graph-based?.** no (from the abstract).
- **Duplication / leakage handling.** Unknown (abstract only).
- **Label source and noise.** Snippets are selected via traceback error messages in GitHub data. Estimated labelling confidence is ~85%. Test-sample labels were manually validated to almost 100% confidence (Abstract).
- **Metrics and key results.** Test set: precision 96% (buggy) and 61% (correct); recall 34% (buggy) and 99% (correct). On BugsInPy the model flags ~14% of buggy snippets (Abstract).
- **Stated limitations.** Unknown beyond the abstract.
- **Critical assessment.** Large and Python-specific, but the label scope is narrow: exception-raising bugs found from tracebacks, not post-release defects of a project. Reported per-class precision and recall are inconsistent with the stated class ratio unless the test set was rebalanced; this cannot be checked without the full text. Duplicate and near-duplicate functions across GitHub repositories are a known risk for code-embedding leakage, and their handling is unknown. 14% detection on BugsInPy suggests weak transfer.
- **Relevance to project.** Low-medium. It is a Python function-level corpus that could pretrain or probe models, but its labels do not match release-based Django defect labels. It shows the scarcity of Python method-level SDP data.

## Opu 2026

**Citation.** Opu M. N. I., Wang S., Chowdhury S. (2026). LLM-Based Detection of Tangled Code Changes for Higher-Quality Method-Level Bug Datasets. Read from arXiv:2505.08263v3 (25 Oct 2025); the DOI resolves to the ACM version.  
**DOI.** 10.1145/3793302.3793351

- **Access.** preprint
- **Task and granularity.** Method-level classification of a method change inside a bug-fix commit as bug-related (Buggy) or incidental (NotBuggy), i.e. method-level untangling. Plus a label-quality analysis (RQ4).
- **Language and data.** Java. Built on the Chowdhury et al. dataset of 774,051 methods from 49 projects with full CodeShovel histories (Sec 3.1). The gold set has 1,764 method changes. 730 Buggy are methods that were the only method changed in a bug-fix commit. 727 NotBuggy are methods never in a bug-fix commit, after removing 3 duplicate diffs. 166 Buggy and 141 NotBuggy tangled cases were manually labelled from 450 random multi-method bug-fix commits (Sec 3.1).
- **Representation.** Method-level code diff plus commit message, as prompt text or as embeddings. Embeddings: Gemini text-embedding-004, EmbeddingGemma-300m, CodeBERT, GraphCodeBERT, with sliding-window mean pooling for the open models (Sec 4.3).
- **Model.** Zero-shot, few-shot, chain-of-thought and combined prompting with GPT-5, GPT-4o, Gemini-2.0-Flash and GPT-OSS-120B (Abstract, RQ1-RQ2). RF, SVC, DT and MLP on embeddings (Sec 4.3).
- **Baselines.** Diff-only vs diff+message prompts (RQ1). Prompting variants (RQ2). Embedding models compared with each other (Table 5). No prior untangling tool is compared at method level.
- **Evaluation setup.** Prompting is evaluated on the whole gold set. Embedding classifiers use a random 80/20 split plus leave-one-out (Sec 4.3). Accuracy, precision, recall, F1, MCC (Sec 3.4). RQ4 applies GPT-4o few-shot+CoT to all 49 projects and compares five metric distributions (size, readability, McCabe, FanOut, MI; first version of each method) between Buggy and NotBuggy with Wilcoxon rank-sum and Cliff's delta (Sec 4.4).
- **Cross-version?.** no. The classification task uses a random 80/20 split and LOO. RQ4 is a distributional analysis with no prediction model and no release split.
- **Graph-based?.** no. GraphCodeBERT is used only as a text embedding model (Table 5).
- **Duplication / leakage handling.** Minimal. 3 duplicate diffs were removed from NotBuggy (Sec 3.1). Diffs from the same commit or project can fall on both sides of the random 80/20 split. LLM pretraining exposure to these public repositories is acknowledged only generally as 'data leakage' (Sec 6).
- **Label source and noise.** Base labels come from Chowdhury et al. A method is Buggy if it appears in a bug-fix commit. It is NotBuggy if it is at least 2 years old and never in a bug fix (Sec 4.4). One graduate student did the manual labelling. A second annotator relabelled 100 samples, giving Cohen's kappa 0.82; quality fixes were resolved as NotBuggy (Sec 3.1). The RQ4 'Less-Noisy' labels are GPT-4o outputs and were not validated on that application.
- **Metrics and key results.** RQ1: best zero-shot F1 0.879 (GPT-5, diff+message) (Sec 1). RQ2: few-shot+CoT with GPT-4o F1 0.883 (Abstract, Sec 1). RQ3 (Table 4, text-embedding-004): MLP Acc 0.895, F1 0.902, MCC 0.791; SVC F1 0.891, MCC 0.768. Open models with MLP (Table 5): GraphCodeBERT F1 0.831, MCC 0.656; CodeBERT F1 0.782, MCC 0.533. LOO MLP: F1 0.906, MCC 0.8073 (Sec 4.3). RQ4 (Table 6): projects with a large effect size for Size rise from 36.73% to 73.47%, FanOut from 40.82% to 71.43%, MI from 51.02% to 77.55%. Significant separation is found in one additional project per metric (Sec 4.4).
- **Stated limitations.** Subjective manual labelling. Java open-source only. CodeShovel histories may be inaccurate (Sec 5). No full bug prediction model was built (Sec 4.4).
- **Critical assessment.** (1) Most of the gold set (1,457 of 1,764) is easy by construction: single-method fixes vs methods never touched by a fix. Only 307 tangled cases test the actual untangling problem, and results on that subset alone are not reported in the sections read. (2) The 80/20 split is random, with no grouping by commit or project. (3) RQ4 does not show better defect prediction. Larger metric separation after relabelling is expected if the LLM prefers to keep small, focused changes as Buggy, so it may reflect LLM bias rather than truth. (4) NotBuggy requires >=2 years without a fix, which by definition excludes dormant defects only partly. (5) Proprietary models limit reproducibility. Even so, it is the only paper here that targets tangling at method level.
- **Relevance to project.** High for label quality. Django and ActiveMQ method labels derived from fix commits will contain tangled methods. A cheap check is to compare results on single-method-fix positives vs all positives, or to apply a CodeBERT/GraphCodeBERT untangling filter (F1 0.78-0.83 here) as a sensitivity analysis.

## Ahluwalia 2019

**Citation.** Ahluwalia A., Falessi D., Di Penta M. (2019). Snoring: A Noise in Defect Prediction Datasets. MSR 2019.  
**DOI.** 10.1109/msr.2019.00019

- **Access.** abstract_only
- **Task and granularity.** Empirical study of label noise from defects discovered several releases after introduction ('sleeping' defects and 'snoring' classes). Class level.
- **Language and data.** 282 releases of six Apache open-source projects (Abstract).
- **Representation.** Not applicable (label analysis).
- **Model.** None reported in the abstract.
- **Baselines.** None reported in the abstract.
- **Evaluation setup.** Measures how long defects sleep and the missing rate of defective classes when labels are taken at different times or after removing releases (Abstract).
- **Cross-version?.** no prediction experiment. It analyses release-level labelling over time at class level. Provisional (abstract only).
- **Graph-based?.** no
- **Duplication / leakage handling.** Not addressed (abstract).
- **Label source and noise.** Release-level defect attribution. Classes affected only by sleeping defects are treated as defect-free until discovery (Abstract).
- **Metrics and key results.** In all projects, most defects slept for more than 20% of existing releases. In most projects the missing rate is above 25% even after removing 50% of releases (Abstract).
- **Stated limitations.** Unknown beyond the abstract.
- **Critical assessment.** Establishes that release-based labels in recent releases are systematically incomplete, i.e. false negatives. Class level, 6 projects. Exact labelling method and missing-rate definition not checked.
- **Relevance to project.** High. Labels for the latest Django releases (e.g., 5.x) and the last ActiveMQ release (5.8.0) are probably incomplete. Test-set labels at release N+1 need an observation window, or these releases should be reported separately.

## Falessi 2021

**Citation.** Falessi D., Ahluwalia A., Di Penta M. (2021/2022). The Impact of Dormant Defects on Defect Prediction: A Study of 19 Apache Projects. ACM TOSEM. Read from arXiv:2105.12372.  
**DOI.** 10.1145/3467895

- **Access.** preprint
- **Task and granularity.** Class-level within-project, across-release defect prediction. Studies the effect of snoring (dormant-defect label noise) in training data and a countermeasure.
- **Language and data.** Java, 19 Apache projects (Jira and Git, >=10 releases), 616 releases and 4,101 defects (Sec 5; Table 4).
- **Representation.** 16 product and process metrics: size, LOC touched, revisions, fixes, authors, churn, change set size, age, etc. (Table 5). Correlation-based feature subset selection (Sec 2.2.3a).
- **Model.** 14 Weka classifiers plus AutoWEKA, which ran 2 h per training set (Sec 2.2.3b-c).
- **Baselines.** Training with snoring (TrS) vs without (TrNS) (RQ1). Removing non-defective classes from the last 0-4 training releases (RQ2).
- **Evaluation setup.** Data is ordered by release. The last 50% of releases are removed so the ground truth is nearly snoring-free (they cite prior work estimating >99% of snoring removed). Then a 66/33 order-preserving holdout: the first 66% is training, the rest test (Sec 2.2.3, Fig. 1). TrS is labelled at the end of the training period, TrNS and TeNS at project end (Fig. 2). Wilcoxon signed-rank, Cliff's delta, Holm correction (Sec 2.2.4). Repeated-measures permutation test for RQ2 (Sec 2.3.4). Metrics: precision, recall, F1, AUC, MCC, Kappa.
- **Cross-version?.** Yes, release-based at class level (older releases train, later releases test, order preserved; Sec 2.2.3, Fig. 1). Not method level.
- **Graph-based?.** no
- **Duplication / leakage handling.** Not addressed. Classes unchanged between training and test releases are not removed.
- **Label source and noise.** Realistic approach: Jira affected versions, with own SZZ (ignoring comments, whitespace and docstrings) when the AV is missing. AV availability is 14%-93% per project (Table 4). Classes touched by the fix are labelled defective in [introduction version, fix version) (Sec 2.2.3). Snoring loss, i.e. defective classes missed in TrS, ranges from 18% (TAJO) to 98% (CHUKWA) and exceeds 50% in most projects (Table 6).
- **Metrics and key results.** RQ1: snoring significantly lowers recall, with a large effect for all 15 classifiers. Precision does not differ significantly (Table 7). Median relative recall loss is ~90% (Fig. 6, Sec 4). RQ2: removing non-defective classes in the last training release gives average relative gains of precision 17%, recall 41%, F1 33%, Kappa 39%, MCC 32%, AUC 3% (Table 9). Removing 3-4 releases is worse (Table 9).
- **Stated limitations.** Some snoring may remain after dropping 50% of releases. SZZ and AV labels differ. No balancing. Single 66/33 split. Untested models and tuning (Sec 5). 19 projects.
- **Critical assessment.** Methodologically stronger than most of this set: order-preserving split, MCC and Kappa reported, multiple-testing correction. Weaknesses: (1) Discarding 50% of releases changes the population studied. (2) Internal inconsistencies. Sec 3.2 says the permutation test shows improvement on all metrics except recall, while the RQ2 summary says all six metrics. Sec 2.3 says 'remove all the classes labeled as defective' where non-defective is meant. Table 10 is captioned 'RQ3'. Table 12 lists THRIFT, which is absent from Table 4, and omits TOMEE; SYNCOPE's defective proportion exceeds 1. (3) AUC gains are only 3%, so much of the effect may be threshold or prior shift (more positives) rather than better ranking; the authors argue against this from precision gains (Sec 5). (4) No handling of unchanged classes.
- **Relevance to project.** High. Direct guidance for the Django (24 releases) and ActiveMQ protocol: (a) avoid using the most recent releases as test sets unless their labels have matured, (b) consider dropping non-defective methods from the last training release, (c) report MCC and AUC, since recall is the metric most affected.

## Liu 2024

**Citation.** Liu X., Zhou Y., Lu Z., Mei Y., et al. (2024). Unveiling the impact of unchanged modules across versions on the evaluation of within-project defect prediction models. Journal of Software: Evolution and Process 36(12): e2715.  
**DOI.** 10.1002/smr.2715

- **Access.** abstract_only
- **Task and granularity.** Evaluation-methodology study of within-project (previous version -> target version) defect prediction. Modules are files/classes; the exact granularity is not confirmed from the abstract.
- **Language and data.** 481 target versions from 62 projects (Abstract). Publisher figure captions (via ResearchGate) show an Eclipse 2.0 vs 2.1 same-name file comparison and ratios of unchanged positive and negative modules per target version. Provisional.
- **Representation.** Not the focus. Standard defect datasets.
- **Model.** Multiple WPDP learners (abstract); specifics unknown.
- **Baselines.** Evaluation with vs without unchanged modules in target versions.
- **Evaluation setup.** A method to detect modules with identical executable code in source and target versions and remove them from target versions. Performance and model rankings are compared before and after removal (Abstract).
- **Cross-version?.** Yes, at module (file/class) level: source versions -> target version (Abstract). Not method level.
- **Graph-based?.** no
- **Duplication / leakage handling.** This is the paper's subject. Unchanged modules (identical executable code) are detected and removed from target versions (Abstract). Figure captions mention label consistency of unchanged modules that were buggy in the source version (CB vs BB). Provisional.
- **Label source and noise.** From existing defect datasets; details unknown.
- **Metrics and key results.** Removing unchanged modules significantly changes reported performance of individual learners. Model rankings change little, with a slight effect on selecting the models that generalise better. Recommendation: remove unchanged modules from target versions (Abstract).
- **Stated limitations.** Unknown (abstract only).
- **Critical assessment.** The closest prior work to this project's leakage angle. From the abstract alone it is not possible to check the size and direction of the performance change, the definition of 'executable code' equality (e.g., comments and whitespace), or whether method level was studied. The finding that rankings are stable suggests that relative comparisons of representations may survive de-duplication while absolute numbers do not. This needs testing for graph vs text representations, which may memorise unchanged methods differently.
- **Relevance to project.** Very high. It supports de-duplicating unchanged methods in release N+1 and suggests reporting both absolute scores and rankings with and without unchanged methods. The full text should be obtained (paywalled; marked as bronze OA, but no copy was retrievable here).

## Zhang 2016/17

**Citation.** Zhang F., Hassan A. E., McIntosh S., Zou Y. (2017). The Use of Summation to Aggregate Software Metrics Hinders the Performance of Defect Prediction Models. IEEE TSE 43(5):476-491.  
**DOI.** 10.1109/tse.2016.2599161

- **Access.** abstract_only
- **Task and granularity.** File-level defect prediction (defect proneness, rank or count, effort-aware), with method- and class-level metrics aggregated to file level (Abstract).
- **Language and data.** 255 open-source projects (Abstract). The preprint snippet mentions C, C++, C# and Java.
- **Representation.** Method- and class-level metrics aggregated by 11 schemes (summation, central tendency, dispersion, etc.) (Abstract).
- **Model.** Unknown from the abstract.
- **Baselines.** Summation only vs other schemes vs all schemes (12 configurations) (Abstract).
- **Evaluation setup.** Unknown from the abstract (likely within-project resampling; not verified).
- **Cross-version?.** no (not stated in the abstract; provisional).
- **Graph-based?.** no
- **Duplication / leakage handling.** Not addressed (abstract).
- **Label source and noise.** File-level defect data from VCS (Abstract).
- **Metrics and key results.** Aggregation changes correlations among metrics and with defect count. For defect proneness, summation alone is best in 11% of projects, all schemes together in 40%. For rank or count, summation and all schemes perform similarly. For effort-aware prediction, mean or median aggregation is closest to best (Abstract).
- **Stated limitations.** Unknown (abstract only).
- **Critical assessment.** The relevant point is granularity mismatch. Coarse labels with aggregated fine-grained features distort the metric-label relation, and the choice of aggregator changes results. Evaluation details could not be checked.
- **Relevance to project.** Indirect. (a) If file-level SonarQube metrics are mapped to methods, or method predictions rolled up to files, the aggregation choice matters. (b) By analogy, which is my inference and not the paper's claim, the readout or pooling of node embeddings into a function-level CFG/DDG vector (sum vs mean vs max) should be treated as a tuned and reported choice, especially for effort-aware metrics, where size-correlated sums favour large methods.

## Wattanakriengkrai 2020

**Citation.** Wattanakriengkrai S., Thongtanunam P., Tantithamthavorn C., Hata H., Matsumoto K. (2022). Predicting Defective Lines Using a Model-Agnostic Technique (LINE-DP). IEEE TSE 48(5):1480-1496 (online Sept 2020).  
**DOI.** 10.1109/tse.2020.3023177

- **Access.** full_text
- **Task and granularity.** Line-level defect prediction and ranking, derived from a file-level model via LIME (Sec 5.2).
- **Language and data.** Java. 32 releases of 9 Apache systems from Yatish et al.'s affected-release datasets (Sec 6.1, Table 1). ActiveMQ 5.0.0, 5.1.0, 5.2.0, 5.3.0 and 5.8.0 are the same ActiveMQ releases this project uses. Camel, Derby, Groovy, HBase, Hive, JRuby, Lucene, Wicket. Defective files are 2%-28% per release (Table 1). Median 1.2-2.5% of lines in defective files are defective; defective methods cover 14-32% of a defective file's lines (Sec 3).
- **Representation.** Bag of code tokens (CountVectorizer after removing non-alphanumerics; tokens appearing once dropped) (Sec 5.2 Step 1).
- **Model.** File-level Logistic Regression (chosen over RF, SVM, kNN and NN with default scikit-learn settings; file-level MCC median 0.35 within-release, 0.18 cross-release). LIME on predicted-defective files; the top-20 risky tokens mark and rank lines (Sec 5.2 Steps 2-4).
- **Baselines.** Random guessing, PMD, ErrorProne, n-gram entropy (NLP; Ray et al.), TMI-LR, TMI-RF (Sec 6.3).
- **Evaluation setup.** Within-release: stratified 10x10-fold CV. Cross-release: train on release k-1, test on k, over 23 consecutive-release pairs (Sec 6.5). Metrics: recall, FAR, d2h, MCC, Top20%LOC recall, IFA (Sec 6.4). Precision is deliberately not evaluated (RQ1). One-sided Wilcoxon signed-rank with effect size r (Sec 6.6).
- **Cross-version?.** Yes, at line level: release k-1 -> k for 23 consecutive pairs (Sec 6.5), e.g. ActiveMQ 5.0.0 -> 5.1.0. For ActiveMQ, 5.3.0 -> 5.8.0 counts as 'consecutive' within the studied set although intermediate releases exist (Table 1).
- **Graph-based?.** no
- **Duplication / leakage handling.** None. Files and lines unchanged between release k-1 and k are not removed, and token features of unchanged files are identical across releases.
- **Label source and noise.** Bug reports of type 'Bug' in Jira that affect the studied release, linked to commits by issue-ID regex. Lines modified or removed by those bug-fixing commits and present in the release are defective; files touched are defective (Sec 6.2). Only issues reported after the release, affecting only that release, and closed are used (Sec 8.2). Tangled fixes are not handled, so refactoring lines in fix commits become 'defective'. Missing issue IDs give false negatives (Sec 8.2).
- **Metrics and key results.** LINE-DP median recall is 0.61 (within) and 0.62 (cross); FAR 0.47 and 0.48 (Sec 7 RQ1, Fig. 7). Top20%LOC recall is 0.27 (within) and 0.26 (cross) vs 0.17-0.22 for baselines; IFA is lower than baselines (Fig. 8, Table 3). Recall gains over PMD are 4,871% (within-release, Table 2). MCC is 9% lower than TMI-LR within-release and not significant (Table 2). Computation takes 10.68 s (within) and 8.46 s (cross) (RQ3). 63% of hit defective blocks are common defect types, mostly argument change (32%) and condition change (18%) (RQ4). Note: the abstract reports Top20%LOC recall as 0.27 and the conclusion swaps within/cross as 26%/27%.
- **Stated limitations.** Many false positives when common tokens are risky. Depends on the file-level model. Misses lines with rare tokens (Sec 8.1). Some defective lines labelled clean. First-author categorisation (Sec 8.2). 9 systems.
- **Critical assessment.** (1) Line-level scores are conditional on the file-level model and the >0.5 threshold, and FAR around 0.47 means about half of clean lines in flagged files are flagged. (2) Precision is excluded by design, and MCC is weak (no gain over TMI-LR). (3) k=20 and the NLP entropy thresholds (0.7 within, 0.6 cross) come from sensitivity analyses reported in an appendix. The paper does not say whether these used held-out data; they appear to be chosen on the evaluation releases (possible tuning on test). (4) No de-duplication of unchanged files across k-1 -> k. Because bag-of-tokens features are identical for unchanged files, file-level cross-release scores are likely inflated. (5) Baselines like PMD and ErrorProne target different bug types, so the large % gains are not very informative. Strengths: release-based labels from affected versions, effort-aware measures (Top20%LOC, IFA), and public line-level datasets.
- **Relevance to project.** Very high. These are probably the source datasets of the project's ActiveMQ releases, so the same labelling caveats apply (issue-ID linkage, tangled fixes, ActiveMQ 5.3.0 -> 5.8.0 gap). The paper also offers a line/method-level cross-release protocol and effort-aware metrics (Top20%LOC recall, IFA) to adopt for method-level CFG/DDG models. Defective lines map to methods directly, so method labels can be derived consistently.

## Theme synthesis

1. Very little public method-level data has release-based labels. Of the ten papers, the method/function-level datasets are ELFF (Shippey 2016; SZZ, 23 Java SVN projects, 69 versions, no evaluation), BugHunter (Ferenc et al. 2020 JSS; fix-commit before/after snapshots, not release-based) and PyTraceBugs (Python; traceback-exception bugs; abstract only). The Chowdhury et al. method-history dataset used by Opu et al. 2026 (774,051 Java methods, 49 projects) is a fourth. Ferenc et al. 2020 SQJ is class/file only. Wattanakriengkrai et al. provide line-level labels (and hence derivable method labels) for 32 Apache releases, including the ActiveMQ releases used in this project. None of these is Python with release-based labels, which supports the Python/Django gap noted earlier.
2. Cross-version evaluation is rare and never de-duplicated. Only Wattanakriengkrai (line level, k-1 -> k, 23 pairs), Falessi 2021 (class level, order-preserving 66/33 holdout) and Liu 2024 (module level; abstract only) use release-based splits. BugHunter and the Ferenc SQJ unified dataset use random 10-fold CV, and Ferenc pools several versions of the same project before cross-validating. Opu uses random 80/20 and LOO. Only Liu 2024 removes unchanged modules from target versions. Among the full texts read, no method- or line-level cross-version study removes unchanged code. BugHunter's conflict filtering (Sec 5.6) only resolves identical feature vectors with contradictory labels.
3. Label noise has three separate sources, each documented here. (a) Linkage gaps: ELFF link coverage averages ~41% (7.59%-93.84%, Table 2), and Jira affected-version availability is 14%-93% in Falessi (Table 4). (b) Dormant defects / snoring: most defects sleep >20% of releases (Ahluwalia 2019). 18%-98% of defective classes are missed when labelling at the end of training (Falessi Table 6), with a ~90% median relative loss in recall. Dropping non-defective instances of the last training release recovers MCC by ~32% on average (Table 9). (c) Tangled fixes: Opu et al. show that commit-message-based method labels are noisy and that LLM untangling increases metric separability. However, their downstream evidence is distributional, not predictive. BugHunter's JUnit validation (0.95% wrong entries) only checked comment-only mismatches.
4. Evaluation reporting is weak. BugHunter and the Ferenc SQJ paper report only F-measure/precision/recall (Ferenc also AUC), mostly with default Weka learners. Ferenc's Camel 1.0 (F 0.93-0.95 with AUC 0.39-0.49, Table 17) shows that F-measure misleads under skew. Falessi, Wattanakriengkrai and Opu report MCC. Wattanakriengkrai adds effort-aware Top20%LOC recall and IFA but omits precision by design. Possible tuning on evaluation data: LINE-DP's k=20 and the NLP-baseline entropy thresholds come from sensitivity analyses, with no stated held-out data. Falessi's AutoWEKA tuning is confined to training sets.
5. None of the ten papers is graph-based. Graph structure appears only incidentally: OpenStaticAnalyzer's internal element graph, and GraphCodeBERT used as a text embedder in Opu (F1 0.831, MCC 0.656 vs CodeBERT F1 0.782, MCC 0.533; Table 5). This track therefore contributes protocol and label constraints, not graph-model evidence.
6. Implications for the Django/ActiveMQ CFG+DDG study (my synthesis, not claims of the papers): (i) Use release N -> N+1 splits and remove methods whose normalised body is identical in N and N+1 from the test set (Liu 2024). Report both absolute scores and model rankings with and without them. (ii) Mature the labels: exclude or flag the most recent releases as test targets (Ahluwalia 2019; Falessi 2021) and consider dropping non-defective methods of the last training release. (iii) Run a tangling sensitivity check: restrict positives to single-method fixes, or apply a light untangling classifier (Opu). (iv) Report MCC, AUC and effort-aware measures (Top20%LOC recall, IFA, Popt) rather than F1 alone. (v) Treat graph readout/aggregation as a reported design choice (Zhang 2016, by analogy). (vi) The ActiveMQ releases likely come from the Yatish/LINE-DP corpus, so its issue-ID linkage and tangled-fix noise, and the 5.3.0 -> 5.8.0 release gap, apply directly.

## Additional papers found

- Chowdhury S., Uddin G., Hemmati H., Holmes R. (2024). Method-level Bug Prediction: Problems and Promises. ACM TOSEM. DOI 10.1145/3640331 (seen in search results; earlier session notes report time-aware evaluations drop to near-random). Method-level, uses ELFF/Ferenc/Mo datasets, realistic time-aware scenarios.
- Pascarella L., Palomba F., Bacchelli A. (2018). Re-evaluating method-level bug prediction. SANER 2018. DOI 10.1109/saner.2018.8330264 (from prior session; not re-verified here). Release-based re-evaluation of method-level prediction.
- Pascarella L., Palomba F., Bacchelli A. (2020). On the performance of method-level bug prediction: A negative result. JSS. DOI 10.1016/j.jss.2019.110493 (from prior session; not re-verified here).
- Herbold S., Trautsch A., Trautsch F., Ledel B. (2022). Problems with SZZ and features: An empirical study of the state of practice of defect prediction data collection. EMSE. DOI 10.1007/s10664-021-10092-4 (seen in search results). Label noise from SZZ variants.
- Yatish S., Jiarpakdee J., Thongtanunam P., Tantithamthavorn C. (2019). Mining software defects: should we consider affected releases? ICSE 2019. Source of the affected-release datasets used by LINE-DP and likely of this project's ActiveMQ releases. DOI not verified here (CrossRef check blocked).
- Pornprasit C., Tantithamthavorn C. (2022). DeepLineDP: Towards a deep learning approach for line-level defect prediction. IEEE TSE. Cross-release line-level, same corpus as LINE-DP. DOI not verified here.
- Tóth Z., Gyimesi P., Ferenc R. (2016). A Public Bug Database of GitHub Projects and its Application in Bug Prediction. ICCSA 2016. Traditional release-based class/file (and method in BugHunter Sec 6.3) GitHub Bug Dataset, 15 Java projects. DOI not verified here.
- Ferenc R., Gyimesi P., Gyimesi G., Tóth Z., Gyimóthy T. (2020). BugHunter Dataset, JSS 169:110691, DOI 10.1016/j.jss.2020.110691 (verified via CrossRef). Data DOI 10.17632/8tx7kjbkg4.2 (stated in the paper, Sec 5.8).
- Grund F., Chowdhury S., Bradley N. C., Hall B., Holmes R. (2021). CodeShovel: constructing method-level source code histories. ICSE 2021. Method-history tool behind the Chowdhury/Opu datasets. DOI not verified here.
- Herzig K., Just S., Zeller A. (2016). The impact of tangled code changes on defect prediction models. EMSE. File-level tangling impact. DOI not verified here.
- Giger E., D'Ambros M., Pinzger M., Gall H. C. (2012). Method-level bug prediction. ESEM 2012. Early method-level study, not release-based. DOI not verified here.
- HaPy-Bug: Human Annotated Python Bug Resolution Dataset (2025). arXiv:2504.04810 (seen in search results). Python bug-fix commits with annotation, a possible source for Python label validation.

## Access notes

- Full text: Ferenc 2020 SQJ (Springer OA), Wattanakriengkrai (IEEE OA). Shippey 2016 is the author copy from Lancaster EPrints.
- Preprints: BugHunter (arXiv 2006.10158), Falessi (arXiv 2105.12372), Opu (arXiv 2505.08263v3).
- Abstract only: PyTraceBugs, Ahluwalia 2019, Liu 2024 (paywalled, no open copy), Zhang 2016 (the author preprint at rebels.cs.uwaterloo.ca exists but the domain was not requested).