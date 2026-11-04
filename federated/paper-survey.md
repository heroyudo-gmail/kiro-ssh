# Federated Learning for Network Intrusion Detection Systems: A Survey with Reproducible Verification and Adversarial Experiments on a Cloud Testbed

> **Judul paper (English, final untuk JICTRA)** = baris di atas.
>
> **Opsi judul English (arsip; final = baris di atas):**
> 1. *Federated Learning for Network Intrusion Detection Systems: A Survey with
>    Reproducible Verification and Adversarial Experiments on a Cloud Testbed* ← dipilih
> 2. *Does It Still Hold? A Survey of Federated Learning for Network Intrusion
>    Detection with Reproducible Verification on AWS*
> 3. *From Reading to Running: A Reproducible Survey of Federated Learning for
>    Network Intrusion Detection on a Public Cloud Testbed*
> 4. *Federated Learning for Network Intrusion Detection: A Survey and Controlled
>    Reproduction Study with Adversarial Evaluation*
> 5. *Beyond the Literature: A Reproducible Survey of Federated Learning for Network
>    Intrusion Detection with Cross-Dataset and Adversarial Verification on AWS*
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
> **Daftar isi naskah (judul bab English, isi Indonesia):**
> Abstract · 1 Introduction · 2 Survey Methodology · 3 Thematic Review ·
> 4 Reproduction Study & Adversarial Experiments on AWS ·
> 5 Discussion: Gaps, Research Agenda & Threats to Validity · 6 Conclusion ·
> References · (Lampiran: catatan kerja)

---

## Abstract

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
yang seragam** menggunakan CSE-CIC-IDS2018 dan UNSW-NB15. Kami juga
menjalankan eksperimen adversarial—evasion (FGSM, PGD, saliency/JSMA) dan adversarial
training—pada setting lintas-dataset yang belum pernah diuji bersama. Dari enam klaim,
dua terkonfirmasi (FL lintas-dataset runtuh, MCC −0,03 vs 0,55 terpusat; evasion
sangat mudah, attack success rate hingga 1,00), satu bergantung domain
(dampak non-IID nyata pada CIC tetapi tidak pada UNSW), dan dua tidak bertahan
(FedProx tidak mengungguli FedAvg; adversarial training menaikkan akurasi bersih namun
gagal memulihkan robustness). Biaya cloud terukur kecil (≈300 KB dan ≈16 detik per
ronde). Survei ini memberikan taksonomi terpadu, protokol evaluasi yang dapat
direproduksi, dan agenda riset untuk FL-NIDS yang privacy-preserving, robust, dan
dapat di-deploy.

**Kata kunci:** federated learning; network intrusion detection; non-IID data;
adversarial robustness; cross-dataset generalization; cloud deployment; reproducibility.

---

## 1. Introduction

Network Intrusion Detection System (NIDS) berbasis pembelajaran mesin kini menjadi
komponen inti pertahanan siber, dari jaringan enterprise hingga Internet of Things
(IoT) dan Industrial IoT. Namun model yang akurat menuntut data lalu lintas yang
besar dan representatif, sementara data semacam itu bersifat sensitif dan jarang
boleh keluar dari batas organisasi karena alasan privasi serta kepatuhan regulasi.
Tarik-menarik inilah—antara kebutuhan data lintas-organisasi dan larangan berbagi data
mentah—yang mendorong minat besar pada pembelajaran terdistribusi untuk keamanan
jaringan.

Federated Learning (FL) menawarkan jalan keluar yang menarik: alih-alih memusatkan
data, setiap client melatih model pada datanya sendiri dan hanya mempertukarkan
pembaruan model (bobot atau gradien), sehingga data mentah tetap berada di sisi
masing-masing organisasi [1]. Dalam satu dekade terakhir, penerapan FL untuk NIDS
tumbuh pesat dan telah dirangkum oleh sejumlah survei dan taksonomi yang memetakan
arsitektur, strategi agregasi, serta tantangan terbukanya [1], [2], [3], [4].

Meski menjanjikan, FL untuk NIDS menghadapi tiga tantangan mendasar yang berulang di
seluruh literatur. Pertama, **heterogenitas data (non-IID)**: lalu lintas dan pola
serangan tiap organisasi berbeda, dan telah ditunjukkan bahwa FedAvg—algoritma
agregasi baku—menurun tajam ketika distribusi antar-klien menyimpang, bahkan gagal
pada skenario lintas-dataset [4], [5]. Kedua, **kerentanan adversarial dan
Byzantine**: model deteksi dapat dikelabui oleh perturbasi masukan yang kecil
(evasion), sedangkan klien jahat dapat meracuni model global melalui pembaruan yang
dimanipulasi [6], [7], [8]. Ketiga, **serangan baru dengan data terbatas**:
sistem harus mengenali serangan zero-day dari sedikit contoh, memotivasi pendekatan
few-shot dan transfer lintas-domain [9], [10].

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
kami memakai penyelarasan nama fitur manual yang sudah lazim di literatur [5]
sebagai bagian dari setup eksperimen.

Melampaui reproduksi, kami juga menutup sebagian celah yang diakui kosong oleh
literatur, yaitu integrasi FL dengan robustness adversarial yang **diuji secara
lintas-dataset**. Kami menjalankan eksperimen evasion menggunakan FGSM (*Fast Gradient
Sign Method*), PGD (*Projected Gradient Descent*), dan serangan berbasis saliency
JSMA (*Jacobian-based Saliency Map Attack*), lalu menguji adversarial training sebagai
pertahanan—semuanya metode yang sudah ada—pada FL-NIDS lintas-dataset di cloud. FGSM
membangkitkan perturbasi satu langkah searah tanda gradien; PGD adalah versi iteratif
yang lebih kuat; JSMA memilih fitur paling berpengaruh melalui peta saliency. Yang
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
celah, agenda riset, dan ancaman validitas; Bagian 6 menutup dengan kesimpulan.

---

## 2. Survey Methodology

