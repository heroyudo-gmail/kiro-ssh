# notebooks/01_belajar-fl-tanpaSFM/ -- Jalur BELAJAR + FONDASI Federated Learning (TANPA SFM)

Folder ini berisi notebook **belajar** FL dari nol, **tanpa SFM**, yang sekaligus
berfungsi sebagai **fondasi/baseline** untuk paper utama `../paper-survey.md`. Model
dibuat **identik** dengan node riset `../../aws/fed_node_survey.py`: MLP numpy
`d -> 128 -> 64 -> 1` (ReLU, sigmoid, BCE, SGD) dengan **z-score lokal per-klien**,
supaya angka yang dihasilkan di sini sebanding dan dapat langsung dipakai di paper.

**Muara: paper submittable (target Sinta 2+).** Paper utama = `../paper-survey.md`.
Folder ini mengisi klaim **R1** (FedAvg vs FedProx) dan **R2** (dampak non-IID) pada
single-dataset; versi cross-dataset (**R3**) dan adversarial (**R5/R6**) ada di
`../02_survey-tanpaSFM/`.

## Prinsip
- **Tanpa SFM.** SFM (metode kami) masih dalam review jurnal, jadi tidak dipakai di
  jalur belajar maupun sebagai pondasi/rujukan. Satu dataset (CIC-IDS2017) dibagi ke
  beberapa klien -- tidak ada penyelarasan fitur lintas-dataset.
- **Satu dataset, banyak klien.** CIC-IDS2017 dipartisi ke K=4 klien.
- **Angka = hasil eksekusi nyata** di SageMaker; jangan mengarang. Belum dijalankan
  = tetap `[TBD]` di paper.

## Peta notebook (urut dijalankan)

| Notebook | Yang dipelajari | Output | -> Paper |
|---|---|---|---|
| `01_data_partition.ipynb` | Bagi 1 dataset -> K klien IID (stratified) | `fl_data/*.npz` | prasyarat |
| `02_local_vs_central.ipynb` | Dua bound: centralized (atas) vs lokal-saja (bawah) | `learn_out/02_baselines.csv` | konteks |
| `03_fedavg.ipynb` | Inti FedAvg: broadcast -> latih lokal -> agregasi tertimbang | `learn_out/03_fedavg.csv` | R1 (baseline) |
| `04_noniid_dirichlet.ipynb` | Efek non-IID (sweep Dirichlet alpha) pada FedAvg | `learn_out/04_noniid.csv` | R2 |
| `05_fedprox.ipynb` | FedProx (proximal term mu) meredam non-IID | `learn_out/05_fedprox.csv` | R1 |
| `06_multiseed_ci.ipynb` | **Multi-seed {13,42,101,202,303} + 95% CI** (siap-paper) | `learn_out/06_multiseed_ci.csv` | **R1, R2 (angka final)** |

> `02`-`05` menghasilkan satu angka (cepat, untuk paham mekanik). `06` mengulang
> lintas 5 seed + CI -> inilah angka yang layak masuk tabel 4.3 paper.

## Alur di SageMaker
1. `git pull` di SageMaker.
2. Jalankan `01` -> partisi tersimpan di `fl_data/` (dataset di-sync dari S3 bila perlu).
3. Jalankan `02` -> `06` berurutan; tiap notebook menulis CSV ke `learn_out/`.
4. Isi kolom 'Angka lab kami' R1/R2 di `../paper-survey.md` Bagian 4.3 dari
   `learn_out/06_multiseed_ci.csv`.
5. (Opsional) upload `learn_out/` ke S3 untuk arsip.

## Jalur kritis menuju submit (paper-survey)
1. **Fondasi (folder ini):** jalankan `01`-`06` -> angka R1, R2 (single-dataset).
2. **Survey cloud:** `../02_survey-tanpaSFM/s01` + run EC2 (`../aws/fed-runbook-survey.md`)
   -> R3 (cross-dataset), R6 (adversarial training).
3. **Survey simulasi:** `s05` (R2 sweep), `s06` (R1 FedProx), `s07` (multi-seed CI),
   `s14` (R5 evasion).
4. **Isi `../paper-survey.md` Bagian 4.3** dari semua CSV -> ganti `[TBD]`.
5. Finalkan Abstrak, Bagian 7 (Kesimpulan), pilih judul English.

## Hubungan dengan folder lain
- `../02_survey-tanpaSFM/` : versi RISET (cross-dataset, multi-seed CI, adversarial)
  -> paper utama `../paper-survey.md`. Logika FedAvg/FedProx/MLP identik dengan folder ini.
- `../03_federated-denganSFM/` : eksperimen Paper 6 berbasis SFM (TERPISAH, bukan rujukan).
- `../04_adversarial-fl/` : eksperimen serangan/pertahanan FL.
