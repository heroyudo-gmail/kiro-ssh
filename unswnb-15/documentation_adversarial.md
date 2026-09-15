# Dokumentasi Percobaan — Paper 2 (Adversarial Robustness NIDS)

> **Fungsi file ini:** memori persisten percobaan Paper 2. Kalau konteks hilang/reset,
> BACA FILE INI DULU sebelum bekerja. Berisi: ringkasan riset, peta notebook↔tabel,
> status revisi reviewer, daftar tugas tersisa, dan keputusan kunci.
> **Untuk operasi AWS (deploy/serangan/inferensi):** lihat `aws/adv-runbook.md`.
>
> **PETA MEMORI (2 file per paper).** Ini **Paper 2** (adversarial, lanjutan Paper 1).
> Pasangan Paper 2: file ini + `aws/adv-runbook.md`. **Paper 1** (SFM + few-shot, sumbu
> generalisasi) ada di `documentation.md` + `aws/runbook.md`. Sumber kebenaran detail
> tetap notebook (`notebooks/`) + `git log`; dua file .md ini adalah pintu masuknya.

---

## 1. Identitas paper

- **File utama:** `unswnb-15/paper2-adversarial.tex`
- **Judul (setelah revisi #18):** *When Cross-Network Generalization Meets Adversarial
  Evasion: A Study of Few-Shot-Calibrated XGBoost NIDS under Protocol-Consistent Attacks*
- **Penulis:** Hero Yudo Martono, Iwan Syarif, Ferry Astika Saputra
- **Bahasa:** isi Indonesia; istilah teknis, judul, caption, highlights Inggris.
- **Bibliografi:** `thebibliography` manual (bukan .bib). Compile: **pdfLaTeX** di Overleaf,
  2× recompile. Butuh folder `figure-p2/` (2 PNG + 2 tikz `.tex`) ikut ter-upload.
- **Target jurnal:** JISA-like (Elsevier). Angka desimal pakai koma (gaya Indonesia).

## 2. Pertanyaan riset & pesan utama (JANGAN diubah tanpa alasan)

Lanjutan **Paper 1** (SFM+few-shot, `\cite{martono2024sfm}`). Paper 1 = sumbu generalisasi
(distribution shift). Paper 2 = sumbu kedua (evasion adversarial) + **interaksi keduanya**.

**RQ:** Dapatkah satu XGBoost ringan (9 fitur SFM) menjaga generalisasi lintas-jaringan
(via few-shot) SEKALIGUS tahan evasion (via adversarial training) — dan mengapa
keberadaannya bersyarat pada arah?

**Pesan utama (hasil campuran, dilaporkan JUJUR — ini kekuatan paper, bukan kelemahan):**
1. Generalisasi lintas-jaringan hanya dari **few-shot**, bukan adversarial training.
2. Adversarial training di atas few-shot **tidak merusak** generalisasi (paritas).
3. Ketahanan adaptive **asimetris terhadap arah** source→target.
4. Adversarial training **tidak universal**: signifikan MEMBANTU di UNSW→CIC, tapi
   signifikan MERUGIKAN di CIC→UNSW-PGD (robust overfitting ke serangan 1-langkah).

## 3. Setup eksperimen (fakta yang jangan dicek ulang)

- **Model:** XGBoost biner. max_depth=8, lr=0.1, n_estimators=200, subsample/colsample=0.8,
  tree_method=hist.
- **9 fitur SFM:** duration, fwd_pkts, bwd_pkts, fwd_bytes, bwd_bytes, fwd_mean, bwd_mean,
  src_load, dst_load.
- **Mapping kolom:** CIC (idx 0) / UNSW (idx 1) → lihat `MAP_A` di notebook 14.
- **z-score:** StandardScaler fit **train sumber saja**, transform ke uji/target/AWS.
- **4 varian:** baseline | few-shot (+1% target) | adv (FGSM adv-training, ratio 0.20,
  eps_train 0.1) | few-shot+adv (usulan).
- **5 seed:** {13,42,101,202,303}. Semua tabel berbasis-seed = mean (±std / CI / p-value).
- **Serangan (suite berjenjang):** FGSM 1-langkah (finite-difference saliency, h=0.01) →
  PGD iteratif (iter=10, alpha=0.02, L∞-ball) → AutoAttack/tree-specific (future work).
  eps evaluasi {0.05, 0.1, 0.2}.
- **PCFS (protocol-consistent feature-space):** proyeksi valid = x≥0, integer packets,
  B≥p, mean=B/p, load ℓ=B/d direkonsiliasi, monotonik add-only. BUKAN klaim deliverability.
- **Metrik:** MCC utama + ASR + recall/precision/F1 + FPR/balanced-acc.

## 4. Dataset (angka pasti, dari `dataset_stats.csv`)

| Dataset | total | attack | benign | split |
|---|---|---|---|---|
| CSE-CIC-IDS2018 | 1.623.261 | 274.808 | 1.348.453 | stratified 70/30, seed-fixed |
| UNSW-NB15 | 257.673 | 164.673 | 93.000 | official 175.341/82.332 |
| AWS (real, self-labelled) | 17.753 | 17.620 | 133 | stratified train/test per seed |

- Notasi arah **A→B = latih di A, uji di B** (domain adaptation). CIC→UNSW & UNSW→CIC.
- Leakage control: 1% few-shot HANYA dari partisi train target; clean-target dievaluasi
  hanya di test disjoint. D_tgt = D_calib ⊔ D_test.

## 5. Peta NOTEBOOK ↔ TABEL (penting untuk reproduksi)

> **PRINSIP PENTING (jangan langgar):** Notebook **11–17 SEMUA milik Paper 2**
> (notebook ≤10 milik Paper 1, mis. `10_wasserstein_shift.ipynb`). **JANGAN membuat
> notebook/sel baru yang menghitung ulang hasil yang sudah ada di notebook sebelumnya.**
> Buat baru HANYA jika hasil yang dibutuhkan belum pernah dihasilkan. Sebelum menambah
> eksperimen, cek tabel di bawah dulu — kemungkinan besar sudah ada.

Semua di `unswnb-15/notebooks/`. Output → `paper2_reviewer_out/` + S3
`s3://ssh-detection-features-232032302717/unsw-far/paper2_reviewer/`.

| Notebook | Peran | Menghasilkan | Tabel/dipakai di paper |
|---|---|---|---|
| `11_adv_fewshot_pipeline.ipynb` | INTI: latih 4 varian (baseline/fewshot/adv/fewshot_adv), 2 arah; simpan model+scaler ke S3 `unsw-far/paper2/` | paper2_pipeline_meta.json, model .json + scaler.pkl | fondasi semua eksperimen + deploy AWS (runbook) |
| `12_adv_evaluation.ipynb` | Evaluasi clean/evasion/adaptive 4 varian (single-run) | paper2_eval_results.json | `tab:p2main` |
| `13_rangkuman_adversarial.ipynb` | Rangkuman cerita + AWS 2-EC2 (sel 5b) | ringkasan, aws JSON | `tab:aws`, `tab:aws_unsw` |
| `14_reviewer_experiments.ipynb` | Revisi reviewer A2/A3/A5/B5 + #8/#10/#14 | reviewer_agg, multiattack_*, significance_*, perturbation_metrics, dataset_stats | `tab:multiattack`, `tab:fewshot_seeds`, `tab:significance`, `tab:advmetrics`, `tab:dataset` |
| `15_aws_fewshot_calibration.ipynb` | Validasi 3-tahap AWS (offline, pakai ulang aws_labeled) | aws_stages_agg.csv | `tab:aws_stages` |
| `16_defense_baselines.ipynb` | Pembanding pertahanan (PGD-AT/Gaussian/rand-smoothing) | defense_baselines_agg.csv | `tab:defense_baselines` ⏳ |
| `17_decision_cell.ipynb` | Bukti empiris narrow-cell (kappa/w/d_boundary/crossing) | decision_cell.csv | `tab:decisioncell` ⏳ |

**Aturan mana notebook menghasilkan tabel apa → JANGAN duplikasi.** Contoh: kalau butuh
angka clean-target 4 varian, itu SUDAH ada (nb11/12 → tab:p2main; nb14 → tab:fewshot_seeds).
Kalau butuh ASR/recall/precision adversarial, SUDAH ada (nb14 → reviewer_agg → tab:advmetrics).

**Data sumber notebook (path di SageMaker):**
`../../CICDDoS2018/data/cleaned_100.pkl`, `../data/UNSW_NB15_{testing,training}-set.csv`,
`aws_labeled/detect_{clean,volumetric}_flows.csv` (9 fitur + ground_truth; ter-track di git).

## 6. Angka kunci yang SUDAH masuk paper (untuk sanity-check)

- **tab:p2main (nb12, single-run):** CIC→UNSW few-shot+adv clean 0,696 / adaptive 0,495;
  UNSW→CIC few-shot+adv clean 0,897 / adaptive −0,025.
- **tab:fewshot_seeds (5 seed clean MCC):** CIC→UNSW few-shot 0,650±0,016, few-shot+adv
  0,662±0,012; UNSW→CIC few-shot 0,899±0,004, few-shot+adv 0,898±0,004. (adv std besar 0,203)
- **tab:significance (paired t-test):** CIC→UNSW clean p=0,24 (ns); CIC→UNSW PGD p=0,012
  (adv MERUGIKAN, Δ−0,222); UNSW→CIC FGSM p=0,003 (Δ+0,389); UNSW→CIC PGD p=0,033 (Δ+0,302).
- **tab:advmetrics (ASR):** CIC→UNSW few-shot FGSM ASR 0,02 (MCC turun tapi ~tak ada evasion);
  UNSW→CIC few-shot FGSM ASR 0,985; few-shot+adv turunkan ke 0,872 (FGSM)/0,738 (PGD).
- **tab:aws_stages (nb15, 3-tahap):** CIC→AWS MCC clean S0 0,001→S1 0,184→S2 0,246;
  recall S0 0,000→S1 0,970. UNSW→AWS MCC S0 0,052→S1 0,026→S2 0,143; recall ~0,99.
  Adversarial S2 lemah (−0,04..0,07). → few-shot transfer utk generalisasi, bukan evasion.
- **perturbation_metrics:** serangan sparse ~2,6–5,4 fitur; valid-flow 0,79–1,0;
  FPR UNSW 0,33 / CIC 0,015. (L∞/L2 mentah TIDAK dilaporkan — artefak skala load.)

## 7. Status revisi reviewer

| # | Isu | Status |
|---|---|---|
| 1 | Adaptive white-box lemah (butuh PGD/suite) | ✅ suite FGSM→PGD→AutoAttack, tab:multiattack terisi |
| 3 | Novelty = kombinasi komponen | ✅ reframe jadi temuan interaksi/rezim asimetris |
| 5 | "functional-preserving" over-claim | ✅ diganti PCFS di seluruh paper |
| 6 | AWS belum validasi pipeline | ✅ nb15 validasi 3-tahap, tab:aws_stages terisi |
| 7 | Leakage few-shot 1% | ✅ D_calib⊔D_test eksplisit + 5 seed |
| 8 | Variance/signifikansi | ✅ tab:significance p-value nyata |
| 9 | Kurang defense baseline | ✅ nb16 (PGD-AT/Gauss/smoothing) — ⏳ tab:defense_baselines PLACEHOLDER |
| 10 | Metrik selain MCC (ASR dll) | ✅ tab:advmetrics + perturbation_metrics |
| 11 | Narrow-cells spekulatif | ✅ nb17 kuantifikasi — ⏳ tab:decisioncell PLACEHOLDER |
| 12 | MCC AWS "artefak" | ✅ reframe jadi trade-off sensitivitas-spesifisitas |
| 13 | Threat model formal | ✅ tab:threatmodel |
| 14 | Dataset section tipis | ✅ tab:dataset + paragraf praproses |
| 17 | Hasil buruk = aset | ✅ paragraf "Pesan utama" di conclusion |
| 18 | Judul misleading | ✅ judul baru (research-question-driven) |
| 19-B4 | Hubungan dgn Paper 1 | ✅ paragraf khusus di related work |
| C | Polishing (bahasa/abstract/highlights) | ⏳ sebagian: highlights ✅; abstract/referensi nanti setelah angka final |

Belum pernah muncul dari reviewer: #2, #4, #15, #16.

## 8. TUGAS TERSISA (yang menunggu / belum selesai)

1. **Isi `tab:defense_baselines`** dari `defense_baselines_agg.csv` (nb16). PLACEHOLDER `--`.
2. **Isi `tab:decisioncell`** dari `decision_cell.csv` (nb17) + verifikasi prediksi
   `d_boundary^CIC < UNSW`, `w^CIC < UNSW`, `kappa^CIC < UNSW`. Kalau TIDAK terkonfirmasi,
   revisi narasi jujur (jangan paksakan).
3. **Polishing prioritas C:** abstract (padatkan, cerminkan angka final), reference
   formatting, nomenclature/notasi. Kerjakan PALING AKHIR.

## 9. CARA AMBIL HASIL DARI S3 (TERBUKTI JALAN — jangan muter-muter)

- **PowerShell di workspace ini rendering-nya rusak** (echo berulang, exit -1) TAPI perintah
  tetap tereksekusi. Solusi: **redirect output ke file lalu baca file dgn read tool.**
- AWS CLI + kredensial user `hero` (akun 232032302717) BERFUNGSI dari workspace.
- Pola download (contoh):
  ```
  aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/paper2_reviewer/<file>.csv paper2_reviewer_out/ --region ap-southeast-1 > _dl.txt 2>&1
  ```
  lalu baca CSV-nya dengan read tool, olah, isi ke .tex, commit.
- Artefak CSV kecil di-whitelist di root `.gitignore` (`!unswnb-15/paper2_reviewer_out/*.csv`,
  `!unswnb-15/notebooks/aws_labeled/*.csv`) supaya ter-track.

## 10. KEBIASAAN KERJA (konvensi yang sudah dipakai)

- Setiap revisi reviewer: edit `.tex` → verifikasi `\begin`/`\end` seimbang + cite↔bibitem
  cocok → commit granular per-review → push ke `origin/main`.
- JANGAN mengarang angka. Placeholder `--` sampai hasil nyata ada. Semua angka dari
  eksperimen (notebook) atau file rilis dataset.
- Notebook: docstring pakai `#` (BUKAN triple-quote) — triple-quote di JSON notebook
  pernah bikin SyntaxError escape. Validasi tiap edit notebook: json.load + ast.parse.
- Angka desimal di tabel .tex: koma (`0{,}696`), konsisten gaya paper.
