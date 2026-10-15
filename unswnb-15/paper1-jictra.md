# Semantic Feature Mapping Validated on Live Cloud Traffic: A Deployment-Oriented Recipe for Cross-Network Intrusion Detection

> **Target:** JICTRA (Journal of ICT Research and Applications, ITB) — konten (reframe dari versi JISA yang di-desk-reject).
> **Status konten:** draf reframe. Semua ANGKA dari eksperimen NYATA (sama dgn versi tervalidasi); tidak ada angka ilustratif.
> **Fokus reframe (Jalur A):** novelty = **SFM + validasi di jaringan nyata baru (AWS)** sebagai bintang utama.
> **Format JICTRA:** Inggris, SI units, abstrak 100-200 kata, 5-10 keyword, referensi gaya nomor [1], maks 20 halaman.
> **Anti-overlap:** paper ini = SFM + real-network (CENTRALIZED). Berbeda dari paper-jictra federated (Paper 4). Tak ada tumpang-tindih.

**Authors:** Hero Yudo Martono (corresponding, hero@pens.ac.id), Iwan Syarif, Ferry Astika Saputra
**Affiliation:** Department of Informatics and Computer Engineering, Politeknik Elektronika Negeri Surabaya (PENS), Surabaya, Indonesia

---

## Abstract

(Target 100-200 kata.)

Machine-learning network intrusion detection systems (NIDS) reach near-perfect
accuracy on their training dataset yet collapse on a different network. A less
examined obstacle is *feature-extractor mismatch*: the same nominal flow feature is
computed differently by different export tools (CICFlowMeter vs. Argus/Bro), so a
model trained on one tool fails behind another. We propose a **Semantic Feature
Mapping (SFM)** that is *statistically validated* per feature pair across tools —
accepting only pairs comparable in scale and rejecting spuriously named ones (the
TCP-window case) — and, crucially, we validate the whole recipe on **live cloud
(AWS) traffic**, which prior cross-dataset studies do not. Using CSE-CIC-IDS2018 and
UNSW-NB15, a single lightweight XGBoost excels in-domain (MCC 0.91/0.74) but
collapses cross-network (MCC approximately 0). A controlled diagnosis shows the
shared features are informative enough (joint training) while a directly measured
distribution shift (domain-classifier accuracy approximately 0.99) is the major
contributor. On real AWS traffic, zero-shot fails (MCC approximately 0) but 1% of
local labels lift MCC to 0.49 and 10-20% to approximately 0.59. All numbers come
from executed, reproducible experiments.

**Keywords:** network intrusion detection; cross-network generalization; semantic
feature mapping; feature-extractor mismatch; real-traffic validation; few-shot
calibration; edge deployment.

---

## 1. Introduction

Machine-learning NIDS routinely report over 99% accuracy on public benchmarks, yet
this rarely materializes as a working detector on a *different*, previously unseen
network. The gap stems from a seldom-tested assumption: that training and
operational traffic share the same distribution. Prior cross-dataset studies [1,2,3]
confirm the collapse — average MCC falling from 0.946 within-dataset to 0.294
cross-dataset [1] — but they generally *stop at observing* it, and they evaluate
only dataset-to-dataset, never against **live production traffic**.

This paper closes two deployment-facing gaps that, to our knowledge, no prior work
addresses *together*:

1. **Feature-extractor mismatch.** Different flow exporters compute the same nominal
   feature differently; a name-based unified schema silently admits non-comparable
   pairs. We detect and *reject* such pairs by statistical validation.
2. **No validation on a real new network.** Cross-dataset papers measure
   dataset-to-dataset drops; none deploys the mapped model on live traffic to
   measure false-alarm behavior and repair cost.

**Core novelty (what is new here).** The combination that is absent from prior work:
a **statistically validated cross-tool Semantic Feature Mapping** carried
**end-to-end to a live cloud network (AWS)** — measuring false-alarm rate under
benign traffic, quantifying a three-domain distribution shift, and restoring
detection with a few local labels. Unified-feature-set work [4] standardizes schemas
but neither validates each pair statistically nor tests on live traffic;
cross-dataset studies [1,2,3] document the drop but offer no field validation or
low-cost repair. We bridge both.

