# notebook_xai — Eksperimen Paper 4 (XAI untuk NIDS)

Eksperimen pendukung `paper4-xai.md`. **Tanpa Semantic Feature Mapping.**
Lintas-dataset: **CIC-IDS2017 (referensi/latih) → CSE-CIC-IDS2018 (target transfer)**,
keduanya CICFlowMeter. Arah utama **2017 → 2018** (replikasi langsung paper referensi JTIIK);
arah balik 2018 → 2017 ikut dihitung sebagai penguat.

## Dijalankan di AWS SageMaker (bukan lokal)

Alur kerja baku proyek ini (lihat `.kiro/steering/compute-workflow.md`):

1. Kiro menyiapkan notebook → **push ke GitHub**.
2. Di SageMaker: **`git pull`** repo.
3. Isi sel **KONFIG S3** di `01` (nama bucket + prefix dataset & artefak).
4. **Run** `01 → 02 → 03` berurutan.
5. Tiap notebook meng-**upload `artifacts/` ke S3** di sel terakhir.
6. Komputer lokal **download `artifacts/` dari S3** → dipakai mengisi `[ISI]` di paper.

## Urutan menjalankan

1. `01_preprocessing.ipynb` — sync CSV dari S3, normalisasi kolom/label, irisan fitur,
   simpan `artifacts/cic2017.pkl`, `artifacts/cic2018.pkl`, `artifacts/schema_summary.json`.
2. `02_cross_dataset_diagnosis.ipynb` — untuk **XGBoost DAN Random Forest**: within/cross,
   weighted-F1 vs MCC, PR-AUC, kalibrasi ambang, few-shot, multi-seed
   → `artifacts/diagnosis_results.json` + `artifacts/model_comparison.json`.
3. `03_shap_xai.ipynb` — SHAP sadar-kondisi (model gagal vs pulih), untuk kedua model
   → `artifacts/shap_results.json`.

Angka dari file JSON di `artifacts/` dipakai mengisi placeholder `[ISI]` di `paper4-xai.md`.

## Model

Dua model dijalankan dan dibandingkan: XGBoost dan Random Forest (`MODELS = ['xgb', 'rf']`).
XGBoost **wajib** terpasang (notebook meng-`pip install` di sel pertama). Untuk satu model
saja, ubah daftar `MODELS`.

## Paket Python

Di-install otomatis oleh sel pertama tiap notebook:
```
numpy pandas scipy scikit-learn xgboost imbalanced-learn shap
```

## Parameter yang bisa diubah

- `01`: `S3_BUCKET`, `S3_RAW_CIC2017`, `S3_RAW_CIC2018`, `S3_ARTIFACTS_OUT`,
  `SYNC_FROM_S3`, `MAX_ROWS_PER_FILE`.
- `02`/`03`: `S3_ARTIFACTS_OUT` (samakan dgn 01), `SEEDS`, `FRACS`, `TOPK`, `USE_SMOTE`, `MODELS`.

---

## DATA YANG PERLU DISIAPKAN DI S3

### Dataset 1 — CIC-IDS2017 (referensi / latih)
- Sumber resmi: https://www.unb.ca/cic/datasets/ids-2017.html
- Yang dibutuhkan: **CSV hasil CICFlowMeter** (per-flow), bukan PCAP mentah.
- Upload ke S3 prefix yang ditunjuk `S3_RAW_CIC2017` (mis. `s3://<bucket>/raw/cic-ids2017/`).

### Dataset 2 — CSE-CIC-IDS2018 (target lintas)
- Sumber resmi: https://www.unb.ca/cic/datasets/ids-2018.html
- Yang dibutuhkan: **CSV CICFlowMeter**.
- Upload ke S3 prefix yang ditunjuk `S3_RAW_CIC2018` (mis. `s3://<bucket>/raw/cse-cic-ids2018/`).

### Format file yang notebook harapkan
- **CSV** dengan header (koma sebagai pemisah). Satu baris = satu flow.
- Harus ada **kolom label** (nama mengandung "label", case-insensitive). Notebook memetakan
  ke biner: mengandung "benign"/"normal" → 0, selain itu → 1.
- Kolom fitur numerik CICFlowMeter (mis. Flow Duration, Tot Fwd Pkts, dst.).
  Kolom metadata (IP, port, protocol, timestamp, flow id) otomatis dibuang.
- Nama kolom tidak perlu diselaraskan manual — notebook menormalisasi nama + mengambil
  irisan otomatis. Pastikan keduanya CSV CICFlowMeter.

### Catatan ukuran & kinerja
- `MAX_ROWS_PER_FILE` (default 100.000) membatasi sampel per file secara stratified.
  Untuk XGBoost/RF tabular cukup instance CPU ber-RAM besar (mis. `ml.m5.2xlarge` /
  `ml.r5.xlarge`); **GPU tidak diperlukan**.

### Yang dibutuhkan untuk lanjut mengisi paper
Cukup **folder `artifacts/`** hasil ketiga notebook (4 file JSON):
`schema_summary.json`, `diagnosis_results.json`, `model_comparison.json`, `shap_results.json`.
Download dari S3 ke lokal, lalu angka-angkanya mengisi semua `[ISI]` di `paper4-xai.md`.
