# Federated Learning for Network Intrusion Detection Systems: A Survey with Reproducible Verification and Adversarial Experiments on a Cloud Testbed

> **Judul paper (English, final untuk JICTRA)** = baris di atas.
>
> **Opsi judul English (pilih salah satu saat finalisasi):**
> 1. *Federated Learning for Network Intrusion Detection Systems: A Survey with
>    Reproducible Verification and Adversarial Experiments on a Cloud Testbed* ← default
> 2. *Does It Still Hold? A Survey of Federated Learning for Network Intrusion
>    Detection with Reproducible Verification on AWS*
> 3. *From Reading to Running: A Reproducible Survey of Federated Learning for
>    Network Intrusion Detection on a Public Cloud Testbed*
> 4. *Federated Learning for Network Intrusion Detection: A Survey and Controlled
>    Reproduction Study with Adversarial Evaluation*
>
> **Judul kerja (Indonesia, bukan untuk submit):** Federated Learning untuk Network
> Intrusion Detection System (NIDS): Sintesis Literatur dan Verifikasi Reproduktif di
> Lab Cloud AWS.
>
> **Catatan baca.** Dokumen ini disusun **berurutan seperti naskah paper**: Abstrak →
> Bagian 1–7 → Referensi. Semua **catatan kerja, perencanaan, dan rencana lab** ada di
> **LAMPIRAN** di bagian paling bawah (tidak masuk naskah). Target: **JICTRA (ITB)**,
> Sinta 1 / Scopus Q3. Status: **draf — Bagian 1 sudah narasi penuh; Bagian 2–7 campur
> narasi & kerangka; angka lab `[TBD]`.**
>
> **Daftar isi naskah:**
> Abstrak · 1 Pendahuluan · 2 Metodologi Survei · 3 Telaah Tematik ·
> 4 Studi Reproduksi & Eksperimen Adversarial di AWS · 5 Diskusi: Gap & Agenda Riset ·
> 6 Ancaman Validitas · 7 Kesimpulan · Referensi · (Lampiran: catatan kerja)

---

## Abstrak

> Gaya JICTRA: 100–200 kata, 5–10 keyword, bentuk lampau untuk hasil. Finalkan setelah
> angka lab masuk (ganti `[TBD]`).

Federated Learning (FL) menjanjikan pelatihan Network Intrusion Detection System
(NIDS) kolaboratif lintas-organisasi tanpa memusatkan data trafik yang sensitif.
Namun literatur FL-NIDS terfragmentasi: dataset, arsitektur, strategi agregasi, dan
protokol evaluasi berbeda antar-studi, sehingga klaim performa sulit dibandingkan,
dan bukti deployment pada cloud publik masih langka. Makalah ini menyajikan survei
sistematis FL-NIDS yang mengorganisasi literatur terkini (2020–2026) ke dalam empat
tema—arsitektur dan agregasi, penanganan heterogenitas (non-IID), robustness
adversarial dan Byzantine, serta few-shot/transfer lintas-domain—dan, berbeda dari
survei terdahulu, **menguji empiris** sejumlah klaim representatif dari **metode yang
sudah terpublikasi** (mis. FedAvg, FedProx) pada **testbed Amazon Web Services (AWS)
yang seragam** menggunakan CSE-CIC-IDS2018 dan UNSW-NB15. Selain mereproduksi klaim
inti (perbandingan agregasi, dampak non-IID, kelayakan lintas-dataset), kami juga
menjalankan eksperimen adversarial—evasion (FGSM, PGD, serangan berbasis saliency/
JSMA) dan adversarial training—pada setting lintas-dataset yang belum pernah diuji
bersama. Kami [TBD: ringkas temuan]. Kami juga melaporkan biaya komunikasi, latensi,
dan throughput nyata pada cloud. Survei ini memberikan taksonomi terpadu, protokol
evaluasi yang dapat direproduksi, dan agenda riset untuk FL-NIDS yang
privacy-preserving, robust, dan dapat di-deploy.

**Kata kunci:** federated learning; network intrusion detection; non-IID data;
adversarial robustness; cross-dataset generalization; cloud deployment; reproducibility.

---

## 1. Pendahuluan

Network Intrusion Detection System (NIDS) berbasis pembelajaran mesin kini menjadi
komponen inti pertahanan siber, dari jaringan enterprise hingga Internet of Things
(IoT) dan Industrial IoT. Namun model yang akurat menuntut data lalu lintas yang
besar dan representatif, sementara data semacam itu bersifat sensitif dan jarang
boleh keluar dari batas organisasi karena alasan privasi serta kepatuhan regulasi.
Ketegangan inilah—antara kebutuhan data lintas-organisasi dan larangan berbagi data
mentah—yang mendorong minat besar pada pembelajaran terdistribusi untuk keamanan
jaringan.

Federated Learning (FL) menawarkan jalan keluar yang menarik: alih-alih memusatkan
data, setiap peserta melatih model pada datanya sendiri dan hanya mempertukarkan
pembaruan model (bobot atau gradien), sehingga data mentah tetap berada di sisi
masing-masing organisasi [F1]. Dalam satu dekade terakhir, penerapan FL untuk NIDS
tumbuh pesat dan telah dirangkum oleh sejumlah survei dan taksonomi yang memetakan
arsitektur, strategi agregasi, serta tantangan terbukanya [F1], [F2], [F3], [F4].

Meski menjanjikan, FL untuk NIDS menghadapi tiga tantangan mendasar yang berulang di
seluruh literatur. Pertama, **heterogenitas data (non-IID)**: lalu lintas dan pola
serangan tiap organisasi berbeda, dan telah ditunjukkan bahwa FedAvg—algoritma
agregasi baku—menurun tajam ketika distribusi antar-klien menyimpang, bahkan gagal
pada skenario lintas-dataset [F4], [F11]. Kedua, **kerentanan adversarial dan
Byzantine**: model deteksi dapat dikelabui oleh perturbasi masukan yang kecil
(evasion), sedangkan klien jahat dapat meracuni model global melalui pembaruan yang
dimanipulasi [F16], [F23], [F34]. Ketiga, **serangan baru dengan data terbatas**:
sistem harus mengenali serangan zero-day dari sedikit contoh, memotivasi pendekatan
few-shot dan transfer lintas-domain [F36], [F39].

