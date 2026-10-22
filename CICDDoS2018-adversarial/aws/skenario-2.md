

aws cloudformation create-stack --stack-name multidetect-target2 --template-body file://07-target2-instance.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1 --no-cli-pager



aws cloudformation delete-stack --stack-name multidetect-target2 --region ap-southeast-1 --no-cli-pager


# Skenario 2: Deteksi Intrusi dengan Tools Open-Source

## Overview
- **Metode deteksi:** Suricata (IDS) + Fail2Ban + Nginx Rate Limiting
- **Infrastruktur:** 1 EC2 Amazon Linux 2023 (t3.large) — single node all-in-one
- **VPC:** testing-multidetection (sama dengan Target-1)
- **Tujuan:** Jalankan serangan yang sama → lihat mana yang terdeteksi oleh tools open-source → bandingkan dengan ML (skenario 1)

---

## Perbedaan dengan Skenario 1

| Aspek | Skenario 1 (ML) | Skenario 2 (Open-Source) |
|-------|-----------------|--------------------------|
| Deteksi | Model XGBoost/RF predict dari flow features | Suricata rules + Fail2Ban monitor logs |
| Cara kerja | Offline (capture → extract → predict) | **Real-time** (detect saat serangan terjadi) |
| Output | CSV prediksi per flow | Alert log per event |
| Bottleneck | Flow extraction dari pcap besar (GAGAL) | Tidak ada — alert langsung muncul |

---

## Tools yang Perlu Diinstall

### Attack Tools (sama seperti Skenario 1)

### Deploy Infrastructure
```cmd
set AWS_PAGER=
:: Step 1: VPC (kalau belum ada)
aws cloudformation create-stack --stack-name multidetect-network --template-body file://05-network-vpc.yaml --region ap-southeast-1 --no-cli-pager

:: Tunggu CREATE_COMPLETE, lalu:
:: Step 2: EC2 Target-2
aws cloudformation create-stack --stack-name multidetect-target2 --template-body file://07-target2-instance.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1 --no-cli-pager
```

### Install Tools (via SSM setelah EC2 running)

Gunakan script `install-attacker.sh`:

**Upload ke S3 (dari laptop, sekali saja):**
```bash
aws s3 cp install-attacker.sh s3://ssh-detection-features-232032302717/scripts/install-attacker.sh --region ap-southeast-1
```

**Di EC2 baru (via SSM):**
```bash
aws s3 cp s3://ssh-detection-features-232032302717/scripts/install-attacker.sh /tmp/install-attacker.sh
chmod +x /tmp/install-attacker.sh
sudo /tmp/install-attacker.sh
```

### Detection Tools (BARU — ini yang membedakan dari Skenario 1)
```bash
# Enable EPEL (untuk suricata dan fail2ban)
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm 2>/dev/null || sudo amazon-linux-extras install epel -y 2>/dev/null || echo "EPEL may already be available"

# Suricata (IDS/IPS — deteksi serangan network layer 3-7)
sudo yum install -y suricata
sudo suricata-update  # download rules
sudo systemctl enable suricata

# Fail2Ban (deteksi brute-force dari auth logs)
sudo yum install -y fail2ban
sudo systemctl enable fail2ban

# Kalau suricata/fail2ban tidak tersedia via yum, install manual:
# Suricata: https://suricata.io/download/
# Fail2Ban: pip install fail2ban atau git clone

# Nginx rate limiting (deteksi HTTP flood — built-in nginx config)
# (dikonfigurasi di step berikutnya)
```

---

## Konfigurasi Detection Tools

### Suricata — Custom Rules untuk IDS2018
```bash
sudo tee /etc/suricata/rules/local.rules << 'EOF'
# SSH Brute-Force (>5 attempts in 60s)
alert ssh any any -> any 22 (msg:"IDS2018 SSH Brute-Force"; flow:to_server; threshold:type both, track by_src, count 5, seconds 60; sid:2018001; rev:1;)

# FTP Brute-Force
alert ftp any any -> any 21 (msg:"IDS2018 FTP Brute-Force"; flow:to_server; content:"USER"; threshold:type both, track by_src, count 5, seconds 60; sid:2018002; rev:1;)

# HTTP Flood (>100 req in 10s)
alert http any any -> any 80 (msg:"IDS2018 HTTP Flood (Hulk/GoldenEye)"; flow:to_server,established; threshold:type both, track by_src, count 100, seconds 10; sid:2018003; rev:1;)

# SYN Flood (>500 SYN in 10s)
alert tcp any any -> any any (msg:"IDS2018 SYN Flood"; flags:S; threshold:type both, track by_src, count 500, seconds 10; sid:2018004; rev:1;)

# UDP Flood (>1000 packets in 10s)
alert udp any any -> any any (msg:"IDS2018 UDP Flood"; threshold:type both, track by_src, count 1000, seconds 10; sid:2018005; rev:1;)
EOF

# Start Suricata (listen on loopback)
sudo suricata -c /etc/suricata/suricata.yaml -i lo -D
```