Metodologi survei ini terdiri atas dua komponen yang saling melengkapi. Komponen
pertama adalah protokol telaah pustaka yang sistematis untuk membangun taksonomi
tematik (Bagian 3). Komponen kedua—yang membedakan survei ini dari survei
terdahulu—adalah protokol verifikasi reproduktif yang memandu eksperimen pada
testbed cloud (Bagian 4). Kami memaparkan keduanya secara berurutan agar pembaca
dapat menilai cakupan maupun keterulangannya.

### 2.1 Literature search protocol

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

### 2.2 Inclusion and exclusion criteria

Sebuah karya dimasukkan apabila memenuhi seluruh kriteria berikut: (i) terbit dalam
rentang 2020–2026; (ii) berfokus pada federated learning, robustness adversarial,
atau few-shot/transfer dalam konteks deteksi intrusi jaringan; (iii) menyajikan
metodologi eksperimental atau kerangka teknis yang jelas; dan (iv) berupa publikasi
tertelaah sejawat atau pracetak yang kredibel. Karya yang hanya menyinggung FL atau
NIDS secara sepintas, tanpa kontribusi metodologis yang dapat ditelaah, dikeluarkan.

### 2.3 Per-study data extraction

Untuk setiap karya yang lolos seleksi, kami mengekstrak atribut yang seragam agar
dapat dibandingkan antar-studi: arsitektur federasi (horizontal, vertikal, atau
cross-silo); algoritma agregasi (FedAvg, FedProx, atau agregasi khusus); model
pembelajaran mesin atau pembelajaran dalam yang dipakai; teknik penanganan non-IID;
mekanisme pertahanan adversarial atau Byzantine; pendekatan few-shot, meta-learning,
atau transfer; dataset dan metrik evaluasi; serta—penting untuk survei ini—apakah
karya tersebut dievaluasi secara lintas-dataset dan apakah memiliki bukti deployment
pada cloud. Dua atribut terakhir inilah yang menjadi kolom penanda pada tabel
komparatif di Bagian 3 dan langsung menyorot celah yang kami isi di Bagian 4.

### 2.4 Reference consolidation and numbering

Hasil ketiga fase digabung dan dideduplikasi berdasarkan DOI serta judul, karena
sebagian karya muncul di lebih dari satu fase pencarian. Konsolidasi menghasilkan
satu daftar referensi yang rapi dengan satu nomor untuk satu karya; penomoran akhir
mengikuti urutan kemunculan di naskah mengikuti gaya IEEE. Kami juga mencatat bahwa
karya penyelarasan fitur semantik milik kami sendiri masih dalam proses tinjauan;
karya tersebut hanya dirujuk sebagai karya-terkait bila diperlukan dan **tidak**
digunakan sebagai metode dalam survei ini (lihat Bagian 2.5 dan 4.1).

### 2.5 Reproducible verification protocol

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
(Bagian 5.1). Ketiga, **keterulangan**: seluruh langkah, konfigurasi, dan biaya cloud
didokumentasikan agar dapat diulang dengan anggaran wajar. Rincian teknis
testbed—topologi, dataset, model, dan daftar klaim yang diuji—dipaparkan pada
Bagian 4, sedangkan prosedur operasional lengkap disediakan sebagai materi
pelengkap yang dapat direproduksi.

---

## 3. Thematic Review

> Status: kerangka bullet; akan dinaratifkan. Tiap angka dari karya orang lain
> ditandai "(dilaporkan penulis asli)". Jawab SQ1–SQ3.

### 3.1 FL-NIDS Architectures & Aggregation Strategies (SQ1)

Arsitektur yang dominan pada FL-NIDS adalah horizontal cross-silo, di mana beberapa
organisasi atau domain melatih model bersama tanpa berbagi data mentah [1], [11], dan
agregasi bakunya adalah FedAvg yang merata-ratakan bobot klien secara tertimbang
ukuran data [1]. Di atas fondasi ini, literatur mengembangkan sejumlah varian agregasi
yang lebih canggih. Entente [11] memakai Adaptive Contribution Scaling dan graph
sketching untuk deteksi berbasis graf jaringan, dan melaporkan precision/recall tinggi
dengan FPR rendah pada OpTC, LANL Cyber1, dan Pivoting. FedAGRU [12] menambahkan
agregasi berbasis attention pada model GRU-SVM, sementara FedIn-NID [13] mengandalkan
agregasi global dinamis (exponential moving average) dengan pemilihan klien
multidimensi untuk IIoT. Untuk deteksi DDoS, FLAD [14] mengadaptasi FedAvg dengan
pemilihan klien berbasis akurasi validasi dan melaporkan konvergensi yang lebih cepat.
Arah lain menekankan efisiensi: resource-efficient FL [15] berfokus menekan biaya
komunikasi dan komputasi. Secara keseluruhan, inovasi pada lapisan agregasi cukup
kaya, tetapi mayoritas diuji hanya dalam satu jaringan dan jarang lintas-dataset.

### 3.2 Heterogeneity & Non-IID Data (SQ2)

Heterogenitas data adalah tantangan yang paling banyak disorot. Lavaur dkk. [5]
menunjukkan bahwa FL-NIDS menurun drastis pada skenario cross-dataset yang melibatkan
UNSW-NB15, Bot-IoT, ToN_IoT, dan CSE-CIC-IDS2018—bukti bahwa perbedaan distribusi
antar-jaringan, bukan sekadar non-IID ringan antar-klien, dapat meruntuhkan performa.
Untuk mengatasinya, literatur menempuh beberapa jalur. Pendekatan personalisasi dan
klasterisasi berusaha menyesuaikan model ke tiap klien, seperti Sentinel yang memakai
knowledge distillation [16] dan FedDB yang mengelompokkan klien dengan DBSCAN [17].
Jalur lain menyelaraskan fitur atau perilaku antar-domain, misalnya FedCross-VAN [18]
dan graph prior pada Entente [11]. Ada pula yang menata arsitektur secara hirarkis,
seperti mist-assisted FL [19], serta studi yang secara eksplisit membandingkan kondisi
IID versus non-IID [20]. Yang menarik, istilah "semantic feature mapping" jarang
disebut secara eksplisit; penyelarasan fitur lebih sering muncul secara implisit.
Survei ini tidak mengusulkan solusi penyelarasan baru—untuk kebutuhan lintas-dataset
kami memakai penyelarasan nama fitur manual yang sudah ada sebagai bagian dari setup.

