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
| T1 | Akuisisi & inspeksi dataset UNSW-NB15 (struktur kolom, label, distribusi) | **SELESAI** (§9.3) |
| T2 | Semantic Feature Mapping: tabel irisan fitur CIC-IDS2018 ↔ UNSW-NB15 (verifikasi semantik + statistik) | **SELESAI** (§10.4–10.8) |
| T3 | Pra-pemrosesan seragam + baseline cross-dataset (XGBoost tunggal): latih A→uji B, kuantifikasi generalization gap | **SELESAI** (§11) |
| T5 | Adversarial Training XGBoost tunggal pada fitur irisan + evaluasi lintas-dataset (2 arah × clean/adv) | **SELESAI** (§12) |
| T6 | Cross-network alignment (baseline vs joint training vs CORAL) untuk menaikkan MCC cross-network | **SELESAI** (§13) |
| T7 | Domain adaptation: few-shot target adaptation + cross-dataset mixup | **SELESAI** (§14) |
| T8 | Functional-Preserving Evasion (constraint protokol) — unconstrained vs functional | **SELESAI** (§15) |
| T9 | Adaptive White-Box Evaluation pada model cross-network robust | Belum |
| T10 | Long-Term Real-Traffic Deployment AWS (3–7 hari), ukur FAR | Belum |
| T11 | Penulisan naskah Q1 + gambar/tabel dari hasil nyata | Belum |
| T12 (opsional/lanjutan) | Robust Adversarial Ensemble (XGB+LGBM+CatBoost, defense bervariasi, soft-voting/meta) | Belum |

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

### 9.3 Hasil Inspeksi Nyata (T1 — SELESAI)
Inspeksi dilakukan langsung pada berkas partisi (versi yang dipakai), disimpan di `unswnb-15/data/` (di luar Git; diblokir `.gitignore`). Berikut temuan **nyata** (bukan asumsi):

- **Struktur:** 45 kolom = `id` + **42 fitur** + `attack_cat` (multi-kelas) + `label` (biner 0/1). Header training-set dan testing-set identik.
- **Penamaan berkas tertukar (PENTING):** berkas `UNSW_NB15_training-set.csv` justru berisi **82.332** record, sedangkan `UNSW_NB15_testing-set.csv` berisi **175.341** record. Angka resmi UNSW adalah training 175.341 & testing 82.332 — jadi **isi kedua berkas tertukar dengan namanya** (isu yang diketahui pada beberapa rilis). Konsekuensi: gunakan berkas 175.341 sebagai data latih dan 82.332 sebagai data uji, **berdasarkan jumlah record, bukan nama berkas**.
- **10 kelas** (`attack_cat`): Normal, Generic, Exploits, Fuzzers, DoS, Reconnaissance, Analysis, Backdoor, Shellcode, Worms. Terdapat *class imbalance* (mis. Worms hanya 44/130 record vs Generic puluhan ribu) — sejalan dengan alasan pemilihan metrik MCC.
- **42 fitur:** `dur, proto, service, state, spkts, dpkts, sbytes, dbytes, rate, sttl, dttl, sload, dload, sloss, dloss, sinpkt, dinpkt, sjit, djit, swin, stcpb, dtcpb, dwin, tcprtt, synack, ackdat, smean, dmean, trans_depth, response_body_len, ct_srv_src, ct_state_ttl, ct_dst_ltm, ct_src_dport_ltm, ct_dst_sport_ltm, ct_dst_src_ltm, is_ftp_login, ct_ftp_cmd, ct_flw_http_mthd, ct_src_ltm, ct_srv_dst, is_sm_ips_ports`.
- Catatan: nama kolom versi partisi sedikit berbeda dari `NUSW-NB15_features.csv` (mis. `spkts`/`dpkts` vs `Spkts`/`Dpkts`; `sinpkt`/`dinpkt` vs `Sintpkt`/`Dintpkt`; `smean`/`dmean` vs `smeansz`/`dmeansz`). Versi partisi juga sudah membuang IP/port/timestamp dan menambah `rate` + `id`.

---

## 10. Semantic Feature Mapping (T2 — Rancangan Awal)

Konvensi arah: pada CIC-IDS2018 istilah **Fwd/Bwd** (forward/backward) setara dengan **source/destination (s/d)** pada UNSW-NB15. Tabel berikut memetakan **Top-10 fitur CIC-IDS2018** (basis paper NIDS pertama) ke fitur UNSW-NB15 yang berfungsi semantik sama.

