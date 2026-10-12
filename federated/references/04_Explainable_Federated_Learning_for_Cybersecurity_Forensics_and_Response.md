# 03. Explainable Federated Learning for Cybersecurity Forensics and Response

## Judul dalam Bahasa Indonesia
Pembelajaran Federated yang Dapat Dijelaskan untuk Forensik Keamanan Siber dan Respon Insiden

## English Title
Explainable Federated Learning for Cybersecurity Forensics and Response

## 1. Pendahuluan Judul
Dalam keamanan siber, model AI tidak hanya harus akurat dalam mendeteksi ancaman, tetapi juga harus dapat dijelaskan ketika tim keamanan perlu memahami konteks insiden. Ini menjadi lebih penting dalam lingkungan federated learning, di mana data berada di banyak node yang berbeda. Model yang dihasilkan dari pembelajaran terdistribusi sering kali sangat kompleks dan sulit dipahami, terutama ketika keputusan model berdampak pada proses forensik dan respon insiden.

Masalah interpretabilitas menjadi krusial karena tim keamanan membutuhkan bukti yang dapat dipahami untuk menjelaskan mengapa suatu aktivitas ditandai sebagai ancaman, dari mana asalnya, dan tindakan yang paling tepat untuk diambil. Di sisi lain, pengumpulan data yang terdistribusi dan sensitif membuat kebutuhan akan solusi explainable FL menjadi semakin nyata.

Penelitian ini berfokus pada pengembangan explainable federated learning (XFL) yang dapat membantu proses forensik siber dan response automation. Tujuan utama adalah menjembatani kesenjangan antara performa model dan kemampuan manusia untuk memahami, memvalidasi, dan menindaklanjuti keputusan model.

## 2. Ideal Abstrak
Federated Learning (FL) telah menjadi pendekatan penting untuk membangun model keamanan siber tanpa memindahkan data sensitif. Namun, model yang dihasilkan dari FL sering kali beroperasi sebagai black box, sehingga sulit dipahami oleh analis keamanan. Kondisi ini menimbulkan tantangan dalam forensik siber, investigasi insiden, dan pengambilan keputusan respon yang cepat.

Penelitian ini mengangkat kebutuhan akan explainable federated learning (XFL) sebagai solusi untuk mengintegrasikan interpretabilitas dalam lingkungan pembelajaran terdistribusi. Fokus utama meliputi mekanisme interpretasi seperti feature importance, SHAP-based explanation, client-level contribution analysis, dan ekstraksi rule dari model federated yang sudah dilatih.

Hasil kajian menunjukkan bahwa XFL memiliki potensi besar untuk meningkatkan kepercayaan, auditabilitas, dan efektivitas operasi keamanan. Dengan kemampuan menjelaskan keputusan model, tim keamanan dapat mengidentifikasi alasan di balik alert, mengevaluasi kontribusi masing-masing klien, dan memperkuat proses incident response. Namun, interpretabilitas tetap menghadapi trade-off dengan akurasi dan biaya komputasi.

## 3. Introduction
Forensik siber menuntut bukti yang jelas, konteks kejadian, dan mekanisme yang dapat dipertanggungjawabkan. Ketika model AI digunakan untuk menganalisis aktivitas yang mencurigakan, hasil dari model tersebut harus dapat dijelaskan agar manusia bisa menilai apakah keputusan tersebut valid atau tidak.

Dalam lingkungan federated learning, kejelasan ini menjadi lebih sulit karena data tidak dipusatkan. Model dibangun dari kontribusi banyak klien, masing-masing dengan perspektif dan pola data yang berbeda. Sedangkan tim keamanan biasanya membutuhkan explanation yang dapat dikaitkan dengan event, sumber ancaman, dan perubahan perilaku sistem.

Sebagai contoh, ketika model mengklasifikasikan lalu lintas jaringan sebagai malicious, analis keamanan perlu tahu fitur apa yang paling memengaruhi keputusan tersebut. Apakah itu protokol yang unik, pola koneksi, volume transfer data, atau aktivitas endpoint yang abnormal? Tanpa menjelaskan hal itu, keputusan model sulit digunakan untuk investigasi forensik atau koordinasi respon.

Karena itu, explainable federated learning menjadi area penting. XFL tidak hanya meningkatkan trust pada model, tetapi juga memfasilitasi audit, compliance, dan respons yang lebih cepat dalam situasi krisis keamanan.

## 4. Related Work
Riset tentang explainable AI (XAI) sudah berkembang dalam berbagai domain, termasuk deteksi intrusi dan pemantauan keamanan. Teknik seperti SHAP, LIME, feature attribution, dan attention-based explanation banyak digunakan untuk memaparkan alasan model. Namun, kebanyakan pendekatan ini dikembangkan untuk model tunggal atau model pusat, bukan untuk model yang dibangun dari data terdistribusi.