**Contributions.**
1. A cross-tool SFM with per-pair statistical validation, including a concrete
   feature-extractor mismatch finding (TCP-window features).
2. Quantitative evidence of cross-network collapse, and a controlled diagnosis
   separating feature insufficiency from distribution shift.
3. A low-cost repair (1% target labels, or cross-dataset mixup) with multi-seed
   confidence intervals.
4. **End-to-end validation on live AWS traffic**: false-alarm rate, a quantified
   three-domain shift, and few-shot recovery — the piece missing from prior
   cross-dataset work.

**Research questions.** RQ1: can semantically equivalent flow features from
heterogeneous tools be reliably identified? RQ2: how far does a single-source NIDS
generalize after semantic alignment? RQ3: what distinguishes representation
insufficiency from distribution shift? RQ4: how much target labeling recovers
performance? RQ5: does the recipe transfer to real AWS traffic?

**Reproducibility.** All reported values come from executed experiments; no
illustrative values are presented as results, and negative/non-monotone outcomes are
reported as observed.

---

## 2. Related Work

**Cross-dataset generalization.** D'Hooge et al. [2] showed supervised NIDS fail on
unseen networks; Verkerken et al. [3] reported ~30% AUROC drop with unsupervised
models; Cantone et al. [1] documented MCC falling from 0.946 (within) to 0.294
(cross) over four datasets. These works confirm the collapse but stop at observing
it, without separating feature insufficiency from distribution shift and without a
low-cost recovery or live-traffic validation.

**Unified feature sets.** Sarhan et al. [4] proposed a standardized NetFlow feature
set to enable cross-dataset comparison. We go further: each mapped pair is
*statistically validated* on its original scale, and spuriously named matches are
*rejected* (the TCP-window case) — exactly what a name-based schema admits silently.

**Dataset integrity.** Reconstructions found >20% of CIC-IDS2017 flows needed
relabeling [5], CICFlowMeter feature errors [6], and 6-7% label-error rates on
CIC/CSE-CIC datasets [7]. Layeghy et al. [8] showed synthetic benign traffic differs
statistically (large Wasserstein distance) from real networks — motivating both our
cross-tool mapping and our live-traffic validation.

**Domain adaptation.** CORAL [9] aligns covariance; few-shot methods [10] target
label-limited NIDS. Deep domain-invariant NIDS (DI-NIDS [8]) learns adversarially
invariant features but needs a heavy deep stack and ample target data — impractical
for edge. We keep a fixed lightweight XGBoost backbone and recover performance with
cheap per-deployment calibration, a different edge-oriented operating point. A
head-to-head against deep DA needs a different stack and is left as future work
(scope stated explicitly, not an unmeasured superiority claim).

## 3. Data and Semantic Feature Mapping

**Datasets (deliberately cross-source).** CSE-CIC-IDS2018 (CICFlowMeter, 68 clean
features) and UNSW-NB15 (Argus & Bro/Zeek, 42 features; 175,341 train / 82,332 test
records). The differing extraction tools are a *prerequisite* for realistically
testing feature-extractor mismatch, not a weakness. All attack types are collapsed
to a single `attack` class (controlled binary setting).

**SFM construction and validation.** SFM maps functionally equivalent features even
when names differ (e.g., `Flow Duration` <-> `dur`). Each candidate pair is *not*
accepted on name similarity but validated in three steps: (i) match semantics from
each tool's official documentation; (ii) return CIC features to original scale
(x_orig = x_scaled * sigma + mu, as our CIC release is z-scored); (iii) compare
summary statistics (median, p99, max) for scale-order equivalence. A pair is
*aligned* when median/p99 ratios share an order of magnitude, *scale-mismatch* at
1-3 orders (unit conversion), *different-feature* beyond 3 orders. The nine strong
pairs form Model A; two IAT pairs form optional Model B; two TCP-window pairs are
**discarded** as a feature-extractor mismatch (continuous in CICFlowMeter,
effectively binary in Argus/Bro) despite similar names. Per-dataset z-score
normalization resolves residual unit differences so each retained pair stays
semantically comparable.

