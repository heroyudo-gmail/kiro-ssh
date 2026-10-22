# CICDDoS2018 — Dokumentasi Penelitian

## Multi-Class Intrusion Detection Using Feature-Reduced XGBoost on CSE-CIC-IDS2018

---

## 1. Ringkasan

Penelitian menggunakan dataset CSE-CIC-IDS2018 untuk multi-class intrusion detection. Dataset ini lebih kaya dibanding CICDDoS2019 karena mencakup berbagai kategori serangan: Brute-Force, DoS, DDoS, Web Attack, Infiltration, dan Botnet.

---

## 2. Dataset: CSE-CIC-IDS2018

**Sumber:** Canadian Institute for Cybersecurity, University of New Brunswick
**URL:** https://www.unb.ca/cic/datasets/ids-2018.html

### File yang Tersedia

| # | File | Ukuran | Hari | Jenis Serangan |
|---|------|--------|------|----------------|
| 1 | Wednesday-14-02-2018 | 341.6 MB | 14 Feb | SSH Brute-Force, FTP Brute-Force |
| 2 | Thursday-15-02-2018 | 358.5 MB | 15 Feb | DoS (GoldenEye, Hulk, SlowHTTPTest, Slowloris) |
| 3 | Friday-16-02-2018 | 318.3 MB | 16 Feb | DoS (Slowloris, SlowHTTPTest, Hulk, GoldenEye) |
| 4 | Tuesday-20-02-2018 | 3,867.1 MB | 20 Feb | DDoS (LOIC-HTTP, LOIC-UDP) |
| 5 | Wednesday-21-02-2018 | 313.7 MB | 21 Feb | DDoS (HOIC) |
| 6 | Thursday-22-02-2018 | 364.9 MB | 22 Feb | Brute-Force (Web), XSS |
| 7 | Friday-23-02-2018 | 365.1 MB | 23 Feb | Brute-Force (Web), SQL Injection |
| 8 | Wednesday-28-02-2018 | 199.6 MB | 28 Feb | Infiltration |
| 9 | Thursday-01-03-2018 | 101.4 MB | 1 Mar | Infiltration |
| 10 | Friday-02-03-2018 | 336.0 MB | 2 Mar | Botnet |
| 11 | SSH-Bruteforce.csv | 220.5 MB | (extracted) | SSH Brute-Force only |

**Total:** ~6.7 GB, 11 file CSV

### Jenis Serangan (Multi-Class Labels)

| Kategori | Jenis Serangan | File |
|----------|---------------|------|
| Brute-Force | SSH-Bruteforce, FTP-BruteForce | 14 Feb |
| DoS | GoldenEye, Hulk, SlowHTTPTest, Slowloris | 15-16 Feb |
| DDoS | LOIC-HTTP, LOIC-UDP, HOIC | 20-21 Feb |
| Web Attack | Brute Force, XSS, SQL Injection | 22-23 Feb |
| Infiltration | Infiltration | 28 Feb, 1 Mar |
| Botnet | Bot | 2 Mar |
| Normal | Benign | Semua file |

### Karakteristik Dataset
- Fitur: 79-80 kolom (CICFlowMeter generated)
- Kolom label: biasanya kolom terakhir
- Berisi campuran Benign + Attack per file
- File Tuesday-20-02 sangat besar (3.8 GB) — perlu sampling agresif

---

## 3. Tujuan Penelitian

1. Multi-class intrusion detection (bukan hanya SSH)
2. Membandingkan 3 model: XGBoost, Random Forest, SVM
3. Feature reduction (Top-10, Top-15, Top-20 optimal features)
4. Pilih 3 model terbaik (overall F1) → deploy & uji coba di AWS
5. Deploy model ke arsitektur AWS yang sudah ada (Lambda/EC2)

---

## 4. Metodologi

### Pendekatan 1: Semua Attack Types
- Gabungkan semua 10 file (tanpa SSH-Bruteforce.csv yang sudah extracted)
- Label: Benign, SSH-Bruteforce, FTP-BruteForce, DoS-Hulk, DoS-GoldenEye, DoS-Slowloris, DoS-SlowHTTPTest, DDoS-LOIC-HTTP, DDoS-LOIC-UDP, DDoS-HOIC, Web-BruteForce, XSS, SQL-Injection, Infiltration, Bot
- Stratified sampling per file (karena sangat besar)

### Pendekatan 2: Fokus DoS/DDoS saja
- Hanya gunakan file 15-16 Feb (DoS) dan 20-21 Feb (DDoS)
- Label: Benign, GoldenEye, Hulk, Slowloris, SlowHTTPTest, LOIC-HTTP, LOIC-UDP, HOIC
- Lebih fokus dan comparable dengan CICDDoS2019

### Pipeline Notebook
```
Notebook 01: Sampling & Visualisasi Distribusi
             - Scan seluruh file → distribusi populasi
             - Bar chart distribusi label populasi asli
             - Pie chart komposisi attack types (full traffic + attack-only)
             - Stratified sampling 10% → file_100.csv
             - Comparison plot original vs sampled percentage
             - Generate subset: file_75, file_50, file_25
Notebook 02: Preprocessing & Cleaning
             - Impute Inf → max finite value per kolom
             - Hapus baris NaN
             - Drop kolom: Timestamp, Dst Port, Protocol
             - Hapus kolom zero-variance
             - StandardScaler pada fitur numerik
             - LabelEncoder pada label string → integer
             - Output: cleaned_100.pkl, cleaned_75.pkl, cleaned_50.pkl, cleaned_25.pkl
Notebook 03: Training & Evaluation (All Features)
             - 3 Model: XGBoost, Random Forest, SVM
             - Train & test pada 4 ukuran dataset (split 80/20)
             - Table performa: Accuracy, Precision, Recall, F1, ROC-AUC
             - Table efisiensi: Training time, Inference/10k, Model size, RAM
             - Learning Curve (F1 vs dataset size) per model
             - Confusion Matrix Heatmap (per model, dataset 100%)
             - Feature Importance Chart (Top-20)
             - Narasi perbandingan otomatis
             - Output: experiment_results_03.pkl, models/*.pkl
Notebook 04: Ablation Study — Feature Reduction
             - 3 Model x 4 Skenario (All, Top-20, Top-15, Top-10)
             - Table performa & efisiensi per skenario
             - Grafik F1-Score vs Number of Features per model
             - Grafik Training Time vs Number of Features
             - Confusion Matrix best configuration
             - Feature Importance Top-10 (deployment)
             - Narasi & rekomendasi deployment
             - Export Top-3 model terbaik (overall F1) ke models/deploy/
             - Format: XGBoost → .json native, RF/SVM → .pkl
             - Metadata: *_meta.json (scaler, features, labels, performance)
             - Output: ablation_results_04.pkl, ablation_*.csv, models/deploy/*
```

---

## 5. Perbandingan dengan CICDDoS2019

| Aspek | CICDDoS2018 | CICDDoS2019 |
|-------|-------------|-------------|
| Attack categories | 6 (BF, DoS, DDoS, Web, Infiltration, Bot) | 1 (DDoS only) |
| Attack types | 15+ | 13 |
| Total size | ~6.7 GB | ~8 GB |
| Training/Testing split | Per-day (custom) | Pre-split (01-12 vs 03-11) |
| Fitur | 79-80 | 87 |
| Keunggulan | Lebih beragam | Lebih fokus DDoS |

---

## 6. Progress

- [x] Download dataset (11 file CSV)
- [x] Notebook 01: Sampling & Visualisasi distribusi
- [x] Notebook 02: Preprocessing & Cleaning
- [x] Notebook 03: Training & Evaluation (3 model × 4 dataset sizes)
- [x] Notebook 04: Ablation Study (Top-20/15/10) + Export Top-3 model
- [ ] Deploy Top-3 model ke AWS (Lambda/EC2)
- [ ] Uji coba real-world di AWS (live traffic)
- [ ] Tulis paper/presentasi

---

## 7. Visualisasi (Notebook 01)

### Output Grafik

