# ROADMAP -- Masuk Domain Smart Grid lewat FL (bertahap, dari kekuatan FL-NIDS)

> **Tujuan:** memperluas riset dari FL-NIDS (trafik jaringan) ke keamanan smart grid
> SECARA BERTAHAP, tanpa melompat ke domain fisika tenaga listrik yang belum dikuasai.
> **Prinsip:** masuk dari SISI KEKUATAN (FL / keamanan ML), bukan dari sisi fisika grid.
> **Status:** Tahap 1 dipilih sebagai titik mulai (jembatan literatur). Belum ada aksi coding.
> **Kejujuran posisi:** kita AHLI di FL-NIDS, PENDATANG di power systems. Nyatakan
> eksplisit di tiap naskah; jangan menyamar sebagai ahli grid.

---

## MENGAPA BERTAHAP (jarak yang nyata)

**Sudah dikuasai (aset dari paper 1-6 + survey):**
- FL-NIDS: FedAvg/FedProx, non-IID (Dirichlet), cross-dataset, SFM, adversarial (FGSM/PGD),
  XAI (SHAP), multi-seed CI, deployment AWS nyata.
- Dataset trafik: CIC-IDS2017/2018, UNSW-NB15.
- Metodologi survey reproduktif (`../paper-survey.md`).

**Belum dikuasai (gap domain smart grid):**
- Data siber-fisik (tegangan/frekuensi/PMU/SCADA), bukan flow jaringan.
- Dinamika fisik grid (stabilitas, state estimation, hukum Kirchhoff).
- Serangan khas grid: False Data Injection (FDI), bukan DDoS/portscan.
- Validasi Hardware-in-the-Loop (HIL).

**Jembatan (titik singgung nyata):** paper smart grid (cyber-id.md) menyebut FL sebagai
teknik deteksi, dan menyorot PERSIS kelemahan yang kita kuasai -- FL non-IID, poisoning,
minim bukti deployment. Jadi kita masuk lewat "FL untuk keamanan DATA grid", bukan
"kendali FISIK grid".

---

## PETA TAHAP (perlahan, tiap tahap = 1 artefak nyata)

| Tahap | Fokus | Butuh data grid? | Risiko | Output |
|---|---|---|---|---|
| 0 | Orientasi domain (baca) | tidak | sangat rendah | catatan istilah + daftar dataset |
| **1** | **Jembatan literatur (position/mini-survey)** | **tidak** | **rendah** | **naskah survey** |
| 2 | Reproduksi baseline FL di dataset grid publik | ya | sedang | notebook + CSV |
| 3 | Kontribusi kecil orisinal (non-IID/adversarial FDI) | ya | sedang-tinggi | paper riset Sinta 2 |
| 4 | Aspek siber-fisik (DT/kendali) -- butuh kolaborator | ya + HIL | tinggi | future work |

> Kerjakan 0 -> 1 dulu. Jangan menyentuh Tahap 4 tanpa kolaborator power systems.

---

## TAHAP 1 (AKTIF) -- Jembatan Literatur

**Ide naskah:** *"Federated Learning untuk Deteksi Serangan di Smart Grid: Pelajaran
dari FL-NIDS"* (position paper / mini-survey). Memakai keahlian FL non-IID/adversarial
yang sudah teruji untuk MENGKRITISI penerapan FL di grid -- belum perlu data grid.

**Kenapa aman:** memakai metodologi survey yang sudah terbukti (`../paper-survey.md`)
+ bahan `references/` yang sudah ada. Kontribusi = pemetaan jujur, bukan klaim empiris
di domain yang belum diuji.

**Bahan yang SUDAH ada (tinggal diarahkan):**
- `references/01_Robust_Aggregation...` -> poisoning/backdoor (relevan: grid takut FDI poisoning).
- `references/02_Adaptive...Cross_Domain...` -> cross-domain drift (relevan: grid beda topologi).
- `references/03_Communication_Efficient...` -> overhead komunikasi (relevan: substasiun terbatas).
- `references/04_Explainable...` -> XAI forensik (relevan: operator grid butuh interpretasi).
- `references/05_Quantum_Inspired...` -> (opsional, jauh).
- `references/cyber-id.md` -> KONTEKS MOTIVASI (reviu paper DT smart grid MDPI 2026).
  BUKAN pondasi/rujukan utama (domain belum dikuasai).
- `references/state_of_art_gap_federated_nids.md` -> gap FL-NIDS yang bisa dipetakan ke grid.

**Kerangka naskah usulan (draf):**
1. Pendahuluan: kenapa FL menarik untuk smart grid (privasi antar-utilitas) + tiga
   kelemahan FL yang sudah dikenal di NIDS (non-IID, poisoning, validation gap).
2. Latar: ringkas FL-NIDS (yang kita kuasai) + ringkas kebutuhan keamanan grid
   (dari cyber-id.md, diakui sebagai bacaan sekunder).
3. Pemetaan: pelajaran FL-NIDS -> implikasi untuk FL-grid (tabel: masalah NIDS <-> analог grid).
4. Gap & agenda: apa yang belum teruji di FL-grid, yang bisa kita isi di Tahap 2-3.
5. Kesimpulan: posisi jujur + arah riset.

**Checklist Tahap 1:**
- [ ] Tahap 0 ringan: buat catatan istilah (FDI, state estimation, PMU/SCADA) + daftar
      dataset grid publik yang bisa diakses (verifikasi link nyata, jangan mengarang).
- [ ] Tentukan target jurnal (Sinta 2) + gaya sitasi.
- [ ] Susun kerangka naskah (pakai 5 poin di atas) -> file `.md` baru.
- [ ] Isi bagian pemetaan dari bahan `references/` yang sudah ada.
- [ ] Review kejujuran: pastikan posisi "pendatang di grid" eksplisit.

---

## YANG PERLU DIKONFIRMASI (lengkapi saat diketahui)
- Target jurnal/venue Tahap 1 (Sinta 2 mana? atau tetap JICTRA?).
- Apakah ada akses/kenalan di bidang power systems (menentukan kelayakan Tahap 4).
- Dataset grid publik yang realistis diakses dari AWS (untuk Tahap 2) -- perlu dicek.

## CATATAN
- Semua angka empiris (Tahap 2+) HARUS dari eksekusi nyata di SageMaker; jangan mengarang.
- cyber-id.md = konteks, bukan fondasi (pola sama seperti SFM: jangan jadikan rujukan inti
  sesuatu yang di luar penguasaan/validasi kita).
