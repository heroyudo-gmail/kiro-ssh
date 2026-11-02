# notebooks/01_belajar-fl-tanpaSFM/ -- Jalur BELAJAR Federated Learning (TANPA SFM)

Folder ini berisi notebook **belajar** FL dari nol, **tanpa SFM**. Tujuannya memahami
mekanik FL yang dipakai di riset survey (`../02_survey-tanpaSFM/`), bukan menghasilkan
angka untuk paper. Karena itu modelnya dibuat **identik** dengan node riset
`../../aws/fed_node_survey.py`: MLP numpy `d -> 128 -> 64 -> 1` (ReLU, sigmoid, BCE,
SGD) dengan **z-score lokal per-klien**. Yang dipelajari di sini langsung nyambung ke
baseline SOTA tanpa-SFM (FedAvg, FedProx, non-IID), bukan contoh mainan terpisah.

## Prinsip
- **Tanpa SFM.** SFM (metode kami) masih dalam review jurnal, jadi tidak dipakai di
  jalur belajar maupun sebagai pondasi. Satu dataset (CIC-IDS2017) dibagi ke beberapa
  klien -- tidak ada penyelarasan fitur lintas-dataset.
- **Satu dataset, banyak klien.** CIC-IDS2017 dipartisi ke K=4 klien.
- **Angka = hasil eksekusi nyata** di SageMaker; jangan mengarang.

## Peta notebook (urut dijalankan)

| Notebook | Yang dipelajari | Output |
|---|---|---|
| `01_data_partition.ipynb` | Bagi 1 dataset -> K klien IID (stratified) | `fl_data/*.npz` |
| `02_local_vs_central.ipynb` | Dua bound: centralized (atas) vs lokal-saja (bawah) | `learn_out/02_baselines.csv` |
| `03_fedavg.ipynb` | Inti FedAvg: broadcast -> latih lokal -> agregasi tertimbang | `learn_out/03_fedavg.csv` |
| `04_noniid_dirichlet.ipynb` | Efek non-IID (sweep Dirichlet alpha) pada FedAvg | `learn_out/04_noniid.csv` |
| `05_fedprox.ipynb` | FedProx (proximal term mu) meredam non-IID | `learn_out/05_fedprox.csv` |

## Alur di SageMaker
1. `git pull` di SageMaker.
2. Jalankan `01` -> partisi tersimpan di `fl_data/` (dataset di-sync dari S3 bila perlu).
3. Jalankan `02` -> `05` berurutan; tiap notebook menulis CSV ke `learn_out/`.
4. (Opsional) upload `learn_out/` ke S3 untuk arsip.

## Hubungan dengan folder lain
- `../02_survey-tanpaSFM/` : versi RISET (cross-dataset, multi-seed CI, adversarial)
  yang hasilnya dipakai di `../paper-survey.md`. Logika FedAvg/FedProx/MLP identik.
- `../03_federated-denganSFM/` : eksperimen Paper 6 berbasis SFM (TERPISAH, bukan rujukan).
- `../04_adversarial-fl/` : eksperimen serangan/pertahanan FL.
