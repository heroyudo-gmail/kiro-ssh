# Multi-Class DDoS Detection Using XGBoost

## Penelitian Lanjutan dari SSH Brute-Force Detection

### Tujuan
Meningkatkan dari binary classification (SSH attack vs Benign) menjadi **multiclass classification** yang mampu mendeteksi dan mengklasifikasi berbagai jenis serangan DDoS.

### Dataset
**CICDDoS2019** — Canadian Institute for Cybersecurity
- URL: https://www.unb.ca/cic/datasets/ddos-2019.html
- 13 jenis DDoS attack + Benign
- 87 fitur (CICFlowMeter generated)
- Training day + Testing day

### Jenis Attack dalam Dataset

| # | Attack Type | Protocol |
|---|-------------|----------|
| 1 | DNS | UDP |
| 2 | LDAP | UDP |
| 3 | MSSQL | UDP |
| 4 | NetBIOS | UDP |
| 5 | NTP | UDP |
| 6 | SNMP | UDP |
| 7 | SSDP | UDP |
| 8 | UDP | UDP |
| 9 | UDP-Lag | UDP |
| 10 | SYN | TCP |
| 11 | TFTP | UDP |
| 12 | WebDDoS | TCP |
| 13 | Portmap | UDP |

### Pendekatan
- Model: XGBoost (`multi:softmax`, num_class=14)
- Feature reduction: Top-N features via gain importance
- Comparison: XGBoost vs Random Forest vs LightGBM
- Deployment: Same AWS architecture (Traffic Mirror + Analyzer)

### Struktur Folder

```
CICDDoS2019/
├── notebooks/
│   ├── 01_data_exploration.ipynb    # EDA dataset
│   ├── 02_preprocessing.ipynb       # Cleaning, balancing, encoding
│   ├── 03_model_training.ipynb      # Multiclass training + CV
│   ├── 04_feature_selection.ipynb   # Top-N feature analysis
│   ├── 05_ablation_study.ipynb      # Feature reduction impact
│   └── 06_evaluation.ipynb          # Confusion matrix, per-class metrics
├── models/                          # Trained model files
├── data/                            # Dataset (gitignored)
├── aws/                             # AWS deployment scripts
├── paper/                           # Paper .tex files
├── README.md                        # File ini
└── DOCUMENTATION.md                 # Dokumentasi lengkap
```

### Langkah-Langkah Penelitian

1. [ ] Download dataset CICDDoS2019
2. [ ] Exploratory Data Analysis (EDA)
3. [ ] Preprocessing (cleaning, encoding, balancing)
4. [ ] Baseline training (all features, multiclass)
5. [ ] Feature importance & selection (Top-10, Top-15, Top-20)
6. [ ] Ablation study
7. [ ] Model comparison (XGBoost vs RF vs LightGBM)
8. [ ] Deploy ke AWS (update flow_extractor untuk multi-class)
9. [ ] Live testing dengan berbagai jenis DDoS simulasi
10. [ ] Paper writing

### Perbedaan dengan Penelitian Sebelumnya

| Aspek | SSH (sebelum) | DDoS (ini) |
|-------|---------------|------------|
| Classification | Binary (attack/benign) | Multiclass (14 classes) |
| Dataset | CSE-CIC-IDS2018 (625K) | CICDDoS2019 (50M+) |
| Attack types | 1 (SSH brute-force) | 13 DDoS variants |
| Challenge | Terlalu mudah (F1=100%) | Lebih menantang |
| Model output | 0/1 | Class label (0-13) |
