# Runbook T10 — UNSW-NB15 Real-Traffic (3-EC2, pola NIDS-01)

> Panduan eksekusi **berurutan** + cara **resume cepat** + cara **hapus infra** setelah selesai.
> Pengetahuan disimpan di sini agar percobaan bisa diulang cepat. **Region:** ap-southeast-1.
> Semua hasil (pcap, metrik, FAR) diunggah ke S3 SEBELUM infra dihapus.

---

## 0. Arsitektur (ringkas)

- **VPC** `10.5.0.0/16` — public subnet (Attacker) + private subnet (Target, Analyzer) + IGW + NAT.
- **Attacker** (public): jalankan serangan (Fase 2).
- **Target** (private): layanan SSH/HTTP + **CAPTURE di sini** (pelajaran NIDS-01).
- **Analyzer** (private): NFStream (9 fitur SFM) + inferensi XGBoost + metrik.
- Akses instance via **SSM Session Manager** (bukan SSH publik). Butuh NAT aktif.
- IaC: `unsw-vpc-3ec2.yaml` (satu stack gabungan). Biaya: `cost-estimate.md`.

---

## 1. Prasyarat (sekali)

**Bucket S3:** `ssh-detection-features-232032302717` (sama dengan NIDS-01).

- **Model + meta (dari SageMaker):** jalankan `notebooks/09_model_efficiency.ipynb` sampai
  sel terakhir. Sel itu otomatis:
  - menyimpan `modelA_9feat.json` (model XGBoost 9-fitur) dan
  - `deploy_meta_9feat.json` (`{"features":[9], "scaler_mean":[9], "scaler_scale":[9]}`), lalu
  - **mengunggah keduanya** ke `s3://ssh-detection-features-232032302717/unsw-far/models/`.
  (Jika upload gagal karena izin, upload manual dengan `aws s3 cp` — perintah tercetak di notebook.)
- **Skrip → S3:** `unsw_extract_infer.py`, `capture_target.sh`, `attack_scenario.sh`,
  `benign_traffic.sh` → `s3://ssh-detection-features-232032302717/unsw-far/scripts/`.
  > **Cara cepat (satu perintah):** dari folder `aws/`, jalankan `./upload_to_s3.sh`. Skrip ini
  > otomatis: (a) **GATE** memverifikasi `unsw_extract_infer.py` sudah versi ter-FIX (`dur_feat_us`),
  > (b) cek kredensial & akses bucket, (c) upload keempat skrip (+ model bila ada di folder), lalu
  > (d) menampilkan isi S3. Batal bila gate/kredensial gagal. Override: `S3_BUCKET=... REGION=... ./upload_to_s3.sh`.
  > **Pastikan `unsw_extract_infer.py` sudah versi ter-FIX** (fitur `duration` dalam
  > MIKRODETIK agar cocok scaler CIC, `dur_feat_us = dur_ms*1000`; pembagi laju tetap
  > detik `dur_s = dur_ms/1000`). Cek: `grep dur_feat_us unsw_extract_infer.py`
  > harus muncul sebelum di-upload. Lihat prasyarat ramp di Bagian 3A.

> EC2 tidak perlu SageMaker: cukup `aws s3 cp` dari bucket di atas (langkah §2).

---

## 2. Deploy infra (DUA stack terpisah: VPC lalu EC2)

> Arsitektur T10: **2 EC2** = **Attacker** + **Target+Analyzer (GABUNGAN)**, keduanya
> di PRIVATE subnet, internet via NAT, akses via SSM. Karena capture & inferensi di
> SATU mesin (target-analyzer), TIDAK perlu upload/download pcap antar-node.
> (Template lama 3-EC2 `unsw-vpc-3ec2.yaml` tetap disimpan untuk referensi.)

**2.1 Stack VPC** (jaringan + NAT + SG + IAM):
```bash
aws cloudformation create-stack --stack-name unsw-far-vpc \
  --template-body file://unsw-vpc.yaml \
  --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation wait stack-create-complete --stack-name unsw-far-vpc --region ap-southeast-1
```

