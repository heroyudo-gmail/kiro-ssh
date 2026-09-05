# Rencana Deployment AWS (T10) — Cross-Network Robust NIDS (UNSW-NB15 × CIC-IDS2018)

> **Status:** RENCANA (belum dieksekusi). Disusun mengadopsi pengalaman nyata deployment
> **NIDS-01** (`CICDDoS2018/aws/skenario-testing-nids01.md`) yang sudah terbukti jalan.
> Eksekusi dilakukan saat siap (butuh biaya AWS). Semua angka hasil nanti diisi dari
> eksperimen nyata — tidak dikarang.

---

## 1. Tujuan T10 — DUA FASE TERPISAH

T10 terdiri dari **dua eksperimen berbeda yang tidak boleh dicampur**, karena mengukur
hal yang berbeda:

### Fase 1 — Uji FAR (JANGKA PANJANG, TANPA serangan)
- **Pertanyaan:** dari semua trafik **normal**, berapa yang **salah** ditandai model
  sebagai serangan (*False Alarm Rate*)?
- **Trafik:** 100% benign (tidak ada serangan sama sekali). Setiap prediksi "attack"
  otomatis = *false alarm*.
- **Durasi:** panjang (3–7 hari) — WAJIB panjang karena FAR butuh variasi trafik normal
  lintas siklus siang/malam dan weekday/weekend agar angkanya stabil & kredibel.
- **Metrik:** FAR = (flow benign diprediksi attack) / (total flow benign).

### Fase 2 — Uji Deteksi (SINGKAT, DENGAN serangan)
- **Pertanyaan:** apakah model menangkap serangan pada trafik AWS live (mereplikasi pola
  offline T3–T9)?
- **Trafik:** benign + serangan berlabel (ground truth diketahui dari timeline).
- **Durasi:** singkat (~7 menit per run, pola NIDS-01).
- **Metrik:** MCC, F1, Precision, Recall (deteksi), + diagnostik *feature-extractor mismatch*.

> **PENTING:** FAR (Fase 1) dan deteksi (Fase 2) diukur **terpisah**. Menyuntikkan serangan
> ke Fase 1 akan merusak perhitungan FAR (flow "attack" jadi ambigu: benar-deteksi vs
> false-alarm). Keduanya menjawab pertanyaan berbeda dan dilaporkan sebagai hasil terpisah.

---

## 2. Pelajaran dari NIDS-01 yang WAJIB Dipakai (jangan ulangi kesalahan)

Diambil langsung dari catatan eksekusi NIDS-01:

1. **Capture di TARGET, bukan Analyzer.** Analyzer tidak berada di jalur trafik
   Attacker→Target, sehingga tcpdump di Analyzer menghasilkan pcap kosong (24 byte).
   Solusi terbukti: capture di Target (`capture_target.sh`) → upload S3 → Analyzer download.
2. **Interface `ens5`, bukan `eth0`.** EC2 modern (Amazon Linux 2023) memakai `ens5`.
3. **Capture per-interface (`-i ens5`), JANGAN `-i any`.** `-i any` = Linux cooked-mode (SLL)
   → NFStream menghasilkan **0 flow**.
4. **NFStreamer WAJIB `statistical_analysis=True`** agar 86 kolom fitur muncul.
5. **NFStream tidak mengekspos TCP window** → butuh **custom NFPlugin** (`nfstream_win_extract.py`)
   yang mem-parse `packet.ip_packet` (raw bytes). Untuk UNSW-NB15 kita **tidak** pakai
   swin/dwin (sudah dibuang di T2 karena mismatch), jadi plugin window **tidak wajib** —
   penyederhanaan yang menguntungkan.
6. **Idle/resume untuk hemat biaya:** hapus NAT Gateway + stop EC2 saat tidak dipakai;
   VPC/subnet/EC2(stopped)/IAM tetap ada. Resume: create NAT + start EC2.

---

## 3. Perbedaan Kunci vs NIDS-01 (khusus UNSW-NB15)

| Aspek | NIDS-01 (CIC) | T10 (UNSW-NB15 cross-network) |
|---|---|---|
| Fitur model | Top-10 CIC (butuh window plugin) | **9 fitur Model A** (dur, spkts, dpkts, sbytes, dbytes, smean, dmean, sload, dload) — **tanpa TCP window** |
| Plugin window NFStream | Wajib (Opsi A) | **Tidak perlu** (swin/dwin dibuang di T2) |
| Fokus utama | Matriks 2×2 serangan (S1–S4) | **FAR jangka panjang (3–7 hari)** + validasi cross-network |
| Model diuji | baseline vs robust CIC | baseline CIC, robust CIC, **few-shot adapted** (1% target) |
| Mapping fitur | NFStream → CIC Top-10 | NFStream → **9 fitur kanonik SFM** |

