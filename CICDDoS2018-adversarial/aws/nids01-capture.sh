#!/bin/bash
# =============================================================
# NIDS01 Real-Traffic Testing — Packet Capture (di Analyzer)
# =============================================================
# Dijalankan di EC2 Analyzer
# Usage: ./nids01-capture.sh start <SCENARIO> <TARGET_IP>
#        ./nids01-capture.sh stop
# =============================================================

ACTION=${1:-"help"}
SCENARIO=${2:-"clean"}
TARGET_IP=${3:-"10.3.2.x"}
CAPTURE_DIR="/opt/nids/captures"

mkdir -p $CAPTURE_DIR

case $ACTION in
    start)
        PCAP_FILE="${CAPTURE_DIR}/nids01_${SCENARIO}.pcap"
        echo "============================================================"
        echo "  NIDS01 — START CAPTURE: $SCENARIO"
        echo "============================================================"
        echo "  Target IP filter: $TARGET_IP"
        echo "  Output: $PCAP_FILE"
        echo "  Start: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "============================================================"
        
        # Start tcpdump in background
        sudo tcpdump -i eth0 host $TARGET_IP -w $PCAP_FILE &
        TCPDUMP_PID=$!
        echo $TCPDUMP_PID > /tmp/nids01_tcpdump.pid
        
        echo ""
        echo "  tcpdump PID: $TCPDUMP_PID"
        echo "  Capturing..."
        echo ""
        echo "  Setelah serangan selesai (~12 menit), jalankan:"
        echo "    ./nids01-capture.sh stop"
        ;;
    
    stop)
        if [ -f /tmp/nids01_tcpdump.pid ]; then
            PID=$(cat /tmp/nids01_tcpdump.pid)
            echo "Stopping tcpdump (PID: $PID)..."
            sudo kill $PID 2>/dev/null
            sleep 3
            rm -f /tmp/nids01_tcpdump.pid
            
            echo ""
            echo "Capture files:"
            ls -lh ${CAPTURE_DIR}/nids01_*.pcap 2>/dev/null
            echo ""
            echo "Next step: jalankan extract & inference:"
            echo "  source /opt/nids-env/bin/activate"
            echo "  python3 /opt/nids/scripts/nids01_extract_infer.py <SCENARIO>"
        else
            echo "ERROR: Tidak ada capture yang berjalan (PID file not found)"
        fi
        ;;
    
    *)
        echo "Usage:"
        echo "  ./nids01-capture.sh start clean 10.3.2.100"
        echo "  ./nids01-capture.sh start evasion 10.3.2.100"
        echo "  ./nids01-capture.sh stop"
        ;;
esac
