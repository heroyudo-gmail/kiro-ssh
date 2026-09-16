# `evolusion/shared/` — Aset Warisan dari Paper 1 (dipakai ulang, tidak diulang)

Berkas di folder ini **disalin dari `../../unswnb-15/`** (Paper 1) agar Paper 3 tidak
mengulang kerja yang sudah selesai & tervalidasi. Semua adalah **hasil nyata** Paper 1.

> Prinsip: pakai ulang fondasi yang sama (dataset, SFM, fitur, extractor). **Hanya**
> ganti bagian yang tujuannya memang berbeda di Paper 3 (biner → multi-class + open-set).

## Isi & asal

| Berkas | Asal (Paper 1) | Dipakai ulang untuk | Perlu diubah di Paper 3? |
|---|---|---|---|
| `feature_inventory.json` | `unswnb-15/feature_inventory.json` | Inventaris fitur CIC (68) & UNSW (42) + extractor | **Tidak** — identik |
| `mapping_validation.json` | `unswnb-15/mapping_validation.json` | Hasil validasi SFM (pasangan aligned/mismatch); dasar 9 fitur Model A | **Tidak** — identik |
| `model_efficiency.json` | `unswnb-15/model_efficiency.json` | Profil efisiensi (ukuran/latensi/throughput) untuk klaim deployability | **Ya (ukur ulang)** — angka ini untuk model BINER; Paper 3 multi-class |
| `extract9_infer_reference.py` | `unswnb-15/aws/unsw_extract_infer.py` | Ekstraksi 9-fitur SFM via NFStream + audit satuan (`duration`=µs) | **Sebagian** — `extract9()` dipakai apa adanya; head inferensi diganti multi-class + open-set |

## Yang TIDAK ikut disalin (dan alasannya)

- **Dataset `.pkl` (`cleaned_100.pkl`, dst) & partisi CSV UNSW** — besar, diblokir
  `.gitignore` / disimpan di S3. Ambil dari sumber yang sama seperti Paper 1.
- **Artefak model & scaler deployment** (`modelA_9feat.json`, `deploy_meta_9feat.json`)
  — tidak di repo (S3). Selain itu Paper 3 butuh artefak **multi-class** sendiri
  (mis. `model_multiclass_9feat.json` + `deploy_meta_mc.json` yang juga memuat
  **centroid & kovarians per-kelas** untuk skor Mahalanobis open-set).
- **Notebook Paper 1/2** (`01`–`25`) — tetap di `unswnb-15/notebooks/`; Paper 3 memulai
  penomoran dari `30_` (drift/streaming). Catatan: `24_multiclass.ipynb`,
  `25_multiclass_aws.ipynb`, dan `30_drift_detector_poc.ipynb` di Paper 1 relevan sebagai
  titik-awal — rujuk, jangan gandakan.

## Ringkas: 9 fitur SFM Model A (basis Paper 3)

`dur, spkts, dpkts, sbytes, dbytes, smean, dmean, sload, dload`
(padanan CIC: Flow Duration, Tot Fwd/Bwd Pkts, TotLen Fwd/Bwd Pkts, Fwd/Bwd Pkt Len Mean,
Flow Byts/s, Bwd Pkts/s). `swin`/`dwin` **dibuang** (TCP window mismatch);
`sinpkt`/`dinpkt` (Model B) tidak menolong generalisasi.
