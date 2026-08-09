# VPC Testing — Catatan & Lessons Learned

## Percobaan 1: 5 EC2 (Amazon Linux 2023) — GAGAL

### Setup
- 5 EC2: 3 Attacker + 1 Target + 1 Analyzer
- OS: Amazon Linux 2023 (semua instance)
- Network: Private subnet + NAT Gateway + VPC Endpoints (SSM)
- Tools install via UserData

### Masalah yang Terjadi

| # | Masalah | Root Cause | Dampak |
|---|---------|-----------|--------|
| 1 | Target EC2 tidak bisa diakses via SSM | pip install di UserData menimpa system packages (dateutil, six) → SSM agent crash | Tidak bisa capture traffic di Target |
| 2 | AWS CLI broken di Analyzer | Sama — pip install global merusak botocore dependencies | Gagal download model dari S3 (awalnya) |
| 3 | hping3 tidak tersedia | Amazon Linux 2023 repo tidak punya hping3, compile gagal (missing tcl) | Phase DDoS-SYN gagal |
| 4 | Pcap kosong (24 bytes) | tcpdump jalan di Analyzer tapi traffic attacker→target tidak lewat Analyzer | Tidak ada flow data |
| 5 | SSH brute-force timeout | Hydra SSH terlalu lambat (SSH rate limiting default) dalam 60 detik | Phase 1 selalu timeout |
| 6 | cicflowmeter output kosong | Pcap kosong → tidak ada input | Inference gagal (no flow CSV) |

### Biaya Terbuang
- NAT Gateway: ~$0.045/jam (tetap jalan meskipun instances stopped)
- 5 EC2 running selama debugging: ~$0.40/jam
- VPC Endpoints (Interface): ~$0.01/jam per endpoint × 3

---

## Perbaikan untuk Retry 5 EC2 di Masa Depan

### 1. Ganti OS → Debian 12 atau Ubuntu 22.04

**Alasan:**
- `apt install hping3 hydra slowhttptest nmap medusa` — semua tersedia langsung
- pip install lebih aman (pakai `--break-system-packages` atau venv)
- SSM agent install manual reliable via `.deb` package

**AMI:**
- Debian 12: cari di AWS Marketplace (gratis)
- Ubuntu 22.04: `ami-0672bc4a5a0d5e68f` (ap-southeast-1, cek latest)

### 2. JANGAN pip install global di UserData

**Masalah:** `pip3 install boto3 pandas numpy xgboost` menimpa system packages yang dibutuhkan SSM agent dan AWS CLI.

**Solusi:**
```bash
# Pakai virtual environment
python3 -m venv /opt/venv
/opt/venv/bin/pip install boto3 pandas numpy xgboost scikit-learn cicflowmeter

# Atau di Debian/Ubuntu, pakai flag:
pip3 install ... --break-system-packages
# (ini aman di Debian karena system packages terpisah dari pip)
```

### 3. Semua instance pakai AnalyzerRole (bukan SSMRole)

**Masalah:** Target pakai SSMRole (tanpa S3 access) → tidak bisa upload pcap/flows ke S3.

**Solusi:** Pakai satu role untuk semua instance:
```yaml
ManagedPolicyArns:
  - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
Policies:
  - PolicyName: S3Access
    PolicyDocument:
      Statement:
        - Effect: Allow
          Action: s3:*
          Resource: '*'
```

### 4. Traffic Capture Strategy

**Masalah:** Analyzer tidak bisa capture traffic yang flow-nya attacker→target (Analyzer bukan di jalur).

**Solusi (pilih salah satu):**

| Opsi | Complexity | Reliability |
|------|-----------|-------------|
| **A. Capture di Target** | Low | High — traffic pasti lewat sini |
| **B. Traffic Mirroring** | Medium | High — ENI target mirror ke analyzer |
| **C. All-in-one** | Lowest | Highest — semua di 1 mesin |

**Rekomendasi: Opsi A** (capture di Target, transfer CSV ke Analyzer via S3)

### 5. SSH Rate Limiting

**Masalah:** SSH default MaxAuthTries=6, LoginGraceTime=120 → Hydra sangat lambat.

**Fix di Target UserData:**
```bash
echo "MaxAuthTries 100" >> /etc/ssh/sshd_config
echo "LoginGraceTime 300" >> /etc/ssh/sshd_config
systemctl restart sshd
```

**Hydra command:** pakai `-t 16` (16 threads parallel)

### 6. Validasi Sebelum Run Test

Tambahkan step validasi di `run_test.py` sebelum attack phases:

```python
# Cek semua instance SSM Online
# Cek tools: which hydra, which hping3, cicflowmeter --help
# Cek services: systemctl status sshd nginx vsftpd
# Cek models: ls /opt/ids2018/models/*.json
# BARU jalankan attack schedule
```

### 7. Urutan Deploy yang Benar

```
1. Network stack (VPC + subnet + IGW atau NAT)
2. Instances stack (semua Debian + AnalyzerRole)
3. Wait 3 menit
4. VALIDASI: ssm describe-instance-information → semua 5 Online?
5. Upload models + scripts via SSM send-command
6. VALIDASI: cek tools + services di setiap instance
7. Run test
```

### 8. Hindari NAT Gateway (hemat biaya)

**Opsi:** Pakai public subnet + IGW (bukan private subnet + NAT)
- Pro: tidak ada biaya NAT ($0.045/jam = $32/bulan)
- Con: instances punya public IP (kurang secure, tapi untuk testing OK)
- Atau: pakai NAT hanya saat install, lalu delete

---

## Percobaan 2: Single Node (Debian) — IN PROGRESS

### Setup
- 1 EC2 t3.large: attacker + target + analyzer all-in-one
- OS: Debian 12
- Network: Public subnet + IGW (tanpa NAT)
- File: `05-single-node-debian.yaml`

### Keuntungan
- Semua di satu mesin → attack ke localhost → capture loopback
- Tidak ada masalah cross-instance / traffic routing
- Tidak ada masalah SSM (hanya 1 instance)
- Tidak ada NAT cost
- Debug mudah (1 mesin)

### Kekurangan
- Tidak realistis (attacker = target = analyzer)
- Untuk paper/presentasi: perlu disclaimer "testing environment"
- Traffic pattern mungkin sedikit berbeda dari multi-host

---

## Checklist Sebelum Run Test (untuk semua skenario)

- [ ] Semua instance SSM Online (`aws ssm describe-instance-information`)
- [ ] AWS CLI berfungsi di semua instance (`aws --version`)
- [ ] Attack tools terinstall (hydra, hping3, slowloris, ab, nping)
- [ ] Target services running (sshd port 22, nginx port 80, vsftpd port 21)
- [ ] CICFlowMeter terinstall (`cicflowmeter --help`)
- [ ] Models + meta files ada di analyzer (`ls /opt/ids2018/models/`)
- [ ] Schedule.json ada (`cat /opt/ids2018/schedule/schedule.json`)
- [ ] inference.py ada (`ls /opt/ids2018/inference.py`)
- [ ] tcpdump bisa capture (`tcpdump -i any -c 5 -w /tmp/test.pcap`)
- [ ] Disk space cukup (`df -h`)
