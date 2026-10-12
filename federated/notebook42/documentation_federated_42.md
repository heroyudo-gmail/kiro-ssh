# Dokumentasi Percobaan — Paper 4-2 (Robust Aggregation untuk Federated NIDS)

> **Judul kerja:** *Agregasi Tangguh (Robust Aggregation) untuk NIDS Terfederasi
> Lintas-Dataset Melawan Serangan Poisoning dan Backdoor* — di atas ruang SFM
> (fondasi Paper 1) dan infrastruktur federated Paper 4.
>
> **Fungsi file ini:** memori persisten + laporan hasil Paper 4-2. Kalau konteks
> hilang/reset, BACA FILE INI DULU.
>
> **STATUS: PERENCANAAN (Fase 0).** Belum ada eksperimen; semua angka hasil `[TBD]`.
> **JANGAN mengarang angka** — placeholder `[TBD]`/`--` sampai hasil nyata.
>
> **Hubungan dgn Paper 4:** Paper 4 (interoperabilitas skema-fitur via SFM) menyebut
> ketahanan poisoning sebagai *future work*. Paper 4-2 MENGISI itu: sumbu baru =
> **keamanan/ketahanan** (bukan interoperabilitas). Tetap memakai konsep federated +
> ruang SFM + `aws/fed_node.py` sebagai basis. Ini silsilah lanjutan, BUKAN
> salami-slicing: pertanyaan, ancaman, metode, dan metrik berbeda.
>
> **PETA:** paper = `notebook42/paper-4-2.tex` (ID dulu, lalu EN). Notebook di
> `notebook42/`. Hasil ke S3 `unsw-far/federated42/results/`.

---

# BAGIAN I — RENCANA RISET

## A. Tujuan, pertanyaan riset & novelty

**Masalah.** FedAvg mengasumsikan semua klien jujur. Di NIDS terdistribusi
multi-organisasi, sebagian klien dapat **jahat** (dikompromikan / sengaja merusak):
mengirim update beracun (*poisoning*) atau menanam *backdoor* (pola pemicu → label
target). FedAvg (rata-rata berbobot) sangat rentan — satu-dua klien jahat bisa
menggeser model global.

**Pertanyaan riset:**
> Dalam FL-NIDS lintas-dataset pada ruang SFM, (RQ1) seberapa rapuh FedAvg terhadap
> klien jahat seiring naiknya fraksi penyerang; (RQ2) sejauh mana *robust aggregation*
> (Krum, Multi-Krum, Trimmed-Mean, Median) memulihkan MCC dan menekan *Attack Success
> Rate* backdoor; (RQ3) berapa harga ketahanan (penurunan MCC saat TANPA serangan)?

**Novelty (satu sumbu, tajam):**
> *Robust aggregation* dievaluasi secara spesifik pada **NIDS lintas-dataset di ruang
> SFM** — bukan data generik. Mengukur interaksi antara heterogenitas lintas-dataset
> (temuan Paper 4) DAN kehadiran penyerang. Literatur robust-agg umumnya diuji pada
> data IID/benchmark umum; penerapan + evaluasi pada FL-NIDS lintas-tool masih tipis.

## B. Desain eksperimen (DRAF — kalibrasi saat Fase 1)

**Basis.** MLP numpy dari `aws/fed_node.py` (9→128→64→1), z-score per-klien lokal,
ruang 9 fitur SFM (partisi dari Paper 4 nb01). Dataset: CSE-CIC-IDS2018 + UNSW-NB15.

**Setting klien.** Multi-klien (skenario-B, Dirichlet) — **K=10 (inti), opsi perluasan K=20** —
agar *fraksi penyerang* bermakna (f=10/20/30% → 1/2/3 penyerang pada K=10). KEPUTUSAN FINAL.

**Model ancaman (attacker):**
1. **Label-flipping poisoning** — klien jahat membalik label train lokalnya.
2. **Weight/gradient scaling** — klien jahat mengirim update diperbesar (boosting).
3. **Backdoor** — klien jahat menyisipkan pola pemicu (trigger) pada fitur → memaksa
   label target (mis. attack→benign). Diukur dgn *Attack Success Rate* (ASR).

**Fraksi penyerang:** f ∈ {0%, 10%, 20%, 30%} dari K.

**Aturan agregasi (dibandingkan):**
- **FedAvg** (baseline rentan).
- **Krum / Multi-Krum** (pilih update terdekat ke mayoritas; buang outlier).
- **Trimmed-Mean** (buang ekstrem per-koordinat).
- **Coordinate-wise Median**.
- (opsional) **FLTrust-like** (server punya root-set kecil tepercaya untuk skor trust).

**Metrik:**
- **MCC** GLOBAL-test (deteksi utama) + recall/precision/F1/bal-acc.
- **ASR** (backdoor) — proporsi sampel ber-trigger yang salah-klasifikasi ke target.
- **Recovery gap** — selisih MCC robust-agg vs no-attack (seberapa pulih).
- **Clean cost** — penurunan MCC robust-agg saat f=0 (harga ketahanan).
- Multi-seed {13,42,101,202,303} + rerata±sb + CI95 (pola Paper 2/4).

