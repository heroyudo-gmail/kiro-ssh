# Skenario 3: Deteksi Intrusi dengan AWS Managed Services

## Overview
- **Metode deteksi:** AWS WAF + GuardDuty + Security Hub
- **Infrastruktur:** 1 EC2 Amazon Linux 2023 (t3.large) + AWS services
- **VPC:** testing-multidetection (sama dengan Target-1 dan Target-2)
- **Tujuan:** Jalankan serangan yang sama → lihat mana yang terdeteksi oleh AWS managed services → bandingkan dengan ML (skenario 1) dan open-source (skenario 2)

---

## Install Attack Tools + Target Services

Gunakan script `install-attacker.sh` (sama untuk semua skenario):

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

**Catatan:** Password testuser di script = `S3cur3P@ss!` (TIDAK ada di wordlist, supaya brute-force gagal dan bisa terdeteksi sebagai serangan).

---

## AWS Services yang Dihubungkan (via Console/CLI)

### Deploy Infrastructure (CloudFormation)

Urutan deploy — **tunggu setiap step CREATE_COMPLETE sebelum lanjut:**

```cmd
set AWS_PAGER=

:: Step 1: VPC + 2 subnet (AZ-A + AZ-B) + IGW + SG
aws cloudformation create-stack --stack-name multidetect-network --template-body file://05-network-vpc.yaml --region ap-southeast-1 --no-cli-pager

:: Tunggu selesai (cek status):
aws cloudformation describe-stacks --stack-name multidetect-network --query "Stacks[0].StackStatus" --output text --region ap-southeast-1 --no-cli-pager

:: Step 2: EC2 Target-3 (AZ-A) + Target-4 (AZ-B) — bisa paralel
aws cloudformation create-stack --stack-name multidetect-target3 --template-body file://08-target3-instance.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1 --no-cli-pager
aws cloudformation create-stack --stack-name multidetect-target4 --template-body file://09-target4-instance-azb.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1 --no-cli-pager

:: Tunggu keduanya selesai

:: Step 3: ALB (butuh subnet dari 05 + instance ID dari 08 & 09)
aws cloudformation create-stack --stack-name multidetect-alb --template-body file://10-alb.yaml --region ap-southeast-1 --no-cli-pager
```

### Dependency Chain
```
05-network-vpc.yaml
  ├── exports: vpc-id, subnet-id, subnet-b-id, sg-id, rt-id
  │
  ├── 08-target3-instance.yaml (imports: subnet-id, sg-id)
  │     └── exports: target3-id
  │
  ├── 09-target4-instance-azb.yaml (imports: subnet-b-id, sg-id)
  │     └── exports: target4-id
  │
  └── 10-alb.yaml (imports: vpc-id, subnet-id, subnet-b-id, target3-id, target4-id)
        └── exports: alb-dns, alb-arn
```

### Setelah ALB aktif, setup AWS Services:

#### WAF (file 11-waf.yaml)
```cmd
:: Deploy WAF (setelah stack 10 ALB selesai)
aws cloudformation create-stack --stack-name multidetect-waf --template-body file://11-waf.yaml --region ap-southeast-1 --no-cli-pager

:: Delete setelah testing selesai (hemat biaya)
aws cloudformation delete-stack --stack-name multidetect-waf --region ap-southeast-1 --no-cli-pager
```

WAF Rules yang aktif:
| # | Rule | Fungsi | Serangan yang Dideteksi |
|---|------|--------|------------------------|
| 1 | Rate Limit 1000/5min | HTTP Flood protection | GoldenEye, Hulk |
| 2 | Core Rule Set (OWASP) | XSS, path traversal, command injection | SlowHTTPTest (partial) |
| 3 | Known Bad Inputs | Log4j, bad user agents | — |
| 4 | SQL Injection | SQLi patterns | — |
| 5 | IP Reputation | Known malicious IPs | — |

WAF Logs: CloudWatch → Log Groups → `aws-waf-logs-testing-multidetection`

