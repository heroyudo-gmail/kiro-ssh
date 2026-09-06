# Dokumen Kebutuhan

## Pendahuluan

Fitur ini mendefinisikan prosedur eksekusi eksperimen **T10** (pengukuran False Alarm Rate / FAR Model A — XGBoost 9-fitur SFM — pada trafik REAL di AWS, arsitektur 3-EC2 pola NIDS-01, region ap-southeast-1) secara **BERTAHAP** dengan pola *ramp* lima tahap (S0 sampai S4). Setiap tahap memiliki **gate terukur** yang harus lulus sebelum eksekusi boleh naik ke tahap berikutnya.

Motivasi utama: runbook yang ada (`aws/runbook.md`) sudah baik untuk deploy/resume/teardown, tetapi langsung melompat ke percobaan "24 jam kontinu" tanpa tahap validasi bertahap. Risiko yang dikhawatirkan: bila langsung menjalankan 24 jam lalu ada error di tengah (mis. *feature/scaler mismatch* satuan, capture 0 flow, kegagalan rotasi/upload), biaya jam-jaman terbuang dan hasil tidak dapat dipakai. Ramp bertahap menangkap kesalahan seperti itu **dini** (dalam hitungan menit) sebelum membuang biaya besar.

Fitur ini juga mencakup perbaikan bug terverifikasi pada `aws/unsw_extract_infer.py` (fitur `duration` diisi dalam milidetik padahal Model A dilatih dengan detik — salah faktor 1000×) sebagai prasyarat sebelum tahap pertama.

### Prinsip Kejujuran Data (Konstrain Mutlak)

Seluruh angka yang akan masuk ke paper harus berasal dari eksperimen NYATA yang benar-benar dieksekusi. Tidak boleh ada nilai hasil yang dikarang, ditebak, atau diisi sebagai *placeholder* yang menyerupai hasil nyata. Slot hasil yang belum diisi harus tetap kosong atau ditandai eksplisit sebagai belum diisi. Prinsip ini dinyatakan sebagai kebutuhan formal (Requirement 1) dan berlaku di seluruh tahap.

## Glosarium

- **T10**: Eksperimen pengukuran False Alarm Rate Model A pada trafik real di AWS.
- **Model A**: Model klasifikasi XGBoost 9-fitur SFM, dilatih pada pemetaan UNSW-NB15 ↔ CIC. Berkas: `modelA_9feat.json` + `deploy_meta_9feat.json`.
- **FAR (False Alarm Rate)**: Proporsi flow benign yang diprediksi sebagai attack. Pada Fase 1 (tanpa serangan) seluruh flow benign, sehingga setiap prediksi attack dihitung sebagai *false alarm*. FAR = jumlah false alarm / jumlah flow.
- **Ramp**: Rangkaian eksekusi bertahap S0 → S1 → S2 → S3 → S4 dengan durasi meningkat.
- **Tahap S0 (Smoke)**: Uji cepat ~2–3 menit untuk memastikan pipeline berjalan end-to-end dan sanity fitur lolos.
- **Tahap S1**: Eksekusi 10 menit dengan gate FAR masuk akal dan cek satuan fitur.
- **Tahap S2**: Eksekusi 30 menit dengan gate rotasi pcap, upload/unduh S3, dan konsistensi FAR.
- **Tahap S3**: Eksekusi 2 jam dengan gate stabilitas FAR antar-segmen.
- **Tahap S4**: Eksekusi 24 jam dengan gate hasil layak paper.
- **Gate**: Kriteria terukur yang harus dipenuhi sebelum menaikkan tahap; kegagalan gate memicu prosedur STOP.
- **Prosedur STOP**: Penghentian ramp saat gate gagal; melarang naik tahap sampai penyebab didiagnosis dan diperbaiki.
- **Sanity Fitur**: Pemeriksaan bahwa nilai fitur real berada dalam rentang satuan yang benar (mis. `duration` dalam detik, bukan skala ribuan yang menandakan milidetik).
- **Feature-Scaler Mismatch**: Ketidakcocokan satuan/skala antara fitur real dan statistik training (`scaler_mean`, `scaler_scale`), terdeteksi lewat z-score ekstrem.
- **Z-of-mean**: Untuk tiap fitur, `(mean_fitur_real - scaler_mean) / scaler_scale`; nilai ekstrem menandakan mismatch satuan/scaler.
- **Analyzer**: EC2 (private) yang menjalankan NFStream + inferensi XGBoost + metrik.
- **Target**: EC2 (private) tempat capture trafik dilakukan (pelajaran NIDS-01).
- **Attacker**: EC2 (public); tidak dipakai pada Fase 1 (FAR).
- **IFACE**: Interface jaringan spesifik untuk capture (mis. `ens5`); `-i any` menyebabkan enkapsulasi SLL sehingga NFStream membaca 0 flow.
- **Runbook**: Berkas `aws/runbook.md` berisi prosedur deploy/resume/teardown.
- **Skrip Ekstraksi**: Berkas `aws/unsw_extract_infer.py` (ekstraksi 9 fitur + inferensi).
- **S3 Bucket**: `ssh-detection-features-232032302717`, prefix `unsw-far/` (subfolder `models/`, `scripts/`, `captures/`, `results/`).
- **Operator**: Orang yang menjalankan prosedur ramp secara manual mengikuti dokumen.