Dalam konteks FL, beberapa studi mulai membahas interpretabilitas model gabungan, terutama untuk melihat kontribusi klien atau fitur umum yang paling berpengaruh. Namun, masih sedikit penelitian yang secara khusus menghubungkan interpretabilitas dengan kebutuhan forensik dan response automation dalam keamanan siber.

Masalah ini sangat relevan karena keamanan siber bukan hanya tentang prediksi, melainkan juga tentang keputusan tindakan. Ketika model dapat dijelaskan, tim keamanan dapat memvalidasi hasil, membangun timeline kejadian, dan menyusun langkah mitigasi dengan lebih percaya diri. Kesenjangan inilah yang menjadi fokus utama riset ini.

## 5. Method
Penelitian ini menggunakan metodologi review dan analisis konseptual untuk mengeksplorasi explainable FL dalam konteks forensik keamanan siber. Langkah-langkah yang dilakukan adalah:

1. Mengidentifikasi kebutuhan interpretabilitas dalam keperluan keamanan dan incident response.
2. Menganalisis mekanisme XAI yang kompatibel dengan federated learning.
3. Menilai kemampuan teknik interpretasi untuk menjelaskan keputusan model secara global dan lokal.
4. Menghubungkan hasil explanation dengan kebutuhan forensik, audit, dan tindakan mitigasi.
5. Menentukan hambatan utama, termasuk trade-off antara interpretabilitas, performa, dan komunikasi.

Metode ini dipilih agar hasil kajian dapat langsung berkontribusi pada perancangan model yang lebih dapat dipahami dan lebih berguna bagi praktisi keamanan.

## 6. Result and Discussion
Hasil kajian menunjukkan bahwa interpretabilitas dalam FL sangat penting, terutama ketika model digunakan untuk mendukung keputusan operasional. Ketika model dapat menjelaskan peran fitur-fitur utama, seperti IP abnormal, aktivitas login baru, atau transfer data berlebihan, tim keamanan dapat menghubungkan hasil model dengan konteks kejadian yang sebenarnya.

Dalam praktiknya, explainable FL membantu dua hal utama: audit dan respon cepat. Pertama, model dapat dijadikan bukti yang lebih terdokumentasi untuk audit internal maupun kepatuhan regulasi. Kedua, tim keamanan dapat mengambil tindakan yang lebih tepat karena alasan keputusan model jelas dan terukur. Keduanya sangat penting dalam lingkungan yang rawan insiden.

Namun, interpretabilitas tidak datang tanpa trade-off. Proses analisis explanation mungkin menambah biaya komputasi, menurunkan kecepatan inferensi, atau memerlukan representasi yang lebih sederhana. Karena itu, desain XFL harus menyeimbangkan kebutuhan keamanan, efisiensi, dan kemampuan menjelaskan keputusan kepada manusia.

## 7. Conclusion
Explainable Federated Learning menjadi solusi yang sangat relevan untuk menjembatani kebutuhan keamanan siber modern dengan kebutuhan auditabilitas dan human-centered response. Dalam lingkungan di mana data tersebar dan sensitif, model tidak hanya perlu akurat tetapi juga mampu menjelaskan alasan keputusan kepada tim keamanan.

Penelitian ini menegaskan bahwa XFL berpotensi menjadi komponen penting dalam forensik siber. Dengan mekanisme interpretasi yang tepat, model dapat mendukung investigasi insiden, meningkatkan kepercayaan pengguna, dan mempercepat respon terhadap ancaman. Masa depan penelitian perlu fokus pada cara membuat XFL lebih praktis, stabil, dan terintegrasi dengan proses keamanan real-world.

## 8. Referensi
1. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). Why Should I Trust You?: Explaining the Predictions of Any Classifier.
2. Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions.
3. Kairouz, P., et al. (2021). Advances and Open Problems in Federated Learning.
4. Li, T., et al. (2020). Federated Optimization in Heterogeneous Networks.
5. Sarker, I. H. (2021). Machine learning for cybersecurity: A review.
6. Chio, C., & Freeman, D. (2018). Machine Learning and Security.
7. Shokri, R., & Shmatikov, V. (2015). Privacy-preserving deep learning.
8. Bagdasaryan, E., et al. (2020). How to Backdoor Federated Learning.
9. Yang, Q., et al. (2019). Federated Learning.
10. Gunning, D., & Aha, D. (2019). DARPA’s Explainable AI Program.
