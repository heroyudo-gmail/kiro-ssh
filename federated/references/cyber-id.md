# REVIU AKADEMIK KRITIS JURNAL: CYBER-RESILIENT DIGITAL TWIN ARCHITECTURES FOR SMART GRIDS

**Judul Artikel:** *Cyber-Resilient Digital Twin Architectures for Smart Grids: A Review of Attack Modeling, Detection, Mitigation, and Secure Control Strategies*  
**Penulis:** Osasumwen Cedric Ogiesoba-Eguakun dan Suman Rath  
**Afiliasi:** Department of Electrical and Computer Engineering, The University of Tulsa, Tulsa, OK, USA  
**Publikasi:** *MDPI Electronics*, Vol. 15, No. 20, Artikel 4701 (Oktober 2026)  
**DOI:** 10.3390/electronics15204701  
**Peran Reviewer:** Guru Besar / Peer Reviewer Senior Bidang Keamanan Sistem Siber-Fisik (*Cyber-Physical Systems Security*)

---

## REKAPITULASI EVALUASI EKSEKUTIF

Artikel ini menyajikan survei sistematis dan sintesis kritis yang sangat komprehensif mengenai penerapan arsitektur *Digital Twin* yang tangguh siber (*Cyber-Resilient Digital Twin* / CRDT) pada jaringan listrik pintar (*smart grid*). Berdasarkan metode tinjauan terstruktur PRISMA 2020 terhadap **1.627 artikel** dari basis data Scopus, IEEE Xplore, dan ACM Digital Library, penulis mengkritisi **149 publikasi terpilih** dan menyusun taksonomi terpadu yang menghubungkan pemodelan serangan multi-lapisan, deteksi cerdas (fisika, ML, DL, GNN, FL), pertahanan proaktif (MTD, deceptions), kontrol selamat/terisolasi mandiri (*self-healing control*), hingga kesiapan validasi *Hardware-in-the-Loop* (HIL).

Berikut adalah analisis dan reviu akademis mendalam yang mencakup 9 aspek utama permintaan reviu:

---

## 1. FORMULASI MASALAH (PROBLEM FORMULATION)

Digitalisasi infrastruktur energi kritis melalui penggelaran *Advanced Metering Infrastructure* (AMI), *Phasor Measurement Units* (PMU), *Supervisory Control and Data Acquisition* (SCADA), sensor IoT, dan pengontrol terdistribusi telah memperluas permukaan serangan siber (*cyberattack surface*) secara drastis [1-3]. 

Masalah utama yang dirumuskan dalam paper ini mencakup tiga tingkatan:
1. **Kerentanan Kompleks pada Komponen Terintegrasi:** Berbeda dengan sistem TI konvensional yang berfokus pada kerahasiaan data (*confidentiality*), serangan pada CPS/smart grid berdampak langsung pada dinamika fisik jaringan (stabilitas tegangan, frekuensi, dan pasokan daya) [1, 4]. Serangan seperti *False Data Injection* (FDI), *Denial-of-Service* (DoS), *Replay Attack*, dan *Advanced Persistent Threats* (APTs), serta ancaman berorientasi AI (GenAI/LLM), mampu memanipulasi pengukuran sensor dan perintah kontrol tanpa terdeteksi oleh alarm konvensional [4, 6].
2. **Keterbatasan Alat Simulasi Tradisional:** Simulasi grid tradisional bersifat statis dan beroperasi secara *offline* berdasarkan skenario pra-definisi. Alat ini tidak memiliki sinkronisasi berkelanjutan (*continuous synchronization*) dengan aset fisik dunia nyata serta tidak mampu merespons serangan dinamis yang beradaptasi secara *real-time* berdasarkan umpan balik sistem [10, 11].
3. **Fragmentasi Literatur Keamanan Digital Twin:** Meskipun *Digital Twin* (DT) dipandang sebagai solusi menjanjikan untuk menjembatani ruang siber dan fisik, penelitian yang ada saat ini terfragmentasi secara terisolasi (*siloed*)—hanya berfokus pada salah satu elemen seperti arsitektur DT saja, deteksi anomaly AI saja, atau skenario serangan tertentu, tanpa adanya kerangka kerja terintegrasi yang menghubungkan seluruh siklus hidup resiliensi siber (*cyber-resilience lifecycle*) [8, 9].