Di tengah kemajuan ini, muncul satu masalah yang justru menyulitkan pembaca dan
praktisi: **klaim performa FL-NIDS sulit dibandingkan antar-makalah.** Setiap studi
memakai dataset, arsitektur model, strategi agregasi, dan protokol evaluasi yang
berbeda, sehingga angka yang dilaporkan tidak setara dan tidak dapat ditumpuk menjadi
kesimpulan tunggal. Survei yang ada mengompilasi hasil-hasil ini secara apik, tetapi
tetap bersifat telaah pustaka—merangkum apa yang dilaporkan penulis asli tanpa
menguji ulang apakah klaim itu bertahan pada lingkungan yang terkontrol dan setara.
Terlebih lagi, bukti **deployment pada cloud publik berskala** nyaris tidak ada:
sebagian besar validasi dilakukan di testbed edge kecil atau simulasi, sehingga biaya
komunikasi, latensi, dan throughput di dunia nyata belum terdokumentasi dengan baik.

Makalah ini menjawab kesenjangan tersebut dengan pendekatan survei dua-lapis.
**Lapisan pertama** adalah telaah tematik: kami mengorganisasi literatur FL-NIDS
terkini (2020–2026) ke dalam empat tema—arsitektur dan strategi agregasi, penanganan
heterogenitas (non-IID), robustness adversarial dan Byzantine, serta few-shot/transfer
lintas-domain. **Lapisan kedua**, yang membedakan survei ini dari survei terdahulu,
adalah **verifikasi empiris**: kami menjalankan ulang sejumlah klaim representatif
dari **metode yang sudah terpublikasi** (mis. FedAvg, FedProx) pada **satu testbed
Amazon Web Services (AWS) yang seragam**, dengan model, hyperparameter, dan metrik
yang dikontrol, menggunakan dua dataset benchmark publik: CSE-CIC-IDS2018 dan
UNSW-NB15. Dengan begitu, pembaca memperoleh angka yang sebanding pada satu platform,
bukan agregat lintas-makalah yang tidak setara. Kami menegaskan bahwa survei ini
**tidak** mengusulkan metode baru dan **tidak** memakai teknik penyelarasan fitur
milik kami sendiri yang masih dalam proses tinjauan; untuk kebutuhan lintas-dataset,
kami memakai penyelarasan nama fitur manual yang sudah lazim di literatur [F11]
sebagai bagian dari setup eksperimen.

Melampaui reproduksi, kami juga menutup sebagian celah yang diakui kosong oleh
literatur, yaitu integrasi FL dengan robustness adversarial yang **diuji secara
lintas-dataset**. Kami menjalankan eksperimen evasion menggunakan FGSM, PGD, dan
serangan berbasis saliency (JSMA), lalu menguji adversarial training sebagai
pertahanan—semuanya metode yang sudah ada—pada FL-NIDS lintas-dataset di cloud. Yang
baru di sini adalah **buktinya**, bukan metodenya.

Kontribusi makalah ini dapat diringkas sebagai berikut. (1) Telaah tematik mutakhir
FL-NIDS dengan tabel komparatif yang secara eksplisit menandai apakah tiap karya
diuji lintas-dataset dan apakah memiliki bukti deployment cloud—dua dimensi yang
jarang dibuat survei lain. (2) Verifikasi reproduktif terkontrol atas klaim inti
(FedAvg versus FedProx, dampak non-IID, dan kelayakan FL lintas-dataset) pada testbed
AWS yang seragam, lengkap dengan laporan mana klaim yang bertahan dan mana yang
tidak. (3) Pengukuran biaya deployment cloud nyata—komunikasi, latensi, dan
throughput—yang menutup sebagian celah bukti produksi. (4) Eksperimen robustness
adversarial (evasion dan adversarial training) pada setting lintas-dataset yang belum
pernah diuji bersama. (5) Protokol evaluasi dan resep lab yang dapat direproduksi
dengan anggaran cloud wajar, sebagai baseline bagi komunitas riset—khususnya di
Indonesia—sebelum membangun kontribusi lanjutan.

Untuk mengarahkan kedua lapisan tersebut, kami merumuskan enam pertanyaan survei
(SQ). SQ1–SQ3 memandu lapisan telaah: bagaimana lanskap arsitektur dan agregasi
FL-NIDS saat ini dan mana yang dominan (SQ1); seberapa parah non-IID menurunkan
performa dan solusi apa yang terbukti (SQ2); serta sejauh mana robustness adversarial
dan Byzantine telah dicapai (SQ3). SQ4–SQ6 memandu lapisan verifikasi: apakah klaim
representatif (FedAvg versus FedProx, dampak non-IID, dan FL lintas-dataset) bertahan
saat direproduksi pada testbed AWS seragam (SQ4); berapa biaya nyata komunikasi,
latensi, dan throughput saat FL-NIDS di-deploy di cloud (SQ5); serta seberapa rapuh
FL-NIDS terhadap evasion—termasuk serangan berbasis saliency—dan seberapa jauh
adversarial training memulihkannya pada setting lintas-dataset (SQ6).

Sisa makalah ini disusun sebagai berikut. Bagian 2 menjelaskan metodologi survei
(protokol pencarian, kriteria inklusi, dan ekstraksi data). Bagian 3 menyajikan
telaah tematik atas keempat tema beserta tabel komparatif. Bagian 4 memaparkan studi
reproduksi dan eksperimen adversarial pada testbed AWS. Bagian 5 membahas pemetaan
celah dan agenda riset, Bagian 6 ancaman validitas, dan Bagian 7 menutup dengan
kesimpulan.

---

## 2. Metodologi Survei

Metodologi survei ini terdiri atas dua komponen yang saling melengkapi. Komponen
pertama adalah protokol telaah pustaka yang sistematis untuk membangun taksonomi
tematik (Bagian 3). Komponen kedua—yang membedakan survei ini dari survei
terdahulu—adalah protokol verifikasi reproduktif yang memandu eksperimen pada
testbed cloud (Bagian 4). Kami memaparkan keduanya secara berurutan agar pembaca
dapat menilai cakupan maupun keterulangannya.

### 2.1 Protokol pencarian literatur

Pencarian literatur dilakukan dalam tiga fase yang saling melengkapi untuk
memastikan cakupan menyeluruh terhadap tiga poros utama FL-NIDS. Fase pertama
menyasar federated learning untuk NIDS dan generalisasi lintas-dataset; fase kedua
menyasar robustness adversarial dan deteksi DDoS; fase ketiga menyasar few-shot,
meta-learning, dan penyelarasan fitur lintas-domain. Pencarian dijalankan pada basis
data dan mesin telusur akademik—mencakup SciSpace, Google Scholar, dan arXiv—dengan
rentang terbit difokuskan pada 2020–2026 agar relevan dengan perkembangan terkini.
Kueri tiap fase dirumuskan dari kombinasi kata kunci inti (mis. *federated learning*,
*network intrusion detection*, *non-IID*, *adversarial*, *few-shot*,
*cross-dataset*) dan diperhalus secara iteratif berdasarkan hasil awal.