| File | Deskripsi |
|------|-----------|
| `bar_distribusi_label_populasi.png` | Bar chart distribusi jumlah flow per label (seluruh populasi asli) |
| `pie_komposisi_attack_types.png` | Pie chart 2-panel: (1) komposisi full traffic Benign+Attack, (2) komposisi attack types only |
| `comparison_original_vs_sampled.png` | Grouped bar chart perbandingan persentase original vs sampled 10% per label |

### Interpretasi
- Bar chart menunjukkan ketimpangan kelas (class imbalance) yang signifikan — DDoS mendominasi traffic
- Pie chart memperlihatkan proporsi Benign vs Attack dan proporsi relatif antar attack types
- Comparison plot memverifikasi bahwa stratified sampling berhasil mempertahankan distribusi asli (deviasi minimal)

---

## 8. Model Deployment & AWS Testing

### 8.1 Arsitektur AWS Testing

```
┌─────────────────────────────────────────────────────────────────────┐
│  VPC 10.1.0.0/16 (Private Subnet 10.1.1.0/24)                      │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Attacker-1   │  │ Attacker-2   │  │ Attacker-3   │              │
│  │ (BruteForce) │  │ (DoS)        │  │ (DDoS)       │              │
│  │ t3.small     │  │ t3.small     │  │ t3.small     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                       │
│         └──────────────────┼──────────────────┘                      │
│                            │ attack traffic                           │
│                            ▼                                          │
│                   ┌────────────────┐                                  │
│                   │ Target Server  │                                  │
│                   │ SSH+HTTP+FTP   │                                  │
│                   │ t3.small       │                                  │
│                   └────────┬───────┘                                  │
│                            │ Traffic Mirror / tcpdump                  │
│                            ▼                                          │
│                   ┌────────────────┐                                  │
│                   │ Analyzer       │                                  │
│                   │ CICFlowMeter   │──→ S3 (results)                 │
│                   │ + 3 Models     │                                  │
│                   │ t3.medium      │                                  │
│                   └────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.2 Isi Masing-Masing Server

#### Target Server (t3.small)
| Komponen | Fungsi |
|----------|--------|
| SSH (sshd) | Target brute-force SSH |
| Nginx (HTTP port 80) | Target DoS HTTP (Slowloris, GoldenEye, Hulk) |
| vsftpd (FTP port 21) | Target brute-force FTP |
| User: testuser/P@ssw0rd123 | Akun untuk testing |

#### Attacker-1: Brute-Force (t3.small)
| Tool | Serangan | Command |
|------|----------|---------|
| Hydra | SSH-Bruteforce | `hydra -L users.txt -P pass.txt TARGET ssh` |
| Hydra | FTP-BruteForce | `hydra -L users.txt -P pass.txt TARGET ftp` |
| Nmap | Service scan (benign) | `nmap -sV -p 22,21 TARGET` |

#### Attacker-2: DoS — Application Layer (t3.small)
| Tool | Serangan | Command |
|------|----------|---------|
| slowloris | DoS-Slowloris | `slowloris TARGET -p 80 -s 200` |
| GoldenEye | DoS-GoldenEye | `python3 goldeneye.py http://TARGET -w 50 -s 100` |
| SlowHTTPTest | DoS-SlowHTTPTest | `slowhttptest -c 1000 -H -i 10 -r 200 -u http://TARGET` |
| ab (ApacheBench) | DoS-Hulk (simulasi) | `ab -n 50000 -c 500 http://TARGET/` |

#### Attacker-3: DDoS — Volumetric (t3.small)
| Tool | Serangan | Command |
|------|----------|---------|
| hping3 | SYN Flood (LOIC-like) | `hping3 -S --flood -p 80 TARGET` |
| hping3 | UDP Flood | `hping3 --udp --flood -p 53 TARGET` |
| udp_flood.py | UDP volumetric (HOIC-like) | `python3 udp_flood.py TARGET 80 300` |
| nping | TCP Flood | `nping --tcp --rate 1000 -p 80 TARGET` |

#### Analyzer (t3.medium)
| Komponen | Fungsi |
|----------|--------|
| Java 17 | Runtime CICFlowMeter |
| CICFlowMeter | Extract flow features dari pcap/live capture |
| Python 3 + XGBoost | Load 3 model, inference |
| tcpdump/tshark | Packet capture |
| Schedule config (JSON) | Ground truth: kapan & dari mana serangan |
| Result logger | Tabel: predicted vs actual → performance metrics |

### 8.2.1 Rekomendasi OS Image

| Opsi | Pro | Kontra | Rekomendasi |
|------|-----|--------|-------------|
| **Amazon Linux 2023** | SSM built-in, ringan, gratis, stabil, yum/dnf | Perlu compile beberapa tools manual | ✅ **Target + Analyzer** |
| **Kali Linux (AWS Marketplace)** | Semua attack tools pre-installed | Besar (~8GB), biaya marketplace, SSM perlu setup manual | ✅ **Attacker 1/2/3** |
| **Ubuntu 22.04** | apt-get mudah, banyak package | SSM perlu install manual | Alternatif |

**Rekomendasi final:**
- **Attacker 1/2/3 → Kali Linux** — karena Hydra, Slowloris, hping3, GoldenEye, SlowHTTPTest, Nmap, Scapy semua sudah pre-installed. Tidak perlu compile manual.
- **Target + Analyzer → Amazon Linux 2023** — ringan, SSM native, stabil untuk server role.

> **Catatan:** Jika ingin hemat biaya (Kali di Marketplace bisa ada fee), bisa pakai Amazon Linux untuk semua dan install tools manual via UserData. CloudFormation template yang sudah dibuat menggunakan Amazon Linux 2023 dengan auto-install via UserData.

### 8.2.2 Detail Library & Tools per Server

#### Attacker-1: Brute-Force — Library yang Diinstall

| Package/Tool | Versi | Install Command | Sudah di UserData? |
|-------------|-------|-----------------|-------------------|
| gcc, make, openssl-devel | system | `yum install -y gcc make openssl-devel` | ✅ Ya |
| libssh-devel, pcre-devel | system | `yum install -y libssh-devel pcre-devel` | ✅ Ya |
| **Hydra** | v9.5 | compile from source (GitHub) | ✅ Ya |
| **Medusa** | latest | `yum install -y medusa` | ✅ Ya |
| **Nmap** | latest | `yum install -y nmap` | ✅ Ya |
| **Ncrack** (opsional) | latest | compile from source | ❌ Manual |
| sshpass | latest | `yum install -y sshpass` | ❌ Tambahkan |
| Password list (10k) | — | download dari SecLists (GitHub) | ✅ Ya |

#### Attacker-2: DoS — Library yang Diinstall

| Package/Tool | Versi | Install Command | Sudah di UserData? |
|-------------|-------|-----------------|-------------------|
| Python 3 + pip | system | `yum install -y python3 python3-pip` | ✅ Ya |
| git | system | `yum install -y git` | ✅ Ya |
| **slowloris** (Python) | latest | `pip3 install slowloris` | ✅ Ya |
| **GoldenEye** | latest | `git clone github.com/jseidl/GoldenEye` | ✅ Ya |
| gcc-c++, openssl-devel | system | `yum install -y gcc-c++ openssl-devel` | ✅ Ya |
| **SlowHTTPTest** | v1.9.0 | compile from source (GitHub) | ✅ Ya |
| **ab (ApacheBench)** | system | `yum install -y httpd-tools` | ✅ Ya |
| **RUDY** (opsional) | — | Python script custom | ❌ Manual |

#### Attacker-3: DDoS — Library yang Diinstall

| Package/Tool | Versi | Install Command | Sudah di UserData? |
|-------------|-------|-----------------|-------------------|
| gcc, make, libpcap-devel | system | `yum install -y gcc make libpcap-devel` | ✅ Ya |
| **hping3** | latest | compile from source / `yum install` | ✅ Ya |
| **Nmap + nping** | latest | `yum install -y nmap nmap-ncat` | ✅ Ya |
| Python 3 + pip | system | `yum install -y python3 python3-pip` | ✅ Ya |
| **Scapy** (Python) | latest | `pip3 install scapy` | ✅ Ya |
| **udp_flood.py** (custom) | — | Script custom (Python socket) | ✅ Ya |
| **synflood.py** (opsional) | — | Scapy-based SYN flood | ❌ Manual |
| iperf3 (opsional) | latest | `yum install -y iperf3` | ❌ Manual |

