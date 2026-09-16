# Paper 3 — Dokumentasi Penelitian NIDS Class-Incremental / Self-Calibrating

## NIDS yang Mengalibrasi-Diri: Pengenalan Jenis Serangan Baru secara Online (Open-Set + Class-Incremental) untuk Trafik Cloud

> **PETA MEMORI (baca ini dulu).** Ini dokumentasi **Paper 3** (NIDS *closed-loop*:
> deteksi jenis serangan **baru** saat runtime + penambahan kelas otonom tanpa lupa
> kelas lama). Pasangannya: `aws/runbook.md` (operasi AWS Paper 3 — deployment jangka
> panjang & injeksi serangan baru saat testing). Naskah paper: `paper3.tex`.
>
> **Silsilah penelitian:**
> - **Paper 1** (`../unswnb-15/documentation.md`) — Semantic Feature Mapping (SFM) +
>   few-shot adaptation, generalisasi lintas-jaringan, validasi trafik AWS nyata.
>   Adaptasi **one-shot / offline** (sekali sebelum deploy), model **biner** (attack/normal).
> - **Paper 2** (`../unswnb-15/documentation_adversarial.md`) — ketahanan adversarial.
> - **Paper 3 (dokumen ini)** — adaptasi **online / kontinu** saat runtime, model
>   **multi-class**, mampu **menambah kelas serangan baru** yang belum pernah dilihat.
>
> **Status dokumen:** Perencanaan (roadmap). Sebagian besar item adalah *rencana kerja*,
> bukan hasil terbukti. Item yang berlanjut dari Paper 1 ditandai eksplisit.
>
> **Prinsip kerja (wajib):** semua angka & klaim harus **jujur terhadap eksperimen
> nyata — tidak boleh dikarang.** Setiap nilai (skor open-set, recall per-kelas,
> forgetting, akurasi labeling, MCC/FAR, biaya label) berasal dari eksekusi
> notebook / AWS yang dapat direproduksi.

---

## 1. Ringkasan Kebutuhan (Inti Paper 3)

Tujuan awal **sama seperti Paper 1**: model NIDS yang (a) dapat digunakan
**lintas-dataset (cross-network)** via SFM + few-shot, dan (b) **diuji di infrastruktur
AWS** yang kita bangun (trafik nyata, ekstraksi fitur NFStream, inferensi live).

**Tambahan kebutuhan baru Paper 3 (novelty):**

> Model NIDS awalnya hanya mengenal **N jenis serangan** (kelas *known*) dan diuji
> dengan N jenis itu. Kemudian saat online muncul **jenis serangan baru** (mis. 3 jenis)
> yang belum pernah dilihat. Karena **jaraknya terlalu jauh** dari semua kelas dikenal,
> flow-flow ini ditandai **unknown** dan **dikelompokkan menjadi kandidat kelas baru**.
> Kandidat itu **dilabeli** (oleh oracle terjadwal, dibantu LLM sebagai penamaan
> otomatis), lalu model **di-update secara inkremental** (data baru + **memory** kelas
> lama) sehingga bisa mengenali kelas baru tersebut. **Model baru hanya menggantikan
> model lama apabila lolos validasi** (recall kelas lama tak turun & kelas baru terdeteksi).

Kebutuhan itu terurai menjadi empat komponen teknis:

| Frasa kebutuhan | Komponen teknis | Bagian |
|---|---|---|
| "jaraknya terlalu jauh → unknown" | **Open-Set Recognition** (Mahalanobis di 9-fitur SFM + confidence) | §4 |
| "dikelompokkan jadi kandidat kelas baru" | **Novelty Clustering** (HDBSCAN, cluster padat + persisten) | §5 |
| "dilabeli sistem (LLM/oracle)" | **Pelabelan**: oracle terjadwal (utama) + LLM auto-name (tambahan, divalidasi) | §6 |
| "update pakai data baru + memory, lolos validasi" | **Class-Incremental Update + Replay Memory + Guardrail promosi** | §7 |

