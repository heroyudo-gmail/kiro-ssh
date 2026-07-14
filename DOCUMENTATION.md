# SSH Brute-Force Detection — Dokumentasi Lengkap

## "A Feature-Reduced SSH Brute-Force Detection Method Using XGBoost on AWS Infrastructure"

---

## 1. Ringkasan Project

Project ini mereplikasi dan memperluas paper yang mengusulkan sistem deteksi SSH brute-force menggunakan XGBoost. Kami melakukan:

1. Training & benchmarking model ML pada 2 dataset (notebook)
2. Multi-dataset comparison & ablation study
3. Deployment end-to-end di AWS (Traffic Mirroring → Analyzer → XGBoost Inference → SNS)
4. Live testing dengan model XGBoost sesungguhnya

**Arsitektur Final:** Semua proses (capture, extract, predict, alert) terpusat di Analyzer Node — tanpa Lambda.

---

## 2. Struktur File

```
kiro-ssh/
├── notebooks/
│   ├── model_training.ipynb        # Training Dataset A (625k samples)
│   ├── deteksi_ssh.ipynb           # Multi-dataset comparison (A vs B)
│   ├── ablation_study.ipynb        # Ablation study (Full → Top-5)
│   ├── model_performance.ipynb     # Model performance comparison
│   ├── testing.ipynb               # File test awal
├── aws/
│   ├── 01-network.yaml             # CloudFormation: VPC + Subnet + Endpoints
│   ├── 02-instances.yaml           # CloudFormation: 3 EC2 instances
│   ├── 03-detection-pipeline.yaml  # CloudFormation: S3 + Lambda + SNS
│   ├── 04-nat-gateway.yaml         # CloudFormation: Temporary NAT
│   ├── flow_extractor.py           # Analyzer: capture + extract + XGBoost predict + SNS alert
│   ├── lambda/
│   │   └── index.py                # Lambda code (backup, tidak digunakan)
│   ├── DEPLOY_GUIDE.md             # Panduan deployment
│   └── README.md                   # AWS overview
├── hero.tex                         # Paper dengan data fiktif (paper1)
├── hero2.tex                        # Paper dengan data real (paper2)
├── presentasi.md                    # Outline presentasi 20 slide
├── DOCUMENTATION.md                 # File ini
└── README.md
```

---

## 3. Hasil Training (Notebook)

### Dataset A: SSH-Bruteforce.csv (binary: SSH vs Benign)
- Samples: 625,919 (438,330 Benign + 187,589 SSH-Bruteforce)
- Balanced ke 375,178 (undersampling)
- Fitur: 78 numerik
- F1-Score (5-fold CV): XGBoost=100%, RF=100%, SVM=99.99%

### Dataset B: Wednesday-14-02-2018 (SSH vs Non-SSH incl. FTP)
- Samples: 1,048,575 (667,626 Benign + 193,360 FTP + 187,589 SSH)
- Balanced ke 375,178
- Encoding: SSH=1, sisanya (Benign+FTP)=0
- F1-Score (5-fold CV): XGBoost=99.99%, RF=99.99%, SVM=99.99%

### Top-10 Feature Importance (XGBoost Gain)

| Rank | Feature | Description |
|------|---------|-------------|
| 1 | Dst Port | Destination port |
| 2 | Init Bwd Win Byts | Initial TCP backward window size |
| 3 | Fwd Seg Size Min | Minimum segment size forward |
| 4 | Flow Pkts/s | Packet rate per second |
| 5 | Flow Duration | Total flow duration |
| 6 | Fwd Header Len | Total forward header bytes |
| 7 | Bwd Header Len | Total backward header bytes |
| 8 | Bwd IAT Min | Min inter-arrival time backward |
| 9 | Init Fwd Win Byts | Initial TCP forward window size |
| 10 | ACK Flag Cnt | Count of ACK flags |