#### Target Server — Library yang Diinstall

| Package/Tool | Versi | Install Command | Sudah di UserData? |
|-------------|-------|-----------------|-------------------|
| **sshd** (OpenSSH) | system | Pre-installed (AL2023) | ✅ Ya |
| **Nginx** | latest | `yum install -y nginx` | ✅ Ya |
| **vsftpd** | latest | `yum install -y vsftpd` | ✅ Ya |
| User testuser | — | `useradd + chpasswd` | ✅ Ya |
| Password auth enabled | — | `sed` edit sshd_config | ✅ Ya |

#### Analyzer — Library yang Diinstall

| Package/Tool | Versi | Install Command | Sudah di UserData? |
|-------------|-------|-----------------|-------------------|
| **Java 17** (Corretto) | 17 | `yum install -y java-17-amazon-corretto` | ✅ Ya |
| **Python 3** + pip | system | `yum install -y python3 python3-pip` | ✅ Ya |
| **boto3** | latest | `pip3 install boto3` | ✅ Ya |
| **pandas** | latest | `pip3 install pandas` | ✅ Ya |
| **numpy** | latest | `pip3 install numpy` | ✅ Ya |
| **xgboost** | latest | `pip3 install xgboost` | ✅ Ya |
| **scikit-learn** | latest | `pip3 install scikit-learn` | ✅ Ya |
| **matplotlib** | latest | `pip3 install matplotlib` | ✅ Ya |
| **tcpdump** | system | `yum install -y tcpdump` | ✅ Ya |
| **tshark** (Wireshark CLI) | system | `yum install -y tshark` | ✅ Ya |
| **libpcap** | system | `yum install -y libpcap` | ✅ Ya |
| **CICFlowMeter** | 4.0 | Upload JAR dari S3 (post-deploy) | ❌ Post-deploy |
| **3 Model files** (.json) | — | Upload dari S3 (post-deploy) | ❌ Post-deploy |
| **3 Meta files** (.json) | — | Upload dari S3 (post-deploy) | ❌ Post-deploy |

### 8.2.3 Jika Menggunakan Kali Linux (Alternatif)

Jika menggunakan **Kali Linux AMI** untuk Attacker, tools berikut sudah **pre-installed**:

| Tool | Status di Kali |
|------|---------------|
| Hydra | ✅ Pre-installed (`/usr/bin/hydra`) |
| Medusa | ✅ Pre-installed |
| Nmap | ✅ Pre-installed |
| Ncrack | ✅ Pre-installed |
| hping3 | ✅ Pre-installed |
| Slowloris | ✅ `apt install slowloris` atau pip |
| GoldenEye | ❌ Perlu `git clone` |
| SlowHTTPTest | ✅ `apt install slowhttptest` |
| Scapy | ✅ Pre-installed (Python) |
| ab (ApacheBench) | ✅ `apt install apache2-utils` |
| SecLists (wordlist) | ✅ Pre-installed di `/usr/share/seclists/` |

**Keuntungan Kali:** UserData bisa dikosongkan (tools sudah ada), deploy lebih cepat.

**Kekurangan Kali:** AMI dari Marketplace (mungkin ada fee), image ~8GB (boot lebih lambat), SSM agent perlu install manual (`snap install amazon-ssm-agent`).

> **CloudFormation saat ini menggunakan Amazon Linux 2023** dengan semua tools di-compile/install via UserData. Jika ingin switch ke Kali, ubah parameter `InstanceAmiId` ke Kali AMI ID dan hapus/kurangi UserData.

### 8.3 Skenario Testing (1 Jam)

**Total durasi: 60 menit**

| Menit | Fase | Attacker | Serangan | Label (Ground Truth) |
|-------|------|----------|----------|---------------------|
| 00-05 | Warm-up | — | Benign traffic only | Benign |
| 05-10 | Attack 1 | Attacker-1 | SSH-Bruteforce (Hydra) | SSH-Bruteforce |
| 10-12 | Cooldown | — | Benign | Benign |
| 12-17 | Attack 2 | Attacker-1 | FTP-BruteForce (Hydra) | FTP-BruteForce |
| 17-19 | Cooldown | — | Benign | Benign |
| 19-24 | Attack 3 | Attacker-2 | Slowloris | DoS-Slowloris |
| 24-26 | Cooldown | — | Benign | Benign |
| 26-31 | Attack 4 | Attacker-2 | GoldenEye | DoS-GoldenEye |
| 31-33 | Cooldown | — | Benign | Benign |
| 33-38 | Attack 5 | Attacker-2 | SlowHTTPTest | DoS-SlowHTTPTest |
| 38-40 | Cooldown | — | Benign | Benign |
| 40-45 | Attack 6 | Attacker-2 | Hulk (ab flood) | DoS-Hulk |
| 45-47 | Cooldown | — | Benign | Benign |
| 47-52 | Attack 7 | Attacker-3 | SYN Flood (hping3) | DDoS-SYN |
| 52-54 | Cooldown | — | Benign | Benign |
| 54-59 | Attack 8 | Attacker-3 | UDP Flood | DDoS-UDP |
| 59-60 | Final | — | Benign cooldown | Benign |

**Catatan:**
- Cooldown 2 menit antar serangan agar CICFlowMeter selesai flush flow sebelumnya
- 8 jenis serangan × 5 menit + cooldown = 56 menit → **1 jam cukup**
- Bisa dipercepat ke 30-40 menit jika cooldown dikurangi ke 1 menit

### 8.4 Proses di Analyzer

```
1. Analyzer load schedule.json (ground truth)
2. Analyzer start CICFlowMeter (live capture atau pcap)
3. Setiap flow yang selesai:
   a. Extract fitur sesuai meta.json (feature_names)
   b. Scaling: (X - mean) / scale (dari meta.json)
   c. Predict dengan 3 model (Top-3 terbaik)
   d. Lookup ground truth berdasarkan timestamp + src_ip
   e. Log: [timestamp, src_ip, dst_ip, predicted, actual, correct?]
4. Setelah selesai → hitung per model:
   - Accuracy, Precision, Recall, F1, ROC-AUC
   - Per-class metrics
   - Confusion matrix
5. Export:
   - CSV detail (setiap flow + prediksi)
   - CSV summary (performance per model)
   - PNG grafik (confusion matrix, per-class F1)
   - Upload ke S3
```

### 8.5 Output untuk Offline Testing / Presentasi

| File | Isi |
|------|-----|
| `aws_test_flows.csv` | Setiap flow: features + predicted + actual |
| `aws_test_performance.csv` | Summary metrics per model |
| `aws_confusion_matrix_rank1.png` | Heatmap model terbaik |
| `aws_per_class_f1.png` | F1 per attack type per model |

Data ini bisa di-replay offline: load CSV → re-run model → verifikasi hasil (crosscheck).

### 8.5.1 Contoh Output: `aws_test_flows.csv`

Setiap baris = 1 network flow yang di-capture CICFlowMeter lalu di-predict oleh model.

