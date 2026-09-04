# Eksperimen Sistem Cloud-Backup Tahan-Ransomware (AWS)

Rekonstruksi sistem paper IJECE #42551: cadangan awan yang menggabungkan
**air-gapped backup + kompresi multi-algoritma adaptif + deteksi anomali
(SHA-256/metadata) + pemulihan otomatis**. Dijalankan di AWS EC2 (subnet publik,
tanpa NAT) dengan satu EBS terpisah sebagai penyimpanan air-gapped.

> Tujuan: menghasilkan angka nyata (rasio kompresi, RTO, FPR/FNR) untuk mengisi
> placeholder `⚠️[EST]` di `../rangkuman.md` dan `../ijece-id.tex`.

## Isi folder

| Berkas | Fungsi |
|---|---|
| `vpc.yaml` | CloudFormation: VPC 10.4.0.0/16 + subnet publik + IGW (tanpa NAT) |
| `ec2.yaml` | CloudFormation: EC2 publik + EBS air-gapped + security group |
| `generate_dataset.py` | Bangkitkan 43 berkas sintetis (CSV/LOG/JPG/XLSX) |
| `backup_system.py` | Baseline SHA-256 + AES-256 + kompresi 5 algoritma + simpan air-gapped |
| `ransomware_sim.py` | 3 pola serangan terkontrol (tanpa malware nyata) |
| `detector_recovery.py` | Deteksi anomali + auto-restore + hitung FPR/FNR/RTO |
| `run_experiment.py` | Orkestrasi end-to-end + rangkuman siap-paper |

## Prasyarat

- AWS CLI terkonfigurasi, region `ap-southeast-1` (atau sesuaikan).
- Session Manager plugin terpasang (untuk `aws ssm start-session`).
- **Tanpa key pair** - akses instans lewat SSM Session Manager (pola sama dengan project NIDS).

## Langkah 1 - Deploy infrastruktur

```bash
# 1a. Jaringan (VPC tanpa NAT)
aws cloudformation deploy \
  --template-file vpc.yaml \
  --stack-name rw-backup-vpc \
  --parameter-overrides ProjectName=rw-backup \
  --region ap-southeast-1

# 1b. EC2 + EBS air-gapped (IAM role + SSM; tanpa key pair, tanpa port SSH)
aws cloudformation deploy \
  --template-file ec2.yaml \
  --stack-name rw-backup-ec2 \
  --parameter-overrides ProjectName=rw-backup \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1

# Ambil output (InstanceId + perintah SSM)
aws cloudformation describe-stacks --stack-name rw-backup-ec2 \
  --query "Stacks[0].Outputs" --region ap-southeast-1
```

## Langkah 2 - Buka sesi & siapkan EBS air-gapped

Masuk ke instans via SSM (tanpa SSH), lalu format & mount volume kedua (sekali saja):

```bash
# buka sesi (ganti i-xxxx dengan InstanceId dari output)
aws ssm start-session --target i-xxxxxxxxxxxx --region ap-southeast-1
```

Di dalam sesi:

```bash
lsblk                                  # cari volume ~20GB (mis. /dev/nvme1n1)
sudo mkfs.ext4 /dev/nvme1n1            # format (HANYA sekali, saat pertama)
sudo mkdir -p /mnt/airgap
sudo mount /dev/nvme1n1 /mnt/airgap
sudo chown ubuntu:ubuntu /mnt/airgap
```

> Konsep air-gapped: mount hanya saat backup/restore, lalu `sudo umount /mnt/airgap`
> setelah selesai untuk meniru isolasi. Skrip eksperimen menulis ke
> `/mnt/airgap/backup`.

## Langkah 3 - Ambil kode & pasang dependency

```bash
git clone https://github.com/heroyudo-gmail/kiro-ssh.git
cd kiro-ssh/ransomware/aws
# dependency sudah dipasang via user-data; bila perlu ulang:
pip3 install zstandard brotli lz4 python-snappy pycryptodome openpyxl pillow numpy
```

## Langkah 4 - Jalankan eksperimen

```bash
# Opsi CEPAT (default, berkas maks ~50 MB) - validasi cepat
sudo mount /dev/nvme1n1 /mnt/airgap    # aktifkan air-gapped
python3 run_experiment.py --scale fast --airgap /mnt/airgap/backup --regen
sudo umount /mnt/airgap                # nonaktifkan air-gapped (isolasi)

# Opsi SKALA PENUH (berkas sampai 1 GB) - butuh EBS >= 120 GB
python3 run_experiment.py --scale full --airgap /mnt/airgap/backup --regen
```

Output ada di `./results/`:

| Berkas | Isi |
|---|---|
| `compression_report.csv` | rasio & waktu kompresi per algoritma/berkas (= Tabel 6) |
| `efficiency_report.csv` | skor efisiensi MCDM/WSM per algoritma (E%) |
| `experiment_summary.json` | rangkuman: FPR, FNR, RTO, tabel deteksi (siap-paper) |
| `eval_normal.json` | hasil uji kondisi normal (FPR) |
| `eval_<attack>.json` | hasil tiap skenario serangan (FNR, restore, RTO) |
| `baseline.json` | hash + metadata referensi |

## Langkah 5 - Isi angka ke paper

Ambil nilai dari `experiment_summary.json` -> `paper_ready`, lalu ganti placeholder
`⚠️[EST]` di `../rangkuman.md` (Bagian 3) dan angka di `../ijece-id.tex`.

## Alur eksperimen (yang dilakukan `run_experiment.py`)

1. Bangkitkan 43 berkas sintetis.
2. **Backup**: baseline SHA-256 + metadata -> enkripsi AES-256 -> kompresi 5 algoritma
   (semua diukur; berkas terpilih rule-based disimpan ke air-gapped).
3. **Uji normal** (tanpa serangan) -> FPR (harus 0).
4. Untuk tiap pola serangan (encrypt-hold / metadata-corruption / overwrite-corrupt):
   pulihkan dataset bersih -> serang 43 berkas -> deteksi + auto-restore -> FNR, RTO.
5. Rangkum ke `experiment_summary.json`.

## Hemat biaya

- Setelah selesai: **stop** instans (`aws ec2 stop-instances`) agar biaya compute ~nol.
  EBS air-gapped (`DeleteOnTermination=false`) tetap menyimpan cadangan.
- Hapus stack bila sudah tidak perlu: `aws cloudformation delete-stack ...`
  (hapus stack EC2 dulu, baru VPC).

## Catatan kejujuran data

Angka yang dihasilkan berasal dari implementasi ini dan lingkungan EC2 -- dapat
berbeda dari draf paper. Ganti placeholder paper HANYA dengan angka hasil run ini.
Nilai FPR/FNR 0% (bila terjadi) adalah konsekuensi deteksi berbasis hash pada
lingkungan terkontrol -- sudah dijelaskan jujur di `../ijece-id.tex`.
