# Masukan Reviewer — Paper Q1 (UNSW-NB15 × CSE-CIC-IDS2018)

> Rangkuman masukan reviewer atas progres saat ini (setelah T1–T9 + naskah `paper-q1-id.tex`).
> Dipakai sebagai daftar tindak lanjut menuju kelayakan Q1. Status setiap butir ditandai.

---

## A. Kekuatan Utama (dipertahankan)

Reviewer menilai tiga hal berikut sebagai nilai jual kuat yang **harus dipertahankan**:

1. **Kejujuran akademis (Prinsip Kejujuran Data).**
   Pengakuan terbuka bahwa model *robust* runtuh terhadap serangan *adaptive white-box*
   (MCC $0{,}99 \rightarrow 0{,}25$–$0{,}43$) dinilai sebagai penulisan ilmiah yang matang —
   menunjukkan pemahaman *obfuscated gradients* dan *false robustness*.
   *(Sumber: T9, §16 dokumentasi / §9.2 naskah.)*

2. **Kasus riil TCP Window Mismatch pada SFM.**
   Temuan `swin`/`dwin` (UNSW) praktis biner {0,255} vs `Init Fwd/Bwd Win Byts` (CIC) kontinu
   0–65535 adalah kontribusi empiris berharga: membuktikan *extractor mismatch* adalah masalah
   **semantik nyata**, bukan sekadar beda nama kolom.
   *(Sumber: T2, §10.7 dokumentasi / §3.2 naskah.)*

3. **Pemisahan konseptual yang jelas.**
   Terbukti empiris bahwa *adversarial-robustness* dan *cross-network-robustness* adalah dua
   masalah berbeda yang butuh solusi berbeda.
   *(Sumber: T5 + T8, §12/§15 dokumentasi.)*

---

## B. Saran Taktis untuk Kelayakan Q1

### 1. Perdalam formulasi matematika (Metodologi — §5 & §9.1 naskah)
Reviewer Q1 (khususnya IEEE Transactions) sensitif terhadap kedalaman matematika; metode
tidak cukup dijelaskan naratif.

- **Aproksimasi gradien numerik (§5).** Tuliskan eksplisit persamaan *central finite-difference*
  untuk mengestimasi $\nabla_x L$ pada XGBoost yang *non-differentiable*:
  $$\hat{\nabla}_{x_i} L \approx \frac{L(\mathbf{x}+h\mathbf{e}_i) - L(\mathbf{x}-h\mathbf{e}_i)}{2h}$$
- **Kendala fungsional (§9.1).** Formulasikan sebagai *constrained optimization* dengan ruang
  perturbasi layak $\mathcal{S}_{valid}$, mis.:
  - fitur biner/kategori: batas langkah $\delta = 0$,
  - jumlah paket bulat: $spkts, dpkts \in \mathbb{Z}^{+}$,
  - konsistensi rasio: $sbytes \ge spkts$ (tiap paket $\ge 1$ byte),
  - monotonic *add-only* pada pkts/bytes/duration.
- **Status:** BELUM — perlu menambahkan blok persamaan pada `paper-q1-id.tex`.

### 2. Analisis teoretis "Asimetri Performa" (Diskusi — §10 naskah)
Pertanyaan yang pasti muncul: *mengapa CIC→UNSW (MCC ~0,65–0,68) selalu lebih rendah dari
UNSW→CIC (MCC ~0,80–0,91)?*

- **Arah perbaikan:** tambah sub-bab diskusi dari sudut **kompleksitas dataset**.
  UNSW-NB15 dibangkitkan IXIA PerfectStorm — variasi serangan lebih kompleks & *noise* lebih
  tinggi (9 kelas), sedangkan CSE-CIC-IDS2018 berbasis *testbed* lebih terstruktur.
  *Distribution shift* dari domain "sederhana" (CIC) ke "kompleks" (UNSW) inheren lebih sulit.
- **Konsisten dengan data kita:** CORAL juga asimetris (T6) — arah dari sumber kaya lebih sulit.
- **Status:** BELUM — perlu sub-bab analisis asimetri.

### 3. Bingkai ulang "Single Model XGBoost" jadi nilai jual (Framing — §3.3 & Keterbatasan)
Di level Q1, dewan editor peduli **Green AI** dan **Edge Computing**. Ubah dari "keterbatasan"
menjadi **keunggulan efisiensi komputasi**.

