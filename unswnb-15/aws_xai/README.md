# aws_xai — Komputasi AWS SageMaker untuk Paper 4 (XAI)

Semua eksperimen `notebook_xai/` dijalankan di **AWS SageMaker** (bukan lokal), sesuai
alur kerja proyek di `.kiro/steering/compute-workflow.md`.

## Alur kerja

1. **Lokal/Kiro**: siapkan notebook di `../notebook_xai/` → push ke GitHub.
2. **SageMaker**: buka Studio/Notebook Instance → `git pull` repo.
3. **SageMaker**: isi sel KONFIG S3 di `01_preprocessing.ipynb`, lalu run `01 → 02 → 03`.
   - Sel pertama tiap notebook meng-`pip install` dependensi.
   - `01` meng-`aws s3 sync` CSV mentah dari S3 ke instance.
   - Sel terakhir tiap notebook meng-`aws s3 sync artifacts/ → S3`.
4. **Lokal**: `aws s3 sync s3://<bucket>/paper4-xai/artifacts/ ./artifacts/` → pakai JSON
   untuk mengisi `[ISI]` di `../paper4-xai.md`.

## Prasyarat di S3 (ISI nama bucket milik mitra APN)

```
s3://<bucket>/raw/cic-ids2017/       # CSV CICFlowMeter CIC-IDS2017  (referensi)
s3://<bucket>/raw/cse-cic-ids2018/   # CSV CICFlowMeter CSE-CIC-IDS2018 (target)
s3://<bucket>/paper4-xai/artifacts/  # tujuan upload hasil (dibuat otomatis)
```

## Instance SageMaker

- XGBoost + Random Forest pada data tabular → **CPU, RAM besar**. Contoh:
  `ml.m5.2xlarge` (8 vCPU/32 GB) atau `ml.r5.xlarge` (4 vCPU/32 GB).
- **GPU tidak diperlukan** (hindari `ml.p*`/`ml.g*`).
- IAM role SageMaker harus punya izin baca/tulis ke bucket S3 di atas.

## Catatan
Biaya AWS di-support mitra AWS APN. Tidak ada eksekusi di komputer lokal selain penulisan
paper dan pengisian angka hasil.