### 3.3 Adversarial Robustness & Byzantine/Poisoning (SQ3)

Ketahanan model terhadap serangan dibahas dari dua sisi: evasion pada waktu inferensi
dan peracunan pada waktu pelatihan. Pada sisi evasion, adversarial training menjadi
pertahanan yang paling sering diusulkan; Ennaji dkk. [21] melaporkan akurasi 91,23%
pada Edge-IIoTset, SFAT [6] menyoroti "exacerbated heterogeneity" dan menambahkan
mekanisme α-slack, sedangkan HADA [22] melaporkan akurasi 66–73% di bawah serangan
FGSM/PGD. Pada sisi peracunan, pertahanan Byzantine berupaya menolak pembaruan klien
jahat: FedSecIoT [23] dan karya Saha dkk. [7] memakai agregasi multi-Krum, FORT-IDS
[24] mengandalkan agregasi yang tahan outlier, dan serangan label-flipping juga
teramati pada setting FL-NIDS [5]. Khusus untuk DDoS, GADoT [25] memakai GAN untuk
membangkitkan contoh adversarial saat pelatihan. Beberapa karya menyediakan tolok ukur
dan telaah atas lanskap ini [26], [8], [27]. Benang merahnya, trade-off antara
robustness dan akurasi belum tuntas—apalagi pada kondisi non-IID—dan integrasi evaluasi
adversarial dengan setting cross-dataset masih langka. Celah inilah yang kami uji
sendiri pada Bagian 4 (R5–R6), sehingga tema ini hadir dua sisi: sebagai telaah di
sini dan sebagai eksperimen di sana.

### 3.4 Few-Shot, Meta-Learning & Cross-Domain Transfer (SQ2–SQ3)

Tema terakhir menyasar kemampuan mengenali serangan baru dari sedikit contoh. Pada
jalur few-shot, Ceviz dkk. [10] menerapkannya untuk jaringan UAV, sementara FeCoGraph
[28] memakai pembelajaran kontrastif berbasis graf. Pendekatan meta-learning
diwakili Hu dkk. [9] yang merancang federated meta-learning untuk melawan advanced
persistent threat. Untuk transfer lintas-domain, FedPKT [29] memakai transfer
pengetahuan prototipikal, dan pada arah ensemble, karya [30] menggabungkan CNN, LSTM,
dan Transformer serta melaporkan akurasi 98,5% pada enam dataset dengan konsekuensi
kompleksitas yang tinggi. Secara umum, penggabungan penyelarasan semantik dan few-shot
yang diuji benar-benar lintas-dataset masih jarang; survei ini mencatatnya sebagai
celah terbuka, bukan mengisinya.

### 3.5 State-of-the-Art Comparison Table

Tabel 1 merangkum karya representatif FL-NIDS secara kualitatif. Kolom "Cross-dataset?"
dan "Cloud deploy?" adalah penanda yang jarang dibuat survei lain dan langsung
memperlihatkan celah yang kami isi di Bagian 4. Perlu ditegaskan bahwa kolom
"Performa" **tidak sebanding antar-baris**: tiap karya memakai metrik, dataset, dan
setup yang berbeda (mis. akurasi pada satu dataset tidak setara dengan F1 pada dataset
lain), sehingga angka hanya dikutip apa adanya sebagaimana dilaporkan penulis asli.
Justru ketaksebandingan inilah yang memotivasi verifikasi terkontrol pada testbed
seragam di Bagian 4, di mana metode-metode tersebut dibandingkan dengan metrik dan
data yang sama.

*Table 1. Comparison of representative FL-NIDS frameworks.*

| Framework | Fokus | Metodologi kunci | Dataset | Performa (dilaporkan asli) | Cross-dataset? | Cloud deploy? |
|---|---|---|---|---|---|---|
| Entente [11] | GNIDS cross-silo | ACS + graph sketching | OpTC, LANL, Pivoting | High P/R, low FPR | Tidak | Tidak |
| FedAGRU [12] | FL wireless edge | attention + GRU-SVM | KDD'99, CICIDS2017, WSN-DS | High acc, low FAR | Tidak | Tidak |
| FedSecIoT [23] | Byzantine-robust | Multi-Krum | N-BaIoT | 90%+ acc, +60% robust vs FedAvg | Tidak | Tidak |
| FLAD [14] | FL adaptif DDoS | adaptive selection | CIC-DDoS2019 | High F1, cepat konvergen | Tidak | Tidak |
| HADA [22] | privacy-preserving FL | HADA + SHAP + DP | Edge-IIoTset dll | 85–89% acc, 66–73% under adv | Tidak | Edge |
| Ensemble+XAI [30] | ensemble + XAI | CNN+LSTM+Transformer + GAN def | 6 dataset | 98,5% acc, AUC>0,99 | Multi-dataset | Tidak |
| Hu dkk. [9] | few-shot meta vs APT | federated meta-learning | IDS datasets | adaptasi cepat | Sebagian | Tidak |

---

## 4. Reproduction Study & Adversarial Experiments on AWS

> **Bagian pembeda utama.** Kami menjalankan metode terpublikasi pada **satu testbed
> AWS seragam** dan melaporkan angka yang sebanding. **Semua angka = `[TBD]`** sampai
> eksperimen dieksekusi. Detail operasional (infra, runbook, fase) di Lampiran B.

### 4.1 Testbed design

Sebelum pelatihan, kedua dataset tidak dipakai dengan seluruh fiturnya. CSE-CIC-IDS2018
diekstrak dengan CICFlowMeter (sekitar 80 fitur) sedangkan UNSW-NB15 dengan Argus/Bro
(42 fitur), sehingga skema fiturnya berbeda. Agar kedua client berbicara dalam ruang
fitur yang sama, kami hanya memakai **sembilan fitur** yang memiliki padanan nama 1:1
di kedua ekstraktor—durasi aliran, jumlah dan volume paket arah maju/mundur, rata-rata
ukuran paket, dan laju—sebagai skema bersama (Figure 1). Fitur yang khas pada satu
ekstraktor saja (misalnya `ct_srv_src`, TTL, atau `trans_depth` pada UNSW; fitur IAT
atau flag pada CICFlowMeter) tidak memiliki padanan dan karenanya dibuang. Angka
sembilan ini adalah konsekuensi dari irisan kedua ekstraktor, bukan pilihan desain;
penyelarasan nama fitur manual semacam ini sudah lazim di literatur cross-dataset
[5] dan kami perlakukan sebagai setup, bukan kontribusi. Tiap client lalu menerapkan
skema sembilan fitur ini **pada datanya sendiri**.

