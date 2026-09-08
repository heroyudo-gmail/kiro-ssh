#!/bin/bash
# ============================================================
# T10 UNSW-NB15 — Pembangkit trafik BENIGN untuk Fase 1 (FAR).
# Dijalankan di TARGET (atau host mana pun yang trafiknya tertangkap capture).
# Tujuan: menghasilkan BANYAK flow benign yang BERAGAM selama observasi FAR,
# sehingga FAR dihitung dari ribuan flow (kredibel), bukan puluhan.
#
# TIDAK ADA serangan di sini. Semua aktivitas adalah trafik normal:
#   - HTTP GET berkala (loopback Nginx lokal + situs publik via NAT)
#   - DNS lookup
#   - unduhan berkas kecil berkala
#   - sesi SSH sah singkat (opsional, bila kunci/kredensial tersedia)
#
# Jalankan di background sepanjang tahap FAR (D1/D2/D3/...):
#   nohup sudo ./benign_traffic.sh > /opt/unsw/benign.log 2>&1 &
# Hentikan saat capture tahap selesai:
#   sudo pkill -f benign_traffic.sh
# ============================================================
set -u

# Target HTTP lokal (Nginx di Target). Loopback = trafik pasti tertangkap di iface lokal
# hanya jika capture di iface loopback; untuk trafik yang lewat ens5, pakai IP privat Target.
TARGET_IP="${TARGET_IP:-127.0.0.1}"          # override: TARGET_IP=10.5.x.x
# Situs publik untuk variasi flow keluar (via NAT). Aman & ringan.
PUB_HOSTS=("example.com" "www.google.com" "cloudfront.net" "amazon.com" "wikipedia.org")
# Endpoint unduhan kecil (beberapa ratus KB) untuk variasi ukuran flow.
DL_URLS=(
  "http://$TARGET_IP/"
  "https://www.google.com/robots.txt"
  "https://example.com/"
)

log(){ echo "[$(date +%T)] $*"; }
log "benign_traffic START (TARGET_IP=$TARGET_IP). Ctrl-C / pkill utk stop."

# Loop tak-berujung; berhenti saat proses di-kill (pkill / akhir tahap).
while true; do
  # 1) HTTP GET ke layanan lokal Target (banyak flow pendek)
  for i in $(seq 1 5); do
    curl -s -m 5 "http://$TARGET_IP/" >/dev/null 2>&1 || true
    sleep 0.5
  done

  # 2) DNS lookup acak (flow UDP 53) + HTTP ke situs publik (flow keluar via NAT)
  h=${PUB_HOSTS[$((RANDOM % ${#PUB_HOSTS[@]}))]}
  getent hosts "$h" >/dev/null 2>&1 || nslookup "$h" >/dev/null 2>&1 || true
  curl -s -m 8 "https://$h/" >/dev/null 2>&1 || true

  # 3) Unduhan berkas kecil berkala (variasi ukuran flow)
  u=${DL_URLS[$((RANDOM % ${#DL_URLS[@]}))]}
  curl -s -m 10 -o /dev/null "$u" 2>&1 || true

  # 4) Sesi SSH sah singkat (opsional; hanya jika sshpass + kredensial valid tersedia)
  #    Dinonaktifkan default agar tak menimbulkan pola "gagal login" (mirip brute-force).
  #    Aktifkan dgn: BENIGN_SSH=1 SSH_USER=... SSH_PASS=... TARGET_IP=...
  if [ "${BENIGN_SSH:-0}" = "1" ] && command -v sshpass >/dev/null; then
    sshpass -p "${SSH_PASS:-}" ssh -o StrictHostKeyChecking=no \
      -o ConnectTimeout=5 "${SSH_USER:-ec2-user}@$TARGET_IP" "uptime" >/dev/null 2>&1 || true
  fi

  # Jeda acak 2-6 detik agar pola trafik tidak terlalu periodik (lebih realistis).
  sleep $((2 + RANDOM % 5))
done
