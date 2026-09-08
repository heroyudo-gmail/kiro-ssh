# PANDUAN COPY-PASTE KE WORD 365 (Template JETS-ITB)

> **Cara pakai file ini:**
> 1. Teks paragraf biasa → blok, copy, paste ke Word. Setelah paste, pilih Style JETS yang sesuai (Title / Author / Address / Abstract / Keyword / Heading 1 / Text / Figure / Table / Reference).
> 2. **RUMUS** → di Word tekan **Alt + =** (menyisipkan equation), pastikan tab *Equation* di-set mode **"LaTeX"** (bukan Unicode), lalu **paste kode di dalam blok `LATEX:`**. Tekan spasi/Enter → rumus otomatis jadi cantik.
>    - Inline (di tengah kalimat): sisipkan equation kecil di posisi `⟨rumus N⟩`.
>    - Display (baris sendiri, bernomor): buat paragraf Equation, sisipkan, dan beri nomor (1), (2), ...
> 3. **Tabel** → copy blok tabel Markdown, paste ke Word (Word mengubahnya jadi tabel), lalu terapkan Style *Table* pada caption.
> 4. **Gambar** → sisipkan file dari folder `nids-figures/` sesuai penanda, caption pakai Style *Figure*.
>
> Semua sitasi sudah dalam format APA (Author, Year). Tidak ada perintah LaTeX yang tersisa di badan teks.

---

## [STYLE: Title]

Strengthening NIDS Resilience through XGBoost Gain-based Feature Reduction and Adversarial Training against Saliency Map Evasion Attacks

## [STYLE: Author]

Hero Yudo Martono1,*, Iwan Syarif1, Ferry Astika Saputra1

## [STYLE: Address]

1Department of Informatics Engineering, Politeknik Elektronika Negeri Surabaya, Surabaya, Indonesia

Email: hero@pens.ac.id; iwanarif@pens.ac.id; ferryas@pens.ac.id

*Corresponding author: hero@pens.ac.id

## [STYLE: Abstract]

**Abstract.** Machine learning-based Network Intrusion Detection Systems (NIDS) often perform well only under clean laboratory traffic and remain vulnerable to deliberate manipulation during the inference phase. At the same time, feature dimensionality reduction is needed for system efficiency, yet it may enlarge the attack surface. This study evaluates and strengthens the robustness of an XGBoost model whose features have been optimized using the Gain-based Importance method. The CSE-CIC-IDS2018 dataset, comprising 15.7 million network traffic samples across seven attack categories, is used. The proposed methodology has three main stages: (1) feature reduction from 68 to 10 features using the XGBoost Gain metric; (2) simulation of Saliency Map-based evasion attacks with epsilon variations (ε ∈ {0.01, 0.05, 0.1}); and (3) implementation of Adversarial Training as a defense mechanism. Because XGBoost is a non-differentiable tree-based model, input sensitivity is approximated numerically through finite differences over the model's probability outputs. Experimental results show that the baseline model suffers a drastic drop in the Matthews Correlation Coefficient (MCC) from 0.9351 to 0.0184 (a 98% decline) under evasion attack (ε = 0.1). The model hardened through Adversarial Training recovers the MCC to 0.9953 on adversarial data while preserving detection integrity on normal traffic (MCC = 0.9347, only 0.04% below the baseline). A Robustness Ablation Study over four feature configurations (Full/68, Top-15, Top-10, Top-5) confirms that the Top-10 configuration is the optimal sweet spot, balancing computational efficiency and resilience. Furthermore, validation on real network traffic in an AWS cloud environment shows that the robustness pattern remains consistent with the offline results—the baseline degrades under evasion while the robust model holds—demonstrating that the effectiveness of Adversarial Training is not confined to benchmark datasets.

## [STYLE: Keyword]

*Keywords:* adversarial training; CSE-CIC-IDS2018; evasion attack; feature reduction; network intrusion detection system; saliency map; XGBoost.

---

## [STYLE: Heading 1] Introduction

The rapid growth of network traffic and the increasing sophistication of cyberattacks have made the Network Intrusion Detection System (NIDS) an essential defensive component. The development of machine learning-based NIDS depends heavily on the availability of high-quality public benchmark datasets. Several datasets have become de facto standards for evaluating detection models, ranging from KDD Cup 99 (Tavallaee et al., 2009), UNSW-NB15 (Moustafa & Slay, 2015), CIC-IDS/CSE-CIC-IDS (Sharafaldin et al., 2018), Bot-IoT (Koroniotis et al., 2019), and TON_IoT (Alsaedi et al., 2020), to CICIoT2023 (Neto et al., 2023). Various surveys confirm that machine learning and deep learning methods have become mainstream in modern NIDS research (Al-Ajlan & Ykhlef, 2024; Dunmore et al., 2023; Huang et al., 2022).

One classic challenge in NIDS datasets is the extreme class imbalance between normal traffic and attacks. To address this, Generative Adversarial Networks (GAN), introduced by Goodfellow et al. (2014), are widely used for data synthesis and balancing. Several generative architecture variants have been developed as foundations, including Conditional GAN (Mirza & Osindero, 2014), Wasserstein GAN (Arjovsky et al., 2017), Deep Convolutional GAN (Radford et al., 2015), Self-Attention GAN (Zhang et al., 2019), Auxiliary Classifier GAN (Odena et al., 2017), and Conditional Tabular GAN (Xu et al., 2019).

At the NIDS application level, several studies combine generative models with traditional machine learning classifiers such as Random Forest, Decision Tree, SVM, and XGBoost to improve detection (Mari et al., 2023; Kumar & Sinha, 2023; Alabsi et al., 2023; Babu & Rao, 2023; Rahman et al., 2024; Yang et al., 2025). Another group of studies employs deep learning architectures such as CNN, DNN, LSTM, and GRU as downstream classifiers after data generation (de Araujo-Filho et al., 2023; Yang et al., 2023; Rahman et al., 2023; Ding et al., 2024; Park et al., 2023; Xu et al., 2025b). These approaches have proven capable of improving detection performance under clean laboratory traffic conditions.

However, the same generative capability can be exploited as an offensive weapon. Several studies show that GANs can generate adversarial samples that deceive NIDS models through evasion attacks, on both machine learning-based and deep learning-based classifiers (Zhao et al., 2021; Aldhaheri & Alhuzali, 2023; Wang et al., 2024a). Such attacks are even effective under low-data regimes (Randhawa et al., 2023), in machine learning-based evasion schemes (Xu et al., 2025a), in IoT environments (Mbow et al., 2024), and in the malware domain (Trung et al., 2024; Devadiga et al., 2023). These findings reveal a fundamental security gap: a model that performs excellently on clean data can collapse drastically when its input features are subtly and deliberately manipulated during the inference phase.

To close this gap, defense mechanisms such as Adversarial Training and diffusion-based adversarial purification have been proposed to strengthen the model's decision boundary (Merzouk et al., 2025). Generative approaches have also evolved toward ensemble/hybrid methods (Riaz et al., 2025; Alshehri et al., 2025) as well as privacy-preserving and distributed architectures such as differentially private GAN (Hassan et al., 2023), distributed GAN (Jiang et al., 2023), and federated learning (Wang et al., 2024b). Meanwhile, the demand for computational efficiency drives the adoption of feature dimensionality reduction so that models can be deployed on resource-constrained devices. Ironically, aggressive feature reduction may enlarge the attack surface: by concentrating decisions on a few features, the gradient sensitivity of those features increases, making the model easier to exploit. This tension between efficiency and robustness has not been systematically explored in the literature.