```
| flow_id | timestamp           | src_ip     | dst_ip     | duration | fwd_pkt | ... | predicted_rank1 | predicted_rank2 | predicted_rank3 | actual_label    | correct_r1 | correct_r2 | correct_r3 |
|---------|---------------------|------------|------------|----------|---------|-----|-----------------|-----------------|-----------------|-----------------|------------|------------|------------|
| 1       | 2026-08-10 10:00:12 | 10.1.1.20  | 10.1.1.10  | 0.532    | 3       | ... | Benign          | Benign          | Benign          | Benign          | ✓          | ✓          | ✓          |
| 2       | 2026-08-10 10:00:45 | 10.1.1.20  | 10.1.1.10  | 1.204    | 5       | ... | Benign          | Benign          | Benign          | Benign          | ✓          | ✓          | ✓          |
| ...     | ...                 | ...        | ...        | ...      | ...     | ... | ...             | ...             | ...             | ...             | ...        | ...        | ...        |
| 47      | 2026-08-10 10:05:03 | 10.1.1.21  | 10.1.1.10  | 0.018    | 12      | ... | SSH-Bruteforce  | SSH-Bruteforce  | SSH-Bruteforce  | SSH-Bruteforce  | ✓          | ✓          | ✓          |
| 48      | 2026-08-10 10:05:08 | 10.1.1.21  | 10.1.1.10  | 0.022    | 15      | ... | SSH-Bruteforce  | SSH-Bruteforce  | Benign          | SSH-Bruteforce  | ✓          | ✓          | ✗          |
| ...     | ...                 | ...        | ...        | ...      | ...     | ... | ...             | ...             | ...             | ...             | ...        | ...        | ...        |
| 203     | 2026-08-10 10:19:15 | 10.1.1.22  | 10.1.1.10  | 58.320   | 1       | ... | DoS-Slowloris   | DoS-Slowloris   | DoS-Slowloris   | DoS-Slowloris   | ✓          | ✓          | ✓          |
| ...     | ...                 | ...        | ...        | ...      | ...     | ... | ...             | ...             | ...             | ...             | ...        | ...        | ...        |
| 512     | 2026-08-10 10:47:22 | 10.1.1.23  | 10.1.1.10  | 0.001    | 1024    | ... | DDoS-SYN        | DDoS-SYN        | DoS-Hulk        | DDoS-SYN        | ✓          | ✓          | ✗          |
```

**Estimasi jumlah flow:** 500-2000 flows selama 1 jam testing (tergantung attack rate & CICFlowMeter timeout setting).

### 8.5.2 Contoh Output: `aws_test_performance.csv`

Summary metrics per model:

```
| Model          | Scenario | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC (%) | Total Flows | Correct | Wrong |
|----------------|----------|--------------|---------------|------------|--------------|-------------|-------------|---------|-------|
| XGBoost        | Top-20   | 94.32        | 93.87         | 94.32      | 93.95        | 98.71       | 847         | 799     | 48    |
| XGBoost        | Top-15   | 93.15        | 92.44         | 93.15      | 92.68        | 97.89       | 847         | 789     | 58    |
| Random Forest  | Top-20   | 91.26        | 90.55         | 91.26      | 90.78        | 96.42       | 847         | 773     | 74    |
```

### 8.5.3 Contoh Output: Per-Class Performance (per model)

```
| Attack Type       | # Flows | Rank1 Precision | Rank1 Recall | Rank1 F1 | Rank2 F1 | Rank3 F1 |
|-------------------|---------|-----------------|--------------|----------|----------|----------|
| Benign            | 210     | 97.2%           | 95.8%        | 96.5%    | 95.1%    | 93.2%    |
| SSH-Bruteforce    | 85      | 98.5%           | 97.6%        | 98.0%    | 97.2%    | 95.8%    |
| FTP-BruteForce    | 78      | 96.3%           | 94.1%        | 95.2%    | 94.0%    | 91.5%    |
| DoS-Slowloris     | 62      | 91.5%           | 89.2%        | 90.3%    | 88.7%    | 85.4%    |
| DoS-GoldenEye     | 95      | 93.8%           | 92.4%        | 93.1%    | 91.5%    | 89.2%    |
| DoS-SlowHTTPTest  | 58      | 88.7%           | 86.5%        | 87.6%    | 85.3%    | 82.1%    |
| DoS-Hulk          | 112     | 95.1%           | 94.8%        | 95.0%    | 93.6%    | 91.8%    |
| DDoS-SYN          | 89      | 96.7%           | 95.3%        | 96.0%    | 94.8%    | 92.5%    |
| DDoS-UDP          | 58      | 94.2%           | 92.8%        | 93.5%    | 91.7%    | 89.3%    |
```

### 8.5.4 Contoh Output: Confusion Matrix (Model Rank #1)

```
                   Predicted →
Actual ↓        Ben  SSH  FTP  Slo  Gol  SlH  Hul  SYN  UDP
Benign          201   3    2    1    0    2    1    0    0
SSH-Bruteforce    1   83   1    0    0    0    0    0    0
FTP-BruteForce    2    1   74   0    0    1    0    0    0
DoS-Slowloris     3    0    0   55   2    2    0    0    0
DoS-GoldenEye     1    0    0    1   88   3    2    0    0
DoS-SlowHTTPTest  2    0    0    3    1   51   1    0    0
DoS-Hulk          1    0    0    0    2    1  107   1    0
DDoS-SYN          0    0    0    0    0    0    1   85   3
DDoS-UDP          0    0    0    0    0    0    1    2   55
```

### 8.5.5 Contoh Output: Terminal Orchestrator (`run_test.py`)

```
[10:00:00] ============================================================
[10:00:00] IDS2018 AWS TESTING — ORCHESTRATOR
[10:00:00] ============================================================
[10:00:00] Region: ap-southeast-1
[10:00:00] Target IP: 10.1.1.10
[10:00:00] Analyzer: i-0abc123...
[10:00:00] Total phases: 8
[10:00:00] Estimated total time: 56 min 0s
[10:00:00] ============================================================
[10:00:01] [ANALYZER] Starting tcpdump + CICFlowMeter...
[10:00:06] [ANALYZER] Capture started
[10:00:06] [WARMUP] Generating benign traffic for 300s...
[10:05:06] [WARMUP] Complete
[10:05:06]
[10:05:06] ============================================================
[10:05:06] [PHASE 1/8] SSH-Bruteforce
[10:05:06]   Attacker: attacker1 (i-0def456...)
[10:05:06]   Duration: 300s
[10:05:06] ============================================================
[10:05:07]   → SSM command sent: cmd-1a2b3c4d...
[10:05:07]   → Waiting 300s for attack to complete...
[10:10:07]   → Status: Success
[10:10:07]     [STATUS][ATTEMPT] target 10.1.1.10 - login "testuser"
[10:10:07]     [22][ssh] host: 10.1.1.10   login: testuser   password: P@ssw0rd123
[10:10:07]   → Cooldown 120s...
[10:12:07]
[10:12:07] ============================================================
[10:12:07] [PHASE 2/8] FTP-BruteForce
           ...
[10:56:XX]
[10:56:XX] ============================================================
[10:56:XX] TEST COMPLETE!
[10:56:XX] ============================================================
[10:56:XX] Total elapsed: 56 min 12s
[10:56:XX] Phases executed: 8
[10:56:XX]
[10:56:XX] Phase summary:
[10:56:XX]    1. SSH-Bruteforce       [attacker1] → Success
[10:56:XX]    2. FTP-BruteForce       [attacker1] → Success
[10:56:XX]    3. DoS-Slowloris        [attacker2] → Success
[10:56:XX]    4. DoS-GoldenEye        [attacker2] → Success
[10:56:XX]    5. DoS-SlowHTTPTest     [attacker2] → Success
[10:56:XX]    6. DoS-Hulk             [attacker2] → Success
[10:56:XX]    7. DDoS-SYN             [attacker3] → Success
[10:56:XX]    8. DDoS-UDP             [attacker3] → Success
[10:56:XX]
[10:56:XX] Results: s3://bucket/ids2018/results/
[10:56:XX] ============================================================
```

### 8.5.6 Prediksi Realistis Hasil Testing

Berdasarkan pengalaman model training pada dataset offline:

| Aspek | Prediksi |
|-------|----------|
| **Overall Accuracy** | 85-95% (lebih rendah dari offline karena domain shift) |
| **Brute-Force detection** | Tinggi (>95%) — pola sangat khas (banyak failed login dalam waktu singkat) |
| **DoS detection** | Menengah-Tinggi (88-94%) — Slowloris/GoldenEye punya signature flow yang jelas |
| **DDoS detection** | Tinggi (>93%) — SYN/UDP flood menghasilkan flow pattern sangat berbeda dari benign |
| **Kesalahan umum** | Slowloris ↔ SlowHTTPTest (mirip secara fitur), DoS-Hulk ↔ DDoS-SYN (keduanya high-rate) |
| **False Positive (Benign → Attack)** | Rendah (<5%) — benign traffic cukup bersih |
| **Domain shift** | Real traffic ≠ dataset 2018 persis, tapi fundamental pattern tetap sama |

