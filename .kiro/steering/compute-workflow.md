# Compute & Research Workflow (SageMaker-centric)

Aturan ini berlaku untuk SEMUA paper dan SEMUA notebook `.ipynb` di workspace
`kiro-ssh` (paper 1-4, adversarial, XAI, dan pekerjaan berikutnya).

## Prinsip utama

- **Semua komputasi dijalankan di AWS SageMaker, bukan di komputer lokal.**
  Tujuannya: terpusat, reproducible, tidak membebani laptop. Biaya AWS di-support
  mitra AWS APN pengguna, jadi JANGAN menyarankan "jalankan lokal saja" atau
  mengkhawatirkan biaya/spek lokal.
- Komputer lokal hanya untuk **menulis paper** (`.tex`/`.md`) dan mengisi angka hasil.

## Alur kerja baku (sudah dipakai di 3 paper sebelumnya)

1. Kiro membuat/menyiapkan file `.ipynb` sesuai kebutuhan komputasi paper.
2. Push notebook ke GitHub.
3. Pengguna masuk SageMaker, lalu `git pull` dari GitHub.
4. Pengguna mengeksekusi notebook di SageMaker.
5. Hasil (artefak: JSON/CSV/angka, dan figure bila ada) di-upload ke S3.
6. Komputer lokal men-download hasil dari S3 ke lokal.
7. Angka hasil dipakai mengisi placeholder `[ISI]` di paper.

## Konsekuensi untuk cara Kiro membuat notebook

- Notebook harus **self-contained dan siap jalan headless di SageMaker**:
  - Instalasi paket dilakukan di dalam notebook (sel `pip install ...`) bila perlu.
  - Path dataset eksplisit dan mudah diubah (sel KONFIG di atas). Dataset umumnya
    datang dari S3 — sediakan variabel path yang jelas.
  - Output ditulis rapi ke folder `artifacts/` (JSON/CSV) agar gampang di-upload ke S3.
  - Semua angka hasil HARUS dari eksekusi nyata; jangan mengarang angka untuk paper.
- Jangan menambahkan langkah yang mengandaikan eksekusi di mesin lokal pengguna.

## Catatan yang masih perlu dikonfirmasi pengguna (lengkapi saat diketahui)

- Jenis environment: SageMaker Studio (JupyterLab) vs Notebook Instance klasik.
- Lokasi/bucket S3 untuk dataset mentah dan untuk artefak hasil.
- Instance type default (untuk XGBoost/RF tabular cukup CPU ber-RAM besar,
  mis. `ml.m5.2xlarge` / `ml.r5.xlarge`; GPU tidak diperlukan untuk model pohon).
