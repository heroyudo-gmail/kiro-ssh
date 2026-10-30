# Bedah Paper Referensi — Dasar Penyusunan `paper4-xai.md`

> **Tujuan dokumen.** Membedah manuskrip referensi (JTIIK) secara kritis sebelum kita
> menulis paper sendiri. Dokumen ini bukan paper; ini catatan analisis internal: apa yang
> paper itu klaim, mana yang kuat (layak dicontoh), mana yang lemah (celah untuk kita
> perbaiki), dan peta "kekurangan → rencana perbaikan". Semua angka di sini dikutip dari
> isi manuskrip apa adanya (`references/manuskrip_extracted.txt`).
>
> **Catatan penting arah kerja:** paper kita (`paper4-xai.md`) berdiri sendiri —
> **TIDAK memakai Semantic Feature Mapping (SFM)**. Dokumen ini hanya membedah referensi;
> keputusan metode final dibahas di bagian akhir ("Peta Perbaikan").

---

## 1. Identitas Paper Referensi

| Item | Isi |
|---|---|
| Judul | Explainable Artificial Intelligence untuk Network Intrusion Detection System: Analisis Interpretabilitas dan Generalisasi Lintas-Dataset pada Pipeline Bebas-Kebocoran |
| Target jurnal | JTIIK (p-ISSN 2355-7699 / e-ISSN 2528-6579) |
| Bahasa | Indonesia + abstrak Inggris; gaya sitasi nama–tahun |
| Dataset | CIC-IDS-2017 (referensi) → 10 partisi CSE-CIC-IDS2018 (target) |
| Model | RandomForestClassifier (dilatih di CIC17) |
| XAI | SHAP (global, stabilitas peringkat antar-target); LIME disebut tapi tak dilaporkan |
| Status | Draft (penulis & tanggal masih placeholder) |

---

## 2. Inti Argumen (Rangka yang Dibangun Paper)

1. **Pipeline bebas-kebocoran (leak-free):** normalisasi label/kolom, harmonisasi skema
   fitur, stratified subsampling, split train–test, lalu *seleksi fitur / standardisasi /
   SMOTE hanya pada data latih*.
2. **Protokol lintas-dataset:** latih di CIC17, evaluasi langsung ke 10 partisi CIC18
   (transfer, bukan re-fit di target).
3. **Temuan utama (the punchline):** within-dataset nyaris sempurna, tetapi lintas-dataset
   MCC runtuh ke 0,00% walau weighted-F1 tetap tampak tinggi.
4. **Pesan metodologis:** weighted-F1 dan akurasi menyesatkan pada data tidak seimbang →
   wajib melaporkan MCC + recall per-kelas + confusion matrix + validasi lintas-dataset.
5. **XAI (SHAP):** fitur teratas stabil antar-target, tetapi stabilitas fitur tidak
   menjamin transferabilitas model.

### Angka kunci yang dilaporkan

- **Within-dataset (CIC17):** F1 0,9963 · MCC 98,54% · Akurasi 0,9963 · AUC 0,9997.
- **Lintas-dataset (rata-rata 10 target CIC18):** weighted-F1 0,7864 · MCC 0,00% ·
  Akurasi 0,8511 · AUC 0,4635 · recall kelas Attack = 0 di semua target.
- **Gap generalisasi:** F1 turun 0,2099; MCC turun 98,54 poin persen.
- **SHAP top-5 (stabilitas peringkat):** Bwd Packet Length Min (avg rank 1,82),
  Flow Duration (3,27), Fwd URG Flags (4,18), Bwd Packet Length Max (4,45),
  Average Packet Size (4,91).

---

## 3. KELEBIHAN — yang layak dicontoh

| Kode | Kelebihan | Mengapa kuat |
|---|---|---|
| K1 | Pipeline leak-free yang disiplin | `fit` semua transformasi (seleksi fitur, scaler, SMOTE) hanya di train; benar secara metodologi dan sering dilanggar paper lain. |
| K2 | Kritik metrik tajam dan benar | Menunjukkan weighted-F1 0,996 bisa muncul padahal 0 serangan terdeteksi — pesan valid & berguna. |
| K3 | Narasi "angka bagus bisa menipu" | Kontras within vs cross sangat komunikatif, mudah dipahami reviewer. |
| K4 | Jujur mengakui keterbatasan | Mengakui hanya CIC17 sebagai referensi, biner saja, belum domain adaptation. |
| K5 | XAI dikaitkan ke keputusan model | SHAP global + stabilitas peringkat antar-target, bukan sekadar menempel gambar. |

---

## 4. KEKURANGAN — celah untuk kita perbaiki

