#!/bin/bash
# ============================================================
# NIDS01 - Packet Capture DI TARGET
# Target menerima semua serangan, jadi capture di sini menangkap
# seluruh trafik attack + benign. Setelah selesai, pcap di-upload
# ke S3 agar Analyzer bisa download & inference.
#
# Alasan: Analyzer TIDAK berada di jalur trafik Attacker->Target
# (bukan gateway/mirror), sehingga tcpdump di Analyzer tidak
# melihat paket antar keduanya.
#
# Usage:
#   ./capture_target.sh RT-S1 [durasi_detik] [attacker_ip] [iface]
# ============================================================
set -u
SCENARIO="${1:-RT-S1}"
DURATION="${2:-440}"
ATTACKER_IP="${3:-10.3.1.214}"
IFACE="${4:-ens5}"
BUCKET="ssh-detection-features-232032302717"

PCAP="/tmp/${SCENARIO}.pcap"

echo "[$(date +%H:%M:%S)] === CAPTURE START (TARGET): $SCENARIO ==="
echo "  Interface   : $IFACE"
echo "  Attacker    : $ATTACKER_IP"
echo "  Durasi      : ${DURATION}s"
echo "  Output      : $PCAP"

# Capture semua trafik yang melibatkan attacker IP (attack + akan termasuk benign dari analyzer/curl)
# Pakai 'host attacker' + port 80/22 untuk menangkap benign juga
sudo timeout "$DURATION" tcpdump -i "$IFACE" "host $ATTACKER_IP or (tcp port 80 or tcp port 22)" -w "$PCAP" 2>/dev/null

echo "[$(date +%H:%M:%S)] === CAPTURE DONE ==="
ls -la "$PCAP"

# Upload ke S3
echo "[$(date +%H:%M:%S)] Upload pcap ke S3..."
aws s3 cp "$PCAP" "s3://${BUCKET}/captures/${SCENARIO}.pcap" --region ap-southeast-1
echo "[$(date +%H:%M:%S)] Uploaded: s3://${BUCKET}/captures/${SCENARIO}.pcap"
