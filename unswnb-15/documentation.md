# UNSW-NB15 x CSE-CIC-IDS2018 — Dokumentasi Penelitian NIDS Level Q1

## Cross-Network Robust NIDS via Semantic Feature Mapping & Adaptive Adversarial Ensemble

> **Status dokumen:** Perencanaan (roadmap). Sebagian besar item di sini adalah *rencana kerja*, bukan hasil yang sudah terbukti. Item yang sudah/berlanjut dari penelitian sebelumnya ditandai eksplisit. Prinsip kerja: **semua angka & klaim harus jujur terhadap eksperimen nyata — tidak boleh dikarang.**

---

## 1. Konteks & Kontinuitas dari Penelitian Sebelumnya

Penelitian ini merupakan kelanjutan langsung dari paper NIDS pertama (CSE-CIC-IDS2018: reduksi fitur XGBoost Gain + Adversarial Training berbasis Saliency Map + validasi real-traffic AWS). Paper pertama secara **jujur mengakui tiga keterbatasan**, dan tiga keterbatasan itulah yang menjadi **gap inti** paper Q1 ini:

| Keterbatasan Paper 1 (diakui) | Menjadi Gap Paper Q1 |
|---|---|
| Generalisasi lintas-dataset belum diuji | (1) Ketidakmampuan generalisasi lintas-jaringan |
| MCC real-traffic turun akibat *feature-extractor mismatch* (NFStream vs CICFlowMeter; z ≈ +6,2 dan +3,3) | (2) Feature-extractor mismatch |
| Evaluasi hanya *transfer/grey-box*, belum *white-box adaptive* | (3) Kerentanan evasion adaptif |

Kontinuitas ini adalah kekuatan naratif utama untuk reviewer Q1: bukan riset baru dari nol, melainkan penutupan gap yang sudah diidentifikasi secara ilmiah.

---

## 2. Latar Belakang & Gap Penelitian (Core Argument)

NIDS berbasis machine learning saat ini menderita tiga masalah kritis yang saling berkaitan:

1. **Ketidakmampuan Generalisasi Lintas-Jaringan.** Model yang dilatih pada satu lingkungan laboratorium kolaps saat menghadapi karakteristik trafik dari topologi jaringan berbeda.
2. **Feature-Extractor Mismatch.** Perbedaan definisi fitur antar-alat ekstraksi (CICFlowMeter, NFStream, Zeek) merusak akurasi deteksi pada fase inferensi dunia nyata.
3. **Kerentanan Evasion Adaptif.** Adversarial Training konvensional sering hanya dievaluasi terhadap serangan statis/transfer (grey-box). Penyerang adaptif dunia nyata mengeksploitasi gradien model pertahanan itu sendiri secara white-box.

**Tesis paper:** sebuah NIDS dapat dibuat *cross-network robust* dan *evasion-adaptive robust* melalui pemetaan fitur semantik lintas-dataset, arsitektur ensemble adversarial, dan serangan yang menjaga validitas fungsional protokol.

---

## 3. Metodologi Eksperimen Multi-Dataset (The "Golden Pair")

Tidak lagi bertumpu pada satu dataset tunggal. Kombinasi:

- **CSE-CIC-IDS2018** — representasi trafik jaringan enterprise skala besar (sudah dipakai di Paper 1).
- **UNSW-NB15** — representasi trafik jaringan modern (dataset kedua, fokus folder ini). *Alternatif/eskalasi:* CICIoT2023 untuk representasi IoT.

### 3.1 Tahap Krusial — Semantic Feature Mapping
Sebelum pelatihan, disusun **tabel penyelarasan semantik** yang memetakan fitur-fitur berfungsi matematis sama dari kedua dataset meski bernama kolom berbeda (mis. durasi aliran, statistik paket forward/backward, laju byte). Ini menghasilkan **himpunan fitur irisan (intersection)** yang menjadi basis pelatihan lintas-dataset.

> **Catatan kejujuran:** tabel mapping harus dibangun dari **inspeksi nyata** kolom kedua dataset (bukan asumsi). UNSW-NB15 punya ~49 fitur (Argus/Bro-based), CIC-IDS2018 ~80 fitur (CICFlowMeter). Definisi "sama" harus diverifikasi secara semantik & statistik, bukan sekadar kemiripan nama.

