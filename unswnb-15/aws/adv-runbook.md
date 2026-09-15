# Runbook Paper 2 — Adversarial Real-Traffic di AWS (2-EC2)

> Kelanjutan Paper 1. Menguji **ketahanan adversarial** 4 model Paper 2
> (baseline/fewshot/adv/fewshot_adv) pada **trafik AWS nyata**, dengan evasion
> network-level (varian `evasion`) + FGSM functional-preserving pada fitur.
> **Region:** ap-southeast-1. Semua hasil diunggah ke S3 sebelum infra dihapus.

---

## 0. Arsitektur

- **VPC** `10.6.0.0/16` (beda dari Paper 1 `10.5.0.0/16` agar bisa jalan berdampingan).
- **Attacker** (private): jalankan `adv-attack-scenario.sh` (clean & evasion).
- **Target+Analyzer** (private, gabungan): layanan SSH/HTTP + **capture** (tcpdump -i ens5,
  BUKAN -i any) + NFStream 9 fitur + **inferensi 4 model** via `adv-extract-infer.py`.
- Akses via **SSM Session Manager** (bukan SSH publik). Internet via NAT.
- IaC: `adv-vpc.yaml` + `adv-2ec2.yaml`. ProjectName = `adv-far`.

---

## 1. Prasyarat (sekali)

**Bucket S3:** `ssh-detection-features-232032302717`.

- **4 model Paper 2 + scaler** (dari notebook `11_adv_fewshot_pipeline.ipynb`): notebook itu
  menyimpan ke `paper2_models/<ARAH>/` dan mengunggah ke
  `s3://.../unsw-far/paper2/`. Struktur per arah (mis. `CIC_to_UNSW/`):
  `baseline.json, fewshot.json, adv.json, fewshot_adv.json, scaler.pkl`.
- **Skrip → S3:** `adv-attack-scenario.sh`, `adv-capture.sh`, `adv-extract-infer.py`
  → `s3://.../unsw-far/scripts-p2/`.

---

## 2. Deploy infra (DUA stack: VPC lalu EC2)

**2.1 Stack VPC:**
```bash
aws cloudformation create-stack --stack-name adv-far-vpc \
  --template-body file://adv-vpc.yaml \
  --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation wait stack-create-complete --stack-name adv-far-vpc --region ap-southeast-1
```

**2.2 Stack EC2** (ProjectName harus `adv-far`, sama dengan VPC):
```bash
aws cloudformation create-stack --stack-name adv-far-ec2 \
  --template-body file://adv-2ec2.yaml \
  --parameters ParameterKey=ProjectName,ParameterValue=adv-far \
  --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1
aws cloudformation wait stack-create-complete --stack-name adv-far-ec2 --region ap-southeast-1
```

**2.3 Ambil ID & IP:**
```bash
aws cloudformation describe-stacks --stack-name adv-far-ec2 --region ap-southeast-1 \
  --query "Stacks[0].Outputs" --output table
```

---

## 3. Siapkan node (via SSM)

**Target+Analyzer** — unduh model + skrip:
```bash
# di sesi SSM target-analyzer
export S3_BUCKET=ssh-detection-features-232032302717
mkdir -p /opt/adv/{models,captures,results,scripts}
aws s3 cp s3://$S3_BUCKET/unsw-far/paper2/ /opt/adv/models/ --recursive
aws s3 cp s3://$S3_BUCKET/unsw-far/scripts-p2/ /opt/adv/scripts/ --recursive
chmod +x /opt/adv/scripts/*.sh
# cek: harus ada /opt/adv/models/CIC_to_UNSW/{baseline,fewshot,adv,fewshot_adv}.json + scaler.pkl
```

**Attacker** — unduh skrip serangan:
```bash
aws s3 cp s3://$S3_BUCKET/unsw-far/scripts-p2/adv-attack-scenario.sh /opt/adv/ 
chmod +x /opt/adv/adv-attack-scenario.sh
```

