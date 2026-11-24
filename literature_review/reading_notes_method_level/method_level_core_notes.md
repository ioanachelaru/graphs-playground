# Method-level core: reading notes

Track: method-level defect prediction (focus on cross-version and graph-based evaluation). 11 items.

Access summary: full text read for Giger 2012, Pascarella 2018, Pascarella 2020, Ferenc 2020 (Array), Niedermayr 2019; author manuscript for Chowdhury 2024; arXiv v2 for Friesen 2025; replication package files only (paper not found) for the 2026 Zenodo item; abstract/secondary only for Hata 2012, Mo 2021, Jász 2024. Statements about abstract-only papers are provisional.

## Overview table

| Paper | Access | Cross-version at method level | Graph-based |
|---|---|---|---|
| Giger 2012 | full_text | No (random 10-fold) | No |
| Hata 2012 | abstract_only | Unknown (abstract only) | No |
| Pascarella 2018 | full_text | Yes, r_i-1 -> r_i | No |
| Pascarella 2020 | full_text | Yes, r_x-1 -> r_x | No |
| Mo 2021/22 | abstract_only | No (no time info) | No |
| Chowdhury 2024 | preprint | Partly (all releases < x -> x on Shippey data) | No |
| Ferenc 2020 (Array) | full_text | No (class level, mixed versions) | No |
| Niedermayr 2019 | full_text | No (10-fold, cross-project) | No |
| Friesen 2025 | preprint | No (leave-one-project-out) | No |
| Jász 2024 | abstract_only | Unclear (forward-in-time claim) | Partly (call-graph SEA metrics) |
| Anon. 2026 (Zenodo) | not_found | Partly (commit-time 70/30 cut) | No |


## Giger 2012: Giger E, D'Ambros M, Pinzger M, Gall HC. Method-level bug prediction. ESEM 2012, pp. 171-180.

DOI: 10.1145/2372251.2372285