## Requirements

### Requirement 1: Kejujuran Data Eksperimen

**User Story:** Sebagai penulis paper NIDS, saya ingin memastikan setiap angka hasil berasal dari eksperimen nyata, sehingga klaim ilmiah dalam paper dapat dipertanggungjawabkan.

#### Acceptance Criteria

1. THE Prosedur_Ramp SHALL mencatat setiap nilai hasil (FAR, jumlah flow, latensi, throughput) hanya dari keluaran eksekusi nyata yang tersimpan di berkas hasil (`far_log.jsonl`, `*_flows.csv`, `*_metrics.json`).
2. WHERE sebuah slot hasil belum memiliki nilai dari eksekusi nyata, THE Prosedur_Ramp SHALL membiarkan slot tersebut kosong atau menandainya secara eksplisit sebagai belum diisi.
3. IF sebuah nilai hasil tidak dapat ditelusuri ke berkas keluaran eksekusi nyata, THEN THE Prosedur_Ramp SHALL menolak pencatatan nilai tersebut sebagai hasil.
4. THE Prosedur_Ramp SHALL mencatat sumber (nama berkas keluaran dan stempel waktu) untuk setiap nilai hasil yang dipakai di paper.

### Requirement 2: Perbaikan Bug Fitur Duration Sebelum Ramp

**User Story:** Sebagai operator eksperimen, saya ingin fitur `duration` dihitung dalam satuan detik sesuai training Model A, sehingga FAR yang dihasilkan tidak ngawur akibat kesalahan satuan 1000×.

#### Acceptance Criteria

1. THE Skrip_Ekstraksi SHALL menghitung fitur `duration` dalam satuan detik menggunakan `dur_s` (yaitu `bidirectional_duration_ms / 1000`).
2. IF sebuah flow memiliki durasi nol, THEN THE Skrip_Ekstraksi SHALL mengisi fitur `duration` dengan nilai 0 dan mencegah nilai NaN merembes ke fitur `duration`.
3. THE Skrip_Ekstraksi SHALL mempertahankan perhitungan `dst_load` sebagai `dst2src_packets / dur_s` (paket per detik) tanpa perubahan, sesuai pemetaan training `dload` ke CIC `Bwd Pkts/s`.
4. THE Skrip_Ekstraksi SHALL mempertahankan perhitungan `src_load` sebagai `src2dst_bytes / dur_s` (byte per detik) tanpa perubahan.
5. WHEN Skrip_Ekstraksi telah diperbaiki, THE Prosedur_Ramp SHALL mengunggah ulang berkas skrip yang diperbaiki ke `s3://ssh-detection-features-232032302717/unsw-far/scripts/` sebelum tahap S0 dimulai.
6. THE Prosedur_Ramp SHALL memverifikasi bahwa Analyzer mengunduh versi skrip yang sudah diperbaiki sebelum tahap S0 dijalankan.

### Requirement 3: Tahap S0 — Smoke Test

**User Story:** Sebagai operator eksperimen, saya ingin uji smoke ~2–3 menit yang memvalidasi pipeline end-to-end dan sanity fitur, sehingga kesalahan mendasar terdeteksi sebelum membuang biaya jam-jaman.

#### Acceptance Criteria

1. WHEN tahap S0 dimulai, THE Prosedur_Ramp SHALL melakukan capture di Target menggunakan IFACE spesifik dan SHALL TIDAK menggunakan `-i any`.
2. WHEN capture S0 selesai, THE Skrip_Ekstraksi SHALL menghasilkan jumlah flow lebih besar dari nol (Gate S0-a).
3. WHEN pipeline S0 dijalankan, THE Prosedur_Ramp SHALL menyelesaikan ekstraksi dan inferensi end-to-end tanpa error (Gate S0-b).
4. WHEN fitur real S0 diekstraksi, THE Prosedur_Ramp SHALL memeriksa bahwa nilai fitur `duration` berada dalam rentang detik yang masuk akal untuk trafik nyata (Gate S0-c: sanity fitur untuk mendeteksi bug skala milidetik/detik).
5. IF salah satu Gate S0-a, S0-b, atau S0-c gagal, THEN THE Prosedur_Ramp SHALL menjalankan Prosedur_STOP dan SHALL TIDAK menaikkan eksekusi ke tahap S1.