**Catatan penting:**
- Performa di AWS **mungkin lebih rendah** 3-8% dari hasil offline karena:
  - Karakteristik traffic sedikit berbeda (versi tool, OS, network latency)
  - CICFlowMeter versi/setting berbeda dari yang digunakan pembuat dataset
  - Flow timeout setting mempengaruhi feature values
- Ini **normal dan expected** — tujuan testing bukan perfect score, tapi membuktikan model bekerja di real environment

### 8.6 CloudFormation Deployment

```bash
# Step 1: Network
aws cloudformation create-stack \
  --stack-name ids2018-network \
  --template-body file://CICDDoS2018/aws/01-network.yaml \
  --region ap-southeast-1

# Step 2: Instances (tunggu step 1 selesai)
aws cloudformation create-stack \
  --stack-name ids2018-instances \
  --template-body file://CICDDoS2018/aws/02-instances-ml-target.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1

# Step 3: Install tambahan via SSM (setelah instances running)
# Lihat section 8.7
```

### 8.7 Post-Deploy: Install Aplikasi via SSM

Setelah EC2 running, beberapa tool perlu di-install manual via SSM karena compile time lama:

```bash
# Connect ke instance via SSM
aws ssm start-session --target INSTANCE_ID --region ap-southeast-1

# Analyzer: Upload CICFlowMeter + models dari S3
aws s3 cp s3://BUCKET/cicflowmeter/ /opt/cicflowmeter/ --recursive
aws s3 cp s3://BUCKET/models/deploy/ /opt/ids2018/models/ --recursive

# Verify semua tools installed
# Attacker-1: which hydra
# Attacker-2: which slowloris && ls /opt/GoldenEye/
# Attacker-3: which hping3
# Analyzer: java -version && python3 -c "import xgboost"
```

### 8.8 Cara Menjalankan Testing (Step-by-Step Operasional)

Setelah `01-network.yaml` dan `02-instances.yaml` berhasil di-deploy, berikut langkah operasional lengkap:

#### STEP 0: Verifikasi Stack Selesai (dari local/laptop)

```bash
# Cek status stack
aws cloudformation describe-stacks --stack-name ids2018-network --query "Stacks[0].StackStatus"
aws cloudformation describe-stacks --stack-name ids2018-instances --query "Stacks[0].StackStatus"
# Keduanya harus "CREATE_COMPLETE"

# Ambil IP dan Instance ID dari output
aws cloudformation describe-stacks --stack-name ids2018-instances \
  --query "Stacks[0].Outputs" --output table
```

Catat:
- `TARGET_IP` (misal: 10.1.1.10)
- `ATTACKER1_ID`, `ATTACKER2_ID`, `ATTACKER3_ID`, `ANALYZER_ID`

#### STEP 1: Verifikasi Tools di Setiap Instance (5 menit)

Buka 5 terminal SSM secara paralel:

```bash
# Terminal 1 — Target
aws ssm start-session --target TARGET_ID --region ap-southeast-1

# Terminal 2 — Attacker-1
aws ssm start-session --target ATTACKER1_ID --region ap-southeast-1

# Terminal 3 — Attacker-2
aws ssm start-session --target ATTACKER2_ID --region ap-southeast-1

# Terminal 4 — Attacker-3
aws ssm start-session --target ATTACKER3_ID --region ap-southeast-1

# Terminal 5 — Analyzer
aws ssm start-session --target ANALYZER_ID --region ap-southeast-1
```

Verifikasi per instance:

```bash
# Target:
systemctl status sshd nginx vsftpd
ss -tlnp  # port 22, 80, 21 harus LISTEN

# Attacker-1:
which hydra && hydra -h | head -3

# Attacker-2:
which slowloris && ls /opt/GoldenEye/goldeneye.py && which ab

# Attacker-3:
which hping3 && python3 -c "from scapy.all import *; print('OK')"

# Analyzer:
java -version
python3 -c "import xgboost, pandas, numpy, sklearn; print('All libs OK')"
ls /opt/ids2018/models/  # harus ada rank1, rank2, rank3 files
```

#### STEP 2: Setup Analyzer — Start Capture (di Terminal Analyzer)

```bash
# Masuk ke Analyzer via SSM

# 2a. Upload schedule (ground truth) — dari S3 atau paste langsung
cat > /opt/ids2018/schedule/schedule.json << 'EOF'
{
  "test_duration_minutes": 60,
  "target_ip": "10.1.1.10",
  "phases": [
    {"start_min": 0,  "end_min": 5,  "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 5,  "end_min": 10, "type": "attack",  "attacker": "attacker1", "label": "SSH-Bruteforce"},
    {"start_min": 10, "end_min": 12, "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 12, "end_min": 17, "type": "attack",  "attacker": "attacker1", "label": "FTP-BruteForce"},
    {"start_min": 17, "end_min": 19, "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 19, "end_min": 24, "type": "attack",  "attacker": "attacker2", "label": "DoS-Slowloris"},
    {"start_min": 24, "end_min": 26, "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 26, "end_min": 31, "type": "attack",  "attacker": "attacker2", "label": "DoS-GoldenEye"},
    {"start_min": 31, "end_min": 33, "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 33, "end_min": 38, "type": "attack",  "attacker": "attacker2", "label": "DoS-SlowHTTPTest"},
    {"start_min": 38, "end_min": 40, "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 40, "end_min": 45, "type": "attack",  "attacker": "attacker2", "label": "DoS-Hulk"},
    {"start_min": 45, "end_min": 47, "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 47, "end_min": 52, "type": "attack",  "attacker": "attacker3", "label": "DDoS-SYN"},
    {"start_min": 52, "end_min": 54, "type": "benign",  "attacker": null,  "label": "Benign"},
    {"start_min": 54, "end_min": 59, "type": "attack",  "attacker": "attacker3", "label": "DDoS-UDP"},
    {"start_min": 59, "end_min": 60, "type": "benign",  "attacker": null,  "label": "Benign"}
  ],
  "attacker_ips": {
    "attacker1": "ATTACKER1_IP",
    "attacker2": "ATTACKER2_IP",
    "attacker3": "ATTACKER3_IP"
  }
}
EOF

# 2b. Start tcpdump (capture semua traffic ke target)
sudo tcpdump -i eth0 -w /opt/ids2018/capture.pcap &
echo "Capture started at $(date)"

# 2c. Start CICFlowMeter (background, output ke CSV)
cd /opt/cicflowmeter
java -jar CICFlowMeter.jar /opt/ids2018/capture.pcap /opt/ids2018/flows/ &
echo "CICFlowMeter started"
```

#### STEP 3: Jalankan Serangan Sesuai Schedule

**Opsi 1: Otomatis via Orchestrator Script (REKOMENDASI)**

Cukup jalankan satu script dari laptop — semua 3 attacker dikendalikan otomatis:

```bash
# Dari laptop (pastikan AWS CLI configured + boto3 installed):
cd CICDDoS2018/aws/

# 1. Edit config (isi instance ID + IP dari CloudFormation output):
#    test_config.json

# 2. Jalankan orchestrator:
python run_test.py test_config.json
```

Script `run_test.py` akan:
- Start tcpdump di Analyzer
- Generate benign traffic (warmup 5 menit)
- Kirim attack commands ke Attacker 1/2/3 via `aws ssm send-command`
- Tunggu setiap attack selesai (5 menit per attack)
- Cooldown 2 menit antar attack
- Stop capture di Analyzer
- Trigger inference script di Analyzer
- Upload results ke S3
- Print summary di terminal laptop

Seluruh proses berjalan sequential & otomatis. Kamu cukup monitor output di terminal.

**Opsi 2: Manual (jika perlu debug)**

Gunakan timer manual atau script. Berikut command per fase:

**Menit 00-05: Benign (dari laptop, generate normal traffic)**
```bash
# Di Attacker-1 (sebagai benign traffic generator):
for i in $(seq 1 10); do
  sshpass -p 'P@ssw0rd123' ssh -o StrictHostKeyChecking=no testuser@TARGET_IP "echo benign $i"
  sleep 25
done
```

