#!/usr/bin/env python3
"""Buat PPTX presentasi METODE ke promotor (Bahasa Indonesia), 5 slide inti.

Sumber isi: paper6-federated.tex / paper-survey.md (selaras). Gambar dari figure-fed/.
Jalankan: python make_ppt_promotor.py  -> menghasilkan ppt-promotor-metode.pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figure-fed")
OUT = os.path.join(HERE, "ppt-promotor-metode.pptx")

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GREEN = RGBColor(0x2E, 0x8B, 0x57)
GREY = RGBColor(0x55, 0x55, 0x55)
RED = RGBColor(0xB0, 0x30, 0x30)

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height


def add_slide():
    return prs.slides.add_slide(BLANK)


def textbox(slide, left, top, width, height):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def set_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def title_bar(slide, text, subtitle=None):
    tf = textbox(slide, Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.1))
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = text
    r.font.size = Pt(30); r.font.bold = True; r.font.color.rgb = NAVY
    if subtitle:
        p2 = tf.add_paragraph()
        r2 = p2.add_run(); r2.text = subtitle
        r2.font.size = Pt(15); r2.font.color.rgb = GREY; r2.font.italic = True


def bullets(slide, items, left, top, width, height, size=18, gap=6):
    tf = textbox(slide, left, top, width, height)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        # it bisa (level, teks, warna?) atau teks biasa
        if isinstance(it, tuple):
            level, text = it[0], it[1]
            color = it[2] if len(it) > 2 else RGBColor(0x22, 0x22, 0x22)
        else:
            level, text, color = 0, it, RGBColor(0x22, 0x22, 0x22)
        p.level = level
        bullet = "•  " if level == 0 else "–  "
        r = p.add_run(); r.text = bullet + text
        r.font.size = Pt(size - level * 2); r.font.color.rgb = color


# ============== SLIDE 1 — JUDUL ==============
s = add_slide()
set_bg(s, NAVY)
tf = textbox(s, Inches(0.8), Inches(2.1), Inches(11.7), Inches(2.6))
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
r = p.add_run()
r.text = "Federated Learning untuk Deteksi Intrusi Jaringan Lintas-Domain"
r.font.size = Pt(34); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
r2 = p2.add_run()
r2.text = ("Studi jarak domain, protokol evaluasi bebas-kebocoran, "
           "dan analisis robustness adversarial pada testbed cloud")
r2.font.size = Pt(17); r2.font.color.rgb = RGBColor(0xCF, 0xE8, 0xD6); r2.font.italic = True
tf3 = textbox(s, Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.4))
p3 = tf3.paragraphs[0]; p3.alignment = PP_ALIGN.CENTER
r3 = p3.add_run()
r3.text = "Hero Yudo Martono · Iwan Syarif · Ferry Astika Saputra"
r3.font.size = Pt(18); r3.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p4 = tf3.add_paragraph(); p4.alignment = PP_ALIGN.CENTER
r4 = p4.add_run()
r4.text = "Politeknik Elektronika Negeri Surabaya (PENS)  —  Presentasi Metode ke Promotor"
r4.font.size = Pt(14); r4.font.color.rgb = RGBColor(0xCF, 0xE8, 0xD6)


# ============== SLIDE 2 — APA ITU FL ==============
s = add_slide()
title_bar(s, "Apa itu Federated Learning (FL)?",
          "Melatih satu model bersama tanpa memindahkan data mentah")
bullets(s, [
    "FL = beberapa organisasi (client) melatih SATU model bersama tanpa berbagi data mentah.",
    "Yang dipertukarkan hanya BOBOT model, bukan trafik/datanya — privasi tetap terjaga.",
    (0, "Alur satu ronde (diulang ~100x):"),
    (1, "Aggregator mengirim model global ke tiap client."),
    (1, "Tiap client melatih model pada datanya SENDIRI (lokal)."),
    (1, "Client mengirim balik pembaruan bobot."),
    (1, "Aggregator menggabungkan dengan FedAvg (rata-rata berbobot ukuran data)."),
], Inches(0.6), Inches(1.7), Inches(6.6), Inches(5.2), size=17)
img = os.path.join(FIG, "fig_fl_architecture.png")
if os.path.exists(img):
    s.shapes.add_picture(img, Inches(7.5), Inches(1.9), width=Inches(5.4))


# ============== SLIDE 3 — FL vs TERPUSAT ==============
s = add_slide()
title_bar(s, "FL (Terdistribusi) vs Terpusat: Kelebihan & Kekurangan",
          "FL mengejar performa setara terpusat TANPA mengorbankan privasi")
rows = [
    ("Aspek", "Federated (terdistribusi)", "Terpusat (centralized)"),
    ("Privasi data", "Terjaga — data tak pernah keluar organisasi", "Dilanggar — data harus digabung di satu tempat"),
    ("Kepatuhan regulasi", "Mendukung (GDPR, dll.)", "Sulit lintas-organisasi"),
    ("Biaya komunikasi", "Ringan (±300 KB/ronde, model kecil)", "Perlu transfer seluruh dataset"),
    ("Performa (MCC)", "Setara / sedikit unggul (0,85 near; 0,65 far)", "Acuan ideal (0,83 near; 0,62 far)"),
    ("Kelemahan utama", "Rentan non-IID, adversarial, sensitif protokol evaluasi", "Tidak boleh dipakai nyata (langgar privasi)"),
]
tbl_w = Inches(12.1); tbl_h = Inches(4.3)
table = s.shapes.add_table(len(rows), 3, Inches(0.6), Inches(1.8), tbl_w, tbl_h).table
table.columns[0].width = Inches(2.6)
table.columns[1].width = Inches(4.9)
table.columns[2].width = Inches(4.6)
for c in range(3):
    cell = table.cell(0, c)
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    para = cell.text_frame.paragraphs[0]
    run = para.add_run(); run.text = rows[0][c]
    run.font.size = Pt(14); run.font.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
for r_i in range(1, len(rows)):
    for c in range(3):
        cell = table.cell(r_i, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0xF2, 0xF6, 0xFB) if r_i % 2 else RGBColor(0xE4, 0xEC, 0xF5)
        para = cell.text_frame.paragraphs[0]
        run = para.add_run(); run.text = rows[r_i][c]
        run.font.size = Pt(12.5)
        run.font.bold = (c == 0)
        run.font.color.rgb = NAVY if c == 0 else RGBColor(0x22, 0x22, 0x22)


# ============== SLIDE 4 — TABEL REFERENSI FL-NIDS ==============
s = add_slide()
title_bar(s, "Lanskap Riset FL-NIDS Terkini (2020–2026)",
          "Mayoritas belum diuji lintas-dataset dan tanpa bukti deployment cloud — celah yang kami isi")
rows = [
    ("Framework", "Metode kunci", "Lintas-dataset?", "Cloud?"),
    ("Entente", "ACS + graph sketch", "Tidak", "Tidak"),
    ("FedAGRU", "attention + GRU-SVM", "Tidak", "Tidak"),
    ("FedSecIoT", "multi-Krum (Byzantine)", "Tidak", "Tidak"),
    ("FLAD", "adaptive selection (DDoS)", "Tidak", "Tidak"),
    ("HADA", "HADA + SHAP + DP", "Tidak", "Edge"),
    ("Ensemble+XAI", "CNN+LSTM+Transformer", "Multi", "Tidak"),
    ("Hu et al.", "federated meta-learning", "Parsial", "Tidak"),
]
table = s.shapes.add_table(len(rows), 4, Inches(0.6), Inches(1.9), Inches(12.1), Inches(4.3)).table
table.columns[0].width = Inches(2.7)
table.columns[1].width = Inches(5.0)
table.columns[2].width = Inches(2.4)
table.columns[3].width = Inches(2.0)
for c in range(4):
    cell = table.cell(0, c)
    cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
    run = cell.text_frame.paragraphs[0].add_run(); run.text = rows[0][c]
    run.font.size = Pt(14); run.font.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
for r_i in range(1, len(rows)):
    for c in range(4):
        cell = table.cell(r_i, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0xF2, 0xF6, 0xFB) if r_i % 2 else RGBColor(0xE4, 0xEC, 0xF5)
        run = cell.text_frame.paragraphs[0].add_run(); run.text = rows[r_i][c]
        run.font.size = Pt(13)
        if c in (2, 3) and rows[r_i][c] == "Tidak":
            run.font.color.rgb = RED
        else:
            run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        run.font.bold = (c == 0)
note = textbox(s, Inches(0.6), Inches(6.4), Inches(12.1), Inches(0.8))
rn = note.paragraphs[0].add_run()
rn.text = ("Kolom 'Lintas-dataset?' dan 'Cloud?' adalah dua dimensi yang jarang dipenuhi "
           "literatur — justru di sinilah kontribusi kami.")
rn.font.size = Pt(13); rn.font.italic = True; rn.font.color.rgb = GREY


# ============== SLIDE 5 — DESAIN PERCOBAAN ==============
s = add_slide()
title_bar(s, "Desain Percobaan",
          "Sumbu jarak domain + protokol evaluasi bebas-kebocoran di testbed AWS")
bullets(s, [
    (0, "Sumbu JARAK DOMAIN (ide inti):", GREEN),
    (1, "Near-domain: CIC2017 + CIC2018 (ekstraktor sama -> 76 fitur)."),
    (1, "Far-domain: CIC2018 + UNSW-NB15 (ekstraktor beda -> 9 fitur)."),
    (0, "Tiga model dibandingkan:", GREEN),
    (1, "Federated vs Centralized vs Local-only (per client)."),
    (0, "Protokol evaluasi BEBAS-KEBOCORAN (kontribusi):", GREEN),
    (1, "z-score dihitung lokal per client; test dinormalisasi dgn statistik pemiliknya."),
    (0, "Enam klaim diuji (R1-R6):", GREEN),
    (1, "FedAvg/FedProx, non-IID, cross-dataset, biaya, evasion, adversarial training."),
    (0, "Testbed: AWS (EC2 + SageMaker), multi-seed, semua angka dari run nyata.", NAVY),
], Inches(0.6), Inches(1.7), Inches(7.1), Inches(5.4), size=16, gap=4)
img = os.path.join(FIG, "fig_feature_alignment.png")
if os.path.exists(img):
    s.shapes.add_picture(img, Inches(7.9), Inches(2.0), width=Inches(5.0))


def simple_table(slide, rows, left, top, width, height, col_widths=None,
                 header_color=NAVY, font=12.5, red_if=None):
    nr, nc = len(rows), len(rows[0])
    table = slide.shapes.add_table(nr, nc, left, top, width, height).table
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w
    for c in range(nc):
        cell = table.cell(0, c); cell.fill.solid(); cell.fill.fore_color.rgb = header_color
        run = cell.text_frame.paragraphs[0].add_run(); run.text = rows[0][c]
        run.font.size = Pt(font + 1); run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for r_i in range(1, nr):
        for c in range(nc):
            cell = table.cell(r_i, c); cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xF2, 0xF6, 0xFB) if r_i % 2 else RGBColor(0xE4, 0xEC, 0xF5)
            run = cell.text_frame.paragraphs[0].add_run(); run.text = rows[r_i][c]
            run.font.size = Pt(font)
            run.font.bold = (c == 0)
            if red_if and red_if(r_i, c, rows[r_i][c]):
                run.font.color.rgb = RED
            else:
                run.font.color.rgb = NAVY if c == 0 else RGBColor(0x22, 0x22, 0x22)
    return table


# ============== SLIDE 6 — DATASET & PARTISI ==============
s = add_slide()
title_bar(s, "Dataset & Partisi",
          "Tiga dataset benchmark; jumlah fitur ditentukan oleh irisan ekstraktor")
bullets(s, [
    (0, "Tiga dataset, dua konfigurasi:", GREEN),
    (1, "Near-domain: CIC-IDS2017 + CSE-CIC-IDS2018 (keduanya CICFlowMeter)."),
    (1, "Far-domain: CSE-CIC-IDS2018 + UNSW-NB15 (CICFlowMeter vs Argus/Bro)."),
    (0, "Jumlah fitur = konsekuensi irisan ekstraktor, bukan pilihan desain:", GREEN),
    (1, "Ekstraktor SAMA -> 76 fitur bersama (near)."),
    (1, "Ekstraktor BEDA -> hanya 9 fitur yang berpadanan 1:1 (far)."),
    (0, "Label biner: benign = 0, attack = 1. Split 70/30, train di-subsample ~100k.", NAVY),
], Inches(0.6), Inches(1.7), Inches(6.4), Inches(3.1), size=16, gap=4)
rows = [
    ("Client (split)", "Total", "Attack", "Rasio"),
    ("CIC2017 train", "100.000", "19.261", "0,193"),
    ("CIC2018 train", "100.000", "23.829", "0,238"),
    ("CIC2018 (far) train", "100.000", "16.929", "0,169"),
    ("UNSW (far) train", "82.332", "45.332", "0,551"),
]
simple_table(s, rows, Inches(0.6), Inches(5.0), Inches(7.0), Inches(2.0),
             col_widths=[Inches(2.8), Inches(1.5), Inches(1.5), Inches(1.2)], font=12)
img = os.path.join(FIG, "fig_feature_alignment.png")
if os.path.exists(img):
    s.shapes.add_picture(img, Inches(7.8), Inches(1.9), width=Inches(5.1))


# ============== SLIDE 7 — MODEL (CONTROLLED BACKBONE) ==============
s = add_slide()
title_bar(s, "Model: MLP Ringan sebagai Controlled Backbone",
          "Dangkal SENGAJA — bukan untuk memaksimalkan akurasi, tapi untuk mengisolasi efek")
bullets(s, [
    (0, "Arsitektur: MLP d -> 128 -> 64 -> 1 (ReLU, sigmoid, BCE); d = 9 (far) / 76 (near).",),
    (0, "Mengapa sengaja DANGKAL?", GREEN),
    (1, "Payload kecil (±76,8 KB/unggahan) -> cocok cross-silo & jadi objek ukur biaya (R4)."),
    (1, "Mengisolasi efek yang diteliti (agregasi, non-IID, cross-domain, pergeseran skor)"),
    (2, "dari dinamika model besar seperti overfitting representasi laten."),
    (1, "Arsitektur dikunci identik di semua client & skenario -> perbedaan terukur"),
    (2, "dapat diatribusikan ke faktor yang diuji, bukan ke kapasitas model."),
    (0, "Catatan (Threats to Validity):", NAVY),
    (1, "Uji arsitektur lebih dalam (1D-CNN, transformer) = arah lanjutan."),
], Inches(0.6), Inches(1.7), Inches(12.1), Inches(5.2), size=17, gap=6)


# ============== SLIDE 8 — PROTOKOL BEBAS-KEBOCORAN ==============
s = add_slide()
title_bar(s, "Protokol Evaluasi Bebas-Kebocoran (Kontribusi Utama)",
          "Cara normalisasi data uji MENENTUKAN kesimpulan — sering terlewat di literatur")
bullets(s, [
    (0, "Masalah: statistik normalisasi (z-score) bisa 'bocor' antar-client.", RED),
    (0, "Protokol kami (bebas-kebocoran):", GREEN),
    (1, "z-score dihitung LOKAL dari data latih tiap client (tak pernah dibagikan)."),
    (1, "Test set tiap client dinormalisasi dgn statistik latih PEMILIKNYA (konsisten training)."),
    (0, "Bukti dampaknya (model federated yang SAMA):", GREEN),
    (1, "Protokol bebas-kebocoran: MCC 0,65 (far) / 0,85 (near)."),
    (1, "Evaluasi tak konsisten (pooled): MCC anjlok 0,23 (far) / 0,54 (near)."),
    (0, "Pesan: 'FL lintas-dataset runtuh' bisa jadi ARTEFAK evaluasi, bukan sifat FL.", NAVY),
], Inches(0.6), Inches(1.7), Inches(12.1), Inches(5.2), size=17, gap=6)


# ============== SLIDE 9 — EKSPERIMEN ADVERSARIAL ==============
s = add_slide()
title_bar(s, "Eksperimen Adversarial",
          "Serangan evasion + pertahanan adversarial training, pada ruang fitur (worst-case)")
bullets(s, [
    (0, "Serangan evasion (R5): FGSM, PGD, JSMA.", GREEN),
    (1, "Perturbasi di-clip ke persentil 1-99 tiap fitur (ruang z-score lokal)."),
    (1, "Threat model: ruang-fitur sebagai batas-atas worst-case,"),
    (2, "BUKAN packet-level (aliran belum tentu bisa dikirim nyata) — disengaja."),
    (0, "Pertahanan (R6): adversarial training (50% sampel diganti contoh FGSM).", GREEN),
    (1, "Efektif di CIC (recall 0,48 -> 0,91) tetapi MERUSAK UNSW (recall 0,70 -> 0,10)."),
    (1, "Sebab: pergeseran batas keputusan seragam ke arah 'attack' —"),
    (2, "menolong satu domain, melukai domain lain (konflik arah antar-domain)."),
    (0, "Implikasi: pertahanan adversarial harus SADAR-DOMAIN, bukan statis.", NAVY),
], Inches(0.6), Inches(1.7), Inches(12.1), Inches(5.2), size=16, gap=5)


# ============== SLIDE 10 — TESTBED AWS & REPRODUCIBILITY ==============
s = add_slide()
title_bar(s, "Testbed AWS & Reproducibility",
          "Semua angka dari eksekusi NYATA, bukan dikarang")
bullets(s, [
    (0, "Infrastruktur:", GREEN),
    (1, "Far-domain (R3/R5/R6): 3 EC2 t3.medium (1 aggregator + 2 client), bobot via S3."),
    (1, "Near-domain & sweep non-IID: simulasi FL terkontrol di SageMaker (kode identik)."),
    (0, "Reproducibility:", GREEN),
    (1, "Multi-seed {13,42,101,202,303}; dilaporkan mean +/- CI95."),
    (1, "Partisi data tetap -> variasi hanya dari keacakan training."),
    (1, "Biaya cloud kecil: ±300 KB & ±16 detik per ronde; teardown tiap sesi."),
    (0, "Seluruh skrip, notebook, dan konfigurasi cloud dirilis untuk direproduksi.", NAVY),
], Inches(0.6), Inches(1.7), Inches(12.1), Inches(5.2), size=17, gap=6)


# ============== SLIDE 11 — HASIL PERCOBAAN (TABEL) ==============
s = add_slide()
title_bar(s, "Hasil Percobaan (Ringkasan Terukur)",
          "Semua angka = rata-rata multi-seed dari eksekusi nyata; metrik utama MCC")
rows = [
    ("Klaim / uji", "Hasil terukur (MCC / metrik)", "Bertahan?"),
    ("R1 FedProx > FedAvg", "0,571 vs 0,572 (tak beda bermakna)", "Tidak"),
    ("R2 non-IID menurunkan FL", "CIC turun (0,39 @α0,1); UNSW datar", "Bergantung domain"),
    ("R3 cross-dataset FL sulit", "federated 0,65 vs centralized 0,62 (far)", "Tidak"),
    ("R3 near-domain", "federated 0,85 vs centralized 0,83", "FL unggul"),
    ("Local-only (lintas-domain)", "0,23 / 0,01 (far); 0,43 / 0,60 (near)", "Gagal transfer"),
    ("R4 biaya cloud", "±300 KB & ±16 detik per ronde", "Terukur"),
    ("R5 evasion (PGD @ε0,1)", "ASR 0,91; MCC 0,65 -> 0,04", "Ya (rapuh)"),
    ("R6 adversarial training", "CIC: recall 0,48->0,91; UNSW: 0,70->0,10", "Bergantung domain"),
    ("Protokol evaluasi (bocor vs tidak)", "0,65/0,85  vs  0,23/0,54", "Sensitif protokol"),
]
simple_table(s, rows, Inches(0.5), Inches(1.75), Inches(12.3), Inches(5.1),
             col_widths=[Inches(4.0), Inches(5.6), Inches(2.7)], font=12.5,
             red_if=lambda r, c, v: c == 2 and v in ("Tidak", "Gagal transfer"))
note = textbox(s, Inches(0.5), Inches(6.95), Inches(12.3), Inches(0.4))
rn = note.paragraphs[0].add_run()
rn.text = ("Angka kunci: federated menang di kedua jarak domain; local-only selalu gagal "
           "menyeberang; kesimpulan sensitif pada protokol evaluasi.")
rn.font.size = Pt(12); rn.font.italic = True; rn.font.color.rgb = GREY


# ============== SLIDE 12 — HASIL (VISUAL) ==============
s = add_slide()
title_bar(s, "Hasil Percobaan (Visual)",
          "Federated unggul di near & far; local-only gagal transfer; non-IID bergantung domain")
far = os.path.join(FIG, "fig_results.png")
near = os.path.join(FIG, "fig_neardomain.png")
if os.path.exists(far):
    s.shapes.add_picture(far, Inches(0.5), Inches(2.0), width=Inches(6.1))
if os.path.exists(near):
    s.shapes.add_picture(near, Inches(6.9), Inches(2.0), width=Inches(6.0))
cap = textbox(s, Inches(0.5), Inches(5.9), Inches(12.3), Inches(1.0))
p = cap.paragraphs[0]
r = p.add_run(); r.text = "Kiri: far-domain (CIC2018 + UNSW, 9 fitur)."
r.font.size = Pt(13); r.font.color.rgb = GREY
p2 = cap.add_paragraph()
r2 = p2.add_run(); r2.text = "Kanan: near-domain (CIC2017 + CIC2018, 76 fitur)."
r2.font.size = Pt(13); r2.font.color.rgb = GREY
p3 = cap.add_paragraph()
r3 = p3.add_run()
r3.text = ("Batang hijau (federated) >= batang abu (centralized), dan jauh di atas merah/biru "
           "(local-only) — manfaat federasi nyata di kedua jarak domain.")
r3.font.size = Pt(13); r3.font.italic = True; r3.font.color.rgb = NAVY


# ============== SLIDE 13 — KESIMPULAN: CONFERENCE vs JURNAL ==============
s = add_slide()
title_bar(s, "Kesimpulan: Cakupan Conference (ISRITI) vs Jurnal (JOIN)",
          "Jurnal = isi konferensi + material baru (>50%) di sepanjang sumbu jarak domain")
rows = [
    ("Fitur / cakupan", "Conference (ISRITI)", "Jurnal (JOIN)"),
    ("Verifikasi 6 klaim (R1-R6)", "Ya (far-domain)", "Ya (dirangkum)"),
    ("Far-domain (9 fitur)", "Ya", "Ya"),
    ("Near-domain (76 fitur)", "Tidak", "Ya (BARU)"),
    ("Gradasi jarak domain", "Tidak", "Ya (BARU)"),
    ("Protokol bebas-kebocoran", "Sebagai temuan", "Sebagai kontribusi"),
    ("Sebab degradasi UNSW", "1 kalimat ringkas", "Analisis penuh + gambar"),
    ("Jumlah halaman", "6 (batas)", "Penuh (jurnal)"),
]
simple_table(s, rows, Inches(1.0), Inches(1.9), Inches(11.3), Inches(4.6),
             col_widths=[Inches(4.3), Inches(3.5), Inches(3.5)], font=13,
             red_if=lambda r, c, v: v == "Tidak")
note = textbox(s, Inches(1.0), Inches(6.7), Inches(11.3), Inches(0.6))
rn = note.paragraphs[0].add_run()
rn.text = ("Material baru jurnal: near-domain, sumbu jarak domain, protokol sebagai kontribusi, "
           "dan investigasi sebab degradasi UNSW.")
rn.font.size = Pt(13); rn.font.italic = True; rn.font.color.rgb = GREY


prs.save(OUT)
print("Tersimpan:", OUT, "| slides:", len(prs.slides._sldIdLst))
