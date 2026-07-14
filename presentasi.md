# Presentasi: A Feature-Reduced SSH Brute-Force Detection Method Using XGBoost on AWS Infrastructure

---

## Slide 1 — Title

**A Feature-Reduced SSH Brute-Force Detection Method Using XGBoost on AWS Infrastructure**

- Hero Yudo Martono — Dept. Informatics & Computer Engineering
- Reesa Akbar — Electrical Engineering
- Dian Septiani Santoso — Dept. Informatics & Computer Engineering
- Andhik Ampuh Yunanto — Dept. Informatics & Computer Engineering

Politeknik Elektronika Negeri Surabaya

---

## Slide 2 — Latar Belakang

- AWS bisa dijadikan tempat yang tepat untuk melakukan percobaan serangan karena merupakan salah satu cloud provider terbaik
- Server yang terekspos SSH di cloud rentan terhadap brute-force attack
- Ancaman: data breach, unauthorized resource consumption, unexpected cost
- AWS GuardDuty ada, tapi organisasi butuh kontrol penuh atas security logic
- Kebutuhan: model ringan yang bisa di-deploy di serverless (Lambda)


---

## Slide 3 — Rumusan Masalah & Tujuan

**Masalah:**
- Model ML existing (Deep Learning, CNN, LSTM) akurat tapi berat secara komputasi
- Tidak cocok untuk serverless environment (Lambda: batas waktu & memori ketat)
- Evaluasi biasanya hanya pada 1 dataset → generalizability belum teruji

**Tujuan:**
- Membangun model XGBoost yang ringan dengan hanya 10 fitur
- Mengevaluasi di 2 konfigurasi dataset berbeda
- Deploy end-to-end di AWS dan validasi dengan serangan nyata

---

## Slide 4 — Kontribusi

1. Feature-reduced XGBoost pipeline + multi-dataset ablation study
2. Python-based flow extractor sebagai alternatif ringan CICFlowMeter (tanpa Java)
3. Validasi operasional di AWS private subnet testbed (Hydra + Nmap)
4. Live detection: **100% attack detected, 0% false positive**

---

## Slide 5 — Related Work

| Pendekatan | Kelebihan | Kekurangan |
|------------|-----------|------------|
| LSTM/CNN (Deep Learning) | Akurasi tinggi | Berat, lambat, butuh GPU |
| Big Data (Hadoop/Spark) | Skalabel | Infrastruktur mahal |
| Honeypot-based | Data realistis | Tidak real-time |
| Rule-based (GuardDuty) | Mudah deploy | Kurang transparan |
| **XGBoost + Feature Reduction (Ours)** | **Ringan, cepat, akurat** | **Butuh validasi multi-dataset** |

Gap: Belum ada yang mengevaluasi robustness feature selection di multiple dataset configurations

---

## Slide 6 — Dataset

**Dataset A: SSH-Bruteforce.csv**
- 625,919 samples (438,330 Benign + 187,589 SSH-Bruteforce)
- 78 fitur numerik
- Binary classification: SSH attack vs Normal

**Dataset B: Wednesday-14-02-2018**
- 1,048,575 samples (667,626 Benign + 193,360 FTP + 187,589 SSH)
- Lebih menantang: harus bedakan SSH dari FTP brute-force
- SSH = attack (1), sisanya = non-attack (0)

**Preprocessing:**
- Balancing via undersampling → 375,178 samples per dataset
- Stratified 80/20 split + 5-fold cross-validation

---

## Slide 7 — Metodologi: Workflow

**[Tampilkan gambar: alur.png]**

Alur:
1. Dataset acquisition & cleaning
2. Model comparison (XGBoost vs RF vs SVM) — 5-fold CV
3. Feature importance → select Top-10
4. Ablation study (Full → Top-30 → Top-20 → Top-10 → Top-5)
5. Deploy ke AWS architecture
6. Live testing dengan serangan nyata (Hydra + Nmap)

---

## Slide 8 — Feature Selection

**[Tampilkan gambar: rank_fitur.png]**

Top 10 fitur (XGBoost gain importance):
1. Dst Port
2. Init Bwd Win Byts
3. Fwd Seg Size Min
4. Flow Pkts/s
5. Flow Duration
6. Fwd Header Len
7. Bwd Header Len
8. Bwd IAT Min
9. Init Fwd Win Byts
10. ACK Flag Cnt

