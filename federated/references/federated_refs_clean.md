# Daftar Referensi Terkonsolidasi — Paper 4 (Federated SFM-NIDS)

> **Fungsi:** daftar referensi IEEE **bersih & unik** hasil konsolidasi dua berkas
> review (`literature_review_federated_nids.md` + `state_of_art_gap_federated_nids.md`).
> Dipakai sebagai sumber `\bibitem` saat menulis `paper-federated.tex`.
>
> **Catatan penting:**
> - Di NARASI `literature_review` ada penomoran yang salah-rujuk (mis. nomor [26]
>   dipakai untuk beberapa karya berbeda). **Daftar di bawah ini sudah dirapikan**:
>   satu nomor = satu karya, dedup lintas-berkas berdasarkan DOI/judul.
> - [F19] adalah **paper SFM kita (Paper 1)** — fondasi Paper 4; sitasi sebagai karya
>   pendahulu. Pastikan status terbit sebelum submit.
> - Verifikasi DOI/venue sekali lagi saat finalisasi naskah (beberapa entri arXiv/preprint).

## A. Survei & landasan FL-NIDS
- [F1] A. Khraisat, A. Alazab, T. Jan, A. Gopez, "Survey on Federated Learning for Intrusion Detection System: Concept, Architectures, Aggregation Strategies, Challenges, and Future Directions," ACM Computing Surveys, 2024. doi:10.1145/3687124.
- [F2] J. L. Hernández-Ramos et al., "Intrusion Detection Based on Federated Learning: A Systematic Review," ACM Computing Surveys, Apr. 2025. doi:10.1145/3731596.
- [F3] A. A. Wardana, P. Sukarno, "Taxonomy and Survey of Collaborative Intrusion Detection System using Federated Learning," ACM Computing Surveys, Oct. 2024. doi:10.1145/3701724.
- [F4] E. V. Fedorchenko, E. Novikova, A. N. Shulepov, "Comparative Review of the IDS Based on Federated Learning: Advantages and Open Challenges," Algorithms, 15(7):247, 2022. doi:10.3390/a15070247.

## B. Arsitektur & agregasi FL-NIDS
- [F5] J. Xu, C. Li, Y. Zheng, Z. Li, "Entente: Cross-silo Intrusion Detection on Network Log Graphs with Federated Learning," arXiv:2503.14284, 2025. doi:10.48550/arxiv.2503.14284.
- [F6] Z. Chen, N. Lv, P. Li, Y. Fang, K. Chen, W. Pan, "Intrusion Detection for Wireless Edge Networks Based on Federated Learning (FedAGRU)," IEEE Access, 8:217463-217472, 2020. doi:10.1109/ACCESS.2020.3041793.
- [F7] J. Mao, Z. Wei, B. Li, R. Zhang, L. Song, "FedIn-NID: A FL Framework for NID in Large-Scale Heterogeneous Industrial IoT," IEEE TIFS, 2025. doi:10.1109/tifs.2025.3602226.
- [F8] R. Doriguzzi-Corin, S. Cretti, D. Siracusa, "Resource-Efficient Federated Learning for Network Intrusion Detection," IEEE NetSoft, 2024. doi:10.1109/netsoft60951.2024.10588938.
- [F9] Y.-C. Lee, W.-C. Chien, Y.-C. Chang, "FedDB: A Federated Learning Approach Using DBSCAN for DDoS Attack Detection," Applied Sciences, 2024. doi:10.3390/app142210236.
- [F10] A. F. I. M. Zainudin, R. Akter, D.-S. Kim, J.-M. Lee, "FedDDoS: An Efficient FL-based DDoS Attacks Classification in SDN-Enabled IIoT Networks," 2022. doi:10.1109/ICTC55196.2022.9952610.

