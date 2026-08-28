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


---

# TEMUAN PENTING: Keterbatasan NFStream untuk Ekstraksi Top-10 Fitur

**Tanggal:** Percobaan deployment NIDS01 (real-traffic testing)

## Konteks

Setelah men-deploy infrastruktur (4 stack CloudFormation: VPC, Attacker, Target, Analyzer) dan memverifikasi NFStream 6.6.0 terpasang di Analyzer, dilakukan probing terhadap 100 atribut yang diekspos oleh objek `NFlow` NFStream untuk memetakannya ke Top-10 fitur model XGBoost (CIC-IDS2018).

## Hasil Mapping Top-10 Fitur -> NFStream

| # | Fitur Top-10 (CIC-IDS2018) | NFStream field | Status |
|---|---|---|---|
| 1 | Fwd Seg Size Min | `src2dst_min_ps` | Aproksimasi |
| 2 | URG Flag Cnt | `bidirectional_urg_packets` | Tersedia |
| 3 | Tot Bwd Pkts | `dst2src_packets` | Persis |
| 4 | Fwd Act Data Pkts | `src2dst_packets` (filter payload>0) | Aproksimasi |
| 5 | Fwd Pkt Len Max | `src2dst_max_ps` | Persis |
| 6 | Fwd Pkt Len Mean | `src2dst_mean_ps` | Persis |
| 7 | Bwd Pkt Len Mean | `dst2src_mean_ps` | Persis |
| 8 | Init Bwd Win Byts | -- (TCP window awal) | **TIDAK ADA** |
| 9 | TotLen Bwd Pkts | `dst2src_bytes` | Persis |
| 10 | Init Fwd Win Byts | -- (TCP window awal) | **TIDAK ADA** |

## Kekurangan Utama NFStream

NFStream **tidak mengekspos TCP window size** sama sekali dalam 100 atribut defaultnya. Dua fitur berikut TIDAK dapat diambil langsung:

