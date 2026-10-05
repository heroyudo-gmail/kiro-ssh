# Dokumentasi Percobaan — Paper 4 (Federated Cross-Network NIDS via SFM)

> **Judul kerja:** *Federated Cross-Network NIDS via Semantic Feature Mapping:
> can a shared semantic feature space solve feature-schema heterogeneity in
> federated learning?*
>
> **Fungsi file ini:** memori persisten + laporan hasil Paper 4. Kalau konteks
> hilang/reset, BACA FILE INI DULU. Struktur mengikuti pola Paper 2:
> - **Bagian I — Laporan Hasil** (A–J): narasi + rumus + tabel + grafik.
> - **Bagian II — Memori Operasional** (K–P): peta notebook↔tabel, status, tugas,
>   S3, konvensi.
>
> **STATUS: PERENCANAAN (Fase 0).** Belum ada eksperimen; semua angka hasil `[TBD]`.
> **JANGAN mengarang angka** — placeholder `[TBD]`/`--` sampai hasil nyata.
>
> **Prasyarat rilis:** Paper 4 di-submit SETELAH Paper 1 (SFM) accepted. Kita
> KERJAKAN sekarang dengan asumsi Paper 1 diterima; sitasi Paper 1 sebagai fondasi.
>
> **PETA MEMORI:** Paper 1+2 di `unswnb-15/`; Paper 3 (online) di `evolusion/`;
> **Paper 4 (federated) = folder `federated/` ini.** Dataset dipakai bersama dari
> root repo (gitignored).

---

# BAGIAN I — LAPORAN HASIL (baca runut)

> Angka: titik desimal di sini (markdown), koma di `.tex`. Semua `[TBD]` sampai nyata.

## A. Tujuan, pertanyaan riset & novelty

**Masalah yang diangkat.** Dalam federated learning (FL) lintas-organisasi, tiap
klien lazim memakai **alat ekstraksi fitur berbeda** (mis. CICFlowMeter untuk
CSE-CIC-IDS2018 vs Argus/Bro untuk UNSW-NB15), sehingga **skema fitur antar-klien
berbeda**. FedAvg standar mengasumsikan ruang fitur identik antar-klien — asumsi yang
runtuh di dunia nyata (ini **Gap 5/b** di literatur: *feature-schema heterogeneity*
belum tertangani; literatur hanya pakai *feature alignment* implisit, bukan peta
semantik tervalidasi).

**Pertanyaan riset:**
> Dapatkah **Semantic Feature Mapping (SFM)** — peta fitur semantik tervalidasi
> statistik dari Paper 1 — berfungsi sebagai *enabler* federasi antar-klien
> berskema-fitur-beda, dan seberapa jauh federated-SFM menutup celah performa
> terhadap model terpusat (centralized) tanpa memusatkan data mentah?

**Novelty (SATU sumbu, tajam — bukan framework 4-in-1):**
> **SFM sebagai jembatan interoperabilitas fitur dalam FL.** Pertama kali ruang
> fitur semantik yang tervalidasi statistik dipakai agar klien berskema-beda
> (CIC vs UNSW) dapat berfederasi dalam satu model global tanpa berbagi data mentah.
> Kebaruan BUKAN "menambah FL ke pipeline lama", melainkan menunjukkan SFM
> **menyelesaikan** heterogenitas skema-fitur yang menggagalkan FL lintas-dataset.

**Posisi vs Paper 1–3 (anti salami-slicing):**
- Paper 1: SFM + few-shot, generalisasi lintas-jaringan, model **terpusat**.
- Paper 2: ketahanan adversarial + interaksi dua-sumbu, model **terpusat**.
- Paper 3: adaptasi online terhadap drift.
- **Paper 4 (ini):** sumbu baru = **desentralisasi/privasi**. SFM dipindah ke
  setting **federated**; kontribusi orisinal = SFM sebagai enabler federasi
  lintas-skema, diukur vs centralized/local-only. Few-shot & adversarial SENGAJA
  TIDAK dimasukkan (dicadangkan untuk kemungkinan Paper 5), agar klaim tetap tajam.

