# PEER REVIEW REPORT

**Journal:** International Journal of Electrical and Computer Engineering (IJECE)  
**Manuscript Title:** Perancangan sistem cadangan berbasis awan menggunakan algoritma multi-kompresi untuk mitigasi serangan ransomware *(Draft Version)*  
**Authors:** Hero Yudo Martono, Nafisah Rahmadani Harahap  
**Affiliation:** Departemen Teknik Informatika, Politeknik Elektronika Negeri Surabaya, Surabaya, Indonesia  
**Reviewer Recommendation:** **Major Revision**

---

## 1. GENERAL OVERVIEW & SUMMARY
This manuscript addresses two critical challenges in modern cloud-based data storage: the vulnerability of conventional backup systems to network-propagated ransomware attacks and the storage inefficiencies of compressing heterogeneous file formats using a single static algorithm [2, 4, 6]. 

The authors propose an integrated cloud backup framework that combines:
1. **Logical Air-Gapped Isolation:** Isolating backup storage logical volumes so they are only mounted during active backup or restore windows, reducing the attack surface [4, 43, 64].
2. **Adaptive Lossless Multi-Compression:** Automatically selecting from five lossless compression algorithms (Gzip, Zstandard, Brotli, LZ4, and Snappy) based on file characteristics before applying AES-256 encryption (compress-then-encrypt) [9, 22].
3. **Multi-Indicator Integrity Validation:** Combining SHA-256 hashing, metadata analysis (size, modification time, MIME type, extensions), and file structure inspections to detect ransomware-induced anomalies and trigger automated clean recoveries [21, 34, 49].

The system was evaluated on a synthetic dataset of 43 files (~531 MB) modeled after PT Equnix's corporate structures [24, 26, 27]. The proposed adaptive approach achieved 43.3% storage savings and completed compression 21 times faster than static Gzip, operating at a throughput of 611.8 MB/s [59]. Under simulated attacks (targeting CVE-2017-0144, CVE-2018-8453, and CVE-2021-36934), the system achieved a 100% data recovery rate within 4.3 to 5.3 seconds, with a 0% False Positive Rate (FPR) and False Negative Rate (FNR) in a controlled cloud environment (AWS EC2) [2, 84, 88].

---

## 2. KEY STRENGTHS
*   **Solid Theoretical Integration:** The manuscript successfully links the theoretical concept of Shannon Entropy to practical storage optimization and ransomware detection limits [7, 60, 61]. The authors empirically demonstrate that while low-entropy files (e.g., CSV, logs) experience massive entropy spikes when encrypted by ransomware (alerting the system), high-entropy files (e.g., JPG, XLSX) show negligible entropy changes [60, 61]. This justifies their multi-indicator validation approach (relying on hash and metadata instead of entropy alone) [8, 61].
*   **Highly Practical "Compress-Then-Encrypt" Architecture:** By placing compression before AES-256 encryption, the design avoids trying to compress randomized, high-entropy encrypted ciphertext [22]. This ensures real storage savings while maintaining data confidentiality [22].
*   **Rigorous Multi-Platform Validation:** The authors tested their implementation across both local environments (Windows 11) and enterprise-representative cloud setups (AWS EC2 with Ubuntu 22.04 and Windows Server 2022) [42]. The results demonstrate excellent cross-platform consistency in compression ratios, recovery rates, and detection metrics [85, 86].
*   **Realistic Performance Trade-Off Analysis:** Rather than striving for absolute compression ratios, the proposed adaptive strategy prioritizes throughput and low latency [59]. Achieving 43.3% savings at 611.8 MB/s compared to Static-Gzip's 50.1% savings at a sluggish 28.2 MB/s represents a highly practical design decision for business-critical backup recovery [59].

---

## 3. AREAS FOR IMPROVEMENT & CRITICAL CONSTRUCTIVE CRITICISM

### Critique 1: Dataset Scope and Generalizability
*   **Issue:** The empirical results are based on a small synthetic dataset of only 43 files totaling roughly 531 MB [26, 27]. While suitable for functional testing, this does not represent the sheer scale, file variety, or metadata noise of a real enterprise or financial institution.
*   **Recommendation:** To increase academic credibility and generalizability, the authors should supplement their synthetic evaluation with a standard, publicly reproducible compression benchmark, such as the *Silesia Compression Corpus* [27]. Additionally, discussing how the system behaves when scaled to multi-gigabyte or terabyte workloads would strengthen the evaluation.

### Critique 2: Overstatement of "0% False Positive & False Negative Rates"
*   **Issue:** The abstract and results highlight a "0% FPR and 0% FNR" [2, 88]. However, as the authors accurately admit in Section 4.15, this "perfect" score is a deterministic artifact of a highly controlled, synthetic environment using SHA-256 hash matching on known baselines [89]. In a live deployment, SHA-256 mismatches only tell us *that* a file changed, not *how* or *why*. It cannot actively detect stealthy, behavioral ransomware evasion techniques (like Living-off-the-Land or fileless malware) [89].
*   **Recommendation:** The abstract and discussion must temper these 0% claims. The manuscript should explicitly reframe this "perfect accuracy" as a verification of deterministic hash integrity in a controlled simulation, rather than an active, behavioral ML-based malware detection rate [89]. This ensures honest scientific communication.

