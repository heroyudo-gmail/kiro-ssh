# Skenario 1: Deteksi Intrusi dengan Machine Learning

## Overview
- **Metode deteksi:** XGBoost + Random Forest (trained offline pada dataset CIC-IDS2018)
- **Infrastruktur:** 1 EC2 Amazon Linux 2023 (t3.large) — single node all-in-one
- **Tujuan:** Capture traffic serangan → extract flow features → predict dengan ML model → evaluasi accuracy

---

## Infrastruktur

| Komponen | Detail |
|----------|--------|
| OS | Amazon Linux 2023 |
| Instance | t3.large (2 vCPU, 8 GB RAM) |
| VPC | testing-multidetection (10.2.0.0/16) |
| Subnet | Public (10.2.1.0/24) + IGW |
| Akses | SSM Session Manager |
| CloudFormation | 05-single-node-debian.yaml (VPC) + 06-debian-instance.yaml (EC2) |

---

## Tools yang Diinstall

### Attack Tools
| Tool | Install Command | Fungsi |
|------|----------------|--------|
| Hydra | compile from source (v9.5) | SSH/FTP brute-force |
| nping | `yum install nmap` | SYN flood |
| Slowloris | `/opt/venv/bin/pip install slowloris` | HTTP slow connection |
| GoldenEye | `git clone` | HTTP flood |
| SlowHTTPTest | compile from source (v1.9.0) | Slow HTTP POST/GET |
| ApacheBench | `yum install httpd-tools` | HTTP flood (Hulk) |
| udp_flood.py | custom script | UDP volumetric |
| passwords.txt | manual create | Password list untuk brute-force |

### Target Services
| Service | Port | Install |
|---------|------|---------|
| SSH (sshd) | 22 | built-in (enable password auth + MaxAuthTries 100) |
| Nginx | 80 | `yum install nginx` |
| vsftpd | 21 | `yum install vsftpd` |
| testuser | — | `useradd + chpasswd` (password: P@ssw0rd123) |

### Analyzer Tools
| Tool | Install | Fungsi |
|------|---------|--------|
| tcpdump | `yum install tcpdump` | Packet capture |
| extract_flows.py | custom script (scapy) | Extract flow features dari pcap |
| inference.py | custom script | Load model → predict → compare vs ground truth |
| xgboost + sklearn | `/opt/venv/bin/pip install` | ML inference |
| 3 model files (.pkl/.json) | download dari S3 | Trained models (RF Top-20, XGBoost All-68, RF All-68) |
| schedule.json | download dari S3 | Ground truth (kapan serangan apa terjadi) |

### Virtual Environment
```
/opt/venv/bin/python3   — Python dengan semua ML packages
/opt/venv/bin/pip       — pip terpisah dari system
/opt/venv/bin/slowloris — slowloris command
```

---

## Alur Eksperimen

```
┌─────────────────────────────────────────────────────────┐
│ 1. Start tcpdump (capture loopback)                     │
│                                                          │
│ 2. Jalankan 8 serangan ke localhost (sequential)        │
│    - SSH brute-force (60s)                              │
│    - FTP brute-force (60s)                              │
│    - Slowloris (60s)                                    │
│    - GoldenEye (60s)                                    │
│    - SlowHTTPTest (60s)                                 │
│    - HTTP Flood/Hulk (60s)                              │
│    - SYN Flood via nping (60s)                          │
│    - UDP Flood (60s)                                    │
│                                                          │
│ 3. Stop tcpdump → capture.pcap                          │
│                                                          │
│ 4. extract_flows.py → output.csv (flow features)        │
│                                                          │
│ 5. inference.py → predict setiap flow dengan 3 model    │
│    - Compare predicted vs ground truth (schedule.json)  │
│    - Hitung Accuracy, F1, Precision, Recall             │
│                                                          │
│ 6. Output: target1_ml_results.csv + performance.csv     │
└─────────────────────────────────────────────────────────┘
```


#create instance
aws cloudformation create-stack --stack-name multidetect-target2 --template-body file://07-target2-instance.yaml --region ap-southeast-1 --no-cli-pager

#


## Perintah Install (dari nol)

### Deploy Infrastructure
```cmd
set AWS_PAGER=
:: Step 1: VPC (kalau belum ada)
aws cloudformation create-stack --stack-name multidetect-network --template-body file://05-network-vpc.yaml --region ap-southeast-1 --no-cli-pager

:: Tunggu CREATE_COMPLETE, lalu:
:: Step 2: EC2 Target-1
aws cloudformation create-stack --stack-name multidetect-target1 --template-body file://06-target1-instance.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1 --no-cli-pager
```

### Install Tools (via SSM setelah EC2 running)

