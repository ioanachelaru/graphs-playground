# Cross-version, method-level defect prediction: initial review

*First pass, based on OpenAlex records and abstracts (24 papers screened). No full texts were read yet. Treat every number as provisional.*

## Key points

1. **Method-level results collapse under realistic evaluation.**
   - Early studies reported strong results: [Giger et al. 2012](https://doi.org/10.1145/2372251.2372285) reached 84% precision and 88% recall on 21 Java systems, and [Hata et al. 2012](https://doi.org/10.1109/icse.2012.6227193) found method-level prediction more effort-efficient than file level.
   - Those results did not survive time-aware evaluation. [Pascarella et al. 2018](https://doi.org/10.1109/saner.2018.8330264) and [2020](https://doi.org/10.1016/j.jss.2019.110493) replicated them, then evaluated with a more realistic strategy. Performance fell to near-random, and textual, smell and developer features did not help.
   - [Chowdhury et al. 2024](https://doi.org/10.1145/3640331) (TOSEM; 3 public datasets plus 774,051 Java methods from 49 projects) reach the same verdict: models are not ready for industry use, and accuracy "dwindles" in time-sensitive evaluation.
   - Chowdhury et al. name four improvement avenues: noise-free labels, handling concept drift (method age), similar training projects, and mixtures of models.
   - Label noise is a major cause. In their data, 60% of bug-fix commits modify more than one method, and over 15% modify at least 10 (Sec. 5.1, per the ACM page).
2. **Cross-version defect prediction (CVDP) studies are mostly file- or class-level, on PROMISE data.** They treat the problem as distribution shift between releases and propose remedies such as:
   - subset selection: [HALKP](https://doi.org/10.1109/saner.2018.8330210), [DS3](https://doi.org/10.1145/3196321.3196331), [TSTSS](https://doi.org/10.1016/j.jss.2019.03.027), [AVDP 2026](https://doi.org/10.1016/j.array.2026.101239)
   - regularised regression: [Yang & Wen 2018](https://doi.org/10.1109/tr.2018.2847353)
   - borrowing cross-project methods or data: [Amasaki 2018](https://doi.org/10.1145/3273934.3273938), [2020](https://doi.org/10.1007/s10664-019-09777-8)
   - concept-drift detection with chronological splitting: [Kabir et al. 2023](https://doi.org/10.3390/sym15101934)

   None of these abstracts mentions duplicate or unchanged modules.
3. **Label timing biases cross-version data.**
   - Defects often "sleep" across releases. In 282 releases of 6 Apache projects, most defects slept for more than 20% of the releases ([Ahluwalia et al. 2019](https://doi.org/10.1109/msr.2019.00019)).
   - [Falessi et al. 2021](https://doi.org/10.1145/3467895) studied 19 Apache projects. They measure how this affects classifiers and test dropping the most recent releases from training as a countermeasure.
   - Conclusions about cross-project models also change over time ([Bangash et al. 2020](https://doi.org/10.1007/s10664-020-09878-9)).
4. **Unchanged code is a known but rarely controlled problem.** [Liu et al. 2024](https://doi.org/10.1002/smr.2715) (481 target versions, 62 projects) show that unchanged modules significantly change reported within-project performance. That was studied at file/class level only. **No method-level CVDP study found so far de-duplicates or separates unchanged methods.**
5. **Representation work at method level is thin.** Examples are method-call-network embeddings ([Yang et al. 2023](https://doi.org/10.1109/access.2023.3239266)) and a PDG-guided Transformer ([BiPDG-DP, Lin et al. 2026](https://doi.org/10.1002/smr.70115)). The latter uses control and data dependencies, which makes it the closest to our Joern CFG/DDG. Its evaluation protocol is unknown (closed access).
6. **Aggregation matters if method results are reported at file level.** Summing method metrics to file level hurts models ([Zhang et al. 2016](https://doi.org/10.1109/tse.2016.2599161)).

## Datasets
- **ELFF** ([Shippey et al. 2016](https://doi.org/10.1145/2961111.2962620)): 138 method/class datasets from 23 Java systems.
- **Unified Bug Dataset** ([Ferenc et al. 2020](https://doi.org/10.1007/s11219-020-09515-0)): Java; Chowdhury et al. compare against Ferenc et al.'s results.
- **Chowdhury et al. 2024**: 774,051 methods from 49 projects.
- An anonymous 2026 replication package, *Method-Level Bug Prediction: How Far Are We?* ([Zenodo](https://doi.org/10.5281/zenodo.20986662)), covers about 99 Java projects, with code, change and developer metrics plus code embeddings. The paper itself is unpublished or under review.

## Implications for this project
- The literature supports our planned design: forward-in-time release splits; labels as known at release time, with a check for dormant bugs; a separate report on new and changed methods; and noise-aware labels, e.g. excluding or flagging bug fixes that touch many methods.
- Python (Django) method-level CVDP and graph features evaluated under this protocol appear to be open.

## Next steps
- Read in full (PDFs needed or open copies):
  - Pascarella 2020
  - Chowdhury 2024 (author PDF on cs.ubc.ca)
  - Mo et al. 2021 ([IST](https://doi.org/10.1016/j.infsof.2021.106794)), whose abstract was missing
  - Amasaki 2020
  - Falessi 2021
  - Liu 2024
  - BiPDG-DP
- Extract for each paper: split type, label source, deduplication, metrics, and results.
