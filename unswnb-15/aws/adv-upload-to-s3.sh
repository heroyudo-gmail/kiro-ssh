#!/bin/bash
# ============================================================
# Paper 2 (Adversarial) - Upload skrip AWS ke S3 (satu perintah).
# Skrip inferensi/serangan/capture -> s3://<bucket>/unsw-far/scripts-p2/
# Model Paper 2 (dari notebook 11) sudah di s3://<bucket>/unsw-far/paper2/.
#
# Usage (dari folder aws/):
#   ./adv-upload-to-s3.sh
#   S3_BUCKET=... REGION=... ./adv-upload-to-s3.sh   # override
# ============================================================
set -e
S3_BUCKET=${S3_BUCKET:-ssh-detection-features-232032302717}
REGION=${REGION:-ap-southeast-1}
PREFIX="unsw-far/scripts-p2"
FILES=(adv-attack-scenario.sh adv-capture.sh adv-extract-infer.py adv-runbook.md)

echo "[gate] cek file skrip ada..."
for f in "${FILES[@]}"; do
  [ -f "$f" ] || { echo "  MISSING: $f (jalankan dari folder aws/)"; exit 1; }
done

echo "[gate] cek kredensial & akses bucket..."
aws sts get-caller-identity >/dev/null || { echo "  kredensial AWS tidak valid"; exit 1; }
aws s3 ls "s3://$S3_BUCKET/" >/dev/null || { echo "  tak bisa akses bucket $S3_BUCKET"; exit 1; }

echo "[gate] cek model Paper 2 sudah ada di S3 (dari notebook 11)..."
if ! aws s3 ls "s3://$S3_BUCKET/unsw-far/paper2/CIC_to_UNSW/scaler.pkl" --region "$REGION" >/dev/null 2>&1; then
  echo "  PERINGATAN: model Paper 2 belum ada di s3://$S3_BUCKET/unsw-far/paper2/."
  echo "  Jalankan notebook 11_adv_fewshot_pipeline.ipynb dulu. Lanjut upload skrip saja."
fi

echo "[upload] -> s3://$S3_BUCKET/$PREFIX/"
for f in "${FILES[@]}"; do
  aws s3 cp "$f" "s3://$S3_BUCKET/$PREFIX/$f" --region "$REGION"
done

echo "[selesai] isi $PREFIX/:"
aws s3 ls "s3://$S3_BUCKET/$PREFIX/" --region "$REGION"
