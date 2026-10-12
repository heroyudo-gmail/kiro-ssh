# 02. Communication-Efficient Federated Learning for Heterogeneous IoT Networks

## Judul dalam Bahasa Indonesia
Pembelajaran Federated yang Efisien dalam Komunikasi untuk Jaringan IoT yang Heterogen

## English Title
Communication-Efficient Federated Learning for Heterogeneous IoT Networks

## 1. Pendahuluan Judul
Jaringan IoT memiliki karakteristik yang sangat heterogen, mulai dari perangkat dengan sumber daya berbeda, jenis data yang bervariasi, hingga pola konektivitas yang tidak seragam. Kondisi ini memengaruhi kualitas pembelajaran model ketika seluruh node berpartisipasi dalam Federated Learning (FL). Salah satu tantangan utama dalam FL untuk IoT adalah komunikasi antar node. Karena setiap round pembaruan model mengharuskan perangkat mengirim parameter atau gradien ke server, kebutuhan bandwidth dan latensi dapat sangat tinggi, terutama pada perangkat yang terbatas.

Masalah ini semakin kompleks ketika data masing-masing node tidak identik atau tidak terdistribusi secara independent-and-identically distributed (non-IID). Perangkat IoT yang berbeda dapat menghasilkan data dengan pola ancaman yang berbeda, sehingga model hasil agregasi sering kali tidak stabil dan membutuhkan banyak komunikasi untuk mencapai performa yang baik. Di sinilah kebutuhan akan pendekatan communication-efficient FL menjadi sangat penting.

Penelitian ini mengeksplorasi bagaimana FL dapat dibuat lebih efisien dalam jaringan IoT yang heterogen. Fokus utama mencakup model compression, adaptasi round komunikasi, strategi aggregation yang memerhatikan keterbatasan bandwidth, serta dampaknya terhadap akurasi dan responsivitas sistem keamanan.

## 2. Ideal Abstrak
Federated Learning (FL) menawarkan solusi untuk melatih model pada data yang terdistribusi di perangkat IoT tanpa perlu mentransfer data sensitif ke pusat. Namun, jaringan IoT sering kali terdiri dari perangkat yang sangat heterogen dalam hal kemampuan komputasi, bandwidth, dan kualitas koneksi. Kondisi ini membuat komunikasi model menjadi bottleneck utama dalam penerapan FL di lingkungan realistis.

Penelitian ini mengkaji pendekatan communication-efficient FL untuk jaringan IoT yang heterogen, dengan fokus pada kompresi model, seleksi partisipan, pengurangan ukuran update parameter, serta strategi aggregation yang mempertimbangkan keterbatasan perangkat. Selain itu, studi ini menilai bagaimana pendekatan komunikasi yang efisien memengaruhi akurasi model, konsumsi bandwidth, dan stabilitas training di lingkungan non-IID.

Hasil analisis menunjukkan bahwa efisiensi komunikasi tidak hanya menurunkan biaya jaringan, tetapi juga dapat meningkatkan skalabilitas FL untuk skenario IoT yang luas. Namun, efisiensi yang terlalu agresif dapat mengorbankan akurasi model. Oleh karena itu, perlu ada keseimbangan antara pengurangan komunikasi dan kualitas model akhir.

## 3. Introduction
Jaringan IoT modern mencakup beragam perangkat, mulai dari sensor kecil hingga gateway dan sistem edge yang lebih kuat. Perangkat-perangkat ini menghasilkan data yang sangat besar dan beragam, tetapi tidak semua memiliki capabilitas komunikasi atau komputasi yang sama. Dalam konteks keamanan siber, data ini sangat penting untuk mendeteksi serangan seperti botnet, malware, dan anomalous traffic.

Federated Learning memungkinkan seluruh perangkat berbagi pembelajaran model tanpa mentransfer data mentah. Namun, setiap komunikasi model pada FL dapat menimbulkan overhead yang signifikan. Pada lingkungan IoT, faktor ukuran model, lateny jaringan, dan ketidakstabilan koneksi dapat menghambat proses training. Jika tidak diatasi, FL akan sulit diimplementasikan pada skala yang besar.

Masalah yang lebih kompleks muncul karena data IoT biasanya bersifat non-IID. Satu perangkat mungkin melihat pola ancaman tertentu, sementara perangkat lainnya tidak. Kondisi ini meningkatkan kebutuhan untuk pembaruan yang adaptif, komunikasi yang efisien, dan strategi aggregation yang sesuai dengan karakteristik jaringan.

Penelitian ini berfokus pada bagaimana membangun sistem FL yang mampu berfungsi dalam jaringan heterogen tanpa mengorbankan kualitas deteksi. Dengan pendekatan communication-efficient, sistem dapat mencapai keseimbangan yang lebih baik antara performa dan biaya operasional.