- **Access:** full_text
- **Task and granularity:** Binary classification of methods as bug-prone (#bugs>=1) vs not (Sec 3.1, Eq. 1); also top-75/90/95th-percentile cut-points (Sec 3.3). Method level.
- **Language and data:** Java. 21 open-source (sub)systems: 14 Eclipse plug-ins plus Azureus 3, OpenXava, Jena2, Lucene, Xerces, Derby Engine, Ant Core; timeframes 1999-2011 (Table 1). Accepted-version PDF from ZORA (UZH repository).
- **Representation:** 9 source-code metrics (fanIN, fanOUT, localVar, parameters, commentToCodeRatio, countPath, McCabe complexity, execStmt, maxNesting; Table 2) computed on the snapshot at the END of the timeframe (Sec 2.2, Evolizer + Understand). 15 change metrics (methodHistories, authors, stmtAdded/Deleted and max/avg, churn variants, decl, cond, elseAdded/Deleted; Table 3) extracted with ChangeDistiller AST differencing over the whole timeframe (Sec 2.3).
- **Model:** Random Forest, Bayesian Network, SVM, J48 (RapidMiner) (Sec 3.1).
- **Baselines:** Comparison between metric sets (CM vs SCM vs CM&SCM) and classifiers only; no external baseline.
- **Evaluation setup:** Stratified 10-fold cross-validation per project; median over folds and projects; Related-samples Friedman test with post-hoc alpha adjustment (Sec 3.1-3.2). Metrics AUC, precision, recall.
- **Cross-version (release N -> later)?:** No. Single snapshot per project, random stratified 10-fold CV (Sec 3.1). Change metrics and bug counts are taken from the same timeframe.
- **Graph-based?:** No. ASTs are used only to diff revisions (ChangeDistiller); fanIN/fanOUT are scalar call-graph counts.
- **Duplication / leakage handling:** None. Bugs, change metrics and labels share the same time window, so bug-fix commits themselves increment methodHistories/authors/churn (later criticised by Pascarella 2018 Sec V and Chowdhury 2024 Sec 2.3). Code metrics measured after the fixes. No temporal ordering.
- **Label source and noise:** Bug-report references in commit messages (pattern matching, e.g. 'bug#345') mapped to methods changed in that revision (Sec 2.4). Threats section: unlinked bugs, tangled commits (argued minor because on average one method changed per bug-referencing revision), references that are not true bugs. About one third of methods labelled bug-prone (Sec 3.1).
- **Metrics and key results:** Table 4 (median over projects): RF CM AUC .95, P .84, R .88; SCM AUC .72, P .50, R .64; CM&SCM AUC .95, P .85, R .95. Change metrics significantly better than code metrics for all four classifiers. Table 5: with stricter cut-points AUC stays ~.97 for CM, but SCM precision falls to .13 at the 95th percentile.
- **Stated limitations:** Bug-linking bias and missing links; tangled changes; non-bug references counted as bugs; Eclipse/Apache dominance limits external validity (Threats section).
- **Critical assessment:** Foundational but leaky. Process metrics are computed over the same window in which the bugs are counted, so a method that was fixed necessarily has methodHistories>=1 and authors>=1; the very high AUC (.95) largely measures this coupling. Random 10-fold CV mixes methods from the same classes/files; no temporal or release split. ~32% positive rate makes precision look high (a random classifier already gets ~.32). Precision/recall/AUC only, no MCC or effort-aware measures. Pascarella 2018/2020 reproduced it (F ~.80-.86 under CV) and showed collapse to AUC ~.52 release-by-release.
- **Relevance to project:** Defines the classic method-level feature set (9 code + 15 change metrics) usable as a metric baseline. Its protocol is the main example of the leakage the project studies; any comparison with Giger-style numbers must state that they are within-window CV.

## Hata 2012: Hata H, Mizuno O, Kikuno T. Bug prediction based on fine-grained module histories. ICSE 2012, pp. 200-210.

DOI: 10.1109/icse.2012.6227193

- **Access:** abstract_only
- **Task and granularity:** Method-level bug prediction with historical metrics, compared with file- and package-level prediction under effort-based evaluation (abstract).
- **Language and data:** Java projects (abstract does not list them). Dataset published at github.com/hideakihata/MethodLevelBugPredictionDataset (found by web search, not inspected).
- **Representation:** Well-known historical (process) metrics computed on method histories obtained with Historage, a fine-grained Git-based version control system for Java (abstract).
- **Model:** Not stated in the abstract.
- **Baselines:** File-level and package-level prediction models (abstract).
- **Evaluation setup:** Effort-based evaluation (LOC to inspect) comparing granularity levels (abstract). Split protocol not available.
- **Cross-version (release N -> later)?:** Unknown from abstract; full text not accessed (green copy on NAIST repository was granted but the sandbox lost egress before download).
- **Graph-based?:** No (history-metric based per abstract).
- **Duplication / leakage handling:** Not determinable. Chowdhury 2024 (Sec 2.3) lists Hata et al. among MLBP studies evaluated with time-insensitive k-fold CV; this is a secondary claim, not verified in the primary text.
- **Label source and noise:** Not determinable from abstract.
- **Metrics and key results:** Abstract: method-level prediction outperforms package- and file-level prediction when inspection effort is accounted for; correlation analysis indicates past bug information does not contribute to method-level prediction. No numbers available.
- **Stated limitations:** Not available.
- **Critical assessment:** Provisional (abstract only). The effort-aware framing is its main contribution and the right lens for method-level SDP. The finding that past bugs do not help at method level is consistent with Chowdhury 2024 (bug-proneness decays with method age). Per Chowdhury 2024 the evaluation was time-insensitive CV; needs verification.
- **Relevance to project:** Supports reporting effort-aware measures (e.g. Effort@20%, Popt) alongside MCC for the CFG/DDG models. Historage-style method histories are an alternative to CodeShovel for tracking functions across Django/ActiveMQ releases.

## Pascarella 2018: Pascarella L, Palomba F, Bacchelli A. Re-evaluating method-level bug prediction. SANER 2018 (RENE track), pp. 592-601.

DOI: 10.1109/saner.2018.8330264

- **Access:** full_text
- **Task and granularity:** Replication of Giger et al. (RQ1) and release-by-release re-evaluation (RQ2). Binary buggy/non-buggy at method level.
- **Language and data:** Java. 13 GitHub systems (Ant, Checkstyle, Cloudstack, Eclipse JDT, Eclipse Platform, EMF Compare, Gradle, Guava, Guice, Hadoop, Lucene-solr, Vaadin, Wicket): 1.8M methods, 63.4k buggy methods, 91 releases (Table I). Accepted version from ZORA.
- **Representation:** Giger's 9 product + 15 process metrics, re-implemented (Tables II-III, Sec IV-A).
- **Model:** Random Forest, SVM, Bayesian Network, J48 (Weka, default parameters). Random over-sampling and correlation-based feature selection as preprocessing (Sec IV-A).
- **Baselines:** Giger et al. 2012 results; product vs process vs combined.
- **Evaluation setup:** RQ1: 10-fold CV on the last release window (R_last-1..R_last) (Sec IV-A). RQ2: train on release r_i-1, test on r_i, major releases detected by version name ending in 0 or 0.0 (Sec VI-A). Median P, R, F, AUC-ROC; Scott-Knott ESD.
- **Cross-version (release N -> later)?:** Yes, method level: release r_i-1 -> r_i, adjacent major releases only; labels = methods changed in ReLink-identified bug-fix commits in the window between the two releases (Sec VI-A). First release never tested, last never trained. Cloudstack, EMF Compare, Vaadin and Wicket have only 2 releases (Table I), i.e. one pair each.
- **Graph-based?:** No.
- **Duplication / leakage handling:** Temporal split removes look-ahead of the CV protocol. No handling of methods that are unchanged between r_i-1 and r_i (identical feature vectors with possibly different labels), no de-duplication, no release-window normalisation (windows range from months to years, Sec VI-B).
- **Label source and noise:** ReLink issue-commit linking (committer match, <7 days, VSM cosine>0.7), methods changed in linked bug commits; test code removed (Sec IV-A). Manual check of 275 Lucene-solr buggy methods: 85% correct, Krippendorff alpha 0.84 (Sec VII). SZZ deliberately not used (Sec V).
- **Metrics and key results:** RQ1 (Table IV, overall medians product/process/both): P .71/.80/.80, R .44/.80/.80, F .51/.80/.80, AUC .59/.72/.73; RF combined F .86, AUC .86. RQ2 (Table V, overall): P .71/.71/.71, R .59/.60/.60, F .62/.60/.61, AUC .52/.52/.53. Code metrics slightly better than process metrics in RQ2.
- **Stated limitations:** Re-implemented metrics; label imprecision; default classifier parameters; Java/open-source only (Sec VII).
- **Critical assessment:** The first explicit release-based method-level evaluation and the key negative result. Weaknesses: (1) precision ~.71 with AUC ~.52 means precision is close to the test-set base rate, i.e. positive rates in test releases are very high (Pascarella 2020 Table 2 shows e.g. Checkstyle 6,523 of 8,626 methods buggy), so P/R/F are uninformative and MCC is absent; (2) only adjacent major releases, very unequal window lengths; (3) unchanged methods across releases not controlled; (4) default hyper-parameters; (5) labels are 'changed in a bug-fix commit' during the release (fix-time), not 'contained the bug at release time'. Still, AUC ~.5 under a temporal split is a strong warning.
- **Relevance to project:** Closest design to the project's Django/ActiveMQ release-based setup. Its AUC drop is the benchmark the CFG/DDG models must beat; replicate its r_i-1 -> r_i protocol but add MCC, base rates per release, and an unchanged-method filter.

## Pascarella 2020: Pascarella L, Palomba F, Bacchelli A. On the performance of method-level bug prediction: A negative result. Journal of Systems and Software 161 (2020) 110493.

DOI: 10.1016/j.jss.2019.110493

- **Access:** full_text
- **Task and granularity:** Journal extension of the SANER 2018 paper: RQ1 replication, RQ2 release-by-release re-evaluation, RQ3 alternative features. Method level.
- **Language and data:** Same 13 Java systems (Table 1). Table 2 lists last-release methods and buggy methods (overall 329k methods, 79k buggy). Accepted version from ZORA.
- **Representation:** Giger product/process metrics plus RQ3 alternative features: textual (Buse-Weimer readability, comment-code textual coherence via VSM, comment categories; Table 8), method-level code smells, developer-related factors (Sec 7.1).
- **Model:** RF, SVM, BN, J48 (default parameters), random over-sampling, correlation-based feature selection (Sec 6.1).
- **Baselines:** Giger et al. 2012 numbers reported side by side (Table 5); models with and without alternative features.
- **Evaluation setup:** As SANER 2018: 10-fold CV for RQ1; r_x-1 -> r_x release-by-release for RQ2/RQ3 (Sec 6.1). P, R, F, AUC-ROC; Scott-Knott ESD.
- **Cross-version (release N -> later)?:** Yes, method level, adjacent major releases r_x-1 -> r_x (Sec 6.1, 'Bug Prediction Models: Validation').
- **Graph-based?:** No.
- **Duplication / leakage handling:** Same as 2018: temporal split only; no control of unchanged/duplicate methods across releases.
- **Label source and noise:** ReLink linking; buggy = methods changed in bug-linked commits between consecutive releases; test code removed (Sec 4.1, 6.1). Fisher et al. bug-commit detection re-evaluated at 84% precision in their context (Sec 8).
- **Metrics and key results:** Table 7 (release-by-release) is identical to SANER Table V: overall AUC .52/.52/.53, F .62/.60/.61. RQ3: textual features add about 4% F and 5% AUC to product+process; adding smells lowers F by 2%; developer factors add 4%; Scott-Knott ESD finds no model significantly better (Sec 7.2, Figs 2-3).
- **Stated limitations:** Label imprecision, re-implemented metrics, default parameters, Java only, subset of possible alternative metrics (Sec 8).
- **Critical assessment:** Confirms the negative result but inherits all 2018 issues. Internal inconsistency worth noting: Table 1 gives Guava 1.2k buggy methods over the whole history while Table 2 gives 10,221 buggy methods in the last release (similar for Eclipse JDT 3.3k vs 12,063), which suggests different counting units or label definitions between tables. Last-release positive rates of 30-76% (Table 2) are implausibly high for a single release window and make precision ~.71 meaningless. RQ3 improvements are reported as relative percentages without absolute AUC values in text.
- **Relevance to project:** Negative evidence that richer hand-crafted features (textual, smells, developer) do not rescue release-based method-level prediction; motivates testing whether structural CFG/DDG representations do. Its label-prevalence problem argues for reporting per-release base rates for Django/ActiveMQ.

## Mo 2021/22: Mo R, Wei S, Feng Q, Li Z. An exploratory study of bug prediction at the method level. Information and Software Technology 144 (2022) 106794 (online 2021).

DOI: 10.1016/j.infsof.2021.106794

- **Access:** abstract_only
- **Task and granularity:** Method-level bug prediction with code and history metrics (secondary sources). Note: no abstract text could be retrieved (closed access, no OA copy); everything below comes from Chowdhury et al. 2024 (Sec 3.1, Table 1, Table 5, Sec 4) and citing papers.
- **Language and data:** Java, 18 Apache projects per Chowdhury Table 1; Chowdhury Table 5 lists ActiveMQ, Ignite, Nutch, Camel, Flume, Struts, Maven, Kafka, Zookeeper, Avro, Drill, Wicket, Flink, HBase, Calcite, CXF, Cassandra.
- **Representation:** 21 code metrics and 19 change metrics (Chowdhury Table 1).
- **Model:** Random Forest only (Chowdhury Sec 4).
- **Baselines:** Unknown.
- **Evaluation setup:** 10-fold CV per project, AUC reported per project (Chowdhury Sec 4, Table 5).
- **Cross-version (release N -> later)?:** No (per Chowdhury Sec 4: dataset contains no timing information; only cross-project scenario could be re-evaluated).
- **Graph-based?:** No.
- **Duplication / leakage handling:** Per Chowdhury Sec 4: change history was collected over the method's whole lifetime and then used to label it; e.g. zero changes in lifetime implies not buggy, which is look-ahead leakage.
- **Label source and noise:** Not verified in primary text.
- **Metrics and key results:** Original per-project AUC (reproduced by Chowdhury, Table 5): ActiveMQ 0.87, Calcite 0.74, Ignite 0.90, Maven 0.89, Wicket 0.89 (range 0.74-0.90). Chowdhury's cross-project re-evaluation gave lower but still comparatively better numbers, which they attribute to the leakage (Sec 4, Fig 3).
- **Stated limitations:** Not available.
- **Critical assessment:** Provisional (secondary sources only). If Chowdhury's reading is right, the reported AUCs are inflated by lifetime-level history features that encode the label. The dataset is public and includes ActiveMQ and Calcite.
- **Relevance to project:** Directly overlaps the project's systems (ActiveMQ; Calcite from earlier experiments). Its public metric dataset could serve as an external metric baseline, but only after rebuilding features with release-time cut-offs.

## Chowdhury 2024: Chowdhury S, Uddin G, Hemmati H, Holmes R. Method-level bug prediction: Problems and promises. ACM TOSEM 33(4), 2024.

DOI: 10.1145/3640331

- **Access:** preprint
- **Task and granularity:** Re-evaluation of existing method-level bug prediction (MLBP) datasets/models in time-sensitive scenarios (RQ1) and four improvement avenues: label accuracy (RQ2), method age for concept drift (RQ3), training-project selection (RQ4), size-specific models (RQ5). Method level.
- **Language and data:** Java. Three public datasets: Ferenc et al. 2020 (15 projects, 37 code metrics), Shippey et al. 2016 (23 projects, 29 code metrics), Mo et al. 2022 (18 projects, 21 code + 19 change metrics) (Table 1). New dataset: 774,051 methods from 49 projects, 146,749 getters/setters (Table 2), histories via CodeShovel, metrics via JavaParser (Sec 3.2). Author manuscript (cs.ubc.ca), 30 pp.
- **Representation:** Code metrics (size SLOC, McCabe, Buse readability, fan-out, maintainability index) and change indicators (revisions, diff size, added lines, Levenshtein distance) (Sec 3.2.2, 5.2).
- **Model:** Weka J48, Random Forest, Random Tree, SimpleLogistic, DecisionTable (Sec 4, Tables 3-4); RF for RQ4/RQ5.
- **Baselines:** Reproduced original 10-fold CV results of Ferenc et al. and Mo et al. (Tables 3, 5).
- **Evaluation setup:** RQ1 three scenarios: (i) cross-project, (ii) cross-project + past of test project, (iii) only past of test project (Sec 4). Ferenc data: first half of each test project's lifetime for training, last half for testing (Fig 1 caption). Shippey data: all releases before x train, release x test (Sec 4). Mo data: scenario i only. RQ2-RQ3: distribution comparisons with Wilcoxon and Cliff's delta, not prediction.
- **Cross-version (release N -> later)?:** Partly. Scenario ii/iii on Shippey et al. data is release-based at method level (all releases < x -> x, Sec 4); on Ferenc data it is a half-lifetime time split. Mo data has no time info. No adjacent-release N -> N+1 protocol and no per-release tables; results are CDFs over projects (Figs 1-3).
- **Graph-based?:** No.
- **Duplication / leakage handling:** Identifies leakage from k-fold CV and from lifetime-level change features (Sec 2.3, Sec 4 on Mo dataset). Does not de-duplicate or remove unchanged methods; getters/setters (~19%) kept because conclusions did not change (Sec 3.2.1).
- **Label source and noise:** Traditional labels: Ray et al. keywords (error, bug, fix, issue, ...). 'Accurate' labels (Sec 5.1): keyword 'issue' removed, 'misfeature' added, bug and fix word in the same sentence, only commits modifying exactly one method, only the modified version is buggy; not-buggy requires unchanged >=2 years and no later keyword commit. Manual analysis of 500 commits motivated this. ~60% of bug-fix commits modify >1 method, >15% modify >=10 (Fig 4).
- **Metrics and key results:** Reproduced 10-fold CV: Ferenc RF P .648, R .720, F .682 (orig .633/.632/.631) (Table 3); Shippey RF F .717 (Table 4); Mo per-project AUC .74-.90 (Table 5). Time-sensitive: Ferenc scenario i precision within ~0.37 and F1 within ~0.50 for 80% of projects (Sec 4, Fig 1); Shippey scenario i precision within ~0.13 and F1 within ~0.25, better but still low in ii/iii (Fig 2). RQ2: size Cliff's delta negligible in 30.61% of projects with traditional labels vs large in 97.67% with accurate labels (Table 6). RQ3: bug-fix proportion decays with method age, fitted by Zipf (Fig 7). RQ4: for every test project some smaller training-project subset beat using all projects (Fig 9). RQ5: precision/F1 lower on small methods (<=36 SLOC), higher on large (Fig 11).
- **Stated limitations:** Only three public datasets; Java open-source only; CodeShovel string-similarity errors with overloading; keyword choice; bug age approximated by fix time (Sec 7).
- **Critical assessment:** Strongest critique of MLBP evaluation, but its own positive claims are weaker than presented. (1) RQ2 shows univariate separability, not predictive performance; the 'accurate' set keeps only single-method fixes and methods untouched for 2 years, which selects easy, large-vs-stable contrasts and changes the population, so the large effect sizes are partly a selection artefact. (2) RQ4 reports, per test project, the best of several random subsets chosen on the test project itself, an oracle that is optimistic by construction. (3) No MCC or effort-aware measures; results only as CDF plots, so exact numbers are hard to extract. (4) No duplicate/unchanged-method control. (5) No model with age features is actually trained and evaluated to show the RQ3 promise. The RQ1 negative result is robust across three datasets.
- **Relevance to project:** Main reference for the leakage argument and for label construction (single-method fixes, survival window for 'not buggy'). Its method-age finding suggests adding age/'unchanged since last release' features or stratifying evaluation by changed vs unchanged functions in Django/ActiveMQ.

## Ferenc 2020 (Array): Ferenc R, Bán D, Grósz T, Gyimóthy T. Deep learning in static, metric-based bug prediction. Array 6 (2020) 100021.

DOI: 10.1016/j.array.2020.100021

- **Access:** full_text
- **Task and granularity:** CLASS-level binary bug prediction (abstract; Sec 3.2), not method level. The task list assumed method-level BugHunter data; the method-level BugHunter paper is Ferenc et al. 2020 JSS (10.1016/j.jss.2020.110691), used by Chowdhury 2024 and Jász 2024.
- **Language and data:** Java. Class-level part of the Unified Bug Dataset: 47,618 classes (8,780 buggy, 18%), merged from PROMISE, Bug Prediction Dataset and GitHub Bug Dataset (Sec 3.2). OA PDF from publicatio.bibl.u-szeged.hu.
- **Representation:** 60 static class metrics from OpenStaticAnalyzer (size, coupling, cohesion, inheritance, clone, documentation; Table 2), standardised.
- **Model:** Deep rectifier fully connected networks (TensorFlow, 'sdnnc'), tuned layers/neurons/epochs/learning rate, early stopping with 'new bob' learning-rate halving; compared with scikit-learn kNN, GaussianNB, decision tree, random forest, linear and logistic regression, SVC; ensembles (Sec 3.3, 4).
- **Baselines:** Tuned scikit-learn classifiers (Sec 3.3).
- **Evaluation setup:** Stratified 10-fold train/dev/test: per run one bin dev (hyper-parameters, early stopping), one bin test, 8 train; confusion matrices pooled across folds; F-measure primary, AUC for best models (Sec 3.1, 3.4). Upsampling 50% of the class gap in training only.
- **Cross-version (release N -> later)?:** No. Random stratified folds over all versions of all projects; authors explicitly decide not to treat 'the future predicting the past' as a threat (Sec 3.2).
- **Graph-based?:** No.
- **Duplication / leakage handling:** None. Multiple versions of the same project are mixed across folds (Sec 3.2), so near-identical classes from consecutive releases can be in train and test. Hyper-parameters chosen on the dev bin, not the test bin (Sec 4, learning-rate step).
- **Label source and noise:** Inherited from the three source datasets (bug counts binarised). Threats section asserts dataset reliability without new validation.
- **Metrics and key results:** Best DNN F-measure 53.59%; random forest 0.12 points higher; best ensemble (DNN+RF) 55.27% (abstract, Sec 1). A learning-curve experiment suggests DNNs gain more from additional data (Sec 4).
- **Stated limitations:** Dataset reliability; parameter search is not exhaustive; results depend on the unified dataset (Sec 5).
- **Critical assessment:** Off-target for this track (class level). Its protocol mixes releases of the same project across folds and the authors explicitly accept future-to-past prediction, so the F-measures are leakage-prone. The gain of DNN over a tuned RF is nil (RF is 0.12 points better). Useful mainly as an example of careful dev/test separation for tuning and of resampling only the training data.
- **Relevance to project:** Low for the method-level question. Relevant as a cautionary example of mixing versions in CV, which mirrors the duplicate-across-release problem the project studies.

## Niedermayr 2019: Niedermayr R, Röhm T, Wagner S. Too trivial to test? An inverse view on defect prediction to identify methods with low fault risk. PeerJ Computer Science 5:e187 (2019).

DOI: 10.7717/peerj-cs.187

- **Access:** full_text
- **Task and granularity:** Inverse defect prediction: identify methods with low fault risk (LFR) at method level, optimising precision of the 'not faulty' class (Sec 1, 4).
- **Language and data:** Java. Defects4J: JFreeChart, Closure Compiler, Commons Lang, Commons Math, Mockito, Joda-Time; 395 bug-fix patches, 10 non-semantic method changes removed (Sec 5.2-5.3, Table 2). Faulty methods per project 39-148.
- **Representation:** 39 AST-based code metrics/flags per method (SLOC, McCabe, nesting, method chaining, unique variables, counts of 26 Java constructs, getter/setter/constructor/empty/delegation/toString flags; Table 1), computed with Eclipse JDT; discretised into tertiles or 'has-no' booleans (Sec 4.1, Table 3).
- **Model:** Association-rule mining (Apriori, arules) with consequent NotFaulty, min support 10%, min confidence 90%, top-n rules OR-ed; SMOTE on training data (Sec 4.2-4.3, 5.4). Authors report RF was worse (Sec 4.3).
- **Baselines:** None external; within- vs cross-project variants and two rule thresholds (2.5%, 5%).
- **Evaluation setup:** Within-project stratified 10-fold CV (RQ1-2); cross-project: train on the other five projects, test on the sixth (RQ3) (Sec 5.4). Measures: faults in LFR, LFR share of methods/SLOC, fault-density reduction factor.
- **Cross-version (release N -> later)?:** No. Single snapshot per project; random 10-fold within project and leave-one-project-out across projects.
- **Graph-based?:** No.
- **Duplication / leakage handling:** Methods fixed multiple times merged into one instance by majority vote (Sec 4.2). Snapshot mismatch: faulty methods are measured at their faulty state, non-faulty methods at the state of the last bug-fix commit (Fig 1 caption, Sec 5.4), so the two classes come from different points in time. No de-duplication of identical trivial methods (getters/setters) across folds.
- **Label source and noise:** Defects4J minimal, manually curated, reproducible bug patches (Sec 5.2); high precision but under-approximates faults (only reproducible bugs) (Sec 6.3.1). Replication on two Giger et al. systems reported as similar (Sec 6.3.1).
- **Metrics and key results:** Within-project strict classifier (Table 4): median 0.3% of LFR methods faulty, LFR = 31.7% of methods / 14.8% of SLOC, containing 6.0% of faults; fault-density reduction median 5.7 (methods), 3.2 (SLOC). Cross-project strict (Table 6): LFR 23.3% of methods / 8.1% of SLOC, 1.9% of faults, reduction median 10.9 (methods), 3.9 (SLOC). Example rule for Lang: <2 unique variables and no method invocations => NotFaulty, confidence 100% (Table 5).
- **Stated limitations:** Trivial methods can still be faulty (missing code); Defects4J under-approximation; library projects only; Java-specific constructs; faults treated as equally important (Sec 6.1, 6.3).
- **Critical assessment:** Sound idea with honest metrics (fault-density reduction is effort-aware). Caveats: very few faulty methods per project (39-148), so 0.3% vs 0.4% differences rest on single digits; random CV within project; measuring faulty and non-faulty methods at different snapshots can introduce systematic differences; 'triviality' is close to size, so most of the signal may be SLOC.
- **Relevance to project:** Practical: trivial functions (getters, empty, delegation) form a large near-duplicate, near-zero-risk population. Filtering or stratifying them (and Django's many tiny functions) before evaluating CFG/DDG models avoids inflated metrics and is a cheap baseline ('size/triviality rule').

## Friesen 2025: Friesen E, Morton-Salmon S, Opu MNI, Islam S, Chowdhury S. The Repeat Offenders: Characterizing and predicting extremely bug-prone source methods. arXiv:2511.22726v2 (27 Feb 2026).

DOI: 10.48550/arxiv.2511.22726

- **Access:** preprint
- **Task and granularity:** Characterise and predict, at method inception, 'ExtremelyBuggy' methods (involved in >1 bug-fix commit) vs others; method level (Sec 1, 3.5, 4.3).
- **Language and data:** Java. ~1.25M methods from 98 projects (49 from Chowdhury 2024 + 49 new top-starred GitHub repos with >=2000 commits); after 5-year age normalisation 691,610 methods from 92 projects (Sec 3.1, 3.4). Histories via CodeShovel. Note: the DOI 10.48550/arxiv.2511.22726 was not found in CrossRef; text retrieved from arxiv.org/pdf/2511.22726.
- **Representation:** 14 method code metrics at the introduction commit: SLOCStandard, Buse and Posnett readability, McCabe, NVAR, NCOMP, McClure, IndentSTD, MaximumBlockDepth, totalFanOut, Maintainability Index, Parameters, LocalVariables, Halstead Length (Sec 3.2). FanIn omitted because per-commit call graphs were too costly (Sec 3.2).
- **Model:** Logistic regression, decision tree, random forest, AdaBoost, MLP; scikit-learn defaults; under- and over-sampling (Sec 4.3).
- **Baselines:** None external; algorithm comparison only.
- **Evaluation setup:** Leave-one-project-out over 92 projects; precision, recall, F1, AUC, MCC (Sec 4.3).
- **Cross-version (release N -> later)?:** No. Cross-project leave-one-project-out with features at method inception and labels from the following 5 years (Sec 3.4, 4.3).
- **Graph-based?:** No.
- **Duplication / leakage handling:** Project-level split avoids within-project leakage (Sec 4.3). Age normalisation: only methods >=5 years old, only changes in their first 5 years (Sec 3.4). No clone/duplicate control across projects (forks excluded at selection, Sec 3.1.1).
- **Label source and noise:** Three label sets (Sec 3.3): HighRecall (Ray et al. keywords incl. 'issue', tangled commits kept), HighPrecision (Chowdhury keyword pairs, exactly one method changed), Balanced (same keywords, <=5 methods changed). Manual check removed 22 of 287 HighPrecision ExtremelyBuggy methods as false positives (mainly keyword 'flaw') (Sec 4.4).
- **Metrics and key results:** Prevalence (Table 1): ExtremelyBuggy 6.63% (HighRecall), 0.04% (HighPrecision, 287), 0.17% (Balanced, 1,195). In HighRecall, ExtremelyBuggy methods cover >=60% of bugs for ~80% of projects (Fig 4). At inception ExtremelyBuggy methods are larger, less readable, more complex: large Cliff's delta for 13 of 14 metrics (Table 2). Prediction (Fig 6, Balanced, undersampling): precision below 0.25 for ~75% of projects, recall above 0.5 for ~90%; judged not usable. Thematic analysis of 265 methods: confusing control flow 58.5%, abnormal size 35.1% (Table 4).
- **Stated limitations:** CodeShovel inaccuracy; keyword labels; HighPrecision biased to single-method bugs; Java/English-only; 5-year threshold (re-run with 2 and 8 years, same conclusions) (Threats).
- **Critical assessment:** Careful on labels and leakage (project-level split, inception-time features), but the prediction result is reported only as CDF figures with no table of MCC/AUC values; default hyper-parameters; extreme imbalance (0.17%) makes precision near-hopeless for any feature set. The large univariate effect sizes vs poor classifiers again show that separability on pooled data does not translate into prediction. 'Confusing control flow' as the top manual theme is a direct argument for control-flow representations.
- **Relevance to project:** Supports trying CFG-based features: the dominant manual characteristic of repeat-offender methods is control-flow complexity that scalar McCabe does not capture well. Also a template for inception-time (no-history) evaluation and for multiple label-noise variants.

## Jász 2024: Jász J. The effectiveness of hidden dependence metrics in bug prediction. IEEE Access 12 (2024) 77214-77225.

DOI: 10.1109/access.2024.3406929

- **Access:** abstract_only
- **Task and granularity:** Method-level bug prediction with new 'hidden dependence' metrics (abstract).
- **Language and data:** Java; method-level part of the BugHunter dataset (per ResearchGate full-text snippet found by web search). Online appendix: IEEE Dataport doi:10.21227/t74t-vj82 (adds file locations to BugHunter methods).
- **Representation:** Dependence metrics derived from the Static Execute After (SEA) relation computed on the call graph, approximating which methods can execute after a given one (secondary snippet citing ref [16]); combined with or compared to traditional BugHunter method metrics.
- **Model:** Several classifiers; Random Forest best by F-measure (abstract).
- **Baselines:** Traditional method-level metrics (abstract).
- **Evaluation setup:** Not available beyond abstract; abstract claims the metrics also predict 'bugs that will appear later in a given project if sufficient learning data is available', implying some temporal experiment.
- **Cross-version (release N -> later)?:** Unclear. A forward-in-time experiment is claimed in the abstract; split details unknown (full text not accessed: ieeexplore blocked, sandbox egress later lost).
- **Graph-based?:** Yes, partly: interprocedural call-graph-based SEA dependence relation turned into scalar metrics; no GNN, no CFG/DDG learning.
- **Duplication / leakage handling:** Unknown. BugHunter contains per-bug before/after snapshots of the same methods, so duplicate handling matters; not verifiable from abstract.
- **Label source and noise:** BugHunter (issue-tracker-linked GitHub bug fixes; buggy = method state before fix) per secondary sources; not verified.
- **Metrics and key results:** Abstract: outperforms traditional metrics in most cases; with filtering, up to 11% F-measure improvement for Random Forest.
- **Stated limitations:** Not available.
- **Critical assessment:** Provisional. Single-author, F-measure-only claim ('up to 11%' is a best case after filtering). If evaluated on BugHunter with random CV, before-fix and after-fix versions of the same method can land in train and test. Worth a full read because it is the only paper in this track using program-dependence structure at method level.
- **Relevance to project:** Closest to the project's graph idea: shows dependence information (interprocedural) adds signal to method metrics. The project's Joern CFG+DDG are intraprocedural; SEA/call-graph context could be a complementary feature.

## Anon. 2026 (Zenodo): Anonymous. Method-Level Bug Prediction: How Far Are We? Replication package, Zenodo, published 2026-06-28 (record 20986662/20986663), CC-BY-4.0.

DOI: 10.5281/zenodo.20986662

- **Access:** not_found
- **Task and granularity:** Paper text not found. Replication package README, Code.zip and Results.zip read directly. Two tasks (README 'Study at a glance'): Inception = will the first version of a method ever become buggy; Versioned = for each method version, is the next change to it a bug fix. Method level.
- **Language and data:** Java, 99 projects (Results/Tables/dataset_distribution.csv; README says ~99), top-starred GitHub projects incl. spring-boot, guava, flink, netty (projects_full.csv); 11 projects excluded in config.py. Rows: Inception Noisy 745,795 (5.42% buggy), Inception LessNoisy 736,664 (3.19%), Versioned ('Evolution') Noisy 2,223,904 (2.19%), LessNoisy 2,240,773 (1.25%) (dataset_distribution.csv). Pipeline mirrors Chowdhury 2024: HistoryFinder/CodeShovel-style histories and a ComplexityAnalyzer tool (README).
- **Representation:** Code metrics, change history, bug history, developer metrics, and source-code embeddings (default model Qwen/Qwen3-Embedding-8B in 6_generate_embeddings.py), stored once per content hash (README).
- **Model:** LR, DT, RF, XGBoost, MLP; fusion networks of metrics+embeddings (concat, gated, attention, attention-gated, FiLM); samplers RUS/ROS/SMOTE (Results tables).
- **Baselines:** Metrics-only classifiers vs fusion with embeddings; noisy vs less-noisy labels.
- **Evaluation setup:** Project-wise split: 70% of projects train, remaining 30% split 2:1 test/validation (seed 42), plus project-wise 10-fold CV (modules/data_splitter.py). Versioned family also has a per-project temporal 'version split': rows ordered by ProjectAgeAtCurrentRevision, oldest 70% train, newest 30% randomly split 1/3 val and 2/3 test; variants with 30/50/70% train (data_splitter.py; Results/RQ2/RQ2_4*). Top configurations selected on validation (table captions). Metrics: accuracy, per-class P/R/F1, macro-F1, MCC, ROC-AUC, PR-AUC (README).
- **Cross-version (release N -> later)?:** Partly, commit-time based, not release based: per-project 70/30 cut on commit-time ordering of method versions (data_splitter.py, _version_split_labels). No release N -> N+1 protocol. Project-wise splits are cross-project.
- **Graph-based?:** No (metrics and text embeddings only).
- **Duplication / leakage handling:** Project-wise splits keep each project wholly in one partition (code comment claims no method leaks). Version split: earlier versions of the same method are in training while later versions are tested; no de-duplication of identical code (embeddings are deduplicated by content hash, implying identical bodies recur). Possible label look-ahead: the Versioned label depends on the next change, which for rows just before the cut can fall in the test period; the splitter does not drop such rows (provisional, from code reading). Val and test are random draws from the same tail.
- **Label source and noise:** Commit-message keywords: BuggyCommit (action word + bug word in same sentence, or 'bug#') is the conservative label; PotentiallyBuggy and Risky are broader (README table). LessNoisy variants re-label tangled commits with an LLM 'untangler' (default model openai/gpt-oss-20b, 2-shot, chain-of-thought; 4_untangle.py, modules/untangler.py). METHOD_AGE_LOWER_BOUND and NO_BUG_DURATION = 5 years (config.py).
- **Metrics and key results:** Validation-set top configurations: Inception Noisy MLP+RUS MCC 0.18, PR-AUC 0.15; Inception LessNoisy MLP+RUS MCC 0.21; Inception LessNoisy fusion concat MCC 0.26, PR-AUC 0.21, F1-buggy 0.29 (rq1_1/1_2/1_3_top_results.tex). Versioned LessNoisy MLP MCC 0.23; gated fusion MCC 0.24, PR-AUC 0.17 (rq2_2/2_3_top_results.tex). Test, temporal version split (rq2_3_comparison_v_split.tex): MCC 0.224 (50% train), 0.217 (70%), 0.200 (30%); PR-AUC 0.143-0.182. Test per-run, RQ2_4 version split: MCC 0.164-0.197, PR-AUC 0.117-0.140; RQ2_3 project split (25 fusion runs across samplers/configs): MCC 0.066-0.120, PR-AUC 0.029-0.086 (Results/RQ2/RQ2_3 and RQ2_4 test CSVs; 5 runs for RQ2_4).
- **Stated limitations:** Not available (paper not found).
- **Critical assessment:** Most rigorous evaluation design in this track (validation-based selection, MCC and PR-AUC, project-wise and temporal splits, label-noise variants), and its numbers are sobering: MCC ~0.1 cross-project and ~0.2 temporal, PR-AUC 0.03-0.18 at 1-5% base rates. Caveats: temporal split is per commit rather than per release; same-method earlier versions in training and possible next-change label look-ahead may favour the version split over the project split; LLM untangling is unvalidated in the package; anonymous, unpublished. All numbers here are from package files, not a paper, and are provisional.
- **Relevance to project:** Gives realistic reference levels (MCC 0.1-0.25, PR-AUC well below 0.2) for method-level prediction with metrics plus code embeddings, i.e. the same family as the project's doc2vec/CodeBERT baselines. The gap between version split and project split is a leakage signal the project can test explicitly with de-duplicated release-based splits.

## Theme synthesis

1. Protocol determines the result. Every method-level study that reports high performance (Giger 2012: AUC .95; Mo 2021: AUC .74-.90; Pascarella RQ1: F .80-.86) used random k-fold CV within a single window, with process metrics and labels taken from the same period. Every study that moved to a time-respecting or cross-project split reports near-chance or low performance: Pascarella 2018/2020 release-by-release AUC .52-.53; Chowdhury 2024 cross-project precision within ~.37 (Ferenc data) and ~.13 (Shippey data) for 80% of projects; Friesen 2025 precision <.25 for ~75% of projects; the 2026 Zenodo package MCC .07-.12 cross-project and .16-.22 on a commit-time split.
2. Genuinely release-based (N-1 -> N) method-level evaluations are rare. Only Pascarella 2018/2020 do adjacent major releases. Chowdhury 2024 uses all-previous-releases -> release x on Shippey data, and half-lifetime splits on Ferenc data. The Zenodo package uses a commit-time 70/30 cut. None reports per-release base rates together with MCC, and none controls for methods that are unchanged between training and test releases. So the project's question (does leakage from unchanged/duplicate functions inflate cross-version results?) is open at method level.
3. Leakage mechanisms identified in this track: (a) same-window process metrics that encode the label (Giger; Mo per Chowdhury); (b) future information in features or labels (lifetime history; next-change labels near a temporal cut in the Zenodo package, provisional); (c) mixing releases of the same project in CV (Ferenc Array explicitly accepts it); (d) unchanged or near-identical methods across releases (no paper handles it; the Zenodo package deduplicates embeddings by content hash, which shows identical bodies recur); (e) tuning on test data (avoided by Ferenc Array and the Zenodo package; Chowdhury RQ4 picks the best subset per test project, an oracle).
4. Label noise is large and changes conclusions. Keyword labels with 'issue' and tangled commits produce negligible-to-small metric differences between buggy and clean methods; single-method fixes produce large ones (Chowdhury Table 6). About 60% of bug-fix commits touch more than one method (Chowdhury Fig 4). Positive rates vary from 0.04% to ~76% depending on definition (Friesen Table 1; Pascarella 2020 Table 2). The Zenodo package uses an LLM untangler. Results across papers are therefore not comparable without stating the label definition and the base rate.
5. Metrics reporting is weak. Most papers report precision/recall/F1 or AUC only; Pascarella's precision ~.71 at AUC ~.52 shows precision tracking the base rate. MCC and PR-AUC appear only in Friesen (figures only) and the Zenodo package. Effort-aware evaluation appears in Hata 2012 and Niedermayr 2019 (fault-density reduction).
6. Representations. All core method-level studies use scalar code/process metrics; the Zenodo package adds a general text-embedding model. No paper in this track learns from CFG or data-dependence graphs at method level. The only dependence-structure paper is Jász 2024 (call-graph SEA metrics, abstract only, F-measure gain up to 11%). Qualitative evidence favours control-flow structure: 'confusing control flow' is the top theme (58.5%) among repeat-offender methods (Friesen Table 4), while scalar McCabe separates groups in pooled statistics but not in prediction.
7. Python is absent: all eleven items study Java.
8. Implications for the project: evaluate Django/ActiveMQ CFG+DDG models with release N -> N+1 splits; report per-release base rates, MCC, PR-AUC and an effort-aware measure; stratify or filter test functions by changed vs unchanged since the training release and by exact/normalised-body duplicates; include strong cheap baselines (size/triviality rule, Giger-style metrics with release-time cut-offs, method age); state the label definition (single-method fixes vs all fix-touched functions) and report sensitivity to it.

## Additional papers found

- Ferenc R, Gyimesi P, Gyimesi G, Tóth Z, Gyimóthy T. An automatically created novel bug dataset and its validation in bug prediction (BugHunter, method/class/file level). JSS 169 (2020) 110691. DOI 10.1016/j.jss.2020.110691 (DOI as given in Friesen 2025 references).
- Shippey T, Hall T, Counsell S, Bowes D. So you need more method level datasets for your software defect prediction? Voilà! ESEM 2016 (release-ordered method-level dataset used by Chowdhury 2024; DOI not verified).
- Chowdhury S. The good, the bad, and the monstrous: Predicting highly change-prone source code methods at their inception. ACM TOSEM 2025. DOI 10.1145/3715006 (from Friesen 2025 references).
- Esposito M, Falessi D. Uncovering the hidden risks: The importance of predicting bugginess in untouched methods. SCAM 2023, pp. 277-282 (six projects; directly about unchanged methods; DOI not verified).
- Falessi D, Mesiano Laureani S, Çarka J, Esposito M, da Costa DA. Enhancing the defectiveness prediction of methods and classes via JIT. Empirical Software Engineering 28(2):37, 2023 (DOI not verified).
- Falessi et al. The impact of dormant defects on defect prediction: A study of 19 Apache projects (listed on author bibliography; venue/DOI not verified).
- A defect is being born: How close are we? A time sensitive forecasting approach. arXiv:2601.01921 (2026; cites Pascarella 2020 and Esposito & Falessi 2023; not read).
- La Prova D, Gentili E, Falessi D. Anticipating bugs: Ticket-level bug prediction and temporal proximity effects. EMSE 31(2):43, 2026; arXiv:2506.14290.
- Chowdhury S, Kidwai H, Asaduzzaman M. Evidence is all we need: Do self-admitted technical debts impact method-level maintenance? MSR 2025 (DOI not verified).
- Grund F, Chowdhury S, Bradley NC, Hall B, Holmes R. CodeShovel: Constructing method-level source code histories. ICSE 2021, pp. 1510-1522 (tool for tracking methods across versions).
- Jász J. The effectiveness of hidden dependence metrics in bug prediction - online appendix. IEEE Dataport, 2024. DOI 10.21227/t74t-vj82.
- Hata H et al. MethodLevelBugPredictionDataset, github.com/hideakihata/MethodLevelBugPredictionDataset (dataset of Hata et al. ICSE 2012).
- Cohen M, Rokach L, Puzis R. Cross version defect prediction with class dependency embeddings. arXiv:2212.14404 (class-level graph embeddings, 24 release pairs, AUC +4.7% over baseline per abstract).
- DIDP: A fine-grained defect prediction method based on drift-immune graph neural networks (PDG slicing + GNN, file/statement level; Computers, Materials & Continua, 2024-2025; DOI not verified).
- Software defect prediction based on graph code semantics. Expert Systems with Applications 2025 (ScienceDirect pii S0957417425034578): per-method CFG/PDG via improved TinyPDG, CBOW embeddings, aggregated to file level (DOI not verified).
- A method-level defect prediction approach based on structural features of method-calling network (ResearchGate 367371109; venue/DOI not verified).
- Bangash AA, Sahar H, Hindle A, Ali K. On the time-based conclusion stability of cross-project defect prediction models. EMSE 25(6), 2020 (cited by Chowdhury 2024 on time-aware evaluation).
- Wattanakriengkrai S, Thongtanunam P, Tantithamthavorn C, Hata H, Matsumoto K. Predicting defective lines using a model-agnostic technique. IEEE TSE 48(5):1480-1496, 2022 (line-level, release-based).
