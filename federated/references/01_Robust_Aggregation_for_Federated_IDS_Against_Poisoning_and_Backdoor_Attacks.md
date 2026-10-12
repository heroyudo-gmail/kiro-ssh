# 01. Robust Aggregation for Federated IDS Against Poisoning and Backdoor Attacks

## Judul dalam Bahasa Indonesia
Agregasi yang Tangguh untuk Intrusion Detection System Federated Melawan Serangan Poisoning dan Backdoor

## English Title
Robust Aggregation for Federated IDS Against Poisoning and Backdoor Attacks

## 1. Pendahuluan Judul
Sistem deteksi intrusi berbasis Federated Learning (FL) telah menjadi arah penting dalam keamanan siber karena mampu melatih model secara kolaboratif tanpa memindahkan data sensitif antar organisasi. Namun, kemampuan ini tidak otomatis membuat sistem aman dari ancaman baru. Dalam arsitektur FL, setiap klien dapat menyumbangkan update model yang berpotensi dimanipulasi. Jika salah satu atau beberapa klien mengirimkan parameter model yang bias, model gabungan dapat mengalami degradasi performa dan bahkan membuka celah backdoor attack.

Masalah ini menjadi sangat penting dalam konteks IDS dan NIDS, karena data jaringan sangat heterogen dan sering kali tersebar di berbagai lokasi. Data non-IID, perbedaan distribusi, serta variasi ancaman antar klien dapat membingungkan proses aggregasi. Dalam situasi seperti ini, agregasi model tradisional seperti FedAvg cenderung terlalu bergantung pada rata-rata sederhana, sehingga dapat memudahkan attacker untuk menyisipkan update yang merusak.

Penelitian ini membahas kebutuhan akan robust aggregation dalam federated IDS. Pendekatan ini berangkat dari asumsi bahwa keamanan model tidak hanya tergantung pada akurasi lokal, tetapi juga pada kemampuan sistem membedakan update yang sah dari update yang mencurigakan. Dengan demikian, fokus utama penelitian ini adalah membangun agregasi yang tahan terhadap poisoning dan backdoor attack, sambil tetap menjaga performa deteksi intrusi di lingkungan jaringan yang terdistribusi.

## 2. Ideal Abstrak
Federated Learning (FL) menjadi pendekatan yang menjanjikan untuk deteksi intrusi karena memungkinkan model dilatih pada data yang tersebar tanpa mentransfer data sensitif ke server pusat. Namun, arsitektur FL tetap rentan terhadap serangan poisoning dan backdoor attack, terutama ketika beberapa klien berperan sebagai attacker atau mengirimkan update model yang terkontaminasi. Kondisi ini dapat memengaruhi kualitas model gabungan dan menurunkan akurasi deteksi ancaman.

Penelitian ini mengeksplorasi desain robust aggregation untuk federated IDS, dengan fokus pada identifikasi update model yang mencurigakan, pengurangan pengaruh client malicious, serta pemeliharaan stabilitas performa model dalam lingkungan jaringan yang heterogen. Metode yang dibahas meliputi robust aggregation rule, anomaly detection pada gradient atau parameter model, serta integrasi trust scoring dan client validation.

Hasil kajian menunjukkan bahwa robust aggregation sangat penting untuk menjaga integritas model federated dalam sistem keamanan siber. Tanpa mekanisme ini, intrution detection yang menggunakan FL berisiko kehilangan kemampuan mendeteksi serangan baru dan bahkan dapat dimanfaatkan oleh penyerang untuk memperlemah sistem. Oleh karena itu, robust aggregation harus dipandang sebagai komponen inti dari desain federated IDS yang aman dan andal.

## 3. Introduction
Intrusion Detection System (IDS) modern bergantung pada data yang bersifat terdistribusi dan sering kali sensitif. Data log, trafik jaringan, dan aktivitas endpoint sering kali berada di berbagai instansi, edge node, atau perangkat IoT. Kondisi ini membuat pendekatan sentralisasi yang mengumpulkan semua data ke satu lokasi menjadi kurang cocok, baik dari perspektif privasi maupun skalabilitas.

Federated Learning hadir sebagai solusi karena setiap peserta hanya melatih model lokal dan mengirimkan update model ke server. Teknik ini memelihara prinsip data sovereignty sambil tetap memungkinkan kolaborasi untuk membangun model deteksi yang lebih kuat. Namun, FL tidak sepenuhnya kebal terhadap ancaman. Dalam praktiknya, update model bisa dimanipulasi oleh node yang berbahaya, baik melalui poisoning attack maupun backdoor attack.

Ancaman ini sangat berbahaya dalam sistem keamanan siber karena model gabungan dapat dilatih untuk mengenali perilaku legit sebagai ancaman atau sebaliknya. Risiko ini berlipat ganda ketika data jaringan antar node sangat berbeda, sehingga kemampuan untuk mendeteksi outlier dan update yang tidak konsisten menjadi sangat penting.

Penelitian ini memperkenalkan kebutuhan akan robust aggregation sebagai mekanisme utama untuk menjaga integritas federated IDS. Dengan pendekatan ini, server tidak hanya mengombinasikan parameter, tetapi juga menilai validitas kontribusi tiap klien berdasarkan pola update dan konsistensi historisnya.