---

## 1a. Novelty & Kontribusi (dokumen hidup — dapat diperbarui seiring waktu)

> Catatan: tiap komponen *individual* (open-set, HDBSCAN, class-incremental, replay,
> drift detection) sudah ada di literatur. Novelty diletakkan pada **kombinasi + konteks
> + validasi**, bukan pada satu teknik tunggal. Daftar ini sengaja dibuat berperingkat
> dan **boleh direvisi** saat eksperimen berjalan.

**Tesis novelty (rumusan kerja):** kerangka *closed-loop* yang **menemukan, memberi
label, dan mengintegrasikan jenis serangan yang belum pernah dilihat** secara **online**
pada **trafik cloud nyata**, yang **memisahkan novelty sejati dari pergeseran distribusi
lintas-jaringan**, dengan **gerbang promosi tahan-poisoning** yang menjamin tidak ada
regresi pada kelas lama. Empat kata kunci yang sulit diklaim serentak oleh paper lain:
**online + cloud-live + cross-network-aware + safe-promotion**.

| # | Kontribusi | Kekuatan | Posisi |
|---|---|---|---|
| 1 | **Closed-loop penuh divalidasi pada trafik cloud LIVE** (serangan baru dijalankan nyata + ground-truth terjadwal), bukan replay CSV dataset | Paling sulit ditiru; menyambung kekuatan Paper 1 | **Utama** |
| 2 | **Class-discovery di tengah cross-network distribution shift** — membedakan "flow ini KELAS BARU" vs "kelas LAMA dari jaringan berbeda" (keduanya sama-sama jauh dari centroid) | Paling bernilai ilmiah; tumbuh langsung dari temuan Paper 1 (MCC kolaps lintas-jaringan) | **Utama (kandidat)** |
| 3 | **Guardrail promosi tahan-poisoning** — gerbang dua-kriteria (recall lama tak turun + baru naik) menolak update yang meracuni | Angle keamanan "safe autonomous adaptation" | Pendukung kuat |
| 4 | **LLM sebagai auto-namer cluster** — menjembatani cluster statistik tak-berlabel → label semantik taksonomi serangan, diukur jujur vs oracle | Menjual untuk 2026, tapi berisiko dianggap gimmick bila overclaim | **Sekunder** |
| 5 | **Efisiensi/deployability** — seluruh loop di atas XGBoost 9-fitur ringan (2,9 MB, ~439µs/flow, 1 vCPU) | Argumen kepraktisan edge | Pendukung |

> **Keputusan yang masih terbuka (akan difinalisasi seiring eksperimen):**
> - Apakah #2 (novelty vs shift) jadi kontribusi utama (butuh sub-eksperimen: sistem tak
>   boleh salah menganggap "kelas lama dari jaringan lain" sebagai "kelas baru").
> - Apakah #4 (LLM) jadi kontribusi ber-eksperimen atau cukup *future work* di paper ini.

---

## 1b. Aset Paper 1 yang SUDAH Menyentuh Fondasi Paper 3 (jangan diulang)

Saat menyalin aset ke `shared/`, ditemukan bahwa beberapa notebook di
`../unswnb-15/notebooks/` **sudah mengerjakan sebagian fondasi Paper 3**. Ini dicatat
agar roadmap Paper 3 **tidak menduplikasi** yang sudah ada — cukup dirujuk/dilanjutkan.

