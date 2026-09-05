# LAPORAN PENILAIAN PEER REVIEWER (PEER REVIEW REPORT)
**Jurnal Target:** International Journal of Electrical and Computer Engineering (IJECE) (Scopus Q3 / Sinta 1)  
**Judul Manuskrip:** Penguatan Ketangguhan NIDS dengan Reduksi Fitur Berbasis XGBoost Gain-based Importance melalui Adversarial Training terhadap Serangan Evasion Saliency Map  
**Bahasa Manuskrip:** Bahasa Indonesia (Draft Awal)  
**Rekomendasi Keputusan:** **Major Revision (Revisi Mayor)**

---

## I. RINGKASAN UMUM (GENERAL OVERVIEW)
Manuskrip ini mengusulkan sebuah pendekatan terintegrasi untuk memperkuat ketangguhan *Network Intrusion Detection System* (NIDS) berbasis *Extreme Gradient Boosting* (XGBoost) terhadap serangan *evasion* menggunakan metode *Saliency Map*. Kontribusi utama yang ditawarkan mencakup:
1. Reduksi fitur dari 78 menjadi 10 fitur menggunakan metrik *XGBoost Gain-based Importance*.
2. Implementasi *Adversarial Training* menggunakan formulasi optimasi Min-Max untuk merestrukturisasi batas keputusan (*decision boundary*) model.
3. *Robustness Ablation Study* untuk menentukan *sweet spot* dimensi fitur (terpilih konfigurasi Top-10).
4. Validasi pada lalu lintas jaringan nyata (*real-traffic*) di lingkungan awan Amazon Web Services (AWS) menggunakan node *Attacker*, *Target*, dan *Analyzer* berbasis pustaka *NFStream*.

Secara keseluruhan, manuskrip ini ditulis dengan sangat terstruktur, memiliki alur metodologi yang jelas, dan menyertakan pembuktian empiris yang kaya. Validasi di lingkungan nyata (*real-traffic*) merupakan nilai tambah yang luar biasa karena sangat jarang dilakukan dalam literatur NIDS berbasis adversarial. Namun, terdapat beberapa celah metodologis dan teknis krusial yang wajib diperbaiki sebelum manuskrip ini layak diterjemahkan ke dalam bahasa Inggris dan dipertimbangkan untuk publikasi di jurnal kelas dunia selevel IJECE.

---

## II. KEKUATAN UTAMA MANUSKRIP (KEY STRENGTHS)
1. **Validasi Real-Traffic yang Komprehensif (Bab 3.8):** Desain pengujian menggunakan infrastruktur AWS Cloud nyata dengan VPC terisolasi dan ekstraksi aliran menggunakan *NFStream* memberikan kontribusi praktis yang sangat tinggi bagi komunitas keamanan siber. Hal ini membuktikan komitmen penulis terhadap penerapan praktis di dunia nyata.
2. **Robustness Ablation Study (Bab 3.6):** Eksplorasi trade-off antara efisiensi memori (reduksi ukuran biner model hingga 86% menjadi 84 KB) dengan ketahanan klasifikasi (mempertahankan MCC S4 = 0,9953) disajikan secara sistematis dan berhasil membuktikan penemuan *sweet spot* pada konfigurasi Top-10.
3. **Penyajian Metrik Matthews Correlation Coefficient (MCC) sebagai Metrik Utama (Bab 2.6.2):** Keputusan menggunakan MCC sangat tepat mengingat dataset *CSE-CIC-IDS2018* mengalami ketidakseimbangan kelas (*class imbalance*) yang sangat ekstrem. Penggunaan visualisasi *Radar Chart* multi-metrik pada Gambar 14 juga memperkaya analisis performa secara holistik.
4. **Analisis Sensitivitas Gradien Lokal (Saliency Map - Bab 3.2.2):** Analisis perbedaan antara *Global Importance* (XGBoost Gain) dan *Local Sensitivity* (Saliency Map Gradient) sangat mendalam dan berhasil mengidentifikasi bahwa fitur *Init Fwd Win Byts* merupakan fitur yang paling rentan terhadap serangan manipulasi lokal, meskipun secara global hanya menduduki peringkat ke-10 pada skor Gain.

---