Gunakan script `install-attacker.sh` (sudah tersedia di S3):

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

Script ini menginstall: Hydra, SlowHTTPTest, GoldenEye, Slowloris, nmap, ab, tcpdump, udp_flood.py, Nginx, vsftpd, testuser. Lihat file `install-attacker.sh` untuk detail.

---

## Script Testing (Full 8 Attacks)

```bash
#!/bin/bash
# Clear previous
rm -f /opt/ids2018/capture.pcap /opt/ids2018/flows/*.csv /opt/ids2018/results/*.csv

# Start capture
sudo tcpdump -i lo -w /opt/ids2018/capture.pcap &
TCPDUMP_PID=$!; sleep 2

# 8 attacks (60s each)
echo "[$(date +%H:%M:%S)] Phase 1: SSH-Bruteforce"
timeout 60 hydra -l testuser -P /opt/attack/passwords.txt -t 8 127.0.0.1 ssh 2>&1 | tail -2; sleep 5

echo "[$(date +%H:%M:%S)] Phase 2: FTP-BruteForce"
timeout 60 hydra -l testuser -P /opt/attack/passwords.txt -t 8 127.0.0.1 ftp 2>&1 | tail -2; sleep 5

echo "[$(date +%H:%M:%S)] Phase 3: Slowloris"
timeout 60 /opt/venv/bin/slowloris 127.0.0.1 -p 80 -s 200 2>&1 | tail -2; sleep 5

echo "[$(date +%H:%M:%S)] Phase 4: GoldenEye"
timeout 60 python3 /opt/GoldenEye/goldeneye.py http://127.0.0.1 -w 20 -s 50 2>&1 | tail -2; sleep 5

echo "[$(date +%H:%M:%S)] Phase 5: SlowHTTPTest"
timeout 60 slowhttptest -c 500 -H -i 10 -r 100 -t GET -u http://127.0.0.1/ -p 3 -l 60 2>&1 | tail -2; sleep 5

echo "[$(date +%H:%M:%S)] Phase 6: Hulk (ab)"
timeout 60 ab -n 50000 -c 200 http://127.0.0.1/ 2>&1 | tail -3; sleep 5

echo "[$(date +%H:%M:%S)] Phase 7: SYN Flood"
sudo timeout 60 nping --tcp --flags SYN --rate 3000 -p 80 -c 50000 127.0.0.1 2>&1 | tail -3; sleep 5

echo "[$(date +%H:%M:%S)] Phase 8: UDP Flood"
timeout 60 python3 /opt/attack/udp_flood.py 127.0.0.1 80 60 2>&1 | tail -1; sleep 5

# Stop capture
sudo kill $TCPDUMP_PID 2>/dev/null; sleep 3
echo "Pcap size:"; ls -lh /opt/ids2018/capture.pcap

# Extract + Inference
/opt/venv/bin/python3 /opt/ids2018/extract_flows.py /opt/ids2018/capture.pcap /opt/ids2018/flows/output.csv
/opt/venv/bin/python3 /opt/ids2018/inference.py --flows-dir /opt/ids2018/flows/ --models-dir /opt/ids2018/models/ --schedule /opt/ids2018/schedule/schedule.json --output-dir /opt/ids2018/results/ 2>&1 | tail -15

echo "=== DONE ==="
```

---

## Output yang Dihasilkan

| File | Lokasi | Isi |
|------|--------|-----|
| capture.pcap | /opt/ids2018/ | Raw packet capture (semua traffic) |
| output.csv | /opt/ids2018/flows/ | Flow features per connection |
| target1_ml_results.csv | /opt/ids2018/results/ | Per-flow: predicted vs actual |
| target1_ml_performance.csv | /opt/ids2018/results/ | Summary: Acc, F1, Precision per model |

---

## Masalah yang Ditemukan & Solusi

| Masalah | Solusi |
|---------|--------|
| cicflowmeter Python package tidak output CSV | Buat custom `extract_flows.py` pakai scapy |
| cicflowmeter butuh `requests` module | `/opt/venv/bin/pip install requests` |
| extract_flows.py (scapy) sangat lambat pada pcap besar | **Ganti ke tshark** (lihat section di bawah) |
| pip install global merusak system packages | Selalu pakai `/opt/venv/bin/pip` (virtual environment) |
| SSM session timeout saat script jalan | Pakai `nohup` atau `screen` |
| XGBoost model Acc=0% | extract_flows.py hanya generate 34 fitur, XGBoost butuh 68. RF Top-20 tetap akurat |

---

## Fix: Ganti extract_flows.py dengan tshark

