<!-- ============================================================
PAPER 4 - XAI untuk NIDS (versi kerangka / draft Bahasa Indonesia)
Format & urutan mengikuti jurnal JICTRA.
STATUS: KERANGKA. Semua angka bertanda [ISI] diisi dari hasil eksperimen
        notebook di folder `notebook_xai/` (jangan dikarang).
Prinsip: tanpa Semantic Feature Mapping (SFM). Semua angka harus jujur
        dari eksperimen nyata.
Dataset: CIC-IDS2017 (referensi/latih) -> CSE-CIC-IDS2018 (target transfer),
        keduanya CICFlowMeter. Arah utama 2017 -> 2018 (replikasi langsung paper
        referensi JTIIK); arah balik 2018 -> 2017 dihitung sebagai penguat.
Komputasi: seluruh notebook dieksekusi di AWS SageMaker (lihat notebook_xai/ & aws_xai/).
============================================================ -->

# Explainable AI untuk Network Intrusion Detection System: Diagnosis dan Pemulihan Kegagalan Generalisasi Lintas-Dataset pada Pipeline Bebas-Kebocoran

> Catatan draft: judul dapat diringkas. Alternatif:
> "Mengurai Kegagalan Generalisasi NIDS Lintas-Dataset: Pipeline Bebas-Kebocoran,
> Kalibrasi Ambang, dan Interpretasi SHAP yang Sadar-Kondisi".

**Penulis Pertama¹, Penulis Kedua², Penulis Ketiga³**
¹²³ Departemen Teknik Informatika dan Komputer, Politeknik Elektronika Negeri Surabaya (PENS), Surabaya, Indonesia
Email: penulis1@pens.ac.id; penulis2@pens.ac.id; penulis3@pens.ac.id
*Penulis Korespondensi

---

## Abstrak

<!-- Target JICTRA: 100-200 kata, satu paragraf, Bahasa Indonesia. -->

Sistem deteksi intrusi jaringan (NIDS) berbasis pembelajaran mesin kerap menunjukkan
performa nyaris sempurna pada evaluasi within-dataset, namun runtuh ketika diuji pada
dataset dengan distribusi dan komposisi serangan berbeda. Penelitian ini menyajikan
diagnosis dan pemulihan kegagalan generalisasi lintas-dataset menggunakan pipeline
bebas-kebocoran pada CIC-IDS2017 sebagai dataset referensi dan CSE-CIC-IDS2018 sebagai
dataset target, keduanya diekstraksi dengan CICFlowMeter. Dua model dibandingkan, XGBoost
dan Random Forest, dilatih hanya pada data referensi lalu ditransfer ke target tanpa
pelatihan ulang. Pada evaluasi within-dataset, model mencapai F1 [ISI], MCC [ISI], dan
AUC-ROC [ISI]. Pada evaluasi
lintas-dataset, MCC turun menjadi [ISI] walau weighted-F1 tetap tinggi [ISI], yang
menunjukkan bahwa weighted-F1 dan akurasi menyesatkan pada data tidak seimbang. Berbeda
dengan studi terdahulu yang berhenti pada diagnosis, penelitian ini (i) memisahkan
kegagalan ranking dari kegagalan ambang melalui kalibrasi ambang dan PR-AUC, serta
(ii) memulihkan deteksi melalui kalibrasi few-shot minimal sehingga MCC naik menjadi
[ISI]. Analisis SHAP ditafsirkan secara sadar-kondisi: interpretasi pada model yang gagal
berbeda makna dengan model yang telah pulih. Temuan menegaskan pentingnya pelaporan MCC,
recall per-kelas, kalibrasi ambang, dan validasi lintas-dataset.

**Kata kunci:** explainable AI; deteksi intrusi jaringan; generalisasi lintas-dataset;
kalibrasi ambang; SHAP; MCC.

---

## Abstract