In addition, a review of generative and adversarial NIDS literature reveals two important gaps. *First*, the issue of cross-dataset generalization: recent studies prove that a model excelling on one dataset suffers a drastic performance drop when tested on a dataset from a different network (Cantone et al., 2024; Aceto et al., 2024), indicating that benchmark performance does not necessarily reflect generalization capability. *Second*, and most critically, almost all such studies stop at offline evaluation using static datasets—very few validate model robustness on real network traffic in an actual deployment environment. As a result, claims of robustness against evasion remain largely untested under realistic operational conditions, where differences in feature extraction tools and network characteristics can significantly affect performance. The inherent challenges of training generative models, such as mode collapse and convergence instability, further complicate the reproducibility of results in real environments (Educative, 2025).

Based on these gaps, this study proposes an approach that integrates XGBoost Gain-based feature reduction with Saliency Map-based Adversarial Training, then validates it not only offline on the CSE-CIC-IDS2018 dataset but also on real traffic in an AWS cloud environment. The main contributions of this study are: (1) quantifying the security gap caused by evasion attacks on a feature-reduced tree-based model; (2) demonstrating the effectiveness of Adversarial Training in restoring model robustness without sacrificing accuracy on normal traffic; (3) determining the feature-dimension sweet spot through a Robustness Ablation Study; and (4) validating the consistency of model robustness on real network traffic—an aspect rarely addressed in adversarial NIDS literature.

---

## [STYLE: Heading 1] Materials and Methods

The methodology of this study is systematically designed to evaluate and improve the robustness of an NIDS against evasion attacks. It comprises six main stages: dataset preprocessing, XGBoost Gain-based feature optimization, adversarial sample generation, adversarial training, robustness ablation study, and model evaluation, as illustrated in Figure 1.

**[SISIPKAN GAMBAR: nids-figures/fig_flowchart.png — lebar ~90%]**
**[STYLE: Figure]** Figure 1. research methodology flowchart

### [STYLE: Heading 2] Dataset and Data Preprocessing

This study uses the CSE-CIC-IDS2018 dataset provided by the Canadian Institute for Cybersecurity (CIC) (Sharafaldin et al., 2018). This dataset was selected because it offers broad attack coverage reflecting modern network scenarios, consisting of ten CSV files with a total size of approximately 6.7 GB. It covers benign traffic profiles and seven main attack categories: Brute-Force (SSH/FTP), DoS, DDoS, Web Attacks, Infiltration, and Botnet.

Given the massive data volume—particularly the 20 February traffic file that reaches 3.8 GB—this study applies a 10% stratified sampling strategy (Kohavi, 1995) to keep the original attack-label distribution representative in the working subset. The sampling produced 1,570,577 samples out of a total population of 15,705,786 samples. Data cleaning was performed systematically through several crucial stages to ensure model integrity:

1. **Handling of Singular Values:** All samples containing missing values (NaN) were permanently removed. Infinity values in numeric features were imputed using the finite maximum of the corresponding column to prevent mathematical failure during model training.
2. **Elimination of Biased Features:** Flow-identifier features such as Flow ID, Source/Destination IP, Source/Destination Port, and Protocol were dropped because they do not contribute to attack-pattern generalization and risk introducing training bias. The Timestamp column was also removed to ensure the model learns statistical traffic characteristics rather than temporal ordering.
3. **Low-Variance Reduction:** Features with zero variance (constant values) were scanned and discarded because they carry no discriminative information for the classifier.
4. **Normalization and Encoding:** Qualitative attack labels were converted to numeric form using LabelEncoder, and numeric features were normalized using StandardScaler/MinMax scaling from scikit-learn (Pedregosa et al., 2011) to accelerate XGBoost convergence.

Starting from 83 initial technical features, this process yielded a clean data matrix of 68 independent numeric features and one target label, ready for the Gain-based feature selection stage. The distribution of samples before and after preprocessing is summarized in Table 1.

**[STYLE: Table]** Table 1. Sample distribution of CSE-CIC-IDS2018 before and after preprocessing

| Category | Original | 10% Subset | Description |
|---|---|---|---|
| Benign | 13,484,708 | 1,348,470 | Normal traffic |
| DDoS / DoS | 1,391,082 | 139,108 | Volumetric flooding |
| Brute-Force | 380,943 | 38,094 | SSH/FTP login |
| Botnet | 286,191 | 28,619 | C2 command |
| Web Attacks | 928 | 93 | SQLi / XSS |
| Infiltration | 161,934 | 16,193 | Internal penetration |
| **Total** | **15,705,786** | **1,570,577** | 83 features (before cleaning) |

### [STYLE: Heading 2] XGBoost Gain-based Feature Optimization

This stage aims to achieve high computational efficiency without sacrificing information critical for anomaly detection. Given the large feature dimensionality (68 columns after preprocessing), Gain-based feature reduction (Chen & Guestrin, 2016) was performed through the following steps: (1) training a baseline XGBoost model on all 68 features with an 80:20 train–test split; (2) extracting the Gain metric, which represents the average contribution of a feature in reducing the loss function at each split of the decision trees; (3) ranking features from highest to lowest Gain; (4) validating via an ablation study by retraining the model on several feature subsets—Full (68), Top-20, Top-15, and Top-10; and (5) selecting the optimal configuration based on a balance of classification performance (F1-score and MCC), model-artifact size, and inference latency. The configuration meeting these three aspects in a balanced manner is designated as the sweet spot.

### [STYLE: Heading 2] Adversarial Sample Generation (Evasion Attack)

This stage simulates an attacker attempting to deceive the NIDS through an evasion attack. Adversarial sample generation employs a gradient-based technique (Szegedy et al., 2014) to identify model vulnerabilities and apply subtle perturbations to critical features.

#### [STYLE: Heading 3] Mathematical Foundation of the Saliency Map

The Saliency Map approach relies on the notion of output sensitivity to input changes introduced by Simonyan et al. (2014). Let the NIDS be a decision function ⟨rumus A⟩ with parameters ⟨rumus B⟩, where ⟨rumus C⟩ is the network-traffic feature vector and y the ground-truth label. The sensitivity of the loss function ⟨rumus D⟩ to changes in each feature is measured by the gradient vector:

> **PERSAMAAN (1) — display, beri nomor (1)**
> `LATEX:` `\nabla_{\mathbf{x}} L(\theta, \mathbf{x}, y) = \left[ \frac{\partial L}{\partial x_1}, \frac{\partial L}{\partial x_2}, \dots, \frac{\partial L}{\partial x_d} \right]^T`

The Saliency Map score ⟨rumus E⟩ for feature i is the absolute value of the partial derivative of the loss with respect to that feature:

> **PERSAMAAN (2) — display, beri nomor (2)**
> `LATEX:` `S(\mathbf{x}, i) = \left| \frac{\partial L(\theta, \mathbf{x}, y)}{\partial x_i} \right|`

A high ⟨rumus E⟩ indicates that a minimal change to that feature has the most significant effect on the model's decision.