**Hipotesis (diuji, dilaporkan jujur apa pun hasilnya):**
- H1: FL di ruang SFM >> FL di ruang fitur mentah tak-selaras (SFM = enabler).
- H2: centralized ≥ federated-SFM ≥ local-only (urutan wajar; ukur selisihnya).
- H3: non-IID antar-klien menurunkan performa; seberapa jauh SFM meredamnya.

## B. Setup eksperimen & KEPUTUSAN ARSITEKTUR

**Keputusan arsitektur (penting — beda dari Paper 1/2).**
XGBoost (backbone Paper 1/2) **tidak natural untuk FL** (agregasi bobot pohon tak
langsung). Keputusan: model lokal = **MLP ringan pada 9 fitur SFM** (FedAvg lurus
atas bobot). XGBoost centralized tetap dilaporkan sebagai **jembatan ke Paper 1**
(sanity-check: MLP centralized ≈ XGBoost centralized pada 9 fitur SFM). Alasan &
trade-off didokumentasikan; ini keputusan desain utama Paper 4.

**Dataset:** CSE-CIC-IDS2018 ↔ UNSW-NB15 (PAKAI SFM 9-fitur yang SUDAH tervalidasi
Paper 1 — tidak validasi ulang). Fitur: duration, fwd_pkts, bwd_pkts, fwd_bytes,
bwd_bytes, fwd_mean, bwd_mean, src_load, dst_load.

**Skenario federasi:**
- **Skenario-A (inti):** 2 klien = {CIC, UNSW}, non-IID natural (beda skema asli →
  disatukan via SFM). Menguji pertanyaan riset langsung.
- **Skenario-B (perluasan):** K klien (mis. 4–10) via partisi non-IID per-dataset
  (shard berbasis kelas/subnet) untuk menguji skalabilitas & derajat non-IID.

**Baseline (wajib, pembingkai hasil):**
1. **Centralized** (upper bound; data digabung — hanya untuk perbandingan, bukan skenario privasi).
2. **Local-only** per-klien (lower bound; tanpa federasi).
3. **Federated-SFM** (usulan): FedAvg + pembanding FedProx.
4. **Ablasi kunci:** FL **tanpa** SFM (fitur mentah/interseksi naif) vs FL **dengan** SFM.

**Protokol evaluasi (warisi Paper 2):** metrik utama **MCC**; dilengkapi
recall/precision/F1 + balanced-accuracy (penting krn imbalance). **5 seed**
{13,42,101,202,303} + rerata±std + CI95 + uji signifikansi. Metrik FL tambahan:
**communication rounds** & **bytes/round** vs akurasi (kurva biaya-komunikasi).

### A.1 KRITIS — Dari mana 9 fitur SFM, tanpa klien berbagi data? (jawab reviewer)

> Ini titik yang PASTI diserang reviewer. Jawaban harus tegas: **SFM mapping adalah
> KESEPAKATAN SKEMA (public prior), BUKAN hasil belajar dari data gabungan.**

- **Penemuan 9 fitur (Paper 1), sekali & offline:** dibandingkan **definisi/semantik
  kolom** CICFlowMeter vs Argus/Bro (mis. "Flow Duration"≈"dur", "Tot Fwd Pkts"≈"spkts"),
  divalidasi statistik **pada tiap dataset secara terpisah** (distribusi per-fitur, bukan
  baris data). Hasil = **kamus pemetaan** (9 fitur irisan + rumus derivasi) = METADATA,
  beberapa baris teks. Ini pengetahuan domain, bukan data.
