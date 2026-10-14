# Runbook AWS — PAPER SURVEY (FL-NIDS, 3 EC2, tanpa SFM)

> Versi survey dari `fed-runbook.md` (Paper 4). Beda: pakai `fed_node_survey.py`,
> prefix S3 `unsw-far/federated_survey/`, data dari `s01` (manual alignment, bukan SFM),
> stack name `fed-nids-survey`. Infra sama persis: 3 EC2 publik, tanpa NAT, akses SSM,
> bobot via S3. **Semua angka hasil `[TBD]` sampai run nyata.**
>
> Pola Paper 2/4: AL2023 + **boto3** (JANGAN `aws s3 cp` di instance). Teardown = hapus
> 1 stack → biaya nol. Region ap-southeast-1.

## 0. Prasyarat (sekali)
- Jalankan `notebooks2/s01_fed_data_partition.ipynb` → partisi klien ada di S3:
  `unsw-far/federated_survey/data/{cic,unsw}/{cic,unsw}_train.npz` (+ `_test.npz`).
- Unggah skrip ke S3: `unsw-far/federated_survey/scripts/fed_node_survey.py` (via boto3/console).

## 1. Deploy stack (template Paper 4 dipakai ulang; ganti stack name)
```
aws cloudformation create-stack --region ap-southeast-1 \
  --stack-name fed-nids-survey \
  --template-body file://fed-vpc-3ec2-public.yaml \
  --parameters ParameterKey=ProjectName,ParameterValue=fed-nids-survey \
  --capabilities CAPABILITY_IAM
aws cloudformation describe-stacks --region ap-southeast-1 --stack-name fed-nids-survey \
  --query "Stacks[0].Outputs" --output table
```
Catat `AggregatorId`, `ClientCICId`, `ClientUNSWId`.

## 2. Setup tiap node (SSM; boto3, bukan aws s3 cp)
Jalankan di KETIGA instance (ganti <ID>):
```
aws ssm send-command --region ap-southeast-1 --instance-ids <ID> \
  --document-name "AWS-RunShellCommand" --timeout-seconds 900 \
  --parameters commands='[
    "sudo dnf -y install python3-pip >/tmp/pip.log 2>&1",
    "python3 -m pip install -q --user boto3 numpy >/tmp/pipuser.log 2>&1",
    "mkdir -p /opt/fed",
    "python3 - <<PY",
    "import boto3; s3=boto3.client(\"s3\",region_name=\"ap-southeast-1\")",
    "s3.download_file(\"ssh-detection-features-232032302717\",\"unsw-far/federated_survey/scripts/fed_node_survey.py\",\"/opt/fed/fed_node_survey.py\")",
    "print(\"ready\")",
    "PY"
  ]'
```

## 3. Jalankan percobaan (client dulu, lalu aggregator)

### R3 — cross-dataset FedAvg (klaim utama). RUN=S_R3
Client-CIC:
```
aws ssm send-command --region ap-southeast-1 --instance-ids <ClientCICId> \
  --document-name "AWS-RunShellCommand" --timeout-seconds 3600 \
  --parameters commands='["cd /opt/fed && python3 fed_node_survey.py --role client --client-id cic --run S_R3 --rounds 100 --local-epochs 5 >/tmp/cic.log 2>&1 &"]'
```
Client-UNSW: idem, `--client-id unsw`, log `/tmp/unsw.log`.
Aggregator:
```
aws ssm send-command --region ap-southeast-1 --instance-ids <AggregatorId> \
  --document-name "AWS-RunShellCommand" --timeout-seconds 3600 \
  --parameters commands='["cd /opt/fed && python3 fed_node_survey.py --role aggregator --run S_R3 --clients cic,unsw --rounds 100 --mu 0.0 >/tmp/agg.log 2>&1 &"]'
```
Selesai saat `run_S_R3/global_final.npz` muncul di S3.

### R1 — FedProx (ulang R3 dengan mu>0). RUN=S_R1_mu01 / S_R1_mu001
Tambah `--mu 0.1` (atau 0.01) di KEDUA client; aggregator `--mu` untuk pencatatan.

### R6 — adversarial training. RUN=S_R6
Tambah `--adv-ratio 0.5 --adv-eps 0.1` di KEDUA client (aggregator normal).

> R2 (sweep non-IID) & R4 (biaya) lihat catatan di bawah. R5 (evasion) OFFLINE di
> `notebooks2/s14_adv_evasion.ipynb` (tak perlu EC2).

## 4. Pantau
```
aws ssm send-command --region ap-southeast-1 --instance-ids <AggregatorId> \
  --document-name "AWS-RunShellCommand" --parameters commands='["tail -n 30 /tmp/agg.log"]'
aws s3 ls s3://ssh-detection-features-232032302717/unsw-far/federated_survey/run_S_R3/ --recursive --region ap-southeast-1 | tail
```

## 5. Evaluasi (OFFLINE di SageMaker, bukan di EC2)
- R3: `notebooks2/s03_fedavg_crossdataset.ipynb` (set env `RUN=S_R3`).
- R5: `notebooks2/s14_adv_evasion.ipynb` (set env `RUN=S_R3`).
- R1/R2/R6: notebook s06/s05/s15 (TODO) — pola sama: tarik `global_final.npz`, hitung MCC.

## 6. R4 — biaya cloud (diukur dari log, bukan run terpisah)
Saat R1–R3 jalan, catat dari log aggregator/S3:
- **bytes/round**: ukuran `client_<id>_<t>.npz` × jumlah client × rounds.
- **latensi/round**: selisih timestamp antar baris "round t" di `/tmp/agg.log`.
- **wall-clock total**: dari round 0 sampai `global_final.npz`.
Catat ke `survey_out/r4_cloud_cost.csv` secara manual/skrip kecil.

## 7. TEARDOWN (WAJIB)
```
aws cloudformation delete-stack --region ap-southeast-1 --stack-name fed-nids-survey
aws cloudformation wait stack-delete-complete --region ap-southeast-1 --stack-name fed-nids-survey
```
Tanpa NAT → tak ada biaya nyangkut. Hasil tetap aman di S3.

## 8. Jebakan (warisi Paper 2/4)
- JANGAN `aws s3 cp` di instance → pakai boto3 (awscli AL2023 rusak setelah pip).
- SG tanpa inbound publik → akses HANYA via SSM.
- z-score per-client LOKAL (privasi); statistik tak dibagikan.
- Mulai `--rounds 10` untuk uji pipeline sebelum 100 penuh.
- Semua hasil ke S3 SEBELUM teardown.