| Notebook (Paper 1) | Sudah dikerjakan | Relevansi ke Paper 3 | Sisa untuk Paper 3 |
|---|---|---|---|
| `24_multiclass.ipynb` | **Multi-class XGBoost `multi:softprob`** sudah ada: in-domain per dataset (CIC & UNSW) + cross-dataset pada kategori sepadan. Pemetaan label → kategori sudah dibuat; kelas < 200 sampel digabung `Other-rare`; StandardScaler fit-on-train (no leakage). Output: `multiclass_results.json` + confusion + per-kelas. Fitur = 9 SFM (`duration` di-×1e6 = µs, konsisten audit satuan). | **Titik awal T1** (latih ulang multi-class). Sebagian besar T1 **sudah tersedia**. | Skema label terpadu final untuk skenario held-out; simpan artefak model+centroid/kovarians per-kelas untuk open-set. |
| `21_dataset_shift.ipynb` (+ `shift_out/`) | Analisis **distribution shift** CIC↔UNSW: Wasserstein per-fitur + heatmap, PCA/t-SNE, ECDF/boxplot, domain-classifier. Output `dataset_shift_results*.json` + PNG. | Mendukung **novelty #2** (novelty sejati vs distribution shift) — sudah ada bukti kuantitatif shift. | Membedakan "kelas baru" vs "kelas lama dari jaringan lain" secara operasional. |
| `30_drift_detector_poc.ipynb` (+ `drift_out/`) | **PoC detektor drift Paper 3 sudah ada**: stream buatan **CIC→UNS→AWS**, sliding-window $W_1$ (W=1000, STEP=250) + CUSUM (k=0,5σ, h=5σ, ambang 3σ), plot `drift_stream_score.png`, output `drift_poc_results.json`. Sudah tahu alarm $W_1$/CUSUM pertama di titik transisi domain. | **Titik awal T2/T3** (detektor drift + kalibrasi $w$,$h$). PoC **sudah jalan**. | Formalkan kalibrasi ambang; sambungkan ke pemicu & loop adaptasi (belum ada). |

> **Konsekuensi (kejujuran status):** T1 dan T2 **bukan dari nol** — ada fondasi nyata di
> Paper 1. Paper 3 melanjutkan, bukan mengulang. Notebook Paper 3 tetap mulai dari
> penomoran `30_`+ (drift PoC sudah `30_`); yang benar-benar baru bagi Paper 3 adalah
> **open-set scorer, novelty clustering, pelabelan (oracle+LLM), class-incremental +
> replay, guardrail, dan closed-loop AWS**.
>
> **Catatan penempatan:** notebook-notebook di atas **tetap** di `../unswnb-15/notebooks/`
> (tidak digandakan ke `evolusion/`). `shared/` hanya memuat artefak kecil hasil (JSON)
> + skrip extractor referensi. Kalau nanti Paper 3 butuh notebook sendiri, dibuat baru
> di `evolusion/notebooks/` dengan merujuk hasil Paper 1.

---

## 2. Konteks & Kontinuitas dari Paper 1

Aset & temuan Paper 1 yang dipakai (semua nyata, lihat `../unswnb-15/documentation.md`):

- **9 fitur SFM Model A** (irisan tervalidasi CIC ↔ UNSW): `dur, spkts, dpkts, sbytes,
  dbytes, smean, dmean, sload, dload`. (swin/dwin dibuang — TCP window mismatch;
  sinpkt/dinpkt = Model B, tidak menolong generalisasi.)
- **SFM valid** — joint training ~in-domain di kedua jaringan (fitur cukup ekspresif).
- **Cross-network kolaps** — model single-source jatuh ke MCC ≈ 0 lintas-jaringan;
  kalibrasi ~1% label (atau mixup) memulihkan. Relevan: open-set & labeling harus
  tahan *distribution shift* antar-jaringan.
- **Audit satuan (deployment):** `duration` wajib **mikrodetik** saat runtime NFStream
  agar cocok scaler CIC (§18.3 Paper 1). Gate sanity dipertahankan di runbook.

**Perbedaan mendasar Paper 3 (kerja baru):**
- Paper 1 **biner**; Paper 3 **multi-class** → perlu **latih ulang model known multi-class**
  pada 9 fitur SFM (T1).
- Taksonomi label CIC vs UNSW **berbeda** → perlu **skema label multi-class terpadu**
  (pemetaan kategori) — isu baru khusus multi-class (T1).

