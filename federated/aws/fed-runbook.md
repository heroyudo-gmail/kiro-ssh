# Runbook AWS — Paper 4 (Federated SFM-NIDS, 3 EC2 IP publik, tanpa NAT)

> **Topologi:** 3 EC2 public subnet (aggregator + client-cic + client-unsw), **tanpa
> NAT**, SG ketat (tanpa inbound internet), akses operator via **SSM**, bobot
> dipertukarkan **via S3** (`unsw-far/federated/`). Region ap-southeast-1.
> **Pola operasional warisi Paper 2:** AL2023 + **boto3** (JANGAN `aws s3 cp` di
> instance — awscli AL2023 rusak setelah pip). Teardown = hapus 1 stack → biaya nol.
>
> **STATUS:** DISUSUN (belum dieksekusi). Prasyarat: nb01 sudah menaruh partisi klien
> di S3 `unsw-far/federated/data/{cic,unsw}/<id>_train.npz`. Jalankan setelah Fase 1.

---

## 0. Prasyarat (sekali)
- Partisi klien ada di S3 (dari `notebooks/01_fed_data_partition.ipynb`):
  `unsw-far/federated/data/cic/cic_train.npz`, `.../unsw/unsw_train.npz`.
- Skrip `fed_node.py` diunggah ke S3 `unsw-far/federated/scripts/fed_node.py` (via boto3/console).
- Kredensial user `hero` (akun 232032302717), region ap-southeast-1.

## 1. Deploy stack
```
aws cloudformation create-stack --region ap-southeast-1 \
  --stack-name fed-nids \
  --template-body file://fed-vpc-3ec2-public.yaml \
  --capabilities CAPABILITY_IAM
# tunggu CREATE_COMPLETE
aws cloudformation describe-stacks --region ap-southeast-1 --stack-name fed-nids \
  --query "Stacks[0].Outputs" --output table
```
Catat: `AggregatorId`, `ClientCICId`, `ClientUNSWId`.

## 2. Setup tiap node (via SSM; pakai boto3, BUKAN aws s3 cp)
Jalankan di KETIGA instance (ganti <ID>):
```
aws ssm send-command --region ap-southeast-1 \
  --instance-ids <ID> \
  --document-name "AWS-RunShellCommand" \
  --timeout-seconds 900 \
  --parameters commands='[
    "sudo dnf -y install python3-pip >/tmp/pip.log 2>&1",
    "python3 -m pip install -q --user boto3 numpy >/tmp/pipuser.log 2>&1",
    "mkdir -p /opt/fed",
    "python3 - <<PY",
    "import boto3; s3=boto3.client(\"s3\",region_name=\"ap-southeast-1\")",
    "s3.download_file(\"ssh-detection-features-232032302717\",\"unsw-far/federated/scripts/fed_node.py\",\"/opt/fed/fed_node.py\")",
    "print(\"fed_node.py ready\")",
    "PY"
  ]'
```
> Catatan: unduh data klien dilakukan OTOMATIS oleh `fed_node.py` saat run (client
> menarik `data/<id>/<id>_train.npz` sendiri). Tak perlu copy manual.

## 3. Jalankan federasi (urutan: start client dulu, lalu aggregator)
RUN id bebas (mis. R1). Rounds/epoch sesuai dokumentasi Bagian B.

**Client-CIC (<ClientCICId>):**
```
aws ssm send-command --region ap-southeast-1 --instance-ids <ClientCICId> \
  --document-name "AWS-RunShellCommand" --timeout-seconds 3600 \
  --parameters commands='["cd /opt/fed && python3 fed_node.py --role client --client-id cic --run R1 --rounds 50 --local-epochs 1 >/tmp/fed_cic.log 2>&1 &"]'
```
**Client-UNSW (<ClientUNSWId>):** sama, `--client-id unsw`, log `/tmp/fed_unsw.log`.
**Aggregator (<AggregatorId>):**
```
aws ssm send-command --region ap-southeast-1 --instance-ids <AggregatorId> \
  --document-name "AWS-RunShellCommand" --timeout-seconds 3600 \
  --parameters commands='["cd /opt/fed && python3 fed_node.py --role aggregator --run R1 --clients cic,unsw --rounds 50 --mu 0.0 >/tmp/fed_agg.log 2>&1 &"]'
```
FedProx: tambah `--mu 0.01` di SEMUA client (dan aggregator untuk pencatatan).

## 4. Pantau
```
aws ssm send-command --region ap-southeast-1 --instance-ids <AggregatorId> \
  --document-name "AWS-RunShellCommand" \
  --parameters commands='["tail -n 30 /tmp/fed_agg.log"]'
aws s3 ls s3://ssh-detection-features-232032302717/unsw-far/federated/run_R1/ --recursive --region ap-southeast-1 | tail
```
Selesai saat `run_R1/global_final.npz` muncul di S3.

## 5. Evaluasi (OFFLINE, bukan di EC2)
Tarik `run_R1/global_final.npz` → notebook evaluasi (Fase 3) hitung MCC/recall/
precision/balanced-acc pada held-out test global; bandingkan vs centralized (nb02) &
local-only.

## 6. TEARDOWN (WAJIB — hemat biaya)
```
aws cloudformation delete-stack --region ap-southeast-1 --stack-name fed-nids
aws cloudformation wait stack-delete-complete --region ap-southeast-1 --stack-name fed-nids
```
Tanpa NAT GW → tak ada komponen biaya nyangkut. Hasil tetap aman di S3.

## 7. Catatan & jebakan (warisi Paper 2)
- **JANGAN `aws s3 cp` di instance** → pakai boto3 (awscli AL2023 rusak setelah pip).
- SG tanpa inbound publik → akses HANYA via SSM (bukan SSH).
- Bobot via S3 → node tak perlu saling buka port (aman walau IP publik).
- z-score **per-client lokal** (privasi); statistik tak dibagikan.
- Mulai dengan rounds kecil (mis. 10) untuk uji pipeline sebelum 50 penuh.
- Semua hasil ke S3 SEBELUM teardown.