**Feature overlap dengan prior work:** Hanya 3/10 (Dst Port, Flow Pkts/s, Init Fwd Win Byts)

---

## 4. Ablation Study

| Config | Dataset A F1% | Dataset B F1% | Inference Time (ms) | Model Size (KB) |
|--------|---------------|---------------|---------------------|-----------------|
| Full (78) | 100.00 | 99.99 | 75.5 | 80 |
| Top-30 | 100.00 | 99.99 | 44.1 | 79 |
| Top-20 | 100.00 | 99.99 | 44.3 | 79 |
| Top-10 | 100.00 | 99.99 | 42.6 | 86 |
| Top-5 | 100.00 | 99.99 | 40.8 | 92 |

**Kesimpulan:** Tidak ada degradasi bahkan di Top-5. Dataset terlalu "mudah".

---

## 5. Efficiency Comparison (Top-10 Features)

| Model | F1-Score | Model Size | Inference Time |
|-------|----------|------------|----------------|
| XGBoost | 100.00% | 84 KB | 45 ms |
| Random Forest | 100.00% | 0.3 MB | 282 ms |
| SVM (RBF) | 99.99% | 4.8 MB | 1,594 ms |

XGBoost optimal untuk deployment: terkecil dan tercepat.

---

## 6. AWS Infrastructure

### Arsitektur

```
Attacker (Hydra/Nmap)
    → Target Server (port 22)
        → Traffic Mirror (VXLAN, UDP 4789)
            → Analyzer Node:
                tcpdump → parse flows → extract 10 features
                → XGBoost predict → SNS alert (if attack)
                                   → save results ke S3
```

### Komponen

| Resource | Keterangan |
|----------|-----------|
| VPC | 10.0.0.0/16, private subnet 10.0.1.0/24 |
| Target Server | t3.micro, 10.0.1.38, SSH enabled |
| Analyzer Node | t3.medium, 10.0.1.45, XGBoost + tcpdump |
| Attacker Node | t3.micro, 10.0.1.183, Hydra + Nmap |
| S3 Bucket | ssh-detection-features-232032302717 |
| SNS | ssh-detection-alerts → heroyudo@gmail.com |
| Traffic Mirror | TCP port 22, VXLAN to Analyzer ENI |
| Region | ap-southeast-1 (Singapore) |

### Instance IDs
- Target: i-0a3ed2fd3f0e72492
- Analyzer: i-0d48771e71a679289
- Attacker: i-078691dbf75a3f4c8

### Software Stack (Analyzer)
- Amazon Linux 2023
- Python 3.9.25
- XGBoost 2.1.4
- Model: xgboost_model.json (84 KB)

---

## 7. Live Testing dengan XGBoost Model

### Hasil Per Capture Window (Hydra Attack Test)

| Window | Flows | Attacks | Benign | Status |
|--------|-------|---------|--------|--------|
| 1 (pre-attack) | 5 | 0 | 5 | ✅ Correct (no attack) |
| 2 (during Hydra) | 17 | 10 | 7 | ✅ Attack detected |
| 3 (during Hydra) | 15 | 8 | 7 | ✅ Attack detected |
| 4 (during Hydra) | 13 | 8 | 5 | ✅ Attack detected |
| 5 (during Hydra) | 15 | 8 | 7 | ✅ Attack detected |
| 6 (post-attack) | 5 | 0 | 5 | ✅ Correct (attack ended) |

### Analisis
- **XGBoost model berhasil membedakan attack vs benign secara per-flow**
- Sebelum attack: semua flow diklasifikasi benign ✅
- Saat Hydra berjalan: majority flow terdeteksi sebagai attack ✅
- Setelah attack selesai: kembali ke benign ✅
- **Tidak ada false positive pada traffic normal** (berbeda dengan rule-based sebelumnya!)
- Results tersimpan di S3: `s3://ssh-detection-features-232032302717/results/`

### Perbandingan: Rule-Based vs XGBoost