### Masalah
`extract_flows.py` pakai `scapy rdpcap()` → load seluruh pcap ke RAM → jutaan packet dari SYN/UDP flood = **sangat lambat** (40+ menit untuk pcap 10 menit serangan, tidak selesai-selesai).

### Percobaan ke-2: tshark berhasil extract raw packets tapi scapy tetap stuck

**Fakta:**
- Pcap ukuran: **1.9 GB** (dari 10 menit serangan, SYN/UDP flood = 10 detik saja)
- tshark berhasil extract `raw_packets.csv` = **3,658,470 baris** (cepat, hitungan detik)
- Tapi setelah itu, script `extract_flows.py` (scapy) dipanggil → **stuck lagi** karena tetap pakai `rdpcap()`

### Root Cause yang Sesungguhnya
1. **SYN flood rate 3000/s × 10 detik = 30,000 SYN packets** 
2. **UDP flood** mengirim packet terus-menerus selama 10 detik = ratusan ribu packet
3. **Total 3.6 juta packet** dalam pcap 1.9 GB
4. `scapy rdpcap()` load SEMUA ke RAM → t3.large hanya 8 GB RAM → swap → sangat lambat
5. Bahkan tshark raw extract (3.6 juta baris CSV) sulit diproses oleh Python pandas

### Solusi yang Diperlukan (BELUM diimplementasi)
- **Opsi A:** Buat `extract_flows_tshark.py` yang baca `raw_packets.csv` (output tshark) → groupby flow → hitung fitur. TANPA scapy.
- **Opsi B:** Pakai `tshark -z conv,tcp` dan `tshark -z conv,udp` yang langsung output flow-level summary (bukan per-packet). Jauh lebih ringkas.
- **Opsi C:** Filter pcap sebelum extract — hanya ambil 1000 packet per phase (sampling), buang sisanya.

### Lesson Learned
| Masalah | Penyebab | Solusi |
|---------|----------|--------|
| Disk penuh (8 GB) | pcap 3.6 GB dari SYN/UDP flood | Tambah disk ke 20 GB ✓ |
| extract_flows.py (scapy) stuck | 3.6 juta packet di-load ke RAM sekaligus | JANGAN pakai scapy untuk pcap besar |
| pcap terlalu besar | SYN rate 3000/s + UDP flood = jutaan packet per menit | Kurangi rate atau durasi |
| tshark extract cepat tapi raw | 3.6 juta baris per-packet, bukan per-flow | Perlu aggregasi ke flow-level |

### Status Saat Ini
- ✅ Attack berhasil (semua 8 phase jalan)
- ✅ tcpdump capture berhasil (1.9 GB pcap)
- ✅ tshark extract raw_packets.csv berhasil (3.6 juta baris)
- ❌ Konversi raw packets → flow features GAGAL (scapy tidak mampu)
- ❌ extract_flows_tshark.py (pandas) JUGA GAGAL — 3.6 juta baris terlalu besar untuk groupby di t3.large (8 GB RAM)
- ❌ Inference belum bisa jalan (tidak ada flow CSV)

### Kesimpulan Skenario 1
**Bottleneck utama:** flow extraction dari pcap besar. Semua pendekatan gagal:
1. `cicflowmeter` Python → buggy, output kosong
2. `extract_flows.py` (scapy) → load semua ke RAM, stuck
3. `extract_flows_tshark.py` (pandas) → 3.6 juta baris groupby, stuck

**Masalah fundamental:** SYN/UDP flood menghasilkan jutaan packet → pcap terlalu besar → semua extractor kewalahan.

**Solusi yang belum dicoba:**
1. **Sampling saat capture**: `tcpdump -c 100000` (limit 100k packet) atau `-i lo port 22 or port 80 or port 21` (filter hanya port target, buang UDP flood raw)
2. **Chunked processing**: baca raw_packets.csv per-chunk (100k baris), proses, append
3. **Instance lebih besar**: t3.2xlarge (32 GB RAM) mungkin bisa handle
4. **Pisahkan SYN/UDP test**: capture terpisah, bukan bersamaan dengan attack lain

### Skenario 1: DITUNDA — lanjut ke Skenario 2 (Open-Source IDS)

---

## Ground Truth (schedule.json)

Deteksi berdasarkan waktu: setiap flow timestamp dicocokkan ke phase schedule.
Contoh: flow di detik 60-120 → ground truth = SSH-Bruteforce.

---

## Catatan untuk Target-2

Target-2 menggunakan tools open-source (Suricata, Fail2Ban, dll) sebagai pengganti ML model.
Alur sama: attack → capture → **deteksi oleh IDS tools** → bandingkan dengan ground truth.
Perbedaan hanya di step "deteksi" — bukan ML predict, tapi baca alert log dari Suricata/Fail2Ban.