#### [STYLE: Heading 3] Gradient Approximation for a Non-Differentiable Model

It must be emphasized that XGBoost is a tree-based model whose decision boundary is a step function, and is therefore non-differentiable: the partial derivative ⟨rumus F⟩ is zero almost everywhere and undefined exactly at the split thresholds. Consequently, the gradient vector in Eq. (1) and Eq. (2) is **not computed analytically**; instead, it is approximated numerically using the central finite-difference method over the cross-entropy loss constructed from the model's output probabilities (predict_proba under the multi:softprob objective). This probability function is continuous with respect to input perturbations, so the gradient approximation is well defined. For each feature i, the saliency score is computed as:

> **PERSAMAAN (3) — display, beri nomor (3)**
> `LATEX:` `S(\mathbf{x}, i) = \left| \frac{L(\theta, \mathbf{x} + h\mathbf{e}_i, y) - L(\theta, \mathbf{x} - h\mathbf{e}_i, y)}{2h} \right|`

where ⟨rumus G⟩ is the unit basis vector along dimension i, h = 0.01 is the perturbation step size, and L(·) is the cross-entropy ⟨rumus H⟩ with ⟨rumus I⟩ the model's probability for class c. This approach is conceptually equivalent to a score-based (zeroth-order) attack that requires only access to the model's output probability scores, not its internal gradients. Thus, the vulnerability computation remains mathematically valid even for a non-differentiable tree-based model.

#### [STYLE: Heading 3] Epsilon Perturbation Formulation

Once the most sensitive features are identified, the adversarial sample ⟨rumus J⟩ is generated by adding a perturbation vector ⟨rumus K⟩ to the original sample x, bounded by the L∞ norm ε:

> **PERSAMAAN (4) — display, beri nomor (4)**
> `LATEX:` `\mathbf{x}_{adv} = \mathbf{x} + \boldsymbol{\delta}, \quad \text{with } \|\boldsymbol{\delta}\|_\infty \le \epsilon`

Following the Fast Gradient Sign Method (FGSM) introduced by Goodfellow et al. (2015), and substituting the approximated saliency for the analytic gradient, the adversarial sample is formed as:

> **PERSAMAAN (5) — display, beri nomor (5)**
> `LATEX:` `\mathbf{x}_{adv} = \mathbf{x} + \epsilon \cdot \text{sign}\left( S(\mathbf{x}) \right)`

On the feature-reduced model, the decision is concentrated on a very limited set of dimensions; the fewer features used, the larger the approximated saliency ⟨rumus E⟩ on those features tends to be, since the discriminative load concentrates on a narrower space. This mathematical weakness is exploited through the Saliency Map-based attack to produce the adversarial set ⟨rumus L⟩.

### [STYLE: Heading 2] Modeling and Adversarial Training

The NIDS model is built using XGBoost, optimized on the reduced feature subset from Gain-based selection. The objective function is multi:softprob to classify traffic into benign and various attack classes. Key hyperparameters are a maximum tree depth (max_depth) of 8, a learning rate of 0.1, 200 estimators (n_estimators), and subsample and colsample_bytree of 0.8 each to mitigate overfitting.

Adversarial Training is formulated as a Min-Max (saddle-point) optimization following the robustness framework of Madry et al. (2018). Intuitively, it minimizes the worst-case loss induced by attacker perturbations:

> **PERSAMAAN (6) — display, beri nomor (6)**
> `LATEX:` `\min_{\theta} \mathbb{E}_{(\mathbf{x}, y) \sim \mathcal{D}} \left[ \max_{\|\boldsymbol{\delta}\|_\infty \le \epsilon} L(\theta, \mathbf{x} + \boldsymbol{\delta}, y) \right]`

The practical implementation augments the training set: from the clean training data ⟨rumus M⟩, an adversarial subset ⟨rumus N⟩ is generated using the Saliency Map method, and a new training set ⟨rumus O⟩ is formed by combining clean and adversarial samples at an 80:20 ratio:

> **PERSAMAAN (7) — display, beri nomor (7)**
> `LATEX:` `\mathcal{D}_{robust} = \mathcal{D}_{clean} \cup \mathcal{D}_{adv}`

Retraining XGBoost on ⟨rumus O⟩ adjusts the split thresholds of the decision trees so that regions around the original samples—previously vulnerable to an ε-shift—are now covered within the correct decision region, improving robustness without sacrificing accuracy on normal traffic. The complete adversarial training workflow is illustrated in Figure 2.

**[SISIPKAN GAMBAR: nids-figures/fig_advtrain.png — lebar ~95%]**
**[STYLE: Figure]** Figure 2. systematic adversarial training workflow

### [STYLE: Heading 2] Robustness Ablation Study

The Robustness Ablation Study evaluates the trade-off between feature-dimension efficiency and the model's security against evasion attacks. Testing isolates the feature variable into four hierarchical levels based on the XGBoost Gain ranking, as detailed in Table 2.

**[STYLE: Table]** Table 2. Feature configurations for the Robustness Ablation Study

| Configuration | Count | Description |
|---|---|---|
| C1 (Full) | 68 | Full-dimension comparison baseline |
| C2 (Top-15) | 15 | Moderately informative feature subset |
| C3 (Top-10) | 10 | Sweet-spot hypothesis (compact & precise) |
| C4 (Top-5) | 5 | Extreme compression (maximum efficiency) |

> Catatan: C1..C4 idealnya ditulis C dengan subscript 1..4. Untuk konsistensi Word, bisa ketik "C₁, C₂, C₃, C₄" (subscript) atau biarkan C1..C4.

Each configuration ⟨rumus P⟩ (k ∈ {1,2,3,4}) is trained with two approaches—baseline (no defense) and robust (with Adversarial Training)—then tested with evasion samples ⟨rumus J⟩ parameterized by ε. The goal is to identify the sweet spot ⟨rumus Q⟩ that maximizes a combined utility function:

> **PERSAMAAN (8) — display, beri nomor (8)**
> `LATEX:` `\hat{C} = \arg\max_{C_k} \left( \text{MCC}(C_k, \mathbf{x}_{adv}) - \lambda \cdot |C_k| \right)`

where MCC(Ck, xadv) measures detection robustness on manipulated traffic, |Ck| is the number of features, and λ is a dimension-efficiency penalty weight.

### [STYLE: Heading 2] Model Evaluation and Performance Comparison

Evaluation uses a 2×2 cross-testing scenario comparing the standard (baseline) model against the hardened (robust) model on both clean and manipulated traffic, as summarized in Table 3.

**[STYLE: Table]** Table 3. Evaluation scenario matrix for the NIDS model (2×2)

| Scenario | Model | Train | Test | Evaluation objective |
|---|---|---|---|---|
| S1 | Baseline | Clean | Clean | Initial performance under normal conditions |
| S2 | Baseline | Clean | Manipulated | Measure evasion vulnerability (security gap) |
| S3 | Robust | Robust | Clean | Verify accuracy is preserved on normal traffic |
| S4 | Robust | Robust | Manipulated | Prove improved resilience against attacks |

Because CSE-CIC-IDS2018 exhibits extreme class imbalance, the Matthews Correlation Coefficient (MCC) (Matthews, 1975) is chosen as the primary metric. Unlike conventional accuracy, which can be misleading on imbalanced data, MCC accounts for all four quadrants of the confusion matrix proportionally, making it more reliable for imbalanced classification (Chicco & Jurman, 2020):

