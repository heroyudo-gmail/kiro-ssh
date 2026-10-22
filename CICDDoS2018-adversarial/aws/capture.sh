#!/bin/bash
# ============================================================
# NIDS01 - Packet Capture (di Analyzer)
# Capture trafik ke/dari target selama skenario berjalan.
# WAJIB capture per-interface (ens5), JANGAN -i any.
#
# Usage:
#   ./capture.sh RT-S1 [durasi_detik] [target_ip] [iface]
#   default: durasi 440s (~7.3 menit), target 10.3.2.38, iface ens5
# ============================================================
set -u
SCENARIO="${1:-RT-S1}"
DURATION="${2:-440}"
TARGET_IP="${3:-10.3.2.38}"
IFACE="${4:-ens5}"

PCAP="/opt/nids/captures/${SCENARIO}.pcap"
mkdir -p /opt/nids/captures

echo "[$(date +%H:%M:%S)] === CAPTURE START: $SCENARIO ==="
echo "  Interface : $IFACE"
echo "  Target    : $TARGET_IP"
echo "  Durasi    : ${DURATION}s"
echo "  Output    : $PCAP"

# Capture semua trafik yang melibatkan target IP
sudo timeout "$DURATION" tcpdump -i "$IFACE" host "$TARGET_IP" -w "$PCAP" 2>/dev/null

echo "[$(date +%H:%M:%S)] === CAPTURE DONE ==="
ls -la "$PCAP"
echo "Jalankan inference dengan:"
echo "  python /opt/nids/scripts/extract_and_infer.py --scenario $SCENARIO --pcap $PCAP"