---

## 3. Basis Kelas *Known* (dari dataset multi-class yang sudah diinspeksi)

Kedua dataset sudah punya label multi-class nyata (hasil inspeksi Paper 1):

- **CSE-CIC-IDS2018** — Benign + 14 kelas serangan; kategori besar: **Brute-Force, DoS,
  DDoS, Web (SQL Injection), Infiltration, Botnet**.
- **UNSW-NB15** — 10 kelas `attack_cat`: **Normal, Generic, Exploits, Fuzzers, DoS,
  Reconnaissance, Analysis, Backdoor, Shellcode, Worms**. Class imbalance parah
  (mis. Worms hanya 44 record) — perlu diperhatikan saat membentuk kelas & metrik (MCC).

Kelas-kelas inilah **basis known**. Untuk skenario "serangan baru", sebagian kelas
**ditahan (held-out)** dan diperkenalkan kemudian sebagai kelas *unknown*.

---

## 4. Komponen 1 — Open-Set Recognition ("ini jenis baru")

Menjawab **"jaraknya terlalu jauh dari kelas dikenal → unknown".**

Model multi-class *known* memberi prediksi + skor. Sebuah flow ditandai **unknown**
bila jauh dari semua kelas dikenal. Dua mekanisme (basis + pembanding):

- **(Utama) Jarak Mahalanobis** ke centroid tiap kelas di ruang 9-fitur SFM:
  $$d_k(x) = \sqrt{(x-\mu_k)^\top \Sigma_k^{-1} (x-\mu_k)}, \qquad \text{unknown jika } \min_k d_k(x) > \tau.$$
  Ambang $\tau$ dikalibrasi dari distribusi jarak data known (mis. persentil-99).
- **(Pembanding murah) Confidence-based** — probabilitas maksimum rendah / entropi
  tinggi ⇒ unknown.

> **Catatan kejujuran (risiko diketahui):** XGBoost cenderung **overconfident** pada
> input tak-dikenal (memberi prob tinggi ke kelas salah). Karena itu confidence murni
> mungkin lemah untuk open-set; **wajib diuji, bukan diasumsikan**. Mahalanobis
> dijadikan basis; bila keduanya kurang, **peningkatan opsional**: ruang embedding
> terlatih (supervised contrastive / autoencoder) agar "jarak" lebih bermakna —
> ditahan sebagai eskalasi, bukan default (menjaga kesederhanaan XGBoost Paper 1).
> Metrik penilaian: **AUROC known-vs-unknown**.

---

## 5. Komponen 2 — Novelty Clustering ("kumpulan unknown → kandidat kelas baru")

Menjawab **"membuat kelas baru dari kumpulan unknown".** Satu flow jauh ≠ kelas baru
(bisa outlier/noise). Alur dua-tahap:

1. Flow unknown masuk **buffer unknown** (belum jadi kelas).
2. **Clustering** buffer dengan **HDBSCAN** di 9-fitur SFM. Cluster yang **padat +
   persisten lintas-waktu** (muncul berulang, bukan sekali) → **kandidat kelas baru**.
   Outlier sporadis dibuang.

Target ideal: bila diinjeksi "3 jenis serangan baru", clustering memunculkan
**≈ 3 cluster** yang stabil.

> **Catatan kejujuran:** cluster ≠ selalu = 1 jenis serangan (dua jenis mirip bisa
> menyatu; satu jenis bisa pecah). Dilaporkan apa adanya; kualitas cluster diukur
> (mis. homogeneity/ARI terhadap ground-truth lab).

---

## 6. Komponen 3 — Pelabelan Kandidat Kelas Baru

Menjawab **"dilabeli oleh sistem (LLM/oracle)".** Dua jalur, dengan pembagian peran
yang menjaga klaim inti tetap kokoh:

- **(Jalur utama) Oracle terjadwal.** Di lab AWS, serangan **kita sendiri yang
  jadwalkan** → ground-truth (timestamp + src_ip attacker + jenis) **100% akurat**,
  gratis. Ini basis pembuktian bahwa adaptasi berhasil — **tidak bergantung** akurasi LLM.
- **(Jalur tambahan / kontribusi) LLM auto-name.** Sistem menghitung **profil statistik
  tiap cluster** (mis. "durasi sangat panjang, paket forward sedikit, rate rendah,
  koneksi persisten ke port 80") lalu LLM memetakan profil itu ke **taksonomi serangan**
  (mis. "mirip slow-rate DoS / Slowloris"). LLM = *analis penamaan cluster*, **bukan**
  classifier per-flow. **Akurasi penamaan LLM diukur & divalidasi terhadap oracle**
  (mis. "LLM benar menamai 2 dari 3 cluster").

> **Catatan kejujuran:** fitur = 9 angka statistik flow; LLM **tidak** melihat paket
> mentah, jadi tak bisa mengklasifikasi per-flow secara andal. Posisinya sengaja
> dibatasi ke penamaan/atribusi cluster + selalu dibandingkan oracle. Bila LLM meleset,
> novelty inti (open-set + class-incremental) tetap berdiri.

---

## 7. Komponen 4 — Class-Incremental Update + Replay Memory + Guardrail

Menjawab **"update pakai data terbaru + memory data lama, lolos validasi baru menggantikan".**

1. **Update inkremental** — tambah kelas baru (kelas ke-N+1, N+2, …) ke model multi-class.
2. **Replay memory** — data baru (kelas baru berlabel) **digabung** dengan buffer
   sampel representatif kelas lama → cegah **catastrophic forgetting**. Strategi buffer
   (reservoir vs class-balanced) ditentukan dari eksperimen; efek "dengan vs tanpa
   memory" diukur eksplisit (ablation).
3. **Guardrail promosi** — model hasil update = **kandidat**, belum dipakai. Promosi
   hanya jika lolos di **holdout tepercaya**:
   - **recall kelas LAMA tidak turun** (no forgetting), DAN
   - **recall kelas BARU naik dari ~0** (adaptasi berhasil).
   Gagal → **rollback**, model lama dipertahankan (anti-poisoning & anti-osilasi).

---

## 8. Metodologi Eksperimen — Tiga Skenario Progresif

Semua memakai model **multi-class XGBoost** pada **9 fitur SFM**, metrik utama
**MCC + recall per-kelas + forgetting measure + AUROC open-set**.

### 8.1 Skenario A — Held-out Classes (dalam satu dataset) — PoC terkontrol
- Latih model *known* pada sebagian kelas (mis. 5 kelas CIC), **tahan** beberapa kelas
  sebagai "serangan baru".
- Stream data uji: mula-mula kelas known, lalu masukkan kelas held-out.
- Buktikan: model statis **buta** pada held-out (recall ≈ 0) → open-set menandai unknown
  → clustering memunculkan kandidat → adaptasi → recall baru naik, recall lama tetap.
- Paling bersih untuk membuktikan mekanisme class-incremental.

### 8.2 Skenario B — Cross-Dataset Novelty (lintas-jaringan) — lebih menantang
- Kelas *known* dari CIC; kelas **khas UNSW** (mis. Worms, Shellcode, Backdoor,
  Reconnaissance) muncul sebagai "baru".
- Menguji open-set + labeling + incremental **di tengah distribution shift** (menyambung
  narasi Golden Pair Paper 1). Diharapkan lebih sulit; dilaporkan apa adanya.

### 8.3 Skenario C — AWS Online (puncak) — serangan baru dijalankan live
Empat fase (memanfaatkan ground-truth lab):
1. **Base:** deploy model dengan **N jenis serangan** (mis. 5: SSH-BF, FTP-BF, Slowloris,
   GoldenEye, SYN-flood). Uji N jenis → baseline bagus.
2. **Serangan baru masuk:** jalankan **M jenis baru** (mis. 3: Hulk, UDP-flood,
   SlowHTTPTest). Ukur pada model statis: recall kelas baru ≈ 0 (**bukti gap**); open-set
   menandai unknown; clustering → ≈ M cluster.
3. **Adaptasi:** label (oracle + LLM auto-name) → update (data baru + replay) → guardrail
   → promosi. Ukur: recall M kelas baru **naik dari 0**, recall N lama **tetap**.
4. **Guardrail/poisoning (opsional):** kandidat yang merusak kelas lama **ditolak**
   (rollback) — menjawab kekhawatiran keamanan.

**Gambar headline:** confusion matrix sebelum vs sesudah adaptasi (kolom kelas baru dari
"buta" → "terdeteksi", kolom lama tetap) + kurva recall-per-kelas vs waktu (statis vs adaptif).

### 8.4 Validasi Silang dengan Amazon GuardDuty (pembanding pihak-ketiga)
Saat testing online (Skenario C), aktifkan **Amazon GuardDuty** pada VPC yang sama sebagai
**pembanding validasi independen** untuk jenis serangan.

- **Peran:** *cross-check* pihak-ketiga, **bukan** ground-truth (ground-truth tetap oracle
  terjadwal). GuardDuty men-*confirm* bahwa serangan yang kita jalankan memang "terlihat"
  oleh sistem deteksi kelas industri.
- **Perbandingan yang diukur:** cakupan deteksi (jenis apa yang kena/tak-kena), **latensi
  deteksi** (sistem kami vs GuardDuty), dan **granularitas taksonomi** (finding type
  GuardDuty vs kelas kami).

> **Catatan kejujuran (wajib, hindari overclaim):** GuardDuty berbasis **VPC Flow Logs,
> DNS logs, CloudTrail, threat-intel** — **bukan** fitur flow CICFlowMeter/NFStream. Maka:
> (a) taksonomi *finding* GuardDuty ≠ label kelas kita (perlu pemetaan longgar); (b)
> sebagian serangan (mis. variasi DoS aplikasi) mungkin **tidak muncul** di GuardDuty atau
> muncul beda. Framing yang benar: sistem kami **melengkapi** GuardDuty (menemukan &
> mengklasifikasi jenis baru dari fitur flow; GuardDuty memvalidasi dari sudut
> log/threat-intel), **bukan** "mengalahkan" GuardDuty. Bila di beberapa kasus sistem kami
> lebih cepat/lebih spesifik, dilaporkan apa adanya sebagai temuan, bukan klaim umum.

---

## 8a. Status Implementasi Notebook (BACA INI untuk tahu progres kode)

Notebook eksperimen ada di `evolusion/notebooks/` (dijalankan di SageMaker, mulai `01_`).
**Dibuat = kode sudah ditulis & valid; belum tentu sudah dijalankan** (angka nyata muncul
setelah Run All di SageMaker + dataset tersedia). Peta lengkap di `notebooks/README.md`.

| Notebook | Tahap | Status kode | Fungsi singkat | Output utama (→ S3 `evolusion/<prefix>/`) |
|---|---|---|---|---|
| `01_known_base_multiclass.ipynb` | T1 | **DIBUAT** (belum dirun) | Latih model **known** multi-class (kelas held-out disembunyikan); hitung **centroid `mu` + inv-kovarians per-kelas** | `model_known_<DS>.json`, **`deploy_meta_mc_<DS>.json`** (scaler+mu+inv_cov+labels), `known_base_results.json`, `known_base_summary.csv`, `confusion_known_<DS>.png` → `known_base/` |
| `02_openset_scorer.ipynb` | T3 | **DIBUAT** (belum dirun) | Skor open-set **Mahalanobis (utama)** vs **confidence**; uji pemisahan **known (test) vs held-out**; **AUROC known-vs-unknown** + kalibrasi τ (p99 jarak known) | `openset_results.json` (AUROC maha/conf, τ, TPR/FPR), `openset_summary.csv`, `openset_<DS>.png` (hist + ROC) → `openset/` |
| `03_novelty_clustering.ipynb` | T3b | **DIBUAT** (belum dirun) | **HDBSCAN** pada flow held-out yang **lolos gerbang open-set** (dist>τ); cek **n_cluster ≈ M** (jumlah jenis baru); ukur **homogeneity & ARI** vs ground-truth | `novelty_results.json` (n_cluster, homogeneity, ARI, komposisi), `novelty_summary.csv`, `novelty_<DS>.png` (PCA 2D), **`cluster_profile_<DS>.csv`** (profil statistik cluster → bekal LLM) → `novelty/` |
| `04_drift_detector.ipynb` | T2 | **DIBUAT** (belum dirun) | Formalkan **$W_1$ jendela-geser + CUSUM** (dari PoC `30_`); stream CIC→UNSW(→AWS); **delay deteksi** + **sensitivitas W**; alarm drift = sinyal kelas baru mungkin muncul | `drift_results.json` (mu0, thr, alarm, delay, sensitivitas), `drift_sensitivity.csv`, `drift_stream_W1000.png` → `drift/` |

**Alur data antar-notebook:** `01` memproduksi `deploy_meta_mc_<DS>.json` (mu + inv_cov per-kelas)
→ **`02` & `03` wajib memakainya** untuk skor Mahalanobis. Keduanya auto-unduh artefak `01`
dari S3 bila tak ada lokal. Flow held-out yang skornya **di atas τ** = *unknown* → `03`
meng-cluster-nya jadi kandidat kelas baru → `cluster_profile_<DS>.csv` jadi input pelabelan
(oracle + LLM) di `05` (belum dibuat).

**Keputusan penting yang HARUS konsisten lintas-notebook:**
- **`HELDOUT`** (kelas yang disembunyikan = "serangan baru") diset di SEL 1 tiap notebook.
  Default: `CIC=[Botnet, Infiltration]`, `UNSW=[Worms, Shellcode, Backdoor]`. **Jika diubah di
  `01`, WAJIB diubah sama di `02`** (dan notebook berikutnya).
- **Split test known** direkonstruksi identik (merge_rare kelas <200 → `Other-rare`, split 0.3,
  seed 42) agar tak ada kebocoran.
- **Pilih file UNSW berdasarkan JUMLAH RECORD terbanyak (~175k = latih)**, bukan nama berkas
  (isi berkas UNSW tertukar dgn namanya — Paper 1 §9.3).

---

## 9. Rencana Kerja Bertahap (Roadmap)

| Tahap | Kegiatan | Status |
|---|---|---|
| T1 | Latih ulang model **multi-class** (9 fitur SFM) + skema label terpadu CIC/UNSW | **KODE DIBUAT** (`01_known_base_multiclass.ipynb`) — belum dirun di SageMaker |
| T2 | Detektor drift streaming ($W_1$ + CUSUM); kalibrasi $w$, $h$, garis dasar | **KODE DIBUAT** (`04_drift_detector.ipynb`, lanjutan PoC `30_` §1b) — belum dirun di SageMaker |
| T3 | Open-set scorer: Mahalanobis (utama) + confidence (pembanding); kalibrasi $\tau$; ukur AUROC known-vs-unknown | **KODE DIBUAT** (`02_openset_scorer.ipynb`) — belum dirun di SageMaker |
| T3b | Novelty clustering (HDBSCAN); uji "≈ M cluster" pada held-out; ukur homogeneity/ARI | **KODE DIBUAT** (`03_novelty_clustering.ipynb`) — belum dirun di SageMaker |
| T4 | Pelabelan: oracle terjadwal + LLM auto-name dari profil statistik; ukur akurasi LLM vs oracle | Belum |
| T5 | Class-incremental update + replay memory; ablation dengan vs tanpa memory (forgetting) | Belum |
| T6 | Guardrail promosi (recall lama tetap & baru naik); uji skenario poisoning/rollback | Belum |
| T7 | **Skenario A** (held-out dalam dataset) end-to-end offline | Belum |
| T8 | **Skenario B** (cross-dataset novelty) offline | Belum |
| T9 | **Skenario C** (AWS online, 4 fase) — injeksi serangan baru live; ukur recall/MCC/FAR seiring waktu | Belum |
| T9b | Validasi silang **Amazon GuardDuty** (cakupan, latensi, pemetaan taksonomi) selama Skenario C | Belum |
| T10 | Penulisan naskah + gambar/tabel dari hasil nyata | Belum |

---

## 10. Prinsip & Catatan Kerja

- **Kejujuran data mutlak.** Semua angka dari eksperimen nyata & reproducible.
- **Keputusan desain yang sudah disepakati:**
  - Model **multi-class** (bukan biner).
  - Open-set: **Mahalanobis di 9-fitur SFM** basis, **confidence** pembanding;
    embedding contrastive sebagai eskalasi opsional.
  - Pelabelan: **oracle terjadwal = jalur utama**; **LLM = kontribusi tambahan yang
    divalidasi ke oracle**.
  - Update: **data baru + replay memory**; **guardrail** wajib sebelum promosi.
- **Risiko yang dicatat terbuka (diuji, bukan diasumsikan):**
  1. XGBoost overconfident → open-set murni-confidence bisa lemah.
  2. Cluster ≠ selalu 1 jenis serangan (menyatu/pecah).
  3. LLM dari 9 angka statistik terbatas → dibatasi ke penamaan cluster + validasi oracle.
- **Biaya AWS.** Deployment jangka panjang (3–7 hari) berbiaya; rencanakan instans hemat,
  jadwal on/off, pemantauan biaya.
- **Stabilitas loop.** Hindari osilasi update; guardrail + histeresis ambang jadi pengaman.

---

## 11. Struktur Berkas Paper 3 (folder `evolusion/`)

| Berkas | Isi |
|---|---|
| `documentation.md` (dokumen ini) | "Apa & mengapa" — kebutuhan, gap, metode, roadmap, **status notebook (§8a)** |
| `paper3.tex` | Naskah paper (kerangka, diisi setelah eksperimen) |
| `notebooks/` | **Notebook eksperimen** (mulai `01_`) — peta di `notebooks/README.md`; status di §8a |
| `shared/` | **Aset warisan Paper 1** (dipakai ulang, tidak diulang) — lihat `shared/README.md` |
| `aws/runbook.md` | "Bagaimana di AWS" — operasi deployment & injeksi serangan baru saat testing |

**Isi `shared/` (disalin dari `../unswnb-15/`, hasil nyata Paper 1):**
- `feature_inventory.json` — inventaris fitur CIC (68) & UNSW (42) + extractor.
- `mapping_validation.json` — hasil validasi SFM (dasar 9 fitur Model A).
- `model_efficiency.json` — profil efisiensi (referensi; **wajib diukur ulang** untuk multi-class).
- `extract9_infer_reference.py` — ekstraksi 9-fitur NFStream + audit satuan (`duration`=µs);
  `extract9()` dipakai apa adanya, head inferensi diganti multi-class + open-set.

> Aset besar yang **tidak** ikut repo (dataset `.pkl`/CSV, artefak model & scaler
> deployment) tetap di S3/`.gitignore` — sama seperti Paper 1. Paper 3 akan punya artefak
> **multi-class** sendiri (model + `deploy_meta_mc.json` berisi centroid/kovarians per-kelas
> untuk skor Mahalanobis). Detailnya di `shared/README.md`.

> Sumber kebenaran detail tetap notebook + `git log`. Dokumen ini pengingat tingkat-tinggi,
> bukan pengganti kode.