| # | CIC-IDS2018 (Top-10) | UNSW-NB15 | Kekuatan Padanan | Catatan |
|---|---|---|---|---|
| 1 | Init Fwd Win Byts | `swin` | Kuat | TCP window awal arah maju/source |
| 2 | Init Bwd Win Byts | `dwin` | Kuat | TCP window awal arah balik/destination |
| 3 | Tot Bwd Pkts | `dpkts` | Kuat | Jumlah paket arah balik/destination |
| 4 | TotLen Bwd Pkts | `dbytes` | Kuat | Total byte arah balik/destination |
| 5 | Bwd Pkt Len Mean | `dmean` | Kuat | Rata-rata ukuran paket balik/destination |
| 6 | Fwd Pkt Len Mean | `smean` | Kuat | Rata-rata ukuran paket maju/source |
| 7 | Fwd Pkt Len Max | *(tak langsung)* | Lemah | UNSW partisi tak punya max-per-paket; kandidat turunan dari `sbytes`/`spkts` |
| 8 | Fwd Act Data Pkts | `spkts` (aproks.) | Sedang | UNSW tak pisah paket berpayload; `spkts` sbagai proxy |
| 9 | URG Flag Cnt | *(tak ada)* | Tidak ada | UNSW partisi tak mengekspos hitung flag URG |
| 10 | Fwd Seg Size Min | *(tak ada)* | Tidak ada | Tak ada padanan langsung di UNSW partisi |

**Fitur irisan kuat (kandidat basis pelatihan lintas-dataset):** `swin`, `dwin`, `dpkts`, `dbytes`, `dmean`, `smean` (6 fitur) + kandidat sedang `spkts`. Fitur bersama tambahan yang berfungsi umum lintas-dataset (durasi & volume): `dur` (Flow Duration), `sbytes`/`dbytes` (TotLen Fwd/Bwd), `spkts`/`dpkts` (Tot Fwd/Bwd Pkts).

> **Status:** rancangan awal berbasis inspeksi kolom & deskripsi fitur. Validasi lanjutan (T2): konfirmasi kesetaraan **secara statistik** (rentang, distribusi, satuan) sebelum dipakai melatih model lintas-dataset, agar pemetaan benar-benar fungsional dan bukan sekadar kemiripan nama.

### 10.1 Catatan Kritis: Kedua Dataset Berbeda Sumber (Dasar Metodologi)
Hasil diskusi menegaskan tiga perbedaan fundamental antara kedua dataset. Ketiganya **bukan kelemahan**, melainkan justru **menjadi tiga gap inti** yang diangkat paper Q1:

