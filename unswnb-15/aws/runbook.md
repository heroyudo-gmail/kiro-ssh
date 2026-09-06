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

> EC2 tidak perlu SageMaker: cukup `aws s3 cp` dari bucket di atas (langkah §2).

---

## 2. Deploy infra

```bash
aws cloudformation create-stack --stack-name unsw-far \
  --template-body file://unsw-vpc-3ec2.yaml \
  --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1

aws cloudformation wait stack-create-complete --stack-name unsw-far --region ap-southeast-1
aws cloudformation describe-stacks --stack-name unsw-far --region ap-southeast-1 \
  --query "Stacks[0].Outputs" --output table
```
Catat Output: `AttackerId, TargetId, AnalyzerId, TargetPrivateIp, AnalyzerPrivateIp`.

Verifikasi SSM online (~2 menit):
```bash
aws ssm describe-instance-information --region ap-southeast-1 \
  --query "InstanceInformationList[].{Id:InstanceId,Ping:PingStatus}" --output table
```

Unduh skrip+model di Target & Analyzer (via SSM shell):
```bash
export S3_BUCKET=ssh-detection-features-232032302717
aws s3 cp s3://$S3_BUCKET/unsw-far/scripts/ /opt/unsw/scripts/ --recursive
aws s3 cp s3://$S3_BUCKET/unsw-far/models/  /opt/unsw/models/  --recursive   # hanya Analyzer
chmod +x /opt/unsw/scripts/*.sh
```

---

## 3. FASE 1 — FAR (TANPA serangan)

> **Skenario utama (percobaan awal): 24 jam kontinu** — mencakup satu siklus harian
> penuh (siang/malam). Cukup kredibel sebagai validasi awal FAR. **Eskalasi 3–7 hari**
> (variasi weekday/weekend) dilakukan HANYA bila diminta reviewer — infra sama, tinggal
> jalankan lebih lama.
>
> **Penting agar FAR berisi:** jaga trafik normal tetap aktif (banyak flow benign) selama
> 24 jam — curl loop + unduhan berkala + sesi SSH terjadwal. FAR dari puluhan ribu flow
> jauh lebih kuat daripada dari puluhan flow.

Di **Target** (biarkan berjalan ~24 jam):
```bash
cd /opt/unsw/scripts && sudo S3_BUCKET=ssh-detection-features-232032302717 ./capture_target.sh far
```
Bangkitkan trafik NORMAL (cron/loop di Target atau dari Attacker): `curl` berkala,
`dnf update`, unduhan, sesi SSH sah. TIDAK ADA serangan pada fase ini.

Per jam / berkala, di **Analyzer** (proses pcap yang sudah dirotasi):
```bash
# pcap dari Target -> S3 -> Analyzer download -> proses
aws s3 cp /opt/unsw/captures/ s3://ssh-detection-features-232032302717/unsw-far/captures/ --recursive   # di Target
aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/captures/ /opt/unsw/captures/ --recursive   # di Analyzer
export S3_BUCKET=ssh-detection-features-232032302717
python3 /opt/unsw/scripts/unsw_extract_infer.py far /opt/unsw/captures/far_YYYYMMDD_HH.pcap
```
Hasil FAR ditambahkan ke `/opt/unsw/results/far_log.jsonl` (+ auto-upload S3).

---

## 4. FASE 2 — Deteksi (DENGAN serangan, ~7 menit)

Di **Target**: mulai capture deteksi.
```bash
cd /opt/unsw/scripts && sudo ./capture_target.sh detect clean   # atau: evasion
```
Di **Attacker**: jalankan skenario.
```bash
cd /opt/unsw/scripts && ./attack_scenario.sh <TARGET_PRIVATE_IP> clean   # atau: evasion
```
Setelah selesai (~7 menit), hentikan capture di Target (Ctrl-C), upload pcap ke S3,
lalu di **Analyzer**:
```bash
python3 /opt/unsw/scripts/unsw_extract_infer.py detect /opt/unsw/captures/detect_clean.pcap
```
Metrik → `/opt/unsw/results/detect_clean_metrics.json`. Ulangi untuk `evasion`.

---

## 5. Idle / Resume (hemat biaya tanpa hapus)

Idle (stop compute, biaya ~nol kecuali EBS kecil):
```bash
aws ec2 stop-instances --region ap-southeast-1 --instance-ids <Attacker> <Target> <Analyzer>
# (opsional) hapus NAT bila jeda lama — lihat NIDS-01; buat ulang saat resume
```
Resume:
```bash
aws ec2 start-instances --region ap-southeast-1 --instance-ids <Attacker> <Target> <Analyzer>
# tunggu SSM online ~2 menit; private IP tetap, public IP Attacker berubah (tak masalah)
```

---

## 6. SELESAI — Simpan hasil, HAPUS infra (biaya nol)

```bash
# 1) Pastikan semua hasil sudah di S3
aws s3 ls s3://ssh-detection-features-232032302717/unsw-far/results/
# 2) Hapus stack (EC2 + EBS + VPC + IGW + NAT + EIP semua terhapus)
aws cloudformation delete-stack --stack-name unsw-far --region ap-southeast-1
aws cloudformation wait stack-delete-complete --stack-name unsw-far --region ap-southeast-1
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
- Interface capture: _(ens5?)_  | Instance types: _(t3.medium?)_
- Temuan feature-mismatch (z-of-mean real vs train), bila ada: _(catat)_.

---

## 8. Referensi ID (diisi saat deploy, agar resume cepat)
- Stack: `unsw-far` | VPC: _(id)_ | Bucket: _(nama)_
- Attacker: _(id / privIP 10.5.1.x)_ | Target: _(id / privIP 10.5.2.x)_ | Analyzer: _(id / privIP 10.5.2.x)_
- S3 layout: `models/`, `scripts/`, `captures/`, `results/` di prefix `unsw-far/`.
