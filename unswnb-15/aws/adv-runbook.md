# Runbook Paper 2 — Adversarial Real-Traffic di AWS (2-EC2)

> Kelanjutan Paper 1. Menguji **ketahanan adversarial** 4 model Paper 2
> (baseline/fewshot/adv/fewshot_adv) pada **trafik AWS nyata**, dengan evasion
> network-level (varian `evasion`) + FGSM functional-preserving pada fitur.
> **Region:** ap-southeast-1. Semua hasil diunggah ke S3 sebelum infra dihapus.

---

## PELAJARAN dari eksekusi pertama (WAJIB dibaca — pakai pola Paper 1, jangan coba yang baru)

Eksekusi pertama sempat gagal karena mengabaikan pengalaman Paper 1. Berikut akar
masalah + solusi yang SUDAH TERBUKTI. Ikuti ini agar tidak terulang.

1. **AWS CLI di instance RUSAK setelah `pip install`.** UserData menjalankan
   `pip install nfstream xgboost ... numpy pandas`, yang meng-upgrade paket sistem dan
   membuat awscli bawaan AL2023 error (`ModuleNotFoundError: No module named 'dateutil'`).
   Akibatnya `aws s3 cp` GAGAL total.
   - **Solusi (dipakai):** JANGAN pakai `aws s3 cp` di instance. Unduh model+skrip pakai
     **boto3** langsung (Python). Boto3 tak terpengaruh kerusakan awscli. Perlu
     `python3 -m pip install boto3` dulu. (Snippet boto3 ada di Bagian 3 di bawah.)

2. **Tool serangan hydra/sshpass TIDAK ADA di AL2023.** `dnf install hydra` gagal
   (bukan di repo). Attacker AL2023 hanya punya: `nping` (nmap), `ncat` (nmap-ncat),
   `ab` (httpd-tools), `slowloris` (pip), `curl`. TIDAK ada hydra/sshpass.
   - **Solusi (dipakai):** fase SSH brute-force pakai **loop `ncat` ke port 22** sebagai
     proxy trafik (bukan hydra). Skrip serangan final yang terbukti = `atk2.sh` (lihat
     Bagian 4). Fase lain (Slowloris, SYN flood via nping, HTTP via curl) jalan normal.

3. **`tcpdump -i any` DILARANG** (0 flow di NFStream). Selalu iface spesifik: `ens5`.
   Deteksi otomatis: `IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)`.

4. **Serangan lama** (fase Slowloris menahan koneksi) bisa membuat SSM command
   `InProgress` melebihi 7 menit. Set `--timeout-seconds 900`. Stop capture boleh setelah
   serangan hampir selesai; pcap sudah berisi mayoritas trafik.

5. **Hasil eksekusi pertama (varian clean, VALID):** 4789 flow (4167 attack, 622 benign).
   MCC clean: baseline -0,02 | fewshot -0,07 | adv -0,02 | fewshot\_adv 0,00. Semua model
   runtuh zero-shot di AWS (MCC~0) — KONSISTEN temuan Paper 1 (perlu kalibrasi few-shot AWS).
   Tersimpan: `s3://.../unsw-far/paper2_aws/detect_clean_advmetrics.json`.

> **Prinsip:** pakai pola operasional Paper 1 yang sudah terbukti (boto3 untuk unduh,
> tool yang tersedia di AL2023, iface spesifik). Jangan mengulang eksperimen tool baru
> yang belum tentu ada di lingkungan.

---

## JALUR CEPAT untuk pengulangan (pakai ini besok — hemat waktu, hindari yang salah)

Eksperimen SUDAH pernah berhasil penuh (2 arah × clean+evasion × 4 model × FGSM).
Kalau infra dimatikan lalu diulang, ikuti urutan minimal berikut. Estimasi total
~20 menit (mayoritas nunggu stack + serangan 7 menit × 2).

**Urutan minimal yang TERBUKTI:**
1. Deploy 2 stack (Bagian 2). Tunggu `CREATE_COMPLETE`. Ambil `AttackerId`,
   `TargetAnalyzerId`, `TargetAnalyzerPrivateIp`.
2. Setup node via **boto3** (Bagian 3): unduh model `unsw-far/paper2/` (KEDUA arah:
   `CIC_to_UNSW` + `UNSW_to_CIC`) + skrip `unsw-far/scripts-p2/` ke Target-Analyzer;
   install tool + tulis `/tmp/atk2.sh` di Attacker.
3. Untuk tiap varian (clean, lalu evasion): mulai `tcpdump -i ens5` → jalankan
   `atk2.sh <TARGET_IP> <varian>` (SSM `--timeout-seconds 900`) → stop tcpdump.
   Hasil: `detect_clean.pcap` + `detect_evasion.pcap` di `/opt/adv/captures/`.