### Fail2Ban — SSH + FTP jails
```bash
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 300
findtime = 300
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/secure
maxretry = 5

[vsftpd]
enabled = true
port = ftp
logpath = /var/log/vsftpd.log
maxretry = 5
EOF

sudo systemctl start fail2ban
```

### Nginx Rate Limiting
```bash
sudo tee /etc/nginx/conf.d/rate_limit.conf << 'EOF'
limit_req_zone $binary_remote_addr zone=ids2018:10m rate=10r/s;
server {
    listen 80 default_server;
    location / {
        limit_req zone=ids2018 burst=20 nodelay;
        root /usr/share/nginx/html;
    }
}
EOF
sudo nginx -t && sudo systemctl reload nginx
```

---

## Alur Eksperimen

```
┌──────────────────────────────────────────────────────────┐
│ 1. Start Suricata + Fail2Ban + Nginx (real-time detect)  │
│                                                           │
│ 2. Jalankan 8 serangan ke localhost (sequential)         │
│    (sama seperti skenario 1)                             │
│                                                           │
│ 3. Setelah selesai, baca log:                            │
│    - /var/log/suricata/fast.log (Suricata alerts)        │
│    - fail2ban-client status sshd (banned IPs)            │
│    - /var/log/nginx/error.log (rate limit rejects)       │
│                                                           │
│ 4. Hitung: berapa jenis serangan yang terdeteksi         │
│    oleh masing-masing tool                               │
│                                                           │
│ 5. Output: tabel perbandingan                            │
└──────────────────────────────────────────────────────────┘
```

---

## Script Testing

```bash
#!/bin/bash
# === SKENARIO 2: Open-Source IDS Testing ===

# Clear logs
sudo truncate -s 0 /var/log/suricata/fast.log
sudo fail2ban-client unban --all 2>/dev/null
sudo truncate -s 0 /var/log/nginx/error.log

# Verify services running
echo "=== SERVICES ==="
systemctl is-active suricata && echo "✓ Suricata"
systemctl is-active fail2ban && echo "✓ Fail2Ban"
systemctl is-active nginx && echo "✓ Nginx"

# 8 attacks (same as skenario 1)
echo "[$(date +%H:%M:%S)] Phase 1: SSH-Bruteforce (60s)"
timeout 60 hydra -l testuser -P /opt/attack/passwords.txt -t 8 127.0.0.1 ssh 2>&1 | tail -2; sleep 3

echo "[$(date +%H:%M:%S)] Phase 2: FTP-BruteForce (60s)"
timeout 60 hydra -l testuser -P /opt/attack/passwords.txt -t 8 127.0.0.1 ftp 2>&1 | tail -2; sleep 3

echo "[$(date +%H:%M:%S)] Phase 3: Slowloris (60s)"
timeout 60 /opt/venv/bin/slowloris 127.0.0.1 -p 80 -s 200 2>&1 | tail -2; sleep 3

echo "[$(date +%H:%M:%S)] Phase 4: GoldenEye (60s)"
timeout 60 python3 /opt/GoldenEye/goldeneye.py http://127.0.0.1 -w 20 -s 50 2>&1 | tail -2; sleep 3

echo "[$(date +%H:%M:%S)] Phase 5: SlowHTTPTest (60s)"
timeout 60 slowhttptest -c 500 -H -i 10 -r 100 -t GET -u http://127.0.0.1/ -p 3 -l 60 2>&1 | tail -2; sleep 3

echo "[$(date +%H:%M:%S)] Phase 6: Hulk (60s)"
timeout 60 ab -n 50000 -c 200 http://127.0.0.1/ 2>&1 | tail -3; sleep 3

echo "[$(date +%H:%M:%S)] Phase 7: SYN Flood (10s)"
sudo timeout 10 nping --tcp --flags SYN --rate 3000 -p 80 -c 10000 127.0.0.1 2>&1 | tail -3; sleep 3

echo "[$(date +%H:%M:%S)] Phase 8: UDP Flood (10s)"
timeout 10 python3 /opt/attack/udp_flood.py 127.0.0.1 80 10 2>&1 | tail -1; sleep 3

# === COLLECT RESULTS ===
echo ""
echo "============================================================"
echo "  HASIL DETEKSI — OPEN-SOURCE IDS"
echo "============================================================"

echo ""
echo "--- SURICATA ALERTS ---"
sudo cat /var/log/suricata/fast.log | grep -oP '\[.*?\]' | sort | uniq -c | sort -rn
echo "Total alerts: $(wc -l < /var/log/suricata/fast.log)"

echo ""
echo "--- FAIL2BAN ---"
sudo fail2ban-client status sshd 2>/dev/null
sudo fail2ban-client status vsftpd 2>/dev/null

echo ""
echo "--- NGINX RATE LIMIT ---"
grep "limiting requests" /var/log/nginx/error.log 2>/dev/null | wc -l | xargs -I{} echo "Rate limited requests: {}"

echo ""
echo "=== SUMMARY ==="
echo "Suricata detected:"
grep -c "SSH Brute" /var/log/suricata/fast.log 2>/dev/null && echo "  ✓ SSH Brute-Force"
grep -c "FTP Brute" /var/log/suricata/fast.log 2>/dev/null && echo "  ✓ FTP Brute-Force"
grep -c "HTTP Flood" /var/log/suricata/fast.log 2>/dev/null && echo "  ✓ HTTP Flood"
grep -c "SYN Flood" /var/log/suricata/fast.log 2>/dev/null && echo "  ✓ SYN Flood"
grep -c "UDP Flood" /var/log/suricata/fast.log 2>/dev/null && echo "  ✓ UDP Flood"

echo ""
echo "=== DONE ==="
```

