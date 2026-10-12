# 05. Adaptive Federated Learning for Cross-Domain NIDS Under Data Scarcity and Adversarial Drift

## Judul dalam Bahasa Indonesia
Pembelajaran Federated Adaptif untuk NIDS Lintas Domain di Bawah Keterbatasan Data dan Drift Adversarial

## English Title
Adaptive Federated Learning for Cross-Domain NIDS Under Data Scarcity and Adversarial Drift

## 1. Pendahuluan Judul
Sistem deteksi intrusi jaringan tidak dapat dipandang sebagai model statis. Trafik jaringan berubah dari waktu ke waktu karena munculnya ancaman baru, perubahan pola pengguna, serta perubahan konfigurasi sistem. Kondisi ini membuat model deteksi intrusi perlu dapat beradaptasi terhadap drift data dan perubahan ancaman yang terus terjadi. Dalam lingkungan terdistribusi, permasalahan ini menjadi lebih kompleks karena tiap domain memiliki pola data yang berbeda dan sering kali terbatas.

Federated Learning (FL) menawarkan cara kolaboratif untuk membangun model deteksi di seluruh domain tanpa memindahkan data sensitif. Namun, ketika model harus bekerja di banyak domain dengan data yang terbatas atau sangat beragam, pendekatan FL konvensional sering kali tidak cukup. Data scarcity dan adversarial drift dapat memperlambat pelatihan, menurunkan akurasi, dan bahkan memicu bias terhadap domain tertentu.

Penelitian ini membahas kebutuhan akan adaptive federated learning sebagai solusi untuk cross-domain NIDS. Fokusnya adalah pengelolaan heterogenitas data, strategi adaptasi model, serta penguatan ketahanan terhadap perubahan pola ancaman yang bersifat adversarial. Dengan pendekatan ini, model dapat tetap relevan dalam lingkungan yang dinamis dan terus berkembang.

## 2. Ideal Abstrak
Network Intrusion Detection Systems (NIDS) di lingkungan modern sering menghadapi keterbatasan data dan perubahan distribusi ancaman yang cepat. Ketika data bersumber dari berbagai domain dengan karakteristik yang berbeda, model deteksi menjadi sulit dibangun secara universal. Dalam konteks ini, Federated Learning (FL) menawarkan solusi kolaboratif, namun tetap menghadapi tantangan besar terkait data scarcity, non-IID distribution, dan adversarial drift.

Penelitian ini mengeksplorasi adaptive federated learning untuk NIDS lintas domain. Fokus utama mencakup mekanisme adaptasi model terhadap perubahan pola serangan, teknik pembelajaran dengan data terbatas, serta strategi untuk menjaga robust model di bawah perturbasi adversarial. Kajian ini juga menilai bagaimana model dapat menyeimbangkan kontribusi domain yang berbeda untuk menjaga generalisasi dan sensitivitas terhadap ancaman baru.

Hasil kajian menunjukkan bahwa pendekatan adaptif lebih cocok untuk NIDS real-world dibandingkan FL statis. Dengan strategi adaptasi yang tepat, model dapat tetap relevan ketika distribusi data berubah atau ketika ancaman baru muncul. Namun, penyelesaian ini memerlukan desain yang menjaga efisiensi, keadilan kontribusi domain, dan integritas model.

## 3. Introduction
NIDS sangat bergantung pada representasi pola jaringan yang relevan dengan ancaman yang ada. Namun, pola serangan terus berubah seiring waktu, karena pelaku ancaman menyesuaikan strategi mereka terhadap lingkungan baru. Akibatnya, model NIDS tidak dapat dipastikan tahan lama jika tidak dilatih ulang atau tidak diadaptasi terhadap drift data.

Pada lingkungan multi-domain, permasalahan ini menjadi lebih besar. Setiap domain bisa memiliki karakteristik trafik, protokol, lalu lintas user, serta pola serangan yang berbeda. Data yang tersedia pada suatu domain mungkin sangat terbatas, sementara domain lain memiliki volume data yang jauh lebih besar. Kondisi ini membuat model federated yang dibangun dari rata-rata sederhana mudah terpengaruh oleh ketidakseimbangan distribusi.

Adversarial drift semakin memperburuk situasi. Serangan yang dibuat untuk mengecoh model dapat muncul secara bertahap dan sulit terdeteksi jika model tidak adaptif. Oleh karena itu, pendekatan adaptive FL menjadi kebutuhan penting untuk menjaga ketahanan NIDS dalam lingkungan pengembangan nyata.

## 4. Related Work
Studi awal tentang FL untuk NIDS menekankan privasi, heterogenitas data, dan agregasi model. Beberapa penelitian memperkenalkan teknik untuk menangani non-IID, meskipun masih banyak yang mengasumsikan distribusi data stabil. Namun, dalam praktiknya, jaringan terus mengalami perubahan, dan ancaman baru dapat berdampak pada model yang sudah dilatih.