4. Inferensi **4 kali** (2 pcap × 2 arah), backup JSON antar-arah agar tak tertimpa:
   ```
   # arah CIC_to_UNSW (default)
   python3 adv-extract-infer.py detect_clean.pcap   CIC_to_UNSW
   python3 adv-extract-infer.py detect_evasion.pcap CIC_to_UNSW
   cp results/detect_clean_advmetrics.json   results/detect_clean_CIC_to_UNSW.json
   cp results/detect_evasion_advmetrics.json results/detect_evasion_CIC_to_UNSW.json
   # arah UNSW_to_CIC
   python3 adv-extract-infer.py detect_clean.pcap   UNSW_to_CIC
   python3 adv-extract-infer.py detect_evasion.pcap UNSW_to_CIC
   cp results/detect_clean_advmetrics.json   results/detect_clean_UNSW_to_CIC.json
   cp results/detect_evasion_advmetrics.json results/detect_evasion_UNSW_to_CIC.json
   ```
5. Baca 4 JSON via SSM `cat` (JANGAN andalkan auto-upload S3 — lihat butir "jangan
   diulang" #3). Salin angka ke `paper2-adversarial.tex` (Tabel~\ref{tab:aws} &
   `tab:aws_unsw`) + notebook `13_rangkuman_adversarial.ipynb` (sel 5b).
6. **TEARDOWN** (Bagian 5): delete-stack `adv-far-ec2` lalu `adv-far-vpc`.

**JANGAN diulang (buang waktu di eksekusi pertama):**
1. ~~`dnf install hydra` / `sshpass`~~ — tidak ada di AL2023. Langsung pakai `atk2.sh`
   (ncat/slowloris/nping/ab/curl).
2. ~~`aws s3 cp` untuk unduh model di instance~~ — awscli instance rusak pasca pip.
   Langsung boto3.
3. ~~Mengandalkan auto-upload S3 dari `adv-extract-infer.py`~~ — baris `aws s3 cp` di
   skrip GAGAL SENYAP (subprocess `capture_output=True`) karena awscli rusak; ia tetap
   mencetak "diunggah" padahal tidak. **Ambil hasil via SSM `cat` file lokal
   `/opt/adv/results/*.json`** (itu sumber kebenaran). (Opsional: perbaiki skrip agar
   upload pakai boto3.)
4. ~~`tcpdump -i any`~~ — 0 flow. Selalu `-i ens5`.
5. ~~Perintah SSM inline dengan `||`, `\"`, heredoc panjang lewat `--parameters "commands=[...]"`~~
   — parsing PowerShell rusak. **Pakai file: tulis JSON `{"commands":[...]}` lalu
   `--parameters file://path.json`** (andal).
6. ~~Baca output `aws` langsung di terminal utama~~ — sering kosong/echo berantakan
   (exit -1). **Jalankan lewat background process** lalu `get_process_output`.

**Fakta lingkungan yang sudah dipastikan (tak perlu cek ulang):**
- Model KEDUA arah ADA di S3 `unsw-far/paper2/{CIC_to_UNSW,UNSW_to_CIC}/`
  (baseline/fewshot/adv/fewshot_adv `.json` + `scaler.pkl`), verified.
- Skrip Paper 2 di S3 `unsw-far/scripts-p2/`.
- iface = `ens5`. VPC `10.6.0.0/16`. Region `ap-southeast-1`. ProjectName `adv-far`.
- Ground-truth timeline `atk2.sh`: clean=4789 flow (4167 atk/622 benign),
  evasion=3099 flow (3041 atk/58 benign).

**Hasil referensi (untuk sanity-check — kalau angka jauh beda, ada yang salah):**
- CIC→UNSW clean MCC: baseline −0,022 | fewshot −0,068 | adv −0,022 | fewshot_adv 0,000.
- UNSW→CIC clean MCC: baseline −0,401 | fewshot −0,392 | adv −0,494 | fewshot_adv −0,013
  (fewshot_adv recall 0,954 / precision 0,869 — aktif mendeteksi, MCC rendah krn imbalance).
- FGSM ε=0.1 menekan kedua arah (hingga −0,91 pada adv UNSW).

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

## 3. Siapkan node (via SSM) — PAKAI boto3, BUKAN `aws s3 cp` (lihat Pelajaran #1)

**Target+Analyzer** — unduh model + skrip via boto3 (`sudo su -` dulu):
```bash
python3 -m pip install -q boto3
mkdir -p /opt/adv/{models,scripts,captures,results}
python3 - <<'PY'
import os, boto3
b='ssh-detection-features-232032302717'; s3=boto3.client('s3', region_name='ap-southeast-1')
def dl(prefix, dest):
    os.makedirs(dest, exist_ok=True); n=0
    for page in s3.get_paginator('list_objects_v2').paginate(Bucket=b, Prefix=prefix):
        for o in page.get('Contents',[]):
            rel=o['Key'][len(prefix):]
            if not rel: continue
            lp=os.path.join(dest, rel); os.makedirs(os.path.dirname(lp), exist_ok=True)
            s3.download_file(b, o['Key'], lp); n+=1
    print('downloaded', n, 'from', prefix)
dl('unsw-far/paper2/', '/opt/adv/models/')
dl('unsw-far/scripts-p2/', '/opt/adv/scripts/')
PY
chmod +x /opt/adv/scripts/*.sh
find /opt/adv/models -type f | sort   # cek 8 model + 2 scaler + meta
```

