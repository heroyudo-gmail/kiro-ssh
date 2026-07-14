# Deployment Guide — XGBoost Lambda + Flow Extractor v2

## Prerequisites
- AWS CLI configured (`aws configure`)
- Region: ap-southeast-1
- Instances running:
  - Analyzer: i-0d48771e71a679289
  - Attacker: i-078691dbf75a3f4c8
  - Target: i-0a3ed2fd3f0e72492

---

## Step 1: Create Lambda Layer with XGBoost

Lambda butuh XGBoost library. Kita buat Lambda Layer (karena XGBoost tidak include di Lambda default).

### 1a. Build Lambda Layer (dari local Linux/WSL/Docker)

```bash
# Buat folder struktur Lambda Layer
mkdir -p lambda-layer/python

# Install XGBoost + numpy ke folder layer (versi compatible Lambda Python 3.9)
pip install xgboost==1.7.6 numpy -t lambda-layer/python/ --platform manylinux2014_x86_64 --only-binary=:all:

# Zip layer
cd lambda-layer
zip -r ../xgboost-layer.zip python/
cd ..
```

> **Note:** Jika ukuran zip > 50MB, pakai XGBoost versi lebih lama atau strip unnecessary files:
> ```bash
> find lambda-layer/python -name "*.pyc" -delete
> find lambda-layer/python -name "__pycache__" -type d -exec rm -rf {} +
> find lambda-layer/python -name "*.dist-info" -type d -exec rm -rf {} +
> ```

### 1b. Upload Lambda Layer

```bash
aws lambda publish-layer-version \
    --layer-name xgboost-layer \
    --zip-file fileb://xgboost-layer.zip \
    --compatible-runtimes python3.9 \
    --region ap-southeast-1
```

Catat **LayerVersionArn** dari output (contoh: `arn:aws:lambda:ap-southeast-1:232032302717:layer:xgboost-layer:1`)

### 1c. Attach Layer ke Lambda Function

```bash
aws lambda update-function-configuration \
    --function-name ssh-detection-inference \
    --layers "arn:aws:lambda:ap-southeast-1:232032302717:layer:xgboost-layer:1" \
    --region ap-southeast-1
```

---

## Step 2: Deploy Lambda Code + Model

### 2a. Prepare deployment package

```bash
cd aws/lambda/

# Copy model ke folder lambda
cp ../../notebooks/xgboost_model.json .

# Zip deployment package
zip lambda_code.zip index.py xgboost_model.json

# Pindahkan zip ke folder aws
mv lambda_code.zip ../
cd ../..
```

### 2b. Upload Lambda code

```bash
aws lambda update-function-code \
    --function-name ssh-detection-inference \
    --zip-file fileb://aws/lambda_code.zip \
    --region ap-southeast-1
```

### 2c. Update Lambda memory (XGBoost butuh lebih dari 128MB)

```bash
aws lambda update-function-configuration \
    --function-name ssh-detection-inference \
    --memory-size 256 \
    --timeout 30 \
    --region ap-southeast-1
```

---

## Step 3: Deploy Flow Extractor v2 ke Analyzer Node

### 3a. Upload flow_extractor.py ke Analyzer via SSM

```bash
# Connect ke Analyzer
aws ssm start-session --target i-0d48771e71a679289 --region ap-southeast-1
```

Di dalam session Analyzer:

```bash
# Backup file lama
sudo cp /home/ssm-user/flow_extractor.py /home/ssm-user/flow_extractor_v1_backup.py

# Keluar SSM dulu, lalu upload via S3
```

### 3b. Upload via S3 (lebih mudah daripada copy-paste di SSM)

Dari local:
```bash
# Upload flow_extractor.py ke S3
aws s3 cp aws/flow_extractor.py s3://ssh-detection-features-232032302717/scripts/flow_extractor.py --region ap-southeast-1
```

Di Analyzer (via SSM):
```bash
# Download dari S3
aws s3 cp s3://ssh-detection-features-232032302717/scripts/flow_extractor.py /home/ssm-user/flow_extractor.py

# Set executable
chmod +x /home/ssm-user/flow_extractor.py
```

---

## Step 4: Testing

### 4a. Start Flow Extractor di Analyzer

Via SSM ke Analyzer:
```bash
aws ssm start-session --target i-0d48771e71a679289 --region ap-southeast-1
```