| Aspek | CSE-CIC-IDS2018 | UNSW-NB15 | Implikasi |
|---|---|---|---|
| **Alat ekstraksi fitur** | CICFlowMeter (Java) | Argus + Bro/Zeek + 12 algoritma custom | *Feature-extractor mismatch* (gap #2): fitur bernama mirip belum tentu dihitung dengan cara sama |
| **Sumber PCAP / pembangkit trafik** | Testbed CIC (mesin nyata, skenario CIC), 2018 | IXIA PerfectStorm (generator hardware), Cyber Range Lab UNSW, 2015 | Generalisasi lintas-jaringan (gap #1): topologi, tahun, dan karakteristik trafik berbeda |
| **Kategori serangan** | Brute-Force, DoS, DDoS, Web, Infiltration, Botnet | Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, Worms | Perlu pemetaan label, bukan hanya fitur |

**Konsekuensi metodologis (wajib, demi kejujuran ilmiah):** karena *extractor* dan sumber trafik berbeda, pemetaan fitur **TIDAK boleh** hanya berdasarkan kemiripan nama/deskripsi. Setiap pasangan fitur kandidat **wajib divalidasi secara statistik** (rentang, satuan, distribusi) sebelum dipakai melatih model lintas-dataset.

### 10.2 Status Kejujuran Tabel Mapping
Tabel pada Bagian 10 (dan mapping penuh nanti) berstatus **hipotesis awal berbasis nama + deskripsi fitur** (level leksikal/semantik). Label "kuat/sedang/lemah" **belum** merupakan kesimpulan final; validasi statistik (T2) akan menentukannya. Sangat mungkin ditemukan fitur yang "namanya mirip tetapi distribusinya berbeda jauh" (mis. akibat definisi/satuan berbeda) — temuan semacam ini justru **berharga untuk dilaporkan** sebagai bukti *feature-extractor mismatch*.

### 10.3 Rencana Dua Model (Ablation Kualitas Mapping)
Untuk menilai pengaruh kualitas pemetaan terhadap generalisasi:
- **Model A** — hanya fitur irisan **kuat** (~11--13 fitur berpadanan solid: durasi, total paket/byte dua arah, laju byte, rata-rata ukuran paket, TCP window awal).
- **Model B** — Model A **ditambah fitur "sedang"** (mis. inter-arrival time `sinpkt`/`dinpkt` ↔ Fwd/Bwd IAT, jitter) yang padanannya lebih longgar.

Perbandingan A vs B mengukur apakah menambah fitur berpadanan longgar membantu atau justru merusak generalisasi lintas-dataset.

### 10.4 Tabel Semantic Feature Mapping Penuh (68 CIC ↔ 42 UNSW)
Berbasis inventaris fitur nyata (`feature_inventory.json`). Konvensi: **Fwd = source (s)**, **Bwd = destination (d)**.

**A. Irisan KUAT** (definisi & satuan sangat berdekatan — kandidat utama Model A):

| # | CIC-IDS2018 | UNSW-NB15 | Konsep |
|---|---|---|---|
| 1 | Flow Duration | `dur` | Durasi aliran |
| 2 | Tot Fwd Pkts | `spkts` | Total paket arah maju/source |
| 3 | Tot Bwd Pkts | `dpkts` | Total paket arah balik/destination |
| 4 | TotLen Fwd Pkts | `sbytes` | Total byte arah maju/source |
| 5 | TotLen Bwd Pkts | `dbytes` | Total byte arah balik/destination |
| 6 | Fwd Pkt Len Mean | `smean` | Rata-rata ukuran paket maju |
| 7 | Bwd Pkt Len Mean | `dmean` | Rata-rata ukuran paket balik |
| 8 | Init Fwd Win Byts | `swin` | TCP window awal arah maju |
| 9 | Init Bwd Win Byts | `dwin` | TCP window awal arah balik |
| 10 | Flow Byts/s (src) | `sload` | Laju bit/byte source |
| 11 | Bwd Pkts/s / (Bwd Byts/s) | `dload` | Laju bit/byte destination |

**B. Irisan SEDANG** (fungsi mirip, definisi/satuan perlu diverifikasi — tambahan Model B):

| # | CIC-IDS2018 | UNSW-NB15 | Catatan |
|---|---|---|---|
| 12 | Fwd IAT Mean | `sinpkt` | Inter-arrival time maju (mSec vs detik? cek satuan) |
| 13 | Bwd IAT Mean | `dinpkt` | Inter-arrival time balik |
| 14 | (jitter tak eksplisit di CIC) | `sjit`/`djit` | Jitter — CIC tak punya kolom jitter langsung; lemah |
| 15 | TCP handshake (tak eksplisit) | `tcprtt`/`synack`/`ackdat` | CIC tak ekspos RTT setup; lemah |

**C. TIDAK ADA padanan** (unik per dataset):
- CIC unik: flag counts detail (FIN/SYN/RST/PSH/ACK/URG/CWE/ECE), Active/Idle stats, Subflow, Pkt Len Var/Std, Header Len, Down/Up Ratio, Fwd Seg Size Min/Avg, dll.
- UNSW unik: fitur koneksi statistik (`ct_srv_src`, `ct_state_ttl`, `ct_dst_ltm`, dll — hitung koneksi dalam 100 koneksi terakhir), `sttl`/`dttl` (TTL), `sloss`/`dloss`, `proto`/`service`/`state` (kategorikal), `trans_depth`, `is_ftp_login`, dll.

> **Ringkasan:** ~11 fitur irisan **kuat** (Model A), +~2 fitur **sedang** IAT (Model B → ~13). Fitur kategorikal (proto/service/state) dan fitur khas masing-masing dataset **dikeluarkan** dari basis lintas-dataset karena tak ada padanan universal.

### 10.5 STATUS: Hipotesis — Wajib Validasi Statistik
Tabel di atas **masih hipotesis leksikal**. Karena *extractor* berbeda (CICFlowMeter vs Argus/Bro), pasangan yang "namanya cocok" belum tentu sepadan secara kuantitatif. Contoh risiko konkret:
- **Satuan IAT**: CIC `Fwd IAT` biasanya mikrodetik; UNSW `sinpkt` milidetik → perlu konversi.
- **TCP window**: CIC `Init Fwd Win Byts` (byte, 0–65535) vs UNSW `swin` (nilai window advertisement) → cek rentang.
- **Laju**: CIC `Flow Byts/s` vs UNSW `sload` (bits/sec) → byte vs bit, perlu penyesuaian.

Validasi (T2-lanjutan) membandingkan rentang & distribusi tiap pasangan sebelum difinalkan.

### 10.6 Hasil Validasi Statistik (T2 — SELESAI)
Notebook `02_mapping_validation.ipynb` membandingkan rentang/distribusi tiap pasangan (CIC di-*un-scale* lebih dulu). Verdict + interpretasi domain:

| Pasangan | Verdict otomatis | Interpretasi domain (final) |
|---|---|---|
| Tot Fwd Pkts ↔ `spkts` | aligned | **Aman** |
| Fwd Pkt Len Mean ↔ `smean` | aligned | **Aman** |
| Bwd Pkt Len Mean ↔ `dmean` | aligned | **Aman** |
| Flow Duration ↔ `dur` | likely-different | **Beda satuan** (CIC μs vs UNSW detik), bukan beda fitur → selamatkan via z-score |
| Tot Bwd Pkts ↔ `dpkts` | scale-mismatch | Beda skala agregasi → z-score |
| TotLen Fwd Pkts ↔ `sbytes` | scale-mismatch | Beda skala → z-score |
| TotLen Bwd Pkts ↔ `dbytes` | scale-mismatch | Beda skala → z-score |
| Flow Byts/s ↔ `sload` | scale-mismatch | Beda satuan (byte/s vs bit/s) → z-score |
| Bwd Pkts/s ↔ `dload` | scale-mismatch | Beda satuan → z-score |
| Fwd IAT Mean ↔ `sinpkt` | likely-different | Beda satuan (μs vs ms) → z-score (Model B) |
| Bwd IAT Mean ↔ `dinpkt` | likely-different | Beda satuan → z-score (Model B) |
| **Init Fwd Win Byts ↔ `swin`** | scale-mismatch | **BUANG — mismatch definisi** (lihat 10.7) |
| **Init Bwd Win Byts ↔ `dwin`** | scale-mismatch | **BUANG — mismatch definisi** (lihat 10.7) |

### 10.7 Temuan Kunci: TCP Window Mismatch (Bukti Feature-Extractor Mismatch)
Pemeriksaan nilai unik membuktikan `swin`/`dwin` di UNSW **bukan** ukuran window bytes:
- CIC `Init Fwd/Bwd Win Byts`: kontinu **0–65535** (byte window sesungguhnya); di Paper 1 ini fitur **paling sensitif** terhadap evasion.
- UNSW `swin`/`dwin`: praktis **biner** — `swin` = {0: 95.395 record, 255: 79.935, sisanya 11 record}; `dwin` serupa (0/255). Hanya 7–13 nilai unik.

Meski deskripsi resmi UNSW menyebut "TCP window advertisement value", **data aktualnya kategorikal 0/255** — kemungkinan penanda ada/tidaknya window scaling, bukan besaran window. Memetakannya ke Init Win Byts CIC berarti mengarang kesetaraan. **Keputusan: buang dari fitur training**, dan **laporkan sebagai studi kasus feature-extractor mismatch** (gap #2) di naskah — justru memperkuat argumen paper.

### 10.8 Himpunan Fitur Final (Keputusan: Opsi 3 — z-score per dataset)
Preprocessing: **StandardScaler (z-score) diterapkan per dataset secara terpisah**, sehingga perbedaan satuan/skala hilang tanpa mengarang; fitur dengan mismatch definisi (swin/dwin) dibuang.

- **Model A (9 fitur irisan kuat):** `dur, spkts, dpkts, sbytes, dbytes, smean, dmean, sload, dload` ↔ (Flow Duration, Tot Fwd/Bwd Pkts, TotLen Fwd/Bwd Pkts, Fwd/Bwd Pkt Len Mean, Flow Byts/s, Bwd Pkts/s).
- **Model B (11 fitur):** Model A **+** `sinpkt, dinpkt` ↔ (Fwd/Bwd IAT Mean).
- **Dibuang:** `swin`, `dwin` (dilaporkan sebagai temuan mismatch).

### 10.9 Langkah Berikutnya (T3)
1. **Pra-pemrosesan seragam:** subset kedua dataset ke fitur irisan final, z-score per dataset, samakan skema label (biner attack/normal untuk tahap awal; multi-kelas menyusul).
2. **Baseline cross-dataset (XGBoost tunggal):** latih pada dataset A, uji pada dataset B (dan sebaliknya), ukur *generalization gap*. Metrik utama **MCC** (konsisten Paper 1).
3. Bandingkan **Model A vs Model B** untuk menilai pengaruh menambah fitur berpadanan-longgar (IAT) terhadap generalisasi.

---

## 11. Baseline Cross-Dataset (T3 — SELESAI)

Notebook `03_cross_dataset_baseline.ipynb`, dijalankan di SageMaker atas dataset asli. Hasil disimpan di `cross_dataset_baseline.json`. **Seluruh angka di bawah adalah hasil eksekusi nyata.**

### 11.1 Setup
- **Label biner:** attack (1) vs normal (0). Untuk tahap awal, seluruh 14 kelas serangan CIC digabung jadi "attack".
- **XGBoost** `binary:logistic`, `max_depth=8, lr=0.1, n_estimators=200, subsample/colsample=0.8, tree_method='hist'` (mengikuti Paper 1).
- **z-score per dataset** (StandardScaler di-*fit* pada data latih masing-masing).
- **Empat skenario:** `same_cic` (split internal CIC 70/30), `same_unsw` (train 175k → test 82k), `cic2unsw` (latih CIC → uji UNSW), `unsw2cic` (latih UNSW → uji seluruh CIC).

### 11.2 Verifikasi Kejujuran Label (WAJIB, sudah dilakukan)
Sebelum mempercayai angka, label CIC diverifikasi terhadap `label_mapping` di `cleaned_100.pkl`:
- `label_mapping`: `Benign→0`, sisanya (`Bot`, `Brute Force`, `DDOS/DDoS`, `DoS`, `FTP/SSH-BruteForce`, `Infilteration`, `SQL Injection`) → indeks **1–14**.
- Distribusi `y`: kelas 0 (Benign) = 1.348.453; jumlah kelas 1–14 = 274.808.
- Konversi biner (`0→normal`, `1..14→attack`) menghasilkan tepat `{normal: 1.348.453, attack: 274.808}` — **cocok sempurna**.
- **Kesimpulan:** MCC negatif pada skenario cross adalah **fenomena generalisasi nyata**, BUKAN artefak label terbalik.

### 11.3 Hasil (MCC)

| Skenario | Model A (9 fitur) | Model B (11 fitur) |
|---|---|---|
| `same_cic` (latih & uji CIC) | **0,9134** | 0,9137 |
| `same_unsw` (latih & uji UNSW) | **0,7448** | 0,7428 |
| `cic2unsw` (latih CIC → uji UNSW) | **−0,0719** | 0,0035 |
| `unsw2cic` (latih UNSW → uji CIC) | **−0,0613** | −0,0464 |
| **gap (latih CIC)** = MCC(same_cic) − MCC(cic2unsw) | **0,985** | 0,910 |
| **gap (latih UNSW)** = MCC(same_unsw) − MCC(unsw2cic) | **0,806** | 0,789 |

Metrik pendukung (Model A): `same_cic` F1=0,928 ACC=0,976 AUC=0,981; `same_unsw` F1=0,890 ACC=0,868 AUC=0,979. Detail lengkap (F1/ACC/AUC/confusion tiap skenario) di `cross_dataset_baseline.json`.

### 11.4 Temuan
1. **Kolaps generalisasi lintas-jaringan (bukti empiris gap #1).** Model dengan performa dalam-dataset tinggi (MCC 0,91 di CIC; 0,74 di UNSW) **jatuh ke MCC ≈ 0 hingga negatif** saat diuji-silang. MCC ≈ 0 = setara tebakan acak; MCC negatif = sistematis salah arah. *Generalization gap* mencapai **0,81–0,99** — bukti tajam bahwa model NIDS terlatih-satu-jaringan tidak transfer ke jaringan lain.
2. **Bukti dari confusion matrix.** Pada `cic2unsw` (Model A), model salah melabeli 44.804 flow attack UNSW sebagai normal — model belajar batas keputusan spesifik-CIC yang tak berlaku pada distribusi UNSW.
3. **Model A ≈ Model B, IAT tidak menolong.** Menambah `sinpkt`/`dinpkt` (Fwd/Bwd IAT) tidak memperbaiki generalisasi (cross-dataset tetap kolaps). Konsisten dengan verdict validasi bahwa IAT punya mismatch satuan (μs vs detik). Model A (9 fitur, lebih ringkas) dipilih sebagai basis lanjutan; Model B dilaporkan sebagai pembanding.
4. **z-score per dataset tidak cukup.** Normalisasi skala saja tidak menutup gap distribusi antar-jaringan — memotivasi kebutuhan mekanisme *cross-network robust* (mapping robust + adversarial training) di tahap berikutnya, bukan sekadar penyelarasan skala.

### 11.5 Implikasi untuk Paper Q1
Hasil ini adalah **motivasi kuantitatif inti** paper: NIDS state-of-practice runtuh lintas-jaringan. Ini membenarkan kontribusi utama (Semantic Feature Mapping + adversarial robust NIDS). Baseline ini menjadi *lower bound* yang harus dilampaui pada tahap T4+.

---

## 12. Adversarial Training Cross-Dataset (T5 — SELESAI)

Notebook `04_adversarial_cross_dataset.ipynb`, dijalankan di SageMaker. Hasil di `adversarial_cross_dataset.json`. **Seluruh angka hasil eksekusi nyata.**

### 12.1 Setup
- Model **A** (9 fitur), label **biner**. Gradien **finite-difference central** (`h=0.01`), serangan **FGSM** `x_adv = x + eps*sign(dL/dx)`, adaptasi biner dari Paper 1.
- **Adversarial training:** `D_robust = D_clean ∪ D_adv` (80:20, `eps_train=0.1`), retrain XGBoost.
- **z-score per dataset**; komputasi saliency dibatasi 40.000 sampel (efisiensi).
- **Dua arah × 4 kondisi uji:** {CIC, UNSW} × {clean, adversarial eps 0.05/0.1/0.2}, model baseline vs robust.

### 12.2 Hasil Fokus — Generalisasi Lintas-Jaringan (uji *clean* di dataset lain)

| Arah | baseline MCC | robust MCC | Δ |
|---|---|---|---|
| latih CIC → uji UNSW (clean) | −0,072 | −0,011 | **+0,061** |
| latih UNSW → uji CIC (clean) | −0,061 | −0,066 | **−0,005** |

**Temuan utama: adversarial training TIDAK menutup gap generalisasi lintas-jaringan.** Arah CIC→UNSW naik tipis tapi tetap **negatif** (dari "buruk" ke "≈ acak"); arah UNSW→CIC malah turun sedikit. Confusion `robust/UNSW_clean` (arah CIC) = `[[36992, 8],[45332, 0]]` — model robust memprediksi hampir semua flow UNSW sebagai normal (0 attack terdeteksi). Ini mengonfirmasi hipotesis jujur: FGSM adversarial training menahan **perturbasi kecil**, bukan **pergeseran distribusi antar-jaringan**.

### 12.3 Hasil Sekunder — Robustness Evasion *In-Domain* (jaringan sama)
Berbeda dengan cross-network, adversarial training **berhasil** memperkuat robustness evasion pada jaringan yang sama (konsisten Paper 1):

| Kondisi (in-domain) | baseline MCC | robust MCC | Δ |
|---|---|---|---|
| CIC + adv (eps=0.1) | −0,090 | **+0,361** | +0,451 |
| UNSW + adv (eps=0.1) | −0,134 | **+0,363** | +0,497 |
| CIC + adv (eps=0.2) | −0,058 | −0,161 | −0,103 |

Perbaikan besar pada eps ≤ `eps_train` (0,1); pada eps=0,2 (melebihi eps latih) robustness turun — batas ekspektasi adversarial training. Integritas terjaga: `robust/CIC_clean` MCC=0,913 ≈ baseline (tak ada degradasi pada trafik bersih in-domain).

### 12.4 Kesimpulan (klaim jujur untuk paper)
1. **Adversarial training memperkuat robustness evasion in-domain** (MCC naik ~0,45–0,50 pada eps ≤ eps_train) — mereplikasi temuan Paper 1 pada fitur irisan.
2. **Tetapi TIDAK menyelesaikan cross-network generalization** — MCC cross tetap ≈ 0/negatif.
3. **Kontribusi konseptual:** hasil ini **memisahkan secara empiris** dua masalah yang sering dicampur — *adversarial robustness* ≠ *cross-network robustness*. Keduanya butuh solusi berbeda. Ini menajamkan arah paper Q1: diperlukan **mekanisme cross-network khusus** (mis. domain adaptation / alignment distribusi antar-jaringan), bukan sekadar adversarial training konvensional.

### 12.5 Arah Berikutnya (T6+)
- **Cross-network alignment:** eksplisit menyelaraskan distribusi fitur antar-dataset (mis. adversarial *domain adaptation*, CORAL/MMD, atau augmentasi campuran dua dataset) untuk menaikkan MCC cross-network di atas ~0.
- Lalu lanjut Functional-Preserving Evasion, Adaptive White-Box, Long-Term AWS deployment.

---

## 13. Cross-Network Alignment (T6 — SELESAI)

Notebook `05_cross_network_alignment.ipynb`, dijalankan di SageMaker. Hasil di `cross_network_alignment.json`. **Seluruh angka hasil eksekusi nyata.**

### 13.1 Setup
Model A (9 fitur), biner, z-score per dataset. Tiga strategi dibandingkan:
1. **Baseline single-source** (replikasi T3, pembanding).
2. **Joint training** — latih pada gabungan CIC+UNSW (rasio ~3:1 agar CIC tak mendominasi), uji test masing-masing.
3. **CORAL** (Sun et al. 2016) — *unsupervised domain adaptation*: selaraskan kovarians source→target (`X_align = X_s · C_s^{-1/2} · C_t^{1/2}`) TANPA label target, lalu latih di source ter-align, uji target.

### 13.2 Hasil Cross-Network (MCC, uji dataset lain)

| Strategi | CIC→UNSW | UNSW→CIC |
|---|---|---|
| Baseline single-source | −0,072 | −0,061 |
| **CORAL alignment** | **−0,185** | **+0,164** |

**Joint training** (satu model, uji test masing-masing):

| Uji | MCC | (in-domain pembanding) |
|---|---|---|
| CIC test | **0,912** | (0,913) |
| UNSW test | **0,732** | (0,745) |

### 13.3 Temuan
1. **Joint training = temuan terkuat.** Satu model tunggal yang melihat kedua jaringan saat latih mencapai MCC ~0,91 (CIC) dan ~0,73 (UNSW) **serentak** — hampir setara performa in-domain di **keduanya**. Ini bukti empiris kuat bahwa **Semantic Feature Mapping valid**: 9 fitur irisan cukup ekspresif merepresentasikan kedua jaringan. Masalah generalisasi **bukan pada fitur**, melainkan pada model single-source yang tak melihat distribusi target.
2. **CORAL membantu sebagian & ASIMETRIS.** UNSW→CIC naik dari −0,061 ke **+0,164** (MCC positif pertama di cross-network). Namun CIC→UNSW justru **turun** (−0,072 → −0,185). Dugaan: distribusi CIC jauh lebih kaya/besar (1,6 jt flow); menyelaraskan kovarians CIC ke ruang UNSW yang lebih sempit merusak struktur, sedangkan arah sebaliknya memperkaya. **Penting:** +0,164 masih jauh di bawah in-domain (0,74–0,91) — CORAL membantu, belum menyelesaikan.
3. **Diagnosis inti:** masalah generalisasi lintas-jaringan adalah **distribution shift**, bukan ketidakcukupan fitur. Alignment orde-2 (CORAL) belum memadai untuk arah dari sumber berdistribusi kaya.

### 13.4 Kesimpulan untuk Paper Q1
Rangkaian T3→T5→T6 membentuk **narasi kuantitatif yang bersih dan jujur**:
- T3: model single-source kolaps lintas-jaringan (MCC ~0).
- T5: adversarial training memperkuat evasion in-domain tetapi TIDAK menutup gap cross-network → *adversarial-robustness ≠ cross-network-robustness*.
- T6: fitur irisan (SFM) TERBUKTI valid (joint training ~in-domain di kedua jaringan); gap disebabkan *distribution shift*; CORAL membantu sebagian & asimetris.

**Implikasi:** kontribusi metodologis paper diarahkan ke penggabungan *multi-source exposure* + *domain adaptation* yang lebih kuat (mis. adversarial DA / MMD / mixup lintas-dataset), dengan SFM sebagai fondasi yang sudah tervalidasi.

### 13.5 Arah Berikutnya (T7+)
- Perkuat DA (MMD / adversarial domain-invariant features / mixup lintas-dataset) untuk menaikkan CIC→UNSW ke MCC positif dan mendekatkan cross ke joint.
- Lalu Functional-Preserving Evasion, Adaptive White-Box, Long-Term AWS deployment.

---

## 14. Domain Adaptation: Few-Shot + Mixup (T7 — SELESAI)

Notebook `06_domain_adaptation.ipynb`, dijalankan di SageMaker. Hasil di `domain_adaptation.json`. **Seluruh angka hasil eksekusi nyata.**

### 14.1 Setup
Model A (9 fitur), biner, z-score per dataset. Dua eksperimen:
1. **Few-shot target adaptation** — latih di source + fraksi label target (0/1/5/10/25%), uji di test target. Protokol jujur: fraksi diambil dari **train target**, uji di **test target** (tanpa kebocoran).
2. **Cross-dataset mixup** — sampel sintetik `x = λ·x_src + (1−λ)·x_tgt_train` (Beta(0,4)), label komponen dominan; unsupervised terhadap test target.

### 14.2 Hasil Few-Shot (MCC vs fraksi label target)

| Fraksi target | CIC→UNSW | UNSW→CIC |
|---|---|---|
| 0% (baseline T3) | −0,072 | −0,061 |
| **1%** | **0,648** | **0,899** |
| 5% | 0,662 | 0,911 |
| 10% | 0,681 | 0,911 |
| 25% | 0,695 | 0,912 |

*(1% target = 1.753 flow UNSW / 11.362 flow CIC. In-domain pembanding: UNSW 0,745; CIC 0,913.)*

**Mixup (unsupervised, tanpa label target uji):** CIC→UNSW = **0,680**; UNSW→CIC = **0,798**.

### 14.3 Temuan
1. **Lompatan dramatis 0%→1% (headline).** Menambah hanya **1% label target** membalik MCC dari negatif (lebih buruk dari acak) menjadi kuat: CIC→UNSW −0,072→**0,648**; UNSW→CIC −0,061→**0,899** (hampir menyentuh in-domain 0,913).
2. **Kurva datar setelah 1%.** Dari 1%→25% kenaikan marginal (UNSW→CIC 0,899→0,912). Artinya **kalibrasi minimal sudah cukup**; label tambahan hasil marginal. Pesan praktis untuk deployment.
3. **Mixup bekerja tanpa label target.** CIC→UNSW 0,680 (bahkan > few-shot 25%) dan UNSW→CIC 0,798. Interpolasi lintas-dataset menjembatani distribution shift tanpa satu pun label target — opsi *fully unsupervised* yang berguna.
4. **Asimetri konsisten.** CIC→UNSW mentok ~0,65–0,70 vs UNSW→CIC ~0,91 — sejalan temuan CORAL (T6): adaptasi dari sumber berdistribusi kaya (CIC) ke target lebih sempit (UNSW) lebih sulit. Dilaporkan apa adanya.

### 14.4 Kesimpulan untuk Paper Q1 (narasi lengkap T3→T7)
- **T3 — Masalah:** NIDS single-source kolaps lintas-jaringan (MCC ~0).
- **T5 — Bukan evasion:** adversarial training memperkuat evasion in-domain, TIDAK menutup cross-network (*adversarial-robustness ≠ cross-network-robustness*).
- **T6 — Bukan fitur:** joint training ~in-domain di kedua jaringan → **Semantic Feature Mapping valid**; gap = *distribution shift*.
- **T7 — Solusi:** kalibrasi minimal (**1% label target**) atau **mixup unsupervised** memulihkan MCC ke ~0,65–0,91.

**Klaim inti yang dapat dipertahankan:** Semantic Feature Mapping membuat NIDS cross-network **praktis** — jaringan baru cukup dikalibrasi dengan ~1% data berlabel (atau tanpa label via mixup) untuk mencapai deteksi berguna. Ini menjawab masalah deployment dunia nyata, bukan sekadar klaim teoretis.

### 14.5 Arah Berikutnya (T8+)
- Functional-Preserving Evasion (constraint protokol pada saddle-point).
- Adaptive White-Box Evaluation pada model cross-network robust.
- Long-Term Real-Traffic Deployment AWS (3–7 hari), ukur FAR.

---

## 15. Functional-Preserving Evasion (T8 — SELESAI)

Notebook `07_functional_preserving_evasion.ipynb`, dijalankan di SageMaker. Hasil di `functional_preserving_evasion.json`. **Seluruh angka hasil eksekusi nyata.**

### 15.1 Setup
Model A (9 fitur), biner. FGSM (finite-diff saliency) dibandingkan dalam dua mode:
- **Unconstrained** — perturbasi bebas di ruang z-score (ala T5); dapat menghasilkan flow **mustahil** (paket pecahan, bytes < pkts, durasi negatif).
- **Functional-preserving** — constraint diterapkan di **ruang asli** (un-scale → clip/round → re-scale): non-negatif; `fwd_pkts`/`bwd_pkts` integer; `bytes ≥ pkts`; `mean = bytes/pkts` (konsisten); serta **monotonic add-only** pada pkts/bytes/duration (penyerang hanya boleh MENAMBAH trafik, tak boleh mengurangi yang sudah terkirim).

Diserang: 4 model — baseline single-source (CIC, UNSW) dan few-shot adapted (+1% target).

### 15.2 Hasil (eps=0,1) — MCC di bawah serangan

| Model | clean | unconstrained | functional |
|---|---|---|---|
| CIC baseline | 0,912 | −0,090 | **0,127** |
| CIC adapted (+1% UNSW) | 0,911 | −0,163 | −0,029 |
| UNSW baseline | 0,748 | −0,134 | **0,313** |
| UNSW adapted (+1% CIC) | 0,744 | −0,217 | **0,385** |

### 15.3 Temuan
1. **Evasion tak-terbatas MELEBIH-LEBIHKAN ancaman.** Di keempat model, functional MCC jauh > unconstrained MCC (mis. UNSW baseline: −0,134 → +0,313; selisih +0,45). Ketika penyerang dibatasi ke flow yang benar-benar valid/dapat dikirim, daya serang turun substansial. **Koreksi metodologis penting:** banyak "keberhasilan evasion" bertumpu pada flow mustahil. Ini justru poin kekuatan paper adversarial level Q1.
2. **Namun ancaman functional tetap nyata.** Functional MCC tetap turun tajam dari clean (CIC 0,912→0,127; UNSW 0,748→0,313). Bahkan dengan flow sah, penyerang masih merusak deteksi signifikan — pertahanan tetap dibutuhkan.
3. **Robustness evasion ⊥ cross-network adaptation.** Few-shot adaptation tidak memperbaiki robustness evasion secara konsisten (CIC adapted functional −0,029 < CIC baseline 0,127; UNSW adapted 0,385 > baseline 0,313). Menguatkan pemisahan konseptual dari T5: adaptasi distribusi ≠ ketahanan adversarial.

### 15.4 Kesimpulan untuk Paper Q1
T8 melengkapi trio gap dengan **dimensi realisme serangan**: evaluasi adversarial harus memakai constraint fungsional agar ancaman tidak dilebih-lebihkan. Kombinasi tiga temuan — generalisasi (T3/6/7), pemisahan adversarial vs cross-network (T5/8), realisme evasion (T8) — membentuk kontribusi yang koheren dan jujur.

### 15.5 Arah Berikutnya (T9+)
- Adaptive White-Box Evaluation (penyerang membangkitkan evasion langsung dari gradien model, skenario terburuk).
- Long-Term Real-Traffic Deployment AWS (3–7 hari), ukur FAR.
