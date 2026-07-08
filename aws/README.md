# AWS Deployment - SSH Brute-Force Detection

## Arsitektur (sesuai paper)

```
[Target EC2 - SSH Server]
        |
   Traffic Mirroring (TCP port 22)
        |
        v
[Analyzer EC2 - CICFlowMeter]
        |
   Extract 10 features -> CSV
        |
        v
[S3 Bucket] --> trigger --> [Lambda Function] --> [SNS Alert]
                              (XGBoost inference)
```

## Komponen

1. **Target Server** (t3.micro) - EC2 dengan SSH, Traffic Mirroring enabled
2. **Analyzer Node** (t3.medium) - EC2 menjalankan CICFlowMeter
3. **S3 Bucket** - Menyimpan feature vectors (CSV)
4. **Lambda Function** - Load XGBoost model, predict, kirim alert
5. **SNS Topic** - Kirim notifikasi jika terdeteksi attack

## Cara Deploy

1. `cd aws/`
2. Edit `config.env` sesuai region dan preference kamu
3. Jalankan `python deploy.py` untuk setup semua resource
4. Jalankan simulasi attack dari Attacker Node

## Estimasi Biaya

~$42/bulan (sesuai paper) untuk 1 ENI yang dimonitor.