- **Argumen:** di *edge* nyata (smart router, IoT gateway), *ensemble* berat / *deep learning*
  tak realistis karena boros memori & CPU. XGBoost tunggal = *Edge-friendly Robust NIDS*.
- **Bukti kuantitatif yang perlu diukur (nyata, jangan dikarang):**
  - ukuran biner model XGBoost tunggal (mis. puluhan KB),
  - *inference latency* per *flow* (mis. mikrodetik).
- **Status:** BELUM — perlu eksperimen ringan ukur ukuran model & latency, lalu tulis argumennya.

### 4. Visualisasi pergeseran distribusi (t-SNE / UMAP) — gambar tambahan
Untuk membuktikan celah = *distribution shift* (bukan fitur), tambahkan visualisasi 2D.

- **Rencana:** t-SNE atau UMAP pada 9 fitur irisan SFM; plot sebaran CIC (biru) vs UNSW (merah).
  Tunjukkan *overlap* minim sebelum kalibrasi, dan penyelarasan setelah 1% label / *mixup*.
- **Integrasi:** jadi gambar baru (mis. `fig6_tsne_shift.png`) di `figure-q1/`; tambah ke
  `make_figures.py` (butuh subset data → dijalankan di SageMaker karena perlu CSV/pkl).
- **Status:** BELUM — perlu notebook/skrip t-SNE + gambar.

### 5. Sempurnakan Future Work AWS Deployment — diagram arsitektur
Agar rencana T10 tidak terlihat "janji kosong", tambahkan *deployment blueprint diagram*.

- **Rencana:** diagram alur — sensor penangkap paket (EC2 + NFStream) → ekstraksi fitur →
  penyelarasan via SFM → model XGBoost *robust* → deteksi *real-time*; ukur FAR selama 3–7 hari.
- **Integrasi:** buat diagram (TikZ→PNG atau draw.io) → `figure-q1/`; rujuk di §12 naskah.
- **Status:** BELUM — perlu diagram arsitektur deployment.

---

## C. Ringkasan Tindak Lanjut (checklist)

| # | Tindakan | Lokasi | Butuh SageMaker? | Status |
|---|---|---|---|---|
| B1a | Persamaan finite-difference gradien | naskah §5 | tidak | **SELESAI** (Pers. 1) |
| B1b | Formulasi constrained optimization $\mathcal{S}_{valid}$ | naskah §9.1 | tidak | **SELESAI** (Pers. 3–4) |
| B2 | Sub-bab analisis asimetri performa (kompleksitas dataset) | naskah §10 | tidak | **SELESAI** (§10.1) |
| B3 | Ukur ukuran model + inference latency; bingkai Edge/Green AI | naskah §3.4 + eksperimen | ya (ukur) | **Sebagian**: framing + tabel placeholder selesai (§3.4); angka nyata menunggu pengukuran |
| B4 | Visualisasi t-SNE/UMAP distribution shift | `figure-q1/` + naskah §7 | ya (data) | Belum (butuh SageMaker) |
| B5 | Diagram arsitektur deployment AWS | `figure-q1/` + naskah §12 | tidak | **SELESAI** (fig6, §12) |
| T10 | Eksekusi deployment AWS 3–7 hari, ukur FAR (nyata) | eksperimen | ya (AWS) | **Rencana matang** (`aws/deployment-plan.md`, adopsi pengalaman NIDS-01); eksekusi menunggu |

> **Catatan kejujuran:** semua angka baru (ukuran model, latency, FAR, koordinat t-SNE) wajib
> berasal dari eksperimen nyata yang dapat direproduksi — konsisten dengan prinsip kerja kita.

---

## D. Prioritas yang Disarankan (urutan kerja)

1. **B1a, B1b, B2** — murni penulisan (tanpa SageMaker), dampak besar untuk kedalaman Q1.
2. **B4** — visualisasi t-SNE (butuh data; kuat sebagai bukti *distribution shift*).
3. **B3** — ukur ukuran model + latency (ringan, angka konkret untuk framing Edge/Green AI).
4. **B5** — diagram arsitektur deployment.
5. **T10** — eksekusi AWS nyata (biaya & waktu), lalu isi hasil FAR + buat versi English.