**Menit 05-10: SSH Brute-Force (Attacker-1)**
```bash
# Di Attacker-1:
hydra -l testuser -P /opt/attack/passwords.txt -t 8 -w 3 TARGET_IP ssh -V 2>&1 | tee /opt/attack/log_ssh_bruteforce.txt
```

**Menit 12-17: FTP Brute-Force (Attacker-1)**
```bash
# Di Attacker-1:
hydra -l testuser -P /opt/attack/passwords.txt -t 8 -w 3 TARGET_IP ftp -V 2>&1 | tee /opt/attack/log_ftp_bruteforce.txt
```

**Menit 19-24: Slowloris (Attacker-2)**
```bash
# Di Attacker-2:
timeout 300 slowloris TARGET_IP -p 80 -s 200 --sleeptime 1 2>&1 | tee /opt/attack/log_slowloris.txt
```

**Menit 26-31: GoldenEye (Attacker-2)**
```bash
# Di Attacker-2:
timeout 300 python3 /opt/GoldenEye/goldeneye.py http://TARGET_IP -w 50 -s 100 2>&1 | tee /opt/attack/log_goldeneye.txt
```

**Menit 33-38: SlowHTTPTest (Attacker-2)**
```bash
# Di Attacker-2:
timeout 300 slowhttptest -c 1000 -H -i 10 -r 200 -t GET -u http://TARGET_IP/ -p 3 -l 300 2>&1 | tee /opt/attack/log_slowhttptest.txt
```

**Menit 40-45: Hulk / HTTP Flood (Attacker-2)**
```bash
# Di Attacker-2:
timeout 300 ab -n 100000 -c 500 http://TARGET_IP/ 2>&1 | tee /opt/attack/log_hulk.txt
```

**Menit 47-52: SYN Flood (Attacker-3)**
```bash
# Di Attacker-3:
sudo timeout 300 hping3 -S --flood -V -p 80 TARGET_IP 2>&1 | tee /opt/attack/log_synflood.txt
```

**Menit 54-59: UDP Flood (Attacker-3)**
```bash
# Di Attacker-3:
sudo timeout 300 python3 /opt/attack/udp_flood.py TARGET_IP 80 300 2>&1 | tee /opt/attack/log_udpflood.txt
```

#### STEP 4: Stop Capture & Run Inference (di Analyzer)

```bash
# Stop tcpdump
sudo kill $(pgrep tcpdump)
echo "Capture stopped at $(date)"

# Tunggu CICFlowMeter selesai proses
sleep 30
kill $(pgrep -f CICFlowMeter) 2>/dev/null

# Run inference script (predict + compare vs ground truth)
cd /opt/ids2018
python3 inference.py \
  --flows-dir /opt/ids2018/flows/ \
  --models-dir /opt/ids2018/models/ \
  --schedule /opt/ids2018/schedule/schedule.json \
  --output-dir /opt/ids2018/results/

echo "Inference complete!"
ls -la /opt/ids2018/results/
```

#### STEP 5: Download Hasil & Upload ke S3

```bash
# Upload results ke S3
aws s3 cp /opt/ids2018/results/ s3://BUCKET/ids2018/results/ --recursive

# Atau download langsung ke local via SSM + S3
# (dari laptop):
aws s3 cp s3://BUCKET/ids2018/results/ ./results_aws/ --recursive
```

#### STEP 6: Cleanup (Stop Instances untuk Hemat Biaya)

```bash
# Stop semua instances
aws ec2 stop-instances --instance-ids \
  TARGET_ID ATTACKER1_ID ATTACKER2_ID ATTACKER3_ID ANALYZER_ID \
  --region ap-southeast-1

# Atau hapus seluruh stack
aws cloudformation delete-stack --stack-name ids2018-instances --region ap-southeast-1
aws cloudformation delete-stack --stack-name ids2018-network --region ap-southeast-1
```

#### Tips Operasional

| Tips | Penjelasan |
|------|-----------|
| Gunakan `tmux` di setiap SSM session | Agar command tetap jalan walau session putus |
| Set `date` yang sama di semua instance | Pastikan NTP sync agar timestamp konsisten |
| Pakai `timeout` di setiap attack command | Agar tidak lupa stop (auto 5 menit) |
| Log stdout setiap attack ke file | Untuk bukti bahwa attack benar-benar jalan |
| Monitor Target load (`htop`) | Pastikan target tidak crash selama DoS |

| Rank | Model File | Format | Alasan |
|------|-----------|--------|--------|
| #1 | `rank1_*.json` | XGBoost native JSON | Portable, no pickle |
| #2 | `rank2_*.json/.pkl` | JSON atau Pickle | Tergantung model type |
| #3 | `rank3_*.json/.pkl` | JSON atau Pickle | Tergantung model type |

Setiap model disertai `*_meta.json` berisi:
- `feature_names` — kolom yang perlu diekstrak dari CICFlowMeter output
- `scaler.mean` / `scaler.scale` — untuk StandardScaler
- `inverse_label_mapping` — decode prediksi integer → nama attack

---

## 9. Fase 2: Protected Target (Target-2 + AWS Security Services)

### 9.1 Tujuan

Setelah testing fase 1 selesai (Target-1 tanpa proteksi), deploy **Target-2** yang dilindungi oleh AWS native security services. Bandingkan:
- **Model ML saja** (fase 1) vs **AWS security services saja** (fase 2) vs **Keduanya digabung**
- Mana yang lebih cepat detect? Mana yang lebih akurat?
- Apakah model ML menambah value di atas AWS managed services?

### 9.2 AWS Security Services di Target-2

| Service | Fungsi | Detection Type |
|---------|--------|---------------|
| **ALB** | Load balancer di depan EC2 | Prerequisite WAF |
| **AWS WAF** (Web ACL) | Rate limiting (1000 req/5min), SQL injection rules, bad input filter | HTTP layer attacks |
| **GuardDuty** | Anomaly detection, brute-force detection, recon detection | Network + DNS + Account level |
| **Security Hub** | Aggregasi findings dari GuardDuty + WAF + lainnya | Centralized dashboard |
| **VPC Flow Logs** | Catat semua network traffic (audit trail) | Passive logging |

### 9.3 Arsitektur Target-2

```
Attacker 1/2/3
      │
      ├── SSH direct → Target-2 EC2 (port 22)
      │                    ↑ GuardDuty monitors SSH login patterns
      │
      └── HTTP via ALB → [WAF Web ACL] → ALB → Target-2 EC2 (port 80)
                              │
                              └── Block jika: rate > 1000/5min
                                            OR SQLi detected
                                            OR bad input detected
                                            OR known bad IP

      VPC Flow Logs ← records semua traffic
      Security Hub  ← aggregates findings dari GuardDuty + WAF
```

### 9.4 Deployment

```bash
# Deploy setelah fase 1 testing selesai
aws cloudformation create-stack \
  --stack-name ids2018-protected \
  --template-body file://CICDDoS2018/aws/03-instances-aws-target.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1
```

### 9.5 Skenario Testing Fase 2

Jalankan **serangan yang sama** seperti fase 1, tapi target diganti ke Target-2 (ALB DNS untuk HTTP, direct IP untuk SSH):

```bash
# Update test_config.json:
# "target_ip": "TARGET2_IP" (untuk SSH brute-force)
# "target_http": "ALB_DNS_NAME" (untuk DoS/DDoS HTTP)
python run_test.py test_config_phase2.json
```

### 9.6 Perbandingan Output Fase 1 vs Fase 2

| Metric | Fase 1 (ML Only) | Fase 2 (AWS Services) | Fase 2 (ML + AWS) |
|--------|-------------------|----------------------|-------------------|
| SSH-Bruteforce detected? | ✅ Model predicts | ✅ GuardDuty alert | ✅ Both |
| FTP-Bruteforce detected? | ✅ Model predicts | ⚠️ GuardDuty (limited FTP) | ✅ ML covers gap |
| DoS-Slowloris blocked? | ✅ Detected (not blocked) | ⚠️ WAF rate limit may miss (low rate) | ✅ ML detects |
| DoS-GoldenEye blocked? | ✅ Detected | ✅ WAF rate limit blocks | ✅ Both |
| DoS-Hulk blocked? | ✅ Detected | ✅ WAF rate limit blocks | ✅ Both |
| DDoS-SYN blocked? | ✅ Detected | ⚠️ GuardDuty alerts (no block) | ✅ ML faster detect |
| DDoS-UDP blocked? | ✅ Detected | ⚠️ GuardDuty alerts (no block) | ✅ ML faster detect |
| Detection latency | ~5-10 detik (per flow) | 5-15 menit (GuardDuty) | Fastest: ML |
| False positive rate | Low (trained) | Very low (managed rules) | Lowest combined |
| Cost | EC2 compute only | WAF $5/ACL + $0.60/M req + GuardDuty | Higher |

