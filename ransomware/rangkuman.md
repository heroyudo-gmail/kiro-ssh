# Rangkuman Paper & Revisi Reviewer

**Judul:** Design of a cloud backup system based on multi-compression algorithms for ransomware attack mitigation

**Penulis:** Hero Yudo Martono¹, Nafisah Rahmadani Harahap²
(Department of Informatics Engineering, Politeknik Elektronika Negeri Surabaya)

**Jurnal target:** International Journal of Electrical and Computer Engineering (IJECE) — IAES
**Paper ID:** #42551
**Keputusan editor:** *Revisions required* (revisi wajib), batas 10 minggu
**Nilai reviewer (Reviewer C):** 8 (ambang terima IAES adalah 7 ke atas)

---

## BAGIAN 1 — RINGKASAN ISI PAPER

### Abstrak
Paper mengusulkan sistem *cloud backup* yang mengintegrasikan mekanisme **air-gapped backup** dengan **kompresi lossless multi-algoritma adaptif** untuk meningkatkan ketahanan data dan efisiensi penyimpanan terhadap serangan ransomware. Sistem memakai verifikasi hash **SHA-256**, analisis metadata, dan analisis struktur file untuk membedakan enkripsi backup yang sah dari modifikasi file akibat ransomware.

**Hasil kunci yang diklaim:**
- Zstandard: rasio kompresi 70–80% untuk file besar.
- Snappy & LZ4: waktu proses cepat 0,5–2 detik.
- Berhasil memulihkan seluruh **113 file** terdampak tanpa error.
- **FPR = 0%** dan **FNR = 0%**.

### Pendahuluan
- Konteks: digitalisasi sektor finansial → ledakan volume data → kebutuhan backup aman & efisien.
- Ancaman ransomware modern menyerang juga infrastruktur backup (Sophos 2024: ~43% perangkat organisasi finansial terdampak).
- Solusi: arsitektur **air-gapped** (isolasi backup dari jaringan primer). Karena air-gapped fisik mahal, paper memakai pendekatan **logical air-gapped** (mounting terkontrol + media terisolasi) yang lebih murah dan mudah diterapkan.
- Isu efisiensi penyimpanan → kompresi lossless. Studi terdahulu membahas keamanan backup, mitigasi ransomware, dan kompresi secara **terpisah**.

### Kontribusi (klaim novelty)
Pendekatan terintegrasi dalam satu framework: air-gapped + kompresi multi-algoritma adaptif (Gzip, Zstandard, Brotli, LZ4, Snappy) berbasis aturan (rule-based, bukan ML) + enkripsi AES-256 + verifikasi integritas SHA-256 + deteksi anomali multi-indikator (hash, metadata, struktur file) untuk membedakan enkripsi ransomware dari enkripsi AES-256 yang sah.

### Related Work
Tabel 1 & 2 membandingkan studi terdahulu (Smith & Lee; Kumar & Patel; Novak et al.; Sahu & Panda; NIST) dan perbandingan konseptual air-gapped vs non-air-gapped.

### Metode
- Desain eksperimen kuantitatif; tiap algoritma diuji terpisah (single-mode).
- **Arsitektur 3 lapis:** (1) application layer — upload/backup/restore + hitung SHA-256, ekstraksi metadata, analisis struktur; (2) protection & compression layer — inspeksi metadata, enkripsi AES-256, kompresi 5 algoritma; (3) storage & detection layer — simpan di air-gapped + sinkron ke Google Drive API; auto-restore jika ransomware terdeteksi.
- **Dataset:** sintetis, meniru struktur data finansial PT Equnix. (Tabel 3: 9 CSV, 9 LOG/TXT, 14 JPG, 11 XLSX — rentang 154 KB–1 GB).
- **Kompresi adaptif rule-based** berdasarkan tipe & ukuran file.
- **Simulasi ransomware** (tanpa malware nyata) berbasis pola CVE: CVE-2017-0144 (encrypt-and-hold / WannaCry), CVE-2021-36934 (overwrite & corrupt), CVE-2018-8453 (metadata/header corruption).
- **Metrik:** Compression Ratio, Compression Factor, Storage Saving %, combined efficiency score (MCDM/WSM, α=β=0,5), RTO, FPR, FNR.