![Penyelarasan fitur: hanya sembilan fitur beririsan di kedua ekstraktor yang dipakai;
fitur spesifik-ekstraktor dibuang.](figure-fed/fig_feature_alignment.png)

*Figure 1. Cross-dataset feature alignment.*

Arsitektur federasi yang kami bangun mengikuti pola horizontal cross-silo dengan satu
**aggregator** dan dua **client**, masing-masing memegang satu dataset—Client-CIC
untuk CSE-CIC-IDS2018 dan Client-UNSW untuk UNSW-NB15 (Figure 2). Setiap client
melatih model pada datanya **sendiri** tanpa pernah mengirim data mentah; yang
dipertukarkan hanyalah bobot model. Normalisasi fitur (z-score) juga dihitung **lokal
per-client** memakai statistik masing-masing, sehingga tidak ada statistik data yang
bocor antar-client—menjaga prinsip privasi FL.

Aliran proses per ronde mengikuti FedAvg standar. Pada tiap ronde, aggregator
mengirimkan model global ke kedua client; setiap client melatihnya secara lokal lalu
mengembalikan pembaruan bobotnya; aggregator menggabungkan kedua pembaruan dengan
FedAvg (rata-rata berbobot ukuran data) untuk membentuk model global ronde berikutnya.
Siklus ini diulang selama 100 ronde. Pada realisasinya, ketiga simpul dijalankan
sebagai tiga instans EC2 `t3.medium` dan pertukaran bobot dimediasi melalui Amazon S3
(tanpa soket langsung antar-node), tetapi detail infrastruktur ini bersifat
operasional dan tidak mengubah model FL itu sendiri; pengukuran biaya komunikasinya
dilaporkan pada R4.

![Arsitektur federated learning: satu aggregator (FedAvg) dan dua client (CIC, UNSW)
yang bertukar model global dan pembaruan lokal.](figure-fed/fig_fl_architecture.png)

*Figure 2. Federated learning architecture.*

- **Topologi**: 1 agregator + K client (K=2 untuk cross-dataset; K=4–10 untuk partisi
  non-IID per-dataset); 3 EC2 publik nyata, transport bobot via S3, akses via SSM.
- **Dataset**: CSE-CIC-IDS2018 ↔ UNSW-NB15. Skema fitur diselaraskan dengan
  penyelarasan nama fitur manual (9 pasang padanan dasar antar-tool ekstraktor) —
  metode yang sudah ada, diperlakukan sebagai setup, bukan kontribusi.
- **Model terkontrol**: arsitektur ML/DL ringan identik di semua skenario; baseline
  centralized sebagai sanity-check.
- **Metrik**: MCC (utama), recall/precision/F1, balanced-accuracy; + biaya FL
  (rounds-to-converge, bytes/round, latensi, throughput). Multi-seed {13,42,101,202,303}.

### 4.2 Claims under test
> Dua kelompok: **(A) reproduksi** klaim inti (R1–R4) dan **(B) eksperimen adversarial**
> (R5–R6). Semua memakai metode terpublikasi; yang baru adalah buktinya.

**(A) Reproduksi klaim inti FL-NIDS**
1. **R1 — FedAvg vs FedProx (SQ3/SQ4).** Klaim: FedProx lebih stabil di non-IID [6],[14]. Hasil: pada setting lintas-dataset (klien CIC + UNSW, rata-rata tiga seed), FedAvg dan FedProx **tidak berbeda bermakna**: FedAvg MCC 0,572, FedProx(μ=0,01) 0,573, FedProx(μ=0,1) 0,571 — selisih ≈0,001, dan ketiganya konvergen cepat (7–11 ronde). Pola yang sama muncul pada fondasi single-dataset (α=0,1): FedAvg 0,555 vs FedProx(μ=0,1) 0,553. Di kedua setting FedProx **tidak** memperbaiki FedAvg; arah klaim tidak bertahan pada rentang hyperparameter yang kami uji.
2. **R2 — Dampak non-IID (SQ2/SQ4).** Klaim: performa FL turun seiring heterogenitas [5]; sweep Dirichlet α. Hasil: **dampaknya bergantung domain** — sebuah nuansa yang jarang disorot. Pada klien **CIC**, pola klasik muncul: MCC relatif stabil pada α besar (0,512 di α=100) lalu runtuh dan menjadi sangat tak stabil pada α rendah (0,387 di α=0,1, dengan std melonjak ke 0,27). Sebaliknya pada klien **UNSW**, performa **tidak** turun seiring non-IID — justru datar bahkan sedikit naik (0,621 di α=100; 0,655 di α=0,1), karena kelas UNSW relatif mudah dipisah sehingga partisi timpang pun tak merusak. Jadi klaim "non-IID menurunkan FL" **bertahan pada CIC tetapi tidak pada UNSW**: efeknya nyata namun tidak universal, tergantung separabilitas domain. Pada fondasi single-dataset penurunan juga tegas (0,826 di α=100 → 0,555 di α=0,1, CI membengkak ~46×).
3. **R3 — Cross-dataset FL (SQ4).** Klaim: FL lintas-dataset sulit/menurun tajam [5]; uji dengan alignment manual pada testbed AWS tiga-EC2 (100 ronde FedAvg, klien CIC + UNSW). Hasil: klaim **bertahan telak**. Model federated runtuh ke MCC **−0,026** (recall 0,058, precision 0,260) — praktis setara tebak acak. Sebagai batas atas, model *centralized* (data kedua domain digabung, tak diizinkan di FL nyata) hanya mencapai MCC 0,545; sedangkan *local-only* juga buruk (CIC 0,115; UNSW −0,110). Dengan kata lain, menyatukan dua jaringan yang sangat berbeda lewat FedAvg dan penyelarasan sembilan fitur generik **gagal mentransfer**: tidak ada model tunggal yang baik di kedua domain sekaligus. Arah klaim Lavaur dkk. [5] terkonfirmasi di lingkungan kami.
4. **R4 — Biaya cloud nyata (SQ5).** Efisiensi komunikasi FL [15]: komunikasi/latensi per ronde di AWS. Hasil: model ringan 9.601 parameter → 76,8 KB per unggahan klien, sehingga ≈300 KB lalu lintas agregator per ronde untuk dua klien (dua arah) — ongkos komunikasi sangat kecil. Dari jejak waktu objek pada run S\_R3 (tiga EC2 `t3.medium`, bobot via S3), 100 ronde memakan ≈27 menit (round 0 → ronde final), yakni ≈16 detik per ronde termasuk sinkronisasi S3; angka ini diukur saat dua run berjalan paralel sehingga menanggung CPU bersama (batas atas latensi, dilaporkan apa adanya).