---

## E. Peer Review Q1 Kedua — Rekomendasi: MINOR REVISION

Tinjauan sejawat kedua atas naskah `paper-q1-id.tex` (setelap tindak lanjut A–B sebelumnya).
Rekomendasi: **Minor Revision** — dinilai hampir siap untuk *Computers & Security* (Elsevier)
atau *IEEE TDSC*. Empat poin revisi minor:

| Poin | Isi | Butuh eksekusi nyata? | Status |
|---|---|---|---|
| **A** | Isi placeholder `[TBD]` Tabel efisiensi (§3.4): ukuran model, latensi inferensi, throughput @1 vCPU — KRITIS (pemicu desk-reject) | Ya (ukur model 9-fitur) | **Menunggu pengukuran** — jangan diisi karangan |
| **B** | Definisi formal operator proyeksi $\Pi_{\mathcal{S}_{valid}}$ (algoritma 7 langkah) | Tidak | **SELESAI** (§8.1 naskah, langkah 1–7 + urutan) |
| **C** | Strategi pertahanan potensial thd serangan adaptif (multi-step PGD functional-constrained; randomized smoothing / decision-boundary smoothing) | Tidak | **SELESAI** (paragraf "Arah mitigasi" §sec:awb) |
| **D** | Konsistenkan format referensi gaya IEEE | Tidak | **SELESAI** (bibliography: in Proc., venue italik, halaman, kota) |

**Kekuatan yang diakui reviewer:** integritas ilmiah (pelaporan jujur runtuh adaptive),
studi kasus TCP window mismatch, functional-preserving evasion, analisis asimetri, gambar
kualitas publikasi.

**Sisa satu-satunya penghalang submit = Poin A** (angka efisiensi nyata). Bisa diukur begitu
model 9-fitur tersedia (tidak butuh deployment AWS penuh, cukup 1 vCPU + model). Detail di
`documentation.md` §17.

### E.1 Skema AWS T10 — 3-EC2 (persis NIDS-01) — SUDAH DIDESAIN
Keputusan: memakai skema **3-EC2 mereplikasi NIDS-01** (Attacker public; Target & Analyzer
private + NAT) demi **comparability** dengan paper NIDS-01. Sudah disiapkan lengkap, eksekusi
menunggu kesiapan:

| Artefak | Isi | Status |
|---|---|---|
| `aws/unsw-vpc-3ec2.yaml` | CloudFormation 1-stack: VPC + public/private subnet + IGW + NAT + SG + IAM SSM/S3 + 3 EC2 | **SELESAI (desain)** |
| `aws/capture_target.sh` | Capture di Target (`-i ens5`), mode far / detect | **SELESAI** |
| `aws/attack_scenario.sh` | Skenario serangan Fase 2 (SSH brute / Slowloris / SYN flood), clean & evasion | **SELESAI** |
| `aws/unsw_extract_infer.py` | Analyzer: NFStream 9-fitur SFM → z-score → XGBoost; mode `far` (FAR) & `detect` (MCC/F1) | **SELESAI** |
| `aws/runbook.md` | Langkah eksekusi + resume cepat + hapus infra + slot hasil nyata | **SELESAI** |
| `aws/cost-estimate.md` | Biaya: Fase 2 ≈$1; FAR 3 hari ≈$13–15 (terjadwal ≈$4–6); 7 hari ≈$30–33 | **SELESAI** |

Penyederhanaan vs NIDS-01: Model A 9-fitur tanpa TCP window → tak perlu custom window plugin.

Dua jalur mengisi Poin A/T10:
- **Cepat (Poin A saja):** `notebooks/09_model_efficiency.ipynb` di SageMaker (tanpa AWS).
- **Lengkap (Poin A + FAR + deteksi real-traffic):** deploy `unsw-vpc-3ec2.yaml`, ikuti
  `runbook.md` — mengisi FAR (§12 naskah), deteksi, dan latensi @1 vCPU (Tabel §3.4).
- **Setelah selesai:** hasil → S3, lalu `delete-stack` (biaya nol); pengetahuan tersimpan di
  `runbook.md` untuk pengulangan cepat.
