#!/bin/bash
# ============================================================
# Paper 2 (Adversarial) - Capture di Target+Analyzer.
# Membungkus tcpdump pada iface SPESIFIK (bukan -i any -> 0 flow di NFStream).
# Usage (di Target+Analyzer):
#   ./adv-capture.sh start <nama>    # mulai capture -> /opt/adv/captures/<nama>.pcap
#   ./adv-capture.sh stop            # hentikan capture terakhir
# Contoh:
#   ./adv-capture.sh start detect_clean
#   ./adv-capture.sh start detect_evasion
# ============================================================
set -e
ACTION=${1:-}
NAME=${2:-capture}
CAPDIR=/opt/adv/captures
PIDF=/tmp/adv_tcpdump.pid
mkdir -p "$CAPDIR"

IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)
[ -z "$IFACE" ] && { echo "ERROR: iface default tak terdeteksi"; exit 1; }

case "$ACTION" in
  start)
    echo "[capture] iface=$IFACE -> $CAPDIR/$NAME.pcap"
    sudo tcpdump -i "$IFACE" -w "$CAPDIR/$NAME.pcap" >/dev/null 2>&1 &
    echo $! | sudo tee "$PIDF" >/dev/null
    echo "[capture] PID=$(cat "$PIDF") berjalan. Jalankan serangan, lalu: $0 stop"
    ;;
  stop)
    if [ -f "$PIDF" ]; then
      sudo kill "$(cat "$PIDF")" 2>/dev/null || true
      sleep 2
      sudo rm -f "$PIDF"
      echo "[capture] dihentikan."
      ls -lh "$CAPDIR"/
    else
      echo "[capture] tidak ada PID tersimpan ($PIDF)."
    fi
    ;;
  *)
    echo "Usage: $0 <start|stop> [nama]"; exit 1;;
esac
