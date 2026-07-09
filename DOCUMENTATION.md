# SSH Brute-Force Detection — Dokumentasi Lengkap

## Replikasi Paper: "A Feature-Reduced SSH Brute-Force Detection Method Using XGBoost on AWS Infrastructure"

---

## 1. Ringkasan Project

Project ini mereplikasi dan memperluas paper yang mengusulkan sistem deteksi SSH brute-force menggunakan XGBoost yang di-deploy di AWS Lambda. Kami melakukan:

1. Training & benchmarking model ML (notebook)
2. Multi-dataset comparison
3. Deployment end-to-end di AWS (Traffic Mirroring → Analyzer → S3 → Lambda → SNS)
4. Live testing dengan 6 skenario serangan

---

## 2. Struktur File

```
kiro-ssh/
├── notebooks/
│   ├── model_training.ipynb      # Replikasi paper (single dataset)
│   ├── deteksi_ssh.ipynb         # Multi-dataset comparison (A vs B)
│   ├── testing.ipynb             # File test awal
│   ├── SSH-Bruteforce.csv        # Dataset A (625k samples)
│   ├── xgboost_model.json        # Model dari Dataset A
│   └── xgboost_ssh_detector.json # Model dari Dataset B
├── aws/
│   ├── 01-network.yaml           # CloudFormation: VPC + Subnet + Endpoints
│   ├── 02-instances.yaml         # CloudFormation: 3 EC2 instances
│   ├── 03-detection-pipeline.yaml # CloudFormation: S3 + Lambda + SNS
│   ├── 04-nat-gateway.yaml       # CloudFormation: Temporary NAT
│   ├── lambda/
│   │   └── index.py              # Lambda inference code
│   ├── flow_extractor.py         # Analyzer: capture + extract + upload
│   ├── lambda_code.zip           # Lambda deployment package
│   └── README.md                 # AWS deployment guide
├── Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv  # Dataset B
├── .gitignore
└── README.md
```

---

## 3. Hasil Training (Notebook)

### Dataset A: SSH-Bruteforce.csv (binary: SSH vs Benign)
- Samples: 625,919 → balanced ke 375,178
- F1-Score (5-fold CV): XGBoost=100%, RF=100%, SVM=99.99%

### Dataset B: Wednesday-14-02-2018 (SSH vs Non-SSH incl. FTP)
- Samples: 1,048,575 → balanced ke 375,178
- Lebih menantang karena model harus membedakan SSH attack dari FTP attack

### Perbandingan dengan Paper
| Metric | Paper | Kita (Dataset A) |
|--------|-------|-----------------|
| XGBoost F1 | 99.85% | 100% |
| RF F1 | 99.70% | 100% |
| SVM F1 | 94.14% | 99.99% |
| Model Size | 145 KB | 84 KB |

### Perbedaan Utama
- Dataset berbeda (paper: 380k balanced curated; kita: 625k raw undersampled)
- Versi XGBoost berbeda (paper: 1.7.5; kita: 3.2.0)
- Top-10 fitur overlap hanya 3/10

---

## 4. AWS Infrastructure

### Komponen
| Resource | Keterangan |
|----------|-----------|
| VPC | 10.0.0.0/16, private subnet 10.0.1.0/24 |
| Target Server | t3.micro, 10.0.1.38, SSH enabled |
| Analyzer Node | t3.medium, 10.0.1.45, tcpdump + Python |
| Attacker Node | t3.micro, 10.0.1.183, Hydra + Nmap |
| S3 Bucket | ssh-detection-features-232032302717 |
| Lambda | ssh-detection-inference (rules-based) |
| SNS | ssh-detection-alerts → heroyudo@gmail.com |
| Traffic Mirror | TCP port 22, VXLAN to Analyzer |

### Instance IDs
- Target: i-0a3ed2fd3f0e72492
- Analyzer: i-0d48771e71a679289
- Attacker: i-078691dbf75a3f4c8

### ENI IDs
- Target: eni-04d92f77e57f2d86b
- Analyzer: eni-0103e68743773555c
- Attacker: eni-0329eeb620ac8da36

### Traffic Mirror IDs
- Filter: tmf-03f4b7e4510521d7a
- Target: tmt-025232c66c0795b03
- Session: tms-0892d6aed0adf83f0

---

## 5. Hasil Live AWS Testing

### Pipeline Flow
```
Attacker (Hydra/SSH/Nmap)
    → Target Server (port 22)
        → Traffic Mirror (VXLAN, UDP 4789)
            → Analyzer (tcpdump → extract 10 features → CSV)
                → S3 upload
                    → Lambda trigger (predict: attack/benign)
                        → SNS email alert
```

### Hasil Per Skenario