**Temuan penting:** Hanya 3/10 overlap dengan prior work (dataset & versi XGBoost berbeda)

---

## Slide 9 — Arsitektur AWS

**[Tampilkan gambar: figure1.png]**

Pipeline:
```
Attacker → Target Server (port 22)
    → Traffic Mirror (VXLAN, UDP 4789)
        → Analyzer (tcpdump → extract features → XGBoost predict)
            → SNS email alert (if attack)
            → S3 (save results for audit)
```

Semua dalam Private VPC (10.0.0.0/16), subnet 10.0.1.0/24, tanpa internet gateway.

---

## Slide 10 — Detail Komponen

| Komponen | Spesifikasi | Fungsi |
|----------|-------------|--------|
| Target Server | t3.micro, 10.0.1.38 | SSH server yang diproteksi |
| Analyzer Node | t3.medium, 10.0.1.45 | tcpdump + XGBoost inference |
| Attacker Node | t3.micro, 10.0.1.183 | Hydra 9.5 + Nmap 7.93 |
| S3 Bucket | ssh-detection-features-* | Penyimpanan hasil deteksi |
| SNS | Email notification | Alert ke admin |
| Traffic Mirror | TCP port 22, VXLAN | Copy raw packets |

- XGBoost 2.1.4, Model: 84 KB (JSON)
- Akses via SSM (VPC Endpoints) — tanpa SSH key / public IP

---

## Slide 11 — Skenario Testing

| # | Skenario | Durasi | Expected |
|---|----------|--------|----------|
| 1 | Normal SSH (15 login admin) | 200 sec | Benign |
| 2 | Failed login low rate (2-5 attempts) | 150 sec | Benign |
| 3 | Hydra low-rate (500 attempts) | 300 sec | Attack |
| 4 | Hydra high-rate (500 att, 16 threads) | 180 sec | Attack |
| 5 | Nmap scan (reconnaissance) | 60 sec | Suspicious |
| 6 | Mixed (normal + brute-force) | 240 sec | Mixed |

Semua dilakukan di isolated private subnet, ethical guidelines dipatuhi.

---

## Slide 12 — Hasil: Feature Importance

| Rank | Dataset A (SSH vs Benign) | Dataset B (SSH vs Non-SSH) |
|------|--------------------------|---------------------------|
| 1 | Dst Port | Dst Port |
| 2 | Init Bwd Win Byts | Init Bwd Win Byts |
| 3 | Fwd Seg Size Min | Fwd Seg Size Min |
| 4 | Flow Pkts/s | Flow Pkts/s |
| 5-10 | (sama di kedua dataset) | (sama di kedua dataset) |

**Insight:**
- Ranking konsisten antara Dataset A dan B
- Tapi hanya 3/10 overlap dengan prior work (beda dataset version + XGBoost 3.2.0 vs 1.7.5)
- Feature importance sangat sensitif terhadap preprocessing

---

## Slide 13 — Hasil: Ablation Study

| Feature Set | Dataset A F1% | Dataset B F1% | Time (ms) | Size (KB) |
|-------------|---------------|---------------|-----------|-----------|
| Full (78) | 100.00 | 99.99 | 75.5 | 80 |
| Top-30 | 100.00 | 99.99 | 44.1 | 79 |
| Top-20 | 100.00 | 99.99 | 44.3 | 79 |
| Top-10 | 100.00 | 99.99 | 42.6 | 86 |
| Top-5 | 100.00 | 99.99 | 40.8 | 92 |

**vs Prior work:** Paper lain melaporkan drop di Top-5 (96.40%) — kita tidak mengalami drop.
**Alasan:** Raw CSE-CIC-IDS2018 memiliki pattern yang sangat discriminative.

---

## Slide 14 — Hasil: Model Performance (5-Fold CV)

| Method | Accuracy% | Precision% | Recall% | F1% |
|--------|-----------|-----------|---------|-----|
| XGBoost | 100.00 | 99.99 | 100.00 | 100.00 |
| Random Forest | 100.00 | 100.00 | 100.00 | 100.00 |
| SVM (RBF) | 99.99 | 99.98 | 100.00 | 99.99 |

**Statistik:**
- t-test XGBoost vs RF: t = -1.91, p = 0.129 (tidak signifikan)
- Kesimpulan: dataset composition > algorithm choice

---

## Slide 15 — Hasil: Efficiency Comparison

