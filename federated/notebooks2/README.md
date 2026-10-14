# notebooks2/ — Notebook untuk PAPER SURVEY (bukan Paper 4)

Folder ini berisi notebook eksperimen untuk **paper survey FL-NIDS**
(`../paper-survey.md`), terpisah dari `../notebooks/` milik Paper 4.

**Perbedaan utama dari notebooks Paper 4:**
- **TIDAK memakai SFM** (metode kami yang masih dalam review jurnal). Penyelarasan
  skema fitur CIC↔UNSW memakai **manual feature-name alignment** — metode cross-dataset
  yang sudah lazim di literatur ([F11]) — diperlakukan sebagai *setup*, bukan kontribusi.
- Output & data di S3 prefix **terpisah**: `unsw-far/federated_survey/` (bukan
  `unsw-far/federated/` milik Paper 4), agar tidak saling menimpa.
- Penamaan `s01_*` .. `s15_*` (prefix `s` = survey).

## Peta notebook (rencana)

| Notebook | Fungsi | Klaim | Status |
|---|---|---|---|
| `s01_fed_data_partition.ipynb` | partisi data per-klien + manual alignment | prasyarat semua R | ✅ dibuat |
| `s03_fedavg_crossdataset.ipynb` | FedAvg cross-dataset vs centralized/local | R3 | ✅ dibuat |
| `s14_adv_evasion.ipynb` | FGSM/PGD + saliency/JSMA (constrained, offline) | R5 | ✅ dibuat |
| `s05_noniid_sweep.ipynb` | sweep Dirichlet α, cari titik putus (simulasi) | R2 | ✅ dibuat |
| `s06_fedprox_comm.ipynb` | FedAvg vs FedProx + bytes/round (simulasi+analitis) | R1, R4 | ✅ dibuat |
| `s07_multiseed_ci.ipynb` | agregasi multi-seed + CI + signifikansi | R1–R3 | ✅ dibuat |
| `s15_adv_training.ipynb` | adversarial training sebagai defense | R6 | ✅ dibuat |

## Urutan menjalankan di SageMaker (ringkas)
1. **s01** → partisi data ke S3 (`federated_survey/data/`). WAJIB pertama.
2. **Run EC2** (lihat `../aws/fed-runbook-survey.md`): R3 (`S_R3`), R1-FedProx opsional,
   R6 (`S_R6`, pakai `--adv-ratio 0.5 --adv-eps 0.1`).
3. **s03** (R3), **s14** (R5, offline), **s15** (R6) → tarik `global_final.npz`, hitung metrik.
4. **s05** (R2, set `DATASET=unsw` lalu `cic`), **s06** (R1+R4), **s07** (CI) → simulasi di notebook.
5. Isi tabel §4.3 `paper-survey.md` dari CSV di `survey_out/` + S3 `federated_survey/results/`.

## Catatan metodologi (jujur, untuk §6 naskah)
- **R3, R6, R4-latensi** = deployment NYATA di 3 EC2 (bukti cloud, klaim C2).
- **R1, R2, R5, R7-CI, R4-bytes** = simulasi di notebook (logika FedAvg/FedProx/MLP/
  z-score IDENTIK `fed_node_survey.py`). Dipakai karena sweep butuh banyak kombinasi;
  disebut eksplisit di Ancaman Validitas agar jujur.

**Node FL survey:** `../aws/fed_node_survey.py` (✅ dibuat) — FedAvg + FedProx (`--mu`)
+ hook adversarial training (`--adv-ratio`,`--adv-eps`), baca prefix `federated_survey/`.
**Runbook survey:** `../aws/fed-runbook-survey.md`.

**Aturan kejujuran:** semua angka hasil = `[TBD]` sampai dijalankan nyata; jangan
mengarang. Jalankan di SageMaker/EC2 ber-data; hasil disimpan ke S3 sebelum teardown.