**Hipotesis (diuji JUJUR, apa pun hasilnya):**
- H1: MCC FedAvg turun tajam saat f naik (bukti kerentanan).
- H2: Robust-agg menahan penurunan MCC & menekan ASR backdoor.
- H3: Trade-off — robust-agg menurunkan MCC sedikit saat f=0 (clean cost).

## C. Rumus kunci (ISI final saat metode beku)

- **FedAvg:** w_(t+1) = sum_k (n_k/n) w_k.
- **Krum:** pilih update w_i yg meminimalkan sum jarak kuadrat ke (K-f-2) tetangga terdekat.
- **Trimmed-Mean(beta):** per-koordinat, buang beta terkecil & beta terbesar, rata-ratakan sisanya.
- **Median:** per-koordinat ambil median update klien.
- **ASR:** (# sampel ber-trigger diprediksi = label target) / (# sampel ber-trigger).
- **MCC:** (TP*TN - FP*FN)/sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)).

## D–H. Hasil (BELUM ADA — placeholder)
- **D. Kerentanan FedAvg vs fraksi penyerang (RQ1).** [TBD]
- **E. Robust-agg: pemulihan MCC vs serangan (RQ2).** [TBD]
- **F. Backdoor: ASR FedAvg vs robust-agg (RQ2).** [TBD]
- **G. Clean cost / trade-off robust-agg (RQ3).** [TBD]
- **H. Multi-seed + CI + grafik.** [TBD]

---

# BAGIAN II — MEMORI OPERASIONAL

## I. Peta NOTEBOOK (DISUSUN; eksekusi menunggu SageMaker)

> Catatan: aturan agregasi + model serangan dijadikan **modul `robust_agg.py`**
> (sumber tunggal, di-reuse semua notebook) — menggantikan rencana nb `42_03`.
> Divalidasi *smoke test*: Krum/Multi-Krum menolak klien jahat; ASR benar.

| Notebook / modul | Peran | Output | Status |
|---|---|---|---|
| `robust_agg.py` | Modul: 5 aturan agregasi (FedAvg/Krum/Multi-Krum/Trimmed-Mean/Median) + 3 serangan (label-flip/scale/backdoor) + ASR | — | ✅ smoke-test |
| `01_setup_partition.ipynb` | Partisi K=10 Dirichlet di ruang SFM + global-test; reuse partisi SFM Paper 4 | parts_K10.npz, global_test.npz, parts_stats.csv | ◐ disusun |
| `02_attacks.ipynb` | Demo/verifikasi 3 serangan efektif (FedAvg f=20%) | attack_demo.csv | ◐ disusun |
| `03_vuln_curve.ipynb` | Kurva MCC vs fraksi penyerang (5 aturan, label-flip) + grafik | vuln_curve.csv, figure-fed42/mcc_vs_fraction.png | ◐ disusun |
| `04_vuln_fedavg.ipynb` | RQ1: kerentanan FedAvg vs fraksi penyerang (0/10/20/30%) | vuln_fedavg.csv | ◐ disusun |
| `05_defense.ipynb` | RQ2: 5 aturan vs serangan (f=20%) + RQ3 harga ketahanan (f=0) | defense.csv, clean_cost.csv | ◐ disusun |
| `06_backdoor_asr.ipynb` | RQ2: ASR backdoor FedAvg vs robust-agg (f=10/20/30%) | backdoor_asr.csv | ◐ disusun |
| `07_multiseed_ci.ipynb` | 5-seed + CI95 + grafik (backdoor f=20%) + unggah S3 | agg42.csv, figure-fed42/*.png | ◐ disusun |

## J. Status

| # | Item | Status |
|---|---|---|
| 1 | Scope & novelty (robust-agg di SFM lintas-dataset) | ◐ draf (Bagian A) |
| 2 | Desain ancaman + aturan agregasi + metrik | ◐ draf (Bagian B) |
| 3 | Keputusan jumlah klien K=10 (opsi 20) | ✅ final |
| 4 | Implementasi notebook (robust_agg.py + 01/02/04/05/06/07) | ◐ DISUSUN (42_03 -> modul) |
| 5 | Eksekusi SageMaker + isi angka nyata | ⏳ |
| 6 | Naskah paper-4-2.tex (ID): hipotesis ilustratif + pembeda tajam Paper 2 + figur kurva | ◐ ID draf; EN menunggu hasil |

## K. Konvensi kerja (warisi Paper 1–4)

- JANGAN mengarang angka. Placeholder `--`/`[TBD]` sampai hasil nyata.
- Notebook: docstring pakai `#` (bukan triple-quote); validasi json.load + ast.parse.
- Reuse `../aws/fed_node.py` (jangan tulis-ulang logika FL inti).
- Angka `.tex`: koma; markdown: titik. Teks DI DALAM figur: Inggris.
- Dua naskah: `paper-4-2.tex` (ID, kerja) → `paper-4-2-english.tex` (submit).
- Tiap revisi `.tex`: verifikasi \begin/\end seimbang + cite↔bibitem cocok → commit.
- Hasil ke S3 `unsw-far/federated42/results/` (boto3, bukan aws s3 cp di instance).