### 3.2 Protokol Pelatihan-Pengujian Lintas-Dataset
- Latih pada fitur irisan dataset A, uji pada dataset B (dan sebaliknya) — mengukur generalisasi lintas-jaringan.
- Bandingkan dengan baseline "latih & uji pada dataset sama" untuk mengkuantifikasi *generalization gap*.

---

## 4. Model: XGBoost Tunggal (Tahap Sekarang) → Ensemble (Lanjutan)

### 4.1 Tahap Sekarang — Model Tunggal XGBoost
Untuk tahap awal, penelitian **tetap menggunakan model tunggal XGBoost**, konsisten dengan Paper 1. Alasan:
- Fokus pada kontribusi inti yang baru: **generalisasi lintas-jaringan** dan **Semantic Feature Mapping** — bukan kompleksitas model.
- Menjaga *comparability* langsung dengan hasil Paper 1 (XGBoost Top-10, Adversarial Training berbasis Saliency Map).
- Mengisolasi variabel: efek dari fitur irisan lintas-dataset dapat dinilai tanpa tercampur efek ensemble.

Konfigurasi mengikuti Paper 1: `multi:softprob`, `max_depth=8`, `learning_rate=0.1`, `n_estimators=200`, `subsample`/`colsample_bytree=0.8`. Pertahanan tetap Adversarial Training (Min-Max) dengan gradien Saliency Map yang diaproksimasi numerik (finite difference / score-based, karena XGBoost *non-differentiable*).

### 4.2 Arah Lanjutan (Future) — Robust Adversarial Ensemble
*Belum dikerjakan pada tahap ini.* Sebagai pengembangan setelah model tunggal terbukti:
- **Robust Ensemble Architecture** menggabungkan beberapa algoritma tree-boosting (XGBoost, LightGBM, CatBoost) atau deep learning terkompresi.
- Tiap anggota dilatih dengan strategi Adversarial Training bervariasi (Saliency Map / FGSM / L2).
- Keputusan akhir via soft-voting atau meta-classifier dinamis untuk decision boundary yang lebih beragam/tangguh.

---

## 5. Formulasi Serangan: Functional-Preserving Evasion

Reviewer Q1 sering menolak paper adversarial karena perturbasi matematis dianggap merusak struktur paket TCP/IP sehingga tak dapat dikirim di dunia nyata.

- Perkenalkan **Functional-Preserving Constraints** pada fungsi optimasi *saddle-point*.
- Batasan matematis ketat: fitur penting (bendera TCP, nomor port, window size) hanya boleh dimanipulasi dalam batas protokol jaringan yang valid, agar paket tidak *malformed* di sistem operasi target.
- Ini menjembatani gap "adversarial teoretis" vs "serangan yang benar-benar dapat dikirim" — poin kuat untuk Q1.

---

## 6. Validasi: Adaptive Attacks & Long-Term Real-Traffic