---

## 2. SOLUSI YANG ADA SAAT INI (EXISTING SOLUTIONS)

Dalam literatur yang disurvei, solusi pertahanan keamanan smart grid berbasis DT dan siber-fisik dapat dikategorikan ke dalam beberapa pendekatan utama:

1. **Deteksi Berbasis Fisika (Physics-Based Detection):** Memanfaatkan hukum fisika (hukum Kirchhoff dan keseimbangan daya) serta estimasi status (*state estimation residual analysis* $r = z - H\hat{x}$) untuk mengidentifikasi anomali [4, 48, 49].
2. **Klasifikasi Machine Learning (ML) Konvensional:** Menggunakan algoritma terawasi seperti *Support Vector Machine* (SVM), *Decision Trees*, *Random Forest* (RF), dan *k-NN* untuk mengklasifikasikan pola data sensor [6, 63].
3. **Deep Learning (DL) dan Arsitektur Kompleks:** Menggunakan *Convolutional Neural Networks* (CNN) untuk mengekstraksi korelasi spasial antar pengukuran, *Recurrent Neural Networks* (RNN/LSTM) untuk mendeteksi urutan temporal serangan (seperti *replay attack*), serta model *Transformer* (berbasis *self-attention*) untuk pemrosesan pengukuran terdistribusi [6, 26, 60].
4. **Graph Neural Networks (GNN):** Memodelkan topologi fisik dan komunikasi smart grid sebagai grafik $G=(V,E)$ guna mengidentifikasi dan melokalisasi serangan FDI yang terselubung (*stealth attacks*) [61].
5. **Federated Learning (FL):** Memungkinkan pelatihan model AI secara terdesentralisasi antar-substasiun atau entitas grid tanpa membagikan data operasional mentah, guna menjaga privasi lokasi data [13, 30].
6. **Pertahanan Proaktif (Moving Target Defense / MTD & Cyber-Deception):** MTD merubah konfigurasi jaringan atau parameter kontrol secara dinamis untuk mengacaukan pemetaan penyerang [14], sedangkan *cyber-deception* (honeypot/decoy) mengarahkan penyerang ke replika virtual terisolasi [33].
7. **Kontrol Selamat & Berdaya Tahan (Resilient Control & Self-Healing):** Penggunaan *Model Predictive Control* (MPC), *Reinforcement Learning* (RL), dan logika *self-healing* untuk mengisolasi perangkat terkompromi dan memulihkan operasi normal [5, 34, 74].

---

## 3. TINJAUAN PUSTAKA TERKAIT (RELATED WORKS)

Penulis mengidentifikasi dan membandingkan secara eksplisit 11 makalah tinjauan pustaka (*review/survey papers*) utama yang terbit antara tahun 2023 hingga 2026. Tabel komparatif dalam paper menunjukkan pemetaan cakupan ruang lingkup terkait:

* **Achuthan et al. (2025):** Menganalisis hubungan teknologi DT dan keamanan siber secara lintas domain (bukan spesifik jaringan listrik) menggunakan analisis *BERTopic* pada 300 publikasi [8].
* **Canaan et al. (2025):** Tinjauan keamanan siber pada *microgrid* berbasis DT, tetapi tidak menyajikan prosedur pencarian pustaka terstruktur [9].
* **Barreto & Aoki (2025):** Tinjauan *State-of-the-Art* berbasis ProKnow-C pada 74 publikasi yang berfokus pada aplikasi dan metode simulasi DT [18].
* **Jørgensen & Ma (2025, 2026):** Tinjauan pemetaan PRISMA-ScR mengenai lansekap ancaman dan regulasi DT listrik di Uni Eropa [2, 22].
* **Lakhal et al. (2025):** Tinjauan terstruktur ancaman OT dan pertahanan AI pada 940 publikasi Scopus [17].
* **Amulya et al. (2024):** Tinjauan kerangka kerja asesmen kerentanan kontrol frekuensi beban (*load-frequency control*), tetapi tidak berpusat pada arsitektur DT terintegrasi [19].
* **Sifat et al. (2023), Sahoo et al. (2025), Pilakkat et al. (2026):** Meninjau otomasi, kontrol prediktif, dan integrasi PV pada *smart microgrid* berbasis DT [20, 21, 23].

---

