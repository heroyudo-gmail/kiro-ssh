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