### Hasil & Pembahasan
- Lingkungan uji: Windows 11, i7-11800H, 16 GB RAM, Python 3.10, Flask, PyCryptodome, Google Drive API, media SSD/VHDX terisolasi.
- **Kondisi normal:** koneksi OAuth 2.0 ke Drive, validasi hash+metadata (baseline JSON), enkripsi AES-256, kompresi. Tidak ada anomali terdeteksi.
- **Tabel 6:** performa kompresi per tipe/ukuran file (Snappy/LZ4 cepat untuk teks kecil-menengah; Zstandard rasio tinggi untuk file besar; JPG kompresi rendah 5–15% karena sudah terkompresi).
- **Kondisi terserang:** 3 skenario kerusakan diuji; hash SHA-256 berubah di semua skenario → deteksi berhasil. Tabel 7/8/9 memperlihatkan perubahan hash & metadata.
- **Recovery:** auto air-gapped restore; **113 file** berhasil dipulihkan tanpa error (status [OK]).
- **RTO:** 45–100 detik (Tabel 10 memproyeksikan RTO untuk file lebih besar, naik ~linear).
- **FPR = 0%, FNR = 0%** (Tabel 11).

### Kesimpulan
Integrasi air-gapped + kompresi multi-algoritma meningkatkan resiliensi dan efisiensi. Snappy/LZ4 cepat untuk file kecil-menengah; Zstandard hingga 80% storage saving untuk CSV besar. Recovery 100%, zero false positive. Kompresi rule-based dipilih karena overhead rendah. **Future work:** menambah Random Forest (ML) untuk seleksi algoritma kompresi.

### Bagian pelengkap
Funding (PENS + PT Equnix), CRediT author statement, Conflict of Interest (tidak ada), Data Availability (dataset sintetis), ~40+ referensi.

---

## BAGIAN 2 — REVISI DARI REVIEWER (IJECE)

### Persyaratan umum jurnal
- Minimal **25 referensi** (min. 18 artikel jurnal terkini) untuk Research Paper.
- Ikuti *guide for authors* IJECE (template `.docx`/LaTeX), cek ejaan/tata bahasa.
- Sertakan **biografi penulis** lengkap + tautan profil (Scholar, Scopus, WoS ResearcherID, ORCID) untuk tiap penulis.
- Lengkapi bagian **Funding, Acknowledgement, CRediT, Data Availability, Conflict of Interest**.
- Sertakan **Response to reviewers** dan deklarasi revisi saat submit ulang (ID sama, bukan submission baru).

### Komentar Editor-in-Chief & Associate Editors
1. Perkuat **struktur, kejelasan, dan argumentasi**; mulai dengan pendahuluan yang punya thesis statement kuat; tiap paragraf punya topic sentence & alur logis; berikan bukti solid; pertimbangkan counterargument; simpulkan dengan menegaskan thesis.
2. Tonjolkan **state of the art** di Pendahuluan; **bandingkan temuan** dengan hasil terdahulu di Results & Discussion; definisikan kontribusi secara eksplisit.
3. Bagian **Metode** harus mencakup pendekatan standar & baru + justifikasi validitas, dan langkah-demi-langkah yang **reproducible**.
4. Paper **kurang diskusi kritis, perbandingan, dan interpretasi** — apa implikasi temuan? apa yang berguna ke depan?

### Reviewer A — pertanyaan strategis (harus dijawab)
1. Bagaimana manuscript sesuai *scope* jurnal & mengapa menarik/akan dikutip?
2. Apa objektif & pendekatan (metode/teknik/algoritma/novelty konseptual/kerangka teori)?
3. Apa **kontribusi baru** manuscript?
4. Bagaimana menambah pengetahuan yang ada?
5. Implikasi masa depan yang menonjol?
6. Mengapa jurnal ini harus mempublikasikannya?