### 9.7 Kesimpulan yang Diharapkan

1. **AWS WAF** efektif untuk HTTP flood (rate-based) tapi **tidak detect** Slowloris (low-rate) atau SSH brute-force
2. **GuardDuty** detect brute-force SSH tapi **lambat** (15 menit publishing) dan **tidak block** (hanya alert)
3. **Model ML** detect **semua jenis** dengan latency rendah (~detik) tapi **tidak block** (hanya classify)
4. **Kombinasi terbaik**: ML untuk fast detection + WAF untuk active blocking + GuardDuty untuk audit/compliance

Ini menjadi **value proposition** penelitian: model ML melengkapi AWS native services dengan:
- Deteksi lebih cepat (real-time vs 15 menit)
- Coverage lebih luas (SSH, FTP, low-rate DoS yang WAF miss)
- Multi-class classification (tahu JENIS serangan, bukan hanya "anomaly")

---

## 10. Fase 3: Open-Source IDS Target (Target-3)

### 10.1 Tujuan

Deploy Target-3 yang dilindungi oleh **tools open-source** untuk intrusion detection & prevention di Layer 3, 4, dan 7. Bandingkan dengan Target-1 (ML) dan Target-2 (AWS managed).

### 10.2 Tools yang Diinstall di Target-3

| Tool | Layer | Fungsi | Detect? | Block? |
|------|-------|--------|---------|--------|
| **Suricata** | L3, L4, L7 | Network IDS/IPS — inspect semua packet, rule-based detection | ✅ | ✅ (IPS mode) |
| **Fail2Ban** | L7 (Application) | Monitor auth logs → ban IP via iptables | ✅ | ✅ (auto-ban) |
| **Nginx Rate Limiting** | L7 (HTTP) | Rate limit 10 req/s per IP, burst 20 | ✅ (implicit) | ✅ (reject 503) |

**Suricata Rules (custom untuk IDS2018):**
- SSH Brute-Force: >5 attempts / 60s → alert
- FTP Brute-Force: >5 USER commands / 60s → alert
- HTTP Flood (Hulk/GoldenEye): >100 req / 10s → alert
- Slowloris: incomplete HTTP requests >20 / 30s → alert
- SYN Flood: >500 SYN / 10s → alert
- UDP Flood: >1000 packets / 10s → alert
- Slow HTTP POST: >10 incomplete POST / 30s → alert

### 10.3 Deployment

```bash
aws cloudformation create-stack \
  --stack-name ids2018-opensource \
  --template-body file://CICDDoS2018/aws/04-opensource-target.yaml \
  --region ap-southeast-1
```

### 10.4 Collect Results (di Target-3)

```bash
# Setelah testing selesai, collect semua alerts:
/opt/ids2018/collect_alerts.sh

# Output: /opt/ids2018/logs/alerts_YYYYMMDD_HHMMSS.csv
# Upload ke S3:
aws s3 cp /opt/ids2018/logs/ s3://BUCKET/ids2018/results/ --recursive
```

---

## 11. Notebook 05: Perbandingan 3 Pendekatan

File: `CICDDoS2018/notebooks/05_comparison.ipynb`

### Input Files (dari S3 setelah testing):
- `results/target1_ml_results.csv` — per-flow predictions dari ML model
- `results/target2_aws_results.csv` — WAF blocks + GuardDuty findings
- `results/target3_opensource_results.csv` — Suricata alerts + Fail2Ban bans

### Output Visualisasi:
| File | Deskripsi |
|------|-----------|
| `comparison_detection_rate.png` | Grouped bar chart: detection rate per attack type × 3 targets |
| `comparison_radar.png` | Radar chart: 5 dimensi (detect rate, speed, coverage, FP, blocking) |
| `comparison_latency.png` | Bar chart: detection latency per attack (log scale) |
| `comparison_heatmap.png` | Heatmap: attack type × system → detection rate |
| `comparison_detection_rates.csv` | Tabel detection rate (untuk paper) |
| `comparison_latency.csv` | Tabel latency (untuk paper) |
| `comparison_overall.csv` | Tabel perbandingan keseluruhan |

---

## 12. Catatan Penting

1. File Tuesday-20-02 (3.8 GB) perlu strategi khusus — mungkin sampling lebih agresif atau skip untuk run awal
2. Label naming perlu dicek per file (mungkin berbeda format)
3. Bisa di-reuse arsitektur AWS yang sama (Traffic Mirror + Analyzer)
4. Untuk demo, bisa simulate berbagai attack type dari Attacker Node (Hydra, Slowloris, hping3)


---

## Ringkasan Notebook (Quick Reference)

### 01_sampling.ipynb — Sampling & Visualisasi Distribusi

**Apa yang dilakukan:**
- Scan semua file CSV dataset (10 file, ~6.7 GB total)
- Hitung distribusi label populasi asli (Benign vs masing-masing attack type)
- Stratified sampling 10% → simpan sebagai `file_100.csv`
- Generate subset: `file_75.csv`, `file_50.csv`, `file_25.csv`
- Verifikasi sampling mempertahankan distribusi asli

**Output .png:**
| File | Isi |
|------|-----|
| `bar_distribusi_label_populasi.png` | Bar chart jumlah flow per label di dataset asli |
| `pie_komposisi_attack_types.png` | Pie chart: (1) Benign vs Attack, (2) proporsi antar attack types |
| `comparison_original_vs_sampled.png` | Grouped bar chart perbandingan % original vs sampled per label |

---

### 02_preprocessing.ipynb — Preprocessing & Cleaning

**Apa yang dilakukan:**
- Load semua file subset (100/75/50/25)
- Impute nilai Infinity → max finite value per kolom
- Hapus baris NaN
- Drop kolom: Timestamp, Dst Port, Protocol (non-feature)
- Hapus kolom zero-variance (fitur yang nilainya konstan)
- StandardScaler normalisasi fitur numerik
- LabelEncoder: label string → integer

**Output .png:** Tidak ada (hanya menghasilkan file .pkl yang dipakai notebook selanjutnya)

**Output data:** `cleaned_100.pkl`, `cleaned_75.pkl`, `cleaned_50.pkl`, `cleaned_25.pkl`

---

### 03_training.ipynb — Training & Evaluation (All Features)

**Apa yang dilakukan:**
- Train 3 model (XGBoost, Random Forest, SVM) pada 4 ukuran dataset
- Split 80/20 per dataset size
- Hitung metrik: Accuracy, Precision, Recall, F1, ROC-AUC
- Hitung efisiensi: Training time, Inference per 10k samples, Model size, RAM usage
- Feature importance (Top-20) berdasarkan XGBoost gain

**Output .png:**
| File | Isi |
|------|-----|
| `learning_curve_all_features.png` | Line chart F1-score vs dataset size (100/75/50/25) per model |
| `confusion_matrix_all_models.png` | Heatmap confusion matrix untuk ketiga model (dataset 100%) |
| `feature_importance_top20.png` | Horizontal bar chart 20 fitur terpenting berdasarkan gain |

**Output data:** `experiment_results_03.pkl`, model files di `models/`

---

### 04_ablation.ipynb — Feature Reduction (Ablation Study)

**Apa yang dilakukan:**
- Train 3 model × 4 konfigurasi fitur: All features, Top-20, Top-15, Top-10
- Ukur F1-score dan inference time per konfigurasi
- Tentukan konfigurasi optimal (sweet spot: F1 tertinggi, size terkecil)
- Export Top-3 model terbaik untuk deployment (format .json / .pkl)
- Simpan metadata per model (scaler params, feature names, label mapping)

