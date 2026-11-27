# Federated SFM (FSFM) - dokumen desain

Status: **rencana, belum ada angka**. Semua angka hasil harus berasal dari eksekusi nyata di SageMaker.
Dokumen ini menetapkan kriteria keberhasilan SEBELUM melihat hasil, supaya klaim tidak disesuaikan setelahnya.

## 1. Ide singkat

SFM di `unswnb-15/paper1-jictra.tex` dijalankan terpusat: satu mesin melihat data dua dataset, memetakan fitur,
lalu menyisakan irisan 9 fitur. Pada FL data tidak boleh dikumpulkan, dan klien berbeda dalam jumlah fitur.
FSFM = pemetaan fitur semantik yang dijalankan terdistribusi, dengan **pemetaan bertingkat (tiered)**:

| Tingkat | Fitur | Dimiliki oleh | Cara agregasi |
|---|---|---|---|
| Inti (core) | 9 fitur hasil SFM | CIC2017, CIC2018, UNSW | rata-rata semua klien |
| Ekstensi (ext) | 67 fitur CICFlowMeter lain | CIC2017, CIC2018 saja | rata-rata hanya klien pemilik |

Intuisi: irisan 3 dataset tetap 9 fitur (UNSW yang memaksa), tapi dua klien CIC tidak perlu kehilangan 67 fitur lain.
Hasil sebelumnya menunjukkan kekayaan fitur menjelaskan jurang MCC (near@9 0,537 vs near@76 0,851).

## 2. Posisi terhadap literatur (hasil pencarian terbatas, belum tinjauan sistematis)

- Fitur heterogen di FL secara umum: Personalised FL on Heterogeneous Feature Spaces (arXiv 2301.11447),
  Global Layers untuk tabular non-IID (arXiv 2305.19290), Federated Imputation under Heterogeneous Feature Spaces (arXiv 2605.16099).
- FL deteksi ancaman pada skema berbeda tanpa padanan kolom: Split-parameter FL (Springer, 2026, doi 10.1007/s43926-026-00520-6).
- Fitur standar NIDS berbasis NetFlow (Sarhan dkk., arXiv 2101.11315). Reviewer akan bertanya kenapa tidak mengonversi semua
  dataset ke NetFlow. Jawaban: butuh pcap/ekspor ulang, tidak mungkin bila klien hanya punya fitur hasil ekspor.
- Celah yang diklaim (sempit): padanan semantik **sebagian yang bisa diaudit** antar alat ekspor aliran, ringkasan statistik
  saja yang dibagikan, dan agregasi sadar-tingkat. Klaim "FL untuk fitur heterogen" secara umum TIDAK boleh dipakai.
- Batasan jujur: pencarian baru tiga kueri. Sebelum submit, lakukan tinjauan literatur yang lebih menyeluruh.

## 3. Catatan penting tentang SFM terpusat (dari paper1)

- Keputusan memasukkan fitur terutama **semantik**: verifikasi dari dokumentasi alat, faktor satuan `c` yang terdokumentasi,
  dan label proksi. Rasio median/p99 berfungsi sebagai label (aligned / scale-mismatch); pasangan scale-mismatch tetap dipakai
  (skalanya dihilangkan z-score per dataset). Hanya pasangan "different-feature" (mis. TCP window) yang ditolak.
- Akibatnya bagian "audit terdistribusi" bersifat sekunder: ia mereproduksi label dari ringkasan statistik, bukan menemukan fitur
  baru secara otomatis. Kontribusi utama harus ada di pemetaan bertingkat + agregasi sadar-tingkat.
- Data partisi sebelumnya (`s01_fed_data_partition`) memakai 9 fitur tanpa faktor satuan (durasi CIC dalam mikrodetik, UNSW dalam detik).
  Normalisasi lokal log1p + z-score meredam sebagian, tidak seluruhnya. Dicatat sebagai batasan.

## 4. Protokol

1. **Audit ringkasan (jG_00).** Tiap klien mengirim median dan p99 per fitur (bukan data). Server memberi label tiap pasangan dengan aturan
   paper1 dan menetapkan tingkat fitur. Uji ketahanan: derau multiplikatif pada ringkasan. Ini BUKAN jaminan privasi diferensial formal.