| Model | F1-score | Model Size | Inference Time |
|-------|----------|-----------|----------------|
| **XGBoost** | **100.00%** | **84 KB** | **45 ms** |
| Random Forest | 100.00% | 0.3 MB | 282 ms |
| SVM | 99.99% | 4.8 MB | 1,594 ms |

**Mengapa XGBoost optimal untuk deployment:**
- Model terkecil (84 KB) — cold start cepat
- Inference tercepat (45 ms) — biaya minimal
- SVM tidak cocok: 1.6 detik inference, model besar

---

## Slide 16 — Hasil: Live Detection (XGBoost Model)

| Window | Flows | Attacks | Benign | Status |
|--------|-------|---------|--------|--------|
| 1 (pre-attack) | 5 | 0 | 5 | ✅ No false positive |
| 2 (Hydra active) | 17 | 10 | 7 | ✅ Attack detected |
| 3 (Hydra active) | 15 | 8 | 7 | ✅ Attack detected |
| 4 (Hydra active) | 13 | 8 | 5 | ✅ Attack detected |
| 5 (Hydra active) | 15 | 8 | 7 | ✅ Attack detected |
| 6 (post-attack) | 5 | 0 | 5 | ✅ Correct — attack ended |

**Detection rate: 100% | False Positive rate: 0%**

**Metrik Live Testing:**
- True Positive Rate (attack scenarios detected): **100%** (4/4 attack windows)
- False Positive Rate (benign flagged as attack): **0%** (0/2 benign windows)
- Scenario-level Accuracy: **100%** (6/6 scenarios correct)
- Per-flow during attack: 34/60 flows classified attack, 26/60 benign (response traffic)

---

## Slide 17 — Perbandingan: Rule-Based vs XGBoost

| Skenario | Rule-Based (threshold) | XGBoost (10 fitur) |
|----------|----------------------|-------------------|
| Normal SSH | ❌ Attack (FP) | ✅ Benign |
| Failed login | ❌ Attack (FP) | ✅ Benign |
| Hydra low-rate | ✅ Attack | ✅ Attack |
| Hydra high-rate | ✅ Attack | ✅ Attack |
| Nmap scan | ✅ Benign | ✅ Benign |
| Mixed traffic | ✅ Attack | ✅ Attack |

**Key insight:** Single-threshold (pkts/s > 1.0) tidak bisa bedakan normal SSH dari brute-force. XGBoost mempertimbangkan 10 fitur secara bersamaan → eliminasi false positive.

---

## Slide 18 — Cost Analysis

| Komponen | Biaya/bulan |
|----------|-------------|
| Traffic Mirroring (1 ENI × 730 hrs) | $10.95 |
| Analyzer EC2 (t3.medium × 730 hrs) | $30.37 |
| S3 storage (< 1 GB) | $0.02 |
| SNS alerts | $0.00 |
| VPC Endpoints (SSM, opsional) | $21.90 |
| **Total** | **$63.26** |
| **Tanpa VPC Endpoints** | **$41.36** |

**Insight:**
- Core cost: EC2 + Traffic Mirroring = $41/bulan
- VPC Endpoints pilihan keamanan (bisa dihilangkan)
- Total operasional sangat terjangkau untuk enterprise security

---

## Slide 19 — Kesimpulan

1. **XGBoost model bekerja di live traffic** — 100% detection rate, 0% false positive
2. **Dataset menentukan segalanya** — raw CSE-CIC-IDS2018 F1 ≥ 99.99% di semua konfigurasi
3. **Feature importance tidak stabil** — hanya 3/10 overlap dengan prior work
4. **XGBoost paling efisien** — 84 KB, 45 ms inference
5. **Arsitektur terbukti viable** — end-to-end pipeline ~$41/bulan

**Threats to Validity:**
- Dataset "terlalu mudah" (pattern sangat jelas)
- tcpdump = estimasi kasar vs CICFlowMeter exact
- Testing di 1 subnet saja

---

## Slide 20 — Future Work & Terima Kasih

**Future Work:**
1. Per-flow classification menggunakan CICFlowMeter → exact feature values
2. Evaluasi dengan distributed/low-rate attack patterns
3. Automated Security Group update → auto-block attacker IP
4. Multi-ENI monitoring → skalabilitas
5. Dataset yang lebih menantang (live production traffic)

**Terima Kasih**

Pertanyaan?

---