**2.2 Stack EC2** (2 instance; mereferensikan VPC via ImportValue — `ProjectName` harus
sama, default `unsw-far`):
```bash
aws cloudformation create-stack --stack-name unsw-far-ec2 \
  --template-body file://unsw-2ec2.yaml \
  --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation wait stack-create-complete --stack-name unsw-far-ec2 --region ap-southeast-1
aws cloudformation describe-stacks --stack-name unsw-far-ec2 --region ap-southeast-1 \
  --query "Stacks[0].Outputs" --output table
```
Catat Output: `AttackerId, TargetAnalyzerId, AttackerPrivateIp, TargetAnalyzerPrivateIp`.

Verifikasi SSM online (~2 menit):
```bash
aws ssm describe-instance-information --region ap-southeast-1 \
  --query "InstanceInformationList[].{Id:InstanceId,Ping:PingStatus}" --output table
```

Unduh skrip+model di **Target+Analyzer** (via SSM shell; capture & inferensi satu mesin):
```bash
export S3_BUCKET=ssh-detection-features-232032302717
aws s3 cp s3://$S3_BUCKET/unsw-far/scripts/ /opt/unsw/scripts/ --recursive
aws s3 cp s3://$S3_BUCKET/unsw-far/models/  /opt/unsw/models/  --recursive
chmod +x /opt/unsw/scripts/*.sh
```

---

## 3. FASE 1 — FAR (TANPA serangan)

> **JANGAN langsung 24 jam.** Jalankan **RAMP BERTAHAP S0->D1->D2->D3 (Bagian 3A)** dulu:
> smoke ~3m (gate) -> **1 jam** -> **6 jam** -> **24 jam**, tiap tahap lolos GATE. Bagian
> di bawah ini (24 jam kontinu) adalah tahap **D3** — dijalankan HANYA setelah S0/D1/D2 lolos.
>
> **Desain multi-durasi (percobaan bertahap untuk PERBANDINGAN, bukan sekadar gate).**
> Titik durasi: **1 jam -> 6 jam -> 24 jam**, lalu eskalasi opsional **3 hari -> 7 hari**.
> Tujuannya bukan cuma validasi pipeline, tetapi **membandingkan FAR antar-durasi observasi**
> (lihat Tabel §7.2) — membuktikan FAR rendah **stabil** seiring waktu, bukan artefak snapshot
> pendek. Setiap durasi memakai infra yang SAMA; hanya waktu capture yang berbeda. Eskalasi
> 3-7 hari (variasi weekday/weekend) dijalankan setelah 24 jam kredibel.
>
> **Penting agar FAR berisi:** jaga trafik normal tetap aktif (banyak flow benign) selama
> 24 jam — curl loop + unduhan berkala + sesi SSH terjadwal. FAR dari puluhan ribu flow
> jauh lebih kuat daripada dari puluhan flow.

Di **Target+Analyzer** (mesin gabungan; biarkan berjalan ~24 jam):
```bash
cd /opt/unsw/scripts && sudo S3_BUCKET=ssh-detection-features-232032302717 ./capture_target.sh far
```
Bangkitkan trafik NORMAL (cron/loop di Target atau dari Attacker): `curl` berkala,
`dnf update`, unduhan, sesi SSH sah. TIDAK ADA serangan pada fase ini.

Per jam / berkala, di **mesin yang sama** (proses pcap yang sudah dirotasi; capture &
inferensi satu host, TIDAK perlu transfer antar-node):
```bash
# (opsional) backup pcap ke S3
aws s3 cp /opt/unsw/captures/ s3://ssh-detection-features-232032302717/unsw-far/captures/ --recursive
export S3_BUCKET=ssh-detection-features-232032302717
python3 /opt/unsw/scripts/unsw_extract_infer.py far /opt/unsw/captures/far_YYYYMMDD_HH.pcap
```
Hasil FAR ditambahkan ke `/opt/unsw/results/far_log.jsonl` (+ auto-upload S3).

---

## 3A. RAMP BERTAHAP S0 -> D1(1j) -> D2(6j) -> D3(24j) -> [D4(3h) -> D5(7h)] — WAJIB berurutan