---

## 4. Jalankan percobaan (dua pcap: clean & evasion)

Untuk tiap varian, urutannya: mulai capture di Target → jalankan serangan di
Attacker → stop capture → infer.

**4.1 Mulai capture (Target+Analyzer):**
```bash
IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)   # biasanya ens5
sudo tcpdump -i "$IFACE" -w /opt/adv/captures/detect_clean.pcap &      # ganti ke detect_evasion.pcap utk varian evasion
echo $! > /tmp/tcpdump.pid
```

**4.2 Jalankan serangan (Attacker):** (TARGET_IP = PrivateIp target-analyzer)
```bash
# varian CLEAN
/opt/adv/adv-attack-scenario.sh <TARGET_IP> clean
# --- atau --- varian EVASION (network-level: TCP window + jitter + rate rendah)
/opt/adv/adv-attack-scenario.sh <TARGET_IP> evasion
```

**4.3 Stop capture (Target+Analyzer):**
```bash
sudo kill "$(cat /tmp/tcpdump.pid)"; sleep 2
ls -lh /opt/adv/captures/
```

**4.4 Inferensi + evaluasi adversarial (Target+Analyzer):**
```bash
export S3_BUCKET=ssh-detection-features-232032302717
python3 /opt/adv/scripts/adv-extract-infer.py /opt/adv/captures/detect_clean.pcap    CIC_to_UNSW
python3 /opt/adv/scripts/adv-extract-infer.py /opt/adv/captures/detect_evasion.pcap  CIC_to_UNSW
# hasil: /opt/adv/results/*_advmetrics.json + .csv  -> auto-upload s3://.../unsw-far/paper2_aws/
```

Keluaran per model (baseline/fewshot/adv/fewshot_adv): `clean_mcc`, `clean_recall`,
`clean_precision`, dan `fgsm_functional_mcc_eps{0.05,0.1,0.2}`. Bandingkan:
- **clean pada pcap clean vs evasion** → efek evasion network-level nyata.
- **clean vs fgsm_functional** → efek evasion feature-space (adaptive) di trafik nyata.
- **antar-model** → apakah `fewshot_adv` paling tahan di trafik AWS nyata.

---

## 5. Unduh hasil + hapus infra

```bash
# unduh hasil ke lokal (opsional; sudah auto-upload)
aws s3 cp s3://ssh-detection-features-232032302717/unsw-far/paper2_aws/ ./paper2_aws/ --recursive

# HAPUS infra (urutan: EC2 dulu, lalu VPC)
aws cloudformation delete-stack --stack-name adv-far-ec2 --region ap-southeast-1
aws cloudformation wait stack-delete-complete --stack-name adv-far-ec2 --region ap-southeast-1
aws cloudformation delete-stack --stack-name adv-far-vpc --region ap-southeast-1
aws cloudformation wait stack-delete-complete --stack-name adv-far-vpc --region ap-southeast-1
```

---

## 6. Catatan penting

- **`-i any` DILARANG** saat tcpdump (menghasilkan 0 flow di NFStream). Pakai iface spesifik (ens5).
- **Ground-truth timeline** (menit): `0-1 benign | 1-3 attack | 3-5 attack | 5-6 attack | 6-7 benign`
  — cocok dengan `GT` di `adv-extract-infer.py`. Jangan ubah durasi fase tanpa mengubah GT.
- **ARAH model**: default `CIC_to_UNSW` (scaler di-fit pada CIC). Bila ingin arah lain, pastikan
  folder model + scaler untuk arah itu tersedia di `/opt/adv/models/<ARAH>/`.
- **Kejujuran**: laporkan MCC apa adanya. Bila model runtuh di trafik AWS (spt temuan Paper 1
  zero-shot), itu temuan valid — bukan kegagalan eksperimen.
- **Biaya**: dua t3.medium + NAT. Hapus infra segera setelah hasil ter-upload.