### Reviewer A — komentar per bagian
- **Abstrak:** tidak menyatakan bahwa serangan ransomware **disimulasikan & terkontrol** (bukan eksekusi malware nyata); tidak menyebut dataset **sintetis & terbatas**.
- **Pendahuluan:** perlu tegaskan bahwa studi terdahulu membahas backup security, mitigasi ransomware, dan kompresi secara terpisah — dan belum menganalisis arsitektur backup tahan-ransomware, immutable cloud storage, snapshot-based recovery, deduplication, atau zero-trust backup.
- **Metode:** (1) *workflow membingungkan*; (2) mekanisme kompresi adaptif hanya **rule-based** (tipe & ukuran file); (3) simulasi ransomware pakai label CVE tapi **pemetaannya kurang rigor teknis**; (4) logika deteksi **terlalu bergantung** pada perubahan hash & metadata.
- **Results & Discussion:** hasil kompresi per tipe file **tanpa analisis statistik detail** — tidak ada repeated trials, standar deviasi, utilisasi CPU/RAM, throughput, konsumsi energi, biaya upload/download cloud, atau perbandingan dengan deduplication/incremental backup. Beberapa gambar **tidak dirujuk** di pembahasan.
- **Kesimpulan:** future work **terlalu sempit** (hanya Random Forest untuk seleksi kompresi). Perlu peluang riset lebih luas: realistic ransomware testing, immutable cloud backup, analisis keamanan formal, key management, evaluasi skala enterprise, arsitektur zero-trust backup.
- **Referensi:** pastikan [21], [41]–[44] **dikutip di dalam artikel**; sertakan **DOI** referensi (jika ada).

### Reviewer B
- **Abstrak** harus menyatakan sistem divalidasi dengan **model serangan simulasi pada dataset sintetis berisi 113 file**.
- **Pendahuluan** perlu paragraf tentang **problem matematis efisiensi kompresi** pada data high-entropy (terenkripsi) vs low-entropy (plaintext); definisikan **research gap**.
- **Gambar 1, 2, 3, 10** harus dirujuk & dijelaskan di teks **sebelum** ditampilkan.
- **Gambar 14, 15, 16 tidak ditemukan** di manuscript.
- **Tabel 3, 9, 11** harus dirujuk & dijelaskan di teks sebelum ditampilkan.
- **Kesimpulan** lebih ringkas: rangkum temuan utama, jawab tujuan/rumusan masalah, tegaskan kontribusi & arah future work.
- Referensi **[21] belum dikutip** di teks — semua referensi wajib dikutip.

### Reviewer C (nilai: 8)
- Judul & abstrak sudah sesuai; paper terorganisir baik; kontribusi bermutu "Good".
- Bahasa Inggris **belum benar** (ada error). Catatan:
  1. **Kesalahan tata bahasa** — beberapa kalimat kehilangan artikel/subjek/kata kerja bantu. Contoh: *"evaluate the resilience..."* → seharusnya *"To evaluate the resilience..."*.
  2. **Ambiguitas ukuran dataset** — deskripsi menyebut 9 CSV + 9 LOG/TXT + 14 JPG + 11 XLSX = **43 file**, tetapi bagian lain berulang kali melaporkan restorasi **113 file**. (Diskrepansi harus diperjelas.)
  3. **Hasil deteksi berlebihan** — FPR=0% & FNR=0% mungkin di eksperimen terkontrol, tapi **jarang** di sistem deteksi ransomware dunia nyata (perlu diskusi lebih hati-hati).

**Rekomendasi Reviewer C:** cocok untuk publikasi setelah revisi minor-moderat. Perbaikan yang diminta:
1. Perjelas diskrepansi ukuran dataset (43) vs jumlah file dipulihkan (113).
2. Diskusi lebih hati-hati soal hasil 0% FPR & 0% FNR.
3. Deskripsikan mekanisme seleksi kompresi secara eksplisit sebagai **rule-based**.
4. Perkuat validasi eksperimen dengan **analisis statistik tambahan**.
5. Lakukan **editing bahasa Inggris** menyeluruh (tata bahasa, format, konsistensi).

---

## RINGKASAN PRIORITAS PERBAIKAN (gabungan semua reviewer)

| Prioritas | Item | Sumber |
|---|---|---|
| Tinggi | Perjelas diskrepansi **43 vs 113 file** | Reviewer C, B |
| Tinggi | Nyatakan **simulasi terkontrol + dataset sintetis** di abstrak | Reviewer A, B |
| Tinggi | Diskusi hati-hati soal **0% FPR/FNR** | Reviewer C |
| Tinggi | Semua **gambar & tabel dirujuk** di teks sebelum tampil; perbaiki Gambar 14–16 yang hilang | Reviewer B |
| Tinggi | Semua **referensi dikutip** ([21],[41]-[44]) + tambah DOI + penuhi min. 25 ref (18 jurnal) | Reviewer A, B, jurnal |
| Sedang | Tambah **analisis statistik** (repeated trials, std dev, CPU/RAM, throughput, biaya cloud, perbandingan deduplication/incremental) | Reviewer A |
| Sedang | Perjelas **workflow metode** & pemetaan CVE yang lebih rigor | Reviewer A |
| Sedang | Perluas **future work** (bukan hanya Random Forest) | Reviewer A |
| Sedang | Tambah paragraf **research gap** & problem matematis entropi kompresi | Reviewer B |
| Sedang | **Editing bahasa Inggris** menyeluruh | Reviewer C, Editor |
| Wajib | Biografi penulis + tautan profil (Scholar/Scopus/WoS/ORCID); lengkapi Funding, Acknowledgement, CRediT, Data Availability, CoI | Editor |
| Wajib | Siapkan **Response to Reviewers** + deklarasi revisi | Editor |