**Catatan WAF limitation:** WAF hanya inspect HTTP traffic via ALB. Serangan SSH/FTP/SYN/UDP langsung ke EC2 IP **tidak melewati WAF**.

#### GuardDuty + VPC Flow Logs (file 12-guardduty-flowlogs.yaml)
```cmd
:: Deploy GuardDuty (setelah stack 05 selesai)
aws cloudformation create-stack --stack-name multidetect-guardduty --template-body file://12-guardduty-flowlogs.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1 --no-cli-pager

:: Delete setelah testing selesai
aws cloudformation delete-stack --stack-name multidetect-guardduty --region ap-southeast-1 --no-cli-pager
```

GuardDuty menganalisis VPC Flow Logs untuk detect anomaly di L3/L4. Findings muncul **15-30 menit** setelah serangan.

Cek findings:
```cmd
aws guardduty list-findings --detector-id DETECTOR_ID --region ap-southeast-1 --no-cli-pager
aws guardduty get-findings --detector-id DETECTOR_ID --finding-ids FINDING_ID --region ap-southeast-1 --no-cli-pager
```

Flow Logs: CloudWatch → Log Groups → `/aws/vpc/flowlogs/testing-multidetection`

---

## Prediksi Deteksi: WAF + GuardDuty Combined

| Serangan | Layer | AWS Service | Finding Type / Rule | Detect? |
|----------|-------|-------------|--------------------:|---------|
| SSH Brute-Force | L4 | GuardDuty | `UnauthorizedAccess:EC2/SSHBruteForce` | ✅ |
| FTP Brute-Force | L4 | GuardDuty | `UnauthorizedAccess:EC2/TrojanEC2` (generic) | ⚠️ Mungkin |
| Slowloris | L7 | WAF | — (low-rate, tidak trigger rate limit) | ❌ |
| GoldenEye | L7 | WAF | Rate Limit 1000/5min → Block | ✅ |
| SlowHTTPTest | L7 | WAF | Core Rule Set (partial) | ⚠️ Mungkin |
| Hulk (HTTP Flood) | L7 | WAF | Rate Limit 1000/5min → Block | ✅ |
| SYN Flood | L3/4 | GuardDuty | `Recon:EC2/PortProbeUnprotectedPort` | ✅ |
| UDP Flood | L3/4 | GuardDuty | Traffic anomaly (volume spike) | ✅ |

### Catatan Penting
- **GuardDuty butuh serangan dari IP LAIN** (bukan localhost) — loopback tidak tercatat di VPC Flow Logs
- Untuk test valid: jalankan serangan dari **Target-1 (10.2.1.x) ke Target-3 (10.2.1.y)** via private IP
- GuardDuty publish **setiap 15 menit** — bukan real-time
- WAF **langsung block** (real-time) tapi hanya HTTP via ALB
- Total prediksi: **5-6 dari 8 serangan** terdeteksi (WAF + GuardDuty combined)

| AWS Service | Fungsi | Serangan yang Dideteksi |
|-------------|--------|------------------------|
| **GuardDuty** | Anomaly detection dari VPC Flow Logs + DNS + CloudTrail | SSH BF, port scan, unusual traffic |
| **AWS WAF** (via ALB) | Rate limiting + managed rules | HTTP floods (GoldenEye, Hulk, SlowHTTPTest) |
| **Security Hub** | Aggregasi findings | Semua (dari GuardDuty + WAF) |
| **VPC Flow Logs** | Log semua network traffic | Audit trail (tidak detect langsung) |

### Setup via AWS Console:

1. **GuardDuty:** Console → GuardDuty → Enable (1 klik)
2. **VPC Flow Logs:** Console → VPC → Flow Logs → Create (target: CloudWatch Logs)
3. **AWS WAF:** 
   - Buat ALB di depan EC2 (port 80)
   - Buat Web ACL dengan rules: Rate limit 1000 req/5min + AWS managed rules
   - Associate Web ACL ke ALB