> **PERSAMAAN (9) — display, beri nomor (9)**
> `LATEX:` `\text{MCC} = \frac{(TP \times TN) - (FP \times FN)}{\sqrt{(TP + FP)(TP + FN)(TN + FP)(TN + FN)}}`

The MCC ranges over [−1, +1], where +1 denotes perfect prediction, 0 random guessing, and −1 total disagreement. As supporting metrics, Precision and F1-score are also reported:

> **PERSAMAAN (10) — display, beri nomor (10)**
> `LATEX:` `\text{Precision} = \frac{TP}{TP + FP}, \qquad F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}`

where Recall = TP/(TP + FN). A performance drop in S2 reveals the security gap, whereas recovery of MCC and F1-score in S4 demonstrates the success of model hardening through Adversarial Training.

---

### CATATAN RUMUS INLINE (⟨rumus A⟩ … ⟨rumus Q⟩)
> Untuk setiap penanda ⟨rumus X⟩ di badan teks, di Word tekan **Alt + =** pada posisi itu, set mode **LaTeX**, lalu paste kode berikut:
>
> - A: `f(\mathbf{x})`
> - B: `\theta`
> - C: `\mathbf{x} = [x_1, x_2, \dots, x_d]^T \in \mathbb{R}^d`
> - D: `L(\theta, \mathbf{x}, y)`
> - E: `S(\mathbf{x}, i)`
> - F: `\partial L / \partial x_i`
> - G: `\mathbf{e}_i`
> - H: `L = -\sum_{c} y_c \log p_c(\mathbf{x})`
> - I: `p_c(\mathbf{x})`
> - J: `\mathbf{x}_{adv}`
> - K: `\boldsymbol{\delta}`
> - L: `\mathbf{x}_{adv}`
> - M: `\mathcal{D}_{clean}`
> - N: `\mathcal{D}_{adv}`
> - O: `\mathcal{D}_{robust}`
> - P: `C_k`
> - Q: `\hat{C}`

---

## [STYLE: Heading 1] Results

### [STYLE: Heading 2] Preprocessing Results and Subset Description

The preprocessing transformed the massive raw CSE-CIC-IDS2018 dataset (≈6.7 GB) into a clean, proportionally balanced subset. The 10% stratified sampling preserved the original attack-category ratios. During data cleaning, 2,861 samples containing undefined values (NaN/Missing) were eliminated, and Infinity values in quantitative variables such as Flow Bytes/s were imputed with the finite maximum of the respective column. Removing six flow-identifier features (Flow ID, Source/Destination IP, Ports, Protocol) and the Timestamp variable prevented overfitting to specific network topology, while a variance scan discarded eight constant (zero-variance) features. From 83 initial technical features, preprocessing produced a clean data matrix of 68 independent numeric features plus one target label.

### [STYLE: Heading 2] XGBoost Gain Ranking and Sensitive-Feature Exploration

Training the baseline model on all 68 features showed that the Gain contribution is not evenly distributed but concentrated on a few dominant attributes. Table 4 lists the top-20 features by Gain score. Cumulatively, the top-10 features account for more than 85% of the total accumulated Gain, empirically confirming that most of the 68 features are redundant or contribute minimal discriminative information.

**[STYLE: Table]** Table 4. Top-20 features ranked by XGBoost Gain-based importance

| Rank | Feature | Rank | Feature |
|---|---|---|---|
| 1 | Fwd Seg Size Min | 11 | Bwd Pkt Len Std |
| 2 | URG Flag Cnt | 12 | Bwd Seg Size Avg |
| 3 | Tot Bwd Pkts | 13 | Fwd IAT Std |
| 4 | Fwd Act Data Pkts | 14 | Bwd IAT Max |
| 5 | Fwd Pkt Len Max | 15 | Bwd Pkt Len Max |
| 6 | Fwd Pkt Len Mean | 16 | Fwd Header Len |
| 7 | Bwd Pkt Len Mean | 17 | Fwd Pkts/s |
| 8 | Init Bwd Win Byts | 18 | Fwd URG Flags |
| 9 | TotLen Bwd Pkts | 19 | Fwd IAT Tot |
| 10 | Init Fwd Win Byts | 20 | Fwd Pkt Len Std |

A gradient-based analysis further distinguished global importance (XGBoost Gain) from local sensitivity (approximated Saliency Map). The evaluation showed that when the model is forced to decide from only 10 features, the saliency magnitude on those features increases sharply compared with the 68-feature model. The feature *Init Fwd Win Byts* recorded the highest saliency score, making it the most sensitive to perturbation—even though it ranks only 10th in the Gain metric. Technically, *Init Fwd Win Byts* represents the initial forward TCP window size, which an attacker can manipulate in the TCP header without breaking packet functionality, making it a realistic evasion target.

### [STYLE: Heading 2] Feature-Selection Ablation Results

Following the ablation procedure, the XGBoost model was retrained on four feature configurations. Table 5 compares classification performance, model-artifact size, and inference speed.

**[STYLE: Table]** Table 5. Feature-selection ablation: performance and efficiency comparison

| Configuration | Features | F1-score | ROC-AUC | Model Size | Inference (10k) |
|---|---|---|---|---|---|
| Full Features | 68 | 0.9798 | 0.9911 | 7.17 MB | 0.2400 s |
| Top-20 | 20 | 0.9795 | 0.9900 | 6.82 MB | 0.2266 s |
| Top-15 | 15 | 0.9717 | 0.9883 | 5.91 MB | 0.1930 s |
| **Top-10** | **10** | **0.9717** | **0.9865** | **5.65 MB** | **0.1826 s** |

The F1-score decreases only 0.83% from Full (0.9798) to Top-10 (0.9717), while the model size shrinks 21.2% (7.17 MB to 5.65 MB) and inference time drops 23.9% (0.2400 s to 0.1826 s per 10,000 samples). Because Top-10 matches the Top-15 F1-score with a more compact and faster model, it was selected as the sweet spot.

### [STYLE: Heading 2] Comparative Evaluation of the Four Scenarios (S1–S4)

Table 6 presents the quantitative results of the four cross-testing scenarios on the Top-10 subset with perturbation ε = 0.10.

**[STYLE: Table]** Table 6. Quantitative evaluation results for scenarios S1, S2, S3, and S4

| Scenario | Model | Test data | MCC | F1-score | Precision |
|---|---|---|---|---|---|
| S1 (Baseline) | Baseline | Clean | 0.9351 | 0.9729 | 0.9720 |
| S2 (Vulnerability) | Baseline | Manipulated | 0.0184 | 0.7539 | 0.6905 |
| S3 (Integrity) | Robust | Clean | 0.9347 | 0.9727 | 0.9718 |
| S4 (Robustness) | Robust | Manipulated | **0.9953** | **0.9985** | **0.9985** |

Under evasion attack, the baseline MCC collapses from 0.9351 (S1) to 0.0184 (S2), a 98% decline that constitutes the security gap. After Adversarial Training, the robust model recovers to MCC = 0.9953 on manipulated data (S4), an increase of +0.9769 over S2. Meanwhile, the robust model on clean data (S3) retains MCC = 0.9347, only 0.04% below the baseline S1, indicating that hardening does not degrade normal-traffic detection. Notably, the F1-score in S2 remains at 0.7539 despite the near-zero MCC, because the weighted F1 is still inflated by correct classification of the majority (benign) class, whereas MCC more sensitively captures the collapse on the minority (attack) classes.