Riset mengenai adversarial drift dan data scarcity juga berkembang, namun masih belum banyak yang menghubungkannya secara langsung dengan cross-domain federated NIDS. Banyak pendekatan fokus pada satu domain atau satu dataset, sehingga sulit untuk menggeneralisasikan hasil ke skenario multi-domain yang lebih kompleks.

Ada jelas celah besar pada area ini: belum banyak framework adaptive FL yang menilai bagaimana model harus berubah ketika data dan ancaman berubah, terutama di lingkungan dengan keterbatasan data dan perbedaan domain. Inilah yang membuat topik ini sangat relevan untuk riset masa depan.

## 5. Method
Penelitian ini membahas model konseptual untuk adaptive FL pada cross-domain NIDS. Langkah-langkah utama yang dilakukan adalah:

1. Mengidentifikasi karakteristik data NIDS lintas domain, termasuk data scarcity dan heterogenitas distribusi.
2. Menganalisis mekanisme drift data dan ancaman adversarial yang dapat mempengaruhi performa model.
3. Menilai berbagai strategi adaptif pada FL, termasuk domain-aware aggregation dan client-specific reweighting.
4. Menganalisis bagaimana model dapat diperbarui dengan tetap menjaga stabilitas dan keadilan kontribusi antar domain.
5. Menentukan indikator performa seperti robustness, generalization, dan sensitivitas terhadap ancaman baru.

Metode ini dipilih untuk menghadirkan solusi yang lebih realistis dibandingkan pendekatan FL statis, terutama untuk lingkungan jaringan yang terus berkembang.

## 6. Result and Discussion
Hasil kajian menunjukkan bahwa adaptive federated learning lebih sesuai untuk NIDS lintas domain dibandingkan pendekatan statis. Ketika distribusi data berubah atau data baru muncul, model adaptif dapat menyesuaikan bobot kontribusi domain dan memperbarui parameter secara lebih tepat. Hal ini mengurangi risiko bias terhadap domain yang dominan sementara tetap mempertahankan generalisasi terhadap domain yang lebih kecil.

Di sisi lain, adversarial drift tetap menjadi tantangan besar. Jika model tidak dilengkapi mekanisme yang mampu memfilter update yang mencurigakan, ancaman dapat secara perlahan merusak kemampuan deteksi. Oleh karena itu, adaptive FL perlu dikombinasikan dengan robust aggregation dan pemeriksaan konsistensi update antar domain.

Selain itu, hasil kajian menegaskan bahwa menjaga keseimbangan antara adaptasi dan stabilitas sangat penting. Model yang terlalu cepat beradaptasi bisa mengikuti noise atau pola sesaat, sedangkan model yang terlalu konservatif bisa gagal menangkap ancaman baru. Inilah sebabnya, adaptive FL perlu dirancang dengan mekanisme pembelajaran yang cermat dan dapat diandalkan.

## 7. Conclusion
Adaptive Federated Learning menjadi arah penting dalam pengembangan cross-domain NIDS karena model perlu tetap efektif di bawah kondisi data scarcity, heterogenitas domain, dan perubahan ancaman yang terus berlangsung. Dalam lingkungan tersebut, FL statis tidak cukup untuk menjaga akurasi dan ketahanan model.

Pengembangan riset di masa depan perlu menekankan kombinasi antara adaptasi model, robust aggregation, dan evaluasi real-world pada lingkungan multi-domain. Dengan pendekatan yang tepat, adaptive FL dapat menjadi fondasi bagi NIDS yang lebih kuat, lebih responsif, dan lebih tahan terhadap ancaman yang berubah dengan cepat.

## 8. Referensi
1. Kairouz, P., et al. (2021). Advances and Open Problems in Federated Learning.
2. Li, T., et al. (2020). Federated Optimization in Heterogeneous Networks.
3. McMahan, B., et al. (2017). Communication-Efficient Learning of Deep Networks from Decentralized Data.
4. Moustafa, N., & Slay, J. (2015). UNSW-NB15: A comprehensive data set for network intrusion detection systems.
5. Sarker, I. H. (2021). Machine learning for cybersecurity: A review.
6. Biggio, B., et al. (2013). Evasion attacks against machine learning at test time.
7. Bagdasaryan, E., et al. (2020). How to Backdoor Federated Learning.
8. Yang, Q., et al. (2019). Federated Learning.
9. Nguyen, T. D., et al. (2021). Federated Learning for Cybersecurity: A Survey.
10. Wang, S., et al. (2021). Adaptive federated optimization for non-IID data.