> **Alasan:** langsung 24 jam berisiko — bila ada error di tengah (mismatch satuan
> fitur, capture 0 flow, gagal rotasi/upload) biaya jam-jaman terbuang. Ramp menaikkan
> durasi bertahap; tiap tahap punya **GATE terukur**. Bila gate GAGAL -> **STOP**, jangan
> naik tahap; diagnosa & perbaiki dulu, lalu ulang tahap dari awal.
> Kaitan spec: `.kiro/specs/t10-ramp-execution/requirements.md`.
>
> **Peta tahap & tujuan ganda (gate + titik perbandingan FAR):**
>
> | Tahap | Durasi | Peran | Dilaporkan di paper? |
> |---|---|---|---|
> | **S0** | ~3 menit | smoke test: gate pipeline (flow>0, no error, satuan `duration` detik) | tidak (internal) |
> | **D1** | 1 jam | FAR titik-1 + gate satuan/scaler (\|z\|<=6, FAR!=1) | ya (baris tabel) |
> | **D2** | 6 jam | FAR lintas beberapa jam (variasi intra-hari) | ya (baris tabel) |
> | **D3** | 24 jam | FAR satu siklus harian penuh (siang/malam) | ya (baris tabel) |
> | **D4** | 3 hari | eskalasi: variasi weekday | ya (opsional) |
> | **D5** | 7 hari | eskalasi: variasi weekday/weekend | ya (opsional) |
>
> Setiap D1-D5 mengisi satu baris **Tabel Perbandingan FAR Antar-Durasi (§7.2)**.