The per-class behavior across the four scenarios is visualized in the confusion matrices of Figure 3. In S2, nearly all attack classes are misclassified as benign (the collapse), whereas S4 restores a clean diagonal, confirming the recovery. A grouped-bar summary of the four metrics is shown in Figure 4.

**[SISIPKAN GAMBAR: nids-figures/evaluation_confusion_2x2_en.png — lebar penuh]**
**[STYLE: Figure]** Figure 3. confusion matrices for the 2x2 evaluation scenarios (XGBoost Top-10, ε=0.1)

**[SISIPKAN GAMBAR: nids-figures/evaluation_grouped_bar_2x2_en.png — lebar ~85%]**
**[STYLE: Figure]** Figure 4. comprehensive metric comparison across scenarios S1–S4

### [STYLE: Heading 2] Robustness Ablation Results: Feature-Dimension Sweet Spot

The Robustness Ablation Study evaluated the effect of feature pruning on resilience under evasion (ε = 0.10). Table 7 reports the adversarial-data MCC for the baseline (S2) and robust (S4) models across the four configurations, together with the recovery achieved by Adversarial Training.

**[STYLE: Table]** Table 7. Robustness ablation: adversarial-data MCC before (S2) and after (S4) Adversarial Training per configuration (ε = 0.10)

| Configuration | Features | MCC base+adv (S2) | MCC rob+adv (S4) | Recovery |
|---|---|---|---|---|
| C1 (Full) | 68 | −0.047 | **0.997** | +1.044 |
| C2 (Top-15) | 15 | −0.006 | 0.992 | +0.998 |
| C3 (Top-10) | 10 | **0.018** | **0.995** | +0.977 |
| C4 (Top-5) | 5 | −0.070 | 0.873 | +0.943 |

All baseline models collapse under attack (MCC near zero or negative), whereas every robust model recovers to MCC > 0.87. The Top-5 configuration (C4) shows the lowest robustness (MCC S4 = 0.873), indicating that five features are insufficient to form a stable decision boundary. Configurations C1, C2, and C3 differ only marginally in MCC S4 (0.997, 0.992, and 0.995 respectively; < 0.5%), while model size grows from 5.65 MB to 7.17 MB. The Top-10 configuration (C3) is the only one that keeps the baseline adversarial MCC positive (0.018) while achieving MCC S4 = 0.995, confirming it as the optimal sweet spot.

### [STYLE: Heading 2] Real-Traffic Validation in the AWS Cloud Environment

To verify that the offline findings are not merely laboratory artifacts, the baseline and robust models were tested on real network traffic generated in an Amazon Web Services (AWS) cloud environment. The testing infrastructure was built inside a Virtual Private Cloud (VPC, 10.3.0.0/16) comprising three EC2 nodes: an Attacker node (public subnet) running Hydra, Slowloris, and nping; a Target node (private subnet) running SSH and HTTP (Nginx) services; and an Analyzer node performing feature extraction and inference. Traffic to the Target was captured using tcpdump, stored to Amazon S3, and extracted into flow features using the NFStream library. Because NFStream does not natively expose two of the Top-10 TCP window features (*Init Fwd Win Byts* and *Init Bwd Win Byts*), a custom NFStream plugin was developed to parse the TCP window value from the first packet of each flow direction, so that all 10 features could be extracted intact. The testing topology is shown in Figure 5.

**[SISIPKAN GAMBAR: nids-figures/fig_aws.png — lebar penuh]**
**[STYLE: Figure]** Figure 5. real-traffic testing infrastructure on AWS: the attacker node (public subnet) launches attacks against the target node (private subnet); traffic is captured at the target and routed through Amazon S3 to the analyzer node for feature extraction and inference

The test replicated the 2×2 matrix (RT-S1 to RT-S4) equivalent to the offline scenarios. Table 8 compares real-traffic results with offline results on the Top-10 configuration.

**[STYLE: Table]** Table 8. Offline vs. real-traffic (AWS) performance comparison on the Top-10 configuration

| Scenario | MCC (Offline) | MCC (Real) | F1 (Offline) | F1 (Real) |
|---|---|---|---|---|
| RT-S1 (Base + Clean) | 0.9351 | 0.164 | 0.9729 | 0.855 |
| RT-S2 (Base + Evasion) | 0.0184 | −0.070 | 0.7539 | 0.633 |
| RT-S3 (Robust + Clean) | 0.9347 | 0.339 | 0.9727 | 0.581 |
| RT-S4 (Robust + Evasion) | 0.9953 | 0.389 | 0.9985 | 0.626 |

Although the absolute MCC values decrease on real traffic, the relative behavioral pattern is preserved. The baseline degrades when exposed to evasion (RT-S1 → RT-S2: MCC 0.164 → −0.070, falling below random guessing), whereas the robust model instead improves (RT-S3 → RT-S4: MCC 0.339 → 0.389) and records perfect Precision (1.0). Diagnostic analysis of the feature distributions attributes the absolute drop to feature mismatch between extractors: *Fwd Seg Size Min* in NFStream (≈66 bytes, including header) differs from the CICFlowMeter definition at training time (≈18 bytes), a deviation of z ≈ +6.2; and the TCP window value on modern EC2 instances (≈62 KB) is far larger than in the CIC-IDS2018 recording (≈8 KB), a deviation of z ≈ +3.3 on *Init Fwd/Bwd Win Byts*.

---

## [STYLE: Heading 1] Discussion

### [STYLE: Heading 2] Security Gap and the Effectiveness of Adversarial Training

The experimental results reveal a fundamental vulnerability of the feature-reduced baseline model. Although the baseline achieves a high MCC of 0.9351 under normal conditions (S1), its performance collapses to 0.0184 under a subtle perturbation of ε = 0.10 (S2)—a 98% decline. This confirms that concentrating the decision on a small set of features, while efficient, sharpens the model's local sensitivity and enlarges the attack surface. The disparity between the near-zero MCC and the still-moderate F1-score (0.7539) in S2 also demonstrates why MCC is the more trustworthy metric on imbalanced data: the weighted F1 remains inflated by the majority (benign) class even as detection of the attack classes fails almost entirely.

Adversarial Training addresses this weakness effectively. On clean traffic, the robust model (S3, MCC = 0.9347) is virtually identical to the baseline (S1), only 0.04% lower—evidence that augmenting the training set with adversarial samples does not induce a "paranoid" model or harm normal-traffic detection. On manipulated traffic, the robust model recovers to MCC = 0.9953 (S4), isolating the attacker's gradient-shift within the redrawn decision boundary.

### [STYLE: Heading 2] Interpreting the S4 > S1 Phenomenon: Transfer vs. White-Box Attack