**Output .png:**
| File | Isi |
|------|-----|
| `ablation_f1_vs_features.png` | Line chart F1-score vs jumlah fitur per model |
| `ablation_time_vs_features.png` | Line chart inference time vs jumlah fitur per model |
| `confusion_matrix_best_ablation.png` | Heatmap CM dari konfigurasi model terbaik |
| `feature_importance_top10_deploy.png` | Horizontal bar chart 10 fitur final untuk deployment |

**Output data:** `ablation_results_04.pkl`, model files di `models/deploy/`

---

### 05_comparison.ipynb — Final Comparison & Presentasi

**Apa yang dilakukan:**
- Load semua hasil dari notebook 03 dan 04
- Rangkum perbandingan performa antar model dan konfigurasi
- Buat visualisasi untuk presentasi/paper
- Generate tabel summary detection rate per attack type
- Bandingkan latency (inference time) antar model

**Output .png:**
| File | Isi |
|------|-----|
| `comparison_detection_rate.png` | Bar chart detection rate per attack type per model |
| `comparison_radar.png` | Radar/spider chart multi-metrik per model |
| `comparison_latency.png` | Bar chart latency comparison antar model + konfigurasi fitur |

**Output data:** Summary CSV untuk paper

---

## Ringkasan File AWS (Quick Reference)

### CloudFormation YAML — Infrastructure as Code

| File | Stack | Kegunaan |
|------|-------|----------|
| `05-network-vpc.yaml` | Network layer | VPC, Private Subnet, Route Table, Security Groups, VPC Endpoints |
| `06-target1-instance.yaml` | Target 1 | EC2 target server (SSH+HTTP+FTP) — AZ-A |
| `07-target2-instance.yaml` | Target 2 | EC2 target tambahan — AZ-A |
| `08-target3-instance.yaml` | Target 3 | EC2 target tambahan — AZ-A |
| `09-target4-instance-azb.yaml` | Target 4 | EC2 target di AZ-B (multi-AZ testing) |
| `10-alb.yaml` | Load Balancer | Application Load Balancer di depan target servers |
| `11-waf.yaml` | WAF | AWS WAF rules untuk proteksi HTTP (DDoS protection) |
| `12-guardduty-flowlogs.yaml` | Monitoring | GuardDuty + VPC Flow Logs sebagai baseline comparison |

**Deploy order:** 05 → 06/07/08/09 → 10 → 11 → 12
**Delete order:** 12 → 11 → 10 → 09/08/07/06 → 05

### Script Pendukung

| File | Kegunaan |
|------|----------|
| `extract_flows_tshark.py` | Ekstraksi flow features dari pcap menggunakan tshark (alternatif CICFlowMeter) |
| `inference.py` | Script inferensi: load model, predict, log result, upload S3 |
| `install-attacker.sh` | Script install semua attack tools (Hydra, Slowloris, GoldenEye, hping3, dll) |
| `run_test.py` | Orchestrator: jalankan semua skenario serangan secara otomatis via SSM |
| `testing-attack.sh` | Script serangan manual (alternative untuk run_test.py) |

### Dokumentasi Skenario

| File | Isi |
|------|-----|
| `langkah.md` | Langkah-langkah operasional deploy & testing |
| `vpc_testing.md` | Detail konfigurasi VPC untuk testing |
| `attack.md` | Daftar serangan dan command per tool |
| `skenario-1.md` | Detail skenario testing batch 1 (Brute-Force) |
| `skenario-2.md` | Detail skenario testing batch 2 (DoS) |
| `skenario-3.md` | Detail skenario testing batch 3 (DDoS) |

---


## Ringkasan Notebook 05-08 (Adversarial Robustness Pipeline)

### 05_adversarial_attack.ipynb — Saliency Map & Evasion Simulation

**Apa yang dilakukan:**
- Load model baseline XGBoost Top-10 dari notebook 04
- Hitung Saliency Map (gradient sensitivitas loss terhadap tiap fitur)
- Generate adversarial samples menggunakan FGSM (ε = 0.01, 0.05, 0.1)
- Evaluasi vulnerability: ukur MCC/F1 drop pada setiap level epsilon
- Identifikasi kelas yang paling rentan terhadap evasion

**Hasil utama:**
- Fitur paling sensitif: `Init Fwd Win Byts` (saliency = 35.37)
- MCC drop: 0.9332 → 0.0189 pada ε=0.1 (penurunan 98%)
- F1 drop: 97.28% → 75.67%
- Kelas paling rentan: DDoS-HOIC (100% drop), DDoS-LOIC-UDP (100%)

**Output:** `adversarial_results_05.pkl`, `adversarial_samples_05.pkl`, 4 file PNG

---

### 06_adversarial_training.ipynb — Hardening via Adversarial Training

**Apa yang dilakukan:**
- Load adversarial samples dari notebook 05
- Augmentasi training data: D_robust = D_clean ∪ D_adv (rasio 80:20)
- Re-train XGBoost pada D_robust (Min-Max optimization)
- Evaluasi 4 skenario S1-S4:
  - S1: Baseline + Clean → MCC = 0.9332
  - S2: Baseline + Adversarial → MCC = 0.0189
  - S3: Robust + Clean → MCC = 0.9327
  - S4: Robust + Adversarial → MCC = 0.9946

**Hasil utama:**
- Security Gap (S1→S2): 0.9143
- Integrity Loss (S1→S3): 0.0005 (0.05% — minimal)
- Recovery (S2→S4): +0.9757 (penuh!)
- Adversarial Training BERHASIL tanpa mengorbankan akurasi normal

**Output:** `robust_results_06.pkl`, 2 file PNG

---

### 07_robustness_ablation.ipynb — Feature Count vs Robustness

**Apa yang dilakukan:**
- Uji 4 konfigurasi: C1(Full/68), C2(Top-15), C3(Top-10), C4(Top-5)
- Setiap konfigurasi: train baseline & robust, test clean & adversarial
- Identifikasi sweet spot (balance efisiensi vs keamanan)

**Hasil utama:**
- C4 (Top-5) paling rentan: security gap = 0.7820
- C1 (Full) paling aman tapi besar: MCC adv = 0.9967
- **C3 (Top-10) = sweet spot**: balance optimal antara size, speed, dan robustness
- JANGAN deploy Top-5 (terlalu rentan, recovery tidak memadai)

**Output:** `robustness_ablation_07.pkl`, 2 file PNG

---

### 08_evaluation.ipynb — Final Evaluation & Visualisasi Paper

**Apa yang dilakukan:**
- Rangkum semua hasil S1-S4 dari notebook 06
- Buat visualisasi final: confusion matrix 2×2, radar chart, grouped bar
- Generate tabel summary untuk paper
- Export semua metrik dalam format siap paper

**Output:** `evaluation_final_08.pkl`, 3 file PNG

---

## Hasil Utama Penelitian (S1-S4)

| Skenario | Model | Data Uji | MCC | F1 (%) | Interpretasi |
|----------|-------|----------|-----|--------|-------------|
| S1 | Baseline | Clean | 0.9332 | 97.28 | Performa normal |
| S2 | Baseline | Adversarial (ε=0.1) | 0.0189 | 75.67 | GAGAL — hampir random |
| S3 | Robust (AT) | Clean | 0.9327 | ~97.2 | Integritas terjaga |
| S4 | Robust (AT) | Adversarial (ε=0.1) | 0.9946 | ~99.7 | Recovery sempurna |

## Progress Update

- [x] Notebook 01: Sampling & Visualisasi
- [x] Notebook 02: Preprocessing & Cleaning
- [x] Notebook 03: Training & Evaluation (3 model × 4 sizes)
- [x] Notebook 04: Ablation Study + Export models
- [x] Notebook 05: Adversarial Attack (Saliency Map + FGSM)
- [x] Notebook 06: Adversarial Training (S1-S4)
- [x] Notebook 07: Robustness Ablation (C1-C4)
- [x] Notebook 08: Final Evaluation & Visualisasi
- [ ] Notebook 09: Comparison (opsional, untuk presentasi)
- [x] Paper LaTeX: nids-01.tex (updated dengan data aktual)
- [ ] Deploy & Live Testing di AWS

---