<!-- Versi Inggris dari abstrak, isi menyusul setelah versi Indonesia final. -->

*[ISI: terjemahan abstrak setelah versi Indonesia difinalkan.]*

**Keywords:** explainable AI; network intrusion detection; cross-dataset generalization;
threshold calibration; SHAP; MCC.

---

## 1. Pendahuluan

<!-- Isi: latar belakang, gap, kontribusi. Gaya sitasi JICTRA: nama-tahun. -->

Transformasi digital memperluas permukaan serangan jaringan dan meningkatkan kebutuhan
terhadap NIDS yang andal. Pendekatan pembelajaran mesin banyak dipakai karena mampu
mempelajari pola trafik dari dataset benchmark seperti CIC-IDS2017 dan CSE-CIC-IDS2018.
Namun, performa tinggi pada evaluasi within-dataset tidak menjamin keandalan operasional
pada lingkungan yang berbeda (D'hooge dkk., 2020; Cantone dkk., 2024).

Dua persoalan metodologis menonjol. **Pertama, kebocoran data (data leakage)** muncul bila
seleksi fitur, standardisasi, atau oversampling dilakukan sebelum pemisahan latih-uji,
menghasilkan estimasi performa yang terlalu optimistis. **Kedua, kesesuaian skema fitur
tidak menjamin kesesuaian distribusi**: meskipun nama dan jumlah fitur cocok (karena alat
ekstraksi sama, yaitu CICFlowMeter), nilai statistik fitur dapat berbeda akibat perbedaan
komposisi serangan dan kondisi perekaman.

Studi terdahulu (lih. manuskrip referensi XAI-IDS) telah menunjukkan fenomena runtuhnya
MCC pada evaluasi lintas-dataset, tetapi memiliki tiga keterbatasan yang menjadi celah
penelitian ini:
1. **Berhenti pada diagnosis** — menyatakan model gagal tanpa menawarkan pemulihan.
2. **Mencampur dua jenis kegagalan** — menafsirkan MCC = 0 murni sebagai pergeseran
   distribusi, padahal AUC yang bervariasi mengindikasikan sebagian adalah masalah
   kalibrasi ambang.
3. **Interpretasi SHAP tanpa konteks kondisi model** — menghitung SHAP pada model yang
   recall serangannya nol, sehingga interpretasinya rapuh.

**Kontribusi penelitian ini:**
1. Merancang pipeline bebas-kebocoran untuk eksperimen IDS biner lintas-dataset
   CIC-IDS2017 → CSE-CIC-IDS2018 (dan sebaliknya) tanpa pemetaan fitur semantik.
2. Memisahkan **kegagalan ranking** (diukur AUC/PR-AUC) dari **kegagalan ambang**
   (diukur MCC pada ambang 0,5) dan menerapkan kalibrasi ambang.
3. **Memulihkan** deteksi melalui kalibrasi few-shot minimal, dilaporkan dengan
   multi-seed dan interval kepercayaan.
4. **Membandingkan XGBoost dan Random Forest** pada protokol identik untuk menguji apakah
   fenomena kegagalan dan pola pemulihan bersifat umum lintas-algoritma.
5. Menafsirkan SHAP secara **sadar-kondisi**: membandingkan interpretasi pada model gagal
   versus model pulih, untuk kedua model.

<!-- TODO: lengkapi sitasi dasar: Sharafaldin dkk. 2018 (CIC-IDS2017 & CSE-CIC-IDS2018),
     Lundberg & Lee 2017 (SHAP), Chen & Guestrin 2016 (XGBoost), Breiman 2001 (RF),
     Chawla dkk. 2002 (SMOTE), Chicco & Jurman 2020 (MCC). -->

---

## 2. Metode Penelitian

### 2.1 Dataset dan Ruang Lingkup Eksperimen

Eksperimen menggunakan dua dataset benchmark yang keduanya diekstraksi dengan CICFlowMeter:
- **CIC-IDS2017** — dataset referensi (latih). Serangan campuran (brute force, DoS, DDoS,
  web attack, infiltrasi, botnet, port scan).
- **CSE-CIC-IDS2018** — dataset target lintas. Komposisi serangan dan kondisi perekaman
  berbeda dari 2017 meskipun alat ekstraksi fitur sama (CICFlowMeter).

Pemilihan pasangan 2017 → 2018 mengikuti protokol paper referensi sehingga perbandingan
bersifat apple-to-apple. Seluruh label dipetakan ke skema biner: Benign/Normal = 0,
Attack = 1. Untuk mengendalikan beban komputasi, tiap dataset diproses dengan stratified
subsampling [ISI: maks baris per file]. Ringkasan data setelah pembersihan dan pembagian
pada Tabel 1.

**Tabel 1. Ringkasan dataset setelah pra-pemrosesan dan subsampling**

| Dataset | Raw Rows | Sampled | Train | Test | Fitur | %Attack |
|---|---|---|---|---|---|---|
| CIC-IDS2017 (ref) | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |
| CSE-CIC-IDS2018 (target) | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |

### 2.2 Pipeline Bebas-Kebocoran

Seluruh operasi fitting hanya menggunakan data latih. Urutan pemrosesan:
1. **Normalisasi kolom dan label** — pembersihan whitespace/BOM pada nama kolom,
   penyeragaman nama antar rilis CICFlowMeter, normalisasi label (mis. hapus prefiks
   `DrDoS_`, kapitalisasi seragam), pemetaan ke biner.
2. **Pembersihan data** — buang kolom metadata (IP, port, protocol, timestamp, flow id),
   hapus duplikasi, ubah nilai tak hingga menjadi NaN, buang kolom missing dominan, isi
   sisa missing numerik dengan median (statistik median dari **train**).
3. **Penyelarasan skema fitur (tanpa SFM)** — ambil **irisan nama kolom** antara kedua
   dataset setelah normalisasi; tidak ada pemetaan semantik manual, tidak ada pengisian-nol
   untuk fitur yang tak ada. (Varian pengisian-nol diuji sebagai ablation, lihat 3.x.)
4. **Pembagian data** — stratified split 80% latih / 20% uji.
5. **Seleksi fitur, standardisasi, SMOTE — hanya pada data latih.** Seleksi fitur top-k
   dari importance model di data latih; StandardScaler fit di latih; SMOTE hanya di latih.

Pada evaluasi lintas-dataset, model, scaler, dan daftar fitur hasil seleksi dari referensi
(CIC-IDS2017) dipakai langsung pada target (CSE-CIC-IDS2018). Evaluasi mengukur kemampuan
**transfer**, bukan adaptasi ulang.

Seluruh notebook eksperimen (`notebook_xai/01–03`) dieksekusi di **AWS SageMaker**: dataset
mentah di-sync dari S3, notebook dijalankan berurutan, dan artefak hasil (JSON) di-upload
kembali ke S3 untuk mengisi tabel-tabel pada bagian Hasil.

### 2.3 Model Klasifikasi

Dua model dievaluasi dan **dibandingkan**: **XGBoost** (depth=8, lr=0,1, n_estimators=200,
subsample=0,8, colsample_bytree=0,8) dan **Random Forest** (n_estimators=200). Random Forest
dipilih agar sejajar dengan paper referensi, sedangkan XGBoost mewakili gradient boosting
yang umum pada IDS modern. Keduanya dijalankan pada pipeline leak-free identik dan protokol
evaluasi yang sama, sehingga perbandingannya adil. Detail lengkap di notebook `notebook_xai/`.

### 2.4 Metrik Evaluasi

Metrik: accuracy, precision, recall (per-kelas), weighted F1, AUC-ROC, **PR-AUC**, dan
**MCC**. MCC diprioritaskan pada evaluasi lintas-dataset karena memperhitungkan TP/TN/FP/FN
secara simultan dan tetap informatif pada data tidak seimbang (Chicco & Jurman, 2020).
Untuk memisahkan kegagalan ranking dari kegagalan ambang, dilaporkan **AUC/PR-AUC**
(independen ambang) bersama **MCC dan recall Attack pada ambang 0,5 dan ambang terkalibrasi**.

### 2.5 Kalibrasi Ambang dan Pemulihan Few-Shot

- **Kalibrasi ambang**: ambang keputusan dipilih ulang pada target (mis. maksimasi MCC /
  Youden's J pada subset kecil), untuk menguji apakah "kegagalan" sebagian hanya artefak
  ambang 0,5.
- **Pemulihan few-shot**: tambahkan fraksi kecil label target [ISI: 0; 1%; 5%; 10%] ke
  pelatihan lalu ukur kenaikan MCC & recall Attack.

### 2.6 Explainability dengan SHAP

SHAP (TreeSHAP untuk model berbasis pohon) dipakai untuk kepentingan fitur global pada
tiap arah transfer. Fitur diberi peringkat berdasarkan mean absolute SHAP; stabilitas
dihitung dari rata-rata dan standar deviasi peringkat antar-kondisi; korelasi Spearman
mengukur kesamaan peringkat antar-arah. **Interpretasi sadar-kondisi:** SHAP dihitung pada
(a) model gagal (sebelum pemulihan) dan (b) model pulih (sesudah few-shot), lalu
dibandingkan — untuk menegaskan bahwa stabilitas fitur tidak identik dengan transferabilitas.

---

## 3. Hasil dan Pembahasan

### 3.1 Kinerja Within-Dataset

Pada evaluasi within-dataset [ISI: CIC-IDS2017], kedua model mencapai performa tinggi.
Skor ini tidak boleh ditafsirkan sebagai kesiapan operasional lintas lingkungan.

**Tabel 2. Kinerja within-dataset (mean multi-seed)**

| Metrik | XGBoost | Random Forest |
|---|---|---|
| F1 (weighted) | [ISI] | [ISI] |
| MCC (%) | [ISI] | [ISI] |
| Akurasi | [ISI] | [ISI] |
| AUC-ROC | [ISI] | [ISI] |
| Recall Attack | [ISI] | [ISI] |

### 3.2 Generalisasi Lintas-Dataset (CIC2017 → CIC2018 dan sebaliknya)

**Tabel 3. Evaluasi lintas-dataset (transfer langsung, ambang 0,5, mean multi-seed)**

| Model | Arah | Tipe | F1 | MCC% | Akurasi | AUC | PR-AUC | Recall Attack |
|---|---|---|---|---|---|---|---|---|
| XGBoost | CIC2017 | Within | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |
| XGBoost | CIC2017 → CIC2018 | Cross | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |
| XGBoost | CIC2018 → CIC2017 | Cross | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |
| RF | CIC2017 | Within | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |
| RF | CIC2017 → CIC2018 | Cross | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |
| RF | CIC2018 → CIC2017 | Cross | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] | [ISI] |

<!-- Fenomena yang diharapkan (hipotesis, konfirmasi via eksperimen): MCC runtuh pada
     cross walau weighted-F1 tampak tinggi; recall Attack mendekati 0 pada ambang 0,5. -->

### 3.3 Diskrepansi Weighted-F1 vs MCC

Pembahasan: pada data target tidak seimbang, weighted-F1 dan akurasi dapat tinggi walau
recall Attack rendah. [ISI: contoh angka dari Tabel 3]. Implikasi: metrik tunggal
weighted-F1/akurasi tidak memadai untuk IDS lintas-dataset.

### 3.4 Ranking vs Ambang: Kalibrasi Ambang (KONTRIBUSI BARU)

Pembahasan: jika AUC/PR-AUC jauh di atas acak sementara MCC@0,5 ≈ 0, maka sebagian
"kegagalan" adalah artefak ambang. [ISI: bandingkan MCC@0,5 vs MCC@ambang-terkalibrasi].

**Tabel 4. Efek kalibrasi ambang pada target**

| Model | Arah | MCC@0,5 | Ambang* | MCC@ambang* |
|---|---|---|---|---|
| XGBoost | CIC2017 → CIC2018 | [ISI] | [ISI] | [ISI] |
| XGBoost | CIC2018 → CIC2017 | [ISI] | [ISI] | [ISI] |
| RF | CIC2017 → CIC2018 | [ISI] | [ISI] | [ISI] |
| RF | CIC2018 → CIC2017 | [ISI] | [ISI] | [ISI] |

### 3.5 Pemulihan via Few-Shot (KONTRIBUSI BARU)

Pembahasan: penambahan fraksi kecil label target memulihkan MCC & recall Attack. [ISI].

**Tabel 5. Pemulihan few-shot (MCC per fraksi label target, mean±CI95 multi-seed)**

| Model | Arah | 0% | 1% | 5% | 10% |
|---|---|---|---|---|---|
| XGBoost | CIC2017 → CIC2018 | [ISI] | [ISI] | [ISI] | [ISI] |
| XGBoost | CIC2018 → CIC2017 | [ISI] | [ISI] | [ISI] | [ISI] |
| RF | CIC2017 → CIC2018 | [ISI] | [ISI] | [ISI] | [ISI] |
| RF | CIC2018 → CIC2017 | [ISI] | [ISI] | [ISI] | [ISI] |

### 3.6 Perbandingan XGBoost vs Random Forest

Kedua model dijalankan pada pipeline dan protokol identik. Perbandingan ini menguji apakah
fenomena kegagalan generalisasi dan pola pemulihan bersifat umum (lintas algoritma) atau
spesifik pada satu model.

**Tabel 6. Perbandingan XGBoost vs Random Forest (mean multi-seed)**

| Metrik | XGBoost | Random Forest |
|---|---|---|
| Within CIC2017 MCC | [ISI] | [ISI] |
| Cross CIC2017→CIC2018 MCC@0,5 | [ISI] | [ISI] |
| Cross CIC2017→CIC2018 AUC | [ISI] | [ISI] |
| Cross MCC@ambang-terkalibrasi | [ISI] | [ISI] |
| Few-shot 1% CIC2017→CIC2018 MCC | [ISI] | [ISI] |
| Cross CIC2018→CIC2017 MCC@0,5 | [ISI] | [ISI] |
| Few-shot 1% CIC2018→CIC2017 MCC | [ISI] | [ISI] |

Pembahasan: [ISI — bandingkan: (i) model mana lebih tahan transfer, (ii) apakah kedua model
sama-sama runtuh pada ambang 0,5, (iii) apakah pemulihan few-shot efektif pada keduanya,
(iv) trade-off kompleksitas/efisiensi]. Simpulkan apakah temuan kegagalan→pemulihan bersifat
umum atau bergantung algoritma.

### 3.7 Stabilitas Fitur SHAP yang Sadar-Kondisi

**Tabel 7. Sepuluh fitur terpenting berdasarkan SHAP (per model, model gagal vs pulih)**

| Model | Kondisi | Fitur Top-5 (urut mean|SHAP|) |
|---|---|---|
| XGBoost | Gagal (transfer) | [ISI] |
| XGBoost | Pulih (few-shot 1%) | [ISI] |
| RF | Gagal (transfer) | [ISI] |
| RF | Pulih (few-shot 1%) | [ISI] |

Pembahasan: bandingkan peringkat SHAP pada model gagal vs model pulih (korelasi Spearman
[ISI] untuk XGBoost, [ISI] untuk RF) dan kesamaan peringkat antar-model (Spearman [ISI]).
Tegaskan bahwa stabilitas fitur tidak menjamin transferabilitas: fitur penting dapat tetap
konsisten walau model gagal mendeteksi serangan.

### 3.8 Analisis Pergeseran Distribusi (opsional, penguat)

[ISI: bukti kuantitatif pergeseran distribusi antar dataset, mis. jarak statistik per
fitur, untuk menjelaskan mengapa transfer langsung gagal.]

### 3.9 Multi-Seed dan Interval Kepercayaan

[ISI: ringkasan mean/std/CI95 untuk angka utama; memperkuat kredibilitas vs studi
single-run.]

### 3.10 Implikasi terhadap Riset dan Operasional IDS

- Evaluasi within-dataset tidak cukup menilai kelayakan IDS.
- MCC, PR-AUC, recall Attack, dan kalibrasi ambang wajib dilaporkan.
- SHAP harus dibaca bersama kondisi model.
- Pemulihan few-shot menunjukkan jalur praktis adaptasi domain berbiaya rendah.

### 3.11 Keterbatasan

[ISI: skema biner; cakupan dua dataset; interpretasi difokuskan SHAP; dsb.]

---

## 4. Kesimpulan

<!-- Ringkas: diagnosis + koreksi (ranking vs ambang) + pemulihan few-shot + SHAP sadar
     kondisi. Semua angka [ISI] dari eksperimen. -->

Penelitian ini menyajikan diagnosis dan pemulihan kegagalan generalisasi lintas-dataset
pada NIDS dengan pipeline bebas-kebocoran, tanpa pemetaan fitur semantik, menggunakan
CIC-IDS2017 (referensi) dan CSE-CIC-IDS2018 (target). Model referensi mencapai performa
within-dataset tinggi ([ISI]) namun runtuh pada transfer lintas-dataset ([ISI]). Berbeda
dari studi terdahulu, penelitian ini memisahkan kegagalan ranking dari kegagalan ambang
[ISI] dan memulihkan deteksi melalui kalibrasi few-shot minimal [ISI]. Analisis SHAP
sadar-kondisi menegaskan bahwa stabilitas fitur tidak menjamin transferabilitas. Penelitian
lanjutan: skenario pergeseran distribusi yang lebih berat (mis. CIC-DDoS2019), klasifikasi
multi-kelas, dan validasi trafik nyata.

---

## Ucapan Terima Kasih

*[ISI]*

---

## Daftar Pustaka

<!-- Gaya JICTRA: nama-tahun. Lengkapi setelah body final. Minimal: -->

- CANTONE, M., MARROCCO, C. dan BRIA, A., 2024. Machine learning in network intrusion
  detection: A cross-dataset generalization study. *IEEE Access*, 12.
- CHAWLA, N.V., dkk., 2002. SMOTE: Synthetic minority over-sampling technique. *JAIR*, 16.
- CHEN, T. dan GUESTRIN, C., 2016. XGBoost: A scalable tree boosting system. *Proc. ACM SIGKDD*.
- CHICCO, D. dan JURMAN, G., 2020. The advantages of the Matthews correlation coefficient
  (MCC) over F1 score and accuracy. *BMC Genomics*, 21(6).
- D'HOOGE, L., dkk., 2020. Inter-dataset generalization strength of supervised ML methods
  for intrusion detection. *J. Inf. Secur. Appl.*, 54.
- LUNDBERG, S.M. dan LEE, S.-I., 2017. A unified approach to interpreting model
  predictions. *NeurIPS*, 30.
- SHARAFALDIN, I., dkk., 2018. Toward generating a new intrusion detection dataset.
  *Proc. ICISSP*.
- SHARAFALDIN, I., dkk., 2019. Developing realistic DDoS attack dataset and taxonomy.
  *Proc. IEEE ICCST*.
<!-- TODO: tambah SHAP TreeSHAP (Lundberg dkk. 2020), Breiman 2001, dll. sesuai isi. -->