---

## BAGIAN 3 — KERANGKA HASIL EKSPERIMEN (⚠️ PLACEHOLDER — BUKAN HASIL REAL)

> **PERINGATAN PENTING.** Seluruh angka pada Bagian 3 ini adalah **placeholder sementara** yang dibuat HANYA untuk melihat struktur/kerangka paper. **BUKAN hasil eksperimen nyata.** Setiap nilai ditandai `⚠️[EST: ...]`. Sebelum submit ke IJECE, SEMUA nilai `⚠️[EST]` **WAJIB diganti** dengan hasil eksperimen real dari EC2. Cari string `⚠️[EST` untuk menemukan semua angka yang harus diganti.
>
> Keputusan yang sudah final (bukan placeholder): **jumlah berkas = 43** (9 CSV + 9 LOG/TXT + 14 JPG + 11 XLSX). Angka "113 berkas" pada draf lama adalah keliru dan diganti menjadi 43 secara konsisten di seluruh paper.

### 3.1 Komposisi dataset (FINAL — 43 berkas)

| No | Tipe Data | Format | Jumlah | Rentang Ukuran |
|---|---|---|---|---|
| 1 | Data transaksi terstruktur | CSV | 9 | 500 KB – 1 GB |
| 2 | Data log sistem | TXT/LOG | 9 | 500 KB – 1 GB |
| 3 | Dokumen visual | JPG | 14 | 154 – 249 KB |
| 4 | Dokumen spreadsheet | XLSX | 11 | 500 KB – 650 MB |
| | **Total** | | **43** | |

### 3.2 Matriks kinerja kompresi per algoritma/tipe berkas (⚠️ PLACEHOLDER)

| Tipe | Ukuran | Algoritma Terbaik | Kompresi (%) | Waktu (s) |
|---|---|---|---|---|
| CSV | ≤ 500 MB | Snappy / LZ4 | ⚠️[EST: 45–60%] | ⚠️[EST: 1–2] |
| CSV | > 500 MB | Zstandard | ⚠️[EST: 70–80%] | ⚠️[EST: 5–8] |
| XLSX | 500 KB | Snappy | ⚠️[EST: 50%] | ⚠️[EST: 0,5] |
| XLSX | 100–200 MB | LZ4 | ⚠️[EST: 55–65%] | ⚠️[EST: 2–3] |
| XLSX | 250 MB | Zstandard | ⚠️[EST: 68%] | ⚠️[EST: 4] |
| XLSX | 350–650 MB | LZ4 | ⚠️[EST: 60–70%] | ⚠️[EST: 3–5] |
| LOG | ≤ 100 MB | Snappy | ⚠️[EST: 50%] | ⚠️[EST: 0,8–1,5] |
| LOG | 250–500 MB | LZ4 | ⚠️[EST: 60–70%] | ⚠️[EST: 2–4] |
| LOG | ≥ 1 GB | Zstandard | ⚠️[EST: 70–80%] | ⚠️[EST: 6–10] |
| JPG | 154–249 KB | Snappy / LZ4 | ⚠️[EST: 5–10%] | ⚠️[EST: 0,2–0,5] |
| JPG | > 250 KB | Zstandard / Brotli | ⚠️[EST: 10–15%] | ⚠️[EST: 1–2] |

*Catatan struktur:* tabel ini = Tabel 6 di paper. Reviewer minta ditambah **std deviasi + repeated trials + CPU/RAM + throughput**. Kolom tambahan yang perlu diisi saat eksperimen real: `Std Dev (%)`, `CPU (%)`, `RAM (MB)`, `Throughput (MB/s)`.

### 3.3 Skor efisiensi gabungan MCDM/WSM (⚠️ PLACEHOLDER)

Rumus: E = α(1−R) + β(1/T), α=β=0,5; lalu dinormalisasi E(%) = E/E_max × 100.

