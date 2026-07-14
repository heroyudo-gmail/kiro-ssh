# CICDDoS2018 — Dokumentasi Penelitian

## SSH Brute-Force Detection Using Feature-Reduced XGBoost

---

## 1. Ringkasan

Penelitian dedicated menggunakan CSE-CIC-IDS2018 untuk binary classification SSH Brute-Force detection.

---

## 2. Dataset

### Dataset A: SSH-Bruteforce.csv
- Samples: 625,919 (438,330 Benign + 187,589 SSH-Bruteforce)
- Fitur: 78 numerik
- Balanced: 375,178 (undersampling)
- Classification: Binary (SSH attack vs Benign)

### Dataset B: Wednesday-14-02-2018
- Samples: 1,048,575 (667,626 Benign + 193,360 FTP + 187,589 SSH)
- Fitur: 79 (Timestamp di-drop)
- Balanced: 375,178
- Classification: Binary (SSH=1, Non-SSH=0)

---

## 3. Pipeline

```
Notebook 01: EDA & Preprocessing → cleaned_train.pkl, cleaned_test.pkl
Notebook 02: Model Training → xgboost_model.json, feature_importance.csv
Notebook 03: Ablation Study → ablation_results.csv
Notebook 04: Evaluation → metrics, confusion matrix
```

---

## 4. Progress

- [ ] Setup folder & copy dataset
- [ ] Notebook 01 (EDA & Preprocessing)
- [ ] Notebook 02 (Model Training)
- [ ] Notebook 03 (Ablation Study)
- [ ] Notebook 04 (Evaluation)

---

## 5. Hasil (akan diisi setelah eksperimen)

(belum dijalankan)