The observation that MCC in S4 (0.9953) exceeds S1 (0.9351) warrants careful interpretation. It arises because the adversarial samples were generated from the saliency of the *baseline* model, not the robust model. This constitutes a **transfer attack** (grey-box with respect to the robust model): perturbations designed to fool the baseline become ineffective against a robust model trained to withstand exactly those patterns, while clean data retains richer natural variation than the stereotypical ⟨rumus R⟩ perturbation. It must be acknowledged honestly that, because of this transfer setup, the S4 robustness value is potentially an **optimistic estimate** of the model's true robustness. Under a stricter **white-box adaptive** scenario—where the attacker generates perturbations directly from the robust model's own saliency—the observed robustness would likely be lower. This study did not perform such white-box adaptive evaluation; the limitation is stated explicitly and set as a primary direction for future work. Accordingly, the robustness claim here is valid within the scope of defense against transfer/static evasion attacks, not adaptive white-box attacks.

### [STYLE: Heading 2] Feature-Dimension Sweet Spot and Practical Implications

The Robustness Ablation Study confirms Top-10 (C3) as the optimal balance: it reduces model size by 21.2% (7.17 MB to 5.65 MB) while maintaining robustness (MCC S4 = 0.995) practically identical to the full model (0.997) and slightly above Top-15 (0.992). Extreme pruning to five features (C4) degrades robustness to 0.873, indicating that five dimensions cannot form a stable decision boundary. These findings carry practical weight for modern network-security architectures. First, the compact ≈5.65 MB model can be embedded directly into resource-constrained edge devices such as routers and IoT gateways, removing the dependency on centralized cloud processing. Second, in serverless architectures (e.g., AWS Lambda) where cost scales with execution time and memory, using only 10 features keeps inference very fast and memory-light, reducing operational cost at enterprise scale. Third, the robust model's resilience (MCC = 0.9953) mitigates false-alarm fatigue, ensuring the NIDS is not easily paralyzed by deliberately crafted TCP/IP-variable shifts.

For reproducibility and to clarify the reported binary size, it should be noted that the 5.65 MB artifact of the Top-10 model is a direct function of the XGBoost ensemble structure rather than of the input dimensionality alone. With 200 boosting trees (n_estimators = 200) and a maximum tree depth of 8 (max_depth = 8), each tree may hold up to ⟨rumus S⟩ split nodes; the serialized model therefore stores the thresholds, split features, and leaf values of the full ensemble, which accounts for the multi-megabyte footprint even when only ten features are used. Reducing the feature set from 68 to 10 shrinks the size by 21.2% (7.17 → 5.65 MB) because fewer candidate features yield shallower, sparser trees on average, but the dominant size driver remains the tree count and depth. This also explains why the figure does not fall below the ~3 MB range typical of aggressively compressed or shallow-depth XGBoost variants: the present configuration deliberately retains depth-8 trees to preserve detection fidelity on the seven-class, highly imbalanced problem. Reporting these hyperparameters (n_estimators = 200, max_depth = 8) makes the 5.65 MB value consistent and interpretable across the manuscript.

The holistic radar comparison across five metrics (MCC, F1-score, Precision, Recall, Accuracy), shown in Figure 6, reinforces this reading: the near-full, symmetric polygons of S1, S3, and S4 indicate balanced high performance, whereas the sharply shrunken S2 polygon—collapsing on the MCC axis yet still wide on Accuracy and Recall—visually confirms the misleading nature of conventional metrics on imbalanced data. The similar polygon shapes of S1, S3, and S4 further emphasize that Adversarial Training restores robustness without distorting the model's detection profile under normal conditions.

**[SISIPKAN GAMBAR: nids-figures/evaluation_radar_2x2_en.png — lebar ~70%]**
**[STYLE: Figure]** Figure 6. multi-metric radar comparison of scenarios S1–S4

### [STYLE: Heading 2] Generalization to Real Traffic and Mitigation Strategies

The real-traffic validation delivers a nuanced but important message. We stress that the primary measure of success for the proposed Adversarial Training is **the consistency of the relative pattern**, not the absolute MCC value: on AWS traffic the baseline still degrades when exposed to evasion (MCC 0.164 → −0.070, falling below random guessing), whereas the robust model instead *improves* (MCC 0.339 → 0.389) and retains perfect Precision (1.0). This qualitative behaviour—baseline collapses, robust model holds—is identical to the offline finding, confirming that the core contribution is robust across test domains and is not merely a benchmark artifact. The decline in the *absolute* MCC should therefore be interpreted not as a fundamental model failure but as a textbook **distribution shift** caused by the different network environment and, above all, by **feature-extractor mismatch** between the training extractor (CICFlowMeter) and the production extractor (NFStream). Two features dominate this shift: the extractor-definition mismatch on *Fwd Seg Size Min* (≈66 bytes in NFStream, including the header, vs. ≈18 bytes at training time; z ≈ +6.2) and the environmental difference in TCP window size on modern EC2 instances (≈62 KB vs. ≈8 KB in the CIC-IDS2018 recording; z ≈ +3.3 on *Init Fwd/Bwd Win Byts*). Rather than weakening the contribution, this absolute drop makes the case *stronger*: it is direct empirical evidence of the generalization gap that motivates—and quantifies the urgency of—the three mitigation strategies recommended below (extractor calibration, domain adaptation, and multi-extractor training), each of which targets precisely this distribution-shift mechanism.

To close this gap and make the system reliably deployable, three concrete mitigation strategies are recommended. *First*, **extractor calibration**: mathematically aligning the production extractor (NFStream) with the training extractor (CICFlowMeter)—for example, correcting *Fwd Seg Size Min* from the NFStream basis (≈66 bytes, including header) to the CICFlowMeter definition (≈18 bytes) via an affine (offset/scaling) transform, which addresses the largest deviation without retraining. *Second*, **domain adaptation / transfer learning**: fine-tuning the model's decision layer using a small amount of labeled real traffic from the target environment to align the decision boundary with the operational feature distribution, particularly for sensitive features such as *Init Fwd Win Byts*. *Third*, **multi-extractor training**: incorporating extraction variability from multiple libraries (CICFlowMeter, NFStream, and Zeek) into the training set so that the model becomes invariant to extractor-implementation differences. These strategies are complementary—calibration offers a quick fix without retraining, domain adaptation aligns the model to a specific environment, and multi-extractor training provides structural cross-environment robustness.

### [STYLE: Heading 2] Comparison with Prior Work

Unlike the mainstream of adversarial NIDS research, which combines generative models with classifiers and stops at offline evaluation (Mari et al., 2023; Kumar & Sinha, 2023; Park et al., 2023; Ding et al., 2024), this study emphasizes the tension between feature efficiency and adversarial robustness on a tree-based model, and validates it on real cloud traffic. Whereas prior evasion studies largely demonstrate attack effectiveness (Zhao et al., 2021; Wang et al., 2024a; Xu et al., 2025a), the present work quantifies the security gap and then closes it through Adversarial Training (Madry et al., 2018), additionally reporting the honest generalization gap on real traffic—an aspect consistent with cross-dataset concerns raised by Cantone et al. (2024) but rarely examined under live-traffic conditions.

> **CATATAN RUMUS INLINE (Discussion):**
> - R: `\epsilon \cdot \text{sign}(S(\mathbf{x}))`
> - S: `2^{8}-1 = 255`

---

## [STYLE: Heading 1] Conclusion