| # | Scenario | SSH Packets | pkts/s | Prediction | Expected | Match |
|---|----------|-------------|--------|------------|----------|-------|
| 1 | Normal SSH (15 logins) | 587 | 2.94 | Attack* | Benign | ❌ FP |
| 2 | Failed login low rate | 251 | 1.67 | Attack* | Benign | ❌ FP |
| 3 | Hydra low-rate (500 attempts) | 1,100 | 3.67 | Attack | Attack | ✅ |
| 4 | Hydra high-rate (500 attempts, 16 threads) | 1,151 | 6.39 | Attack | Attack | ✅ |
| 5 | Nmap scan | 15 | 0.25 | Benign | Suspicious | ✅ |
| 6 | Mixed (normal + brute-force) | 2,067 | 8.61 | Attack | Mixed | ✅ |

*FP = False Positive: rule threshold (pkts/s > 1.0) terlalu sensitif

### Analisis
- **True detection rate (attack scenarios):** 100% (3/3 + mixed)
- **False Positive rate:** 2/6 scenarios (Normal SSH & Failed login)
- **Nmap correctly treated as benign** (sesuai paper: out-of-scope for SSH brute-force)
- **Root cause FP:** Rule-based threshold terlalu sederhana. Model XGBoost asli (10 fitur) akan lebih akurat karena mempertimbangkan kombinasi fitur, bukan hanya pkts/s.

---

## 6. Perbandingan dengan Paper (Table VI)

| Scenario | Paper Detection Rate | Kita |
|----------|---------------------|------|
| Normal SSH | N/A (no alert) | Alert (FP) |
| Failed login | N/A (no alert) | Alert (FP) |
| Hydra low-rate | 99.4% | 100% detected |
| Hydra high-rate | 99.8% | 100% detected |
| Nmap scan | N/A (benign) | No alert ✅ |
| Mixed traffic | 99.6% | Detected ✅ |

---

## 7. CloudFormation Stacks

### Create Order
```cmd
aws cloudformation create-stack --stack-name ssh-detection-network --template-body file://aws/01-network.yaml --region ap-southeast-1
aws cloudformation create-stack --stack-name ssh-detection-instances --template-body file://aws/02-instances.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation create-stack --stack-name ssh-detection-pipeline --template-body file://aws/03-detection-pipeline.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
```

### Delete Order (reverse)
```cmd
aws cloudformation delete-stack --stack-name ssh-detection-pipeline --region ap-southeast-1
aws cloudformation delete-stack --stack-name ssh-detection-instances --region ap-southeast-1
aws cloudformation delete-stack --stack-name ssh-detection-network --region ap-southeast-1
```

### Start/Stop Instances
```cmd
aws ec2 start-instances --instance-ids i-078691dbf75a3f4c8 i-0d48771e71a679289 i-0a3ed2fd3f0e72492 --region ap-southeast-1
aws ec2 stop-instances --instance-ids i-078691dbf75a3f4c8 i-0d48771e71a679289 i-0a3ed2fd3f0e72492 --region ap-southeast-1
```

### NAT Gateway (temporary, for installing packages)
```cmd
aws cloudformation create-stack --stack-name ssh-detection-nat --template-body file://aws/04-nat-gateway.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation delete-stack --stack-name ssh-detection-nat --region ap-southeast-1
```

---

## 8. Akses EC2 via SSM
```cmd
aws ssm start-session --target i-0d48771e71a679289 --region ap-southeast-1  # Analyzer
aws ssm start-session --target i-078691dbf75a3f4c8 --region ap-southeast-1  # Attacker
aws ssm start-session --target i-0a3ed2fd3f0e72492 --region ap-southeast-1  # Target
```

---

## 9. Bahan Diskusi Kelompok

1. **Dataset sangat mempengaruhi hasil** — dataset kita (raw) vs paper (curated) menghasilkan fitur dan performa berbeda
2. **Feature importance tidak stabil** — hanya 3/10 overlap antara kita dan paper
3. **Rule-based vs ML-based** — threshold sederhana menghasilkan False Positives pada traffic normal
4. **Arsitektur paper terbukti bekerja** — end-to-end pipeline berhasil dari capture hingga alert
5. **Trade-off cost vs accuracy** — EC2 analyzer adalah bottleneck biaya (~$30/bulan)
6. **Reproducibility challenge** — paper tidak menyediakan dataset exact, membuat replikasi persis sulit

---

## 10. Future Work

- [ ] Update Lambda dengan XGBoost model sesungguhnya (via Lambda Layer)
- [ ] Per-flow classification (bukan aggregated)
- [ ] Tuning threshold untuk reduce False Positives
- [ ] Automated Security Group update (block attacker IP)
- [ ] Multi-ENI monitoring
