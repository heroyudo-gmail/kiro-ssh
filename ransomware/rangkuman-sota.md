# Rangkuman & Pemetaan State-of-the-Art: Ransomware (dari `ransomware 2.docx` & `ransomware 3.docx`)

Dokumen ini merangkum dua paper survei/review ransomware, lalu memetakannya berdasarkan beberapa fitur agar dapat dibandingkan dan menghasilkan gambaran *state-of-the-art* (SOTA) untuk mendukung penulisan bagian "state of the art" pada paper penelitian.

---

## A. RINGKASAN MASING-MASING DOKUMEN

### Dokumen 1 — `ransomware 2.docx`
**Judul:** *Ransomware Detection, Avoidance, and Mitigation Scheme: A Review and Future Directions*
**Penulis:** Adhirath Kapoor, Ankur Gupta, Rajesh Gupta, Sudeep Tanwar, Gulshan Sharma, Innocent E. Davidson
**Publikasi:** *Sustainability* (MDPI), Vol. 14, 2022. DOI: 10.3390/su14010008
**Jenis:** Review paper.

**Inti:**
- Memperkenalkan **framework DAM (Detection–Avoidance–Mitigation)** — kerangka teoretis untuk mengklasifikasikan teknik, alat, dan strategi mendeteksi, menghindari, dan memitigasi ransomware dalam satu kesatuan.
- Membahas evolusi ransomware (AIDS Trojan 1989 → GPCode → WannaCry, Cerber, Petya → Netwalker, Zeoticus 2.0 yang bisa beroperasi offline tanpa C2 server).
- Sumber infeksi: email attachment, removable media (USB), malvertising, social media/SMS, Ransomware-as-a-Service (RaaS).
- Tipe: Crypto Ransomware vs Locker Ransomware.
- Kontribusi: framework DAM + kontinuum penghindaran (dapat diadopsi organisasi besar hingga kecil) + **studi kasus Djvu ransomware**.
- Statistik: ~51% organisasi global terkena serangan canggih (2020); India paling terdampak (~82%).

**Fokus:** Kerangka klasifikasi konseptual (taksonomi pertahanan) + studi kasus, **bukan** eksperimen kuantitatif.

---

### Dokumen 2 — `ransomware 3.docx`
**Judul:** *Ransomware: Attack Vectors, Detection, and Mitigation — A Comprehensive Survey (2020–2025)* (survei)
**Penulis:** Nazma A. Inamdar (Government Polytechnic Nanded), Manoj Mule (Vishwakarma Institute of Technology, Pune)
**Jenis:** Comprehensive survey (systematic review 50+ artikel, 2020–2025).

**Inti:**
- Metodologi sistematis: pencarian di IEEE, ACM, ScienceDirect, Springer, MDPI, Google Scholar, arXiv → 250+ → 100 (abstrak) → 50+ (full-text).
- **Evolusi 4 fase:** (1) Early 1989–2012 (screen-locker), (2) Crypto-era 2013–2019 (CryptoLocker, WannaCry, NotPetya, Ryuk), (3) Double extortion 2020–2022 (Maze, REvil, DarkSide, Conti), (4) Triple extortion + RaaS 2023–kini (LockBit, BlackCat/ALPHV, Hive, Royal).
- **Statistik:** kerugian global >\$30 miliar (2023, +900% dari 2015); 493 juta serangan (2022); rata-rata tebusan \$2,73 juta (2024); downtime rata-rata 21 hari; healthcare +278% (2020–2023).
- **Vektor serangan:** Phishing/social engineering (34%), RDP exploitation (28%), supply chain (SolarWinds, Kaseya, MOVEit), zero-day.
- **Deteksi:** signature-based, behavior-based, ML/DL (CNN, RNN, LSTM, CNN-LSTM hybrid), hardware-based (HPC), ensemble.
- **Temuan kunci:** ensemble ML mencapai deteksi >99%; multi-layered defense 85–90%; DL 96–99% pada dataset seimbang.
- **Mitigasi:** prevention, detection, response, recovery; backup 3-2-1, immutable/WORM, air-gapped; incident response 6 tahap.

**Fokus:** Survei kuantitatif luas + perbandingan algoritma deteksi + identifikasi research gap & arah masa depan.

---

## B. PEMETAAN LITERATUR (dari literature review Dokumen 2)

Tabel ini memetakan studi-studi yang direview berdasarkan **pendekatan, teknik, metrik, dan kontribusi/keterbatasan**.