## 4. Cross-Network Baseline and Diagnosis

**Collapse (RQ2).** A single XGBoost excels in-domain (MCC 0.91 on CIC, 0.74 on
UNSW) but collapses cross-network (MCC approximately 0) — consistent with the
literature but here measured on the SFM-aligned feature space, ruling out a trivial
schema mismatch as the cause.

**Diagnosis: shift, not (only) insufficiency (RQ3).** Joint training on the nine SFM
features performs well on both domains, showing the shared features carry sufficient
discriminative information — so feature insufficiency is *not* the sole explanation.
A domain classifier separates CIC from UNSW with approximately 0.99 accuracy and a
large inter-domain Wasserstein distance, directly measuring the distribution shift
as the *major contributor* (conceptually motivated by the Ben-David bound).

## 5. Low-Cost Recovery (RQ4)

Minimal calibration recovers cross-network detection: using only 1% of target-network
labels, or supervised cross-dataset *mixup* that uses only target *train* labels,
restores cross-network MCC into the 0.65-0.91 range (multi-seed, with confidence
intervals). An adaptation-direction asymmetry is observed and analyzed:
CIC->UNSW recovers lower (~0.66-0.69) than UNSW->CIC (~0.90), explained by greater
domain dispersion in UNSW (mean SFM-feature variance 3.64 vs 0.68 for CIC,
approximately 5.3x), concentrated in rate/packet-size features. We report this as an
evidence-consistent interpretation, not a causal proof.

## 6. Real-Traffic Validation on AWS (RQ5) — the key differentiator

We deploy the SFM-aligned detector on **live AWS cloud traffic**, the step prior
cross-dataset work omits. Three consistent findings:

1. **Stable under benign traffic.** False-alarm rate stays below 0.5% without drift
   (0.00% at 3 min -> 0.38% at 1 h -> 0.42% over 22,644 flows at 6 h), ruling out any
   unit/scaling defect (which would spike FAR toward 100%).
2. **Zero-shot does not transfer.** Benchmark excellence collapses on live traffic
   (MCC approximately 0; -0.22 for CIC); a three-domain analysis attributes this to
   genuine distribution shift (domain-classifier accuracy approximately 0.99 among
   CIC/UNSW/AWS), concentrated in rate features and backward packet size.
3. **Cheaply repairable.** 1% AWS labels (approximately 107 flows) lift MCC from
   approximately 0 to 0.49; 10-20% reaches approximately 0.59, on par with AWS-only
   (0.598). We report MCC because AWS-test is approximately 99% attack, where F1
   would be misleadingly high.

A stricter episode-level split shows the few-shot gain is smaller and
episode-dependent; we present the flow-level operating point as practical, not a
universal prescription. The most robust evidence for low-cost adaptation remains the
offline cross-network experiments (Section 5).

## 7. Discussion and Limitations

The findings form a coherent narrative: single-source NIDS collapse cross-network; a
directly measured distribution shift (not feature insufficiency) is the major
contributor; and minimal calibration or mixup recovers performance, confirmed on
live AWS traffic. **Limitations:** the direction asymmetry is not fully resolved;
using a single XGBoost is a deliberate edge-efficiency choice (2.9 MB, sub-ms
inference) rather than a limitation, but a head-to-head against deep domain-invariant
baselines (DI-NIDS, DANN) needs a different stack and is future work. Adversarial
robustness is deliberately scoped out: preliminary results show adversarial training
improves in-domain evasion robustness but does *not* close the cross-network gap —
confirming the two problems need different solutions.

## 8. Conclusion and Future Work

