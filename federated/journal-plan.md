# Rencana Jurnal SINTA 1 (IJCITSM) — Extended dari ISRITI

> Dokumen kerja internal. Peta dari konferensi ISRITI (sudah "accepted + presented")
> ke jurnal IJCITSM (SINTA 1). Tujuannya memastikan material jurnal **>50% baru**
> dan kontribusinya berbeda substansial, bukan sekadar menambah halaman.

## 1. Target jurnal

- **IJCITSM** — International Journal of Cyber and IT Service Management.
- SINTA 1 (akreditasi 2024). Open access, Bahasa Inggris, double-blind.
- Indeks: SINTA, Garuda, Crossref, Google Scholar, Dimensions; sedang evaluasi Scopus/DOAJ/EBSCO.
- Terbit 2×/tahun (April & Oktober).
- Scope condong ke **cyber & IT service management** → framing paper menonjolkan sisi
  *federated security monitoring as a cloud service*: deployment, biaya, protokol, reproducibility,
  bukan hanya angka ML.

## 2. Positioning (Plan B — empirical/measurement-heavy)

Review tematik tetap ada sebagai latar, tetapi **inti kebaruan** = verifikasi empiris
lintas-dataset + robustness adversarial yang **diperbesar skalanya** dan **dijawab
pertanyaan terbukanya**.

Judul usulan (sementara):
> "Scaling Reproducible Federated Intrusion Detection Across Network Domains:
> A Leakage-Free Evaluation Protocol and Adversarial Robustness Study on a Cloud Testbed"

Angle pembeda utama vs ISRITI:
1. **Gradasi jarak domain** — near-domain (CICFlowMeter 2017↔2018, fitur penuh) vs
   cross-domain (+UNSW, 9 fitur irisan). ISRITI hanya punya cross-domain.
2. **Protokol evaluasi bebas-kebocoran** dinaikkan dari "temuan" (ISRITI) jadi
   **kontribusi**: usulan + guideline + uji.
3. **Menjawab pertanyaan terbuka ISRITI**: penyebab degradasi UNSW pada adversarial
   training (ISRITI menulis "we did not investigate its cause").

## 3. Batas maksimal ISRITI (sudah "terpakai", jadi di jurnal hanya dirangkum)

| Aspek | ISRITI (plafon) |
|---|---|
| Panjang | 6 halaman IEEEtran |
| Dataset | 2 (CSE-CIC-IDS2018, UNSW-NB15) |
| Client | 2 |
| Fitur | 9 (irisan CICFlowMeter∩Argus/Bro) |
| Agregasi | FedAvg (+FedProx sbg pembanding R1) |
| Eksperimen | R1–R6 (FedAvg/FedProx, non-IID, cross-dataset, biaya, evasion, adv-training) |
| Evasion | FGSM/PGD/JSMA, 4 titik ε {0.05,0.1,0.2,0.5} |
| Statistik | 3 & 5 seed, CI95, Welch, paired-t |
| Referensi | 30 |
| Gambar/tabel | 3 gambar, 4 tabel |

## 4. Peta "SUDAH di ISRITI" vs "BARU di jurnal"

| Komponen | ISRITI | Jurnal (baru?) |
|---|---|---|
| Review tematik 4 tema | ✓ | Dirangkum + diperdalam, refs 50–70 |
| Testbed AWS 3×EC2 | ✓ | Dipakai ulang + skala client naik |
| Cross-domain 9 fitur (2018+UNSW) | ✓ | Dirangkum sbg baseline |
| **Near-domain 2017↔2018 (76 fitur)** | ✗ | **BARU — Konfig A** |
| **Gradasi jarak domain (near vs far)** | ✗ | **BARU — narasi utama** |
| **Protokol evaluasi bebas-kebocoran (sbg kontribusi)** | sbg temuan | **BARU — diformalkan + guideline** |
| **Kurva ε penuh + analisis per-fitur evasion** | 4 titik | **BARU — kurva halus** |
| **Investigasi penyebab degradasi UNSW (adv-train)** | ✗ | **BARU** |
| **Agregasi robust (mis. multi-Krum) / dimensi Byzantine** | ✗ | **BARU (opsional tahap-1)** |
| Statistik lebih dalam (effect size, koreksi multiple-comp) | dasar | **BARU** |
| Fondasi FL single-dataset (01_belajar) | ✗ | **BARU — pelengkap** |

Target: baris "BARU" ≥ 50% bobot paper.

## 5. Desain eksperimen (Opsi 2 — dikunci)

### Konfig A — near-domain (BARU)
- Client: **Client-CIC2017 + Client-CIC2018**.
- Ruang fitur: **irisan penuh CICFlowMeter** (~76 fitur, dari Paper 4 XAI).
- Tujuan: menguji FL saat domain *dekat* (ekstraktor sama). Hipotesis: gap kecil,
  FL ≈ centralized, non-IID efeknya ringan.

### Konfig B — cross-domain (dirangkum dari ISRITI)
- Client: **+Client-UNSW**, ruang **9 fitur irisan**.
- Dipakai sebagai pembanding "far-domain". Angka sebagian besar sudah ada.