### Requirement 4: Tahap S1 — Validasi 10 Menit

**User Story:** Sebagai operator eksperimen, saya ingin eksekusi 10 menit dengan pemeriksaan FAR dan satuan fitur, sehingga *feature-scaler mismatch* tertangkap sebelum eksekusi berjam-jam.

#### Acceptance Criteria

1. WHEN tahap S1 dimulai, THE Prosedur_Ramp SHALL menjalankan capture trafik benign selama 10 menit menggunakan IFACE spesifik.
2. WHEN hasil S1 dihitung, THE Prosedur_Ramp SHALL memverifikasi bahwa FAR berada dalam rentang masuk akal, yaitu lebih besar sama dengan 0 dan kurang dari 1 serta tidak sama dengan 1 (Gate S1-a).
3. WHEN fitur real S1 dievaluasi, THE Prosedur_Ramp SHALL menghitung z-of-mean setiap fitur terhadap `scaler_mean` dan `scaler_scale` training (Gate S1-b).
4. IF ada fitur dengan nilai z-of-mean absolut melebihi ambang yang ditetapkan (mismatch satuan/scaler), THEN THE Prosedur_Ramp SHALL menjalankan Prosedur_STOP dan SHALL TIDAK menaikkan eksekusi ke tahap S2.
5. IF Gate S1-a gagal karena FAR sama dengan 1 atau nilai absurd, THEN THE Prosedur_Ramp SHALL menjalankan Prosedur_STOP dan SHALL TIDAK menaikkan eksekusi ke tahap S2.

### Requirement 5: Tahap S2 — Validasi 30 Menit dengan Rotasi dan S3

**User Story:** Sebagai operator eksperimen, saya ingin eksekusi 30 menit yang menguji rotasi pcap dan jalur S3, sehingga mekanisme upload/unduh terbukti bekerja sebelum eksekusi panjang.

#### Acceptance Criteria

1. WHEN tahap S2 dimulai, THE Prosedur_Ramp SHALL menjalankan capture dengan rotasi pcap per interval selama 30 menit.
2. WHEN sebuah berkas pcap dirotasi di Target, THE Prosedur_Ramp SHALL mengunggah berkas tersebut ke `s3://ssh-detection-features-232032302717/unsw-far/captures/` dengan sukses (Gate S2-a).
3. WHEN berkas pcap tersedia di S3, THE Analyzer SHALL mengunduh dan memproses berkas tersebut tanpa error (Gate S2-b).
4. WHEN FAR S2 dihitung, THE Prosedur_Ramp SHALL memverifikasi bahwa FAR konsisten dengan hasil S1 dalam batas toleransi yang ditetapkan (Gate S2-c).
5. IF salah satu Gate S2-a, S2-b, atau S2-c gagal, THEN THE Prosedur_Ramp SHALL menjalankan Prosedur_STOP dan SHALL TIDAK menaikkan eksekusi ke tahap S3.

### Requirement 6: Tahap S3 — Validasi 2 Jam

**User Story:** Sebagai operator eksperimen, saya ingin eksekusi 2 jam yang memeriksa stabilitas FAR antar-segmen, sehingga saya yakin hasil tidak meledak pada periode tertentu sebelum eksekusi 24 jam.

#### Acceptance Criteria

1. WHEN tahap S3 dimulai, THE Prosedur_Ramp SHALL menjalankan capture trafik benign selama 2 jam dengan rotasi pcap per interval.
2. WHEN hasil S3 dihitung per segmen, THE Prosedur_Ramp SHALL memverifikasi bahwa FAR stabil antar-segmen dalam batas variasi yang ditetapkan (Gate S3-a).
3. WHEN eksekusi S3 selesai, THE Prosedur_Ramp SHALL memverifikasi bahwa jumlah total flow benign mencapai ambang minimum yang ditetapkan untuk FAR yang kredibel (Gate S3-b).
4. IF Gate S3-a atau Gate S3-b gagal, THEN THE Prosedur_Ramp SHALL menjalankan Prosedur_STOP dan SHALL TIDAK menaikkan eksekusi ke tahap S4.

### Requirement 7: Tahap S4 — Eksekusi 24 Jam Layak Paper

**User Story:** Sebagai penulis paper, saya ingin eksekusi final 24 jam dengan hasil FAR agregat dan per jam yang terunggah lengkap, sehingga saya memiliki data kredibel untuk dilaporkan.

#### Acceptance Criteria