- **Dalam federasi (Paper 4): kamus SFM = public prior yang disepakati SEBELUM training.**
  Analogi: organisasi setuju memakai format laporan/NetFlow standar — tak perlu berbagi
  data. Alur:
  1. (offline, sekali) peneliti terbitkan kamus SFM dari Paper 1 → publik.
  2. (tiap klien, LOKAL & mandiri) terapkan kamus ke data SENDIRI → 9 fitur SFM lokal.
     Client-CIC pakai mapping CICFlowMeter; Client-UNSW pakai mapping Argus. TAK bertukar data.
  3. (federasi) kedua klien kini punya ruang fitur 9-dim yang SAMA secara semantik →
     FedAvg bobot MLP sah.
- **Yang TIDAK kita lakukan (anti-kebocoran):** fit mapping/normalisasi pada data GABUNGAN
  kedua klien; mengintip data mentah pihak lain.

**Isu normalisasi (z-score) — keputusan desain eksplisit (uji di Fase 1):**
- (a) **Per-client local z-score** (DEFAULT usulan): tiap klien pakai statistik lokalnya
  sendiri. Paling privacy-preserving; bila performa cukup → temuan bagus ("SFM + norm lokal
  sudah cukup untuk federasi").
- (b) Statistik global via secure aggregation (lebih selaras, butuh mekanisme tambahan).
- (c) Public reference statistics (acuan tetap dari dataset publik).
> Rencana: mulai (a); bila gap vs centralized besar, uji (b)/(c) sebagai ablasi. Laporkan jujur.

### A.2 SFM sebagai "interlingua" fitur: adapter per-tool (ketentuan onboarding klien)

> Penajaman dari A.1 (atas pertanyaan: "yang dibandingkan tool-nya ya?"). **Benar** —
> yang dipetakan adalah skema **tool ekstraktor fitur** (CICFlowMeter, Argus/Bro,
> NFStream, Zeek, ...), bukan datanya. SFM berfungsi sebagai **interlingua / lingua
> franca fitur**: tiap tool diterjemahkan ke 9 fitur SFM yang sama.

**Mekanisme (penting untuk arsitektur & klaim paper):**
- **Registry adapter publik:** kumpulan pemetaan `tool -> 9 fitur SFM`
  (mis. `adapter_cicflowmeter`, `adapter_argus`, `adapter_nfstream`). Tiap adapter =
  metadata (nama kolom sumber + rumus derivasi + catatan validasi), dibuat domain-expert
  **sekali per-tool**, bersifat **publik** (bukan data).
- **Onboarding klien baru dengan tool Z:**
  1. Ambil `adapter_Z` dari registry (publik).
  2. **Secara lokal & mandiri**, klien terapkan `adapter_Z` ke datanya SENDIRI -> 9 fitur SFM.
  3. Klien lalu berfederasi **hanya dalam bahasa 9 fitur SFM** (tukar bobot model).
- **Server TIDAK perlu tahu tool klien** maupun melihat datanya. Server hanya mengenal
  ruang 9 fitur SFM (interlingua). Klien tak perlu "melapor tool" ke server; cukup
  memastikan outputnya di ruang SFM.

**Ketentuan & batas kelayakan (dilaporkan JUJUR di paper):**
- Jika tool klien **sudah** punya adapter di registry -> gabung tanpa usaha tambahan.
- Jika **belum** -> perlu domain-expert membuat adapter baru (pemetaan + validasi definisi
  kolom) **sekali**. Jadi SFM **tidak sepenuhnya otomatis**: butuh adapter per-tool.
  Ini **keterbatasan nyata** -> akui di Limitations (perkuat kredibilitas, pola Paper 2).
- Adapter hanya sah bila tool target benar-benar mengukur fitur **yang bersesuaian secara
  semantik**. Bila sebuah tool tak mengukur suatu besaran (mis. bytes per-arah), fitur itu
  **tak dapat dipetakan** -> ada batas kelayakan. Contoh nyata Paper 1: TCP window CIC
  (kontinu) vs UNSW (biner) -> dibuang, tidak dipaksakan ekuivalen.
- **Privasi tetap utuh:** adapter = metadata publik; penerapan ke data terjadi LOKAL di
  klien; yang keluar node hanya bobot. Tidak ada pertukaran data mentah antar-klien/server.

**Implikasi untuk Paper 4:** kontribusi SFM bukan sekadar "satu pemetaan CIC-UNSW",
melainkan **pola interoperabilitas**: FL lintas-tool dimungkinkan oleh lapisan adapter
SFM. Eksperimen kita (CIC via CICFlowMeter-adapter, UNSW via Argus-adapter) adalah
**instansiasi konkret** pola ini dengan 2 tool/2 klien; generalisasi ke tool lain =
menambah adapter (future work bila perlu).

### Konfigurasi awal (DRAF — kalibrasi saat Fase 1, catat angka final)

**Model lokal (MLP pada 9 fitur SFM):**
- Arsitektur: input 9 → hidden [64, 32] (ReLU) → output 1 (sigmoid). Ringan agar
  Edge-friendly & komunikasi murah (konsisten semangat efisiensi Paper 1 nb09).
- Loss: binary cross-entropy; optimizer lokal: Adam (lr awal `1e-3`).
- Regularisasi: dropout 0.1–0.2 (kalibrasi); z-score fit train-only (warisi Paper 1).
- Catatan: arsitektur sengaja kecil; tujuan Paper 4 BUKAN mengejar MLP terbaik,
  melainkan menguji SFM sebagai enabler FL. Jaga MLP centralized ≈ XGBoost centralized
  pada 9 fitur (jembatan nb02); bila gap besar, naikkan kapasitas secukupnya & catat.

**Konfigurasi federated (DRAF):**
- Agregasi: FedAvg (baseline) + FedProx (`mu` ∈ {0.001, 0.01, 0.1}, pilih via validasi).
- Rounds komunikasi `R`: mulai 50 (naikkan sampai konvergen; laporkan kurva R vs MCC).
- Local epochs `E` per round: {1, 5} (uji sensitivitas; E besar memperparah drift non-IID).
- Client fraction `C`: 1.0 untuk skenario-A (2 klien); {0.5, 1.0} untuk skenario-B.
- Batch size lokal: 256 (sesuaikan ke memori).
- Inisialisasi: bobot global sama ke semua klien tiap awal (standar FedAvg).

**Metrik yang dicatat tiap konfigurasi:** MCC (utama), recall/precision/F1,
balanced-accuracy, + **communication cost** (rounds-to-converge, total bytes
dikirim). 5 seed {13,42,101,202,303}, rerata±std+CI95, uji signifikansi (pola Paper 2).

**Catatan kejujuran:** semua angka di atas adalah SETELAN AWAL; nilai final diisi dari
hasil kalibrasi nyata di Fase 1 (jangan dikunci sebelum diuji).

### Dataset per-klien (ISI dari statistik nyata saat partisi dibuat)

| Klien | Sumber | Total | Attack | Benign | Skema partisi |
|---|---|---:|---:|---:|---|
| [TBD] | | -- | -- | -- | |

## C. Rumus-rumus kunci (ISI final saat metode beku)

**FedAvg:** `w_(t+1) = sum_k (n_k/n) * w_k^(t)`
**FedProx:** FedAvg + proximal term `(mu/2)||w - w_global||^2` di loss lokal.
**MCC:** `(TP*TN - FP*FN)/sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))` (metrik utama, konsisten Paper 1–3).
**SFM:** warisi definisi Paper 1 (peta fitur tervalidasi; z-score fit train-only).

## D–J. Hasil (BELUM ADA — placeholder, isi dari artefak nyata)

- **D. Hasil 1 — Centralized vs Local-only vs Federated-SFM (MCC, 5 seed).** [TBD]
- **E. Hasil 2 — Ablasi: FL dengan vs tanpa SFM (bukti SFM = enabler).** [TBD]
- **F. Hasil 3 — Pengaruh non-IID / jumlah klien (Skenario-B).** [TBD]
- **G. Hasil 4 — FedAvg vs FedProx + biaya komunikasi (rounds/bytes vs MCC).** [TBD]
- **H. (opsional) Hasil 5 — validasi AWS / jembatan XGBoost↔MLP.** [TBD]
- **I. Grafik** (`figure-fed/`, teks figur Inggris). [TBD]
- **J. Kesimpulan (pesan utama, hasil campuran jujur).** [TBD]

---

# BAGIAN II — MEMORI OPERASIONAL

## K. Prinsip reproduksi

Notebook Paper 4 di `federated/notebooks/`. Output → `federated/fed_out/` + S3
`s3://ssh-detection-features-232032302717/unsw-far/federated/`. Dataset sumber dipakai
bersama dari root repo (gitignored): `CICDDoS2018/`, `unswnb-15/data/`. SFM mapping
diwarisi dari `unswnb-15/notebooks/01,02,05`. JANGAN mengarang angka.

## L. Peta NOTEBOOK ↔ TABEL (rencana — isi saat dibuat)

| Notebook | Peran | Menghasilkan | Tabel |
|---|---|---|---|
| `01_fed_data_partition.ipynb` | Partisi klien (A: per-dataset; B: non-IID shard) + statistik | dataset_stats_fed.csv | tabel dataset |
| `02_fed_backbone_bridge.ipynb` | MLP centralized vs XGBoost centralized (jembatan ke Paper 1) | bridge_centralized.csv | tabel D (baseline) |
| `03_fedavg_sfm.ipynb` | FedAvg di ruang SFM (skenario A) + baseline centralized/local | fedavg_sfm.csv | tabel D |
| `04_ablation_sfm.ipynb` | FL dengan vs tanpa SFM | ablation_sfm.csv | tabel E |
| `05_noniid_scaling.ipynb` | K klien non-IID (skenario B) | noniid_scaling.csv | tabel F |
| `06_fedprox_comm.ipynb` | FedAvg vs FedProx + biaya komunikasi | fedprox_comm.csv | tabel G |
| `07_multiseed_ci.ipynb` | Agregasi 5 seed + CI + signifikansi | fed_agg.csv, significance_fed.csv | semua tabel |

## M. Status

| # | Item | Status |
|---|---|---|
| 1 | Scope & novelty (SFM-enabler, satu sumbu) | ✅ ditetapkan (Bagian A) |
| 2 | Dataset = CIC2018 ↔ UNSW (pakai SFM Paper 1) | ✅ diputuskan |
| 3 | Arsitektur = MLP pada 9 fitur SFM + jembatan XGBoost | ✅ diputuskan (Bagian B) |
| 4 | Rapikan daftar referensi FL → federated_refs_clean.md (41 unik) | ✅ |
| 5 | Implementasi partisi + baseline (Fase 1) | ◐ notebook DISUSUN (nb01,nb02); eksekusi SageMaker menunggu |
| 6 | Eksperimen federated inti (Fase 2) | ◐ infra+skrip+runbook + nb03(FedAvg)+nb04(ablasi SFM) DISUSUN; eksekusi menunggu |
| 7 | Validasi 5-seed + naskah ID → EN (Fase 3) | ◐ nb05–nb07 DISUSUN; eksekusi + naskah menunggu |

## N. ROADMAP BERTAHAP (langkah kerja)

**Fase 0 — Scope & persiapan (tanpa SageMaker) — SEBAGIAN SELESAI**
- [x] Finalisasi pertanyaan riset + novelty + posisi vs Paper 1–3 (Bagian A).
- [x] Keputusan arsitektur: MLP pada 9 fitur SFM + jembatan XGBoost (Bagian B).
- [x] Keputusan dataset: CIC2018 ↔ UNSW (SFM Paper 1).
- [x] Rapikan daftar referensi FL → `references/federated_refs_clean.md` (41 entri unik).
- [x] Hyperparameter MLP + konfigurasi FL awal ditetapkan (Bagian B, draf; kalibrasi di Fase 1).

**Fase 1 — Baseline & partisi (SageMaker ringan)**
- [~] nb01: `01_fed_data_partition.ipynb` DISUSUN (siap jalan di SageMaker) — partisi per-klien via SFM public-prior + statistik.
- [~] nb02: `02_fed_backbone_bridge.ipynb` DISUSUN (siap jalan) — MLP vs XGBoost centralized pada 9 fitur SFM (jembatan Paper 1).
- [ ] Baseline local-only per-klien.

**Fase 2 — Federated inti**
- [~] Infra DISUSUN: `aws/fed-vpc-3ec2-public.yaml` (3 EC2 publik, no-NAT, SG ketat, SSM) +
      `aws/fed_node.py` (aggregator+client, MLP numpy, bobot via S3) + `aws/fed-runbook.md`.
      Eksekusi SageMaker/AWS menunggu (Fase 1 harus jalan dulu utk isi data S3).
- [~] nb03: `03_fedavg_sfm.ipynb` DISUSUN (siap jalan) — FedAvg ruang SFM skenario-A + centralized/local sebagai batas; reuse logika `aws/fed_node.py` (simulasi ≡ EC2). Eksekusi menunggu nb01.
- [~] nb04: `04_ablation_sfm.ipynb` DISUSUN (siap jalan) — ablasi FL dengan vs tanpa SFM (naif by-position & name-intersection) → **bukti utama H1**. Eksekusi menunggu nb01 + data mentah.
- [~] nb05: `05_noniid_scaling.ipynb` DISUSUN — skenario-B K klien non-IID (Dirichlet alpha) → H3; reuse `aws/fed_node.py`. Eksekusi menunggu nb01.
- [~] nb06: `06_fedprox_comm.ipynb` DISUSUN — FedAvg vs FedProx (mu) + biaya komunikasi (bytes/round, rounds-to-converge) → H2/efisiensi; FedProx via `fed_node.py` (mu>0). Eksekusi menunggu nb01.

**Fase 3 — Validasi & naskah**
- [~] nb07: `07_multiseed_ci.ipynb` DISUSUN — 5-seed {13,42,101,202,303} + rerata/std/CI95 + uji signifikansi (t-test & Wilcoxon) federated-SFM vs local-only (pola Paper 2). Eksekusi menunggu nb01.
- [ ] (opsional) validasi AWS: deploy model global federated, ukur di trafik nyata.
- [ ] Tulis `paper-federated.tex` (ID) → `paper-federated-english.tex` (EN, elsarticle).
- [ ] Gambar `figure-fed/` teks Inggris; highlights terpisah.
- [ ] Submit SETELAH Paper 1 accepted.

## O. Cara ambil hasil dari S3 (pola Paper 2)

Redirect output ke file lalu baca:
`aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/federated/<file> fed_out/ --region ap-southeast-1 > _dl.txt 2>&1`
Kredensial user `hero` (akun 232032302717), region `ap-southeast-1`.

## P. Konvensi kerja (warisi Paper 1–3)

- Tiap revisi `.tex`: verifikasi `\begin`/`\end` seimbang + cite↔bibitem cocok →
  commit granular → push `origin/main`.
- JANGAN mengarang angka. Placeholder `--`/`[TBD]` sampai hasil nyata.
- Notebook: docstring pakai `#` (bukan triple-quote); validasi json.load + ast.parse.
- Angka `.tex`: koma; laporan markdown: titik. Teks DI DALAM figur: Inggris.
- Dua naskah: `.tex` ID (kerja) + `-english.tex` (submit JISA, elsarticle authoryear).
- Angka SOTA dari paper lain (mis. "98.5%") HANYA sebagai related-work; hasil kita
  wajib dari eksperimen nyata.


---

---

## R. Rancangan Infrastruktur Multi-EC2 (Opsi B — IP publik, tanpa NAT)

> **Keputusan final:** federasi = **multi-EC2 penuh**, ketiga node pakai **IP publik**
> di **public subnet** (via Internet Gateway), **TANPA NAT Gateway**. Alasan: NAT GW
> adalah komponen termahal & jebakan biaya (~$1,4/hari + $/GB) untuk eksperimen pendek;
> IP publik + Security Group ketat memberi biaya lebih rendah, setup lebih sederhana,
> dan **teardown bersih total** (hapus 1 stack → semua hilang, biaya nol).
> Data mentah tiap klien tetap HANYA di node-nya (inti privasi FL); yang dipertukarkan
> hanya **bobot model** lewat S3. Region ap-southeast-1. Pola operasional warisi Paper 2
> (AL2023, boto3, SSM, hasil ke S3).

### R.1 Jumlah server & peran

**Skenario-A (inti, 3 EC2):**

| Peran | Jumlah | Jaringan | Isi | Fungsi |
|---|---|---|---|---|
| **Aggregator** (FL server) | 1 | public subnet, IP publik | model global MLP + skrip agregasi | broadcast bobot global → agregasi FedAvg/FedProx → ulang tiap round |
| **Client-CIC** | 1 | public subnet, IP publik | HANYA partisi CSE-CIC-IDS2018 (9 fitur SFM) | latih lokal E epoch → kirim bobot |
| **Client-UNSW** | 1 | public subnet, IP publik | HANYA partisi UNSW-NB15 (9 fitur SFM) | latih lokal E epoch → kirim bobot |

**Skenario-B (perluasan):** 1 aggregator + K client (K=4–10), tiap client shard non-IID.
Semua tetap IP publik + SG ketat. Jumlah EC2 = 1 + K.

### R.2 Diagram jaringan (ASCII — tampil di Markdown Preview)

```
                    AWS VPC (ap-southeast-1)   10.0.0.0/16
  +---------------------------------------------------------------------+
  |                                                                     |
  |   Internet Gateway (IGW)  <--- egress langsung ke S3 & paket, NO NAT|
  |            |                                                        |
  |   Public subnet 10.0.1.0/24   (map public IP = yes)                 |
  |                                                                     |
  |     +------------------------------+                                |
  |     |   AGGREGATOR (FL server)     |  EC2 t3.medium AL2023          |
  |     |   IP publik + SG ketat       |  - model global MLP            |
  |     |   - FedAvg / FedProx         |  - checkpoint -> S3            |
  |     +---------------+--------------+                                |
  |      bobot global  |  ^  update bobot (round t)                     |
  |       (round t)    v  |      (dipertukarkan via S3, bukan socket)   |
  |     +--------------+--+----------------+                            |
  |     |                                  |                            |
  | +---v----------------+       +---------v------------+               |
  | |  CLIENT-CIC        |       |  CLIENT-UNSW         |               |
  | |  IP publik+SG ketat|       |  IP publik+SG ketat  |               |
  | |  EC2 t3.medium     |       |  EC2 t3.medium       |               |
  | |  data CIC (SFM)    |       |  data UNSW (SFM)     |               |
  | |  LOKAL, tak keluar |       |  LOKAL, tak keluar   |               |
  | +--------------------+       +----------------------+               |
  |                                                                     |
  +----------------------------------+----------------------------------+
         semua egress ke S3 lewat IGW |  (gratis, region sama; tanpa NAT)
                                      v
                 S3  s3://ssh-detection-features-232032302717/
                     unsw-far/federated/   (bobot per-round, metrik, log)

  Security Group (ketat):
   - INBOUND: TIDAK ada dari 0.0.0.0/0 (tak buka SSH/port apa pun ke internet).
              Akses operator via SSM Session Manager (bukan SSH key).
   - OUTBOUND: HTTPS(443) ke S3/paket; intra-VPC seperlunya.
   - Node TIDAK saling akses socket langsung (pertukaran bobot via S3).
```

**Alur per round t:** (1) aggregator tulis `global_t.npz` ke S3; (2) tiap client baca,
latih lokal E epoch pada partisi SENDIRI, tulis `round_t/client_k.npz` ke S3; (3)
aggregator baca semua `client_k.npz`, FedAvg/FedProx → `global_(t+1).npz`; (4) ulang
sampai R round / konvergen. **Pertukaran lewat S3 → node tak perlu saling buka port.**

### R.3 Data di masing-masing server (apa yang HARUS ada)

| Server | Data wajib ada | Dari mana (via boto3) | TIDAK boleh ada |
|---|---|---|---|
| Aggregator | skrip server FL, model global awal, config (R,E,C,mu) | S3 `unsw-far/federated/scripts/` | data mentah klien apa pun |
| Client-CIC | partisi CIC 9 fitur SFM (z-score-ready) + label | S3 `unsw-far/federated/data/cic/` | partisi UNSW |
| Client-UNSW | partisi UNSW 9 fitur SFM + label | S3 `unsw-far/federated/data/unsw/` | partisi CIC |

> **Privasi (klaim paper):** data latih tiap klien dipisah fisik per-node; yang keluar
> node hanya bobot. **Test set global** (held-out lintas-domain) dipakai HANYA di
> evaluasi offline (bukan dibagikan ke klien) → hindari kebocoran.

### R.4 Komunikasi & keamanan (IP publik, aman untuk eksperimen pendek)

- **Transport bobot: via S3** (bukan socket antar-EC2) — tiap node cukup egress HTTPS
  ke S3. Ini kenapa IP publik tanpa NAT aman & sederhana: tak ada port antar-node yang
  perlu dibuka.
- **Security Group KETAT:** inbound 0.0.0.0/0 = DITUTUP semua (tak ada SSH terbuka).
  Operator masuk via **SSM Session Manager**. Outbound: 443 ke S3 + intra-VPC seperlunya.
- **AL2023 + boto3** untuk unduh data/skrip & upload hasil (JANGAN `aws s3 cp` di
  instance — rusak setelah pip; pelajaran Paper 2).
- IAM role per-EC2: akses S3 prefix `unsw-far/federated/` + SSM core.

### R.5 Training vs Testing

- **Training (terdistribusi, 3 EC2 IP publik):** klien latih lokal → aggregator
  FedAvg/FedProx; checkpoint tiap round → S3.
- **Testing/evaluasi (offline, 1 tempat):** tarik model global final dari S3 → evaluasi
  di notebook (SageMaker/lokal) pada held-out test global; hitung MCC/recall/precision/
  balanced-acc; bandingkan vs centralized & local-only. **Testing tak perlu multi-EC2.**

### R.6 Biaya & teardown

- **Komponen berbiaya:** 3× t3.medium (~$0,05/jam/node → ~$0,15/jam total) + EBS kecil.
  **TANPA NAT GW** → hemat ~$1,4/hari + biaya data NAT. S3 egress region-sama ~gratis.
- Eksperimen training federated pendek (beberapa jam) → estimasi **beberapa dolar saja**.
  Isi angka nyata saat eksekusi (`aws/cost-estimate.md`).
- **Teardown total:** `delete-stack` 1 CloudFormation stack (VPC+IGW+subnet+SG+3 EC2) →
  semua terhapus, **biaya nol**. Tanpa NAT GW tak ada komponen biaya yang mudah nyangkut.

> **Status R:** topologi DITETAPKAN = **3 EC2 IP publik, tanpa NAT, SG ketat + SSM,
> bobot via S3.** CloudFormation `aws/fed-vpc-3ec2-public.yaml` + skrip server/client +
> runbook disusun di Fase 2 (Bagian N), mengikuti pola `unswnb-15/aws/`.