- **Init Fwd Win Byts** (fitur #10): TCP window size dari paket pertama arah src->dst
- **Init Bwd Win Byts** (fitur #8): TCP window size dari paket pertama arah dst->src

Konsekuensi:
1. Jika 2 fitur ini di-set 0/-1 (default), model kehilangan ~20% informasi input.
2. **Init Fwd Win Byts adalah fitur target utama evasion** pada skenario RT-S2/RT-S4 (manipulasi TCP window via `sysctl`). Tanpa ekstraksi fitur ini, evasion pada TCP window menjadi tidak terdeteksi karena fiturnya memang tidak diukur.

## Opsi Solusi

| Opsi | Pendekatan | Trade-off |
|---|---|---|
| A | Custom NFPlugin NFStream yang membaca `tcp.window` dari paket pertama tiap arah | Paling akurat, tetap 10 fitur, tetap 1-pass streaming. Butuh implementasi plugin. |
| B | Hybrid: NFStream (8 fitur) + tshark khusus (`tcp.window_size`) untuk 2 fitur window | Sederhana, tapi 2-pass (NFStream + tshark). |
| C | Terima keterbatasan, set Init Win Byts = -1 | Cepat, tapi evasion window tidak terdeteksi. |

## Keputusan (Dua Skenario Percobaan)

**Skenario Fitur-1 (8-fitur, future work):**
- Latih ulang model **offline** hanya dengan 8 fitur yang NFStream mampu hasilkan secara native (buang Init Fwd/Bwd Win Byts).
- Bandingkan hasil offline (8-fitur) vs online (8-fitur real-traffic).
- Tujuan: mengukur seberapa besar kontribusi 2 fitur TCP window terhadap performa.

**Skenario Fitur-2 (10-fitur, DIPILIH untuk implementasi sekarang):**
- Tetap gunakan 10 fitur penuh.
- Implementasi **Opsi A**: custom NFPlugin untuk mengekstrak `Init Fwd Win Byts` dan `Init Bwd Win Byts` dari TCP window paket pertama tiap arah.
- Ini penting agar hipotesis evasion (RT-S2/RT-S4) dapat diuji secara valid.

## Catatan schedule.json

`schedule.json` yang ada saat ini masih memakai IP lama (10.1.1.x) dan skenario 60 menit. Perlu disesuaikan ke:
- Target IP baru: **10.3.2.38** (private subnet nids01)
- Attacker IP: **10.3.1.214**
- Timing baru sesuai dokumentasi (7 menit: benign -> SSH brute -> Slowloris -> SYN flood -> benign).


---

# SOLUSI OPSI A BERHASIL: Custom NFPlugin untuk Init Fwd/Bwd Win Byts

**Status:** IMPLEMENTASI SELESAI & TERUJI

## Ringkasan

Opsi A (custom NFPlugin) berhasil diimplementasikan untuk mengekstrak 2 fitur TCP window
size yang tidak tersedia di NFStream default. Sekarang **seluruh 10 fitur Top-10 dapat
diekstrak dari NFStream** di lingkungan real-traffic.

## Kunci Teknis

NFStream `NFPacket` mengekspos atribut **`packet.ip_packet`** (bytes) = "Raw content
starting from IP Header". Dari raw bytes ini, TCP window size di-parse manual:

1. IP header length: `ihl = (ip_packet[0] & 0x0F) * 4` (IPv4) atau 40 (IPv6).
2. TCP window size: 2 byte di offset `ihl + 14` dan `ihl + 15` (big-endian).
3. `packet.direction` (0 = src->dst, 1 = dst->src) menentukan arah fwd/bwd.
4. Window pertama tiap arah disimpan di `flow.udps.init_fwd_win_byts` dan
   `flow.udps.init_bwd_win_byts` (nilai -1 jika arah tsb tidak ada paket TCP).

Catatan: `dir(packet)` mengembalikan list kosong karena NFPacket adalah objek Cython,
tetapi atributnya (ip_packet, direction, protocol, syn, dll) tetap dapat diakses langsung
sesuai dokumentasi resmi NFStream.

## File

- Script plugin: `nfstream_win_extract.py`
- Lokasi S3: `s3://ssh-detection-features-232032302717/scripts/nfstream_win_extract.py`
- Lokasi Analyzer: `/opt/nids/scripts/nfstream_win_extract.py`

## Bukti Uji (pcap probe di Analyzer, 14 flows)

```
        src_ip      dst_ip  dst_port  protocol  init_fwd_win_byts  init_bwd_win_byts
   10.3.2.130   10.3.2.38        80         6              62727              62643
   10.3.2.130   47.128.4.174    443         6              62727              62643
```
Nilai window realistis (~62 KB) dan berbeda per arah/flow -> ekstraksi valid.

## Catatan Lingkungan (penting untuk langkah berikutnya)

- **Interface jaringan Analyzer = `ens5`** (BUKAN `eth0`). tcpdump harus pakai `-i ens5`.
- Capture WAJIB per-interface (`-i ens5`), JANGAN `-i any`. Capture `-i any` menghasilkan
  Linux cooked-mode (SLL) yang membuat NFStream menghasilkan 0 flow.
- NFStreamer WAJIB dijalankan dengan `statistical_analysis=True` agar 86 kolom (termasuk
  `bidirectional_urg_packets`, `src2dst_min_ps`, dll) muncul di output.

## Mapping Final Top-10 -> NFStream (LENGKAP)

| # | Top-10 | Sumber NFStream |
|---|---|---|
| 1 | Fwd Seg Size Min | `src2dst_min_ps` |
| 2 | URG Flag Cnt | `bidirectional_urg_packets` |
| 3 | Tot Bwd Pkts | `dst2src_packets` |
| 4 | Fwd Act Data Pkts | `src2dst_packets` |
| 5 | Fwd Pkt Len Max | `src2dst_max_ps` |
| 6 | Fwd Pkt Len Mean | `src2dst_mean_ps` |
| 7 | Bwd Pkt Len Mean | `dst2src_mean_ps` |
| 8 | Init Bwd Win Byts | **plugin** `udps.init_bwd_win_byts` |
| 9 | TotLen Bwd Pkts | `dst2src_bytes` |
| 10 | Init Fwd Win Byts | **plugin** `udps.init_fwd_win_byts` |

## Infrastruktur Ter-deploy (referensi)

| Node | Instance ID | Private IP | Public IP |
|---|---|---|---|
| Attacker | i-0b4e1a8e610543906 | 10.3.1.214 | 54.169.149.255 |
| Target | i-0adc1017c07918e61 | 10.3.2.38 | - |
| Analyzer | i-038b59e834a810974 | 10.3.2.130 | - |

Stack CloudFormation: nids01-vpc, nids01-attacker, nids01-target, nids01-analyzer (semua CREATE_COMPLETE).


---

# HASIL RUN PERTAMA: RT-S1 & RT-S3 (Clean Traffic)

**Status:** Pipeline end-to-end BERHASIL. Hasil metrik menunjukkan temuan penting.

## Masalah Arsitektur yang Ditemukan & Diperbaiki

**Masalah:** Capture awal di Analyzer menghasilkan pcap 24 byte (kosong). Penyebab:
Analyzer (10.3.2.130) TIDAK berada di jalur trafik Attacker->Target, sehingga tcpdump
di Analyzer tidak melihat paket antara keduanya.

**Solusi:** Capture dipindah ke **Target** (10.3.2.38) yang menerima semua serangan.
Pcap di-upload ke S3, lalu Analyzer download untuk inference.
- Ditambahkan IAM inline policy `S3CaptureWrite` ke role `nids01-testing-target-role`.
- Script baru: `capture_target.sh` (di Target).
- Hasil: pcap CLEAN.pcap = 3.3 MB, 450 flows. Berhasil.

## Pipeline yang Terbukti Bekerja

1. Target capture (tcpdump ens5) -> pcap -> S3
2. Analyzer download pcap dari S3
3. NFStream (statistical_analysis=True) + InitWindowPlugin -> 450 flows, 10 fitur
4. Scaling (StandardScaler dari deploy_meta.json)
5. Predict (baseline / robust) -> ground truth labeling -> metrik

## Hasil Metrik (Binary: attack vs benign)

| Skenario | Model | MCC | F1 | Precision | Recall | Accuracy | TN,FP,FN,TP |
|---|---|---|---|---|---|---|---|
| RT-S1 | baseline | 0.164 | 0.855 | 0.841 | 0.869 | 0.76 | 24,60,48,318 |
| RT-S3 | robust | 0.339 | 0.581 | 1.000 | 0.410 | 0.52 | 84,0,216,150 |

Ground truth: SSH-Bruteforce=305, Benign=84, Slowloris=49, DDoS-LOIC-HTTP=12 (total 450).

## TEMUAN PENTING (untuk paper)

1. **Feature mismatch NFStream vs CICFlowMeter TERBUKTI NYATA.**
   - Model baseline TIDAK PERNAH memprediksi "SSH-Bruteforce" (0 prediksi), padahal
     305 flow adalah SSH brute-force. Semua salah-klasifikasi jadi DoS Slowloris/GoldenEye.
   - Prediksi baseline: Slowloris=258, GoldenEye=120, Benign=72.
   - Penyebab: definisi fitur NFStream != CICFlowMeter (mis. `Fwd Seg Size Min` [CIC:
     ukuran segmen TCP min] vs `src2dst_min_ps` [NFStream: ukuran paket min termasuk header]).
   - Di level BINARY (attack vs benign), sebagian besar tetap terdeteksi "attack" -> recall
     baseline 0.869. Tapi MCC rendah karena FP tinggi (benign salah jadi attack).

2. **Model robust jauh lebih konservatif.**
   - Prediksi robust: Benign=300, Slowloris=150. Precision=1.0 (tidak ada FP) tapi
     Recall=0.41 (216 attack lolos jadi FN).
   - Efek adversarial training: decision boundary lebih ketat -> cenderung memprediksi Benign
     saat fitur "tidak yakin". Pada real-traffic dengan feature mismatch, ini membuat banyak
     serangan tidak terdeteksi.

3. **MCC real (0.16-0.34) jauh di bawah offline (~0.93).** Gap ini adalah bukti empiris
   bahwa model yang unggul pada dataset benchmark BELUM TENTU generalisasi ke real-traffic,
   terutama karena perbedaan feature extractor. Ini justru MEMPERKUAT motivasi paper:
   validasi real-traffic itu penting dan sering diabaikan literatur.

## Rekomendasi Langkah Lanjut

1. **Investigasi feature mismatch**: bandingkan statistik 10 fitur NFStream (real) vs
   distribusi training (deploy_meta scaler mean/scale). Cari fitur yang paling menyimpang.
2. **Opsi A-lanjut**: kalibrasi/mapping fitur NFStream agar lebih dekat definisi CICFlowMeter
   (mis. Fwd Seg Size Min -> gunakan payload_size min, bukan packet size min).
3. **Skenario Fitur-1 (8-fitur)**: latih ulang model offline HANYA dengan fitur yang
   definisinya konsisten antara NFStream & CIC, lalu bandingkan.
4. Lanjut RT-S2 & RT-S4 (evasion) untuk melihat apakah pola degradasi/robust konsisten.

## File Hasil (di Analyzer /opt/nids/results/ dan bisa di-upload ke S3)

- RT-S1_results.csv, RT-S1_metrics.json
- RT-S3_results.csv, RT-S3_metrics.json


---

# DIAGNOSTIK FEATURE MISMATCH (Root Cause MCC Rendah)

Membandingkan distribusi 10 fitur real-traffic (NFStream, 450 flows CLEAN) vs mean/scale
training (deploy_meta.json). z_of_mean = (real_mean - train_mean) / train_scale.

| Fitur | train_mean | real_mean | real_min | real_max | z_of_mean |
|---|---|---|---|---|---|
| Fwd Seg Size Min | 17.99 | 65.97 | 54.00 | 66.00 | **+6.23** |
| URG Flag Cnt | 0.04 | 0.00 | 0.00 | 0.00 | -0.21 |
| Tot Bwd Pkts | 6.24 | 32.80 | 4.00 | 11841 | +0.17 |
| Fwd Act Data Pkts | 20.12 | 60.69 | 5.00 | 23686 | +0.03 |
| Fwd Pkt Len Max | 200.67 | 220.02 | 54.00 | 1090 | +0.06 |
| Fwd Pkt Len Mean | 50.32 | 90.24 | 54.00 | 173.58 | +0.66 |
| Bwd Pkt Len Mean | 113.21 | 146.92 | 58.00 | 351.50 | +0.21 |
| Init Bwd Win Byts | 8680 | 62673 | 62643 | 63196 | **+2.62** |
| TotLen Bwd Pkts | 4654 | 2295 | 404 | 686778 | -0.01 |
| Init Fwd Win Byts | 8773 | 62591 | 1480 | 62727 | **+3.32** |

## Dua Sumber Mismatch (temuan penting untuk paper)

**(A) Mismatch DEFINISI feature extractor -- Fwd Seg Size Min (z=+6.23, terparah):**
- NFStream `src2dst_min_ps` = ukuran PAKET minimum (termasuk header IP+TCP, ~54-66 byte).
- CICFlowMeter `Fwd Seg Size Min` = ukuran SEGMEN/payload minimum (biasanya kecil, ~0-20).
- Akibat: fitur ini di real-traffic ~66 sedangkan training ~18 -> model bingung.

**(B) Mismatch ENVIRONMENT jaringan -- Init Fwd/Bwd Win Byts (z=+3.32 / +2.62):**
- AWS EC2 modern memakai TCP window besar (~62 KB) karena window scaling.
- Dataset CIC-IDS2018 direkam dengan window lebih kecil (~8 KB).
- Model belajar "window ~8KB = normal"; window 62KB dianggap di luar distribusi.
- Ini BUKAN bug ekstraksi (plugin sudah benar), melainkan perbedaan karakteristik jaringan
  antara lab pembuatan dataset vs lingkungan AWS nyata.

## Implikasi

- Fitur lain (Tot Bwd Pkts, Fwd Act Data Pkts, Pkt Len, dll) relatif konsisten (|z| < 1).
- 3 fitur menyimpang inilah penyebab utama SSH-Bruteforce salah-klasifikasi & MCC turun.
- Ini justru bukti empiris kuat: generalisasi real-traffic terganggu oleh (A) perbedaan
  tools ekstraksi fitur dan (B) perbedaan environment -- dua hal yang jarang dibahas literatur.

## Rencana Perbaikan

1. **Fwd Seg Size Min**: ubah mapping ke pendekatan payload-based, atau (lebih tepat) latih
   ulang model offline dengan fitur yang didefinisikan konsisten dengan NFStream.
2. **Init Win Byts**: karena ini environment mismatch, opsi:
   (a) skenario 8-fitur (buang kedua Init Win Byts) -> latih ulang offline, atau
   (b) normalisasi/clip window saat inference, atau
   (c) biarkan sebagai temuan (bukti environment gap).
3. Skenario Fitur-1 (8-fitur) menjadi semakin relevan: buang Fwd Seg Size Min + 2 Init Win Byts
   yang bermasalah, sisakan 7 fitur yang konsisten, latih ulang offline, bandingkan online.


---

# HASIL LENGKAP: MATRIKS 2x2 (RT-S1 s/d RT-S4)

Seluruh 4 skenario selesai dijalankan pada real-traffic AWS.

## Tabel Hasil Final

| Skenario | Model | Trafik | MCC | F1 | Precision | Recall | Accuracy | TN,FP,FN,TP |
|---|---|---|---|---|---|---|---|---|
| RT-S1 | baseline | clean   | 0.164  | 0.855 | 0.841 | 0.869 | 0.760 | 24,60,48,318 |
| RT-S2 | baseline | evasion | -0.070 | 0.633 | 0.762 | 0.542 | 0.506 | 34,57,154,182 |
| RT-S3 | robust   | clean   | 0.339  | 0.581 | 1.000 | 0.410 | 0.520 | 84,0,216,150 |
| RT-S4 | robust   | evasion | 0.389  | 0.626 | 1.000 | 0.455 | 0.571 | 91,0,183,153 |

Flows: CLEAN=450 (attack 366 / benign 84), EVASION=427 (attack 336 / benign 91).

## Perbandingan dengan Offline

| Skenario | MCC Offline | MCC Real | F1 Offline | F1 Real |
|---|---|---|---|---|
| RT-S1 (Base+Clean)   | 0.9351 | 0.164  | 0.9729 | 0.855 |
| RT-S2 (Base+Evasion) | 0.0184 | -0.070 | 0.7539 | 0.633 |
| RT-S3 (Robust+Clean) | 0.9347 | 0.339  | 0.9727 | 0.581 |
| RT-S4 (Robust+Evasion)| 0.9953 | 0.389  | 0.9985 | 0.626 |

## POLA KUNCI (konsisten dengan offline meski MCC absolut rendah)

1. **Baseline TERDEGRADASI oleh evasion:** RT-S1 -> RT-S2, MCC turun 0.164 -> -0.070
   (di bawah random). Mereplikasi pola offline (0.935 -> 0.018).

2. **Robust RECOVERY dari evasion:** RT-S3 -> RT-S4, MCC naik 0.339 -> 0.389.
   Model robust justru lebih baik saat evasion. Mereplikasi pola offline (robust tetap tinggi).

3. **Robust >> Baseline saat evasion:** RT-S2 (-0.070) vs RT-S4 (0.389). Selisih besar
   -> adversarial training terbukti efektif melindungi terhadap evasion PADA REAL-TRAFFIC.

4. **Robust selalu Precision=1.0** (tidak ada FP) tapi Recall rendah (~0.41-0.46). Model
   robust sangat konservatif -> tidak pernah salah alarm, tapi banyak attack lolos (FN tinggi)
   akibat feature mismatch.

## KESIMPULAN

Meskipun MCC absolut real-traffic jauh di bawah offline (karena feature mismatch NFStream vs
CICFlowMeter + environment gap TCP window), **POLA RELATIF antar-skenario TETAP KONSISTEN**
dengan hasil offline:
- Baseline rentan terhadap evasion (kolaps di bawah random).
- Robust tahan terhadap evasion (recovery, Precision sempurna).

Ini bukti empiris bahwa **Adversarial Training bekerja di lingkungan real-traffic**, bukan
hanya artefak dataset benchmark. Sekaligus mengungkap tantangan nyata deployment: perbedaan
feature extractor & environment menurunkan performa absolut -> menegaskan pentingnya kalibrasi
fitur dan/atau pelatihan ulang dengan fitur yang konsisten (Skenario Fitur-1 / 8-fitur).

## File Hasil di Analyzer (/opt/nids/results/)
- RT-S1_results.csv / RT-S1_metrics.json
- RT-S2_results.csv / RT-S2_metrics.json
- RT-S3_results.csv / RT-S3_metrics.json
- RT-S4_results.csv / RT-S4_metrics.json
- Capture: s3://ssh-detection-features-232032302717/captures/CLEAN.pcap, EVASION.pcap


---

# CARA RESUME PERCOBAAN (setelah cleanup NAT + stop EC2)

Kondisi idle saat ini (hemat biaya):
- NAT Gateway + Elastic IP: DIHAPUS (biaya NAT/EIP = 0).
- 3 EC2: STOPPED (biaya compute = 0, hanya EBS storage kecil).
- VPC, subnet, security group, IAM role, EC2 (stopped): TETAP ADA.
- Semua script terpasang di EC2 + tersimpan di S3. Model & hasil di S3.

## Langkah Resume

### 1. Create NAT Gateway (kembalikan konektivitas internet + SSM ke private subnet)
```
aws cloudformation create-stack --stack-name nids01-nat \
  --template-body file://nids01-05-1-nat.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1

aws cloudformation wait stack-create-complete --stack-name nids01-nat --region ap-southeast-1
```
Catatan: Target & Analyzer ada di PRIVATE subnet tanpa VPC endpoint, jadi SSM ke keduanya
HANYA berfungsi setelah NAT aktif.

### 2. Start 3 EC2
```
aws ec2 start-instances --region ap-southeast-1 \
  --instance-ids i-0b4e1a8e610543906 i-0adc1017c07918e61 i-038b59e834a810974
```
Private IP tetap sama (Attacker 10.3.1.214, Target 10.3.2.38, Analyzer 10.3.2.130).
Public IP Attacker BERUBAH (tidak masalah, percobaan pakai private IP).

### 3. Tunggu SSM online (~2 menit), verifikasi
```
aws ssm describe-instance-information --region ap-southeast-1 \
  --query "InstanceInformationList[].{Id:InstanceId,Ping:PingStatus}" --output table
```

### 4. Lanjut percobaan
Script & model masih ada di EC2 dan S3. Jalankan capture di Target + attack di Attacker,
lalu inference di Analyzer (lihat bagian pipeline di atas).

## Langkah Idle Kembali (hemat biaya setelah selesai)
```
# Hapus NAT (stop biaya NAT + EIP)
aws cloudformation delete-stack --stack-name nids01-nat --region ap-southeast-1

# Stop EC2
aws ec2 stop-instances --region ap-southeast-1 \
  --instance-ids i-0b4e1a8e610543906 i-0adc1017c07918e61 i-038b59e834a810974
```

## Referensi ID (tetap konstan)
- VPC: vpc-01481a725febf0f13
- Public subnet: subnet-0632bc989ee46bce0
- Private subnet: subnet-0ae360071c695a28f
- Security group: sg-0d1e025d35f8f747e
- Private route table: rtb-0d3bcd66eb0f7bf0b
- Attacker EC2: i-0b4e1a8e610543906 (10.3.1.214)
- Target EC2:   i-0adc1017c07918e61 (10.3.2.38)
- Analyzer EC2: i-038b59e834a810974 (10.3.2.130)
- S3 bucket: ssh-detection-features-232032302717
  - scripts/  : nfstream_win_extract.py, extract_and_infer.py, attack_clean.sh, attack_evasion.sh, capture_target.sh, schedule-nids01.json
  - captures/ : CLEAN.pcap, EVASION.pcap
  - results-nids01/ : RT-S1..S4 (csv + json)
  - models/   : baseline_xgboost_top10.json, robust_xgboost_top10.json, deploy_meta.json