## C. Non-IID, heterogenitas, personalisasi
- [F11] L. Lavaur, Y. Busnel, F. Autrel, "Demo: Highlighting the Limits of Federated Learning in Intrusion Detection," IEEE ICDCS, 2024. doi:10.1109/icdcs60910.2024.00135.
- [F12] M. Benkaddour, "Enhancing Federated Learning for Privacy Preserving Intrusion Detection in IoT networks," Przegląd Elektrotechniczny, 2025. doi:10.15199/48.2025.09.21.
- [F13] S. Gurpreet, S. Keshav, P. Rajalakshmi, Y. Xong, "Sentinel: Dynamic Knowledge Distillation for Personalized Federated Intrusion Detection in Heterogeneous IoT Networks," arXiv:2510.23019, 2025. doi:10.48550/arxiv.2510.23019.
- [F14] S. Ali, R. Alireza, A. Mahmood, "Mist-Assisted Federated Learning for Intrusion Detection in Heterogeneous IoT Networks," arXiv:2511.00271, 2025. doi:10.48550/arxiv.2511.00271.
- [F15] M. Khalid, U. Zukaib, M. Al-Rakhami, A. M. Alamri, "FedCross-VAN: Federated Cross-Domain Behavior Alignment for VANET Intrusion Detection," Trans. Emerging Telecom. Tech., 37, 2025. doi:10.1002/ett.70309.

## D. Adversarial robustness & Byzantine/poisoning dalam FL
- [F16] "Combating Exacerbated Heterogeneity for Robust Models in Federated Learning (SFAT)," arXiv:2303.00250, 2023. doi:10.48550/arxiv.2303.00250.
- [F17] E. M. Ennaji, S. E. Hajla, Y. Maleh, S. Mounir, "Adversarially robust federated deep learning models for intrusion detection in IoT," Indonesian J. EECS, 37(2):937, 2024. doi:10.11591/ijeecs.v37.i2.pp937-947.
- [F18] G. Chandu, T. S. Karthik, B. Parag, "Federated Learning for Distributed IoT Security: A Privacy-Preserving Approach to Intrusion Detection (HADA)," IEEE Access, 2025. doi:10.1109/access.2025.3592481.
- [F20] A. Al Mazroa, "FORT-IDS: a federated, optimized, robust and trustworthy IDS for IIoT security," Scientific Reports, 2025. (nature.com/articles/s41598-025-31025-x)
- [F21] S. K. Ghimire, S. Lodh, "FedSecIoT: A FL Framework for Collaborative and Privacy-Preserving Botnet Detection in IoT with Adversarial Robustness," IEEE SILCON, 2025. doi:10.1109/silcon67893.2025.11327096.
- [F22] V. Rey, P. M. S. Sánchez, A. H. Celdrán, G. Bovet, M. Jaggi, "Federated Learning for Malware Detection in IoT Devices," Computer Networks, 2021. doi:10.1016/j.comnet.2021.108693.
- [F23] S. Saha, M. I. Sayed, M. Faezipour, S. Bhatt, "Resilient Federated Learning for DDoS Detection with Multi-Krum Aggregation and Anomaly Detection," IEEE SmartNets, 2025. doi:10.1109/smartnets65254.2025.11106859.
- [F24] Z. Sun, P. Kairouz, A. T. Suresh, H. B. McMahan, "Can You Really Backdoor Federated Learning?," arXiv:1911.07963, 2019.
- [F25] J. Zhang et al., "Delving into the Adversarial Robustness of Federated Learning," arXiv:2302.09479, 2023. doi:10.48550/arXiv.2302.09479.
- [F26] "Statistical Detection of Adversarial examples in Blockchain-based Federated Forest In-vehicle NID Systems," arXiv:2207.04843, 2022. doi:10.48550/arxiv.2207.04843.
- [F27] A. A. Wardana, "Ensuring Trust, Privacy, and Robust Collaborative Learning in Collaborative IDS for Heterogeneous Networks," PhD dissertation, 2024.

