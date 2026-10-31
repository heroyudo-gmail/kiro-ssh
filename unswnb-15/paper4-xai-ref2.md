# Explainable AI untuk Deteksi Intrusi Jaringan: Mendiagnosis dan Memperbaiki Kegagalan Generalisasi Lintas Dataset pada Pipeline Bebas Kebocoran

## Ringkasan Eksekutif

Laporan ini menyajikan analisis mendalam mengenai penggunaan *Explainable Artificial Intelligence* (XAI) dalam mendiagnosis dan memperbaiki kegagalan generalisasi pada Sistem Deteksi Intrusi Jaringan (*Network Intrusion Detection System* - NIDS). Fokus utama adalah pada identifikasi penyebab kegagalan performa ketika model ML diuji pada dataset yang berbeda dari data pelatihannya (*cross-dataset generalization*), serta peran kebocoran data (*data leakage*) dalam menciptakan bias yang menyesatkan. Melalui sumber-sumber literatur terbaru, ditemukan bahwa teknik seperti SHAP dan LIME sangat krusial untuk memetakan atribusi fitur dan mendeteksi pergeseran domain (*domain shift*). Strategi perbaikan yang dibahas meliputi penggunaan *Domain Adaptation*, kalibrasi model melalui *Platt scaling*, serta pengembangan *pipeline* evaluasi yang benar-benar bebas kebocoran. Laporan ini menyimpulkan bahwa transparansi model melalui XAI dan integritas data melalui *pipeline* yang ketat adalah fondasi utama bagi keamanan siber yang berkelanjutan dan dapat dipercaya di masa depan.

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Metode Diagnosis Menggunakan XAI](#2-metode-diagnosis-menggunakan-xai)
3. [Analisis Kegagalan Generalisasi dan Kebocoran Data](#3-analisis-kegagalan-generalisasi-dan-kebocoran-data)
4. [Strategi Perbaikan dan Teknik Generalisasi](#4-strategi-perbaikan-dan-teknik-generalisasi)
5. [Keterbatasan Bukti dan Celah Penelitian](#5-keterbatasan-bukti-dan-celah-penelitian)
6. [Kesimpulan](#6-kesimpulan)

---

## 1. Pendahuluan

Sistem Deteksi Intrusi Jaringan (NIDS) berbasis Kecerdasan Buatan (AI) telah menjadi pilar utama dalam pertahanan keamanan siber modern. Namun, tantangan signifikan muncul ketika model yang dilatih pada satu lingkungan jaringan gagal mempertahankan performanya saat diterapkan pada lingkungan lain yang berbeda secara distribusi data. Fenomena ini dikenal sebagai kegagalan generalisasi lintas dataset (*cross-dataset generalization failure*). Penyebab utama dari masalah ini sering kali berakar pada *domain shift* dan adanya *data leakage* (kebocoran data) yang terjadi selama fase pelatihan atau ekstraksi fitur.

Penggunaan *Explainable AI* (XAI) muncul sebagai solusi diagnostik untuk memahami mekanisme internal model dalam mengambil keputusan. Dengan teknik seperti SHAP (*SHapley Additive exPlanations*) dan LIME (*Local Interpretable Model-agnostic Explanations*), peneliti dapat mengidentifikasi fitur mana yang paling berpengaruh dan apakah model tersebut mempelajari pola serangan yang valid atau sekadar menghafal artefak data yang bocor [1], [2]. Studi terbaru menekankan pentingnya membangun *pipeline* evaluasi yang bebas kebocoran (*leakage-free*) untuk memastikan bahwa performa yang dilaporkan mencerminkan kemampuan deteksi dunia nyata, bukan sekadar bias dataset akademik [4], [5]. Laporan ini mengevaluasi berbagai pendekatan terbaru dalam mendiagnosis masalah tersebut dan strategi untuk memperbaiki ketahanan model agar mampu beroperasi secara efektif lintas domain.

## 2. Metode Diagnosis Menggunakan XAI

Diagnosis terhadap model deteksi intrusi dilakukan untuk memahami mengapa sebuah model memberikan hasil tertentu dan mengapa ia gagal pada data yang belum pernah dilihat sebelumnya (*unseen data*).

### 2.1 Pemanfaatan SHAP dan LIME
Teknik XAI seperti SHAP menjadi standar dalam literatur untuk memberikan penjelasan global dan lokal terhadap keputusan model. SHAP digunakan untuk menganalisis kepentingan fitur lintas dataset, yang memungkinkan peneliti melihat perbedaan urutan fitur yang dianggap penting oleh model antara domain sumber dan target [1], [10]. Misalnya, penggunaan *TreeExplainer* pada model XGBoost membantu menghasilkan atribusi fitur tingkat instans yang mendalam untuk mendeteksi anomali [3]. LIME juga diterapkan untuk memberikan penjelasan lokal, membantu analis memahami perilaku model pada aliran data spesifik guna mendeteksi potensi serangan *zero-day* [2].

### 2.2 Diagnosis Kegagalan melalui Atribusi Fitur
Kegagalan generalisasi sering kali didiagnosis dengan membandingkan ringkasan plot SHAP (*summary plots*) dari berbagai dataset. Variasi nilai SHAP dan distribusi fitur yang tidak selaras antara domain sumber dan target merupakan indikator kuat adanya masalah generalisasi [10]. Selain itu, teknik XAI membantu mengukur kontribusi fitur secara kuantitatif, yang dapat mengungkapkan apakah model terlalu bergantung pada fitur meta-data yang tidak relevan seperti alamat IP atau *flow ID* yang unik, yang seharusnya dihapus untuk menghindari bias [14].

### 2.3 Pendekatan Diagnosis Tanpa XAI Klasik
Selain SHAP dan LIME, beberapa studi mengusulkan metodologi diagnosis berbasis data secara langsung. Teknik seperti *Kernel Density Estimation* (KDE) dan *Principal Component Analysis* (PCA) digunakan untuk mengidentifikasi perbedaan distribusi kelas dan redundansi sampel [11], [13]. Ada juga pendekatan *blind generalization* yang melatih pengklasifikasi pada satu kelas serangan untuk mengevaluasi apakah fitur tersebut menghasilkan performa tinggi secara seragam di kelas lain, guna mengidentifikasi kontaminasi fitur non-metadata [22].

## 3. Analisis Kegagalan Generalisasi dan Kebocoran Data

Kegagalan generalisasi dalam NIDS bukan sekadar masalah algoritma, melainkan sering kali merupakan hasil dari integritas data yang rendah dan desain evaluasi yang cacat.

### 3.1 Fenomena Data Leakage (Kebocoran Data)
Kebocoran data terjadi ketika informasi dari set uji atau informasi yang tidak relevan dengan perilaku serangan masuk ke dalam proses pelatihan model. Hal ini mencakup kebocoran temporal dan redundansi sampel yang sering ditemukan dalam dataset klasik seperti KDD Cup 99 [3]. Identifikasi kebocoran juga mencakup deteksi fitur kontaminan yang menyebabkan model memiliki performa tinggi secara artifisial namun gagal di dunia nyata [22]. Penghapusan fitur seperti alamat IP, nomor *port*, dan *timestamp* sangat disarankan untuk mencegah model mempelajari identitas spesifik aliran data daripada karakteristik intrusi itu sendiri [14].

### 3.2 Pergeseran Domain dan Dataset Heterogen
Kesulitan utama dalam transfer representasi lintas lingkungan jaringan disebabkan oleh perbedaan infrastruktur dan protokol yang menghasilkan distribusi fitur yang berbeda [2]. Pergeseran domain, baik berupa *covariate shift* (perubahan distribusi input) maupun *concept shift* (perubahan hubungan antara input dan output), secara signifikan menurunkan akurasi model pada data *out-of-domain* seperti dataset UNSW-NB15 saat dilatih pada CICIDS2017 [1]. Ketidakseimbangan kelas dan perbedaan struktur kolom antar dataset juga menjadi faktor penghambat generalisasi yang stabil [17].

### 3.3 Dampak pada Kepercayaan Model
Model yang mengalami kegagalan generalisasi sering kali menunjukkan *overconfidence* atau kepercayaan diri berlebih pada data yang sebenarnya asing bagi mereka. Diagnosis menunjukkan bahwa *confidence-based filtering* memiliki efektivitas yang terbatas pada data *out-of-domain*, yang berarti model mungkin memberikan prediksi yang salah namun dengan tingkat keyakinan yang tinggi [1].

## 4. Strategi Perbaikan dan Teknik Generalisasi

Setelah masalah didiagnosis, berbagai teknik dikembangkan untuk memperbaiki model dan meningkatkan kemampuannya dalam menghadapi variasi data lintas domain.

### 4.1 Pipeline Evaluasi Bebas Kebocoran (Leakage-Free)
Membangun *pipeline* yang benar-benar bebas kebocoran adalah langkah pertama yang krusial. Strategi ini mencakup penghitungan statistik penskalaan (*scaling*) hanya pada data latih (*fit on train only*) dan memastikan teknik seperti SMOTE hanya diterapkan pada data pelatihan untuk menghindari kebocoran informasi ke set uji [2], [16]. Penggunaan kerangka evaluasi yang sadar kebocoran (*leakage-aware*) dengan analisis transfer dua arah (*bidirectional transfer*) juga membantu dalam memvalidasi keandalan model [4].

### 4.2 Domain Adaptation dan Penyelarasan Distribusi
*Domain Adaptation* (DA) merupakan strategi populer untuk menjembatani kesenjangan distribusi antara dataset sumber dan target.
- **DANN dan MMD**: Penggunaan *Domain-Adversarial Neural Network* (DANN) dengan lapisan *Gradient Reversal* dan teknik *Maximum Mean Discrepancy* (MMD) membantu menyelaraskan ruang laten fitur lintas dataset heterogen [6], [8].
- **Residual Transfer Network (ResTN) dan MRAN**: Menggunakan arsitektur residual dan *Multi-Representation Adaptation Network* (MRAN) untuk memfasilitasi transfer pengetahuan lintas domain dengan menyelaraskan representasi ganda [21], [30].
- **Adversarial Domain Adaptation**: Memanfaatkan data berlabel dari domain sumber untuk meningkatkan performa pada domain target yang minim label, termasuk penggunaan teknik *multi-layer domain adaptation* untuk menstabilkan pelatihan [26], [27].
- **Transfer Pengetahuan Seimbang**: Pendekatan seperti *class-balanced knowledge transfer* dan *multi-structure domain alignment* membantu meningkatkan kemampuan generalisasi lintas dataset seperti UNSW-NB15 dan ToN-IoT [9].
- **Normalisasi dan Hierarki**: Teknik *reciprocal normalization* dan arsitektur *behavior-driven hierarchy* (BHM-IDS) juga diusulkan untuk menangani pergeseran data [20], [29].

### 4.3 Teknik Pemetaan Semantik dan Ekstraksi Fitur
Peningkatan generalisasi dapat dicapai melalui standardisasi fitur. Penggunaan set fitur umum berbasis NetFlow yang distandarisasi membantu model bekerja lebih konsisten lintas dataset [14]. Teknik *Semantic Feature Mapping* (SFM) dan penemuan semantik melalui klastering otomatis memungkinkan model untuk menangkap komponen intrinsik dari lalu lintas jaringan, sehingga lebih tahan terhadap ambiguitas data [15], [16]. Selain itu, penggunaan *Transformer encoders* untuk *global contextual learning* dan *Graph Neural Networks* (GNNs) untuk menangkap ketergantungan fitur telah terbukti efektif dalam menyelaraskan ruang fitur lintas dataset [7]. Strategi pemilihan fitur seperti *BPSO Feature Selection* dan penanganan ketidakseimbangan kelas melalui *Feature Selection and Minority Class Balancing* (FSCB-IDS) juga berkontribusi pada stabilitas model [4], [23].

### 4.4 Kalibrasi dan Robustness
Kalibrasi model melalui *Platt scaling* dapat digunakan untuk menyesuaikan probabilitas keluaran model, sehingga tingkat kepercayaan model lebih selaras dengan akurasi aktualnya pada data *out-of-domain* [1]. Optimasi metrik seperti AUC dan penggunaan model berkapasitas tinggi untuk abstraksi kelas serangan yang lebih baik juga merupakan strategi yang efektif untuk menghadapi serangan baru [12], [19]. Penggunaan kerangka kerja *hybrid deep learning* untuk deteksi anomali juga memperkuat pertahanan sistem [28]. Untuk meningkatkan ketahanan terhadap data bising, penggunaan *robust core-periphery constrained transformer* yang menambahkan gangguan pada ruang laten dapat membantu model tetap stabil [25]. Tinjauan komprehensif mengenai aplikasi *Deep Transfer Learning* menunjukkan bahwa integrasi teknik augmentasi data dan representasi semantik adalah kunci untuk meminimalkan disparitas domain [24].

## 5. Keterbatasan Bukti dan Celah Penelitian

Meskipun banyak kemajuan telah dicapai, literatur menunjukkan beberapa keterbatasan penting:
- **Ketergantungan pada Dataset Akademik**: Banyak studi masih sangat bergantung pada dataset seperti CICIDS2017, UNSW-NB15, dan NSL-KDD, yang mungkin memiliki artefak unik yang tidak mencerminkan lalu lintas jaringan nyata secara sempurna [18], [19].
- **Kinerja Jangka Panjang**: Penggunaan dataset progresif menunjukkan bahwa kinerja model dapat menurun seiring waktu, dan diperlukan evaluasi lebih lanjut terhadap ketahanan model terhadap serangan yang terus berevolusi secara temporal [17].
- **Kompleksitas Komputasi**: Teknik seperti Transformer dan GNN menawarkan performa tinggi namun memerlukan sumber daya komputasi yang besar, yang mungkin sulit diterapkan pada perangkat jaringan dengan sumber daya terbatas [7], [25].
- **Efektivitas XAI dalam Skala Besar**: Meskipun SHAP dan LIME berguna untuk diagnosis, mereka sering kali lambat secara komputasi saat diterapkan pada jutaan aliran data secara *real-time* [14].

## 6. Kesimpulan

Mendiagnosis dan memperbaiki kegagalan generalisasi pada NIDS memerlukan pendekatan holistik yang menggabungkan transparansi model dan integritas data. *Explainable AI* telah terbukti menjadi instrumen diagnostik yang sangat berharga untuk mengungkap bias dan mendeteksi dampak dari kebocoran data. Namun, diagnosis saja tidak cukup; penerapan *pipeline* yang bebas kebocoran dan teknik *domain adaptation* yang canggih sangat penting untuk membangun model yang robust. Strategi seperti pemetaan semantik fitur dan kalibrasi model menawarkan jalan menuju deteksi intrusi yang lebih dapat diandalkan lintas infrastruktur jaringan yang berbeda. Di masa depan, penelitian harus lebih fokus pada validasi menggunakan lalu lintas jaringan nyata dan pengembangan metode XAI yang lebih efisien secara komputasi guna memastikan keamanan siber yang tangguh dan berkelanjutan.

---
*> Laporan ini disusun berdasarkan analisis terhadap 30 sumber literatur mengenai deteksi intrusi jaringan dan kecerdasan buatan terjelaskan.*

## References

[1]V. K. Mandadi, “Explainable and Trustworthy Network Intrusion Detection: From Multi-Class SHAP Analysis to Confidence-Aware Deployment,” June 2026, doi: 10.5281/zenodo.20698543.

[2]U. Nwankwo, O. Nwokonkwo, C. Ikerionwu, U. F. Eze, and A. John-Otumu, “Explainable Sequence-Aware Deep Learning Framework for Potential Zero-Day Attack Detection and Cross-Domain Generalization in Enterprise Network Intrusion Detection,” Machine learning research, Sept. 2026, doi: 10.11648/j.mlr.20261102.13.

[3]J. L. V. Alonso and C. Pellicer, “Forensic-Oriented Intrusion Detection Using Synthetic Network Traffic Data and Explainable Artificial Intelligence,” July 2026, doi: 10.48550/arxiv.2607.00763.

[4]K. Ogaili and S. Jabbar, “A Leakage-aware Cross-dataset Evaluation Framework for IoT Intrusion Detection: BPSO Feature Selection, CORAL, and Bidirectional Transfer Analysis.”, [Online]. Available: https://openurl.ebsco.com/contentitem/gcd:197977800?sid=ebsco:plink:crawler-gcd&id=ebsco:gcd:197977800&crl=c&jrnl=2185310X

[5]A. U. Khan, “Leakage-Aware IDS Evaluation under Unseen Attacks and Cross-Dataset Shift,” pp. 416–421, July 2026, doi: 10.1109/iaict71158.2026.11620817.

[6]S. Layeghy, M. Baktash, and M. Portmann, “DI-NIDS: Domain Invariant Network Intrusion Detection System,” Knowledge Based Systems, vol. 273, pp. 110626–110626, Oct. 2022, doi: 10.1016/j.knosys.2023.110626.

[7]B. Pravallika, N. koushik Reddy, and T. Ishverya, “Cross-domain cybersecurity: an integrated intrusion detection framework using Deep learning and Cybersecurity,” pp. 1–6, Dec. 2025, doi: 10.1109/icecit67774.2025.11451008.

[8]M. U. Varghese and Z. Taghiyarrenani, “Intrusion Detection in Heterogeneous Networks with Domain-Adaptive Multi-Modal Learning,” arXiv.org, vol. abs/2508.03517, Aug. 2025, doi: 10.48550/arxiv.2508.03517.

[9]Q. Wang, X. Liu, Y. Cheng, Y. Cheng, and B. Zhang, “A domain adaptation network intrusion detection algorithm based on class-balanced knowledge transfer and multi-structure domain alignment”, [Online]. Available: https://link.springer.com/article/10.1007/s10586-026-06374-5

[10]S. Layeghy and M. Portmann, “On Generalisability of Machine Learning-based Network Intrusion Detection Systems,” Computers & Electrical Engineering, vol. abs/2205.04112, pp. 108692–108692, May 2022, doi: 10.1016/j.compeleceng.2023.108692.

[11]M. Cantone, C. Marrocco, and A. Bria, “On the Cross-Dataset Generalization of Machine Learning for Network   Intrusion Detection,” Feb. 2024, doi: 10.48550/arxiv.2402.10974.

[12]L. D’hooge, M. Verkerken, T. Wauters, F. D. Turck, and B. Volckaert, “Investigating Generalized Performance of Data-Constrained Supervised Machine Learning Models on Novel, Related Samples in Intrusion Detection,” Sensors, vol. 23, no. 4, pp. 1846–1846, Feb. 2023, doi: 10.3390/s23041846.

[13]M. Cantone, C. Marrocco, and A. Bria, “Machine Learning in Network Intrusion Detection: A Cross-Dataset Generalization Study,” IEEE Access, pp. 1–1, Jan. 2024, doi: 10.1109/access.2024.3472907.

[14]M. Sarhan, “Evaluating Standard Feature Sets Towards Increased Generalisability and Explainability of ML-Based Network Intrusion Detection,” Big Data Research, vol. 30, pp. 100359–100359, Nov. 2022, doi: 10.1016/j.bdr.2022.100359.

[15]W. Huang, Y. Sun, and R. Huang, “Cross-Dataset Semantic Discovery for Network Intrusion Detection Systems,” pp. 986–990, Apr. 2026, doi: 10.1109/icccs69761.2026.11613514.

[16]H. Y. Martono, I. Syarif, and F. A. Saputra, “Cross-Dataset Generalization of ML-based Network Intrusion Detection via Semantic Feature Mapping and Few-Shot Adaptation, Validated on Real Cloud Traffic”.

[17]T. Chua and I. Salam, “Evaluation of Machine Learning Algorithms in Network-Based Intrusion Detection Using Progressive Dataset,” Symmetry, vol. 15, no. 6, pp. 1251–1251, June 2023, doi: 10.3390/sym15061251.

[18]B. Shannaq, “An AI benchmark selection framework for sustainable cybersecurity: Comparative characterization of CIC-IDS2017, UNSW-NB15, and IoT-23”, [Online]. Available: https://glowfinitybd.com/journal/index.php/BJMSR/article/view/2929

[19]C. Xin and K. Xu, “Cross-Dataset Transformer-IDS with Calibration and AUC Optimization (Evaluated on NSL-KDD, UNSW-NB15, CIC-IDS2017).”, [Online]. Available: https://openurl.ebsco.com/contentitem/gcd:193600133?sid=ebsco:plink:crawler-gcd&id=ebsco:gcd:193600133&crl=c&jrnl=25790072

[20]M. Zekiouk, M. B. Lehocine, and Y. Bouzeraa, “BHM-IDS: Behavior-Driven Hierarchy and Multi-Dataset Training for Cross-Dataset Generalization”, [Online]. Available: https://www.mdpi.com/2076-3417/16/16/7885

[21]W. Huang, Y. Wang, and Z. Wang, “ResTN: Residual Transfer Network for Cross Domain Network Intrusion Detection,” May 2025, doi: 10.1109/icsp65755.2025.11086791.

[22]“Discovering Non-Metadata Contaminant Features in Intrusion Detection Datasets,” Aug. 2022, doi: 10.1109/pst55820.2022.9851974.

[23]A. Guezzaz, S. Benkirane, M. Azrour, S. B. A. Khattak, H. Farman, and M. M. Nasralla, “FSCB-IDS: Feature Selection and Minority Class Balancing for Attacks Detection in VANETs,” Applied Sciences, vol. 13, no. 13, pp. 7488–7488, June 2023, doi: 10.3390/app13137488.

[24]H. Kheddar, Y. Himeur, and A. I. Awad, “Deep Transfer Learning Applications in Intrusion Detection Systems: A Comprehensive Review,” arXiv.org, vol. abs/2304.10550, Apr. 2023, doi: 10.48550/arXiv.2304.10550.

[25]X. Yu, Z. Zhang, D. Zhu, and T. Liu, “Robust Core-Periphery Constrained Transformer for Domain Adaptation,” Aug. 25, 2023. [Online]. Available: https://arxiv.org/abs/2308.13515v5

[26]O. Ciga, J. Chen, and A. Martel, “Multi-layer Domain Adaptation for Deep Convolutional Networks,” Sept. 05, 2019. [Online]. Available: https://arxiv.org/abs/1909.02620v1

[27]B. Xu, M. Mohtarami, and J. Glass, “Adversarial Domain Adaptation for Stance Detection,” Feb. 06, 2019. [Online]. Available: https://arxiv.org/abs/1902.02401v1

[28]R. Kale, Z. Lu, K. W. Fok, and V. L. L. Thing, “A Hybrid Deep Learning Anomaly Detection Framework for Intrusion Detection,” Dec. 02, 2022. doi: 10.1109/BigDataSecurityHPSCIDS54978.2022.00034.

[29]Z. Huang et al., “Reciprocal Normalization for Domain Adaptation,” Dec. 20, 2021. [Online]. Available: https://arxiv.org/abs/2112.10474v1

[30]Y. Zhu et al., “Multi-Representation Adaptation Network for Cross-domain Image Classification,” Jan. 04, 2022. doi: 10.1016/j.neunet.2019.07.010.