### 2.2 Kriteria inklusi dan eksklusi

Sebuah karya dimasukkan apabila memenuhi seluruh kriteria berikut: (i) terbit dalam
rentang 2020–2026; (ii) berfokus pada federated learning, robustness adversarial,
atau few-shot/transfer dalam konteks deteksi intrusi jaringan; (iii) menyajikan
metodologi eksperimental atau kerangka teknis yang jelas; dan (iv) berupa publikasi
tertelaah sejawat atau pracetak yang kredibel. Karya yang hanya menyinggung FL atau
NIDS secara sepintas, tanpa kontribusi metodologis yang dapat ditelaah, dikeluarkan.

### 2.3 Ekstraksi data per-karya

Untuk setiap karya yang lolos seleksi, kami mengekstrak atribut yang seragam agar
dapat dibandingkan antar-studi: arsitektur federasi (horizontal, vertikal, atau
cross-silo); algoritma agregasi (FedAvg, FedProx, atau agregasi khusus); model
pembelajaran mesin atau pembelajaran dalam yang dipakai; teknik penanganan non-IID;
mekanisme pertahanan adversarial atau Byzantine; pendekatan few-shot, meta-learning,
atau transfer; dataset dan metrik evaluasi; serta—penting untuk survei ini—apakah
karya tersebut dievaluasi secara lintas-dataset dan apakah memiliki bukti deployment
pada cloud. Dua atribut terakhir inilah yang menjadi kolom penanda pada tabel
komparatif di Bagian 3 dan langsung menyorot celah yang kami isi di Bagian 4.

### 2.4 Konsolidasi referensi dan penomoran

Hasil ketiga fase digabung dan dideduplikasi berdasarkan DOI serta judul, karena
sebagian karya muncul di lebih dari satu fase pencarian. Konsolidasi menghasilkan
satu daftar referensi yang rapi dengan satu nomor untuk satu karya; penomoran akhir
mengikuti urutan kemunculan di naskah mengikuti gaya IEEE. Kami juga mencatat bahwa
karya penyelarasan fitur semantik milik kami sendiri masih dalam proses tinjauan;
karya tersebut hanya dirujuk sebagai karya-terkait bila diperlukan dan **tidak**
digunakan sebagai metode dalam survei ini (lihat Bagian 2.5 dan 4.1).

### 2.5 Protokol verifikasi reproduktif

Berbeda dari survei murni, kami menambahkan lapisan verifikasi empiris. Prinsipnya
sederhana: alih-alih menerima angka yang dilaporkan tiap penulis apa adanya, kami
memilih sejumlah klaim representatif dari metode yang sudah terpublikasi, lalu
menjalankannya kembali pada **satu testbed yang seragam**—platform, arsitektur
model, hyperparameter, metrik, dan dua dataset benchmark yang sama di seluruh
skenario—sehingga hasilnya sebanding antar-metode. Protokol ini menegakkan tiga
disiplin. Pertama, **keseragaman**: setiap pengaturan memakai model dan pipeline
identik agar perbedaan yang terukur benar-benar berasal dari faktor yang diuji
(agregasi, derajat non-IID, atau lintas-dataset), bukan dari perbedaan
implementasi. Kedua, **kehati-hatian interpretasi**: reproduksi mengukur apakah
*arah* suatu klaim bertahan di lingkungan setara, bukan meniru persis setiap detail
setup penulis asli; perbedaan setup dilaporkan terbuka sebagai ancaman validitas
(Bagian 6). Ketiga, **keterulangan**: seluruh langkah, konfigurasi, dan biaya cloud
didokumentasikan agar dapat diulang dengan anggaran wajar. Rincian teknis
testbed—topologi, dataset, model, dan daftar klaim yang diuji—dipaparkan pada
Bagian 4, sedangkan prosedur operasional lengkap disediakan sebagai materi
pelengkap yang dapat direproduksi.

---

## 3. Telaah Tematik

> Status: kerangka bullet; akan dinaratifkan. Tiap angka dari karya orang lain
> ditandai "(dilaporkan penulis asli)". Jawab SQ1–SQ3.

