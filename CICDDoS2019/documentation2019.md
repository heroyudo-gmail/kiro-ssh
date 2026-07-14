# CICDDoS2019 — Dokumentasi Penelitian

## Multi-Class DDoS Detection Using Feature-Reduced XGBoost on AWS Infrastructure

---

## 1. Ringkasan

Penelitian lanjutan dari SSH Brute-Force Detection. Meningkatkan dari binary classification (attack/benign) menjadi multiclass classification yang mampu mendeteksi dan mengklasifikasi berbagai jenis serangan DDoS.

---

## 2. Dataset: CICDDoS2019

**Sumber:** Canadian Institute for Cybersecurity, University of New Brunswick
**URL:** https://www.unb.ca/cic/datasets/ddos-2019.html

### Training Day (01-12, 12 Januari 2019)

| # | File | Jenis Attack |
|---|------|-------------|
| 1 | DrDoS_DNS.csv | DNS Reflection/Amplification |
| 2 | DrDoS_LDAP.csv | LDAP Reflection |
| 3 | DrDoS_MSSQL.csv | MSSQL Reflection |
| 4 | DrDoS_NetBIOS.csv | NetBIOS Reflection |
| 5 | DrDoS_NTP.csv | NTP Reflection |
| 6 | DrDoS_SNMP.csv | SNMP Reflection |
| 7 | DrDoS_SSDP.csv | SSDP Reflection |
| 8 | DrDoS_UDP.csv | UDP Flood |
| 9 | Syn.csv | SYN Flood |
| 10 | TFTP.csv | TFTP Reflection |
| 11 | UDPLag.csv | UDP Lag |

### Testing Day (03-11, 11 Maret 2019)

| # | File | Jenis Attack |
|---|------|-------------|
| 1 | LDAP.csv | LDAP Reflection |
| 2 | MSSQL.csv | MSSQL Reflection |
| 3 | NetBIOS.csv | NetBIOS Reflection |
| 4 | Portmap.csv | Portmap Reflection |
| 5 | Syn.csv | SYN Flood |
| 6 | UDP.csv | UDP Flood |
| 7 | UDPLag.csv | UDP Lag |

### Catatan
- Training Day: 11 file, 12 jenis attack + Benign
- Testing Day: 7 file, 7 jenis attack + Benign (subset)
- Portmap ada di Testing tapi TIDAK di Training
- DNS, NTP, SNMP, SSDP, TFTP ada di Training tapi TIDAK di Testing
- Fitur: 87 kolom (CICFlowMeter generated) + 1 kolom Label

---

## 3. Metodologi

### Pipeline Notebook

```
Notebook 1 (01_eda_preprocessing.ipynb)
  → Load semua CSV
  → EDA (distribusi, ukuran, tipe data)
  → Cleaning (NaN, Inf, non-numeric, Timestamp)
  → Standardize labels (hapus prefix DrDoS_, uppercase)
  → Balancing (undersample majority classes)
  → Output: cleaned_train.pkl, cleaned_test.pkl

Notebook 2 (02_model_training.ipynb)
  → Load cleaned_train.pkl
  → Train XGBoost multiclass (multi:softmax)
  → Train Random Forest & LightGBM
  → 5-fold Cross-Validation
  → Feature Importance (XGBoost gain)
  → Output: xgboost_model.json, feature_importance.csv

Notebook 3 (03_ablation_study.ipynb)
  → Load cleaned_train.pkl + model
  → Ablation: Full → Top-30 → Top-20 → Top-10 → Top-5
  → Compare F1 per konfigurasi
  → Output: ablation_results.csv

Notebook 4 (04_evaluation.ipynb)
  → Load cleaned_test.pkl + model
  → Predict pada Testing Day data
  → Confusion Matrix
  → Per-class Precision, Recall, F1
  → Overall Accuracy
  → Output: evaluation metrics + plots
```

### Hyperparameters

- **XGBoost:** objective='multi:softmax', num_class=N, max_depth=6, learning_rate=0.3, n_estimators=100
- **Random Forest:** n_estimators=100
- **LightGBM:** objective='multiclass', num_class=N, n_estimators=100

---

## 4. Struktur File

```
CICDDoS2019/
├── data/
│   ├── CIC-DDoS2019-Dataset/
│   │   ├── 01-12/          (Training Day - 11 CSV files)
│   │   └── 03-11/          (Testing Day - 7 CSV files)
│   ├── cleaned_train.pkl   (output notebook 1)
│   ├── cleaned_test.pkl    (output notebook 1)
│   └── train_distribution.png
├── notebooks/
│   ├── 01_eda_preprocessing.ipynb
│   ├── 02_model_training.ipynb      (belum dibuat)
│   ├── 03_ablation_study.ipynb      (belum dibuat)
│   └── 04_evaluation.ipynb          (belum dibuat)
├── models/
│   └── (akan berisi model .json setelah training)
├── documentation2019.md    (file ini)
└── README.md
```

---

## 5. Progress

- [x] Setup folder & struktur
- [x] Download dataset CICDDoS2019
- [x] Buat notebook 01 (EDA & Preprocessing)
- [ ] Jalankan notebook 01
- [ ] Buat & jalankan notebook 02 (Model Training)
- [ ] Buat & jalankan notebook 03 (Ablation Study)
- [ ] Buat & jalankan notebook 04 (Evaluation)
- [ ] Deploy model ke AWS Analyzer
- [ ] Live testing dengan DDoS tools
- [ ] Tulis paper

---

## 6. Hasil (akan diisi setelah eksperimen)

### EDA
- Total samples Training: (belum dijalankan)
- Total samples Testing: (belum dijalankan)
- Jumlah fitur: (belum dijalankan)
- Jumlah class: (belum dijalankan)

### Model Performance
- (belum dijalankan)

### Ablation Study
- (belum dijalankan)

### Testing Day Evaluation
- (belum dijalankan)

---

## 7. Catatan Penting

1. **Portmap** ada di Testing tapi tidak di Training — model tidak akan bisa klasifikasi ini dengan benar (unknown class). Perlu strategi: skip, atau train sebagai "OTHER".
2. Dataset sangat besar — perlu sampling/balancing agresif agar muat di RAM.
3. Label naming berbeda antara Training ("DrDoS_DNS") dan Testing ("DNS") — perlu standardisasi.
4. Fitur sama dengan CICFlowMeter output — compatible dengan arsitektur AWS yang sudah ada.
