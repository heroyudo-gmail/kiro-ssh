# `evolusion/notebooks/` — Notebook Eksperimen Paper 3

Notebook dijalankan di **SageMaker** (konsisten Paper 1). Prinsip: **semua angka dari
eksekusi nyata & reproducible**; artefak besar ke S3 (`s3://<BUCKET>/evolusion/...`),
tidak masuk Git.

Penomoran mulai `01_` (folder mandiri Paper 3). Beberapa notebook **melanjutkan** aset
Paper 1 (lihat `../documentation.md` §1b) — tidak mengulang dari nol.

| Notebook | Tahap (roadmap) | Isi | Melanjutkan |
|---|---|---|---|
| `01_known_base_multiclass.ipynb` | T1 | Muat 9-fitur SFM CIC & UNSW, skema label multi-class, split **known vs held-out**, latih model *known*, **simpan centroid + kovarians per-kelas** (bekal open-set) | `../../unswnb-15/notebooks/24_multiclass.ipynb` |
| `02_openset_scorer.ipynb` (rencana) | T3 | Skor Mahalanobis + confidence; kalibrasi τ; AUROC known-vs-unknown pada held-out | — |
| `03_novelty_clustering.ipynb` | T3b | **DIBUAT** — HDBSCAN pada flow unknown (lolos τ); uji "≈ M cluster"; homogeneity/ARI; profil cluster untuk LLM | — |
| `04_drift_detector.ipynb` | T2 | **DIBUAT** — formalkan $W_1$+CUSUM, delay deteksi, sensitivitas W | `../../unswnb-15/notebooks/30_drift_detector_poc.ipynb` |
| `05_labeling_oracle_llm.ipynb` | T4 | **DIBUAT** — oracle mayoritas + LLM auto-name (fallback rule-based); akurasi vs oracle | — |
| `06_incremental_replay.ipynb` (rencana) | T5 | Class-incremental + replay memory; ablation forgetting | — |
| `07_guardrail_promotion.ipynb` (rencana) | T6 | Gerbang promosi (recall lama tetap & baru naik); uji poisoning/rollback | — |
| `08_scenarioA_heldout.ipynb` (rencana) | T7 | Skenario A end-to-end offline | — |
| `09_scenarioB_crossdataset.ipynb` (rencana) | T8 | Skenario B cross-dataset novelty | — |

> Skenario C (AWS online, T9) + GuardDuty (T9b) dioperasikan lewat `../aws/runbook.md`,
> bukan notebook tunggal.