### Critique 3: Detail on the "Adaptive" Selection Heuristics
*   **Issue:** The paper refers to the compression selection as "adaptive" [2, 9], but Section 3.4 reveals it is actually a static, rule-based decision tree based on file extensions (heuristics) rather than dynamic machine learning [29, 93].
*   **Recommendation:** The authors should clearly document the exact decision-tree logic or rules used in Python (e.g., mapping JPG/XLSX to light algorithms, logs to Snappy/LZ4, and large CSVs to Zstandard) [29, 55]. This will allow other researchers to reproduce and validate the rule-based framework. The transition to a true ML-based selector (e.g., Random Forest) should be highlighted as a planned future upgrade [93].

### Critique 4: Security Analysis of the "Logical" Air-Gap
*   **Issue:** Under AWS, the logical air-gap is achieved by mounting EBS volumes only during active backup/restore sessions [43, 64]. 
*   **Recommendation:** The authors should discuss the "window of vulnerability" during which the EBS volume is mounted [65]. A sophisticated, memory-resident ransomware could wait for the backup tool to trigger a mount command and immediately propagate payload files to the backup drive [65]. Authors should outline mitigations, such as strict AWS IAM permissions, write-once-read-many (WORM) configurations, or read-only mount parameters during restore tasks [16, 65, 93].

---

## 4. DETAILED SECTION-BY-SECTION COMMENTS

### Abstract & Keywords
*   The abstract is highly structured and clearly reports quantitative results (throughput, recovery times, storage savings) [2]. 
*   *Suggestion:* Explicitly state that the evaluation was conducted on a *synthetic* dataset and simulated attacks to align with the disclosures inside the paper [2, 27].

### Section 1: Pendahuluan (Introduction)
*   Provides an excellent, highly engaging review of the current ransomware landscape, highlighting the transition from simple screen-locking to double/triple extortion and data exfiltration [5, 41]. 
*   The explanation of logical air-gapping as a cost-effective alternative to physical air-gapping for Indonesian SMEs is well-reasoned and highly practical [4, 18].
*   The research gaps (combining adaptive compression, air-gapped security, and multi-indicator validation) are clearly identified [8].

### Section 2: Penelitian Terkait (Related Work)
*   Table 1 is exceptionally well-constructed, comparing the proposed system to major literature across focus, methods, limitations, and contributions [11-14].
*   The contrast between their mitigation/recovery approach and mainstream machine-learning detection approaches is highly mature [16]. It correctly positions their system as complementary: acting as the last line of defense when early detection fails [16].

### Section 3: Metode (Methodology)
*   The "compress-then-encrypt" sequence is technically validated [22].
*   Figure 3's flowchart is clear but could benefit from English translations of the labels (e.g., "Mulai" -> "Start", "Selesai" -> "Finish", "Validasi" -> "Validate") to match international publication standards [33].
*   Equations 1 through 8 (Compression Ratio, Compression Factor, Storage Saving, Weighted Sum Model for Efficiency, and RTO/FPR/FNR metrics) are mathematically standard and correctly formulated [35-40].

### Section 4: Hasil dan Pembahasan (Results & Discussion)
*   Worthy of praise is Table 7, which records the CPU and RAM usage alongside repeated trials [56]. Showing that RAM footprints remain under 7 MB proves the system is lightweight enough for resource-constrained environments [57].
*   Figure 10 and Figure 13 (dashboards and bar plots) are highly readable and provide clear empirical backing for the conclusions [56, 68, 69].
*   *Minor Correction:* In Table 14, explain why the file sizes changed for "Encrypt and Hold" (667 KB) vs. metadata corruption (501 KB) after the attack [76]. This is likely due to the headers or encryption padding, but a brief sentence explaining this behavior will aid reader understanding.

### Section 5: Kesimpulan (Conclusion)
*   The conclusion is realistic and avoids overclaiming success, explicitly noting the limitations of synthetic data and rule-based selection [93].
*   The proposed future directions (Machine Learning selectors, testing real malware in sandboxes, zero-trust backups, zero-trust architectures, and WORM storage) are outstanding and show a deep roadmap for academic expansion [93, 94].

---

## SUMMARY OF REVIEW RECOMMENDATIONS
1.  **Reframe the 0% FPR/FNR claim** in the Abstract and Section 4 to reflect its status as a controlled functional validation of hash integrity rather than a live malware detection rate [89].
2.  **Add a brief discussion on scaling,** potentially proposing the use of standard corpora (e.g., Silesia) for future benchmark validation [27].
3.  **Translate all figure labels** (Figures 1, 2, 3, 11, 15) to English to align with standard international review procedures [23, 29, 33, 66, 80].
4.  **Incorporate a brief discussion on Logical Air-Gap security trade-offs** (specifically the risk of malware hijacking the mounted volume) and how to mitigate them (IAM roles, read-only mounts) [65].

*This report represents a constructive review aimed at elevating this draft to publishable standards in high-impact journals like IJECE [1].*