## 4. Related Work
Riset sebelumnya dalam FL untuk IoT banyak membahas penggunaan model lokal, aggregation scheme, dan privacy-preserving. Beberapa studi menitikberatkan pada model compression, seperti pruning, quantization, dan sparsification, untuk mengurangi ukuran komunikasi. Studi lain fokus pada client selection agar hanya perangkat yang siap dan layak ikut berkontribusi dalam setiap round.

Namun, sebagian besar pendekatan tersebut masih belum mengevaluasi secara menyeluruh dampaknya dalam jaringan IoT yang benar-benar heterogen, termasuk perbedaan bandwidth, skala, serta format data. Banyak model yang bekerja baik pada skenario lab tidak selalu efektif saat dihadapkan pada jaringan edge yang dinamis dan tidak stabil.

Ada juga keterbatasan dalam mengintegrasikan efisiensi komunikasi dengan kebutuhan deteksi ancaman di jaringan IoT. Kebutuhan seperti latensi rendah, real-time monitoring, dan adaptasi terhadap ancaman baru sering tidak terakomodasi secara sempurna. Oleh karena itu, diperlukan kerangka kerja FL yang menyeimbangkan komunikasi, akurasi, dan robustositas.

## 5. Method
Penelitian ini menggunakan pendekatan review sistematik terhadap kebutuhan komunikasi efisien dalam FL untuk IoT. Langkah-langkah yang dilakukan adalah:

1. Mengidentifikasi karakteristik jaringan IoT yang heterogen dan kebutuhan pembelajaran terdistribusi.
2. Menganalisis teknik efisiensi komunikasi pada FL, seperti compression, sparse update, dan client selection.
3. Menilai dampak non-IID data terhadap kebutuhan komunikasi dan akurasi model.
4. Menganalisis trade-off antara ukuran update, tingkat akurasi, dan biaya jaringan.
5. Menyusun kerangka kerja yang relevan untuk penerapan FL dalam sistem keamanan IoT.

Metode ini dipilih karena fokus utama penelitian bukan sekadar membahas teori, tetapi menghubungkan kebutuhan komunikasi dengan konteks operasional yang nyata.

## 6. Result and Discussion
Hasil kajian menunjukkan bahwa efisiensi komunikasi adalah faktor kunci agar FL dapat diterapkan pada jaringan IoT yang besar dan heterogen. Tanpa strategi pengurangan overhead, model gabungan membutuhkan banyak iterasi dan banyak bandwidth untuk mencapai akurasi yang memadai. Kondisi ini menjadi serius ketika banyak node memiliki keterbatasan daya dan konektivitas.

Teknik compression dan client selection terbukti membantu menurunkan beban komunikasi, tetapi dampaknya bervariasi. Compression yang terlalu agresif dapat mengurangi kualitas gradien dan menurunkan akurasi deteksi, sementara client selection yang terlalu ketat dapat mengurangi diversitas data. Oleh karena itu, pendekatan adaptif lebih disarankan dibandingkan strategi tunggal.

Dalam konteks keamanan IoT, pendekatan yang paling efektif adalah gabungan antara efisiensi komunikasi, adaptasi terhadap non-IID, dan pemantauan performa real-time. Meskipun komunikasi lebih efisien, sistem tetap harus menjaga tingkat deteksi yang tinggi agar ancaman dapat diidentifikasi sebelum berdampak besar.

## 7. Conclusion
Communication-efficient FL merupakan prasyarat penting untuk penerapan federated learning di jaringan IoT yang heterogen. Tanpa pengelolaan komunikasi yang tepat, FL akan sulit diimplementasikan pada perangkat yang memiliki keterbatasan sumber daya dan bandwidth. Namun, efisiensi komunikasi tidak boleh dicapai dengan mengorbankan kualitas model dan kemampuan deteksi ancaman.

Ke depan, riset perlu fokus pada pendekatan adaptive dan context-aware, yang menyesuaikan ukuran update, jadwal komunikasi, dan seleksi klien sesuai dengan kondisi jaringan. Dengan pendekatan ini, FL dapat menjadi solusi yang lebih scalable untuk keamanan IoT modern.

## 8. Referensi
1. McMahan, B., et al. (2017). Communication-Efficient Learning of Deep Networks from Decentralized Data.
2. Kairouz, P., et al. (2021). Advances and Open Problems in Federated Learning.
3. Li, T., et al. (2020). Federated Optimization in Heterogeneous Networks.
4. Hamer, J., et al. (2020). FedBoost: A communication-efficient federated learning method.
5. Wang, S., et al. (2021). Adaptive federated optimization for non-IID data.
6. Yang, Q., et al. (2019). Federated Learning.
7. Nguyen, H. T., et al. (2021). Communication-aware federated learning in IoT networks.
8. Geyer, R. C., et al. (2017). Differentially private federated learning for mobile keyboard prediction.
9. Sattler, F., et al. (2020). Robust and communication-efficient federated learning.
10. Djenna, A., & Boulahia, C. (2021). AI-driven cybersecurity: challenges and opportunities.