## 4. KELEMAHAN SOLUSI DAN TINJAUAN PUSTAKA SAAT INI (DRAWBACKS OF EXISTING SOLUTIONS & RELATED WORKS)

### A. Kelemahan Solusi Teknis yang Ada:
* **Deteksi Berbasis Fisika:** Sangat sensitif terhadap kesalahan model (*model mismatch*), perubahan topologi jaringan, serta penundaan sinkronisasi. Gagal mendeteksi serangan FDI yang dirancang khusus presisi (*stealthy FDIA* $a=Hc$) [32, 48].
* **ML/DL Konvensional:** Berisiko tinggi mengalami *overfitting* pada skenario pelatihan, bertindak sebagai *black-box* yang sulit diinterpretasikan (*low interpretability*), memicu alarm palsu (*false alarms*) saat terjadi fluktuasi beban/Pembangkit EBT sah, serta membutuhkan daya komputasi tinggi yang membebani perangkat *edge* [6, 56].
* **Federated Learning (FL):** Rentan terhadap serangan racun data (*poisoning/backdoor attacks*) dari klien jahat, mengalami *overhead* komunikasi yang tinggi, dan sensitif terhadap ketidakseimbangan data (*non-IID data*) [30, 39].
* **Moving Target Defense (MTD):** Reorganisasi topologi atau parameter yang terlalu sering dapat memicu ransien operasional (*transients*) yang mengganggu kestabilan fisik grid [14].
* **Kelemahan Validasi:** Sebagian besar solusi hanya diuji melalui simulasi komputer *offline* tanpa bukti pengujian *Hardware-in-the-Loop* (HIL) atau skala lapangan (*field deployment*) [3, 15].

### B. Kelemahan Paper Tinjauan Pustaka Sebelumnya:
* **Ruang Lingkup Terbatas & Terpisah:** Tidak ada tinjauan sebelumnya yang mencakup secara penuh seluruh rantai resiliensi siber (Arsitektur DT, Pemodelan Serangan, Deteksi, Mitigasi, Kontrol Selamat, Validasi HIL, hingga ancaman GenAI dan kriptografi pasca-kuantum / PQC) [8, 9, 18].
* **Rendahnya Rigoritas Metodologis:** Banyak survei terdahulu yang tidak melaporkan prosedur pencarian basis data yang dapat direproduksi (*reproducible*), tidak menetapkan kriteria inklusi/eksklusi formal, serta mengabaikan penilaian kualitas (*quality appraisal*) terhadap artikel yang ditinjau [9, 16, 20].

---

## 5. MOTIVASI DAN IDE YANG DIUSULKAN (MOTIVATION AND PROPOSED IDEA)

### Motivasi:
Keamanan smart grid tidak lagi memadai jika hanya mengandalkan deteksi serangan pasif. Diperlukan paradigma pertahanan berbasis **Cyber-Resilient Digital Twin (CRDT)** yang menggabungkan pengamatan spasial-temporal siber-fisik, sinkronisasi dua arah (*bidirectional coupling*), dan kemampuan eksekusi kontrol mandiri untuk menjamin kelangsungan operasi jaringan listrik di bawah serangan yang sedang berlangsung.

### Ide yang Diusulkan (Proposed Idea):
Penulis mengusulkan **Kerangka Kerja & Arsitektur Referensi Cyber-Resilient Digital Twin (CRDT)** terpadu untuk smart grid melalui tinjauan metodologis multi-database terstruktur. 

Ide utama artikel ini meliputi:
1. **Pendekatan Metodologi PRISMA 2020 & QAC:** Menyaring 1.627 publikasi dari Scopus, IEEE Xplore, dan ACM Digital Library menjadi 149 studi berkualitas yang dievaluasi menggunakan *Quality Appraisal Checklist* (QAC) 8-item.
2. **Arsitektur Referensi CRDT 4-Domain:** Mengintegrasikan 4 lapisan fungsional ( Physical Grid, Communication & Data, DT Intelligence, Resilient & Secure Control) yang dihubungkan oleh 4 antarmuka fisik-virtual (I1–I4) serta jalur umpan balik (*closed-loop feedback*).
3. **Peta Jalan Validasi Multidimensi:** Memetakan transisi teknologi dari simulasi *offline*, simulasi *real-time*, HIL (Controller-HIL & Power-HIL), hingga penggelaran skala utilitas (*utility-scale deployment*).