| Algoritma | E(%) | Status |
|---|---|---|
| Zstandard | ⚠️[EST: 88] | ⚠️[EST: Good] |
| LZ4 | ⚠️[EST: 92] | ⚠️[EST: Excellent] |
| Snappy | ⚠️[EST: 90] | ⚠️[EST: Excellent] |
| Gzip | ⚠️[EST: 76] | ⚠️[EST: Fair] |
| Brotli | ⚠️[EST: 79] | ⚠️[EST: Fair] |

### 3.4 Simulasi serangan & deteksi (⚠️ PLACEHOLDER untuk angka, pola FINAL)

Tiga pola serangan (final, berbasis CVE):
- **Encrypt-and-hold** (CVE-2017-0144 / pola WannaCry)
- **Metadata/Header corruption** (CVE-2018-8453)
- **Overwrite-and-corrupt** (CVE-2021-36934)

Tabel deteksi & recovery (jumlah berkas = 43):

| Skenario | Total Berkas | Terdeteksi | Auto Restore | Status Aktual | Hasil |
|---|---|---|---|---|---|
| Enkripsi AES-256 normal | 43 | ⚠️[EST: 0] | Tidak | Aman | True Negative |
| Encrypt-and-Hold | 43 | ⚠️[EST: 43] | Ya | Ransomware | True Positive |
| Metadata/Header Corruption | 43 | ⚠️[EST: 43] | Ya | Ransomware | True Positive |
| Overwrite-and-Corrupt | 43 | ⚠️[EST: 43] | Ya | Ransomware | True Positive |

### 3.5 FPR / FNR (⚠️ PLACEHOLDER — perlu diskusi jujur)

- FPR = ⚠️[EST: 0%], FNR = ⚠️[EST: 0%]
- **Catatan penting untuk revisi (Reviewer C):** jika hasil real tetap 0%/0%, WAJIB ditambah paragraf yang menjelaskan bahwa nilai sempurna ini adalah *konsekuensi logis dari deteksi berbasis integritas hash pada lingkungan terkontrol* (setiap perubahan 1 byte pasti mengubah SHA-256), BUKAN klaim bahwa sistem sempurna di dunia nyata. Sebutkan keterbatasan: tidak menguji evasion canggih (FPE, fileless, LotL) yang bisa mengelabui deteksi berbasis integritas.

### 3.6 Recovery Time Objective / RTO (⚠️ PLACEHOLDER)

| Tipe Serangan | Ukuran | Total Berkas | RTO (detik) |
|---|---|---|---|
| Encrypt-and-Hold | 500 KB | 43 | ⚠️[EST: 75–85] |
| | 500 MB | | ⚠️[EST: 95–130] |
| | 1 GB | | ⚠️[EST: 120–180] |
| Metadata/Header Corruption | 500 KB | 43 | ⚠️[EST: 45–60] |
| | 500 MB | | ⚠️[EST: 60–90] |
| | 1 GB | | ⚠️[EST: 90–120] |
| Overwrite-and-Corrupt | 500 KB | 43 | ⚠️[EST: 85–100] |
| | 500 MB | | ⚠️[EST: 120–180] |
| | 1 GB | | ⚠️[EST: 180–240] |

### 3.7 Ringkasan alur paper (kerangka narasi — untuk cek struktur)

1. **Abstract** → tegaskan: simulasi terkontrol (bukan malware nyata) + dataset sintetis 43 berkas + hasil kompresi + recovery + FPR/FNR.
2. **Introduction** → digitalisasi finansial → ancaman ransomware ke backup → air-gapped (logis) → efisiensi kompresi → research gap (studi terdahulu bahas terpisah) → kontribusi.
3. **Related Work** → Tabel 1 (studi terkait) + Tabel 2 (air-gapped vs non air-gapped).
4. **Method** → arsitektur 3 lapisan → dataset (43) → AES-256 → kompresi rule-based → prosedur backup/restore → simulasi CVE → mekanisme deteksi → metrik (CR, CF, SS, E, RTO, FPR, FNR).
5. **Results & Discussion** → lingkungan uji → kondisi normal (Gbr 4–9, Tbl 5) → kompresi (Tbl 6, Gbr 10) → air-gapped (Gbr 11–13) → kondisi terserang (Tbl 7–9) → respons & restore (Gbr 14–16, Tbl 10 RTO) → FPR/FNR (Tbl 11) → **diskusi kritis + perbandingan literatur** (yang diminta reviewer).
6. **Conclusion** → ringkas temuan + jawab tujuan + kontribusi + future work (diperluas: immutable/WORM, zero-trust backup, realistic ransomware, key management, skala enterprise, ML seleksi kompresi).
7. **Bagian pelengkap** → Funding, CRediT, CoI, Data Availability, Referensi (≥25, 18 jurnal, +DOI), Biografi.