4. **Security Hub:** Console → Security Hub → Enable

### Setup via CLI:
```bash
# GuardDuty
aws guardduty create-detector --enable --region ap-southeast-1

# VPC Flow Logs (butuh VPC ID dan Log Group)
aws ec2 create-flow-logs --resource-type VPC --resource-ids VPC_ID --traffic-type ALL --log-destination-type cloud-watch-logs --log-group-name /aws/vpc/flowlogs/testing-multidetection --region ap-southeast-1
```

---

## Alur Eksperimen

```
┌──────────────────────────────────────────────────────────┐
│ 1. Enable GuardDuty + WAF + VPC Flow Logs                │
│                                                           │
│ 2. Jalankan 8 serangan (sama seperti skenario 1 & 2)    │
│                                                           │
│ 3. Tunggu 15-30 menit (GuardDuty publish interval)       │
│                                                           │
│ 4. Cek findings:                                         │
│    - GuardDuty Console → Findings                        │
│    - WAF Console → Sampled requests (blocked)            │
│    - Security Hub → Findings                             │
│                                                           │
│ 5. Hitung: berapa jenis serangan yang terdeteksi         │
└──────────────────────────────────────────────────────────┘
```

---

## Script Testing (serangan sama)

```bash
#!/bin/bash
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

echo "=== ATTACKS DONE ==="
echo "Tunggu 15-30 menit lalu cek:"
echo "  - GuardDuty: aws guardduty list-findings --detector-id DETECTOR_ID --region ap-southeast-1"
echo "  - WAF: aws wafv2 get-sampled-requests ..."
echo "  - Security Hub: aws securityhub get-findings --region ap-southeast-1"
```

---

## Cek Findings Setelah Testing

```bash
# GuardDuty findings
aws guardduty list-findings --detector-id DETECTOR_ID --region ap-southeast-1 --no-cli-pager
aws guardduty get-findings --detector-id DETECTOR_ID --finding-ids FINDING_ID --region ap-southeast-1 --no-cli-pager

# Security Hub findings
aws securityhub get-findings --filters '{"ProductName":[{"Value":"GuardDuty","Comparison":"EQUALS"}]}' --region ap-southeast-1 --no-cli-pager
```

---

## Output yang Diharapkan

| AWS Service | Serangan yang Dideteksi | Tidak Dideteksi | Latency |
|-------------|------------------------|-----------------|---------|
| GuardDuty | SSH BF (UnauthorizedAccess:EC2/SSHBruteForce) | Slowloris, SlowHTTP | 15-30 menit |
| AWS WAF | GoldenEye, Hulk, SlowHTTPTest (rate limit) | SSH, FTP, SYN, UDP | Instant (block) |
| VPC Flow Logs | SYN flood pattern (audit only) | Tidak detect, hanya log | — |

---

## Perbedaan Penting dari Skenario 1 & 2

| Aspek | Skenario 3 (AWS) |
|-------|-----------------|
| Biaya | WAF ~$5/bulan + GuardDuty ~$1/bulan + ALB ~$16/bulan |
| Latency detect | GuardDuty: 15-30 menit (!), WAF: instant |
| Bisa block? | WAF: Ya (HTTP). GuardDuty: Tidak (alert only) |
| Install di EC2? | Tidak perlu install apapun di EC2 (managed) |
| Coverage | HTTP (WAF) + SSH brute-force (GuardDuty). Tidak cover UDP/SYN langsung |

---

## Catatan
- GuardDuty butuh **VPC Flow Logs enabled** untuk detect network anomalies
- GuardDuty detect SSH brute-force hanya dari **EC2 public IP** (bukan localhost) — jadi test dari localhost mungkin TIDAK terdeteksi
- Untuk test yang valid, serangan harus datang dari **IP lain** (instance lain atau internet)
- AWS WAF hanya bisa dipasang di **ALB/CloudFront**, bukan langsung di EC2