---

## 4. Arsitektur (mengikuti template NIDS-01)

| Komponen | Spesifikasi | Fungsi |
|---|---|---|
| VPC | 10.x.0.0/16 | Isolasi jaringan |
| Subnet Public | 10.x.1.0/24 | (opsional attacker) + NAT Gateway |
| Subnet Private | 10.x.2.0/24 | Target + Analyzer |
| EC2 Target/Sensor | t3.medium | Menjalankan layanan + **capture trafik (ens5)** |
| EC2 Analyzer | t3.medium | NFStream extract + inference + hitung FAR |
| S3 Bucket | — | Model (.json), scaler/meta, pcap, hasil |

> Reuse CloudFormation NIDS-01 (`nids01-05-vpc.yaml`, `-06-attacker`, `-07-target`,
> `-08-analyzer`, `-05-1-nat.yaml`) sebagai basis; ganti nama stack jadi `unsw-*`.

---

## 5a. Pipeline FASE 1 — FAR Jangka Panjang (TANPA serangan)

Berbeda dari NIDS-01 (7 menit), FAR butuh trafik **normal** kontinu berhari-hari.
**Tidak ada serangan pada fase ini.**

```
1. Deploy VPC + Target(sensor) + Analyzer + NAT (CloudFormation).
2. Upload model + deploy_meta (scaler 9 fitur) ke Analyzer/S3.
3. Bangkitkan TRAFIK NORMAL realistis di Target secara kontinu (TANPA serangan):
   - layanan web/SSH aktif + generator trafik benign terjadwal (cron):
     curl loop, apt/yum update berkala, unduhan file, sesi SSH sah, health-check, dsb.
   - variasikan siang/malam + weekday/weekend agar meniru fluktuasi harian nyata.
4. Capture bergulir di Target: tcpdump -i ens5, rotasi per jam (-G 3600 -w far_%Y%m%d_%H.pcap).
5. Setiap jam: upload pcap ke S3; Analyzer proses (NFStream 9 fitur → inference).
6. Karena SEMUA trafik = benign, setiap prediksi "attack" adalah FALSE ALARM.
   FAR = (jumlah flow diprediksi attack) / (total flow benign).
7. Agregasi per jam/hari → laporkan FAR per jam/hari + rata-rata sepanjang periode.
```

**Durasi:** idealnya **24 jam × 3–7 hari kontinu**. Opsi hemat: capture **terjadwal**
(mis. 3–4 jam per segmen pagi/siang/malam × beberapa hari) — WAJIB dilaporkan apa adanya
(bukan diklaim kontinu). Cakupan tetap harus mencakup variasi siang/malam & weekday/weekend.

**Model yang diuji untuk FAR:** (a) baseline CIC, (b) robust CIC, (c) few-shot adapted
(CIC + 1% UNSW). Bandingkan FAR ketiganya — hipotesis: model konservatif (robust) FAR lebih
rendah; model adapted lebih seimbang.

---

## 5b. Pipeline FASE 2 — Uji Deteksi (DENGAN serangan, singkat)

Mereplikasi pola NIDS-01 (~7 menit per run). Ground truth ditentukan dari **timeline**
(menit ke berapa serangan apa dijalankan).

```
1. (Reuse infra Fase 1.) Tambah node Attacker di subnet public.
2. Capture di TARGET (tcpdump -i ens5) selama run berlangsung.
3. Jalankan skenario serangan berlabel dari Attacker → Target.
4. Stop capture → pcap → S3 → Analyzer (NFStream 9 fitur → inference).
5. Cocokkan prediksi vs ground-truth timeline → hitung MCC/F1/Precision/Recall.
6. Jalankan diagnostik z-of-mean (real vs train scaler) → identifikasi feature mismatch.
```

**Skenario serangan (pola NIDS-01, ~7 menit):**

| Fase | Menit | Aktivitas | Tool | Ground truth |
|---|---|---|---|---|
| Warm-up | 0–1 | trafik normal | curl loop | Benign |
| Attack-1 | 1–3 | SSH Brute-Force (port 22) | Hydra | Attack |
| Attack-2 | 3–5 | DoS Slowloris (port 80) | slowloris | Attack |
| Attack-3 | 5–6 | DDoS SYN Flood (rate 200/s) | nping | Attack |
| Cool-down | 6–7 | trafik normal | curl loop | Benign |

**Dua varian trafik** (seperti NIDS-01): *clean* (serangan standar) dan *evasion*
(serangan + perturbasi level-paket: `tc netem` untuk jitter/IAT, padding payload untuk
ubah ukuran paket). Bandingkan degradasi baseline vs recovery robust — mereplikasi S1–S4.