> **Langkah berikutnya:** setelah struktur ini disepakati tim, bangun sistem real di EC2 (`ransomware/aws/`), jalankan eksperimen dengan 43 berkas, lalu ganti SEMUA `⚠️[EST]` dengan angka hasil nyata + tambahkan kolom statistik yang diminta reviewer.

---

## BAGIAN 4 — SPESIFIKASI DATASET SINTETIS (43 BERKAS) — acuan generator & eksperimen

> Tujuan: menetapkan ukuran & pola isi tiap berkas secara eksplisit SEBELUM coding, agar (a) total = 43 dan rentang ukuran cocok dengan Tabel 3 paper, dan (b) rasio kompresi hasil eksperimen realistis & dapat dijelaskan berdasarkan entropi data. Ini menjadi kontrak antara paper dan generator dataset (`generate_dataset.py`).

### Prinsip desain (kaitan entropi -> rasio kompresi)
- **CSV & LOG/TXT** = teks terstruktur ber-pola berulang (entropi rendah) -> rasio kompresi TINGGI (mendukung klaim Zstandard 70-80% pada berkas besar).
- **JPG** = sudah terkompresi lossy (entropi tinggi mendekati acak) -> rasio kompresi SANGAT RENDAH (5-15%), membuktikan keterbatasan kompresi lossless pada data terkompresi.
- **XLSX** = kontainer ZIP berisi XML (sebagian sudah terkompresi) -> rasio kompresi MENENGAH.

### 4.1 CSV (9 berkas) — data transaksi finansial sintetis
Pola isi: baris transaksi berulang (kolom: id, tanggal, akun, tipe_transaksi, nominal, mata_uang, cabang, status). Nilai dari himpunan terbatas -> redundansi tinggi.

| # | Nama berkas | Ukuran target |
|---|---|---|
| 1 | transaksi_01.csv | 500 KB |
| 2 | transaksi_02.csv | 1 MB |
| 3 | transaksi_03.csv | 5 MB |
| 4 | transaksi_04.csv | 25 MB |
| 5 | transaksi_05.csv | 100 MB |
| 6 | transaksi_06.csv | 250 MB |
| 7 | transaksi_07.csv | 500 MB |
| 8 | transaksi_08.csv | 750 MB |
| 9 | transaksi_09.csv | 1 GB |

### 4.2 LOG/TXT (9 berkas) — log aplikasi/audit sintetis
Pola isi: baris log berformat `[timestamp] [LEVEL] [modul] pesan` dengan LEVEL {INFO, WARN, ERROR, DEBUG} dan pesan dari template terbatas -> redundansi tinggi.

| # | Nama berkas | Ukuran target |
|---|---|---|
| 1 | app_01.log | 500 KB |
| 2 | app_02.log | 1 MB |
| 3 | app_03.log | 10 MB |
| 4 | app_04.log | 50 MB |
| 5 | audit_01.log | 100 MB |
| 6 | audit_02.log | 250 MB |
| 7 | audit_03.log | 500 MB |
| 8 | sys_01.txt | 750 MB |
| 9 | sys_02.txt | 1 GB |

### 4.3 JPG (14 berkas) — dokumen visual (sudah terkompresi)
Pola isi: gambar sintetis (noise/gradient/pola) disimpan sebagai JPEG kualitas ~85. Rentang 154--249 KB sesuai Tabel 3.

| # | Nama berkas | Ukuran target |
|---|---|---|
| 1--14 | img_01.jpg .. img_14.jpg | 154--249 KB (variasi merata, mis. 154, 161, 168, ... 249 KB) |

### 4.4 XLSX (11 berkas) — laporan operasional/keuangan
Pola isi: spreadsheet berisi tabel angka & teks berulang (laporan bulanan). Rentang 500 KB -- 650 MB sesuai Tabel 3.