Sebagai pemeriksaan dasar bahwa federasi memang bermanfaat, kami membandingkan model
federated dengan baseline *local-only* (tiap klien melatih sendiri tanpa agregasi)
lintas lima seed: federated mencapai MCC 0,574 (CI95 0,565–0,583) versus local-only
0,364 (0,306–0,422), selisih +0,210 yang signifikan secara statistik (paired *t*-test
p=0,0005). Jadi agregasi federated memberi keuntungan nyata di atas pelatihan lokal
terisolasi — prasyarat yang harus dipenuhi sebelum klaim-klaim lanjutan bermakna.

**(B) Eksperimen adversarial**
5. **R5 — Kerentanan evasion (SQ6).** Klaim: NIDS ML rapuh terhadap evasion [25],[26],[8]; terapkan FGSM/PGD + saliency/JSMA (dibatasi agar flow tetap valid) pada model FL hasil R3, sapu ε ∈ {0,05; 0,1; 0,2; 0,5}. Hasil: klaim **bertahan telak**. Bahkan pada ε kecil (0,05), *attack success rate* sudah 0,96 untuk ketiga serangan; pada ε ≥ 0,2 FGSM/PGD mencapai ASR 1,00 (seluruh serangan yang semula terdeteksi berhasil lolos), menekan MCC dari −0,026 ke −0,15. JSMA sedikit kurang agresif (ASR 0,96–0,99) namun tetap sangat tinggi. Model FL lintas-dataset ini nyaris sepenuhnya dapat dielak.
6. **R6 — Adversarial training sebagai defense (SQ6).** Klaim: adversarial training menaikkan robustness dengan trade-off [6],[21],[27]; latih ulang FL dengan adv-examples (run S\_R6) lalu bandingkan dengan model bersih (S\_R3). Hasil: **tidak bertahan pada setting ini**, dengan nuansa yang kami laporkan jujur. Adversarial training sedikit menaikkan MCC *bersih* (−0,026 → 0,070) tetapi **gagal** pada robustness: MCC di bawah PGD justru memburuk (−0,152 → −0,222). Jadi menambahkan adv-examples pada FL lintas-dataset yang sudah lemah tidak memulihkan ketahanan evasion — menggemakan batas adversarial training pada domain sulit yang juga teramati di literatur. (Catatan: MCC absolut rendah di R5/R6 karena basis R3 sendiri sudah runtuh; nilai dibaca sebagai arah, bukan performa mutlak.)

### 4.3 Results table

> **Catatan sumber angka.** R1, R2, R4-komunikasi, dan uji signifikansi FL-vs-lokal
> adalah **simulasi terkontrol** di notebook (logika FedAvg/FedProx/MLP/z-score identik
> dengan node EC2 `fed_node_survey.py`); R1/R4 memakai klien CIC+UNSW (tiga seed), R2
> menyapu Dirichlet α per domain. **R3, R5, R6 dijalankan nyata** pada testbed AWS
> tiga-EC2 `t3.medium` (100 ronde FedAvg, bobot via S3, akses SSM): R3 dari run bersih
> (S\_R3), R6 dari run adversarial-training (S\_R6), R5 adalah evaluasi evasion offline
> terhadap model S\_R3. R4-latensi diturunkan dari jejak waktu objek S3 per ronde.
> Fondasi single-dataset (CSE-CIC-IDS2018, K=4, lima seed) dilaporkan sebagai pembanding.
> Perbedaan simulasi vs run EC2 dicatat terbuka di Bagian 5.1.

*Table 2. Verification results for the six FL-NIDS claims.*

| Klaim | Jenis | Sumber literatur | Metrik | Angka dilaporkan asli | **Angka lab kami** | Bertahan? |
|---|---|---|---|---|---|---|
| R1 FedProx>FedAvg (non-IID) | reproduksi | [6][14] | MCC (cross-dataset, 3 seed) | [kutip] | FedAvg 0,572 vs FedProx(μ=0,1) 0,571; selisih ≈0,001, tak bermakna | **Tidak** |
| R2 non-IID menurunkan FL | reproduksi | [5] | MCC vs α per domain | [kutip] | CIC: 0,512→0,387 (α=100→0,1), runtuh & tak stabil. UNSW: 0,621→0,655, datar | **Bergantung domain** (ya di CIC, tidak di UNSW) |
| R3 cross-dataset FL sulit | reproduksi | [5] | MCC | [kutip] | federated −0,026 vs centralized 0,545; FL cross-dataset runtuh | **Ya** |
| R4 biaya komunikasi | reproduksi | [15] | bytes/round, latensi | [kutip] | 76,8 KB/unggahan; ≈300 KB/ronde (2 klien); ≈16 s/ronde (CPU bersama) | — |
| R5 evasion FGSM/PGD/JSMA | adversarial | [25][26][8] | attack success rate, ΔMCC | [kutip] | ASR 0,96 di ε=0,05; 1,00 di ε≥0,2 (FGSM/PGD); MCC −0,03→−0,15 | **Ya** (sangat rapuh) |
| R6 adversarial training | adversarial | [6][21][27] | robust MCC, Δclean-acc | [kutip] | clean −0,026→0,070 tapi robust −0,152→−0,222 (memburuk) | **Tidak** |