| Skenario | Rule-Based (sebelum) | XGBoost (sekarang) |
|----------|---------------------|-------------------|
| Normal SSH | Attack (FP) ❌ | Benign ✅ |
| Hydra attack | Attack ✅ | Attack ✅ |
| Post-attack | Benign ✅ | Benign ✅ |

---

## 8. Cost Analysis

| Component | Assumption | Monthly cost |
|-----------|-----------|-------------|
| Traffic Mirroring | 1 ENI × 730 hours | $10.95 |
| Analyzer EC2 | t3.medium × 730 hours | $30.37 |
| S3 storage | < 1 GB/month | $0.02 |
| VPC Endpoints (SSM) | 3 endpoints × 730 hours | $21.90 |
| SNS alert | < 1,000 notifications | $0.00 |
| **Total** | | **$63.26** |
| **Without VPC Endpoints** | | **$41.36** |

Lambda tidak digunakan → biaya Lambda = $0.

---

## 9. CloudFormation Stacks

### Create Order
```cmd
aws cloudformation create-stack --stack-name ssh-detection-network --template-body file://aws/01-network.yaml --region ap-southeast-1
aws cloudformation create-stack --stack-name ssh-detection-instances --template-body file://aws/02-instances.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation create-stack --stack-name ssh-detection-pipeline --template-body file://aws/03-detection-pipeline.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
```

### Start/Stop Instances
```cmd
aws ec2 start-instances --instance-ids i-078691dbf75a3f4c8 i-0d48771e71a679289 i-0a3ed2fd3f0e72492 --region ap-southeast-1
aws ec2 stop-instances --instance-ids i-078691dbf75a3f4c8 i-0d48771e71a679289 i-0a3ed2fd3f0e72492 --region ap-southeast-1
```

### NAT Gateway (temporary)
```cmd
aws cloudformation create-stack --stack-name ssh-detection-nat --template-body file://aws/04-nat-gateway.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation delete-stack --stack-name ssh-detection-nat --region ap-southeast-1
```

---

## 10. Akses EC2 via SSM
```cmd
aws ssm start-session --target i-0d48771e71a679289 --region ap-southeast-1  # Analyzer
aws ssm start-session --target i-078691dbf75a3f4c8 --region ap-southeast-1  # Attacker
aws ssm start-session --target i-0a3ed2fd3f0e72492 --region ap-southeast-1  # Target
```

---

## 11. Menjalankan Detector

Di Analyzer Node (via SSM):
```bash
sudo python3 -u /home/ssm-user/flow_extractor.py
```

Script ini akan:
1. Capture traffic 60 detik per window (tcpdump, interface ens5)
2. Parse VXLAN packets → extract per-flow features
3. Run XGBoost inference (10 fitur)
4. Kirim SNS alert jika attack terdeteksi
5. Simpan hasil ke S3

---

## 12. Bahan Diskusi

1. **XGBoost model terbukti bekerja di live traffic** — per-flow classification berhasil tanpa false positive
2. **Rule-based vs ML-based** — rule-based (pkts/s > 1.0) menghasilkan FP; XGBoost eliminasi FP karena mempertimbangkan 10 fitur
3. **Dataset sangat mempengaruhi hasil** — raw CSE-CIC-IDS2018 terlalu "mudah" (F1=100%)
4. **Feature importance tidak stabil** — hanya 3/10 overlap dengan prior work
5. **Arsitektur simplified** — inference di Analyzer (tanpa Lambda) lebih praktis dan reliable
6. **tcpdump vs CICFlowMeter** — tcpdump memberikan estimasi fitur, CICFlowMeter exact per-flow

---

## 13. Future Work

- [ ] Per-flow classification menggunakan CICFlowMeter (exact features)
- [ ] Automated Security Group update (block attacker IP)
- [ ] Multi-ENI monitoring
- [ ] Test dengan distributed/low-rate attack patterns
- [ ] Evaluasi di dataset yang lebih menantang