| # | Nama berkas | Ukuran target |
|---|---|---|
| 1 | lap_01.xlsx | 500 KB |
| 2 | lap_02.xlsx | 2 MB |
| 3 | lap_03.xlsx | 10 MB |
| 4 | lap_04.xlsx | 50 MB |
| 5 | lap_05.xlsx | 100 MB |
| 6 | lap_06.xlsx | 150 MB |
| 7 | lap_07.xlsx | 250 MB |
| 8 | lap_08.xlsx | 350 MB |
| 9 | lap_09.xlsx | 450 MB |
| 10 | lap_10.xlsx | 550 MB |
| 11 | lap_11.xlsx | 650 MB |

### 4.5 Ringkasan
- Total: 9 + 9 + 14 + 11 = **43 berkas** ✅
- Total ukuran kasar: CSV ~3,1 GB + LOG ~3,2 GB + JPG ~2,8 MB + XLSX ~2,9 GB ≈ **~9,2 GB** pada skala penuh.

### 4.6 CATATAN PENTING — strategi ukuran untuk eksperimen EC2
Skala penuh (~9,2 GB, ada berkas 1 GB) butuh disk besar (EBS ≥ 100 GB) dan waktu proses lama (kompresi berkas 1 GB bisa 6--10 detik/algoritma × 5 algoritma × beberapa berkas besar). Dua opsi:

- **Opsi CEPAT (disarankan untuk validasi awal):** kecilkan skala — berkas maksimum ~50 MB, total < 1 GB, EBS 30 GB. Cukup untuk membuktikan LOGIKA & POLA hasil (algoritma mana menang di tipe/ukuran apa), lalu paper menyebut hasil pada skala uji + proyeksi RTO untuk ukuran lebih besar (seperti sudah ada di Tabel RTO).
- **Opsi SKALA PENUH:** ukuran persis seperti tabel di atas (sampai 1 GB), EBS ≥ 120 GB, biaya & waktu lebih besar. Dipakai bila reviewer menuntut angka pada berkas besar yang benar-benar diukur (bukan proyeksi).

> Keputusan yang perlu diambil tim sebelum coding: pilih Opsi CEPAT atau SKALA PENUH. Default rekomendasi: mulai Opsi CEPAT untuk memvalidasi sistem, naikkan ke skala penuh hanya untuk berkas terpilih bila diperlukan.

---

## BAGIAN 5 — HASIL EKSPERIMEN NYATA (TERVERIFIKASI, menggantikan placeholder Bagian 3)

> Dijalankan di AWS EC2 (t3.large, Ubuntu 22.04, region ap-southeast-1), pipeline **compress-then-encrypt**, dataset sintetis 43 berkas skala Opsi Cepat (total ~490 MB). Sumber: `ransomware/aws/results/` + `s3://ssh-detection-features-232032302717/ransomware-results/`. Angka ini SUDAH mengganti seluruh `⚠️[EST]` di Bagian 3 dan sudah dimasukkan ke `ijece-id.tex`.

### 5.1 Temuan kunci: urutan kompresi vs enkripsi
Pipeline awal (enkripsi->kompresi) menghasilkan **0% penghematan** karena data terenkripsi ber-entropi tinggi tak dapat dikompresi. Diperbaiki menjadi **compress-then-encrypt** (kompresi plaintext dulu, baru enkripsi). Ini benar secara teknis dan menjadi koreksi penting pada urutan metode di paper. **PERLU dikonfirmasi ke programmer** apakah kode asli sudah compress-then-encrypt.

### 5.2 Penghematan penyimpanan (%) — rata-rata per tipe & algoritma (NYATA)

| Tipe | Gzip | Zstandard | Brotli | LZ4 | Snappy |
|---|---|---|---|---|---|
| Log/TXT | 88,5 | 87,6 | **89,5** | 77,4 | 80,2 |
| CSV | 79,9 | 78,7 | **81,1** | 66,6 | 66,4 |
| XLSX | 1,1 | 0,0 | 0,0 | 0,0 | 0,0 |
| JPG | 0,1 | 0,0 | 0,0 | 0,0 | 0,0 |

Teks (entropi rendah) -> kompresi tinggi; JPG/XLSX (sudah terkompresi) -> ~0%. Mendukung hipotesis paper.

### 5.3 Skor efisiensi MCDM/WSM (NYATA, alpha=beta=0.5)

| Algoritma | E(%) | Status |
|---|---|---|
| Snappy | 100,0 | Excellent |
| LZ4 | 94,7 | Excellent |
| Zstandard | 40,7 | Poor |
| Brotli | 6,6 | Poor |
| Gzip | 5,2 | Poor |