Dua catatan metodologis perlu ditekankan dalam membaca Tabel 2. Pertama, verifikasi
kami mengukur apakah *arah* sebuah klaim bertahan di testbed yang seragam, bukan meniru
persis setup penulis asli; selisih angka absolut terhadap karya asli karenanya wajar
dan bukan indikasi kegagalan reproduksi. Kedua, eksperimen adversarial pada R5 dan R6
bekerja di ruang fitur aliran (tabular), bukan pada citra: perturbasi FGSM/PGD/JSMA
kami batasi agar aliran tetap valid—non-negatif, konsisten antar-fitur, dan hanya pada
fitur yang realistis dapat dimanipulasi penyerang—sehingga serangannya lebih
konservatif daripada serangan tak-terkendala pada domain citra. Konsekuensi kedua hal
ini terhadap generalisasi temuan dibahas lebih lanjut pada Bagian 5.1.

---

## 5. Discussion: Gaps, Research Agenda & Threats to Validity

Menyatukan telaah tematik (Bagian 3) dengan hasil verifikasi (Bagian 4) memunculkan
sejumlah celah yang saling berkaitan, dan beberapa di antaranya justru dipertegas oleh
temuan kami sendiri. Celah paling mencolok adalah lemahnya integrasi antara federated
learning dan robustness adversarial ketika diuji secara lintas-dataset. Literatur
cenderung membahas keduanya secara terpisah—ada yang menguji FL lintas-jaringan, ada
yang menguji evasion—tetapi jarang menggabungkannya pada satu eksperimen. Hasil R5 dan
R6 memperlihatkan mengapa penggabungan itu penting: model FL lintas-dataset yang sudah
rapuh ternyata nyaris sepenuhnya dapat dielak, dan adversarial training—pertahanan yang
paling sering disarankan—gagal memulihkannya. Dengan kata lain, celah ini bukan sekadar
kekosongan literatur, melainkan persoalan nyata yang baru terlihat saat kedua dimensi
diuji bersama.

Celah berikutnya menyangkut cara menyelaraskan fitur antar-jaringan. Runtuhnya FL
lintas-dataset pada R3 menunjukkan bahwa penyelarasan nama fitur yang generik—sekadar
memetakan sembilan kolom yang namanya bersesuaian—tidak cukup untuk mentransfer
pengetahuan antara dua jaringan yang sangat berbeda. Penyelarasan yang sadar-semantik,
yang mempertimbangkan makna dan distribusi fitur alih-alih sekadar namanya, masih
merupakan persoalan terbuka; survei ini mencatatnya sebagai celah, bukan mengisinya.
Pada arah yang sama, few-shot dan meta-learning lintas-dataset yang digabung dengan
evaluasi adversarial juga masih terbatas di literatur.

Dua celah terakhir bersifat lebih praktis. Pertama, skalabilitas dan heterogenitas pada
skala produksi—ribuan klien dengan lalu lintas nyata—nyaris tidak memiliki bukti
empiris; sebagian besar studi, termasuk kami, bekerja pada sedikit klien. Kedua, bukti
deployment dan pengukuran biaya di cloud publik hampir tidak ada, suatu kekosongan yang
sebagian kami isi lewat pengukuran komunikasi dan latensi nyata pada R4. Dari pemetaan
ini, agenda riset yang kami pandang paling mendesak adalah: encoder penyelaras fitur
yang sadar-semantik untuk memperbaiki transfer lintas-dataset, pertahanan evasion yang
sadar-arah dan sadar-domain alih-alih adversarial training statis, protokol evaluasi
lintas-dataset yang bebas kebocoran, serta validasi pada testbed cloud yang lebih
mendekati skala produksi.

### 5.1 Threats to Validity

Beberapa hal membatasi sejauh mana temuan kami dapat digeneralisasi, dan kami
menyampaikannya secara terbuka agar pembaca dapat menimbang bobot setiap klaim.
Pertama, verifikasi kami mengukur apakah *arah* sebuah klaim bertahan di lingkungan
yang setara, bukan mereplikasi persis setiap detail setup penulis asli. Perbedaan
dataset, arsitektur model, dan hyperparameter antara reproduksi kami dan karya asli
berarti selisih angka absolut memang diharapkan; yang kami nilai adalah pola dan
arahnya, bukan kecocokan nilai per digit.

Kedua, ruang lingkup eksperimen kami sempit secara sengaja. Kami hanya memakai dua
dataset benchmark (CSE-CIC-IDS2018 dan UNSW-NB15) dan sedikit klien, sehingga temuan
seperti "dampak non-IID bergantung domain" perlu diuji pada lebih banyak pasangan
jaringan sebelum dapat dianggap umum. Anggaran cloud juga membatasi jumlah run dan
seed yang dapat kami jalankan; angka dilaporkan apa adanya beserta interval
kepercayaannya, tetapi presisi statistik pada kondisi non-IID berat tetap terbatas.
Untuk komponen telaah pustaka, potensi bias seleksi kami mitigasi dengan protokol
pencarian yang eksplisit (Bagian 2), meski tidak ada protokol yang sepenuhnya bebas
bias.

Ketiga, dan paling penting untuk ditafsirkan dengan hati-hati, eksperimen adversarial
kami (R5–R6) bekerja pada ruang fitur aliran (tabular), bukan pada paket mentah.
Perturbasi FGSM/PGD/JSMA kami batasi agar aliran tetap valid—nilai non-negatif,
konsisten antar-fitur, dan hanya pada fitur yang realistis dapat dimanipulasi
penyerang. Akibatnya, serangan kami lebih konservatif daripada serangan tak-terkendala
pada domain citra, dan hasil attack success rate harus dibaca dalam kerangka threat
model yang kami asumsikan (pengetahuan white/black-box, kapabilitas terbatas pada
fitur yang dapat diubah). Kerentanan nyata di lapangan bisa berbeda, bergantung pada
seberapa besar kendali yang sesungguhnya dimiliki penyerang atas lalu lintas.

---

## 6. Conclusion