**Model yang diuji:** baseline CIC, robust CIC, few-shot adapted (CIC + 1% UNSW).

---

## 6. Mapping Fitur NFStream → 9 Fitur Model A (kanonik SFM)

| # | Fitur kanonik (Model A) | Sumber NFStream | Catatan |
|---|---|---|---|
| 1 | duration  | `bidirectional_duration_ms` | konversi satuan bila perlu (z-score per dataset menyerap skala) |
| 2 | fwd_pkts  | `src2dst_packets` | persis |
| 3 | bwd_pkts  | `dst2src_packets` | persis |
| 4 | fwd_bytes | `src2dst_bytes` | persis |
| 5 | bwd_bytes | `dst2src_bytes` | persis |
| 6 | fwd_mean  | `src2dst_mean_ps` | ukuran paket rata-rata src→dst |
| 7 | bwd_mean  | `dst2src_mean_ps` | ukuran paket rata-rata dst→src |
| 8 | src_load  | turunan: `src2dst_bytes` / durasi (byte/s) | hitung manual bila kolom laju tak ada |
| 9 | dst_load  | turunan: `dst2src_packets` / durasi (pkt/s) | sesuaikan definisi (Bwd Pkts/s) |

> **Catatan kejujuran (penting):** sama seperti NIDS-01, NFStream ≠ CICFlowMeter ≠ Argus/Bro.
> Perbedaan definisi (mis. `mean_ps` termasuk header vs payload) akan menimbulkan
> *feature-extractor mismatch*. Ini **justru gap #2 paper Q1** — hasil real-traffic yang
> menyimpang dari offline WAJIB dilaporkan apa adanya sebagai bukti lapangan, bukan disembunyikan.
> Diagnostik z-of-mean (real vs train scaler) seperti NIDS-01 harus dijalankan untuk
> mengidentifikasi fitur paling menyimpang.

---

## 7. Estimasi Biaya (indikatif, verifikasi saat eksekusi)

- 2× EC2 t3.medium + 1 NAT Gateway + S3 + transfer.
- Deployment 3–7 hari kontinu: perkirakan biaya NAT + 2 EC2 berjalan penuh.
- Hemat: stop EC2 + hapus NAT saat jeda; pertimbangkan capture terjadwal (tidak 24 jam penuh)
  bila anggaran ketat, asalkan tetap mencakup variasi siang/malam.

---

## 8. Checklist Eksekusi (saat siap)

**Persiapan (sekali):**
- [ ] Siapkan model 9-fitur + `deploy_meta.json` (scaler mean/scale 9 fitur) di S3.
- [ ] Deploy CloudFormation (reuse template NIDS-01, ganti prefix `unsw-`).
- [ ] Verifikasi SSM online (butuh NAT aktif untuk private subnet).

**Fase 1 — FAR (jangka panjang, tanpa serangan):**
- [ ] Set generator trafik benign kontinu (TANPA serangan) + rotasi tcpdump `-i ens5 -G 3600`.
- [ ] Pipeline per-jam: pcap → S3 → NFStream(9 fitur) → inference → hitung false alarm.
- [ ] Agregasi FAR per jam/hari; simpan `far_daily.json` (hasil nyata).
- [ ] Catat durasi PERSIS (kontinu vs terjadwal) untuk dilaporkan jujur di naskah.

**Fase 2 — Deteksi (singkat, dengan serangan):**
- [ ] Deploy node Attacker; capture di Target `-i ens5`.
- [ ] Jalankan skenario serangan berlabel (clean + evasion), ~7 menit/run.
- [ ] Inference → MCC/F1/Precision/Recall vs ground-truth timeline.
- [ ] Jalankan diagnostik z-of-mean (real vs train) untuk deteksi feature mismatch (gap #2).

**Penutup:**
- [ ] Idle kembali (hapus NAT + stop EC2) setelah selesai.

---

## 9. Output yang Akan Mengisi Naskah (§12 + tabel efisiensi §3.4)

- **Fase 1:** `far_daily.json` / tabel FAR per jam-hari → isi hasil deployment di §12.
- **Fase 2:** tabel deteksi MCC/F1 (clean vs evasion, 3 model) → hasil real-traffic di §12;
  diagnostik feature-mismatch → memperkuat pembahasan gap #2.
- Ukuran biner model 9-fitur + latency inferensi per flow → isi Tabel efisiensi §3.4
  (slot `[TBD]` saat ini).

> Semua diisi HANYA dari pengukuran nyata. Durasi Fase 1 dilaporkan apa adanya (kontinu
> atau terjadwal), tidak melebih-lebihkan.

> Semua diisi HANYA dari pengukuran nyata. Sampai eksekusi dilakukan, slot tetap ditandai
> sebagai rencana agar naskah tidak memuat angka karangan.
