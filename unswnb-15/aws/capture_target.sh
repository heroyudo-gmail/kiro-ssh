#!/bin/bash
# ============================================================
# T10 UNSW-NB15 — Capture di TARGET (pelajaran NIDS-01).
# Analyzer TIDAK di jalur trafik -> capture WAJIB di Target.
# Interface WAJIB spesifik (ens5), JANGAN -i any (SLL -> 0 flow di NFStream).
# ============================================================
# Usage:
#   Fase 1 (FAR, jangka panjang, rotasi per jam):
#     sudo ./capture_target.sh far
#   Fase 2 (deteksi, ~7 menit, satu file):
#     sudo ./capture_target.sh detect <clean|evasion>
set -e

IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)
[ -z "$IFACE" ] && IFACE=ens5
OUTDIR=/opt/unsw/captures
mkdir -p "$OUTDIR"
BUCKET="${S3_BUCKET:-}"

MODE=$1
echo "Interface: $IFACE (verifikasi: ip -o link)"

if [ "$MODE" = "far" ]; then
  # Fase 1: rotasi pcap per jam. TANPA serangan (trafik normal saja).
  echo "[FAR] capture rotasi 3600s -> $OUTDIR/far_%Y%m%d_%H.pcap (Ctrl-C utk stop)"
  exec sudo tcpdump -i "$IFACE" -G 3600 -w "$OUTDIR/far_%Y%m%d_%H.pcap"
elif [ "$MODE" = "detect" ]; then
  VARIANT=${2:-clean}
  PCAP="$OUTDIR/detect_${VARIANT}.pcap"
  echo "[DETECT] capture -> $PCAP (jalankan attack_scenario.sh di Attacker, lalu Ctrl-C)"
  exec sudo tcpdump -i "$IFACE" -w "$PCAP"
else
  echo "Usage: $0 far | detect <clean|evasion>"; exit 1
fi
