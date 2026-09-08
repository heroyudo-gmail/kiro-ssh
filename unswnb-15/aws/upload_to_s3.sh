#!/bin/bash
# ============================================================
# T10 UNSW-NB15 — Bootstrap: unggah semua skrip (+ model bila ada) ke S3.
# Menyatukan prasyarat runbook §1 (upload skrip) jadi satu perintah.
# Jalankan dari folder aws/ di mesin yang punya kredensial AWS + skrip terbaru.
#
# Usage:
#   ./upload_to_s3.sh
#   S3_BUCKET=nama-bucket-lain REGION=ap-southeast-1 ./upload_to_s3.sh
# ============================================================
set -euo pipefail

S3_BUCKET="${S3_BUCKET:-ssh-detection-features-232032302717}"
REGION="${REGION:-ap-southeast-1}"
PREFIX="unsw-far"
SCRIPTS=(unsw_extract_infer.py capture_target.sh attack_scenario.sh benign_traffic.sh)
MODELS=(modelA_9feat.json deploy_meta_9feat.json)   # dihasilkan notebook 09 (opsional di sini)

echo "== T10 upload_to_s3 =="
echo "Bucket : s3://$S3_BUCKET/$PREFIX/"
echo "Region : $REGION"

# --- 0) Prasyarat: pastikan berada di folder yang benar ---
for s in "${SCRIPTS[@]}"; do
  [ -f "$s" ] || { echo "ERROR: $s tidak ada. Jalankan dari folder aws/."; exit 1; }
done

# --- 1) GATE: verifikasi satuan 'duration' sudah selaras scaler CIC (mikrodetik) ---
# Scaler deployment di-fit pada CIC Flow Duration (us); extractor HARUS keluarkan us
# untuk fitur duration (dur_ms*1000), sambil pembagi laju tetap detik (dur_s).
if ! grep -q "dur_feat_us" unsw_extract_infer.py; then
  echo "ERROR: unsw_extract_infer.py belum versi ter-FIX (baris 'dur_feat_us' tak ditemukan)."
  echo "       Fitur 'duration' HARUS mikrodetik (dur_ms*1000) agar cocok scaler CIC. Batalkan."
  exit 1
fi
echo "[GATE] duration-unit OK (dur_feat_us ditemukan; selaras scaler CIC mikrodetik)."

# --- 2) Verifikasi kredensial & bucket dapat diakses ---
aws sts get-caller-identity --region "$REGION" >/dev/null 2>&1 || {
  echo "ERROR: kredensial AWS tidak aktif / tidak valid."; exit 1; }
aws s3 ls "s3://$S3_BUCKET/" --region "$REGION" >/dev/null 2>&1 || {
  echo "ERROR: bucket s3://$S3_BUCKET tidak dapat diakses."; exit 1; }

# --- 3) Upload skrip ---
echo "[1/2] Upload skrip -> s3://$S3_BUCKET/$PREFIX/scripts/"
for s in "${SCRIPTS[@]}"; do
  aws s3 cp "$s" "s3://$S3_BUCKET/$PREFIX/scripts/$s" --region "$REGION"
done

# --- 4) Upload model bila ada di folder (opsional; biasanya dari notebook 09) ---
echo "[2/2] Upload model (jika ada di folder ini) -> s3://$S3_BUCKET/$PREFIX/models/"
for m in "${MODELS[@]}"; do
  if [ -f "$m" ]; then
    aws s3 cp "$m" "s3://$S3_BUCKET/$PREFIX/models/$m" --region "$REGION"
  else
    echo "  (lewati $m — tidak ada di folder; hasilkan via notebooks/09_model_efficiency.ipynb)"
  fi
done

# --- 5) Ringkasan isi S3 ---
echo "== Isi S3 sekarang =="
echo "-- scripts --"; aws s3 ls "s3://$S3_BUCKET/$PREFIX/scripts/" --region "$REGION" || true
echo "-- models  --"; aws s3 ls "s3://$S3_BUCKET/$PREFIX/models/"  --region "$REGION" || true
echo "SELESAI. Bila 'models' kosong, jalankan notebook 09 dulu untuk model+meta, lalu ulang."
