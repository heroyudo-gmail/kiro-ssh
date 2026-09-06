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
- **Skrip → S3:** `unsw_extract_infer.py`, `capture_target.sh`, `attack_scenario.sh` →
  `s3://ssh-detection-features-232032302717/unsw-far/scripts/`.
  > **Pastikan `unsw_extract_infer.py` sudah versi ter-FIX** (fitur `duration` dalam
  > DETIK, `dur_feat_s = dur_ms/1000`). Cek: `grep dur_feat_s unsw_extract_infer.py`
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

> **JANGAN langsung 24 jam.** Jalankan **RAMP BERTAHAP S0-S4 (Bagian 3A)** dulu:
> smoke ~3m -> 10m -> 30m -> 2j -> 24j, tiap tahap lolos GATE. Bagian di bawah ini
> (24 jam kontinu) adalah tahap **S4** — dijalankan HANYA setelah S0-S3 lolos.
>
> **Skenario utama (percobaan awal): 24 jam kontinu** — mencakup satu siklus harian
> penuh (siang/malam). Cukup kredibel sebagai validasi awal FAR. **Eskalasi 3–7 hari**
> (variasi weekday/weekend) dilakukan HANYA bila diminta reviewer — infra sama, tinggal
> jalankan lebih lama.
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

## 3A. RAMP BERTAHAP S0-S4 (validasi sebelum 24 jam) — WAJIB dijalankan berurutan

> **Alasan:** langsung 24 jam berisiko — bila ada error di tengah (mismatch satuan
> fitur, capture 0 flow, gagal rotasi/upload) biaya jam-jaman terbuang. Ramp menaikkan
> durasi bertahap; tiap tahap punya **GATE terukur**. Bila gate GAGAL -> **STOP**, jangan
> naik tahap; diagnosa & perbaiki dulu, lalu ulang tahap dari awal.
> Kaitan spec: `.kiro/specs/t10-ramp-execution/requirements.md`.

### Prasyarat ramp (sebelum S0)
- **Bug `duration` sudah diperbaiki** di `unsw_extract_infer.py`: fitur `duration` kini
  dihitung DETIK (`dur_feat_s = dur_ms/1000`), bukan milidetik. (Training Model A memakai
  detik: UNSW `dur` = CIC `Flow Duration`.) `src_load` (byte/s) & `dst_load` (paket/s)
  tidak diubah — sudah benar.
- **Upload ulang skrip terbaru ke S3 + verifikasi Analyzer mengunduhnya:**
  ```bash
  # dari mesin kerja (yang memegang skrip terbaru)
  aws s3 cp unsw_extract_infer.py \
    s3://ssh-detection-features-232032302717/unsw-far/scripts/unsw_extract_infer.py --region ap-southeast-1
  # di ANALYZER (via SSM), tarik ulang lalu cek baris fix ada
  aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/scripts/ /opt/unsw/scripts/ --recursive
  grep -n "dur_feat_s" /opt/unsw/scripts/unsw_extract_infer.py   # harus muncul
  ```
- **Attacker di-stop** selama seluruh Fase 1 (tak dipakai untuk FAR) — hemat biaya:
  ```bash
  aws ec2 stop-instances --region ap-southeast-1 --instance-ids <AttackerId>
  ```
- **Trafik benign harus aktif** selama tiap tahap (curl loop / unduhan / SSH sah) agar
  ada banyak flow. FAR dari ribuan flow jauh lebih kredibel daripada dari puluhan.

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

### S0 — Smoke (~2-3 menit) | tangkap error mendasar & bug satuan
- **Capture:** `timeout 150 tcpdump -i $IFACE ... ramp_s0.pcap` (150 detik), trafik benign aktif.
- **Proses:** `unsw_extract_infer.py far ramp_s0.pcap`.
- **GATE S0:**
  - **S0-a** NFStream menghasilkan **>0 flow** (jika 0 -> hampir pasti `-i any`/SLL, atau IFACE salah).
  - **S0-b** pipeline extract+infer selesai **tanpa error** (tidak ada exception, `far_log.jsonl` bertambah 1 baris).
  - **S0-c** **sanity `duration`:** nilai fitur `duration` (di `ramp_s0_flows.csv`) berada di rentang **detik** masuk akal (mis. mayoritas < ~300 s), BUKAN skala ribuan/puluhan-ribu (tanda bug ms belum keangkut).
- **Cek cepat S0-c (Analyzer):**
  ```bash
  python3 - <<'PY'
  import pandas as pd
  d = pd.read_csv('/opt/unsw/results/ramp_s0_flows.csv')
  print('n_flow=', len(d))
  print(d['duration'].describe())   # max wajar dalam detik, bukan 1e4-1e5
  PY
  ```
- **STOP bila:** flow=0, ada error, atau `duration` berskala ms. Diagnosa (IFACE? skrip lama? model/meta?) lalu ulang S0.

