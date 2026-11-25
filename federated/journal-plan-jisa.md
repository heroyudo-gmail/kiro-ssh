# Rencana Menuju Jurnal Q1 (JISA) — Tahapan

> Target: Journal of Information Security and Applications (Elsevier, Q1, review single-anonymized).
> Naskah acuan: `paper6-federated.tex`. Semua komputasi di SageMaker (notebook `.ipynb`),
> angka dari eksekusi nyata, hasil di S3, Kiro menarik hasil ke lokal.
>
> **Verifikasi sendiri** panduan resmi Elsevier sebelum submit (saat penyusunan, halaman resmi
> tidak bisa dibuka; poin JISA di bawah dari ringkasan pihak ketiga).

## Mengapa perlu tahapan tambahan

JISA menolak di tahap awal naskah yang hanya memakai model ML standar pada dataset publik tanpa
kebaruan keamanan. Naskah kita sekarang punya temuan yang kuat, tetapi tiga penjelasan masih
hipotesis (belum diuji) dan belum ada kontribusi yang bersifat membangun. Tahapan ini mengubah
hipotesis menjadi bukti dan menambah satu kontribusi keamanan.

## Cara kerja tiap tahap

- **Kiro**: menyiapkan notebook, push ke GitHub, menarik hasil dari S3, menulis ke naskah.
- **Kamu**: `git pull` di SageMaker, jalankan notebook sel demi sel, kabari selesai.
- Satu tahap = satu pertanyaan yang dijawab. Setelah tiap tahap kita putuskan lanjut atau tidak.

---

## TAHAP 1 — Tutup tiga hipotesis (murah, simulasi SageMaker)

| Sub | Pertanyaan yang dijawab | Notebook | Hasil yang dicari |
|---|---|---|---|
| 1A | Apakah near-domain lebih baik karena jarak domain, atau hanya karena 76 fitur vs 9? | `jC_01_neardomain_9feat` | MCC near-domain dengan 9 fitur yang sama dgn far-domain |
| 1B | Apakah non-IID di UNSW datar karena rasio serangannya 55%? Apakah far-domain unggul atas near@9 karena UNSW bermayoritas serangan? | `jC_02_noniid_ratio` dan `jC_03_far_ratio` | Rasio serangan ditukar lalu sweep non-IID dan federasi far-domain diulang |
| 1C | Apakah temuan hanya berlaku untuk MLP dangkal? | `jC_04_deeper_model` | MLP lebih dalam / 1D-CNN + baseline XGBoost |

Keputusan: bila 1A–1C mengonfirmasi penjelasan kita, kalimat "future work" di naskah diganti bukti.
Bila ada yang tidak terkonfirmasi, penjelasan di naskah direvisi (ini tetap hasil yang valid).

## TAHAP 2 — Bukti sebab degradasi UNSW + pertahanan sadar-domain (inti kebaruan keamanan)

| Sub | Pertanyaan | Notebook |
|---|---|---|
| 2A | Apakah UNSW rusak karena adversarial training itu sendiri, atau karena agregasi lintas-domain? (adversarial training lokal tanpa agregasi) | `jD_01_local_advtrain` |
| 2B | Bisakah pertahanan sadar-domain (mis. ε / rasio per client) memulihkan UNSW tanpa menghilangkan keuntungan CIC? | `jD_02_domain_aware_at` |

Keputusan: ini penentu cerita. Bila 2B berhasil, naskah punya kontribusi konstruktif.
Bila gagal, kita laporkan apa adanya dan menimbang jurnal lain (mis. JOIN sebagai cadangan).

## TAHAP 3 — Skala dan ancaman khas FL

- 3A: lebih banyak client (K = 5–8) pada pasangan near dan far.
- 3B: satu skenario poisoning / label-flipping dengan agregator robust (Krum atau median).
- 3C (opsional): pasangan dataset ketiga dengan fitur standar (perlu diverifikasi).

## TAHAP 4 — Validitas data

- 4A: split per hari / waktu untuk CIC-IDS2017/2018 (bukan acak) untuk menepis kritik kebocoran.
- 4B: ulang partisi data dengan seed berbeda agar CI mencakup variasi data.
- 4C: recall per jenis serangan (label biner menyembunyikannya).

## TAHAP 5 — Infrastruktur dan klaim cloud

- Role SageMaker saat ini tidak boleh membuat stack EC2. Pilih: minta izin IAM, atau jalankan dari mesin lain.
- Minimal: validasi satu konfigurasi near-domain di EC2 dan tunjukkan hasilnya sama dengan simulasi.
- Jika tidak dilakukan: ubah judul agar tidak melebih-lebihkan "cloud testbed".

## TAHAP 6 — Penulisan untuk JISA

- Abstrak terstruktur ≤ 250 kata; Highlights 3–5 butir (≤ 85 karakter).
- CRediT, Data Availability (kode di GitHub/Zenodo), Declaration of competing interests.
- Pustaka 50–70; lengkapi metadata b1, b20, b22, b27.
- Sitasi versi konferensi ISRITI sebagai versi awal.

## TAHAP 7 — Pra-submit

- Review internal ala reviewer; surat pengantar yang menonjolkan kebaruan keamanan.
- Daftar 3–5 reviewer usulan; cek kemiripan teks terhadap ISRITI.

---

## Status

| Tahap | Status |
|---|---|
| 1A | selesai (`jC_01`): kekayaan fitur, bukan kedekatan domain, menjelaskan near>far; naskah sudah direvisi |
| 1B | notebook disiapkan (`jC_02`, `jC_03`), menunggu dijalankan |
| 1C | belum |
| 2–7 | belum |