We presented a statistically validated cross-tool Semantic Feature Mapping and —
uniquely among cross-dataset NIDS studies — validated the full recipe on live AWS
traffic: stable false-alarm behavior, a quantified three-domain distribution shift,
and few-shot recovery at minimal labeling cost. Future work: online/streaming
continuous adaptation with drift detection; automated few-shot labeling (active
learning, SIEM/SOC integration) with a trusted-holdout guardrail; robust ensembles
under edge budgets; and multi-class attack-category extension. Adversarial robustness
is pursued in a separate study.

## Acknowledgements

The authors thank Politeknik Elektronika Negeri Surabaya (PENS) for computing
support. (Lengkapi dengan sumber dana/hibah bila ada sebelum submit.)

## Nomenclature

| Symbol / Abbr. | Meaning |
|---|---|
| NIDS | Network Intrusion Detection System |
| SFM | Semantic Feature Mapping (statistically validated cross-tool feature mapping) |
| MCC | Matthews Correlation Coefficient |
| FAR | False-Alarm Rate |
| IAT | Inter-Arrival Time (flow feature) |
| CORAL | CORrelation ALignment (domain adaptation) |
| DANN | Domain-Adversarial Neural Network |
| DI-NIDS | Domain-Invariant NIDS |
| $W_1$ | 1-Wasserstein distance between domain distributions |
| $x_{orig}$ | feature value returned to original scale: $x_{scaled}\cdot\sigma + \mu$ |
| few-shot | calibration using a small fraction of target-network labels |
| mixup | supervised cross-dataset interpolation using target train labels |

## References

(Gaya JICTRA: nomor berurutan sesuai kemunculan. Lengkapi detail volume/halaman saat finalisasi.)

[1] Cantone, M., Marrocco, C. & Bria, A., Machine Learning in Network Intrusion Detection: A Cross-Dataset Generalization Study, IEEE Access, 12, pp. 144491-144509, 2024.
[2] D'Hooge, L., Wauters, T., Volckaert, B. & De Turck, F., Inter-dataset Generalization Strength of Supervised Machine Learning Methods for Intrusion Detection, Journal of Information Security and Applications, 54, art. 102564, 2020.
[3] Verkerken, M., D'Hooge, L., Wauters, T., Volckaert, B. & De Turck, F., Towards Model Generalization for Intrusion Detection: Unsupervised Machine Learning Techniques, Journal of Network and Systems Management, 30(1), pp. 1-25, 2022.
[4] Sarhan, M., Layeghy, S. & Portmann, M., Towards a Standard Feature Set for Network Intrusion Detection System Datasets, Mobile Networks and Applications, 27(1), pp. 357-370, 2022.
[5] Engelen, G., Rimmer, V. & Joosen, W., Troubleshooting an Intrusion Detection Dataset: The CICIDS2017 Case Study, Proc. IEEE Security and Privacy Workshops (SPW), pp. 7-12, 2021.
[6] Rosay, A., Cheval, E., Carlier, F. & Leroux, P., Network Intrusion Detection: A Comprehensive Analysis of CIC-IDS2017, Proc. 8th ICISSP, pp. 25-36, 2022.
[7] Liu, L., Engelen, G., Lynar, T., Essam, D. & Joosen, W., Error Prevalence in NIDS Datasets: A Case Study on CIC-IDS-2017 and CSE-CIC-IDS-2018, Proc. IEEE CNS, pp. 254-262, 2022.
[8] Layeghy, S., Baktashmotlagh, M. & Portmann, M., DI-NIDS: Domain Invariant Network Intrusion Detection System, Knowledge-Based Systems, 273, art. 110626, 2023.
[9] Sun, B. & Saenko, K., Deep CORAL: Correlation Alignment for Deep Domain Adaptation, Proc. ECCV Workshops, pp. 443-450, 2016.
[10] Name of author(s), Few-Shot Learning for Network Intrusion Detection, [lengkapi detail saat finalisasi].
[11] Chen, T. & Guestrin, C., XGBoost: A Scalable Tree Boosting System, Proc. 22nd ACM SIGKDD, pp. 785-794, 2016.