## III. CATATAN PERBAIKAN UTAMA (MAJOR REVISIONS - WAJIB DIPERBAIKI)

### 1. Kredibilitas dan Solusi terhadap Kinerja Real-Traffic (RT-S1 s.d. RT-S4)
*   **Masalah:** Pada Tabel 8, dilaporkan bahwa nilai MCC absolut pada trafik nyata (*real-traffic*) AWS menurun drastis dibandingkan hasil *offline*:
    *   RT-S1 (Base + Murni) jatuh menjadi **0,164** (dari 0,9351).
    *   RT-S3 (Robust + Murni) jatuh menjadi **0,339** (dari 0,9347).
    *   RT-S4 (Robust + Evasion) jatuh menjadi **0,389** (dari 0,9953).
    Secara praktis, nilai MCC di bawah 0,4 menunjukkan korelasi yang sangat lemah dan performa klasifikasi yang buruk, sehingga sistem ini belum dapat digunakan secara andal pada lingkungan nyata. Meskipun kejujuran penulis dalam menyajikan penurunan ini sangat dihargai, sekadar menyajikan keterbatasan tanpa menawarkan solusi konkret menurunkan nilai ilmiah dari paper tingkat IJECE.
*   **Rekomendasi Revisi:** Penulis harus menambahkan sub-bab diskusi khusus di Bab 3.8.3 atau Bab 4.2 yang menguraikan **solusi praktis dan langkah konkret** untuk mengatasi masalah *feature mismatch* dan perbedaan karakteristik lingkungan (seperti perbedaan ukuran *TCP window* dan z-score mismatch). Solusi yang perlu didiskusikan antara lain:
    1.  **Kalibrasi Ekstraktor (Extractor Calibration):** Penyesuaian konfigurasi *NFStream* (melalui plugin kustom) agar secara matematis menyelaraskan ekstraksi fitur (misal: *Fwd Seg Size Min*) dengan standar definisi *CICFlowMeter*.
    2.  **Domain Adaptation / Transfer Learning:** Penerapan teknik adaptasi domain untuk melatih ulang lapisan atas model menggunakan sebagian kecil trafik nyata terlabel dari lingkungan AWS sebelum diterapkan sepenuhnya.
    3.  **Pelatihan Berbasis Multi-Extractor:** Memasukkan variabilitas data ekstraksi dari beberapa pustaka berbeda (*CICFlowMeter*, *NFStream*, *Zeek*) ke dalam dataset pelatihan awal guna meningkatkan ketahanan model terhadap perbedaan lingkungan ekstraksi.

### 2. Inkonsistensi Matematis: Sifat Non-Differentiable dari XGBoost
*   **Masalah:** Pada Bab 2.3, penulis memformulasikan pembangkitan sampel adversarial menggunakan gradien matematis *Saliency Map* (Persamaan 1 dan 2) yang berbasis turunan parsial terhadap loss:
    $$\nabla_x L(\theta, x, y) = \left[ \frac{\partial L}{\partial x_1}, \dots \right]^T$$
    Namun, **XGBoost** adalah model berbasis pohon keputusan (*decision trees*) yang secara intrinsik bersifat tidak kontinu dan tidak dapat diturunkan (*non-differentiable*). Batas keputusan pohon berupa fungsi tangga (*step functions*), sehingga nilai gradien inputnya adalah **nol hampir di seluruh tempat** (atau tidak terdefinisi pada batas split). Akibatnya, kalkulus standar menggunakan turunan parsial langsung tidak dapat diaplikasikan pada model XGBoost asli.
*   **Rekomendasi Revisi:** Penulis wajib mengklarifikasi secara teknis dan matematis bagaimana nilai gradien $\nabla_x L(\theta, x, y)$ tersebut dihitung pada XGBoost dalam implementasi kode mereka:
    1.  Apakah mereka melatih sebuah **model pengganti yang diferensiabel (*differentiable surrogate model*)** seperti Neural Network untuk memperkirakan gradien XGBoost (skema *black-box/transfer attack*)? Jika ya, sebutkan arsitektur surrogate model tersebut.
    2.  Atau apakah mereka menggunakan algoritma serangan adversarial khusus pohon keputusan yang tidak memerlukan gradien langsung (misalnya: *Tree-Based Evasion Attacks*, *Boundary Attack*, atau perkakas dari pustaka *Adversarial Robustness Toolbox - ART*)?
    3.  Tuliskan modifikasi matematis atau penjelasan komputasi ini dengan jelas pada Bab 2.3 untuk menjaga integritas kebenaran matematis manuskrip.