---

## 6. KEBARUAN DAN KONTRIBUSI UTAMA (NOVELTY AND CONTRIBUTIONS)

### Kebaruan (Novelty):
Kebaruan utama paper ini **bukan** terletak pada pengenalan istilah *Digital Twin* atau *cybersecurity* secara terpisah, melainkan pada **unifikasi holistik seluruh siklus hidup resiliensi siber smart grid dalam satu kerangka kerja arsitektur CRDT**. Paper ini merupakan literatur pertama yang secara eksplisit menghubungkan sinkronisasi siber-fisik, deteksi berbasis AI/Fisika, privasi terdistribusi, kontrol selamat bermuatan keselamatan (*safety-constrained self-healing*), ancaman GenAI/LLM, serta kriptografi pasca-kuantum (PQC).

### Kontribusi Utama (Key Contributions):
1. **Taksonomi & Taksonomi Antarmuka Komprehensif:** Menyusun taksonomi 5 permukaan serangan (pengukuran, komunikasi, kontrol, perangkat, dan ancaman AI terkoordinasi) serta mendefinisikan 4 antarmuka kunci (I1–I4) beserta paparan risiko dan mekanisme *fallback*-nya.
2. **Tinjauan Metodologis Berulang (Reproducible Review):** Menerapkan 8-item *Quality Appraisal Checklist* (QAC) untuk mengevaluasi 149 artikel secara objektif (33,6% *high quality*, 45,6% *moderate quality*, 20,8% *low quality*).
3. **Sintesis Komparatif Standar:** Menyajikan tabel perbandingan teknis seragam yang membandingkan performa deteksi, rasio alarm palsu, latensi, skalabilitas, dan beban komputasi di antara 7 keluarga strategi pertahanan.
4. **Peta Jalan Riset & Transisi Validasi:** Mengidentifikasi 6 hambatan utama penggelaran industri dan merumuskan alur pengembangan riset dari simulasi virtual menuju penggelaran skala utilitas nyata.

---

## 7. MEKANISME IDE YANG DIUSULKAN (PROPOSED IDEA MECHANISM)

### A. Mekanisme Penelusuran dan Evaluasi Literatur:
* **Penelusuran Multi-Database:** Menggunakan kueri 3-blok konsep (Digital Twin AND Smart Grid AND Cybersecurity) pada basis data Scopus (381 rekaman), IEEE Xplore (533 rekaman), dan ACM DL (713 rekaman), menghasilkan 1.627 rekaman.
* **Penyaringan PRISMA:** Menghapus 174 duplikat dan 507 dokumen non-studi -> menyaring 946 judul/abstrak -> mengevaluasi 164 abstrak/metadata terperinci -> menetapkan **149 publikasi akhir**.
* **Penilaian Kualitas QAC (Q1–Q8):** Menilai kejelasan sinkronisasi DT, model ancaman, ketersediaan dataset, reproduksibilitas, pembanding *baseline*, pelaporan metrik, lingkungan validasi, dan pembahasan keterbatasan.

### B. Mekanisme Kerja Arsitektur Referensi CRDT:
Arsitektur CRDT bekerja melalui sistem umpan balik tertutup (*closed-loop execution*):
1. **Sensori & Komunikasi (I1 & I2):** Data fisik (tegangan, arus, status breaker dari PMU/IED) ditransmisikan melalui protokol IEC 61850/DNP3/MQTT ke lapisan *DT Intelligence* secara *real-time*.
2. **Kecerdasan DT (DT Intelligence Domain):** Melakukan estimasi status ter-sinkronisasi, cross-validasi siber-fisik, deteksi serangan (melalui Fisika/AI/GNN), dan penilaian dampak fisik.
3. **Kontrol Selamat & Berdaya Tahan (I3 & I4):** Mengirimkan skor keyakinan anomali ke lapisan *Resilient Control*. Algoritma seperti MPC atau RL menyusun perintah mitigasi (isolasi perangkat terkompromi, rekonfigurasi inverter, atau penyesuaian *setpoint*) dengan memperhitungkan batasan keselamatan (*safety constraints*).
4. **Umpan Balik & Resinkronisasi:** Pengukuran pasca-mitigasi dikirimkan kembali ke DT untuk memverifikasi efektivitas mitigasi dan melakukan resinkronisasi model virtual.

