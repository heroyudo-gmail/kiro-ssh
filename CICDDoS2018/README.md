# CICDDoS2018 — SSH Brute-Force Detection (Dedicated)

## Penelitian khusus dataset CSE-CIC-IDS2018

### Tujuan
Folder ini berisi percobaan dedicated menggunakan dataset CSE-CIC-IDS2018 untuk deteksi SSH Brute-Force. Sama dengan penelitian utama di root folder, tapi lebih terstruktur.

### Dataset
- **Dataset A:** SSH-Bruteforce.csv (625,919 samples) — binary: SSH vs Benign
- **Dataset B:** Wednesday-14-02-2018 (1,048,575 samples) — SSH vs Non-SSH (incl. FTP)

### Struktur Folder

```
CICDDoS2018/
├── notebooks/
│   ├── 01_eda_preprocessing.ipynb
│   ├── 02_model_training.ipynb
│   ├── 03_ablation_study.ipynb
│   └── 04_evaluation.ipynb
├── models/
├── data/
├── documentation2018.md
└── README.md
```

### Langkah Penelitian

1. [ ] Copy dataset ke folder data/
2. [ ] EDA & Preprocessing
3. [ ] Model Training (XGBoost, RF, SVM)
4. [ ] Ablation Study (Full → Top-5)
5. [ ] Evaluation
6. [ ] Deploy ke AWS