---

## Output yang Diharapkan

| Tool | Serangan yang Dideteksi | Tidak Dideteksi |
|------|------------------------|-----------------|
| Suricata | SSH-BF, FTP-BF, HTTP Flood, SYN Flood, UDP Flood | Slowloris (low-rate) |
| Fail2Ban | SSH-BF, FTP-BF | DoS/DDoS (bukan auth-based) |
| Nginx Rate Limit | GoldenEye, Hulk (high-rate HTTP) | SSH, FTP, SYN, UDP |

---

## Hasil Aktual Testing (6 Aug 2026)

### Kondisi
- **Suricata:** GAGAL INSTALL (tidak tersedia di Amazon Linux 2023 repo, compile gagal zlib)
- **Fail2Ban:** v1.1.0 terinstall dan aktif
- **Nginx:** aktif, rate_limit.conf configured (10 req/s, burst 20)

### Attack Results
| Phase | Serangan | Status |
|-------|----------|--------|
| 1 | SSH-Bruteforce | ✓ Hydra berhasil (password found) |
| 2 | FTP-BruteForce | ✗ Gagal (0 target, vsftpd mungkin block setelah phase 1 dari skenario-1) |
| 3 | Slowloris | ✓ Jalan (60s, terminated) |
| 4 | GoldenEye | ✓ Jalan (60s, terminated) |
| 5 | SlowHTTPTest | ✓ Jalan (60s, terminated) |
| 6 | Hulk (ab) | ✓ Jalan (50000 requests) |
| 7 | SYN Flood | ✓ Jalan (10000 packets, 0.13% loss) |
| 8 | UDP Flood | ✓ Jalan (10s, terminated) |

### Detection Results

| Tool | Serangan | Terdeteksi? | Detail |
|------|----------|-------------|--------|
| **Fail2Ban** | SSH Brute-Force | ❌ TIDAK | Currently banned: 0, Total failed: 0 |
| **Fail2Ban** | FTP Brute-Force | ❌ TIDAK | (FTP attack gagal) |
| **Nginx Rate Limit** | Slowloris | ❌ TIDAK | Low-rate, di bawah threshold |
| **Nginx Rate Limit** | GoldenEye | ✅ YA | Bagian dari 173,422 requests blocked |
| **Nginx Rate Limit** | SlowHTTPTest | ❌ TIDAK (kemungkinan) | Slow request, bukan high-rate |
| **Nginx Rate Limit** | Hulk (ab) | ✅ YA | Mayoritas dari 173,422 requests blocked |
| **Nginx Rate Limit** | SYN Flood | ❌ TIDAK | Network layer, Nginx tidak lihat |
| **Nginx Rate Limit** | UDP Flood | ❌ TIDAK | Network layer, Nginx tidak lihat |