| Studi | Kategori | Teknik/Metode | Metrik / Hasil | Catatan Kunci |
|---|---|---|---|---|
| McIntosh et al. | Survei | Review 212 artikel (2020–2023) | — | Gap: riset fokus enkripsi, padahal serangan nyata = double extortion; 73% pakai sampel lama; klaim deteksi tinggi tanpa uji eksternal |
| Al-rimy et al. | Survei + eksperimen | Taksonomi prevention & detection; buat sampel "AESthetic" | Lolos dari 8 antivirus komersial | Klasifikasi: signature/behavior/hybrid |
| Abdullah et al. | Framework | **DAM** (static/dynamic/hybrid + avoidance + mitigation) | — | Studi kasus DJVU (paralel dgn Dokumen 1) |
| Kritika | Survei DL | CNN, RNN, LSTM, CNN-LSTM | Akurasi 96–99% (dataset seimbang) | CNN-LSTM > single-method; transfer learning lintas-famili; kendala data berkualitas, komputasi real-time, black-box |
| Kumar et al. | ML klasik | DT, RF, NB, LR, SVM, KNN, **XGBoost**, MLP + feature selection | **XGBoost 98,9%**; RF cepat & akurat | Reduksi fitur 60% tetap >98%; ensemble > single; fitur statis PE |
| Wang | Hardware-aided | Custom NN + NAS + Hardware Performance Counters (HPC) | 97,8% akurasi, latensi ½ | Deteksi di bawah level OS, sulit di-bypass |
| Liu et al. | Studi empiris | Dataset **MarauderMap** (7.796 sampel, 1,98 TiB, 6 kategori log) | Reduksi deteksi 41–69% tanpa tambah FP | 3 pola enkripsi (in-place, copy-encrypt-delete, shadow-copy-delete); 42% exfiltrasi (~1,2 GB) sebelum enkripsi |
| Lee et al. | ML anti-evasion | Deteksi **Format-Preserving Encryption (FPE)** via metadata & struktur | **KNN 96,3%**; DT & RF >95% | FPE lolos deteksi berbasis entropi → butuh analisis konten |
| Chen et al. | IoT | Taksonomi IoT ransomware + multi-layer (network monitoring, anomaly, blockchain audit) | Algoritma ringan utk perangkat terbatas | IoT = ancaman baru, butuh strategi khusus |
| Nagar | Analisis TTP | Analisis TTP historis → modern | — | Rekomendasi multi-layer defense + incident response + backup |
| Garcia et al. | Threat-led | Pemetaan TTP ke **MITRE ATT&CK** (LockBit, BlackCat, Hive, Conti) | — | Pertahanan spesifik-adversary > generik |
| Wall et al. | Analisis kualitatif | 39 serangan (26 pre- vs 13 mid-pandemi) | — | Pergeseran vektor ke phishing & VPN; data pribadi jadi inti extortion |
| Kim et al. | Real-time detection | **CryptoSniffer** — monitor CPU AES-NI instruction | **95,7%** deteksi real-time; FP 2,3%; overhead <3% | Berhenti setelah 10–15 file (vs 200+ pada sistem konvensional) |
| Thomas et al. | Backup/recovery | Evaluasi strategi backup (3-2-1, immutable WORM, air-gapped) | Recovery sukses 90% tanpa bayar tebusan | Best practice backup |
| Mitchell et al. | Incident response | Framework 6 tahap (prepare, identify, contain, eradicate, recover, lessons) | Recovery 21 hari → 7 hari | Prosedur respons insiden |

---

## C. PEMETAAN BERDASARKAN FITUR (untuk perbandingan SOTA)

### C.1 Berdasarkan pendekatan deteksi

| Pendekatan | Contoh Teknik | Kelebihan | Keterbatasan | Performa Tipikal |
|---|---|---|---|---|
| Signature-based | Hash/pola dikenal | Cepat, FP sangat rendah (<0,1%) | Gagal pada zero-day & polymorphic; perlu update DB | — |
| Behavior-based | Monitoring proses/API/file | Deteksi zero-day & varian tak dikenal; efektif thd polymorphic | FP lebih tinggi; overhead | — |
| ML klasik | RF, XGBoost, SVM, KNN | Akurasi tinggi, interpretable (tree) | Butuh feature engineering; rentan concept drift | XGBoost 98,9%; KNN 96,3% |
| Deep Learning | CNN, LSTM, CNN-LSTM | Akurasi tertinggi pada data seimbang; belajar fitur otomatis | Black-box; butuh data & komputasi besar | 96–99% |
| Ensemble | Kombinasi multi-model | Deteksi >99% | Kompleksitas, latensi | **>99% (SOTA)** |
| Hardware-aided | HPC + NN/NAS | Sulit di-bypass (di bawah OS); latensi rendah | Butuh dukungan hardware khusus | 97,8% |

### C.2 Berdasarkan tahap pertahanan (framework DAM & survei)

| Tahap | Tujuan | Teknik Utama |
|---|---|---|
| **Detection** | Kenali serangan | Signature, behavior, ML/DL, hardware, hash+metadata |
| **Avoidance** | Cegah infeksi | Cyber-hygiene, security awareness, hardening, access control, patching |
| **Mitigation** | Kurangi dampak & pulihkan | Backup (3-2-1, immutable/WORM, air-gapped), incident response, forensik |