### S1 — 10 menit | FAR masuk akal + cek satuan semua fitur
- **Capture:** `timeout 600 tcpdump -i $IFACE ... ramp_s1.pcap`. Proses mode `far`.
- **GATE S1:**
  - **S1-a** FAR **masuk akal**: `0 <= FAR < 1` dan **tidak = 1** (FAR=1 berarti semua flow dialarm -> hampir pasti mismatch skala/scaler, bukan model buruk).
  - **S1-b** **z-of-mean tiap fitur** terhadap `scaler_mean`/`scaler_scale` training tidak ekstrem. Ambang kerja: **|z| <= ~6** untuk semua 9 fitur. Fitur dengan |z| besar menandai mismatch satuan/scaler.
- **Cek S1-b (Analyzer):**
  ```bash
  python3 - <<'PY'
  import json, numpy as np, pandas as pd
  meta = json.load(open('/opt/unsw/models/deploy_meta_9feat.json'))
  mean = np.array(meta['scaler_mean']); scale = np.array(meta['scaler_scale'])
  CANON = ["duration","fwd_pkts","bwd_pkts","fwd_bytes","bwd_bytes","fwd_mean","bwd_mean","src_load","dst_load"]
  d = pd.read_csv('/opt/unsw/results/ramp_s1_flows.csv')[CANON]
  z = (d.mean().values - mean) / scale
  for f,zz in zip(CANON, z):
      flag = '  <-- CEK' if abs(zz) > 6 else ''
      print(f'{f:10s} z_of_mean={zz:+.2f}{flag}')
  PY
  ```
- **STOP bila:** FAR=1 / absurd, atau ada fitur |z|>~6. Perbaiki satuan/scaler/mapping lalu ulang S1.

### S2 — 30 menit | rotasi pcap + jalur S3 (upload+download) + konsistensi FAR
- **Capture rotasi:** di Target jalankan capture dengan rotasi interval pendek (mis. 10 menit -> 3 file) untuk MENGUJI mekanisme rotasi & upload:
  ```bash
  sudo timeout 1800 tcpdump -i "$IFACE" -G 600 -w /opt/unsw/captures/ramp_s2_%H%M.pcap
  ```
- **Proses tiap file rotasi langsung di mesin gabungan**; (opsional) backup pcap ke S3 (lihat helper di atas).
- **GATE S2:**
  - **S2-a** setiap pcap rotasi **berhasil ter-upload** ke `.../unsw-far/captures/` (cek `aws s3 ls`).
  - **S2-b** mesin gabungan **memproses** tiap file rotasi tanpa error (baris bertambah di `far_log.jsonl` per file).
  - **S2-c** FAR **konsisten** dengan S1 (selisih dalam toleransi kerja, mis. dalam beberapa poin persen; jika melonjak jauh, selidiki segmen).
- **STOP bila:** ada file gagal upload/download/proses, atau FAR meloncat tak wajar.

### S3 — 2 jam | stabilitas FAR antar-segmen + volume flow cukup
- **Capture rotasi per jam** (2 file) seperti mode `far`:
  ```bash
  sudo timeout 7200 tcpdump -i "$IFACE" -G 3600 -w /opt/unsw/captures/far_%Y%m%d_%H.pcap
  ```
- Proses tiap file (mode `far`).
- **GATE S3:**
  - **S3-a** FAR **stabil antar-segmen** (tiap jam/segmen tidak ada yang meledak; variasi dalam batas wajar).
  - **S3-b** total **flow benign cukup banyak** untuk FAR kredibel (target kerja: minimal ribuan flow terkumpul; catat angka nyatanya).
- **STOP bila:** ada segmen dengan FAR meledak, atau volume flow terlalu sedikit (naikkan intensitas trafik benign, ulang).

### S4 — 24 jam | eksekusi final layak paper
- **Capture:** `capture_target.sh far` (rotasi per jam, `-G 3600`) selama ~24 jam, trafik benign aktif sepanjang waktu.
- **Proses per jam** (atau berkala) tiap `far_YYYYMMDD_HH.pcap` (mode `far`).
- **GATE S4:**
  - **S4-a** FAR dihitung **per jam** dan **agregat 24 jam** dari `far_log.jsonl` (angka nyata).
  - **S4-b** total flow benign **besar** (layak paper).
  - **S4-c** **seluruh hasil ter-upload** ke `.../unsw-far/results/` **sebelum teardown**.
- **STOP bila S4-c:** ada hasil belum ter-upload -> tunda teardown sampai lengkap.
- Isi angka nyata ke **§7.2** runbook ini, lalu ke tabel FAR (§12) naskah. **JANGAN dikarang.**

> **Kontrol biaya antar tahap:** bila ada jeda panjang antar tahap, stop instance
> (§5) untuk hemat; resume saat lanjut. Teardown penuh (§6) hanya setelah S4 selesai
> & semua hasil di S3. Rujuk `cost-estimate.md` untuk ambang AWS Budgets & cek EIP idle.

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

### 7.2 FAR (Fase 1, §12 naskah) — percobaan awal 24 jam
| Jam ke- | n_flow | false_alarm | FAR |
|---|---|---|---|
| _(diisi per jam dari far_log.jsonl)_ | | | |
| **Total/Rata-rata 24 jam** | | | |
Durasi observasi: **24 jam kontinu** (percobaan awal) — catat jujur. Eskalasi multi-hari
bila diminta reviewer.

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