### 3. Batasan Evaluasi Serangan Evasion: White-Box vs. Transfer Attack (Black-Box)
*   **Masalah:** Di Bab 3.4.3 (Poin 4), penulis menjelaskan bahwa nilai MCC S4 (0,9953) yang lebih tinggi dari S1 disebabkan karena sampel adversarial dibangkitkan menggunakan gradien model baseline—bukan model robust itu sendiri. Ini merupakan skema **Transfer Attack (Black-Box)**. 
    Menguji ketangguhan model pertahanan hanya terhadap serangan transfer dari model baseline memberikan estimasi ketahanan yang terlalu optimis (*overestimated*). Model robust harus dievaluasi di bawah skenario **White-Box Attack**, di mana penyerang membangkitkan sampel adversarial secara langsung menggunakan gradien dari model robust itu sendiri. 
*   **Rekomendasi Revisi:** 
    1.  Penulis harus menjelaskan apakah mereka telah melakukan evaluasi *White-Box* pada model robust (di mana perturbasi dibangkitkan menggunakan model robust itu sendiri). 
    2.  Jika ya, sajikan nilai metriknya di Tabel 6. Jika tidak, penulis wajib menyatakan batasan ini secara eksplisit pada Bab 4 (Hasil dan Pembahasan) serta Bab 5 (Kesimpulan), dengan menekankan bahwa model robust saat ini baru divalidasi terhadap *static transfer attacks* dan ketangguhannya di bawah skenario *adaptive white-box attacks* perlu dievaluasi pada penelitian masa depan (*future work*).

---

## IV. CATATAN PERBAIKAN MINOR (MINOR REVISIONS)
1.  **Format Istilah Asing:** Masih banyak istilah teknis bahasa Inggris di dalam draf bahasa Indonesia yang belum dicetak miring (*italic*). Contoh: *stratified sampling* [10], *zero-variance* [11], *decision boundary* [20], *extreme gradient boosting* [22], *overfitting* [22], *confusion matrix* [30], dll. Mohon disesuaikan sesuai Pedoman Umum Ejaan Bahasa Indonesia (PUEBI).
2.  **Keterkaitan Gambar 14:** Gambar 14 (Radar Chart Multi-Metrik) menyajikan ringkasan visual yang sangat indah, tetapi pembahasannya di teks Bab 3.7 masih sangat singkat. Tambahkan 2-3 kalimat penjelasan di Bab 3.7 yang merujuk langsung ke Gambar 14 untuk menjelaskan arti perluasan poligon model robust dibandingkan penyusutan poligon model baseline di bawah serangan.
3.  **Konsistensi Penulisan Matematika:** Pastikan penggunaan lambang variabel dalam teks konsisten dengan rumus. Misalnya, penulisan lambang epsilon ($\epsilon$) pada teks pastikan menggunakan format LaTeX yang sama dengan rumus agar rapi.
4.  **Format Pustaka/Referensi:** Referensi pada bagian akhir sudah sangat baik dan mutakhir, tetapi pastikan seluruh nama jurnal atau prosiding ditulis secara lengkap dan konsisten mengikuti format standar **IEEE**.

---

## V. KESIMPULAN REVIEWER (REVIEWER DECISION)
Naskah ini sangat menjanjikan dan memiliki kontribusi praktis yang kuat melalui validasi *real-traffic* awan AWS. Rekomendasi saya saat ini adalah **Major Revision (Revisi Mayor)**. Penulis harus terlebih dahulu merevisi manuskrip bahasa Indonesia mereka untuk menjawab tiga catatan mayor di atas (kinerja *real-traffic* yang rendah, kejelasan matematis gradien XGBoost, dan kejelasan batasan evaluasi *white-box*). 

Setelah naskah versi Bahasa Indonesia ini direvisi dengan matang dan dinyatakan diterima secara ilmiah, barulah penulis dapat melanjutkannya ke tahap penerjemahan bahasa Inggris akademik sebelum submisi resmi ke IJECE.