Catatan: skor memberatkan kecepatan (1/T), sehingga Snappy/LZ4 (tercepat) unggul. Untuk efisiensi penyimpanan murni, Brotli/Zstandard unggul (lihat 5.2).

### 5.4 Deteksi & pemulihan (NYATA)

| Skenario | Total | Terdeteksi | Restore OK | RTO (s) | Hasil |
|---|---|---|---|---|---|
| Normal AES-256 | 43 | 0 | - | - | True Negative |
| Encrypt-and-Hold (CVE-2017-0144) | 43 | 43 | 43 | 4,34 | True Positive |
| Metadata/Header Corruption (CVE-2018-8453) | 43 | 43 | 43 | 5,21 | True Positive |
| Overwrite-and-Corrupt (CVE-2021-36934) | 43 | 43 | 43 | 5,34 | True Positive |

- **FPR = 0%, FNR = 0%** (lingkungan terkontrol, deteksi berbasis hash).
- Backup time (43 berkas, 5 algoritma diukur): ~38 detik.
- Semua 43 berkas pulih tanpa galat (hash cocok dengan baseline).

### 5.5 Status placeholder Bagian 3
Seluruh `⚠️[EST]` di Bagian 3 kini DIGANTIKAN oleh angka Bagian 5 ini. Bagian 3 dipertahankan sebagai jejak proses (kerangka awal), tetapi **acuan final adalah Bagian 5**.

---

## BAGIAN 6 — REPLIKASI LINTAS-PLATFORM (Windows vs Linux)

Eksperimen direplikasi di **AWS EC2 Windows Server 2022** (t3.xlarge, 16 GB, drive D: air-gapped) melengkapi hasil **Ubuntu 22.04** (t3.large, 8 GB). Hasil di `ransomware/aws/results-windows/` + `s3://.../ransomware-results-windows/`.

| Metrik | Windows Server 2022 | Ubuntu 22.04 |
|---|---|---|
| Log/TXT (Brotli) | 89,6% | 89,5% |
| CSV (Brotli) | 81,1% | 81,1% |
| JPG / XLSX | ~0% | ~0% |
| Deteksi | 43/43 | 43/43 |
| Pemulihan | 43/43 | 43/43 |
| FPR / FNR | 0% / 0% | 0% / 0% |
| RTO Encrypt-Hold | 5,50 s | 4,34 s |
| RTO Metadata | 5,20 s | 5,21 s |
| RTO Overwrite | 5,32 s | 5,34 s |

**Kesimpulan:** rasio kompresi identik lintas-OS (bergantung data & algoritma, bukan OS); RTO sedikit beda karena hardware. Membuktikan konsistensi lintas-platform → menjawab komentar reviewer soal generalisasi. Setup lokal Windows asli tim = i7-11800H/16GB (tetap disebut di paper sebagai lingkungan pengembangan); AWS = lingkungan replikasi cloud nyata.

---

## BAGIAN 7 — ANALISIS STATISTIK (memperkuat jawaban Reviewer A5/C5)

Uji-berulang 5x pada dataset 43 berkas (~531 MB) di AWS EC2 Ubuntu 22.04, diukur dgn psutil. Sumber: `results/benchmark_stats.csv|json` + `s3://.../ransomware-results/`.

| Algoritma | Waktu rata2 (s) | Std (s) | Throughput (MB/s) | CPU (%) | RAM (MB) |
|---|---|---|---|---|---|
| Gzip | 17,427 | 0,062 | 30,5 | 100 | 6,3 |
| Brotli | 10,468 | 0,237 | 50,7 | 100 | 5,1 |
| Zstandard | 1,721 | 0,016 | 308,7 | 99,9 | 3,4 |
| LZ4 | 0,896 | 0,011 | 592,7 | 100 | <1 |
| Snappy | 0,831 | 0,003 | 639,0 | 99,3 | 0,9 |

**Kesimpulan:** std deviasi sangat kecil = kinerja stabil/konsisten. Snappy/LZ4 ~20x lebih cepat dari Gzip. Proses CPU-bound (~100% CPU), jejak RAM kecil (<7 MB). Menjawab A5/C5 (repeated trials + std + throughput + CPU/RAM). Masuk ke ijece-id.tex sbg subbab "Analisis statistik kinerja kompresi" (Tabel tab:comp_stats). Sisa (energi, deduplication/incremental) tetap future work.