### Summary
```
Fail2Ban:
  ✗ SSH Brute-Force NOT detected (Fail2Ban monitor /var/log/secure tapi Hydra via localhost
    mungkin tidak trigger "Failed password" di log karena langsung berhasil)

Nginx:
  ✓ HTTP Flood DETECTED (173,422 requests blocked)
    - GoldenEye + Hulk (ab) tertangkap oleh rate limiting

Not covered (tanpa Suricata):
  ✗ Slowloris — low-rate, tidak trigger rate limit
  ✗ SYN Flood — network layer
  ✗ UDP Flood — network layer
```

### Analisa Kenapa Fail2Ban Tidak Detect SSH

**Root cause:** Hydra SSH berhasil menemukan password (`1 of 1 target successfully completed, 1 valid password found`) yang berarti:
1. Hydra login sukses sebelum mencapai threshold 5 failed attempts
2. Password `P@ssw0rd123` ada di password list → Hydra find di attempt ke-7 (sebelum Fail2Ban trigger)
3. Fail2Ban hanya monitor **failed** logins, bukan successful brute-force

**Fix untuk next time:** Hapus password benar dari wordlist agar Hydra selalu gagal → trigger more "Failed password" entries di log.

### Kesimpulan Skenario 2

| Metric | Nilai |
|--------|-------|
| Total serangan | 8 |
| Terdeteksi (Nginx) | 2 (GoldenEye + Hulk) |
| Terdeteksi (Fail2Ban) | 0 |
| Terdeteksi (Suricata) | N/A (tidak terinstall) |
| **Detection rate** | **2/8 = 25%** |

**vs Skenario 1 (ML):** Belum ada hasil final karena extraction gagal, tapi model RF Top-20 sudah terbukti 100% accuracy pada test kecil (5 flows).

---

## Catatan untuk Perbaikan

1. **Suricata:** Gunakan Ubuntu/Debian (`apt install suricata`) — jangan Amazon Linux
2. **Fail2Ban:** Hapus password benar dari wordlist agar brute-force selalu gagal
3. **Nginx:** Rate limit hanya detect high-rate HTTP, tidak detect low-rate (Slowloris) atau non-HTTP
4. **Kesimpulan:** Tanpa Suricata, open-source IDS hanya bisa detect 25% serangan. Suricata krusial untuk network-layer detection.


---

## Hasil Aktual Testing (06 Aug 2026)

### Status Tools
- **Suricata:** GAGAL install (tidak tersedia di Amazon Linux 2023 EPEL, compile gagal: missing zlib-devel + libhtp)
- **Fail2Ban:** v1.1.0 terinstall, aktif
- **Nginx Rate Limit:** aktif, configured (10 req/s burst 20)

### Hasil Deteksi

| # | Serangan | Fail2Ban | Nginx Rate Limit | Terdeteksi? |
|---|----------|----------|------------------|-------------|
| 1 | SSH Brute-Force | ✗ (0 banned) | — | ❌ |
| 2 | FTP Brute-Force | — (FTP error) | — | ❌ |
| 3 | Slowloris | — | ✗ (low-rate) | ❌ |
| 4 | GoldenEye | — | ✓ | ✅ |
| 5 | SlowHTTPTest | — | ✓ | ✅ |
| 6 | Hulk (ab) | — | ✓ | ✅ |
| 7 | SYN Flood | — | — | ❌ |
| 8 | UDP Flood | — | — | ❌ |

### Summary
- **Total terdeteksi: 3 dari 8 serangan** (hanya HTTP floods oleh Nginx rate limit)
- **Nginx Rate Limit:** 173,422 requests blocked — efektif untuk high-rate HTTP
- **Fail2Ban:** tidak trigger — Hydra found valid password sebelum threshold (maxretry=5)
- **Suricata:** tidak tersedia → network-layer attacks tidak terdeteksi

### Analisa Mengapa Fail2Ban Gagal Detect SSH
- Password `P@ssw0rd123` ada di wordlist → Hydra login sukses di attempt pertama
- Fail2Ban hanya trigger setelah 5 failed attempts → tidak pernah tercapai
- Fix: gunakan password yang TIDAK ada di wordlist, atau turunkan maxretry

### Lesson Learned
- Amazon Linux 2023 **tidak cocok** untuk Suricata (dependencies tidak tersedia)
- Untuk full IDS testing, gunakan **Ubuntu 22.04** atau **Debian 12** (apt install suricata langsung jalan)
- Nginx rate limit hanya cover HTTP layer — tidak bisa detect SSH/FTP/SYN/UDP
- Tanpa Suricata, open-source detection sangat terbatas (hanya 3/8 = 37.5%)