## 4. Related Work
Penelitian sebelumnya mengenai FL untuk IDS telah memfokuskan banyak perhatian pada privasi, efisiensi komunikasi, dan heterogenitas data. Banyak studi memperkenalkan skema aggregasi seperti FedAvg, FedProx, dan variasi berdasarkan weighting. Namun, metode-metode ini masih sering menganggap klien sebagai entitas yang dapat dipercaya, meskipun dalam praktiknya beberapa klien bisa terinfeksi atau sengaja merusak model.

Pada sisi yang sama, riset keamanan FL mencakup pengembangan robust aggregation untuk menangani model poisoning. Teknik seperti median aggregation, trimmed mean, Krum, dan multi-Krum ditawarkan untuk menilai update yang tidak konsisten. Meskipun begitu, sebagian besar usaha tersebut masih dievaluasi pada data umum dan belum secara spesifik menguji skenario IDS/NIDS yang bersifat multi-tenant dan real-time.

Ada celah yang jelas: belum banyak penelitian yang mengintegrasikan robust aggregation dengan konteks deteksi intrusi di jaringan terdistribusi, terutama bila menghadapi adaptasi ancaman yang cepat dan dataset yang sangat tidak seragam. Inilah yang menjadi landasan penting untuk pengembangan robust aggregation pada federated IDS.

## 5. Method
Penelitian ini menggunakan pendekatan literatur review dan desaign framework untuk mengidentifikasi kebutuhan robust aggregation pada federated IDS. Langkah yang dilakukan adalah:

1. Mengumpulkan pendekatan FL untuk IDS yang sudah ada, termasuk FedAvg dan variasi robust aggregation.
2. Mengidentifikasi jenis ancaman yang relevan, yaitu poisoning attack, backdoor attack, dan malicious client behavior.
3. Menganalisis indikator update model yang mencurigakan, seperti outlier gradient, perubahan besar secara tiba-tiba, dan inkonsistensi terhadap data lokal klien.
4. Mengembangkan skema robust aggregation yang menilai kontribusi tiap klien berdasarkan kesesuaian historis dan struktur update.
5. Menilai efeknya terhadap akurasi IDS, false positive, dan kemampuan mendeteksi ancaman baru.

Metode ini dipilih untuk fokus pada desain yang tidak hanya teoritis, tetapi juga relevan untuk deployment di lingkungan keamanan siber yang nyata.

## 6. Result and Discussion
Hasil kajian menunjukkan bahwa robust aggregation sangat penting untuk menjaga keberlangsungan federated IDS. Dalam skenario di mana satu atau beberapa klien membangkitkan update yang menyimpang, metode aggregasi konvensional cenderung menurunkan kualitas model secara keseluruhan. Akibatnya, model gabungan dapat gagal mengenali serangan yang sebenarnya atau bahkan menandai traffic sah sebagai ancaman.

Pada sisi lain, robust aggregation dapat memperbaiki stabilitas model dengan memfilter update yang tidak konsisten, menimbang kontribusi client secara berbasis trust, atau menggunakan median/trimmed mechanism untuk mengurangi efek outlier. Strategi ini terbukti lebih cocok untuk lingkungan yang memiliki distribusi data heterogen dan kemungkinan malicious participant.

Namun, tidak ada satu metode yang sepenuhnya universal. Terdapat trade-off antara tingkat kinerja robust, overhead komputasi, dan cara menangani data non-IID. Karena itu, desain robust aggregation harus disesuaikan dengan karakteristik IDS, seperti jenis trafik, skala jaringan, dan kebutuhan real-time.

## 7. Conclusion
Federated Learning untuk IDS sangat menjanjikan, tetapi keamanan model tetap menjadi masalah utama jika tidak disertai dengan robust aggregation. Serangan poisoning dan backdoor dapat mengganggu model gabungan dan menurunkan keandalan sistem deteksi intrusi. Oleh karena itu, robust aggregation harus dianggap sebagai komponen inti agar federated IDS dapat beroperasi secara aman dalam lingkungan yang terdistribusi.

Penelitian selanjutnya perlu berfokus pada integrasi robust aggregation dengan karakteristik data real-world, skema penilaian client, dan mekanisme deteksi ancaman yang lebih adaptif. Dengan pendekatan ini, federated IDS tidak hanya tetap menjaga privasi data, tetapi juga memiliki ketahanan yang lebih kuat terhadap serangan yang canggih.

## 8. Referensi
1. McMahan, B., et al. (2017). Communication-Efficient Learning of Deep Networks from Decentralized Data.
2. Kairouz, P., et al. (2021). Advances and Open Problems in Federated Learning.
3. Fung, C., et al. (2018). Mitigating Sybils in Federated Learning Poisoning.
4. Blanchard, P., et al. (2017). Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent.
5. Moustafa, N., & Slay, J. (2015). UNSW-NB15: A comprehensive data set for network intrusion detection systems.
6. Bagdasaryan, E., et al. (2020). How to Backdoor Federated Learning.
7. Sun, Z., et al. (2019). Can You Trust Your Model? Backdoor via Federated Learning.
8. Li, T., et al. (2020). Federated Optimization in Heterogeneous Networks.
9. Nguyen, T. D., et al. (2021). Federated Learning for Cybersecurity: A Survey.
10. Singh, A., et al. (2022). Robust federated intrusion detection in heterogeneous networks.
