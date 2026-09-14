# Cover Letter — Submission to Journal of Information Security and Applications (JISA)

[Date]

Dear Editor-in-Chief,

We are pleased to submit our manuscript entitled **"Cross-Dataset Generalization
of ML-based Network Intrusion Detection via Semantic Feature Mapping and Few-Shot
Adaptation, Validated on Real Cloud Traffic"** for consideration for publication
in the *Journal of Information Security and Applications*.

Machine-learning-based network intrusion detection systems (NIDS) routinely report
near-perfect accuracy on public benchmarks, yet their ability to generalize to
different networks is rarely evaluated honestly. Our work addresses this gap
directly. Using a deliberately cross-source dataset pair (CSE-CIC-IDS2018 and
UNSW-NB15, extracted with different tools), we make the following contributions:

1. A statistically validated **Semantic Feature Mapping (SFM)** that aligns
   features across extraction tools, including a concrete **feature-extractor
   mismatch** finding on TCP-window features.
2. **Quantitative evidence** that single-source NIDS collapse cross-network
   (MCC near zero), and a **diagnosis** — grounded in the Ben-David
   domain-adaptation bound — that the cause is **distribution shift**, not feature
   insufficiency.
3. **Low-cost solutions**: only 1% of target-network labels, or label-free
   cross-dataset mixup, recover cross-network MCC to the 0.65–0.91 range.
4. **Real cloud-traffic validation on AWS**: a low and stable False Alarm Rate
   (<0.5%) under benign load; a quantified three-domain distribution shift
   (Wasserstein distance and a domain classifier); and restoration of failed
   zero-shot detection via few-shot calibration.

We emphasize a **data-honesty principle**: every number in the manuscript comes
from real, reproducible experiments and is reported as-is, including negative and
non-monotone results.

We believe this work fits the scope of JISA — practical, security-focused machine
learning with rigorous, honest evaluation — and will be of interest to its
readership working on intrusion detection and cross-domain robustness.

This manuscript is original, has not been published previously, and is not under
consideration for publication elsewhere. All authors have approved the manuscript
and agree with its submission. The authors declare no competing interests.

Thank you for considering our submission. We look forward to your response.

Sincerely,

Hero Yudo Martono (corresponding author)
Iwan Syarif
Ferry Astika Saputra
Department of Informatics and Computer Engineering,
Politeknik Elektronika Negeri Surabaya (PENS), Surabaya, Indonesia
Email: hero@pens.ac.id