## E. GAN / adversarial training untuk DDoS (non-FL & FL)
- [F28] "GADoT: GAN-based Adversarial Training for Robust DDoS Attack Detection," arXiv:2201.13102, 2022. doi:10.48550/arxiv.2201.13102.
- [F29] T. Björn, "FGAN: Federated Generative Adversarial Networks for Anomaly Detection in Network Traffic," arXiv:2203.11106, 2022. doi:10.48550/arxiv.2203.11106.
- [F30] Q. Zeng, S. Olatunde-Salawu, F. Nait-Abdesselam, "FGA-IDS: A FL and GAN-Augmented IDS for UAV Networks," IEEE CIC, 2024. doi:10.1109/cic62241.2024.00017.
- [F31] R. Doriguzzi-Corin, D. Siracusa, "FLAD: Adaptive Federated Learning for DDoS Attack Detection," arXiv:2205.06661, 2022. doi:10.48550/arXiv.2205.06661.
- [F32] I. Debicha, T. Debatty, J.-M. Dricot, W. Mees, "Adversarial Training for Deep Learning-based Intrusion Detection Systems," arXiv:2104.09852, 2021.
- [F33] H. Dadhwal, M. de Abreu, N. Parvizi, S. Saha, "Benchmarking the adversarial resilience of ML models for DDoS detection," Array, 29:100664, 2026. doi:10.1016/j.array.2025.100664.
- [F34] S. Saini, A. Chennamaneni, B. A. Sawyerr, "A Review of the Duality of Adversarial Learning in Network Intrusion: Attacks and Countermeasures," arXiv:2412.13880, 2024. doi:10.48550/arxiv.2412.13880.
- [F35] M. Wang, N. Yang, D. Gunasinghe, N. Weng, "On the Robustness of ML-Based NIDS: An Adversarial and Distribution Shift Perspective," Computers, 2023. doi:10.3390/computers12100209.

## F. Few-shot / meta-learning / transfer dalam FL-NIDS
- [F36] Y. Hu, J. Wu, G. Li, J. Li, J. Cheng, "Privacy-Preserving Few-Shot Traffic Detection Against APTs via Federated Meta Learning," IEEE TNSE, 11:2549-2560, 2024. doi:10.1109/tnse.2023.3304556.
- [F37] Q. Mao, X. Lin, G. Li, J. Li, "FeCoGraph: Label-aware federated graph contrastive learning for few-shot network intrusion detection," IEEE TIFS, 2025. doi:10.1109/tifs.2025.3541890.
- [F38] K. Yin, J. Zhang, Z. Xia, C. Yu, "FedPKT: Robust Cross-Domain Few-Shot Intrusion Detection via Prototypical Knowledge Transfer," IEEE (document 11360061).
- [F39] Ö. Ceviz, S. Şen, P. Sadioglu, "Distributed Intrusion Detection in Dynamic Networks of UAVs using Few-Shot Federated Learning," arXiv:2501.13213, 2025. doi:10.48550/arxiv.2501.13213.
- [F40] J. Zhang, C. Luo, M. Carpenter, G. Min, "Federated Learning for Distributed IIoT Intrusion Detection Using Transfer Approaches," IEEE TII, 19:8159-8169, 2023. doi:10.1109/TII.2022.3216575.
- [F41] K. S, V. Malathi, B. J. Lakshmi, A. V. Sriharsha, T. D. Kumar, T. Lakshmibai, "Federated and Explainable IDS for Large-Scale Heterogeneous Networks using Ensemble Deep Learning," IEEE ICACRS, 2025. doi:10.1109/icacrs67045.2025.11324277.

## G. Fondasi sendiri (Paper 1 — WAJIB disitasi sebagai pendahulu)
- [F19] H. Y. Martono, I. Syarif, F. A. Saputra, "Cross-Dataset Generalization of ML-based Network Intrusion Detection via Semantic Feature Mapping and Few-Shot Adaptation, Validated on Real Cloud Traffic," [status terbit DIISI saat accepted].

---
**Catatan dedup:** entri yang muncul di KEDUA berkas review (mis. GADoT, Lavaur,
Chandu/HADA, FLAD, Dadhwal, Entente, Sentinel, FedCross-VAN, FeCoGraph, FedPKT, Hu,
Khraisat) sudah digabung jadi SATU entri. Total ~41 referensi unik. Nomor [F*] bersifat
sementara (grup tematik); saat menulis `.tex`, nomori ulang sesuai urutan kemunculan.