```bash
# Jalankan flow extractor
cd /home/ssm-user
sudo python3 flow_extractor.py
```

### 4b. Jalankan skenario attack dari Attacker Node

Via SSM ke Attacker:
```bash
aws ssm start-session --target i-078691dbf75a3f4c8 --region ap-southeast-1
```

**Skenario 1: Normal SSH (expected: Benign)**
```bash
# Login SSH ke target beberapa kali
for i in $(seq 1 15); do
    sshpass -p 'password123' ssh -o StrictHostKeyChecking=no ec2-user@10.0.1.38 "echo login $i" 2>/dev/null
    sleep 10
done
```

**Skenario 2: Failed login low rate (expected: Benign)**
```bash
# 5 failed attempts
for i in $(seq 1 5); do
    sshpass -p 'wrongpassword' ssh -o StrictHostKeyChecking=no ec2-user@10.0.1.38 "echo test" 2>/dev/null
    sleep 30
done
```

**Skenario 3: Hydra low-rate (expected: Attack)**
```bash
hydra -l ec2-user -P /usr/share/wordlists/rockyou.txt \
    -t 4 -w 5 10.0.1.38 ssh -V -f -u 2>/dev/null | head -500
```

**Skenario 4: Hydra high-rate (expected: Attack)**
```bash
hydra -l ec2-user -P /usr/share/wordlists/rockyou.txt \
    -t 16 -w 2 10.0.1.38 ssh -V -f -u 2>/dev/null | head -500
```

**Skenario 5: Nmap scan (expected: Benign/Suspicious)**
```bash
nmap -sV -p 22 10.0.1.38
```

**Skenario 6: Mixed traffic (expected: Attack detected)**
```bash
# Normal SSH di background
for i in $(seq 1 5); do
    sshpass -p 'password123' ssh -o StrictHostKeyChecking=no ec2-user@10.0.1.38 "echo normal $i" 2>/dev/null &
done

# Brute-force
hydra -l ec2-user -P /usr/share/wordlists/rockyou.txt \
    -t 8 10.0.1.38 ssh -V -f -u 2>/dev/null | head -300
```

### 4c. Verifikasi hasil

```bash
# Check S3 untuk CSV yang di-upload
aws s3 ls s3://ssh-detection-features-232032302717/features/ --region ap-southeast-1

# Check Lambda logs
aws logs tail /aws/lambda/ssh-detection-inference --since 1h --region ap-southeast-1

# Check SNS (email notification)
# Cek inbox heroyudo@gmail.com
```

---

## Step 5: Cleanup (setelah selesai testing)

```bash
# Stop semua instances untuk hemat biaya
aws ec2 stop-instances \
    --instance-ids i-078691dbf75a3f4c8 i-0d48771e71a679289 i-0a3ed2fd3f0e72492 \
    --region ap-southeast-1
```

---

## Troubleshooting

### Lambda error "No module named 'xgboost'"
- Layer belum ter-attach → ulangi Step 1c

### Lambda error "Unable to import module 'index'"
- Pastikan file dalam zip bernama `index.py` (bukan di subfolder)

### Lambda timeout
- Naikkan timeout ke 60 detik: `--timeout 60`

### Flow extractor tidak capture traffic
- Pastikan Traffic Mirror session aktif
- Check interface: `sudo tcpdump -i eth0 udp port 4789 -c 5`

### Model file not found
- Pastikan `xgboost_model.json` ada di zip Lambda
- Atau upload ke Layer di `/opt/xgboost_model.json`

---

## Expected Results (setelah deploy XGBoost)

| Skenario | Sebelum (rule-based) | Setelah (XGBoost) |
|----------|---------------------|-------------------|
| Normal SSH | Attack (FP) ❌ | Benign ✅ (expected) |
| Failed login | Attack (FP) ❌ | Benign ✅ (expected) |
| Hydra low-rate | Attack ✅ | Attack ✅ |
| Hydra high-rate | Attack ✅ | Attack ✅ |
| Nmap scan | Benign ✅ | Benign ✅ |
| Mixed | Attack ✅ | Attack ✅ |

Dengan model XGBoost, false positive seharusnya hilang karena model mempertimbangkan 10 fitur secara bersamaan.