| Kode | Kekurangan | Dampak | Peluang perbaikan |
|---|---|---|---|
| L1 | **Berhenti di diagnosis, tanpa solusi.** Paper hanya menyatakan "model gagal, MCC=0, perlu domain adaptation" lalu selesai. | Kontribusi berhenti pada "mengeluh". | Tambahkan **tahap pemulihan** (kalibrasi/adaptasi minimal) → tunjukkan MCC bisa naik kembali. Ini lompatan kontribusi terbesar. |
| L2 | **Lintas-dataset relatif ringan: CIC-2017 → CIC-2018.** Keduanya CICFlowMeter; beda utama hanya hari perekaman. | "Lintas-dataset" di sini hampir sama alat & skema fitur; shift-nya ringan. | Pakai skenario shift yang lebih bermakna dan/atau justifikasi dengan **bukti shift kuantitatif** (mis. jarak distribusi), bukan sekadar klaim. |
| L3 | **MCC = 0,00% seragam di 10 target, tetapi AUC bervariasi (0,0169–0,76).** | MCC (threshold 0,5) runtuh total, padahal AUC beberapa target > 0,7 (THURSDAY-1 = 0,7308; WEDNESDAY-2 = 0,7632). | **Tanda khas masalah threshold/kalibrasi**, bukan semata "model buta". Kita perbaiki: kalibrasi threshold, laporkan PR-AUC, pisahkan "gagal ranking" vs "gagal threshold". Koreksi ilmiah paling tajam. |
| L4 | **Single-run, tanpa interval kepercayaan.** | Tidak ada ukuran variabilitas; rentan dibantah reviewer. | Gunakan **multi-seed + CI95**. |
| L5 | **Harmonisasi fitur dengan "isi 0".** Fitur referensi yang tak ditemukan di target diisi 0. | Bisa jadi penyebab tersembunyi kegagalan, tapi efeknya tidak diisolasi. | Uji/bahas efek strategi penanganan fitur secara eksplisit (ablation). |
| L6 | **SHAP dihitung pada model yang recall Attack = 0.** | Jika model tak pernah mendeteksi serangan, SHAP menjelaskan "kenapa semua dianggap Normal" — interpretasinya rapuh. Paper tidak menyadari ini. | Bahas bahwa **SHAP harus dibaca bersama kondisi model**; SHAP pada model gagal ≠ SHAP bermakna. Tambahkan SHAP pada model yang sudah dipulihkan sebagai pembanding. |
| L7 | **Tidak ada analisis per-jenis-serangan.** | Hanya biner; tak tahu serangan mana yang lolos. | (Opsional) multi-kelas / recall per-attack. |
| L8 | **Placeholder penulis & tanggal.** | Menandakan draft belum final. | Kosmetik; tidak relevan untuk substansi. |

---

## 5. Temuan Teknis Kunci (L3, perlu ditegaskan)

Pada Tabel 2 referensi, MCC seluruh target = 0,00% **tetapi** AUC bervariasi lebar
(0,0169 s.d. 0,7632). MCC dihitung dari prediksi kelas pada threshold 0,5; AUC dihitung
dari skor ranking. Kombinasi **"MCC = 0 tetapi AUC ≠ 0,5"** adalah indikasi khas
**masalah threshold/kalibrasi** — ada sinyal pembeda pada skor, tetapi titik potong 0,5
tidak cocok untuk distribusi target yang sangat tidak seimbang.

Paper referensi menafsirkan fenomena ini **murni** sebagai kegagalan distribusi. Itu
**sebagian benar, sebagian keliru**: pergeseran distribusi memang ada, tetapi sebagian
"kegagalan" sebenarnya adalah artefak threshold. Memisahkan dua hal ini (kegagalan
ranking vs kegagalan threshold) adalah salah satu koreksi ilmiah paling bernilai yang bisa
kita tawarkan.

---

## 6. Peta Perbaikan: Kekurangan → Rencana Kerja Kita

Prinsip: **tanpa SFM**, semua angka jujur dari eksperimen nyata, format & urutan JICTRA,
bahasa Indonesia, output tahap awal = `paper4-xai.md`.

| Dari kekurangan | Rencana perbaikan di paper kita |
|---|---|
| L1 (tanpa solusi) | Tambahkan tahap pemulihan minimal setelah diagnosis, lalu ukur kenaikan MCC & recall Attack. |
| L2 (shift ringan) | Pilih skenario lintas-dataset + sertakan bukti shift kuantitatif sebagai justifikasi. |
| L3 (threshold vs distribusi) | Pisahkan analisis ranking (AUC/PR-AUC) dari analisis keputusan (MCC@0,5); tambahkan kalibrasi threshold. |
| L4 (single-run) | Multi-seed + CI95 untuk semua angka utama. |
| L5 (isi-0) | Ablation/pembahasan strategi penanganan fitur. |
| L6 (SHAP pada model gagal) | SHAP dibaca bersama kondisi model; bandingkan SHAP model gagal vs model pulih. |
| L7 (biner saja) | Opsional: recall per-jenis-serangan. |

### Hal yang MASIH perlu diputuskan bersama (belum final)

1. **Dataset lintas** yang dipakai (menentukan apakah perlu folder `aws_xai` untuk
   validasi trafik nyata, dan notebook di `notebook_xai`).
2. **Ketersediaan data mentah/preprocessed** untuk menjalankan SHAP sungguhan vs menyusun
   kerangka dulu.
3. **Model**: ikut RandomForest (seperti referensi) atau pakai model lain — selama tanpa
   SFM dan angka jujur.

> Keputusan atas tiga poin di atas akan dicatat di sini begitu disepakati, sebelum
> penyusunan `paper4-xai.md` dimulai.