### 3.1 Arsitektur & Strategi Agregasi FL-NIDS (SQ1)
- **Arsitektur dominan**: horizontal cross-silo antar organisasi/domain [F1], [F5].
- **Agregasi baseline**: FedAvg (rata-rata berbobot ukuran data) [F1].
- **Varian agregasi lanjutan**:
  - Entente [F5]: Adaptive Contribution Scaling + graph sketching untuk GNIDS
    (OpTC, LANL Cyber1, Pivoting; precision/recall tinggi, FPR rendah — dilaporkan asli).
  - FedAGRU [F6]: attention-based aggregation, GRU-SVM (KDD'99, CICIDS2017, WSN-DS).
  - FedIn-NID [F7]: agregasi global dinamis (EMA) + pemilihan client multidimensi (IIoT).
  - FLAD [F31]: FedAvg adaptif (arithmetic mean + pemilihan client by akurasi
    validasi) untuk DDoS (CIC-DDoS2019; konvergensi lebih cepat — dilaporkan asli).
  - Resource-efficient FL [F8]: fokus efisiensi komunikasi/komputasi.

### 3.2 Heterogenitas & Data Non-IID (SQ2)
- **Bukti penurunan non-IID**: Lavaur dkk. [F11] menunjukkan FL-NIDS turun drastis di
  skenario cross-dataset (UNSW-NB15, Bot-IoT, ToN_IoT, CSE-CIC-IDS2018).
- **Solusi non-IID**:
  - Personalisasi/klasterisasi: Sentinel (knowledge distillation) [F13]; FedDB (DBSCAN) [F9].
  - Alignment fitur/perilaku: FedCross-VAN [F15]; graph priors Entente [F5].
  - Arsitektur hirarkis/mist: Mist-assisted FL [F14].
  - Evaluasi IID vs non-IID eksplisit: Benkaddour [F12] (CNN di UNSW-NB15).
- **Catatan**: istilah "semantic feature mapping" eksplisit jarang; umumnya "feature
  alignment" implisit. Survei ini tidak mengusulkan solusi alignment baru — untuk
  cross-dataset kami memakai alignment nama fitur manual yang sudah ada sebagai setup.

### 3.3 Robustness Adversarial & Byzantine/Poisoning (SQ3)
- **Adversarial training dalam FL**: Ennaji dkk. [F17] (Edge-IIoTset, akurasi 91,23%
  — dilaporkan asli); SFAT [F16] ("exacerbated heterogeneity" + α-slack); HADA [F18]
  (66–73% di bawah FGSM/PGD — dilaporkan asli).
- **Byzantine/poisoning**: Multi-Krum (FedSecIoT [F21], Saha dkk. [F23]); Rey dkk.
  [F22] (N-BaIoT); label-flipping [F11]; backdoor FL [F24]; robustness FL [F25].
- **GAN-based adversarial training (DDoS)**: GADoT [F28]; FGAN [F29]; FGA-IDS [F30].
- **Benchmark & review adversarial**: Dadhwal dkk. [F33]; Saini dkk. [F34]; Wang dkk.
  [F35]; Debicha dkk. [F32].
- **Catatan**: trade-off robustness vs accuracy belum tuntas, apalagi di non-IID;
  integrasi cross-dataset + adversarial masih langka (gap a). **Tema inilah yang kami
  uji sendiri di Bagian 4 (R5–R6)**, sehingga punya dua sisi: telaah di sini +
  eksperimen di Bagian 4.

### 3.4 Few-Shot, Meta-Learning & Transfer Lintas-Domain (SQ2–SQ3)
- **Few-shot FL**: Ceviz dkk. [F39] (UAV); FeCoGraph [F37] (graph contrastive).
- **Meta-learning**: Hu dkk. [F36] (federated meta-learning lawan APT).
- **Prototypical/transfer cross-domain**: FedPKT [F38]; transfer IIoT Zhang dkk. [F40].
- **Ensemble + XAI**: [F41] (CNN+LSTM+Transformer, akurasi 98,5% multi-dataset —
  dilaporkan asli; kompleksitas tinggi).
- **Catatan**: semantic-mapping + few-shot cross-dataset masih jarang (gap b/c);
  survei ini mencatatnya sebagai celah terbuka, bukan mengisinya.

### 3.5 Tabel Komparatif State-of-the-Art
> Kolom "Cross-dataset?" dan "Cloud deploy?" adalah penanda yang jarang dibuat survei
> lain — langsung memperlihatkan celah yang kami isi di Bagian 4.

| Framework | Fokus | Metodologi kunci | Dataset | Performa (dilaporkan asli) | Cross-dataset? | Cloud deploy? |
|---|---|---|---|---|---|---|
| Entente [F5] | GNIDS cross-silo | ACS + graph sketching | OpTC, LANL, Pivoting | High P/R, low FPR | Tidak | Tidak |
| FedAGRU [F6] | FL wireless edge | attention + GRU-SVM | KDD'99, CICIDS2017, WSN-DS | High acc, low FAR | Tidak | Tidak |
| FedSecIoT [F21] | Byzantine-robust | Multi-Krum | N-BaIoT | 90%+ acc, +60% robust vs FedAvg | Tidak | Tidak |
| FLAD [F31] | FL adaptif DDoS | adaptive selection | CIC-DDoS2019 | High F1, cepat konvergen | Tidak | Tidak |
| HADA [F18] | privacy-preserving FL | HADA + SHAP + DP | Edge-IIoTset dll | 85–89% acc, 66–73% under adv | Tidak | Edge |
| Ensemble+XAI [F41] | ensemble + XAI | CNN+LSTM+Transformer + GAN def | 6 dataset | 98,5% acc, AUC>0,99 | Multi-dataset | Tidak |
| Hu dkk. [F36] | few-shot meta vs APT | federated meta-learning | IDS datasets | adaptasi cepat | Sebagian | Tidak |

---

## 4. Studi Reproduksi & Eksperimen Adversarial di AWS

> **Bagian pembeda utama.** Kami menjalankan metode terpublikasi pada **satu testbed
> AWS seragam** dan melaporkan angka yang sebanding. **Semua angka = `[TBD]`** sampai
> eksperimen dieksekusi. Detail operasional (infra, runbook, fase) di Lampiran B.

### 4.1 Rancangan testbed
- **Topologi**: 1 agregator + K client (K=2 untuk cross-dataset; K=4–10 untuk partisi
  non-IID per-dataset); 3 EC2 publik nyata, transport bobot via S3, akses via SSM.
- **Dataset**: CSE-CIC-IDS2018 ↔ UNSW-NB15. Skema fitur diselaraskan dengan
  penyelarasan nama fitur manual (9 pasang padanan dasar antar-tool ekstraktor) —
  metode yang sudah ada, diperlakukan sebagai setup, bukan kontribusi.
- **Model terkontrol**: arsitektur ML/DL ringan identik di semua skenario; baseline
  centralized sebagai sanity-check.
- **Metrik**: MCC (utama), recall/precision/F1, balanced-accuracy; + biaya FL
  (rounds-to-converge, bytes/round, latensi, throughput). Multi-seed {13,42,101,202,303}.

### 4.2 Klaim yang diuji
> Dua kelompok: **(A) reproduksi** klaim inti (R1–R4) dan **(B) eksperimen adversarial**
> (R5–R6). Semua memakai metode terpublikasi; yang baru adalah buktinya.

**(A) Reproduksi klaim inti FL-NIDS**
1. **R1 — FedAvg vs FedProx (SQ3/SQ4).** Klaim: FedProx lebih stabil di non-IID [F16],[F31]. Hasil: [TBD].
2. **R2 — Dampak non-IID (SQ2/SQ4).** Klaim: performa FL turun seiring heterogenitas [F11]; sweep Dirichlet α, cari titik putus FedAvg. Hasil: [TBD].
3. **R3 — Cross-dataset FL (SQ4).** Klaim: FL lintas-dataset sulit/menurun tajam [F11]; uji dengan alignment manual. Hasil: [TBD].
4. **R4 — Biaya cloud nyata (SQ5).** Efisiensi komunikasi FL [F8]: latensi/throughput/komunikasi per round di AWS. Hasil: [TBD].

**(B) Eksperimen adversarial**
5. **R5 — Kerentanan evasion (SQ6).** Klaim: NIDS ML rapuh terhadap evasion [F28],[F33],[F34]; terapkan FGSM/PGD + saliency/JSMA; ukur attack success rate & ΔMCC (homogen & cross). Hasil: [TBD].
6. **R6 — Adversarial training sebagai defense (SQ6).** Klaim: adversarial training menaikkan robustness dengan trade-off [F16],[F17],[F32]; latih ulang FL dgn adv-examples; ukur robust MCC vs penurunan clean accuracy. Hasil: [TBD].

### 4.3 Tabel hasil (ISI dari CSV/log nyata)

| Klaim | Jenis | Sumber literatur | Metrik | Angka dilaporkan asli | **Angka lab kami (AWS)** | Bertahan? |
|---|---|---|---|---|---|---|
| R1 FedProx>FedAvg (non-IID) | reproduksi | [F16][F31] | MCC/F1 | [kutip] | [TBD] | [TBD] |
| R2 non-IID menurunkan FL | reproduksi | [F11] | ΔMCC | [kutip] | [TBD] | [TBD] |
| R3 cross-dataset FL sulit | reproduksi | [F11] | MCC | [kutip] | [TBD] | [TBD] |
| R4 biaya komunikasi | reproduksi | [F8] | bytes/round, latensi | [kutip] | [TBD] | — |
| R5 evasion FGSM/PGD/JSMA | adversarial | [F28][F33][F34] | attack success rate, ΔMCC | [kutip] | [TBD] | [TBD] |
| R6 adversarial training | adversarial | [F16][F17][F32] | robust MCC, Δclean-acc | [kutip] | [TBD] | [TBD] |

### 4.4 Catatan kehati-hatian metodologis
- Reproduksi mengukur apakah **arah klaim** bertahan di testbed seragam — bukan meniru
  persis setup penulis asli (perbedaan dicatat di Bagian 6).
- **Adversarial pada tabular flow ≠ pada citra.** Perturbasi FGSM/PGD/JSMA dibatasi
  agar flow tetap valid (non-negatif, konsisten antar-fitur, dalam batas protokol) dan
  hanya pada fitur yang dapat dimanipulasi penyerang. Konsekuensinya R5/R6 lebih
  konservatif daripada serangan citra — itu disengaja dan dilaporkan di Bagian 6.

---

## 5. Diskusi: Gap & Agenda Riset

> Sumber: `references/state_of_art_gap_federated_nids.md` (gap a–e + rekomendasi).

- **Gap a** — Integrasi FL + adversarial robustness yang diuji **cross-dataset**:
  langka. **→ Sebagian kami isi lewat R5–R6 (Bagian 4).**
- **Gap b** — Semantic feature mapping eksplisit dalam FL: belum diformalkan (celah
  terbuka; survei ini mencatat, tidak mengisinya).
- **Gap c** — Few-shot teruji **lintas-dataset** + digabung adversarial: terbatas.
- **Gap d** — Skalabilitas & heterogenitas skala produksi (ribuan klien, trafik nyata): minim bukti.
- **Gap e** — **Deployment & evaluasi di cloud publik (AWS)**: hampir tak ada. **→
  Sebagian kami isi lewat R4 (biaya cloud nyata) di Bagian 4.**
- **Agenda riset**: encoder selaras-semantik; adversarial-aware prototypical federated
  meta-learning; agregasi berbobot-semantik; protokol evaluasi cross-dataset
  bebas-kebocoran; evaluasi cloud testbed.

---

## 6. Ancaman Validitas

- Perbedaan setup reproduksi vs penulis asli (dataset, model, hyperparameter).
- Dua dataset saja (CIC + UNSW) — generalisasi terbatas; diakui jujur.
- Biaya cloud → jumlah run/seed terbatas; dilaporkan apa adanya.
- Potensi bias seleksi literatur; mitigasi: protokol pencarian eksplisit (Bagian 2).
- **Adversarial pada tabular flow (R5–R6):** perturbasi dibatasi agar flow tetap valid
  → serangan lebih konservatif daripada domain citra; threat model yang diasumsikan
  (fitur yang dapat dimanipulasi, white/black-box) membatasi generalisasi temuan.

---

## 7. Kesimpulan

> ISI setelah angka Bagian 4 masuk.

- Ringkas taksonomi empat tema + temuan reproduksi R1–R4 + biaya cloud + eksperimen
  adversarial R5–R6.
- Pernyataan jujur: klaim literatur mana yang bertahan dan mana yang tidak di testbed seragam.
- Nilai untuk komunitas: baseline reproduktif + bukti robustness adversarial pada
  celah terbuka (gap a) + agenda riset FL-NIDS.

---

## Referensi

> Gaya IEEE, 30 referensi. Dipilih dari `references/federated_refs_clean.md` dengan
> keterwakilan empat tema + semua karya yang disitasi di Bagian 3–4. Penomoran di
> bawah ([1]–[30]) adalah penomoran **final paper**; label lama [F*] disimpan dalam
> kurung siku kecil sebagai jejak untuk pemetaan sitasi di naskah. Semua entri punya
> DOI kecuali satu yang ditandai (verifikasi saat finalisasi).

**A. Survei & landasan FL-NIDS**

[1] [F1] A. Khraisat, A. Alazab, T. Jan, and A. Gopez, "Survey on federated learning for intrusion detection system: concept, architectures, aggregation strategies, challenges, and future directions," *ACM Comput. Surv.*, 2024, doi: 10.1145/3687124.

[2] [F2] J. L. Hernández-Ramos *et al.*, "Intrusion detection based on federated learning: a systematic review," *ACM Comput. Surv.*, Apr. 2025, doi: 10.1145/3731596.

[3] [F3] A. A. Wardana and P. Sukarno, "Taxonomy and survey of collaborative intrusion detection system using federated learning," *ACM Comput. Surv.*, Oct. 2024, doi: 10.1145/3701724.

[4] [F4] E. V. Fedorchenko, E. Novikova, and A. N. Shulepov, "Comparative review of the intrusion detection systems based on federated learning: advantages and open challenges," *Algorithms*, vol. 15, no. 7, p. 247, 2022, doi: 10.3390/a15070247.

**B. Arsitektur & strategi agregasi**

[5] [F5] J. Xu, C. Li, Y. Zheng, and Z. Li, "Entente: cross-silo intrusion detection on network log graphs with federated learning," *arXiv:2503.14284*, 2025, doi: 10.48550/arXiv.2503.14284.

[6] [F6] Z. Chen, N. Lv, P. Li, Y. Fang, K. Chen, and W. Pan, "Intrusion detection for wireless edge networks based on federated learning," *IEEE Access*, vol. 8, pp. 217463–217472, 2020, doi: 10.1109/ACCESS.2020.3041793.

[7] [F7] J. Mao, Z. Wei, B. Li, R. Zhang, and L. Song, "FedIn-NID: a federated learning framework for network intrusion detection in large-scale heterogeneous industrial IoT," *IEEE Trans. Inf. Forensics Security*, 2025, doi: 10.1109/TIFS.2025.3602226.

[8] [F8] R. Doriguzzi-Corin, S. Cretti, and D. Siracusa, "Resource-efficient federated learning for network intrusion detection," in *Proc. IEEE Conf. Netw. Softwarization (NetSoft)*, 2024, doi: 10.1109/NetSoft60951.2024.10588938.

[9] [F9] Y.-C. Lee, W.-C. Chien, and Y.-C. Chang, "FedDB: a federated learning approach using DBSCAN for DDoS attack detection," *Appl. Sci.*, vol. 14, no. 22, 2024, doi: 10.3390/app142210236.

**C. Non-IID, heterogenitas & personalisasi**

[10] [F11] L. Lavaur, Y. Busnel, and F. Autrel, "Demo: highlighting the limits of federated learning in intrusion detection," in *Proc. IEEE Int. Conf. Distrib. Comput. Syst. (ICDCS)*, 2024, pp. 1416–1419, doi: 10.1109/ICDCS60910.2024.00135.

[11] [F12] M. Benkaddour, "Enhancing federated learning for privacy preserving intrusion detection in IoT networks," *Przegląd Elektrotechniczny*, 2025, doi: 10.15199/48.2025.09.21.

[12] [F13] G. Singh, K. Singh, P. Rajalakshmi, and Y. Xong, "Sentinel: dynamic knowledge distillation for personalized federated intrusion detection in heterogeneous IoT networks," *arXiv:2510.23019*, 2025, doi: 10.48550/arXiv.2510.23019.

[13] [F14] S. Ali, R. Alireza, and A. Mahmood, "Mist-assisted federated learning for intrusion detection in heterogeneous IoT networks," *arXiv:2511.00271*, 2025, doi: 10.48550/arXiv.2511.00271.

[14] [F15] M. Khalid, U. Zukaib, M. Al-Rakhami, and A. M. Alamri, "FedCross-VAN: federated cross-domain behavior alignment for VANET intrusion detection," *Trans. Emerg. Telecommun. Technol.*, vol. 37, 2025, doi: 10.1002/ett.70309.

**D. Robustness adversarial, Byzantine & poisoning**

[15] [F16] J. Zhang *et al.*, "Combating exacerbated heterogeneity for robust models in federated learning (SFAT)," *arXiv:2303.00250*, 2023, doi: 10.48550/arXiv.2303.00250.

[16] [F17] E. M. Ennaji, S. E. Hajla, Y. Maleh, and S. Mounir, "Adversarially robust federated deep learning models for intrusion detection in IoT," *Indones. J. Electr. Eng. Comput. Sci.*, vol. 37, no. 2, p. 937, 2024, doi: 10.11591/ijeecs.v37.i2.pp937-947.

[17] [F18] G. Chandu, T. S. Karthik, and B. Parag, "Federated learning for distributed IoT security: a privacy-preserving approach to intrusion detection," *IEEE Access*, 2025, doi: 10.1109/ACCESS.2025.3592481.

[18] [F20] A. Al Mazroa *et al.*, "FORT-IDS: a federated, optimized, robust and trustworthy intrusion detection system for IIoT security," *Sci. Rep.*, 2025, doi: 10.1038/s41598-025-31025-x.

[19] [F21] S. K. Ghimire and S. Lodh, "FedSecIoT: a federated learning framework for collaborative and privacy-preserving botnet detection in IoT with adversarial robustness," in *Proc. IEEE SILCON*, 2025, doi: 10.1109/SILCON67893.2025.11327096.

[20] [F23] S. Saha, M. I. Sayed, M. Faezipour, and S. Bhatt, "Resilient federated learning for DDoS detection with multi-Krum aggregation and anomaly detection," in *Proc. IEEE SmartNets*, 2025, doi: 10.1109/SmartNets65254.2025.11106859.

**E. GAN & adversarial training untuk DDoS/NIDS**

[21] [F28] M. S. I. Sajid *et al.*, "GADoT: GAN-based adversarial training for robust DDoS attack detection," *arXiv:2201.13102*, 2022, doi: 10.48550/arXiv.2201.13102.

[22] [F31] R. Doriguzzi-Corin and D. Siracusa, "FLAD: adaptive federated learning for DDoS attack detection," *arXiv:2205.06661*, 2022, doi: 10.48550/arXiv.2205.06661.

[23] [F32] I. Debicha, T. Debatty, J.-M. Dricot, and W. Mees, "Adversarial training for deep learning-based intrusion detection systems," *arXiv:2104.09852*, 2021, doi: 10.48550/arXiv.2104.09852.

[24] [F33] H. Dadhwal, M. de Abreu, N. Parvizi, and S. Saha, "Benchmarking the adversarial resilience of machine learning models for DDoS detection," *Array*, vol. 29, p. 100664, 2026, doi: 10.1016/j.array.2025.100664.

[25] [F34] S. Saini, A. Chennamaneni, and B. A. Sawyerr, "A review of the duality of adversarial learning in network intrusion: attacks and countermeasures," *arXiv:2412.13880*, 2024, doi: 10.48550/arXiv.2412.13880.

**F. Few-shot, meta-learning & transfer lintas-domain**

[26] [F36] Y. Hu, J. Wu, G. Li, J. Li, and J. Cheng, "Privacy-preserving few-shot traffic detection against advanced persistent threats via federated meta learning," *IEEE Trans. Netw. Sci. Eng.*, vol. 11, pp. 2549–2560, 2024, doi: 10.1109/TNSE.2023.3304556.

[27] [F37] Q. Mao, X. Lin, G. Li, and J. Li, "FeCoGraph: label-aware federated graph contrastive learning for few-shot network intrusion detection," *IEEE Trans. Inf. Forensics Security*, 2025, doi: 10.1109/TIFS.2025.3541890.

[28] [F38] K. Yin, J. Zhang, Z. Xia, and C. Yu, "FedPKT: robust cross-domain few-shot intrusion detection via prototypical knowledge transfer," *IEEE Trans. (early access)*, doc. 11360061. [DOI belum terbit — verifikasi saat finalisasi.]

[29] [F39] Ö. Ceviz, S. Şen, and P. Sadioglu, "Distributed intrusion detection in dynamic networks of UAVs using few-shot federated learning," *arXiv:2501.13213*, 2025, doi: 10.48550/arXiv.2501.13213.

[30] [F41] K. S, V. Malathi, B. J. Lakshmi, A. V. Sriharsha, T. D. Kumar, and T. Lakshmibai, "Federated and explainable intrusion detection systems for large-scale heterogeneous networks using ensemble deep learning," in *Proc. IEEE ICACRS*, 2025, doi: 10.1109/ICACRS67045.2025.11324277.

> **Catatan verifikasi (sebelum submit):**
> - 29 dari 30 entri sudah ber-DOI. Satu pengecualian: **[28] FedPKT** — baru tersedia
>   sebagai IEEE early-access (doc. 11360061); DOI final diisi saat terbit resmi.
> - Entri arXiv memakai DOI DataCite `10.48550/arXiv.*` (sah dikutip). Bila versi
>   jurnal/konferensinya sudah terbit, ganti ke DOI penerbit.
> - Label `[F*]` dalam kurung hanya penanda pemetaan; **dihapus** saat konversi ke `.tex`.

<!-- ====================================================================== -->
<!-- MULAI LAMPIRAN: CATATAN KERJA / MEMORI — BUKAN BAGIAN NASKAH PAPER     -->
<!-- ====================================================================== -->

---

# LAMPIRAN (catatan kerja — tidak masuk naskah paper)

> Semua di bawah ini adalah **memori kerja & perencanaan**, bukan teks paper. Saat
> konversi ke `.tex`, bagian ini **dibuang**.

## Lampiran M — Memori & aturan proyek

> **Fungsi:** baca dulu bila konteks reset.
> - Target: JICTRA (ITB), Sinta 1 / Q3. Jenis: survey + verifikasi empiris.
> - **TESIS/BENANG MERAH:** (1) pelajari lanskap → (2) praktikkan metode representatif
>   di AWS kita → (3) simpulkan dari hasil nyata.
> - **BATASAN METODE:** HANYA metode yang sudah terpublikasi. **TIDAK memakai SFM**
>   (karya kami yang masih review). Cross-dataset pakai manual feature-name alignment
>   yang sudah lazim [F11], sebagai setup — bukan kontribusi.
> - **ATURAN KEJUJURAN:** angka lab `[TBD]` sampai dieksekusi; angka kutipan beri
>   sitasi [F*] + "(dilaporkan asli)"; narasi ID, tabel/figur EN; desimal titik di
>   `.md`, koma di `.tex`.
>
> **Sumber materi:** `references/literature_review_federated_nids.md`,
> `references/state_of_art_gap_federated_nids.md`, `references/federated_refs_clean.md`.

## Lampiran P — Positioning & pembeda vs Paper 4

**Masalah yang dilihat.** Riset FL-NIDS terfragmentasi; survei yang ada ([F1]–[F4])
murni telaah pustaka, merangkum angka yang tak sebanding tanpa menguji ulang.

**Pembeda vs Paper 4 (`paper-jictra.tex`) — anti-salami.** Paper 4 = *research paper*
yang mengusung **metode kami sendiri** (Semantic Feature Alignment/SFM) + temuan
spesifik (FedPer menutup gap cross-dataset); fokus sempit & mendalam; masih review.
Survei ini = *survey ber-bukti* yang **tidak mengusung metode baru**, cakupan luas
(seluruh lanskap FL-NIDS), dan sengaja **tidak memakai SFM**. Di survei, SFM/FedPer
hanya boleh muncul sebagai karya-terkait, bukan sebagai hasil kami. Hasil cross-dataset
dibingkai sebagai verifikasi klaim literatur [F11], bukan temuan metode kami.

## Lampiran C — Pernyataan Kontribusi / Klaim (ringkas; versi naratif ada di Bagian 1)

- **C1 (poros) — Survey + verifikasi reproduktif terkontrol** (SQ4 → Bagian 2+4).
- **C2 — Bukti deployment cloud publik nyata** (SQ5 → Bagian 4): biaya komunikasi/latensi/throughput; mengisi gap e.
- **C3 — Taksonomi tematik mutakhir** (SQ1–SQ3 → Bagian 3): tabel dengan kolom cross-dataset & cloud.
- **C4 — Protokol & baseline reproduktif** (SQ4 → Bagian 2+4): resep lab beranggaran wajar.
- **C5 — Eksperimen adversarial pada celah terbuka** (SQ6 → Bagian 4): evasion + adversarial training; mengisi gap a.

**Antisipasi keberatan reviewer (jawab di Bagian 6):**
- *"Hanya 2 dataset."* → controlled reproduction (kedalaman & kesebandingan), diakui sebagai batas.
- *"Survey atau research paper?"* → survey ber-bukti; Bagian 4 melayani tujuan survei, bukan metode baru.
- *"Temuan negatif?"* → dibingkai sebagai mengkuantifikasi KAPAN & MENGAPA FL gagal (informatif).

## Lampiran S — Status & peta section JICTRA

| Bagian naskah (final) | Status | Sumber materi |
|---|---|---|
| Abstrak | draf; finalkan setelah angka | — |
| 1 Pendahuluan | **narasi penuh** | positioning + gap-doc |
| 2 Metodologi Survei | kerangka | `literature_review` §2 |
| 3 Telaah Tematik (3.1–3.5) | kerangka bullet | `literature_review` §3–6 |
| 4 Studi Reproduksi & Adversarial | kerangka + tabel | Lampiran B |
| 5 Diskusi: Gap & Agenda | kerangka | gap-doc |
| 6 Ancaman Validitas | kerangka | — |
| 7 Kesimpulan | placeholder | isi setelah Bagian 4 |
| Referensi | pointer | `federated_refs_clean.md` |

**Sudah ada:**
- Kerangka urut 1–7; Bagian 1 & 2 narasi penuh; 30 referensi IEEE + DOI.
- Keputusan lab terjawab (alignment 9 pasang, instance `t3.medium`, CIC 100k/UNSW 82k).
- **Kode eksekusi LENGKAP:** `aws/fed_node_survey.py` (FedAvg+FedProx+hook adv),
  `aws/fed-runbook-survey.md`, dan 7 notebook `notebooks2/` (s01,s03,s05,s06,s07,s14,s15).

**TODO:**
1. [ ] **Jalankan di AWS/SageMaker** (butuh kredensial + data): s01 → EC2 run (R3,R6) →
       s03/s14/s15/s05/s06/s07 → tarik CSV. (Kode siap; angka masih `[TBD]`.)
2. [ ] Isi tabel §4.3 dari CSV `survey_out/` + S3 `federated_survey/results/`.
3. [ ] Lengkapi tabel komparatif §3.5 dari `literature_review` §6.
4. [ ] Kutip angka "dilaporkan asli" tiap klaim R1–R6.
5. [ ] Naratifkan Bagian 3, 5, 6 (saat ini bullet).
6. [ ] Finalkan Abstrak & Bagian 7 setelah angka masuk.
7. [ ] Konversi ke `.tex`/template JICTRA; verifikasi DOI/venue (khususnya FedPKT).

## Lampiran B — Rencana praktik real-case di AWS (operasional)

> Infrastruktur & kode SUDAH ADA dari Paper 4; tinggal adaptasi (lepas SFM). Angka
> tetap `[TBD]` sampai run nyata.

### B.0 Aset tersedia
- **Infra** (`aws/fed-vpc-3ec2-public.yaml`): 3 EC2 publik (aggregator + client-cic +
  client-unsw), tanpa NAT, akses via SSM, bobot via S3, region ap-southeast-1.
  Teardown 1 stack → biaya nol. **Bukti deployment cloud NYATA (C2), bukan simulasi.**
- **Kode node** (`aws/fed_node.py`): MLP numpy 9→128→64→1, FedAvg + FedProx (`--mu`),
  transport S3, dijalankan via SSM.
- **Runbook** (`aws/fed-runbook.md`): deploy → setup → run → pantau → evaluasi → teardown.
- **Notebook survei** (`notebooks2/`): `s01_fed_data_partition.ipynb` (sudah; reframe
  tanpa SFM, S3 prefix `federated_survey/`). Berikutnya s03/s05/s06/s07/s14/s15.

### B.1 Yang diubah untuk survei (lepas dari SFM)
1. **Manual feature-name alignment, bukan SFM.** Kamus 9 fitur di nb01 sebenarnya
   pemetaan nama kolom langsung CIC↔UNSW → pakai apa adanya, sebut "manual alignment".
2. **Framing = verifikasi klaim literatur**, bukan "SFM enabler"; ablasi SFM di-skip.
3. **Reuse** notebook partisi/FedAvg/non-IID/FedProx/multiseed/homogen.

### B.2 Pemetaan klaim → eksekusi → metrik
| Klaim | Skenario | Aset | Output/metrik |
|---|---|---|---|
| R1 FedAvg vs FedProx | 1 dataset non-IID; `--mu 0` vs `0.01/0.1` | s06 + `fed_node.py` | MCC/F1 + rounds-to-converge |
| R2 dampak non-IID | sweep Dirichlet α (K=4) | s05 | kurva MCC-vs-α, titik putus |
| R3 cross-dataset | 2 klien {CIC,UNSW}, alignment manual | s01+s03 di 3 EC2 | MCC global vs centralized/local |
| R4 biaya cloud | ukur saat R1–R3 di EC2 | runbook + log | bytes/round, latensi, throughput |
| R5 evasion | serang model global terlatih | s14 + model R3 | attack success rate, ΔMCC per ε |
| R6 adv-training | latih ulang FL dgn adv-examples | s15 + node (hook adv) | robust MCC, Δclean-acc, biaya |

### B.3 Urutan eksekusi (fase)
- **Fase 0** — partisi data (s01) → S3 `federated_survey/data/{cic,unsw}/`.
- **Fase 1** — uji pipeline murah: deploy stack, R3 `--rounds 10`.
- **Fase 2 (R1–R4)** — R3 rounds penuh (50–100) multiseed; R2 sweep α
  {100,10,1,0.5,0.1,0.05}; R1 `--mu` {0,0.01,0.1}; R4 catat biaya dari log.
- **Fase 2b (R5–R6)** — R5 evasion OFFLINE pada model final R3 (FGSM/PGD sweep ε +
  JSMA); R6 adversarial training di EC2 (hook adv per-klien).
- **Fase 3** — evaluasi offline: tarik `global_final.npz`, hitung metrik, isi §4.3.
- **Fase 4** — teardown `delete-stack` (WAJIB). Hasil tetap di S3.

### B.4 Keputusan (sebagian sudah terjawab)
1. **Alignment fitur → JELAS.** 9 pasang manual (reframe istilah, bukan ganti kode):
   | Fitur | CIC (CICFlowMeter) | UNSW (Argus/Bro) |
   |---|---|---|
   | duration | Flow Duration | dur |
   | fwd_pkts | Tot Fwd Pkts | spkts |
   | bwd_pkts | Tot Bwd Pkts | dpkts |
   | fwd_bytes | TotLen Fwd Pkts | sbytes |
   | bwd_bytes | TotLen Bwd Pkts | dbytes |
   | fwd_mean | Fwd Pkt Len Mean | smean |
   | bwd_mean | Bwd Pkt Len Mean | dmean |
   | src_load | Flow Byts/s | sload |
   | dst_load | Bwd Pkts/s | dload |
2. **Instance EC2 → JELAS.** `t3.medium` (2 vCPU/4 GB) default; cukup untuk R1–R4;
   pantau saat R6.
3. **Ukuran data → di s01**: CIC 100k (pos ~0,169), UNSW 82k (pos ~0,551), rasio ~1,2:1.
4. **Rounds & local-epochs** final — kalibrasi (mulai kecil).
5. **R4 cukup dari 3 EC2** atau perlu K lebih besar.
6. **R5**: metode (FGSM/PGD/JSMA) + rentang ε + fitur yang boleh diperturbasi + batas plausibilitas.
7. **R6**: rasio adv-examples, metode generasi, per-client vs global.

### B.5 Mekanik serangan adversarial pada flow (penting)
- **Constrained perturbation**: hanya fitur yang dikuasai penyerang; bukan fitur turunan sistem.
- **Hormati batas domain**: non-negatif, konsisten antar-fitur, clip ke range valid.
- **Metode (semua sudah ada)**: FGSM & PGD (ber-ε) + JSMA/saliency (pilih fitur via peta saliency).
- **Pelaporan jujur**: penurunan kemungkinan lebih moderat daripada domain citra; wajar untuk NIDS.
- **Threat model eksplisit**: pengetahuan (white/black-box), kapabilitas (fitur yang bisa diubah), tujuan (evasion).

### B.6 Biaya & kejujuran
- Semua hasil ke S3 SEBELUM teardown; angka dari CSV/log nyata.
- Teardown tiap sesi agar biaya wajar (konsisten C4).