### Prasyarat ramp (sebelum S0)
- **Satuan `duration` sudah diselaraskan** di `unsw_extract_infer.py`: fitur `duration`
  dihitung **MIKRODETIK** (`dur_feat_us = dur_ms*1000`). Alasan (hasil audit 9 fitur):
  scaler deployment di-fit pada **CIC `Flow Duration` (mikrodetik)**, jadi extractor wajib
  menghasilkan mikrodetik agar z-score cocok (bila detik -> mismatch 1e6x, gate D1-b gagal).
  Pembagi laju **tetap detik** (`dur_s = dur_ms/1000`) karena `src_load` (CIC `Flow Byts/s`,
  byte/**detik**) & `dst_load` (CIC `Bwd Pkts/s`, paket/**detik**) memang per-detik — sudah
  benar & tak diubah. Fitur duration dan pembagi laju sengaja beda satuan.
- **Upload ulang skrip terbaru ke S3 + verifikasi Analyzer mengunduhnya:**
  ```bash
  # dari mesin kerja (yang memegang skrip terbaru)
  aws s3 cp unsw_extract_infer.py \
    s3://ssh-detection-features-232032302717/unsw-far/scripts/unsw_extract_infer.py --region ap-southeast-1
  # di ANALYZER (via SSM), tarik ulang lalu cek baris fix ada
  aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/scripts/ /opt/unsw/scripts/ --recursive
  grep -n "dur_feat_us" /opt/unsw/scripts/unsw_extract_infer.py   # harus muncul
  ```
- **Attacker di-stop** selama seluruh Fase 1 (tak dipakai untuk FAR) — hemat biaya:
  ```bash
  aws ec2 stop-instances --region ap-southeast-1 --instance-ids <AttackerId>
  ```
- **Trafik benign harus aktif** selama tiap tahap agar ada banyak flow. FAR dari ribuan
  flow jauh lebih kredibel daripada dari puluhan. Gunakan skrip pembangkit benign siap-pakai
  di **Target** (jalankan di background sebelum/berbarengan capture, hentikan saat tahap selesai):
  ```bash
  cd /opt/unsw/scripts
  # TARGET_IP=127.0.0.1 (loopback) atau IP privat Target agar lewat ens5
  nohup sudo TARGET_IP=127.0.0.1 ./benign_traffic.sh > /opt/unsw/benign.log 2>&1 &
  # ... jalankan capture tahap (S0/D1/D2/D3) ...
  sudo pkill -f benign_traffic.sh   # stop setelah capture tahap selesai
  ```
  Skrip menghasilkan flow beragam (HTTP lokal + publik via NAT, DNS, unduhan kecil). Sesi
  SSH sah OFF secara default (agar tak menyerupai pola gagal-login/brute-force); aktifkan
  hanya bila kredensial valid tersedia (`BENIGN_SSH=1 SSH_USER=... SSH_PASS=...`).

### Helper capture berdurasi tetap (tahap pendek S0-S3)
`capture_target.sh far` memakai rotasi per JAM (`-G 3600`) — cocok untuk S4. Untuk tahap
pendek, capture satu file berdurasi tetap di **Target+Analyzer** (mesin gabungan) dengan `timeout` (IFACE auto dari
default route, TIDAK `-i any`):
```bash
IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1); [ -z "$IFACE" ] && IFACE=ens5
echo "IFACE=$IFACE"   # catat untuk transparansi paper
sudo timeout <DETIK> tcpdump -i "$IFACE" -w /opt/unsw/captures/ramp_<TAHAP>.pcap
```
Lalu proses langsung di mesin yang sama (capture + inferensi satu host):
```bash
export S3_BUCKET=ssh-detection-features-232032302717
python3 /opt/unsw/scripts/unsw_extract_infer.py far /opt/unsw/captures/ramp_<TAHAP>.pcap
# (opsional) backup pcap ke S3
aws s3 cp /opt/unsw/captures/ramp_<TAHAP>.pcap s3://$S3_BUCKET/unsw-far/captures/ --region ap-southeast-1
```

---

### S0 — Smoke (~3 menit) | GATE saja (tidak dilaporkan) | tangkap error mendasar & bug satuan
- **Capture:** `timeout 180 tcpdump -i $IFACE ... ramp_s0.pcap` (180 detik), trafik benign aktif.
- **Proses:** `unsw_extract_infer.py far ramp_s0.pcap`.
- **GATE S0:**
  - **S0-a** NFStream menghasilkan **>0 flow** (jika 0 -> hampir pasti `-i any`/SLL, atau IFACE salah).
  - **S0-b** pipeline extract+infer selesai **tanpa error** (`far_log.jsonl` bertambah 1 baris).
  - **S0-c** **sanity `duration` (MIKRODETIK):** fitur `duration` (di `ramp_s0_flows.csv`) harus berskala **mikrodetik** — flow beberapa detik ~ orde `1e6`-`1e7` us (mis. 10 s = 1e7). BUKAN nilai kecil <~1000 (tanda masih detik/ms; scaler CIC mengharapkan us). Bandingkan juga dengan `scaler_mean[duration]` (~1,2e7) di `deploy_meta_9feat.json` — orde harus sebanding.
- **Cek cepat S0-c (Analyzer):**
  ```bash
  python3 - <<'PY'
  import pandas as pd, json
  d = pd.read_csv('/opt/unsw/results/ramp_s0_flows.csv')
  meta = json.load(open('/opt/unsw/models/deploy_meta_9feat.json'))
  print('n_flow=', len(d))
  print(d['duration'].describe())          # orde 1e6-1e7 us untuk flow beberapa detik
  print('scaler_mean[duration]=', meta['scaler_mean'][0])  # ~1.2e7 (referensi orde)
  PY
  ```
- **STOP bila:** flow=0, ada error, atau `duration` berorde jauh dari `scaler_mean[duration]` (mis. masih detik/ms). Diagnosa (IFACE? skrip versi lama yang masih pakai `dur_ms/1000` detik alih-alih `dur_feat_us`? model/meta?) lalu ulang S0.

### D1 — 1 jam | titik perbandingan FAR #1 + GATE satuan/scaler
- **Capture (1 file 1 jam):** `sudo timeout 3600 tcpdump -i "$IFACE" -w /opt/unsw/captures/far_%Y%m%d_%H.pcap` (trafik benign aktif). Proses mode `far`.
- **GATE D1 (wajib lolos sebelum naik ke D2):**
  - **D1-a** FAR **masuk akal**: `0 <= FAR < 1` dan **tidak = 1** (FAR=1 -> hampir pasti mismatch skala/scaler, bukan model buruk).
  - **D1-b** **z-of-mean tiap fitur** terhadap `scaler_mean`/`scaler_scale` training tidak ekstrem: **|z| <= ~6** untuk semua 9 fitur.
  - **D1-c** volume flow benign tercatat (jadi baris pertama tabel perbandingan §7.2).
- **Cek D1-b (Analyzer):**
  ```bash
  python3 - <<'PY'
  import json, numpy as np, pandas as pd, glob, os
  meta = json.load(open('/opt/unsw/models/deploy_meta_9feat.json'))
  mean = np.array(meta['scaler_mean']); scale = np.array(meta['scaler_scale'])
  CANON = ["duration","fwd_pkts","bwd_pkts","fwd_bytes","bwd_bytes","fwd_mean","bwd_mean","src_load","dst_load"]
  f = sorted(glob.glob('/opt/unsw/results/far_*_flows.csv'), key=os.path.getmtime)[-1]
  d = pd.read_csv(f)[CANON]
  z = (d.mean().values - mean) / scale
  for c,zz in zip(CANON, z):
      print(f'{c:10s} z_of_mean={zz:+.2f}' + ('  <-- CEK' if abs(zz)>6 else ''))
  PY
  ```
- **STOP bila:** FAR=1/absurd, atau ada fitur |z|>~6. Perbaiki satuan/scaler/mapping lalu ulang D1.
- **Catat:** FAR + n_flow D1 -> baris "1 jam" Tabel §7.2.

### D2 — 6 jam | titik perbandingan FAR #2 + rotasi/upload + stabilitas antar-jam
- **Capture rotasi per jam (6 file):**
  ```bash
  sudo timeout 21600 tcpdump -i "$IFACE" -G 3600 -w /opt/unsw/captures/far_%Y%m%d_%H.pcap
  ```
- Proses tiap file (mode `far`); (opsional) backup pcap ke S3.
- **GATE D2:**
  - **D2-a** setiap pcap rotasi **ter-upload** & **terproses** tanpa error (baris bertambah di `far_log.jsonl` per file).
  - **D2-b** FAR **stabil antar-jam** (tak ada jam yang meledak; variasi dalam batas wajar) dan **konsisten dengan D1** (selisih dalam beberapa poin persen).
  - **D2-c** total flow benign terkumpul cukup (target kerja: ribuan flow).
- **STOP bila:** ada file gagal upload/proses, FAR meloncat tak wajar, atau volume flow terlalu sedikit (naikkan intensitas trafik benign, ulang).
- **Catat:** FAR agregat 6 jam + FAR min-max per jam + n_flow -> baris "6 jam" Tabel §7.2.

### D3 — 24 jam | titik perbandingan FAR #3 (satu siklus harian) — eksekusi utama layak paper
- **Capture:** `capture_target.sh far` (rotasi per jam, `-G 3600`) selama ~24 jam, trafik benign aktif sepanjang waktu (siang & malam).
- **Proses per jam** tiap `far_YYYYMMDD_HH.pcap` (mode `far`).
- **GATE D3:**
  - **D3-a** FAR dihitung **per jam** dan **agregat 24 jam** dari `far_log.jsonl` (angka nyata).
  - **D3-b** total flow benign **besar** (layak paper).
  - **D3-c** **seluruh hasil ter-upload** ke `.../unsw-far/results/` **sebelum teardown**.
- **STOP bila D3-c:** ada hasil belum ter-upload -> tunda teardown sampai lengkap.
- **Catat:** FAR agregat 24 jam + FAR min-max per jam + n_flow -> baris "24 jam" Tabel §7.2.

### D4 / D5 — 3 hari / 7 hari | eskalasi (opsional, variasi weekday/weekend)
- Infra & prosedur **sama persis** dengan D3, hanya durasi capture diperpanjang (rotasi per jam berjalan 72 / 168 jam). Jalankan HANYA setelah D3 kredibel (atau bila diminta reviewer).
- **Kontrol biaya WAJIB:** deployment berhari-hari mahal — pantau AWS Budgets, cek EIP idle, pertimbangkan jadwal on/off malam bila trafik benign masih representatif. Rujuk `cost-estimate.md`.
- **GATE D4/D5:** FAR dihitung **per hari** (bandingkan antar-hari, cek weekday vs weekend) + agregat total; semua hasil ter-upload sebelum teardown.
- **Catat:** FAR agregat per durasi -> baris "3 hari" / "7 hari" Tabel §7.2.

> **Kontrol biaya antar tahap:** bila ada jeda panjang antar tahap, stop instance
> (§5) untuk hemat; resume saat lanjut. Teardown penuh (§6) hanya setelah tahap terakhir
> yang direncanakan selesai & semua hasil di S3. Rujuk `cost-estimate.md` untuk ambang AWS
> Budgets & cek EIP idle.

---
## 4. FASE 2 — Deteksi (DENGAN serangan, ~7 menit)

Di **Target+Analyzer** (mesin gabungan): mulai capture deteksi.
```bash
cd /opt/unsw/scripts && sudo ./capture_target.sh detect clean   # atau: evasion
```
Di **Attacker**: jalankan skenario.
```bash
cd /opt/unsw/scripts && ./attack_scenario.sh <TARGET_PRIVATE_IP> clean   # atau: evasion
```
Setelah selesai (~7 menit), hentikan capture (Ctrl-C). Proses langsung di mesin yang
sama (opsional backup pcap ke S3):
```bash
python3 /opt/unsw/scripts/unsw_extract_infer.py detect /opt/unsw/captures/detect_clean.pcap
```
Metrik → `/opt/unsw/results/detect_clean_metrics.json`. Ulangi untuk `evasion`.

---

## 5. Idle / Resume (hemat biaya tanpa hapus)

Idle (stop compute, biaya ~nol kecuali EBS kecil):
```bash
aws ec2 stop-instances --region ap-southeast-1 --instance-ids <AttackerId> <TargetAnalyzerId>
```
Resume:
```bash
aws ec2 start-instances --region ap-southeast-1 --instance-ids <AttackerId> <TargetAnalyzerId>
# tunggu SSM online ~2 menit; private IP tetap
```

---

## 6. SELESAI — Simpan hasil, HAPUS infra (biaya nol)

```bash
# 1) Pastikan semua hasil sudah di S3
aws s3 ls s3://ssh-detection-features-232032302717/unsw-far/results/
# 2) Hapus stack EC2 DULU (harus sebelum VPC karena ImportValue), lalu stack VPC
aws cloudformation delete-stack --stack-name unsw-far-ec2 --region ap-southeast-1
aws cloudformation wait stack-delete-complete --stack-name unsw-far-ec2 --region ap-southeast-1
aws cloudformation delete-stack --stack-name unsw-far-vpc --region ap-southeast-1
aws cloudformation wait stack-delete-complete --stack-name unsw-far-vpc --region ap-southeast-1
# 3) Verifikasi tak ada EIP nyangkut
aws ec2 describe-addresses --region ap-southeast-1
```

---

## 7. Slot Hasil Nyata (diisi setelah eksekusi — JANGAN dikarang)

### 7.1 Profil efisiensi (Tabel §3.4 naskah)
| Metrik | Nilai |
|---|---|
| Ukuran model biner (Model A, 9 fitur) | _(diisi)_ KB |
| Latensi inferensi per flow @1 vCPU | _(diisi)_ µs |
| Throughput | _(diisi)_ flow/detik |

### 7.2 FAR (Fase 1, §12 naskah) — PERBANDINGAN ANTAR-DURASI (percobaan bertahap)

**Tabel utama — FAR per durasi observasi** (satu baris per tahap D1-D5; isi angka nyata):
| Durasi | Total n_flow benign | Total false_alarm | FAR agregat | FAR per-jam min-max |
|---|---|---|---|---|
| 1 jam (D1)  | | | | |
| 6 jam (D2)  | | | | |
| 24 jam (D3) | | | | |
| 3 hari (D4) *(opsional)* | | | | |
| 7 hari (D5) *(opsional)* | | | | |

**Tabel rinci per jam (D3, satu siklus harian)** — untuk melihat pola siang/malam:
| Jam ke- | n_flow | false_alarm | FAR |
|---|---|---|---|
| _(diisi per jam dari far_log.jsonl)_ | | | |
| **Agregat 24 jam** | | | |

Catatan jujur: laporkan durasi apa adanya per tahap. **Interpretasi yang diharapkan:** FAR
agregat **stabil/rendah dan konsisten** lintas durasi (1j -> 6j -> 24j -> ...) membuktikan
FAR bukan artefak snapshot pendek. Bila ada durasi dengan FAR menyimpang, laporkan & analisis
(mis. lonjakan trafik anomali benign, bukan disembunyikan).

### 7.3 Deteksi (Fase 2)
| Varian | MCC | F1 | Precision | Recall |
|---|---|---|---|---|
| clean | | | | |
| evasion | | | | |

### 7.4 Catatan lingkungan (transparansi)
- Interface capture (mesin Target+Analyzer): _(ens5?)_  | Instance types: _(t3.medium?)_
- Temuan feature-mismatch (z-of-mean real vs train), bila ada: _(catat)_.

---

## 8. Referensi ID (diisi saat deploy, agar resume cepat)
- Stack VPC: `unsw-far-vpc` | Stack EC2: `unsw-far-ec2` | VPC: _(id)_ | Bucket: _(nama)_
- Attacker: _(id / privIP 10.5.2.x)_ | Target+Analyzer: _(id / privIP 10.5.2.x)_  (keduanya PRIVATE)
- S3 layout: `models/`, `scripts/`, `captures/`, `results/` di prefix `unsw-far/`.

---

## 9. STATUS SESI TERAKHIR (catatan resume — diperbarui manual)

> Ringkasan posisi terakhir agar sesi berikutnya langsung paham tanpa mengandalkan
> ingatan chat. Perbarui bagian ini setiap akhir sesi kerja AWS.

### Tanggal: 2026-09-08 (teardown penuh)

**Kondisi AWS:** SEMUA stack CloudFormation sudah dihapus (`ACTIVE_STACKS=0` di
region ap-southeast-1). Tidak ada biaya EC2/NAT berjalan. Stack yang pernah dibuat &
sudah dihapus di sesi ini: `unsw-far-vpc`, `unsw-far-ec2`, `rw-backup-*`, `ransomware-*`,
`security-lab-*`, `nids01-*`.

**Belum diperiksa (TODO sesi berikutnya):** Elastic IP idle & EBS volume `available`
yang mungkin nyangkut (biaya kecil) — cek via Console: EC2 -> Elastic IPs & Volumes.

**Progres T10 (deploy pernah BERHASIL lalu di-teardown):**
- Model + meta + 4 skrip sudah ada di S3 (`s3://ssh-detection-features-232032302717/unsw-far/`).
  Model & meta dari notebook 09; skrip dari `upload_to_s3.sh`. TIDAK perlu upload ulang.
- Template `unsw-vpc.yaml` + `unsw-2ec2.yaml` sudah DIPERBAIKI & tervalidasi:
  1. BOM UTF-8 dihapus (dulu bikin error `[???AWSTemplateFormatVersion]`).
  2. Deskripsi SG rule: karakter `->` diganti `ke` (AWS tolak `>` di description).
  Deploy ulang berikutnya harusnya mulus. **Belum di-commit ke Git** (per 2026-09-08).
- Fix satuan `duration` di `unsw_extract_infer.py` sudah benar: `dur_feat_us = dur_ms*1000`
  (mikrodetik, samakan scaler CIC yang `scaler_mean[duration]`~1.2e7). Pembagi laju tetap
  detik (`dur_s`). Gate `dur_feat_us` dipakai di `upload_to_s3.sh` & S0-c.

**BUG yang HARUS diperbaiki saat deploy ulang (belum difix):** saat download skrip/model
ke Target via `ssm send-command`, JANGAN pakai variabel `$S3_BUCKET` di dalam array
`commands` (tidak ter-expand -> folder kosong, `s3 cp` diam-diam gagal). Pakai path S3
**LITERAL**:
```bash
aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/scripts/ /opt/unsw/scripts/ --recursive
aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/models/  /opt/unsw/models/  --recursive
```

**Langkah lanjut T10 (saat mau eksekusi lagi):**
1. Deploy `unsw-vpc.yaml` -> tunggu CREATE_COMPLETE -> deploy `unsw-2ec2.yaml`.
2. Ambil Outputs (instance id + private IP target).
3. Via SSM: download skrip+model (path LITERAL) ke Target; `grep dur_feat_us` harus muncul.
4. S0 smoke (~3 menit): cek `duration` orde ~1e6-1e7 us (sanity S0-c).
5. Lolos -> D1 (1 jam) -> gate |z|<=6 & FAR!=1 -> D2 (6j) -> D3 (24j) -> [D4 3h / D5 7h].
6. Isi hasil ke Tabel §7.2 (perbandingan FAR antar-durasi) lalu ke Tabel FAR naskah.

**Catatan lingkungan kerja:** terminal PowerShell di mesin lokal sering menelan stdout
perintah panjang (kosmetik). Trik andal: tulis output ke file lalu baca file, atau pakai
perintah pendek `describe-stacks ... --output text`. AWS CLI di lokal pakai user IAM `hero`
(akun 232032302717) — punya izin CloudFormation/EC2/SSM. Terminal SageMaker TIDAK punya
izin itu (execution role hanya S3/SageMaker) -> jalankan CloudFormation dari lokal.