This study developed and evaluated an NIDS optimization approach that combines XGBoost Gain-based feature reduction with Saliency Map gradient-based Adversarial Training. Four main conclusions follow. First, the feature-reduced baseline model is highly vulnerable to evasion attacks: although it attains MCC = 0.9351 under normal conditions (S1), performance collapses to MCC = 0.0184 under a subtle perturbation (ε = 0.10, S2)—a 98% decline. Second, Adversarial Training based on Min-Max optimization restores detection reliability to MCC = 0.9953 (S4, an increase of +0.9769 over S2) while preserving integrity on normal traffic (S3, MCC = 0.9347; only 0.04% below the baseline). Third, through the Robustness Ablation Study, the Top-10 configuration (C3) proved to be the optimal sweet spot, cutting model size to 5.65 MB (a 21.2% reduction) while maintaining high resilience (MCC S4 = 0.995); the Top-5 configuration degraded to MCC S4 = 0.873, confirming that five features are insufficient for a stable decision boundary. Fourth, real-traffic validation in the AWS cloud showed that the robustness pattern remains consistent with the offline results—the baseline degrades under evasion while the robust model holds—even though the absolute MCC decreases due to feature mismatch between the NFStream and CICFlowMeter extractors and differences in the TCP window environment. This consistency confirms that the effectiveness of Adversarial Training is robust across test domains, while also revealing a generalization challenge seldom discussed in the literature.

To broaden the scope and implications of this study, several directions are recommended for future research. First, **white-box adaptive attack evaluation**: the current robustness assessment is limited to a transfer-attack scheme (perturbations generated from the baseline model), so the robust model's robustness may be optimistic; future work should generate adversarial samples directly from the robust model's own saliency to obtain a worst-case estimate. Second, **black-box attack testing** (e.g., Boundary Attack or query-based attacks) where the attacker has no direct access to the target model's gradients. Third, **extending classifier types**: applying and comparing this gradient-based hardening strategy on other tree-based architectures (LightGBM, CatBoost) and compressed deep learning models (quantized neural networks). Fourth, **in-the-wild testbed**: deploying the 5.65 MB model on real edge hardware (e.g., Raspberry Pi or a smart router) to measure real-time packet-processing throughput and power consumption. Most importantly, as the immediate and central item on our research roadmap, we will directly execute a quantitative evaluation of the three real-traffic mitigation strategies—extractor calibration, domain adaptation, and multi-extractor training—in order to explicitly close the benchmark-to-deployment generalization gap observed in the AWS environment. This next phase will measure, for each strategy, the degree to which the absolute MCC on real traffic is recovered toward the offline level, thereby transforming the mitigation proposals presented here from recommendations into empirically validated solutions and establishing a clear, long-term path toward a production-ready, evasion-resilient NIDS.

## [STYLE: Acknowledge / Heading 1] Acknowledgement

The authors thank Politeknik Elektronika Negeri Surabaya (PENS) for the research support and facilities provided during this study.

## [STYLE: Heading 1] Conflicts of Interest

The authors declare no conflict of interest.

---

## [STYLE: Heading 1] References

> **Semua entri di bawah pakai Style *Reference*. Sudah APA name-year, urut alfabetis. Tinggal blok-copy.**

Alabsi, B. A., Anbar, M., & Rihan, S. D. A. (2023). Conditional tabular generative adversarial based intrusion detection system for detecting DDoS and DoS attacks on the Internet of Things networks. *Sensors*, 23(12), 5644.

Aldhaheri, S., & Alhuzali, A. (2023). SGAN-IDS: Self-attention-based generative adversarial network against intrusion detection systems. *Sensors*, 23(18), 7796.

Al-Ajlan, M., & Ykhlef, M. (2024). A review of generative adversarial networks for intrusion detection systems: Advances, challenges, and future directions. *Computers, Materials & Continua*, 81(2), 2053–2076.

Alshehri, M. S., Saidani, O., Malwi, W. A., Asiri, F., Latif, S., Khattak, A. A., & Ahmad, J. (2025). A hybrid Wasserstein GAN and autoencoder model for robust intrusion detection in IoT. *Computer Modeling in Engineering & Sciences*, 143(3), 3899–3920.

Alsaedi, A., Moustafa, N., Tari, Z., Mahmood, A. N., & Anwar, A. (2020). TON_IoT telemetry dataset: A new generation dataset of IoT and IIoT for data-driven intrusion detection systems. *IEEE Access*, 8, 165130–165150.

Aceto, G., Giampaolo, F., Guida, C., Izzo, S., Pescapè, A., Piccialli, F., & Prezioso, E. (2024). Synthetic and privacy-preserving traffic trace generation using generative AI models for training network intrusion detection systems. *Journal of Network and Computer Applications*, 229, 103926.

Arjovsky, M., Chintala, S., & Bottou, L. (2017). Wasserstein GAN. *arXiv preprint* arXiv:1701.07875.

Babu, K. S., & Rao, Y. N. (2023). MCGAN: Modified conditional generative adversarial network for class imbalance problems in network intrusion detection system. *Applied Sciences*, 13(4).

Cantone, M., Marrocco, C., & Bria, A. (2024). Machine learning in network intrusion detection: A cross-dataset generalization study. *IEEE Access*, 12, 144491–144509.

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785–794).

Chicco, D., & Jurman, G. (2020). The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. *BMC Genomics*, 21(1), 6.

de Araujo-Filho, P. F., Naili, M., Kaddoum, G., Fapi, E. T., & Zhu, Z. (2023). Unsupervised GAN-based intrusion detection system using temporal convolutional networks and self-attention. *IEEE Transactions on Network and Service Management*, 20(4), 4951–4963.

Devadiga, D., Jin, G., Potdar, B., Koo, H., Han, A., Shringi, A., Singh, A., Chaudhari, K., & Kumar, S. (2023). GLEAM: GAN and LLM for evasive adversarial malware. In *2023 14th International Conference on Information and Communication Technology Convergence (ICTC)* (pp. 53–58).

Ding, H., Sun, Y., Huang, N., Shen, Z., & Cui, X. (2024). TMG-GAN: Generative adversarial networks-based imbalanced learning for network intrusion detection. *IEEE Transactions on Information Forensics and Security*, 19, 1156–1167.

Dunmore, A., Jang-Jaccard, J., Sabrina, F., & Kwak, J. (2023). Generative adversarial networks for malware detection: A survey. *arXiv preprint* arXiv:2302.08558.

Educative. (2025). *What are the challenges in training GAN?* Retrieved September 10, 2025, from https://www.educative.io/answers/what-are-the-challenges-in-training-gan

Goodfellow, I., Pouget-Abadie, J., Mirza, M., Xu, B., Warde-Farley, D., Ozair, S., Courville, A., & Bengio, Y. (2014). Generative adversarial nets. In *Advances in Neural Information Processing Systems* (pp. 2672–2680).

Goodfellow, I. J., Shlens, J., & Szegedy, C. (2015). Explaining and harnessing adversarial examples. In *International Conference on Learning Representations (ICLR)*.

Hassan, U., Chen, D., Cheung, S.-C., & Chuah, C.-N. (2023). HE-GAN: Differentially private GAN using Hamiltonian Monte Carlo based exponential mechanism. In *Proceedings of IEEE ICASSP* (pp. 3186–3190).

Huang, Y., Fields, K. G., & Ma, Y. (2022). A tutorial on generative adversarial networks with application to classification of imbalanced data. *Statistical Analysis and Data Mining: The ASA Data Science Journal*, 15(5), 543–552.

