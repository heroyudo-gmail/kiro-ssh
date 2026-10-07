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
> **STATUS: RUN-2 + KONTROL HOMOGEN (nb08) SELESAI.** Kontrol HOMOGEN (nb08):
> FedAvg BEKERJA normal (CIC 0,563 / UNSW 0,674, mendekati centralized, konvergen
> mulus) -> pipeline FL VALID. HETEROGEN lintas-dataset (nb03): federated KOLAPS
> (−0,026). Kontras ini = bukti kuat "SFM perlu tapi tak cukup; FedAvg naif divergen
> HANYA di heterogenitas lintas-dataset". KEPUTUSAN: framing temuan-negatif terkontrol
> (Opsi B diperkuat). JEMBATAN non-IID (nb09): titik putus FedAvg di α≈0,1 pada UNSW
> (rapuh krn prior label seimbang 0,55), CIC tahan sampai α=0,01 (condong-benign 0,17)
> -> asimetri ini menjelaskan penyebab kolaps lintas-dataset. ONE-CLASS (nb10): mitigasi
> GAGAL (federated-AE 0,039) -> ruang fitur kurang separable. PERSONALIZED (nb12): mitigasi
> BERHASIL -> FedPer 0,731, clustered 0,745 (~centralized) -> failure boundary dapat
> DIMITIGASI dengan personalisasi. NASKAH: paper-jictra.tex (target Q4, 'semantic feature
> alignment', self-contained). Lihat Bagian D–J (TEMA 1-4) + RINGKASAN ALUR 5 langkah.
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

## D–J. Hasil (urutan tematik: HOMOGEN dulu, baru HETEROGEN)

> **Urutan baca (disepakati):** tampilkan dulu **kontrol HOMOGEN** (FL bekerja
> normal) sebagai baseline positif, baru **HETEROGEN lintas-dataset** (FL kolaps)
> sebagai temuan negatif. Kontras keduanya = bukti utama "SFM perlu tapi tak cukup".

---

### TEMA 1 — KONTROL HOMOGEN (IID, per-dataset) — nb08, HASIL NYATA

> **Peringatan kejujuran:** angka NYATA dari `homogen_iid.csv` + `homogen_iid_curve.csv`
> (S3 `unsw-far/federated/results/homogen/`, diunduh 2026-10-07). Eksperimen ini
> **kontrol yang hilang** dari run-1/run-2: menguji FedAvg pada setting HOMOGEN
> (satu dataset dipecah IID ke K=4 klien), mereplikasi kondisi SOTA (mis. Fed-ANIDS).
> Model/hyperparameter IDENTIK nb03 (MLP 128,64; FedAvg; ROUNDS=100, LOCAL_EPOCHS=5,
> LR=3e-3) -> satu-satunya variabel yang berubah: homogen vs heterogen.

**H-kontrol. Centralized / Federated-IID / Local-only (MCC, dievaluasi di test
dataset yang SAMA).**

| Dataset | Centralized | Federated-IID | Local-only (mean) | Gap (cent−fed) |
|---|---:|---:|---:|---:|
| CIC-only  | 0,619 | **0,563** | 0,558 | 0,056 |
| UNSW-only | 0,723 | **0,674** | 0,671 | 0,049 |

**Kurva konvergensi (dari `homogen_iid_curve.csv`): NAIK MULUS, tak ada divergence.**
- CIC: 0,290 (round 0) -> naik monoton -> **0,563** (round 99); plateau mulus.
- UNSW: 0,408 -> naik stabil -> **0,674** (round 99); tak ada kolaps.

**TEMUAN (kontrol VALID):**
1. Urutan sesuai teori FL sehat: **centralized ≥ federated-IID ≥ local-only**,
   dengan gap kecil (0,05–0,06). Federated mendekati centralized, sedikit di atas
   local-only — persis pola FL yang benar.
2. **Pipeline FL kita VALID** (tak ada bug di FedAvg/MLP/ruang SFM): pada homogen,
   FedAvg konvergen mulus di KEDUA dataset.
3. Mereplikasi kondisi SOTA (satu-sumber dipecah) -> metode kita juga sukses di
   kondisi yang sama dgn literatur.

**Catatan metodologi (jujur):** evaluasi federated-IID memakai z-score monitoring
dari gabungan train (mu_g,sd_g). Pada IID antar-shard mirip -> efeknya kecil; untuk
naskah dicatat sebagai detail (deployment nyata pakai z-score lokal per-klien).

---

### TEMA 1b — JEMBATAN non-IID bertingkat (satu dataset, sweep alpha) — nb09, HASIL NYATA

> **Peringatan kejujuran:** angka NYATA dari `noniid_bridge.csv` + `_curve.csv`
> (S3 `unsw-far/federated/results/noniid_bridge/`, diunduh 2026-10-07). Jembatan
> antara TEMA 1 (homogen) dan TEMA 2 (heterogen): SATU dataset dipecah K=4 klien
> via Dirichlet(alpha); alpha turun dari ~IID (100) ke ekstrem (0.01) = SATU-SATUNYA
> sumber heterogenitas (bersih; beda dari nb05 yang mencampur CIC+UNSW). Model/HP
> identik nb03/nb08. Cari **titik putus** FedAvg.

**Hasil (MCC federated vs centralized, per-dataset):**

| dataset | centralized | α=100 | α=10 | α=1 | α=0,5 | α=0,1 | α=0,05 | α=0,01* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CIC (pos 0,17)  | 0,619 | 0,562 | 0,557 | 0,575 | 0,569 | 0,581 | 0,577 | 0,582 |
| UNSW (pos 0,55) | 0,723 | 0,672 | 0,673 | 0,698 | 0,694 | **0,337** | **0,310** | **0,245** |

(*α=0,01: K jatuh ke 2 klien karena shard kosong di-drop -> tidak apple-to-apple,
dilaporkan apa adanya; untuk naskah batasi sweep ≤ α=0,05 agar K konsisten.)

**TEMUAN KUNCI (asimetri CIC vs UNSW):**
1. **CIC sangat TAHAN non-IID** -- bertahan ~0,56–0,58 sampai α=0,01 (ekstrem),
   tak ada titik putus pada rentang ini.
2. **UNSW RAPUH** -- **titik putus tajam di α≈0,1** (label_skew ~0,49): MCC jatuh
   0,69 -> 0,34 (separuh), lalu makin dalam (0,25 di α=0,01).
3. **Penjelasan:** prior label. UNSW seimbang (0,55) -> saat α kecil memaksa klien
   condong satu kelas, klien jadi hampir single-class -> model lokal menyimpang jauh
   -> FedAvg divergen. CIC condong-benign (0,17) -> mayoritas tetap benign di semua
   klien meski skew tinggi -> model lokal tak menyimpang -> FedAvg bertahan.
4. **Menjelaskan nb03:** di lintas-dataset, sisi UNSW (seimbang) + perbedaan
   distribusi dgn CIC menempatkan kondisi DI LUAR titik putus -> divergence nb03
   kemungkinan besar DIDORONG sisi UNSW + heterogenitas antar-sumber.

**Nilai untuk naskah:** kurva MCC-vs-α + titik putus mengkuantifikasi 'seberapa jauh
FedAvg naif menahan heterogenitas sebelum runtuh'. Lintas-dataset berada di luar
batas tsb -> motivasi kuat untuk mitigasi (FedProx μ besar, FedBN/personalized,
atau pendekatan one-class ala Fed-ANIDS yang menghapus ketergantungan prior-label).

---

### TEMA 2 — HETEROGEN LINTAS-DATASET (CIC↔UNSW) — nb03, run-1 & run-2

> Inilah kasus inti Paper 4 (klien = dataset berbeda-sumber, skema & distribusi
> label berbeda). Di sinilah FedAvg/FedProx naif **gagal** — kontras tajam dengan
> TEMA 1. Dua run didokumentasikan apa adanya di bawah.

### RUN-1 (SageMaker, SEED 13/42/101/202/303) — HASIL NYATA & DIAGNOSA

> **Peringatan kejujuran:** angka di bawah adalah hasil eksperimen NYATA run pertama
> (CSV di S3 `unsw-far/federated/results/`). Hasil ini **TIDAK mendukung hipotesis
> utama**. Didokumentasikan apa adanya; perbaikan metode sedang dikerjakan (lihat akhir bagian).

**D. Hasil 1 — Centralized / Local-only / Federated-SFM (MCC).** Dari `fedavg_sfm.csv`
+ `fed_agg.csv` (5 seed). GLOBAL-test:
- Centralized (upper bound): MCC **0,646**.
- Local-only (rerata 5 seed, model terbaik antar-klien): MCC **0,237** (sb 0,024).
- Federated-SFM (rerata 5 seed): MCC **0,175** (sb 0,048).
- **H2 TERBALIK:** federated < local-only, selisih −0,062, **signifikan** (t-test p=0,015;
  Wilcoxon p=0,0625). Lihat `significance_fed.csv`.
- Per-domain federated: CIC-test 0,566 (baik) vs **UNSW-test 0,018** (nyaris gagal).

**E. Hasil 2 — Ablasi SFM (H1).** Dari `ablation_sfm.csv`, GLOBAL-test MCC:
- Federated-SFM (9 selaras): **0,217**; Naif-1 (by-position): **0,201** — selisih hanya
  0,016 (praktis setara). **H1 kuantitatif LEMAH.** Naif-2 (irisan nama) = kosong →
  argumen kualitatif (federasi mentah tak terbentuk) MASIH berlaku, tapi klaim utama lemah.

**F. Hasil 3 — non-IID / jumlah klien (H3).** Dari `noniid_scaling.csv`. Pada
alpha=1,0 tren wajar (K naik → MCC turun: 0,620 → 0,510). Pada alpha=0,1 ada anomali
K=6 (MCC 0,267) akibat satu klien skew ekstrem. H3 **sebagian terdukung**.

**G. Hasil 4 — FedAvg vs FedProx + biaya.** Dari `fedprox_comm.csv`. FedProx
(mu 0,001–0,1) ~ identik FedAvg (MCC_final 0,267), rounds-to-converge 12–13,
2.753 param, 132 KB/round. FedProx **tak membantu** pada setting ini.

**Jembatan backbone (nb02).** Dari `bridge_centralized.csv`, GLOBAL-test: XGBoost
**0,896** vs MLP **0,766** — gap BESAR (MLP under-trained; ConvergenceWarning nb02 nyata).

**DIAGNOSA AKAR MASALAH (run-1):**
1. **Ketimpangan ukuran ekstrem** — CIC train 1.136.282 vs UNSW 82.332 (rasio 14:1).
   FedAvg (bobot n_k/n) → model global didominasi CIC → UNSW-test kolaps (0,018). *Penyebab utama H2 terbalik.*
2. **Ketimpangan label** — CIC pos-rate 0,17 vs UNSW 0,55–0,68.
3. **MLP under-trained** — lr/epoch kurang; MLP << XGBoost.
4. **Baseline local-only "best"** murah hati (ambil MCC terbaik antar-klien).

**RENCANA PERBAIKAN RUN-2 (sedang dikerjakan):**
- nb01: **subsample CIC train stratified ~100k** (jaga pos-rate 0,17) → rasio ~1,2:1, FedAvg adil.
- nb02 & fed_node: naikkan kapasitas/iterasi MLP (max_iter/early_stopping; lr/epoch) agar konvergen.
- Re-run nb01→nb07; isi angka run-2 di sini (JANGAN hapus temuan run-1 — simpan sebagai jejak jujur).

**I. Grafik** (`figure-fed/`, teks figur Inggris). [TBD — dibuat dari CSV run final].

**J. Kesimpulan sementara (jujur).** Pada run-1, FedAvg naif di ruang SFM dengan dua
klien sangat timpang (ukuran 14:1 + distribusi label beda jauh) menghasilkan model
global yang **kalah dari local-only** dan ablasi SFM yang **tak tegas**. SFM tampak
**perlu tetapi belum cukup** tanpa penanganan ketidakseimbangan klien. Keputusan arah:
perbaiki keseimbangan klien + kapasitas model, lalu re-run sebelum menilai ulang hipotesis.

---

### RUN-2 (SageMaker, SEED 13/42/101/202/303) — HASIL NYATA & DIAGNOSA

> **Peringatan kejujuran:** angka di bawah adalah hasil eksperimen NYATA run KEDUA
> (CSV di S3 `unsw-far/federated/results/run_2/`, diunduh 2026-10-07). Perbaikan yang
> diterapkan: (i) subsample CIC train stratified → **100.000** (pos-rate 0,169 terjaga;
> rasio ke UNSW turun dari 14:1 jadi ~1,2:1); (ii) MLP diperbesar (hidden (128,64),
> max_iter 500, early_stopping); (iii) hyperparameter FedAvg dinaikkan (ROUNDS 100,
> LOCAL_EPOCHS 5, LR 3e-3). **Hasil: H2 TETAP GAGAL, bahkan federated KOLAPS lebih
> parah dari run-1.** Didokumentasikan apa adanya.

**Statistik klien run-2** (dari `dataset_stats_fed.csv`): CIC train 100.000 (pos 0,169),
UNSW train 82.332 (pos 0,551). Ketimpangan ukuran **teratasi** (1,2:1), tetapi
ketimpangan **distribusi label/fitur tetap** (0,17 vs 0,55).

**D2. Centralized / Local-only / Federated-SFM (MCC GLOBAL-test).** Dari `fedavg_sfm.csv`:
- Centralized (upper bound): MCC **0,745** (naik dari 0,646 run-1 — perbaikan MLP berhasil).
- Local-only[unsw]: MCC **0,614**; local-only[cic]: 0,284.
- Federated-SFM: MCC **−0,026** ← **KOLAPS total** (di bawah tebakan acak).
- **H2 GAGAL lebih parah:** urutan jadi centralized (0,745) > local-only (0,614) ≫
  federated (−0,026). Federated bukan sekadar kalah, tapi hancur.

**D2-kurva. Divergence FedAvg** (dari `fedavg_sfm_curve.csv`): MCC global naik ke
puncak **0,275 di round ~10**, lalu **turun terus** dan menembus negatif di round ~25,
mentok di −0,04…−0,05 sampai round 99. Pola **client-drift / oscillation** klasik
FedAvg di non-IID. Menaikkan LR (1e-3→3e-3) + LOCAL_EPOCHS (1→5) **mempercepat
kehancuran**: tiap klien menyimpang jauh dari global, rata-rata bobot saling meniadakan.

**E2. Ablasi SFM (H1).** Dari `ablation_sfm.csv`, GLOBAL-test MCC:
- Federated-SFM (9 selaras): **−0,026** (model divergen).
- Naif-1 (by-position): **0,534** — varian "naif" MALAH MENANG (bukan karena naif lebih
  baik, tapi karena model SFM-nya sendiri divergen dengan hyperparam baru).
- Naif-2 (irisan nama): KOSONG → **argumen kualitatif H1 TETAP sah** (federasi mentah
  tanpa SFM mustahil terbentuk). Tapi klaim kuantitatif H1 **gagal/terbalik**.

**F2. non-IID / jumlah klien (H3).** Dari `noniid_scaling.csv`: hasil **tidak konsisten**
— pada alpha=1,0 (lebih IID) MCC 0,16–0,29; pada alpha=100 (hampir IID) malah TURUN ke
0,01–0,03. Ketidakkonsistenan ini menegaskan setup 2-dataset ini fundamental sulit untuk
FedAvg; H3 **tak terbaca jelas**.

**G2. FedAvg vs FedProx + biaya.** Dari `fedprox_comm.csv` — **satu-satunya sinyal
positif**: FedProx proximal term membantu stabilitas secara monoton:
- FedAvg (mu=0): MCC_final **0,075**
- FedProx(mu=0,001): 0,082 · (mu=0,01): 0,130 · **(mu=0,1): 0,187**
- Jadi mu lebih besar → lebih stabil. Tapi angkanya **masih jauh di bawah** local-only
  (0,614). Biaya: 9.601 param, 460 KB/round, rounds-to-converge 82–97.

**H2-seed. Multi-seed CI** (`fed_agg.csv`, `significance_fed.csv`):
- Federated-SFM: **0,229 ± 0,184** (sangat tidak stabil; satu seed −0,026, satu 0,425).
- Local-only: **0,612 ± 0,003** (stabil tinggi).
- mean_diff **−0,382**, paired-t **p=0,0098**, Wilcoxon p=0,0625 → federated
  **signifikan lebih buruk** dari local-only.

**Jembatan backbone run-2 (nb02, `bridge_centralized.csv`), GLOBAL-test:** XGBoost
**0,895** vs MLP **0,771** — gap mengecil sedikit vs run-1 (MLP 0,766), tapi MLP masih
di bawah XGBoost. MLP centralized GLOBAL 0,771 membuktikan arsitektur MLP SENDIRI
mampu; masalahnya murni **agregasi FedAvg**, bukan kapasitas model.

**DIAGNOSA AKAR MASALAH (run-2) — berbeda dari run-1:**
1. **Masalah run-1 (ketimpangan ukuran 14:1) SUDAH diperbaiki** (subsample → 1,2:1),
   dan centralized MLP naik (0,646→0,745). Jadi perbaikan itu benar & berhasil untuk
   centralized.
2. **Tapi masalah sebenarnya BUKAN ukuran — melainkan FedAvg naif rapuh di non-IID
   distribusi.** Dua klien dengan prior label 0,17 vs 0,55 + fitur dari jaringan beda
   membuat FedAvg divergen. Ini masalah **ALGORITMA AGREGASI**, bukan setup data.
3. **Hyperparameter run-2 (LR↑, epochs↑) memperburuk** karena memperbesar client drift.
   Arah tuning kita keliru: untuk non-IID, LR/epochs harus LEBIH KECIL, bukan besar.
4. **FedProx membantu tapi tak cukup** (0,187 ≪ 0,614). Proximal term meredam drift
   sebagian, tak menutup gap.
5. **Fakta kunci:** local-only[unsw] saja = 0,614 GLOBAL-test. Untuk problem 2-dataset
   ini, **federasi tidak memberi nilai tambah** — satu klien yang distribusinya dekat
   global sudah cukup. Ini temuan yang jujur dan penting.

**Kesimpulan run-2 (jujur).** Dua kali run (run-1 H2 terbalik, run-2 federated kolaps)
dengan pola kegagalan konsisten menunjukkan: **memaksakan klaim "FL menang" dari setup
CIC↔UNSW ini tidak didukung data.** SFM terbukti **perlu** (irisan nama kosong → federasi
mentah mustahil; H1 kualitatif sah) tetapi **tidak cukup**: heterogenitas distribusi
label antar-klien membuat FedAvg/FedProx naif divergen. Ini **temuan negatif yang
informatif**, bukan sekadar kegagalan teknis.

**ARAH SETELAH RUN-2 (keputusan framing — Opsi B):**
Alih-alih mengejar "FL menang" (dua run gagal), **reframe kontribusi** jadi pertanyaan
yang jujur dan tetap bernilai ilmiah:
> *Kapan dan mengapa FL cross-dataset NIDS gagal, dan mengapa SFM perlu-tapi-tak-cukup?*
Narasi: (1) SFM menyelesaikan heterogenitas ruang-fitur (H1 kualitatif — enabler
interoperabilitas); (2) namun heterogenitas DISTRIBUSI LABEL antar-dataset membuat
FedAvg/FedProx naif divergen (bukti kuantitatif run-1+run-2); (3) FedProx meredam
sebagian (mu=0,1 terbaik) tapi tak menutup gap; (4) implikasi: FL-NIDS lintas-dataset
butuh agregasi yang sadar-heterogenitas (personalisasi/clustered-FL) — arah future work.
**Opsional run-3** sebagai pelengkap temuan negatif: FedProx(mu=0,1) + LR kecil (1e-3) +
LOCAL_EPOCHS=1 + early-stop di puncak (~round 10), untuk melaporkan "konfigurasi terbaik
yang bisa dicapai pun tetap < local-only".

---

### TEMA 3 — MITIGASI one-class (autoencoder) lintas-dataset — nb10, HASIL NYATA

> **Peringatan kejujuran:** angka NYATA dari `oneclass.csv` + `oneclass_curve.csv`
> (S3 `unsw-far/federated/results/oneclass/`, diunduh 2026-10-07). Upaya MITIGASI
> kasus tersulit (lintas-dataset, TEMA 2) dengan mengganti paradigma: dari supervised
> ke **one-class anomaly detection** ala Fed-ANIDS — tiap klien latih autoencoder
> HANYA pada trafik NORMAL (y=0), deteksi via reconstruction error > persentil-95.
> Hipotesis: menghapus ketergantungan prior-label (akar divergence di TEMA 1b/2)
> membuat FedAvg bobot AE lebih stabil.

**Hasil (MCC):**

| setting | CIC-test | UNSW-test | GLOBAL-test |
|---|---:|---:|---:|
| centralized-AE | −0,070 | −0,042 | −0,003 |
| local-only-AE  | 0,153 | 0,014 | — |
| federated-AE   | 0,150 | 0,002 | **0,039** |

**TEMUAN (hipotesis mitigasi TIDAK terbukti):**
1. federated-AE GLOBAL-test **0,039** — sedikit di atas supervised nb03 (−0,026)
   tetapi **praktis setara nol**; jauh dari local-only supervised (0,614) atau
   homogen (0,56). One-class **tidak menyelamatkan** federasi lintas-dataset.
2. **centralized-AE pun gagal** (MCC ~0 di semua test). Ini sinyal kunci: kalau
   upper-bound terpusat saja gagal, masalahnya **bukan di federasi** melainkan di
   **autoencoder + ruang fitur** untuk tugas ini.
3. **Diagnosa:** 9 fitur SFM dioptimalkan untuk **interoperabilitas lintas-dataset**
   (Paper 1), BUKAN untuk **separabilitas anomali**. Pada 9 fitur flow dasar
   (durasi/paket/byte), trafik serangan tampak mirip normal secara rekonstruksi →
   reconstruction error tak membedakan. Keterbatasan ada di RUANG FITUR, bukan agregasi.

**Implikasi untuk naskah (memperkuat framing):** menambah dimensi baru pada "SFM
perlu tapi tak cukup" — ruang fitur yang bagus untuk ALIGNMENT (interoperabilitas)
tidak otomatis bagus untuk DETECTION federated. Ada trade-off desain fundamental:
alignment-oriented vs separability-oriented feature space. Arah future work: ruang
fitur yang dirancang bersama untuk alignment DAN separabilitas.

**Catatan jujur:** AE yang diuji sederhana (bukan VAE/USAD). Namun karena
centralized-AE pun gagal, memperbesar/mengganti arsitektur AE kecil kemungkinan
menolong selama ruang fiturnya tetap 9-SFM — akar masalah di separabilitas fitur.

---

### TEMA 4 — MITIGASI heterogeneity-aware FL — nb12, HASIL NYATA

> Angka NYATA dari `personalized.csv` (S3 `results/personalized/`). Menjawab:
> apakah strategi FL yang SADAR-HETEROGENITAS bisa menyelamatkan kegagalan FedAvg
> naif (TEMA 2)? Dua strategi diuji di kasus lintas-dataset, backbone sama (MLP 128,64).

**Hasil (GLOBAL-test MCC):**

| strategi | CIC-test | UNSW-test | GLOBAL-test |
|---|---:|---:|---:|
| FedAvg naif (acuan) | 0,532 | 0,616 | −0,026 |
| local-only (acuan) | 0,619 | 0,723 | 0,614 |
| **FedPer** (head personal, backbone di-FedAvg) | 0,608 | 0,700 | **0,731** |
| **Clustered** (model penuh per-klien) | 0,619 | 0,723 | **0,745** |
| centralized (batas atas) | — | — | 0,745 |

**TEMUAN:** mitigasi BERHASIL. FedPer mengangkat GLOBAL dari −0,026 → **0,731**
(dekat centralized); Clustered → **0,745** (setara centralized).

**Catatan jujur:**
1. Keduanya melepas model global tunggal → gain dari PERSONALISASI, bukan agregasi
   yang lebih baik. Clustered = local-only yang dibingkai ulang (kolom per-klien identik).
2. FedPer lebih bermakna: tetap berbagi backbone federated, hanya head yang personal
   → federasi lintas-skema TETAP mungkin, tanpa pooling data, MCC ~centralized.
3. Pesan: pertanyaannya bukan "apakah berfederasi" tapi "APA yang difederasi" —
   berbagi representasi + personalisasi decision boundary mengatasi label-prior mismatch.

---

## RINGKASAN ALUR PEMBUKTIAN (mudah → sulit, untuk naskah)

Urutan naratif Paper 4 (meningkat), terlepas dari urutan waktu pengerjaan:

| # | Tema | Setting | Hasil (GLOBAL/representatif) | Pesan |
|---|---|---|---|---|
| 1 | HOMOGEN (nb08) | 1 dataset, IID, K=4 | CIC 0,563 / UNSW 0,674 (≈ centralized) | FL **VALID** (pipeline benar) |
| 2 | JEMBATAN non-IID (nb09) | 1 dataset, sweep α | UNSW putus α≈0,1; CIC tahan α=0,01 | titik putus **terukur** (prior-label) |
| 3 | HETEROGEN (nb03) | 2 dataset lintas-sumber | federated −0,026 (kolaps) | di luar titik putus → **gagal** |
| 4 | MITIGASI one-class (nb10) | lintas-dataset, AE normal | federated-AE 0,039 (gagal) | ganti paradigma **tak menolong** (fitur) |
| 5 | MITIGASI personalized (nb12) | lintas-dataset, FedPer/clustered | FedPer 0,731; clustered 0,745 | **berhasil** (personalisasi) |

**Narasi tunggal:** FL bekerja saat homogen (1) → bertahan sampai titik putus terukur
(2) → kolaps saat lintas-dataset karena di luar batas itu (3) → one-class pun gagal
karena ruang fitur kurang separable (4) → TAPI strategi sadar-heterogenitas (FedPer)
MEMULIHKAN performa ke ~centralized (5). Kesimpulan: **semantic feature alignment perlu
(enabler interoperabilitas) tetapi tidak cukup; failure boundary dapat DIMITIGASI dengan
personalisasi federasi (berbagi backbone + head personal), bukan agregasi global naif.**

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
| `08_fed_homogen_iid.ipynb` | KONTROL homogen IID per-dataset (CIC-only, UNSW-only) | homogen_iid.csv, homogen_iid_curve.csv | TEMA 1 (homogen) |
| `09_fed_noniid_bridge.ipynb` | JEMBATAN non-IID: sweep Dirichlet alpha per-dataset, titik putus | noniid_bridge.csv, noniid_bridge_curve.csv | TEMA 1b (jembatan) |
| `10_fed_oneclass.ipynb` | MITIGASI one-class (autoencoder, latih hanya normal) lintas-dataset | oneclass.csv, oneclass_curve.csv | TEMA 3 (one-class) |
| `11_feature_separability.ipynb` | Separabilitas 9 fitur (t-SNE/PCA/LDA + metrik) | separability_metrics.csv, sep_*.png | §5.5 naskah |
| `12_personalized_fl.ipynb` | MITIGASI heterogeneity-aware (FedPer + clustered) | personalized.csv, personalized_curve.csv | TEMA 4 (mitigasi) |

## M. Status

| # | Item | Status |
|---|---|---|
| 1 | Scope & novelty (SFM-enabler, satu sumbu) | ✅ ditetapkan (Bagian A) |
| 2 | Dataset = CIC2018 ↔ UNSW (pakai SFM Paper 1) | ✅ diputuskan |
| 3 | Arsitektur = MLP pada 9 fitur SFM + jembatan XGBoost | ✅ diputuskan (Bagian B) |
| 4 | Rapikan daftar referensi FL → federated_refs_clean.md (41 unik) | ✅ |
| 5 | Implementasi partisi + baseline (Fase 1) | ✅ run-2 selesai (nb01,nb02); centralized MLP 0,745 |
| 6 | Eksperimen federated inti (Fase 2) | ✅ run-2 selesai (nb03–nb06); H2 gagal (federated kolaps), FedProx mu=0,1 terbaik 0,187 |
| 7 | Validasi 5-seed + naskah ID → EN (Fase 3) | ◐ nb07 run-2 selesai (fed 0,229±0,184 < local 0,612±0,003); naskah menunggu framing Opsi B |
| 8 | Keputusan framing: temuan-negatif (Opsi B) | ✅ disepakati (Q.6); naskah belum ditulis |
| 9 | Kontrol homogen IID (nb08) — baseline positif | ✅ selesai: CIC 0,563 / UNSW 0,674 (≈ centralized), FL VALID |
| 10 | Jembatan non-IID bertingkat (nb09) — titik putus | ✅ selesai: UNSW putus α≈0,1; CIC tahan sampai α=0,01 (asimetri prior-label) |
| 11 | Eksperimen one-class federated (nb10) — mitigasi | ✅ selesai: federated-AE 0,039 (gagal); diagnosa = ruang SFM kurang separable |
| 12 | Mitigasi heterogeneity-aware (nb12) — FedPer/clustered | ✅ selesai: FedPer 0,731 / clustered 0,745 (~centralized) — mitigasi BERHASIL |
| 13 | Naskah JICTRA (target Scopus Q4 ITB) | ◐ draft `paper-jictra.tex` (self-contained, revisi 2 review, +mitigasi); kompilasi Overleaf |

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


## Q. Penilaian Peluang Diterima di JISA (JUJUR, kondisi run-1)

> Ditulis apa adanya setelah run-1. Bukan motivasi kosong — pijakan untuk keputusan.
> Diperbarui tiap run; run-1 di bawah ini.

### Q.1 Status kelayakan saat ini: RENDAH (dengan hasil run-1 apa adanya)
JISA (Journal of Information Security and Applications, Elsevier, Q1) menuntut
kontribusi yang jelas + hasil yang mendukung klaim. Pada run-1:
- **Klaim utama (H1, SFM=enabler) TIDAK terbukti kuantitatif** — SFM 0,217 vs naif 0,201 (Δ=0,016).
- **Klaim pendukung (H2, FL menutup gap) TERBALIK & signifikan** — federated (0,175) < local-only (0,237), p=0,015.
- Yang tersisa: argumen kualitatif (irisan nama kosong) + jembatan backbone. **Tidak cukup untuk Q1.**

**Kesimpulan jujur:** jika disubmit apa adanya sekarang, **kemungkinan besar ditolak (desk-reject / major-reject)**.

### Q.2 Mengapa ini BISA diperbaiki (akar jelas, bukan cacat fatal)
Hasil buruk run-1 bukan karena ide SFM salah, melainkan karena **setup eksperimen
cacat**: ketimpangan klien 14:1 (CIC 1,14 jt vs UNSW 82 rb) membuat FedAvg didominasi
CIC → UNSW kolaps. Ini masalah METODE, bukan masalah KONSEP. Dapat diperbaiki
(subsample seimbang + kapasitas MLP). Diagnosa lengkap di Bagian D–J.

### Q.3 Skenario setelah RUN-2 (perbaikan) — realistis, tiga kemungkinan
- **Skenario BAIK (peluang JISA naik ke sedang–tinggi):** setelah seimbang, federated-SFM
  ≥ local-only pada GLOBAL-test DAN ablasi SFM jadi tegas (SFM ≫ naif). Maka klaim
  'SFM enabler + FL menutup gap privasi' terdukung → paper layak JISA.
- **Skenario SEDANG (peluang JISA sedang, atau turun ke venue Q2):** federated jadi
  SETARA local-only (tak kalah) + ablasi SFM moderat. Masih publishable, framing jadi
  'SFM memungkinkan federasi lintas-skema dgn performa setara, menjaga privasi'.
- **Skenario KURANG (JISA kecil, pindah venue / ubah framing):** federated tetap di
  bawah. Maka jujur jadikan **studi temuan**: 'SFM perlu tapi tak cukup; FedAvg naif
  gagal pada klien timpang — pelajaran + arah mitigasi'. Tetap kontribusi, tapi bukan Q1.

### Q.4 Yang HARUS ada agar kompetitif di JISA (checklist menuju terbit)
1. **Hasil run-2 mendukung** minimal skenario BAIK/SEDANG (data nyata, bukan dipaksakan).
2. **Backbone adil** — MLP konvergen (bukan under-trained) agar perbandingan sah.
3. **Baseline & ablasi tegas** — SFM vs naif menunjukkan beda bermakna + uji signifikansi.
4. **Analisis non-IID** rapi (H3) + biaya komunikasi (sudah ada kerangkanya).
5. **(Nilai tambah kuat) validasi deployment nyata 3-EC2** — bukti klaim privasi, bukan simulasi.
6. **Posisi vs SOTA FL-NIDS** jelas (41 referensi sudah siap); novelty 'interoperabilitas
   skema-fitur' belum banyak digarap — ini kekuatan bila hasilnya mendukung.
7. **Prasyarat rilis:** Paper 1 (SFM) accepted dulu (fondasi sitasi).

### Q.5 Keputusan arah (disepakati, pra-run-2)
Lanjut **perbaikan metode → run-2** (subsample CIC ~100k + kapasitas MLP), nilai ulang
berdasar DATA run-2, lalu tentukan framing final & kelayakan JISA. **Tidak** menyubmit
hasil run-1. **Tidak** mengarang/menyetel angka demi lolos. Kejujuran data mutlak.

### Q.6 Penilaian ULANG setelah RUN-2 (JUJUR)

**Status kelayakan "FL menang" sebagai klaim Q1: JATUH.** Run-2 menolak jalur ini.
Dua run gagal konsisten → memaksakan klaim FL-superior tidak jujur dan mudah dibantah.

**Yang run-2 BUKTIKAN (positif untuk framing baru):**
- Perbaikan ukuran berhasil untuk centralized (MLP 0,646→0,745) → metode partisi benar.
- MLP centralized GLOBAL 0,771 → arsitektur mampu; kegagalan murni dari AGREGASI FedAvg.
- FedProx mu=0,1 (0,187) > FedAvg (0,075) → proximal meredam drift (sinyal mekanistik).
- Irisan nama kosong (naif-2) → SFM perlu sebagai enabler interoperabilitas (H1 kualitatif).

**Keputusan framing final (Opsi B — temuan negatif informatif):**
Paper 4 **tidak** mengklaim "FL menutup gap". Paper 4 mengklaim:
1. **SFM = enabler interoperabilitas skema-fitur** (tanpa SFM, federasi lintas-tool
   mustahil — bukti kualitatif kuat + analisis adapter A.1/A.2).
2. **Temuan negatif terukur:** di bawah heterogenitas distribusi-label lintas-dataset,
   FedAvg/FedProx naif **divergen** (kurva + 5-seed CI + uji signifikansi) — SFM
   perlu-tapi-tak-cukup.
3. **Arah mitigasi:** FL-NIDS lintas-dataset butuh agregasi sadar-heterogenitas
   (personalized/clustered FL) — future work beralasan.

**Peluang venue dengan framing baru:**
- JISA (Q1): **sedang-rendah**. Temuan negatif bisa diterima Q1 bila analisisnya dalam
  (mekanisme divergence + ablasi tegas + arah mitigasi konkret). Butuh pekerjaan analisis
  tambahan, bukan sekadar lapor gagal.
- Realistis: **Q2 (mis. venue FL/sekuriti terapan)** lebih cocok untuk studi temuan-negatif,
  kecuali kita tambah kontribusi metodologis (mis. implementasi+evaluasi clustered-FL yang
  memperbaiki divergence) → ini akan jadi run-3/paper lebih besar.

**Opsi run-3 (opsional, pelengkap temuan negatif — BUKAN penyelamat klaim):**
FedProx(mu=0,1) + LR 1e-3 + LOCAL_EPOCHS=1 + early-stop ~round 10. Ekspektasi jujur:
federated ≈ puncak kurva (~0,27) namun **tetap < local-only 0,61**. Berguna untuk
melaporkan "konfigurasi terbaik yang dapat dicapai pun tak menutup gap" → memperkuat
temuan negatif, bukan membalikkannya.


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