**Attacker** — install tool AL2023 yang tersedia + tulis skrip serangan terbukti `atk2.sh`
(`sudo su -` dulu):
```bash
dnf install -y nmap nmap-ncat httpd-tools iproute-tc python3-pip
python3 -m ensurepip --upgrade 2>/dev/null || true
python3 -m pip install -q boto3 slowloris
# skrip serangan terbukti (tool AL2023: ncat/slowloris/nping/ab/curl; TANPA hydra/sshpass)
cat > /tmp/atk2.sh <<'SH'
#!/bin/bash
# Serangan Paper2 AWS. Timeline 7 menit: 0-1 benign|1-3 SSH-brute(ncat)|3-5 Slowloris|5-6 SYN|6-7 benign
# Usage: atk2.sh <TARGET_IP> [clean|evasion]
TARGET=$1; VARIANT=${2:-clean}
IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)
if [ "$VARIANT" = evasion ]; then
  sudo sysctl -w net.ipv4.tcp_window_scaling=0 >/dev/null 2>&1 || true
  sudo tc qdisc add dev "$IFACE" root netem delay 10ms 5ms distribution normal 2>/dev/null || \
  sudo tc qdisc change dev "$IFACE" root netem delay 10ms 5ms 2>/dev/null || true
  SLOW=50; SYN_RATE=100; SYN_CNT=6000
else
  SLOW=100; SYN_RATE=200; SYN_CNT=12000
fi
echo "[$(date +%T)] F0 benign 60s"; for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done
echo "[$(date +%T)] F1 SSH-brute(ncat) 120s"; timeout 120 bash -c "while true; do (echo x | ncat -w1 $TARGET 22) >/dev/null 2>&1; done" || true
echo "[$(date +%T)] F2 Slowloris 120s s=$SLOW"; timeout 120 slowloris "$TARGET" -p 80 -s $SLOW 2>&1 | tail -1 || true
echo "[$(date +%T)] F3 SYN flood 60s r=$SYN_RATE"; sudo timeout 60 nping --tcp --flags SYN --rate $SYN_RATE -p 80 -c $SYN_CNT "$TARGET" 2>&1 | tail -2 || true
echo "[$(date +%T)] F4 benign 60s"; for i in $(seq 1 60); do curl -s "http://$TARGET/" >/dev/null; sleep 1; done
if [ "$VARIANT" = evasion ]; then sudo tc qdisc del dev "$IFACE" root netem 2>/dev/null || true; sudo sysctl -w net.ipv4.tcp_window_scaling=1 >/dev/null 2>&1 || true; fi
echo "[$(date +%T)] SELESAI $VARIANT"
SH
chmod +x /tmp/atk2.sh
```

---

## 4. Jalankan percobaan (dua pcap: clean & evasion)

Untuk tiap varian, urutannya: mulai capture di Target → jalankan serangan di
Attacker → stop capture → infer.

**4.1 Mulai capture (Target+Analyzer):** iface SPESIFIK (bukan `any` — lihat Pelajaran #3).
PID file dipisah per varian agar stop capture tak salah proses.
```bash
IFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -1)   # biasanya ens5
# varian CLEAN:
sudo tcpdump -i "$IFACE" -w /opt/adv/captures/detect_clean.pcap & echo $! > /tmp/tcpdump_clean.pid
# --- atau --- varian EVASION:
sudo tcpdump -i "$IFACE" -w /opt/adv/captures/detect_evasion.pcap & echo $! > /tmp/tcpdump_ev.pid
```

**4.2 Jalankan serangan (Attacker):** pakai `atk2.sh` yang terbukti (Bagian 3), BUKAN skrip
lama. Set `--timeout-seconds 900` di SSM (Slowloris menahan koneksi >7 menit — Pelajaran #4).
TARGET_IP = PrivateIp target-analyzer.
```bash
# varian CLEAN
/tmp/atk2.sh <TARGET_IP> clean
# --- atau --- varian EVASION (network-level: TCP window scaling off + jitter netem + rate rendah)
/tmp/atk2.sh <TARGET_IP> evasion
```

**4.3 Stop capture (Target+Analyzer):**
```bash
# varian CLEAN:
sudo kill "$(cat /tmp/tcpdump_clean.pid)"; sleep 2
# --- atau --- varian EVASION:
sudo kill "$(cat /tmp/tcpdump_ev.pid)"; sleep 2
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
