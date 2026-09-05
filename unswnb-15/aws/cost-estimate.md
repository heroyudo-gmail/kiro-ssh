# Estimasi Biaya — T10 Skema 3-EC2 (pola NIDS-01)

> Region acuan: **ap-southeast-1 (Singapore)**. Tarif *on-demand* **indikatif**, wajib
> diverifikasi via AWS Pricing Calculator sebelum eksekusi (harga dapat berubah). USD.
>
> Skema ini mereplikasi NIDS-01: 3 EC2 (Attacker public; Target & Analyzer private) + **NAT
> Gateway** (agar private subnet bisa update paket + SSM). NAT = penyumbang biaya utama.

---

## 1. Komponen & Tarif Indikatif

| Komponen | Tarif (ap-southeast-1) | Catatan |
|---|---|---|
| EC2 `t3.medium` (2 vCPU, 4 GB) | ~$0,0528 / jam | dipakai 3× (Attacker/Target/Analyzer) |
| EBS gp3 (20–30 GB) × 3 | ~$0,08 / GB-bulan → ~$0,20/hari total | root + pcap |
| **NAT Gateway** | ~$0,059 / jam + ~$0,059 / GB proses | **penyumbang biaya utama** |
| Elastic IP (utk NAT) | $0 saat terpasang & aktif | |
| Transfer keluar | ~$0,09–0,12 / GB (100 GB gratis/bln) | minim (internal + S3 same-region gratis) |
| S3 | ~$0,025 / GB-bulan | model + pcap + hasil |

---

## 2. Biaya per Fase

### Fase 2 — Deteksi (singkat, ~beberapa jam total)
Cukup nyalakan 3 EC2 + NAT beberapa jam (deploy + install + 2 run × 7 menit + proses).
| Item | Perkiraan (≈4 jam aktif) |
|---|---|
| 3× t3.medium × 4 jam | ~$0,63 |
| NAT 4 jam + data kecil | ~$0,25 |
| EBS + S3 | ~$0,10 |
| **Total Fase 2** | **≈ $1** |

### Fase 1 — FAR (jangka panjang)
Instance yang perlu menyala kontinu: **Target** (capture) + **Analyzer** (proses) + **NAT**.
Attacker bisa di-stop selama Fase 1 (tak dipakai). Anggap 2× t3.medium + NAT.

| Durasi (24 jam/hari) | 2× t3.medium | NAT (jam) | EBS+S3 | **Total** |
|---|---|---|---|---|
| 3 hari (72 jam) | ~$7,6 | ~$4,3 + data | ~$0,7 | **≈ $13–15** |
| 7 hari (168 jam) | ~$17,7 | ~$9,9 + data | ~$1,6 | **≈ $30–33** |

> **NAT mendominasi** untuk durasi panjang. Ini konsekuensi memakai private subnet
> (skema NIDS-01). Kalau biaya jadi kendala, lihat opsi hemat di bawah.

---

## 3. Opsi Hemat (tetap skema 3-EC2)

1. **Capture terjadwal, bukan 24 jam.** Nyalakan Target+Analyzer+NAT hanya beberapa jam
   per segmen (pagi/siang/malam) selama 3 hari. Biaya turun proporsional (bisa ~$4–6 total).
   **Lapor jujur** di naskah bahwa observasi tidak kontinu.
2. **Hapus NAT saat idle** (pola NIDS-01): stop EC2 + `delete-stack` NAT saat jeda; buat ulang
   saat resume. Menghilangkan biaya NAT di waktu tak dipakai.
3. **Stop Attacker selama Fase 1** (tak dipakai untuk FAR).
4. **Free Tier** (jika akun < 12 bulan): t3.micro gratis — tapi t3.medium tidak; NAT tak masuk Free Tier.

---

## 4. Ringkasan Realistis

| Skenario | Estimasi |
|---|---|
| Fase 2 (deteksi) saja | **≈ $1** |
| Fase 1 FAR 3 hari kontinu | **≈ $13–15** |
| Fase 1 FAR 7 hari kontinu | **≈ $30–33** |
| Fase 1 FAR terjadwal 3 hari (hemat) | **≈ $4–6** |

> **Perbandingan:** skema single-instance tanpa NAT (yang sempat dibahas) jauh lebih murah
> (~$2–6), TETAPI kita sepakat memakai skema NIDS-01 (3-EC2 + private + NAT) demi
> **comparability langsung** dengan paper NIDS-01. Biaya ekstra NAT adalah trade-off sadar.

---

## 5. Kontrol Biaya (wajib)
- Set **AWS Budgets** alert (mis. $20) sebelum mulai.
- Stop Attacker selama Fase 1; stop semua EC2 saat jeda.
- Setelah selesai: `delete-stack unsw-far` (hapus EC2+EBS+VPC+IGW+NAT+EIP → biaya nol).
- Cek tak ada Elastic IP idle (`aws ec2 describe-addresses`).