- **Adaptive White-Box Evaluation.** Membuktikan ketangguhan pada skenario terburuk: penyerang membangkitkan sampel evasion langsung dari gradien (teraproksimasi) model ensemble robust kita sendiri. (Menutup gap #3 Paper 1.)
- **Long-Term Cloud Deployment.** NIDS robust dipasang di AWS untuk memantau trafik aktif kontinu **minimal 3–7 hari**, membuktikan *False Alarm Rate* (FAR) sangat rendah di tengah fluktuasi trafik normal harian.

---

## 7. Rencana Kerja Bertahap (Roadmap)

| Tahap | Kegiatan | Status |
|---|---|---|
| T1 | Akuisisi & inspeksi dataset UNSW-NB15 (struktur kolom, label, distribusi) | Belum |
| T2 | Semantic Feature Mapping: tabel irisan fitur CIC-IDS2018 ↔ UNSW-NB15 (verifikasi semantik + statistik) | Belum |
| T3 | Pra-pemrosesan seragam kedua dataset pada fitur irisan | Belum |
| T4 | Baseline cross-dataset (XGBoost tunggal): latih A→uji B, kuantifikasi generalization gap | Belum |
| T5 | Adversarial Training XGBoost tunggal pada fitur irisan + evaluasi 2×2 (S1–S4) lintas-dataset | Belum |
| T6 | Functional-Preserving Evasion (constraint protokol pada saddle-point) | Belum |
| T7 | Adaptive White-Box Evaluation pada XGBoost robust | Belum |
| T8 | Long-Term Real-Traffic Deployment AWS (3–7 hari), ukur FAR | Belum |
| T9 | Penulisan naskah Q1 + gambar/tabel dari hasil nyata | Belum |
| T10 (opsional/lanjutan) | Robust Adversarial Ensemble (XGB+LGBM+CatBoost, defense bervariasi, soft-voting/meta) | Belum |

---

## 8. Prinsip & Catatan Kerja

- **Kejujuran data mutlak.** Setiap angka (mapping, generalization gap, FAR, hasil white-box) berasal dari eksperimen nyata yang dapat direproduksi. Tidak ada angka ilustratif yang disamarkan sebagai hasil.
- **Reproduktibilitas.** Kode, konfigurasi, dan skrip disimpan di repo; dataset besar & artefak model diblokir `.gitignore` (kecuali hasil kecil untuk paper, via pengecualian eksplisit).
- **Biaya AWS.** Deployment jangka panjang (3–7 hari) berbiaya; rencanakan tipe instans hemat, jadwal on/off, dan pemantauan biaya sebelum eksekusi.
- **Istilah.** "Semantic Feature Mapping" = pemetaan fitur berfungsi sama lintas-dataset (istilah kerja, dapat difinalisasi saat penulisan).

---

## 9. Dataset UNSW-NB15 (ringkas)

UNSW-NB15 dibuat oleh Australian Centre for Cyber Security (ACCS), UNSW Canberra. Trafik dibangkitkan dengan IXIA PerfectStorm, fitur diekstraksi dengan Argus & Bro (Zeek), menghasilkan ~49 fitur dan 9 kategori serangan (mis. Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, Worms) + Normal.

> Detail struktur kolom & distribusi label akan diisi setelah inspeksi nyata dataset (Tahap T1) — belum diisi agar tidak mengarang.

### 9.1 Sumber Resmi
- Halaman resmi: `https://research.unsw.edu.au/projects/unsw-nb15-dataset` (menyediakan PCAP, BRO, Argus, CSV, dan reports).
- Berkas yang dipakai: versi CSV terpartisi **`UNSW_NB15_training-set.csv`** + **`UNSW_NB15_testing-set.csv`** (≈49 fitur + kolom `label` biner dan `attack_cat` multi-kelas) — paling rapi untuk *feature mapping*.
- Lisensi: gratis untuk riset akademik (bukan komersial).

> Catatan: tautan unduh UNSW kadang di-*redirect* ke Google Drive dan dapat berubah; ambil tautan CSV terkini dari halaman resmi di atas.

### 9.2 Alur Akuisisi: Dataset → S3 → SageMaker
Pola konsisten dengan penelitian sebelumnya (data besar tidak masuk Git; hanya di S3 + lokal SageMaker).

**Opsi A (direkomendasikan) — unduh langsung di SageMaker lalu unggah ke S3** (bandwidth internal AWS cepat):
```bash
# 1. Unduh CSV di SageMaker (ganti URL dengan tautan CSV resmi UNSW)
wget -O UNSW_NB15_training-set.csv "URL_TRAINING_SET"
wget -O UNSW_NB15_testing-set.csv  "URL_TESTING_SET"
# Jika tautan berupa Google Drive file besar, gunakan gdown:
#   pip install gdown
#   gdown "https://drive.google.com/uc?id=FILE_ID" -O UNSW_NB15_training-set.csv

# 2. Unggah ke S3
aws s3 cp UNSW_NB15_training-set.csv s3://<BUCKET>/unswnb15/
aws s3 cp UNSW_NB15_testing-set.csv  s3://<BUCKET>/unswnb15/
```

**Opsi B — unggah dari laptop via AWS Console:** S3 → pilih bucket → Upload → Add files → pilih CSV → Upload.

**Opsi C — unggah dari laptop via AWS CLI:**
```bash
aws s3 cp "UNSW_NB15_training-set.csv" s3://<BUCKET>/unswnb15/ --region ap-southeast-1
```

> **Konvensi S3 (diisi setelah dikonfirmasi):** bucket `<BUCKET>`, prefix `unswnb15/`, region `ap-southeast-1`. Nama bucket final akan dicatat di sini agar reproducible.

### 9.3 Langkah Berikutnya (T1)
Setelah dataset berada di S3, disiapkan skrip `s3_download_inspect.py` untuk: unduh dari S3 ke SageMaker, lalu inspeksi struktur (kolom, tipe), label (`label`/`attack_cat`), distribusi kelas, dan statistik ringkas — sebagai dasar Semantic Feature Mapping (T2).