2. **Pelatihan (jG_01).** MLP 128-64, preproses per klien: log1p bertanda lalu z-score dengan statistik train klien itu sendiri,
   Adam lr 1e-3 (hasil jF_01: z-score + SGD kurang terlatih), 30 ronde, 1 epoch lokal, tiga klien: cic2017, cic2018, unsw.
3. **Agregasi tingkat.** Lapisan pertama berukuran 77 masukan (9 inti, 67 ekstensi, 1 bendera "punya ekstensi").
   Baris ekstensi dan bendera dirata-rata hanya atas klien yang memilikinya; semua parameter lain dirata-rata atas semua klien.

## 5. Metode yang dibandingkan (semua dengan data, ronde, dan seed yang sama)

| Kode | Metode | Keterangan |
|---|---|---|
| M0 | local-only | tiap klien sendiri, fitur aslinya |
| M1 | centralized-pad | data digabung, batas atas, melanggar privasi (hanya acuan) |
| M2 | FedAvg-int9 | irisan 9 fitur (setara SFM paper1) |
| M3 | FedAvg-pad76 | semua fitur, klien tanpa ekstensi diisi nol, rata-rata biasa |
| M4 | FedPer-ownlayer | lapisan pertama lokal per klien, sisanya dirata-rata |
| M5 | FedAvg-FSFMtier | **usulan**: pad76 + agregasi tingkat |
| M6-M8 | FedProx (mu 0,01) untuk M2, M3, M5 | metode FL yang sudah ada |

Belum dimasukkan (tambahkan kemudian bila perlu): Global Layers, SCAFFOLD, konversi NetFlow (butuh pcap).

## 6. Kriteria dibaca (disepakati SEBELUM melihat angka)

Metrik: MCC ambang 0,5 pada test tiap klien, rata-rata tiga klien per seed; 5 seed (42, 13, 101, 202, 303); selang kepercayaan 95% t-paired.

- **H1 (tingkat berguna):** M5 - M2 >= 0,05 dan batas bawah CI > 0, serta MCC klien UNSW pada M5 tidak turun lebih dari 0,02 dibanding M2.
- **H2 (bukan sekadar pad/personalisasi):** M5 - M3 >= 0,02 dan M5 - M4 >= 0,02, kedua batas bawah CI > 0.
- **H3 (audit mereproduksi SFM):** label 7 pasangan satuan-eksak di jG_00 sama dengan Tabel 2 paper1; stabil terhadap derau ringkasan.

Pembacaan:
- H1 gagal: ide pemetaan bertingkat tidak layak untuk Q1. Berhenti, laporkan apa adanya.
- H1 lolos, H2 gagal: tingkat tidak lebih baik dari pad/FedPer. Klaim turun menjadi "setara, dengan biaya komunikasi/privasi lebih baik",
  kontribusi harus dipikirkan ulang.
- H1 dan H2 lolos: lanjut ke uji AWS online dan penulisan ulang paper6 dengan FSFM sebagai metode.

## 7. Ancaman validitas yang sudah diketahui

- Tiga klien saja, dua di antaranya dari alat yang sama (CICFlowMeter): keuntungan bertingkat bisa hanya mencerminkan itu.
- MLP numpy dengan satu konfigurasi; pohon gradient-boosting jauh lebih kuat di data ini (jF_01), jadi angka MLP bersifat setup-spesifik.
- Faktor satuan tidak diterapkan pada data pelatihan (lihat bagian 3).
- Simulasi FL dalam satu proses; bukti deployment nyata di AWS adalah tahap berikutnya.

## 8. Pengaruh ke paper6

`paper6-federated.tex` saat ini sengaja TIDAK mengklaim SFM. Penulisan ulang menunggu hasil jG_00 dan jG_01. Bila H1 dan H2 lolos,
judul, abstrak, dan kontribusi berubah; sitasi paper SFM harus mencantumkan statusnya apa adanya.