---

## 8. KEUNGGULAN DAN MANFAAT (MERIT AND ADVANTAGES)

1. **Definisi Kualifikasi CRDT yang Tegas:** Menjelaskan bahwa keberadaan model virtual saja tidak cukup; syarat mutlak CRDT adalah **sinkronisasi dua arah (*bidirectional coupling*) yang dilengkapi fungsi resiliensi siber eksplisit**.
2. **Pertahanan Berlapis (*Defence-in-Depth*):** Menghubungkan deteksi pasif dengan pertahanan proaktif (MTD dan *Deception*) serta kontrol otomatis (*Self-Healing*), sehingga memperkecil celah eksploitasi peretas.
3. **Perlindungan Privasi Kolaboratif:** Mengintegrasikan *Federated Learning* (FL), *Differential Privacy* (DP), dan *Secure Multiparty Computation* (SMPC) untuk memungkinkan kerja sama antar-utilitas tanpa membocorkan data sensitif konsumen.
4. **Metrik Evaluasi Resiliensi Fisik:** Mendorong penggunaan metrik resiliensi fisik—seperti *Stability Preservation Index* ($SI = x_{\text{attack}} / x_{\text{normal}}$), Waktu Pemulihan ($T_R$), dan Integrator Kinerja ($R$)—bukan sekadar akurasi deteksi AI di atas kertas.

---

## 9. MASALAH DAN KETERBATASAN YANG MASIH ADA (REMAINING PROBLEMS AND LIMITATIONS)

### A. Keterbatasan Metodologi Tinjauan Pustaka:
1. **Cakupan Basis Data:** Basis data Web of Science tidak dapat diakses karena keterbatasan langganan institusional penulis; literatur non-Bahasa Inggris mungkin belum terwakili secara penuh.
2. **Tahap Penyaringan:** Penentuan kelayakan akhir didasarkan pada penilaian abstrak dan metadata terperinci, bukan penelaahan teks penuh (*full-text screening*).

### B. Masalah & Tantangan Penelitian Lapangan yang Belum Terjawab (*Open Research Gaps*):
1. **Inkonsistensi Terminologi & Lack of Benchmarks:** Ketidakseragaman definisi *Digital Twin* dan ketiadaan dataset *benchmark* terstandar yang mencakup gabungan telemetry siber dan dinamika fisik berakurasi tinggi.
2. **Tantangan Sinkronisasi Real-Time & Data Poisoning:** Risiko kompromi pada DT itu sendiri (*DT poisoning attack*), di mana penyerang sengaja menyuntikkan data palsu untuk meracuni proses pembaruan model DT.
3. **Skalabilitas Komputasi:** Kesulitan menjaga sinkronisasi *real-time* ketika arsitektur DT diperluas dari skala *microgrid* laboratorium menuju skala utilitas jaringan transmisi/distribusi raksasa.
4. **Ketiadaan Jaminan Keselamatan Formal (Formal Safety Assurance):** Penggunaan AI/RL untuk mitigasi otomatis masih berisiko memicu tindakan kontrol yang salah jika terjadi kesalahan klasifikasi (*false positive*). Diperlukan integrasi verifikasi formal (*Lyapunov stability*, *Control Barrier Functions*).
5. **Kesenjangan Validasi (Validation Gap):** Mayoritas besar studi (>70%) masih tertahan di tahap simulasi *offline*. Masih sangat sedikit pengujian yang memvalidasi resiliensi CRDT pada platform *Hardware-in-the-Loop* (HIL) atau penggelaran uji coba lapangan (*field pilot deployment*).

---

## KESIMPULAN REVIEWER

Paper karya Ogiesoba-Eguakun dan Rath (2026) ini merupakan **pencapaian akademis yang sangat berharga dan menjadi rujukan utama (*landmark review*)** dalam bidang keamanan sistem siber-fisik dan smart grid. Penulis berhasil menggeser fokus riset dari sekadar "mengembangkan algoritma deteksi AI yang lebih rumit" menjadi "bagaimana membangun arsitektur sinkronisasi terpadu yang aman, terverifikasi, dan tervalidasi secara HIL". Paper ini sangat direkomendasikan untuk menjadi panduan riset tingkat magister/doktoral serta acuan pengambil kebijakan dalam merancang infrastruktur energi masa depan yang tangguh siber.
