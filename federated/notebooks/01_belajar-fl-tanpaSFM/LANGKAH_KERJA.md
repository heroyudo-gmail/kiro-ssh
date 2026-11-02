# LANGKAH KERJA -- Jalur FL tanpa-SFM menuju submit paper

> **Fungsi file ini:** catatan langkah agar bisa dilanjutkan di PC mana pun.
> Besok di kantor: `git pull` dulu, lalu ikuti checklist di bawah dari posisi terakhir.
> **Muara:** submit `../paper-survey.md` (target realistis Sinta 2+; naskah menargetkan JICTRA).
> **Prinsip:** TANPA SFM (SFM masih review jurnal, bukan rujukan). Angka HARUS dari
> eksekusi nyata di SageMaker/EC2 -- jangan mengarang; yang belum jalan = tetap `[TBD]`.

---

## POSISI TERAKHIR (update: 2026-09-06, dikerjakan di PC rumah)

- [x] Reorganisasi folder `federated/notebooks/` -> 4 subfolder (commit 0d8852a).
- [x] Notebook belajar dibuat & di-push: `01`-`06` + README (commit 8cbf4d0, 144b982).
- [ ] **BELUM** ada satu pun notebook belajar yang DIJALANKAN di SageMaker -> semua angka masih kosong.
- [ ] Notebook survey (`../02_survey-tanpaSFM/`) belum dijalankan untuk paper.
- [ ] `../paper-survey.md` Bagian 4.3 masih `[TBD]` semua.

> **Lanjut dari sini:** mulai LANGKAH 1 di bawah (di SageMaker).

---

## PETA: notebook -> klaim paper

Paper utama `../paper-survey.md` punya klaim R1-R6. Pemetaannya:

| Klaim | Isi | Notebook sumber |
|---|---|---|
| R1 | FedAvg vs FedProx | belajar `03`,`05`,`06` (single) + survey `s06` |
| R2 | dampak non-IID (titik putus alpha) | belajar `04`,`06` (single) + survey `s05` |
| R3 | cross-dataset FL sulit/kolaps | survey `s03` (+ run EC2) |
| R4 | biaya cloud (bytes/round, latensi) | run EC2 (`../aws/fed-runbook-survey.md`) |
| R5 | evasion FGSM/PGD/JSMA | survey `s14` |
| R6 | adversarial training (defense) | survey `s15` (+ run EC2) |

---

## LANGKAH KERJA (urut; centang saat selesai)

### LANGKAH 1 -- Fondasi: jalankan jalur belajar (single-dataset, R1 & R2)
Di SageMaker, folder ini (`01_belajar-fl-tanpaSFM/`):
- [ ] `git pull`
- [ ] Jalankan `01_data_partition.ipynb` -> hasil di `fl_data/` (dataset di-sync dari S3 bila perlu).
- [ ] Jalankan `02_local_vs_central.ipynb` -> `learn_out/02_baselines.csv`
- [ ] Jalankan `03_fedavg.ipynb` -> `learn_out/03_fedavg.csv`
- [ ] Jalankan `04_noniid_dirichlet.ipynb` -> `learn_out/04_noniid.csv`
- [ ] Jalankan `05_fedprox.ipynb` -> `learn_out/05_fedprox.csv`
- [ ] Jalankan `06_multiseed_ci.ipynb` -> `learn_out/06_multiseed_ci.csv`  **(ANGKA R1 & R2 siap-paper)**
- [ ] (opsional) upload `learn_out/` ke S3 untuk arsip.

### LANGKAH 2 -- Survey cloud: run nyata di EC2 (R3, R4, R6)
Ikuti `../aws/fed-runbook-survey.md`:
- [ ] Jalankan `../02_survey-tanpaSFM/s01_fed_data_partition.ipynb` -> partisi ke S3 `unsw-far/federated_survey/data/`.
- [ ] Run FedAvg cross-dataset di EC2 (`S_R3`) -> `global_final.npz`  (R3 + biaya R4)
- [ ] Run adversarial training di EC2 (`S_R6`, `--adv-ratio 0.5 --adv-eps 0.1`)  (R6)

### LANGKAH 3 -- Survey simulasi: notebook (R2 sweep, R1, CI, R5)
Di `../02_survey-tanpaSFM/`:
- [ ] `s03_fedavg_crossdataset.ipynb` -> `survey_out/r3_crossdataset.csv` (R3, tarik hasil EC2)
- [ ] `s05_noniid_sweep.ipynb` (set DATASET=unsw lalu cic) (R2)
- [ ] `s06_fedprox_comm.ipynb` (R1 + biaya R4)
- [ ] `s07_multiseed_ci.ipynb` (CI R1-R3)
- [ ] `s14_adv_evasion.ipynb` (R5, offline)
- [ ] `s15_adv_training.ipynb` (R6, tarik hasil EC2)

### LANGKAH 4 -- Isi naskah `../paper-survey.md`
- [ ] Isi tabel Bagian 4.3 (kolom "Angka lab kami") dari semua CSV -> ganti `[TBD]`.
      - R1, R2 dari `learn_out/06_multiseed_ci.csv` (+ survey s06/s07 untuk cross-dataset).
      - R3 dari `survey_out/r3_crossdataset.csv`.
      - R4 dari log EC2 (bytes/round, latensi).
      - R5 dari s14, R6 dari s15.
- [ ] Isi kolom "Bertahan?" per klaim (jujur: ya/tidak/sebagian).
- [ ] Tulis temuan di Abstrak (ganti `[TBD: ringkas temuan]`) dan Bagian 7 (Kesimpulan).
- [ ] Pilih judul English final (ada 4 opsi di atas naskah).

### LANGKAH 5 -- Gambar & finalisasi submit
- [ ] (menunggu dibuat) notebook `07_figures.ipynb` -> gambar siap-paper dari `learn_out/*.csv`.
- [ ] Finalisasi referensi IEEE, cek konsistensi angka .md vs rencana .tex.
- [ ] Siapkan berkas submit sesuai template JICTRA.

---

## CATATAN PENTING (jangan lupa)
- **Framing temuan negatif = kontribusi, bukan kegagalan.** Kalau FedAvg cross-dataset
  kolaps, bingkai sebagai "reality check terukur" + analisis sebab (lihat pola di
  `../documentation_federated.md` TEMA 2). Reviewer menghargai kejujuran yang dianalisis.
- **Model identik** di semua notebook belajar & survey: MLP numpy `d->128->64->1`,
  z-score lokal per-klien (lihat `../aws/fed_node_survey.py`). Jangan ubah tanpa alasan.
- **SFM tidak dipakai di jalur ini.** Folder `../03_federated-denganSFM/` (Paper 6) TERPISAH.
- **Shell:** jangan tulis file lewat PowerShell `Set-Content -Encoding UTF8` (menambah BOM).