Survei ini menggabungkan telaah tematik literatur FL-NIDS terkini (2020–2026) dengan
sesuatu yang jarang dilakukan survei lain: verifikasi reproduktif atas klaim-klaim
representatifnya pada satu testbed AWS yang seragam. Alih-alih sekadar merangkum apa
yang dilaporkan penulis asli, kami menguji ulang apakah arah tiap klaim bertahan di
lingkungan yang setara, dan melaporkan hasilnya apa adanya—termasuk ketika klaim itu
tidak bertahan.

Dari enam klaim yang diuji, gambarannya beragam. Dua klaim terkonfirmasi: FL
lintas-dataset memang sulit—menggabungkan CSE-CIC-IDS2018 dan UNSW-NB15 lewat FedAvg
membuat MCC runtuh ke −0,03, jauh di bawah batas atas terpusat 0,55; dan model sangat
rapuh terhadap evasion, dengan attack success rate 0,96 pada perturbasi kecil hingga
1,00 pada perturbasi sedang untuk FGSM dan PGD. Satu klaim bergantung domain: dampak
non-IID yang ditekankan literatur nyata pada klien CIC (MCC jatuh dari 0,51 ke 0,39
seiring heterogenitas meningkat) tetapi hampir tidak terlihat pada UNSW yang kelasnya
lebih mudah dipisah—sebuah nuansa yang menunjukkan bahwa "non-IID menurunkan FL" tidak
berlaku universal. Dua klaim tidak bertahan pada rentang yang kami uji: FedProx tidak
mengungguli FedAvg secara bermakna, dan adversarial training—meski sedikit menaikkan
akurasi pada trafik bersih—gagal memulihkan, bahkan memperburuk, robustness pada
setting lintas-dataset yang sudah lemah. Di sisi biaya, FL-NIDS dengan model ringan
terbukti murah secara komunikasi (≈300 KB per ronde) dengan latensi ≈16 detik per
ronde pada tiga EC2.

Kontribusi utama makalah ini bukan sebuah metode baru, melainkan bukti: sebuah
baseline reproduktif beranggaran cloud wajar yang memperlihatkan dengan jelas mana
klaim FL-NIDS yang kokoh dan mana yang rapuh ketika diuji secara terkontrol. Temuan
bahwa integrasi FL lintas-dataset dengan robustness adversarial masih jauh dari
memadai menegaskan celah terbuka yang penting (gap a). Arah lanjutan yang kami
sarankan mencakup penyelarasan fitur yang sadar-semantik untuk memperbaiki transfer
lintas-dataset, pertahanan evasion yang sadar-arah dan sadar-domain, serta evaluasi
pada skala klien dan trafik yang lebih mendekati produksi. Seluruh protokol, skrip,
dan konfigurasi cloud kami sediakan agar komunitas—khususnya di Indonesia—dapat
mereproduksi dan membangun di atasnya.

---

## References

> Gaya IEEE, 30 referensi, dinomori sesuai urutan kemunculan pertama dalam naskah.
> Semua entri punya DOI kecuali satu yang ditandai (verifikasi saat finalisasi).

[1] A. Khraisat, A. Alazab, T. Jan, and A. Gopez, "Survey on federated learning for intrusion detection system: concept, architectures, aggregation strategies, challenges, and future directions," *ACM Comput. Surv.*, 2024, doi: 10.1145/3687124.

[2] J. L. Hernández-Ramos *et al.*, "Intrusion detection based on federated learning: a systematic review," *ACM Comput. Surv.*, Apr. 2025, doi: 10.1145/3731596.

[3] A. A. Wardana and P. Sukarno, "Taxonomy and survey of collaborative intrusion detection system using federated learning," *ACM Comput. Surv.*, Oct. 2024, doi: 10.1145/3701724.

[4] E. V. Fedorchenko, E. Novikova, and A. N. Shulepov, "Comparative review of the intrusion detection systems based on federated learning: advantages and open challenges," *Algorithms*, vol. 15, no. 7, p. 247, 2022, doi: 10.3390/a15070247.

[5] L. Lavaur, Y. Busnel, and F. Autrel, "Demo: highlighting the limits of federated learning in intrusion detection," in *Proc. IEEE Int. Conf. Distrib. Comput. Syst. (ICDCS)*, 2024, pp. 1416–1419, doi: 10.1109/ICDCS60910.2024.00135.

[6] J. Zhang *et al.*, "Combating exacerbated heterogeneity for robust models in federated learning (SFAT)," *arXiv:2303.00250*, 2023, doi: 10.48550/arXiv.2303.00250.

[7] S. Saha, M. I. Sayed, M. Faezipour, and S. Bhatt, "Resilient federated learning for DDoS detection with multi-Krum aggregation and anomaly detection," in *Proc. IEEE SmartNets*, 2025, doi: 10.1109/SmartNets65254.2025.11106859.

[8] S. Saini, A. Chennamaneni, and B. A. Sawyerr, "A review of the duality of adversarial learning in network intrusion: attacks and countermeasures," *arXiv:2412.13880*, 2024, doi: 10.48550/arXiv.2412.13880.

[9] Y. Hu, J. Wu, G. Li, J. Li, and J. Cheng, "Privacy-preserving few-shot traffic detection against advanced persistent threats via federated meta learning," *IEEE Trans. Netw. Sci. Eng.*, vol. 11, pp. 2549–2560, 2024, doi: 10.1109/TNSE.2023.3304556.

[10] Ö. Ceviz, S. Şen, and P. Sadioglu, "Distributed intrusion detection in dynamic networks of UAVs using few-shot federated learning," *arXiv:2501.13213*, 2025, doi: 10.48550/arXiv.2501.13213.

[11] J. Xu, C. Li, Y. Zheng, and Z. Li, "Entente: cross-silo intrusion detection on network log graphs with federated learning," *arXiv:2503.14284*, 2025, doi: 10.48550/arXiv.2503.14284.

[12] Z. Chen, N. Lv, P. Li, Y. Fang, K. Chen, and W. Pan, "Intrusion detection for wireless edge networks based on federated learning," *IEEE Access*, vol. 8, pp. 217463–217472, 2020, doi: 10.1109/ACCESS.2020.3041793.