1. WHEN tahap S4 dimulai, THE Prosedur_Ramp SHALL menjalankan capture trafik benign selama 24 jam dengan rotasi pcap per jam.
2. WHEN eksekusi S4 selesai, THE Prosedur_Ramp SHALL menghitung FAR per jam dan FAR agregat 24 jam dari berkas hasil nyata (Gate S4-a).
3. WHEN eksekusi S4 selesai, THE Prosedur_Ramp SHALL memverifikasi bahwa jumlah total flow benign besar sesuai ambang layak paper yang ditetapkan (Gate S4-b).
4. WHEN hasil S4 dihitung, THE Prosedur_Ramp SHALL mengunggah seluruh berkas hasil ke `s3://ssh-detection-features-232032302717/unsw-far/results/` sebelum teardown infrastruktur (Gate S4-c).
5. IF Gate S4-c gagal (ada hasil belum terunggah), THEN THE Prosedur_Ramp SHALL menjalankan Prosedur_STOP dan SHALL menunda teardown sampai seluruh hasil terunggah.

### Requirement 8: Prosedur STOP/Abort di Setiap Gate

**User Story:** Sebagai operator eksperimen, saya ingin prosedur berhenti yang jelas saat gate gagal, sehingga saya tidak melanjutkan ke tahap berikutnya dengan konfigurasi yang salah.

#### Acceptance Criteria

1. WHEN sebuah gate gagal, THE Prosedur_STOP SHALL menghentikan kenaikan tahap ramp.
2. WHEN Prosedur_STOP aktif, THE Prosedur_STOP SHALL mencatat gate yang gagal, nilai terukur, dan ambang yang dilanggar.
3. WHILE Prosedur_STOP aktif, THE Prosedur_Ramp SHALL menahan eksekusi tahap berikutnya sampai penyebab kegagalan didiagnosis dan diperbaiki.
4. WHEN penyebab kegagalan telah diperbaiki, THE Prosedur_Ramp SHALL mengulang tahap yang gagal dari awal sebelum melanjutkan.

### Requirement 9: Kontrol Biaya Antar Tahap

**User Story:** Sebagai operator eksperimen, saya ingin mengendalikan biaya AWS antar tahap, sehingga total pengeluaran tetap terkendali sesuai estimasi.

#### Acceptance Criteria

1. WHERE terdapat jeda antar tahap ramp, THE Prosedur_Ramp SHALL menyediakan langkah untuk menghentikan (stop) instance yang tidak dipakai mengacu pada prosedur di `cost-estimate.md`.
2. THE Prosedur_Ramp SHALL menghentikan instance Attacker selama seluruh tahap ramp Fase 1 karena tidak dipakai untuk FAR.
3. WHEN seluruh tahap ramp selesai dan hasil telah terunggah, THE Prosedur_Ramp SHALL melakukan teardown infrastruktur mengacu pada prosedur teardown di runbook.
4. THE Prosedur_Ramp SHALL merujuk ambang AWS Budgets dan langkah verifikasi Elastic IP idle dari `cost-estimate.md`.

### Requirement 10: Pelengkap Runbook untuk Ramp Bertahap

**User Story:** Sebagai operator eksperimen, saya ingin bagian ramp bertahap ditambahkan ke runbook, sehingga prosedur dapat diulang tanpa mengganti isi runbook yang sudah ada.

#### Acceptance Criteria

1. THE Prosedur_Ramp SHALL menambahkan bagian ramp bertahap (S0–S4) ke `aws/runbook.md` sebagai bagian baru.
2. THE Prosedur_Ramp SHALL mempertahankan seluruh isi runbook yang sudah ada tanpa menghapus bagian deploy, resume, atau teardown.
3. THE bagian ramp baru SHALL mencantumkan perintah, kriteria gate terukur, dan tindakan STOP untuk setiap tahap S0–S4.

### Requirement 11: Transparansi Lingkungan untuk Paper

**User Story:** Sebagai penulis paper, saya ingin mencatat detail lingkungan eksekusi, sehingga eksperimen dapat direplikasi dan dilaporkan secara transparan.

#### Acceptance Criteria

1. THE Prosedur_Ramp SHALL mencatat nama interface capture yang dipakai pada tiap tahap.
2. THE Prosedur_Ramp SHALL mencatat tipe instance yang dipakai untuk Target dan Analyzer.
3. WHERE terdeteksi feature-scaler mismatch pada gate sanity, THE Prosedur_Ramp SHALL mencatat temuan tersebut beserta nilai z-of-mean fitur terkait.
4. THE Prosedur_Ramp SHALL menyimpan catatan transparansi lingkungan pada slot catatan lingkungan di runbook.