Narasi: "seberapa jauh FL-NIDS bertahan saat domain makin jauh — near (76 fitur) → far (9 fitur)".

## 6. Aset yang SUDAH siap (hasil cek kode)

- **Dataset 2017 & 2018 di S3**: `s3://ssh-detection-features-232032302717/datasets/CICD2017/`
  dan `.../CICD2018/` (CSV CICFlowMeter; ada auto-sync + auto-unzip).
- **Loader + kamus ALIAS kolom 2018↔2017**, `norm_colname`, `find_label_col`,
  `to_binary` (Benign/normal→0, lainnya→1) — dari `unswnb-15/notebook_xai/01_preprocessing.ipynb`.
  Irisan 2017∩2018 ≈ 76 fitur (terverifikasi di Paper 4).
- **Testbed FL**: `federated/aws/run_survey_blockB.py` + `fed-vpc-3ec2-public.yaml` + `fed_node_survey.py`.
- **Notebook survei cross-domain**: `federated/notebooks/02_survey-tanpaSFM/` (s01..s15).
- **Jalur FL single-dataset (fondasi)**: `federated/notebooks/01_belajar-fl-tanpaSFM/`.

## 7. Notebook/skrip BARU yang perlu disiapkan (alur SageMaker)

> Semua self-contained, headless-ready, output ke `artifacts/`, angka dari eksekusi nyata.

1. `jA_01_partition_neardomain.ipynb` — partisi 2017 & 2018 ke ruang 76-fitur, tulis ke
   S3 `federated_journal/neardomain/`. Reuse loader Paper 4.
2. `jA_02_fed_neardomain_sim.ipynb` — FL 2-client near-domain, 100 ronde, 5 seed,
   **SIMULASI penuh di kernel SageMaker** (Opsi B). Alasan: role SageMaker tak punya
   izin `cloudformation:CreateStack`/`DeleteStack`, jadi jalur EC2 (CloudFormation+SSM)
   tidak bisa dipakai dari SageMaker. Matematika FedAvg/z-score/MLP identik dgn node EC2.
   Near-domain ditulis sbg *simulasi FL terkontrol* (sama status R1/R2 ISRITI); bukti
   deployment cloud nyata tetap dipegang jalur cross-domain (ISRITI R3/R5/R6).
   Output R3-near (MCC per client + union, fed vs centralized vs local-only) ke S3.
3. `jA_03_noniid_neardomain.ipynb` — sweep Dirichlet α near-domain (R2-near).
4. `jB_01_epsilon_curve.ipynb` — kurva ε halus (mis. 0.01..0.5, ~10 titik) FGSM/PGD/JSMA
   untuk near & far + **analisis per-fitur** (fitur mana paling rentan).
5. `jB_02_unsw_degradation.ipynb` — investigasi penyebab degradasi UNSW pada adv-training
   (distribusi fitur, decision boundary, recall collapse). Menjawab pertanyaan terbuka ISRITI.
6. `jS_stats.ipynb` — statistik lanjutan: effect size, koreksi multiple-comparison, uji non-parametrik.
7. (opsional tahap-1) `jB_03_robust_agg.ipynb` — multi-Krum / robust aggregation (dimensi Byzantine).

## 8. Struktur section jurnal (target)

1. Introduction (roadmap + kontribusi diperjelas)
2. Related Work / Thematic Review (diperdalam, refs 50–70)
3. Threat Model & Problem Setup
4. Leakage-Free Evaluation Protocol  ← kontribusi
5. Experimental Setup (near & far, testbed, dataset)
6. Results
   - 6.1 Near-domain FL (BARU)
   - 6.2 Cross-domain FL (rangkum ISRITI)
   - 6.3 Domain-distance gradient (BARU)
   - 6.4 Evasion: full ε curve + per-feature (BARU)
   - 6.5 Adversarial training + UNSW degradation cause (BARU)
   - 6.6 Cloud cost
7. Discussion & Research Agenda
8. Threats to Validity
9. Conclusion

## 9. Urutan run di AWS (tahap-1)

1. Partisi near-domain (SageMaker notebook jA_01) → S3.
2. FL near-domain 5 seed (EC2 via run_survey_blockB extend) → S3.
3. non-IID near-domain (SageMaker) → S3.
4. Kurva ε + per-fitur (SageMaker, offline atas model terlatih) → S3.
5. Investigasi UNSW (SageMaker, offline) → S3.
6. Statistik lanjutan (SageMaker/lokal atas CSV) → S3.
7. Teardown stack tiap sesi (WAJIB).

## 10. Konfirmasi yang masih terbuka

- Nama folder di SageMaker (`cicddos2017`) vs path S3 (`datasets/CICD2017/`) — pastikan
  isinya CIC-IDS2017 CICFlowMeter, BUKAN CIC-DDoS2019.
- Apakah dimensi Byzantine (multi-Krum) masuk tahap-1 atau disimpan untuk revisi.
- Judul final & apakah IoT disinggung sebagai future work (karena tahap-1 belum pakai IoT).