[13] J. Mao, Z. Wei, B. Li, R. Zhang, and L. Song, "FedIn-NID: a federated learning framework for network intrusion detection in large-scale heterogeneous industrial IoT," *IEEE Trans. Inf. Forensics Security*, 2025, doi: 10.1109/TIFS.2025.3602226.

[14] R. Doriguzzi-Corin and D. Siracusa, "FLAD: adaptive federated learning for DDoS attack detection," *arXiv:2205.06661*, 2022, doi: 10.48550/arXiv.2205.06661.

[15] R. Doriguzzi-Corin, S. Cretti, and D. Siracusa, "Resource-efficient federated learning for network intrusion detection," in *Proc. IEEE Conf. Netw. Softwarization (NetSoft)*, 2024, doi: 10.1109/NetSoft60951.2024.10588938.

[16] G. Singh, K. Singh, P. Rajalakshmi, and Y. Xong, "Sentinel: dynamic knowledge distillation for personalized federated intrusion detection in heterogeneous IoT networks," *arXiv:2510.23019*, 2025, doi: 10.48550/arXiv.2510.23019.

[17] Y.-C. Lee, W.-C. Chien, and Y.-C. Chang, "FedDB: a federated learning approach using DBSCAN for DDoS attack detection," *Appl. Sci.*, vol. 14, no. 22, 2024, doi: 10.3390/app142210236.

[18] M. Khalid, U. Zukaib, M. Al-Rakhami, and A. M. Alamri, "FedCross-VAN: federated cross-domain behavior alignment for VANET intrusion detection," *Trans. Emerg. Telecommun. Technol.*, vol. 37, 2025, doi: 10.1002/ett.70309.

[19] S. Ali, R. Alireza, and A. Mahmood, "Mist-assisted federated learning for intrusion detection in heterogeneous IoT networks," *arXiv:2511.00271*, 2025, doi: 10.48550/arXiv.2511.00271.

[20] M. Benkaddour, "Enhancing federated learning for privacy preserving intrusion detection in IoT networks," *Przegląd Elektrotechniczny*, 2025, doi: 10.15199/48.2025.09.21.

[21] E. M. Ennaji, S. E. Hajla, Y. Maleh, and S. Mounir, "Adversarially robust federated deep learning models for intrusion detection in IoT," *Indones. J. Electr. Eng. Comput. Sci.*, vol. 37, no. 2, p. 937, 2024, doi: 10.11591/ijeecs.v37.i2.pp937-947.

[22] G. Chandu, T. S. Karthik, and B. Parag, "Federated learning for distributed IoT security: a privacy-preserving approach to intrusion detection," *IEEE Access*, 2025, doi: 10.1109/ACCESS.2025.3592481.

[23] S. K. Ghimire and S. Lodh, "FedSecIoT: a federated learning framework for collaborative and privacy-preserving botnet detection in IoT with adversarial robustness," in *Proc. IEEE SILCON*, 2025, doi: 10.1109/SILCON67893.2025.11327096.

[24] A. Al Mazroa *et al.*, "FORT-IDS: a federated, optimized, robust and trustworthy intrusion detection system for IIoT security," *Sci. Rep.*, 2025, doi: 10.1038/s41598-025-31025-x.

[25] M. S. I. Sajid *et al.*, "GADoT: GAN-based adversarial training for robust DDoS attack detection," *arXiv:2201.13102*, 2022, doi: 10.48550/arXiv.2201.13102.

[26] H. Dadhwal, M. de Abreu, N. Parvizi, and S. Saha, "Benchmarking the adversarial resilience of machine learning models for DDoS detection," *Array*, vol. 29, p. 100664, 2026, doi: 10.1016/j.array.2025.100664.

[27] I. Debicha, T. Debatty, J.-M. Dricot, and W. Mees, "Adversarial training for deep learning-based intrusion detection systems," *arXiv:2104.09852*, 2021, doi: 10.48550/arXiv.2104.09852.

[28] Q. Mao, X. Lin, G. Li, and J. Li, "FeCoGraph: label-aware federated graph contrastive learning for few-shot network intrusion detection," *IEEE Trans. Inf. Forensics Security*, 2025, doi: 10.1109/TIFS.2025.3541890.

[29] K. Yin, J. Zhang, Z. Xia, and C. Yu, "FedPKT: robust cross-domain few-shot intrusion detection via prototypical knowledge transfer," *IEEE Trans. (early access)*, doc. 11360061. [DOI belum terbit — verifikasi saat finalisasi.]

[30] K. S, V. Malathi, B. J. Lakshmi, A. V. Sriharsha, T. D. Kumar, and T. Lakshmibai, "Federated and explainable intrusion detection systems for large-scale heterogeneous networks using ensemble deep learning," in *Proc. IEEE ICACRS*, 2025, doi: 10.1109/ICACRS67045.2025.11324277.

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

**Pembeda vs Paper 4 (`paper6-federated.tex`) — anti-salami.** Paper 4 = *research paper*
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

**Antisipasi keberatan reviewer (jawab di Bagian 5.1):**
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
  `aws/fed-runbook-survey.md`, dan 7 notebook `notebooks/02_survey-tanpaSFM/` (s01,s03,s05,s06,s07,s14,s15).

**TODO:**
1. [ ] **Jalankan di AWS/SageMaker** (butuh kredensial + data): s01 → EC2 run (R3,R6) →
       s03/s14/s15/s05/s06/s07 → tarik CSV. (Kode siap; angka masih `[TBD]`.)
2. [ ] Isi tabel §4.3 dari CSV `survey_out/` + S3 `federated_survey/results/`.
3. [ ] Lengkapi tabel komparatif §3.5 dari `literature_review` §6.
4. [ ] Kutip angka "dilaporkan asli" tiap klaim R1–R6.
5. [ ] Naratifkan Bagian 3, 5, 6 (saat ini bullet).
6. [ ] Finalkan Abstrak & Bagian 6 (Conclusion) setelah angka masuk.
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
- **Notebook survei** (`notebooks/02_survey-tanpaSFM/`): `s01_fed_data_partition.ipynb` (sudah; reframe
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