### C.3 Berdasarkan strategi backup/recovery (relevan dgn paper penulis)

| Strategi | Ketahanan Ransomware | Catatan |
|---|---|---|
| Connected/conventional backup | Rendah | Repositori dapat diakses dari sistem terinfeksi |
| 3-2-1 rule | Sedang–Tinggi | 3 salinan, 2 media, 1 off-site |
| Immutable / WORM | Tinggi | Tidak dapat dienkripsi ulang |
| **Air-gapped (fisik)** | Sangat tinggi | Isolasi penuh; mahal & kompleks |
| **Air-gapped (logical)** | Tinggi (praktis) | Mounting terkontrol; pendekatan paper penulis (`paper_submit`) |

---

## D. STATE-OF-THE-ART (SINTESIS)

1. **Deteksi terbaik saat ini = ensemble ML (>99%)** dan **DL/CNN-LSTM (96–99%)** pada dataset seimbang; XGBoost menonjol di ML klasik (98,9%). Ensemble konsisten mengungguli single classifier.
2. **Real-time detection** menjadi frontier: sistem seperti CryptoSniffer (monitor AES-NI) menghentikan serangan setelah hanya 10–15 file, jauh lebih cepat dari MTTD rata-rata industri (21 hari).
3. **Evasion makin canggih:** polymorphic/metamorphic, **Format-Preserving Encryption (FPE)** yang mengalahkan deteksi berbasis entropi, time-delayed execution, sandbox evasion, Living-off-the-Land (LotL), fileless ransomware.
4. **Serangan multi-stage & multi-extortion:** double/triple extortion (enkripsi + kebocoran data + DDoS); 42% sampel exfiltrasi data sebelum enkripsi.
5. **Mitigasi mutakhir:** backup immutable/air-gapped + incident response terstruktur; recovery 90% tanpa bayar tebusan bila best practice diterapkan.
6. **Teknologi masa depan:** Generative AI (sintesis varian utk training, 1–2 thn), Blockchain (audit trail immutable, threat-intel terdesentralisasi, 2–3 thn), Federated learning (deteksi kolaboratif tanpa berbagi data mentah), Quantum-safe cryptography (5–10 thn).

---

## E. RESEARCH GAP (peluang riset — dari kedua dokumen)

1. **Deteksi real-time** dengan manajemen FP pada jendela deteksi pendek + membedakan enkripsi sah (TLS, backup) dari malicious.
2. **Keterbatasan dataset:** ketersediaan terbatas, sampel usang (banyak 3–5 tahun), imbalance ekstrem (hingga 100:1), tanpa standardisasi evaluasi, isu privasi.
3. **Validasi dunia nyata:** mayoritas studi tidak diuji pada lingkungan operasional nyata (gap implementasi praktis).
4. **Deteksi lintas-platform:** model terlatih di satu platform sulit ditransfer (Windows/Linux/macOS/Android/IoT) → butuh transfer/federated learning.
5. **Anti-evasion:** deteksi FPE, fileless, LotL, time-delayed masih menantang.
6. **Kebijakan & regulasi:** kerja sama internasional, regulasi pembayaran tebusan, mandatory disclosure, standar proteksi infrastruktur kritis, regulasi cyber-insurance.

---

## F. RELEVANSI UNTUK PAPER PENULIS (`paper_submit` — cloud backup + air-gapped + kompresi)

Pemetaan di atas memberi posisi SOTA untuk memperkuat bagian *Introduction/State of the Art* dan *Related Work*:

- **Posisi paper penulis:** fokus pada **tahap Mitigation/Recovery** (air-gapped logical backup + adaptive compression), bukan pada detection ML canggih — sehingga pembanding SOTA yang relevan adalah kelompok **backup/recovery** (Thomas et al., NIST SP 800-209) dan **air-gapped** (Novak et al.), bukan XGBoost/DL detection.
- **Diferensiasi:** paper penulis menggabungkan air-gapped + kompresi multi-algoritma + deteksi berbasis hash/metadata dalam satu framework — mengisi celah "integrasi keamanan backup + efisiensi penyimpanan" yang menurut survei jarang dibahas bersama.
- **Kelemahan yang harus diakui (sejalan dgn gap SOTA & komentar reviewer):** deteksi hanya berbasis hash/metadata (bukan ML/behavioral), dataset sintetis & terbatas, validasi bukan pada malware nyata, tidak menangani evasion canggih (FPE, fileless). Ini konsisten dengan *research gap* SOTA sehingga bisa diposisikan sebagai *future work* yang kredibel.
- **Peluang penguatan naskah:** tambahkan pembanding kuantitatif dengan strategi backup lain (incremental, deduplication, immutable/WORM), dan sitasi survei terbaru (Dokumen 2) untuk memperkuat klaim SOTA & memenuhi syarat jumlah referensi jurnal.