Jiang, X., Zhang, Y., Zhou, X., & Grossklags, J. (2023). Distributed GAN-based privacy-preserving publication of vertically-partitioned data. *Proceedings on Privacy Enhancing Technologies*, 2023(2), 50–69.

Kohavi, R. (1995). A study of cross-validation and bootstrap for accuracy estimation and model selection. In *Proceedings of the 14th International Joint Conference on Artificial Intelligence (IJCAI)* (pp. 1137–1143).

Koroniotis, N., Moustafa, N., Sitnikova, E., & Turnbull, B. (2019). Towards the development of realistic botnet dataset for IoT networks. *IEEE Access*, 7, 94529–94541.

Kumar, V., & Sinha, D. (2023). Synthetic attack data generation model applying generative adversarial network for intrusion detection. *Computers & Security*, 125, 103054.

Madry, A., Makelov, A., Schmidt, L., Tsipras, D., & Vladu, A. (2018). Towards deep learning models resistant to adversarial attacks. In *International Conference on Learning Representations (ICLR)*.

Mari, A.-G., Zinca, D., & Dobrota, V. (2023). Development of a machine-learning intrusion detection system and testing of its performance using a generative adversarial network. *Sensors*, 23(3), 1315.

Matthews, B. W. (1975). Comparison of the predicted and observed secondary structure of T4 phage lysozyme. *Biochimica et Biophysica Acta (BBA) - Protein Structure*, 405(2), 442–451.

Mbow, M., Roman, R., Takahashi, T., & Sakurai, K. (2024). Evading IoT intrusion detection systems with GAN. In *2024 19th Asia Joint Conference on Information Security (AsiaJCIS)* (pp. 48–55).

Merzouk, M. A., Beurier, E., Yaich, R., Boulahia-Cuppens, N., Cuppens, F., & Khomh, F. (2025). Diffusion-based adversarial purification for intrusion detection. In *IFIP Annual Conference on Data and Applications Security and Privacy* (pp. 351–370). Springer.

Mirza, M., & Osindero, S. (2014). Conditional generative adversarial nets. *arXiv preprint* arXiv:1411.1784.

Moustafa, N., & Slay, J. (2015). UNSW-NB15: A comprehensive data set for network intrusion detection systems. In *MILCOM* (pp. 1–6).

Neto, E. C. P., Dadkhah, S., Ferreira, R., Zohourian, A., Lu, R., & Ghorbani, A. A. (2023). CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT environment. *Sensors*, 23(13).

Odena, A., Olah, C., & Shlens, J. (2017). Conditional image synthesis with auxiliary classifier GANs. In *Proceedings of the 34th International Conference on Machine Learning* (PMLR, Vol. 70, pp. 2642–2651).

Park, C., Lee, J., Kim, Y., Park, J.-G., Kim, H., & Hong, D. (2023). An enhanced AI-based network intrusion detection system using generative adversarial networks. *IEEE Internet of Things Journal*, 10(3), 2330–2345.

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

Radford, A., Metz, L., & Chintala, S. (2015). Unsupervised representation learning with deep convolutional generative adversarial networks. *arXiv preprint* arXiv:1511.06434.

Rahman, S., Pal, S., Mittal, S., Chawla, T., & Karmakar, C. (2024). Syn-GAN: A robust intrusion detection system using GAN-based synthetic data for IoT security. *Internet of Things*, 26, 101212.

Rahman, M. A., Shahriar, H., Clincy, V., Hossain, M. F., & Rahman, M. (2023). A quantum generative adversarial network-based intrusion detection system. In *2023 IEEE 47th Annual Computers, Software, and Applications Conference (COMPSAC)* (pp. 1810–1815).

Randhawa, R. H., Aslam, N., Alauthman, M., & Rafiq, H. (2023). Evasion generative adversarial network for low data regimes. *IEEE Transactions on Artificial Intelligence*, 4(5), 1076–1088.

Riaz, R., Han, G., Shaukat, K., Khan, N. U., Zhu, H., & Wang, L. (2025). A novel ensemble Wasserstein GAN framework for effective anomaly detection in industrial Internet of Things environments. *Scientific Reports*, 15(1), 26786.

Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). Toward generating a new intrusion detection dataset and intrusion traffic characterization. In *ICISSP* (pp. 108–116).

Simonyan, K., Vedaldi, A., & Zisserman, A. (2014). Deep inside convolutional networks: Visualising image classification models and saliency maps. In *Workshop at International Conference on Learning Representations (ICLR)*.

Szegedy, C., Zaremba, W., Sutskever, I., Bruna, J., Erhan, D., Goodfellow, I., & Fergus, R. (2014). Intriguing properties of neural networks. In *International Conference on Learning Representations (ICLR)*.

Tavallaee, M., Bagheri, E., Lu, W., & Ghorbani, A. A. (2009). A detailed analysis of the KDD Cup 99 data set. In *Proceedings of CISDA*.

Trung, D. M., Khoa, N. H., Duy, P. T., Pham, V.-H., & Cam, N. T. (2024). AAGAN: Android malware generation system based on generative adversarial network. *International Journal of Semantic Computing*, 14(1).

Wang, D., Wang, X., & Fei, J. (2024). IDS-GAN: Adversarial attack against intrusion detection based on generative adversarial networks. In *2024 5th International Conference on Computer Vision, Image and Deep Learning (CVIDL)* (pp. 1130–1134).

Wang, J., Yang, K., & Li, M. (2024). NIDS-FGPA: A federated learning network intrusion detection algorithm based on secure aggregation of gradient similarity models. *PLoS ONE*, 19(10), e0308639.

Xu, L., Skoularidou, M., Cuesta-Infante, A., & Veeramachaneni, K. (2019). Modeling tabular data using conditional GAN. In *Advances in Neural Information Processing Systems* (Vol. 32). Curran Associates, Inc.

Xu, D., Lv, Y., Wang, M., Zheng, B., Zhao, J., & Yu, J. (2025). DEMGAN: A machine learning-based intrusion detection system evasion scheme. *Computers, Materials & Continua*, 84(1), 1731–1746.

Xu, C., Zhan, Y., Chen, G., Wang, Z., Liu, S., & Hu, W. (2025). Elevated few-shot network intrusion detection via self-attention mechanisms and iterative refinement. *PLoS ONE*, 20(1), e0317713.

Yang, H., Xu, J., Xiao, Y., & Hu, L. (2023). SPE-ACGAN: A resampling approach for class imbalance problem in network intrusion detection systems. *Electronics*, 12(15), 3323.

Yang, Y., Liu, X., Wang, D., Sui, Q., Yang, C., Li, H., Li, Y., & Luan, T. (2025). A CE-GAN based approach to address data imbalance in network intrusion detection systems. *Scientific Reports*, 15(1), 7916.

Zhang, H., Goodfellow, I., Metaxas, D., & Odena, A. (2019). Self-attention generative adversarial networks. In *Proceedings of the 36th International Conference on Machine Learning* (PMLR, Vol. 97, pp. 7354–7363).

Zhao, S., Li, J., Wang, J., Zhang, Z., Zhu, L., & Zhang, Y. (2021). AttackGAN: Adversarial attack against black-box IDS using generative adversarial networks. *Procedia Computer Science*, 187, 128–133.
