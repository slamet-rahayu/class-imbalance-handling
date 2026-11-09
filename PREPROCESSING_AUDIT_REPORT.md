# PREPROCESSING AUDIT REPORT

Tanggal audit: 7 November 2026 (Asia/Jakarta). Eksperimen: `confirmatory-30seed-v2`; commit rujukan `2f448140cbdf5a593d1d182f26ef955d83cc717b`.

## 1. Executive Summary

**Kesimpulan terbatas: tidak ditemukan kebocoran fitting preprocessing, model utama, atau Platt calibrator dari calibration/test pada jalur source yang diperiksa. Namun, pipeline tidak dapat dinyatakan bebas seluruh bentuk leakage.** Ada risiko duplikasi konten antarpartisi dan ketidakpastian ketersediaan fitur pada waktu prediksi. Pemisahan berdasarkan indeks tidak menjamin pemisahan berdasarkan konten atau entitas.

Preprocessing aktual terdiri atas pemetaan target menjadi integer biner, pemilihan fitur berdasarkan dtype, `StandardScaler` untuk 15 kolom numerik/Boolean, serta `OneHotEncoder(handle_unknown="ignore")` untuk **dua** kolom teks (`Month`, `VisitorType`). Empat fitur kategori berkode angka dan `Weekend` diperlakukan sebagai numerik; bukan seluruh fitur yang secara semantik kategorikal di-one-hot encode. Missing values ditolak, bukan diimputasi. Deduplication, feature selection, dan feature engineering baru tidak ditemukan.

Data mempunyai 12.330 observasi, 17 prediktor, 1.908 positif, 10.422 negatif, tanpa missing value. Ditemukan **125 baris duplikat berlebih**, mencakup **201 baris anggota kelompok duplikat**. Pada masing-masing dari 30 split, indeks train/calibration/test disjoint; tetapi train dan test berbagi **16–32 kelompok konten identik**. Temuan ini diklasifikasikan **RISK**, bukan bukti bahwa rekaman tersebut pasti merupakan orang/sesi yang sama.

Audit dilakukan dengan membaca source, JSON notebook, konfigurasi, dataset, dan output tersimpan; hanya merekonstruksi indeks split dan menghitung diagnostik dataset. Tidak dilakukan model fitting, preprocessing fitting, eksekusi notebook, maupun pengulangan eksperimen. Satu-satunya file baru adalah laporan ini. Seluruh 198 file dalam manifest hash output asli masih sesuai saat pemeriksaan.

## 2. Dataset and Feature Identification

### 2.1 Identitas dan pembacaan

Sumber: UCI Online Shoppers Purchasing Intention, ID 468, DOI `10.24432/C5F88Q`; file lokal `online_shoppers_intention.csv`. Bukti: `DATASET_PROVENANCE.md:3–13` dan `run_experiment.py:61–69` (`DATASET_PROVENANCE`). SHA-256 lokal adalah `b3055ee355f59134d851d32641183cb4a8b45def7124d2f50442a042f358e0d9` (`confirmatory_protocol_v2.json:3`). Tanggal unduh lokal tidak tercatat.

`load_data`, `run_experiment.py:126–138`, menggunakan `pd.read_csv`, menolak missing value, membentuk `y`, lalu menghapus `Revenue` dari `X`. Penghitungan read-only dataset mengonfirmasi 12.330 × 18 kolom, yaitu 17 prediktor dan satu target. Distribusi kelas: negatif 10.422 (84,525547%), positif 1.908 (15,474453%; proporsi 0,15474452554744525). `Revenue` tidak diteruskan sebagai prediktor.

### 2.2 Routing fitur yang benar-benar diterapkan

Dasar routing adalah `pd.api.types.is_numeric_dtype`, bukan kamus semantik fitur (`make_preprocessor`, `run_experiment.py:157–167`). Dtype berikut diperiksa langsung menggunakan environment proyek; string dapat diberi label `str` atau `object` oleh versi pandas lain, tetapi keduanya masuk jalur nonnumerik.

| Fitur | Dtype pembacaan saat audit | Jalur aktual |
|---|---|---|
| Administrative | int64 | StandardScaler |
| Administrative_Duration | float64 | StandardScaler |
| Informational | int64 | StandardScaler |
| Informational_Duration | float64 | StandardScaler |
| ProductRelated | int64 | StandardScaler |
| ProductRelated_Duration | float64 | StandardScaler |
| BounceRates | float64 | StandardScaler |
| ExitRates | float64 | StandardScaler |
| PageValues | float64 | StandardScaler |
| SpecialDay | float64 | StandardScaler |
| Month | string | OneHotEncoder |
| OperatingSystems | int64 | StandardScaler |
| Browser | int64 | StandardScaler |
| Region | int64 | StandardScaler |
| TrafficType | int64 | StandardScaler |
| VisitorType | string | OneHotEncoder |
| Weekend | bool | StandardScaler |

**Fakta:** kode angka kategori diberi perlakuan numerik; tidak ada `OrdinalEncoder` yang mempelajari urutan kategori. **Risiko metodologis:** LR kemudian dapat memodelkan efek linear atas urutan kode yang sebenarnya nominal. Ini bukan kebocoran target, tetapi pilihan representasi yang harus diungkapkan. UCI mendeskripsikan sistem operasi, browser, wilayah, dan jenis trafik sebagai atribut kategori; implementasi aktual tetap ditentukan dtype. [Metadata resmi UCI](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset).

### 2.3 Missing values, duplikasi, dan fitur yang dikeluarkan

- Missing value aktual: **0**. `load_data:130–131` menghentikan proses jika missing value ditemukan. Tidak ada imputasi atau penghapusan baris missing secara diam-diam.
- Duplikat penuh berlebih: **125** (`D.duplicated().sum()`). Jumlah baris dalam kelompok duplikat: **201** (`D.duplicated(keep=False).sum()`). Setelah target dihapus, jumlah duplikat prediktor berlebih juga **125**. Source tidak memanggil `drop_duplicates` pada dataset (`load_data:126–138`).
- Hanya `Revenue` dikeluarkan dari prediktor (`load_data:138`). Tidak ditemukan penghapusan `PageValues`, ID kolom, fitur konstan, atau outlier. Indeks baris dipakai sebagai ID audit dan tidak menjadi fitur model (`run_repetition:393–407`).
- Target dikonversi dengan mapping Boolean/string TRUE/FALSE; fallback `pd.to_numeric`; validasi {0,1}; lalu `astype(int)` (`load_data:133–138`). Ini encoding **target**, bukan label encoding fitur.
- Tidak ada bukti target masuk ke `StandardScaler` atau `OneHotEncoder`. `y` memang dipakai untuk stratifikasi, resampling, supervised fitting, calibration, dan simulasi shift; penggunaan ini harus dibedakan dari target sebagai prediktor.

## 3. Actual Preprocessing Implementation

| Teknik / library | Fitur dan tahap | Cakupan fitting dan penggunaan | Bukti fungsi/file/baris |
|---|---|---|---|
| Parsing CSV, pandas | Seluruh kolom saat loading | Inferensi dtype; bukan estimasi parameter statistik fitur | `run_experiment.py`, `load_data:126–138` |
| Target mapping dan cast | Revenue → y integer | Sebelum splitting; tidak mempelajari statistik data | `load_data:133–138` |
| StandardScaler, sklearn.preprocessing | 15 kolom pada tabel routing | `fit_transform(X_train)` saja; statistik training sebelum ROS | `make_preprocessor:157–167`; `fit_model:170–172` |
| OneHotEncoder, sklearn.preprocessing | Month, VisitorType | Kategori dipelajari dari training; `handle_unknown="ignore"`; kategori calibration/test tidak dipakai untuk fit | `make_preprocessor:165`; `fit_model:172` |
| ColumnTransformer, sklearn.compose | Menggabungkan jalur numerik dan kategorikal | Daftar kolom berdasarkan X_train; seluruh 17 prediktor masuk salah satu jalur | `make_preprocessor:157–167` |
| Pipeline, sklearn.pipeline | Preprocessor dan model yang sudah fit | Dirakit setelah fit; `predict_proba` menjalankan transform preprocessor sebelum prediksi LR; tidak refit | `fit_model:218–219`; `run_repetition:419–420` |
| RandomOverSampler, imblearn | Matriks training hasil preprocessing | `fit_resample` hanya training, sesudah scaler/OHE fit; bukan transform calibration/test | `fit_model:175–177` |
| Clipping dan logit manual, numpy | Probabilitas calibration/test | Transformasi deterministik untuk Platt; bukan transformasi prediktor asli | `fit_platt_scaler:222–227`; `apply_platt:234–236` |
| Clipping dan koreksi odds | Probabilitas setelah raw/Platt | Parameter source dari y_cal dan target dari skenario oracle | `prior_correct:256–270`; `run_repetition:383,444–453` |

`StandardScaler()` dan `OneHotEncoder(...)` selain `handle_unknown` tidak menerima override di source. Karena itu scaler memakai perilaku default library yang dibekukan: centering dan variance scaling; OHE tidak meminta drop salah satu kategori atau mengelompokkan kategori langka. Parameter statistik fitted/scaler dan vocabulary OHE tidak disimpan sebagai model artifacts; identitas numeriknya antarstrategi tidak diuji ulang dengan fitting dalam audit read-only ini. Kesamaan input, pemanggilan, dan konfigurasi terverifikasi secara struktural.

**Tidak ditemukan dalam implementasi yang diperiksa:** MinMaxScaler, normalisasi lain, OrdinalEncoder, LabelEncoder untuk fitur, imputasi, penghapusan duplikat, feature selection, PCA, target encoding, pembuatan interaction/polynomial features, log transform fitur asli, penghapusan outlier, tuning hyperparameter atau cross-validation untuk memilih parameter. Transformasi logit adalah atas probabilitas untuk calibration, bukan log transform durasi/count.

Presisi implementasi Platt: `log(clip(p, EPS, 1-EPS) / clip(1-p, EPS, 1))`, `EPS=1e-12`, lalu logistic calibration satu dimensi. Ini mendekati logit probabilitas clipped, tetapi numerator dan denominator di-clip terpisah; jangan menggantinya dengan asumsi bahwa yang dipakai langsung adalah `decision_function`. Bukti: `run_experiment.py:36,222–236`.

## 4. Data Splitting and Leakage Assessment

### 4.1 Pemisahan dan batas fitting — PASS

`split_data:141–154` memisahkan 20% test terlebih dahulu dengan stratifikasi y dan seed s; kemudian mengambil calibration 0,20/(1−0,20)=0,25 dari development, memakai seed s+1. Hasil: 7.398 training, 2.466 calibration, 2.466 test per seed. `run_repetition:366–373` memanggil splitting sebelum fitting serta memvalidasi disjointness indeks dan cakupan dataset.

Audit independen merekonstruksi indeks untuk semua seed 42–71 dengan dua `train_test_split` yang sama: seluruh 30 seed disjoint berdasarkan indeks dan mencakup seluruh 12.330 ID. Tidak ada model atau scaler yang difit ulang. Pemakaian y untuk stratifikasi adalah bagian desain, bukan target dimasukkan ke fitur.

`fit_model` hanya menerima `X_train,y_train` (`170–188`). `p_cal_raw` dan `p_test_raw` dibuat melalui pipeline fitted (`419–420`). `fit_platt_scaler` menerima `p_cal_raw,y_cal` (`421`, `222–227`), bukan test labels. Base model tidak direfit menggunakan calibration. Test probabilities hanya diterapkan melalui `apply_platt` (`437–440`). Tidak ditemukan perhitungan mean/std atau vocabulary fitur menggunakan seluruh dataset; pengecekan missing sebelum splitting hanya validasi input, tidak mempelajari parameter preprocessing.

### 4.2 Disjoint ID tidak sama dengan disjoint konten — RISK

Diagnostik read-only memakai `pd.util.hash_pandas_object(D,index=False)` atas seluruh kolom, serta hashing ulang atas prediktor saja. Untuk setiap seed, jumlah **kelompok konten identik yang hadir pada kedua partisi** adalah:

| Pasangan partisi | Minimum | Maksimum | Rata-rata 30 seed |
|---|---:|---:|---:|
| Training–calibration | 17 | 34 | 24,2333 |
| Training–test | 16 | 32 | 22,5333 |
| Calibration–test | 6 | 15 | 10,0667 |

Hasil hashing prediktor saja sama. Angka tersebut menghitung kelompok konten bersama, bukan jumlah orang atau estimasi bias. Kesamaan konten terverifikasi, tetapi apakah itu rekaman sesi yang tersalin, sesi independen dengan ciri identik, atau agregasi yang sama **UNVERIFIED**. Karena ID pengguna/session asli tidak tersedia, jangan menyatakan “duplikasi entitas terbukti”. Assertion source hanya melindungi indeks unik, bukan konten unik (`369–373`, `394–397`).

### 4.3 Oracle prevalence — PASS bersyarat pada estimand simulasi

`simulate_prior_shift` menggunakan label test untuk mengambil sampel per kelas tanpa replacement (`239–253`). `actual_prior=y_shifted.mean()` kemudian digunakan sebagai parameter global koreksi odds (`444–453`). Ini memang memakai informasi label test, tetapi **secara eksplisit sebagai target prior oracle** (`469`, `confirmatory_protocol_v2.json:18–20`); bukan memasukkan label individual ke model atau calibrator. Simulasi tidak memvalidasi metode adaptasi tanpa label untuk deployment. Jika naskah mengklaim target prior tersedia tanpa label, klaim itu bertentangan dengan implementasi.

### 4.4 Overlap antar-repetition — RISK bagi inferensi

Overlap ini disengaja oleh repeated random splits dan tidak membuktikan leakage di dalam satu repetition. File `scientific_validation_followup/OVERLAP_SUMMARY.csv:2,6–7` menunjukkan rata-rata per pasangan seed: training 4.438,86 ID (~60%), calibration 493,24 (~20%), test 493,02 (~20%). Dampaknya adalah ketergantungan statistik; 30 seed bukan 30 dataset independen. Jangan menafsirkan Wilcoxon/Holm atau interval antarsplit sebagai bukti populasi independen.

### 4.5 Fitur dengan waktu pembentukan tidak diketahui — UNVERIFIED

`PageValues`, `BounceRates`, dan `ExitRates` diterima langsung dari CSV, tanpa rekonstruksi statistik historis per split (`load_data:126–138`, `make_preprocessor:157–167`). Metadata [UCI](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset) menyebut metrik Google Analytics dan mendeskripsikan Page Value berkaitan dengan nilai halaman sebelum transaksi. Namun metadata itu tidak cukup untuk memastikan kapan statistik dihitung, apakah mencakup informasi outcome dari periode evaluasi, atau kapan semua fitur tersedia untuk keputusan produksi. Source tidak membuat target-derived feature lokal; keamanan temporal/provenance fitur hulu tetap belum terverifikasi. Jangan menyebut PageValues “terbukti leakage” hanya dari korelasi atau nama fitur.

## 5. Consistency Across Training Strategies

Ketiga strategi memanggil `fit_model(X_train,y_train,strategy,seed)` atas split yang sama (`run_repetition:417–421`). Preprocessor baru dibuat terpisah untuk setiap strategi, tetapi memakai fungsi, fitur, konfigurasi, dan input training sebelum resampling yang sama. Karena scaler/OHE tidak dipengaruhi strategi, desain preprocessing konsisten.

| Strategi | Data fitting utama | class_weight | Bukti tersimpan dan source |
|---|---|---|---|
| Baseline | 7.398 baris asli | None | `fit_model:174–188`; `training_metadata.csv`, baris `strategy=baseline` |
| ROS | 12.506–12.508 baris setelah duplikasi minority training; jumlah kedua kelas sama 6.253–6.254 | None | `fit_model:175–177`; metadata `train_*_after` |
| CW | 7.398 baris asli | balanced | `fit_model:174,181–188`; metadata effective weights |

CW menggunakan rumus `n/(2*n_c)`: bobot negatif berkisar 0,591461–0,591556 dan positif 3,230568–3,233392. Rumus metadata ada pada `fit_model:194–200`, sedangkan fitting memakai `class_weight="balanced"` dari sklearn. Baseline/ROS mempunyai bobot metadata 1,0. ROS memakai default sampling_strategy `auto`, setara menyeimbangkan minoritas ke mayoritas pada data ini, serta random_state=seed. Tidak ada ROS pada calibration/test; sampler tidak dipasang dalam prediction pipeline (`218–219`).

Model utama memakai `solver="liblinear"`, `penalty="l2"`, C=1, max_iter=2000, random_state=seed (`run_experiment.py:38–43,181–185`; `confirmatory_protocol_v2.json:26`). Platt memakai lbfgs, L2, C=1, max_iter=100, random_state=0 (`44–50`, `222–227`; konfigurasi baris 27). Calibration tetap natural: 381–382 positif dari 2.466, tidak di-ROS dan tidak dibobot (`training_metadata.csv` serta `426–428`).

Perbedaan sampling dan pembobotan merupakan faktor desain. ROS menggandakan jumlah baris fitting, sedangkan CW mempertahankan jumlah baris; dengan C tetap, keduanya tidak harus memberikan solusi LR identik (normalisasi objective/regularisasi dan intercept juga relevan). Karena itu jangan mengklaim keduanya ekuivalen; audit ini tidak mengubah konfigurasi atau menguji objective alternatif.

## 6. Reconstructed Experimental Pipeline

Urutan eksekusi aktual di `run_repetition` berbeda dari urutan konseptual: **indeks skenario shift sudah dibuat sebelum model difit**. Ini aman terhadap fit sejauh label test tidak diteruskan ke fungsi fitting; skenario hanya menentukan posisi evaluasi.

1. `load_data`: **read_csv**, validasi missing/target, pisahkan X dan y (`366`; `126–138`).
2. `split_data`: dua **train_test_split**, kemudian pemeriksaan indeks disjoint (`367–373`).
3. Tentukan `source_prior` dari **mean y_cal** (`383`).
4. Buat indeks shifted test per prevalence dengan **class-stratified sampling tanpa replacement**; validasi ID dan simpan hash (`386–414`).
5. Untuk setiap strategi, buat **ColumnTransformer**, panggil **fit_transform(X_train)**; fit scaler/OHE sebelum resampling (`417–418`; `170–172`).
6. ROS saja: **fit_resample(X_transformed,y_train)**. Baseline dan CW menggunakan y_train asli (`174–179`).
7. Base LR: **fit(X_transformed,y_fit)**; rakit **Pipeline** berisi komponen fitted (`181–219`).
8. Pipeline **predict_proba(X_cal)** dan **predict_proba(X_test)**: preprocessor menjalankan **transform**, kemudian base LR probabilitas (`419–420`). Tidak ada `Pipeline.fit` kedua.
9. Platt: log transform deterministik probabilitas calibration, **calibrator.fit(logits,y_cal)** (`421`; `222–227`).
10. Terapkan Platt pada probabilitas full test menggunakan **calibrator.predict_proba** (`437–440`; `234–236`).
11. Ambil subset probabilitas dan y_test menggunakan indeks shift yang telah dibuat (`442–448`). Hitung realized prevalence (`445`).
12. Cabang koreksi memanggil **prior_correct**, tanpa fit, untuk raw dan Platt secara terpisah (`449–456`). Raw + Prior diberi label eksploratori (`461–464`).
13. **evaluate** memakai probabilitas akhir; hanya F1 yang memakai threshold 0,5, bukan base `model.predict` (`489`; `305–315`). Buat reliability bins/plots dan simpan ringkasan (`492–508`).

Notebook `notebooks/results_and_discussion.ipynb` adalah analisis output: pembacaan data pada baris JSON 124–127; pairing pada 795–801 dan 1053. Seluruh code cell diperiksa tanpa dieksekusi; tidak ditemukan `.fit(` atau `.fit_transform(`. Notebook bukan lokasi training ulang. `notebooks/build_notebook.py:47–86,95–114` mendukung pemeriksaan loading/validasi yang sama, tetapi notebook aktual tetap diperiksa tersendiri. Wrapper ekspor audit `scientific_validation_followup/export_predictions.py`, `main:56–87`, menggunakan helper frozen dengan input training/calibration/test yang sama; script tersebut hanya dibaca dalam audit ini. `audit_and_paired_analysis.py`, `main:268–285`, membaca hasil metrik dan tidak melakukan preprocessing fitur.

## 7. Findings and Evidence

Status: PASS = sesuai dengan bukti; RISK = indikasi risiko tanpa pelanggaran yang sudah terbukti; FAIL = pelanggaran terbukti; UNVERIFIED = bukti tidak cukup. Tidak ada FAIL fitting leakage yang dapat dibuktikan pada jalur yang diperiksa.

| ID | Komponen | Status | Temuan | Bukti File/Baris | Dampak |
|---|---|---|---|---|---|
| P01 | Target exclusion | PASS | Revenue dikeluarkan dari X; y biner | `run_experiment.py`, `load_data:133–138` | Tidak ada target sebagai prediktor lokal |
| P02 | Missing values | PASS | Dataset tanpa missing; jika ada, proses berhenti; tanpa imputasi | `load_data:127–131`; dataset CSV baris 1–12331 | Dokumentasi harus menyebut penolakan, bukan imputasi |
| P03 | Routing dtype | RISK | Empat kode kategori dan Weekend ikut scaling; hanya dua kolom di-OHE | `make_preprocessor:157–167`; CSV header baris 1 | Asumsi linear terhadap kode nominal; bukan target leakage |
| P04 | Fit preprocessor | PASS | Fit hanya X_train sebelum ROS | `fit_model:170–177` | Tidak ada estimasi mean/std/kategori dari test |
| P05 | Transform inference | PASS | Pipeline fitted digunakan untuk cal/test | `fit_model:218–219`; `run_repetition:419–420` | Transformasi sama, tanpa refit |
| P06 | Split indeks | PASS | Semua 30 seed disjoint ID; split sebelum fit | `split_data:141–154`; `run_repetition:366–373` | Mendukung isolasi fitting dalam repetition |
| P07 | Duplikat konten | RISK | 125 duplikat berlebih; 16–32 kelompok identik bersama train–test | Dataset baris 2–12331, diagnostik §4.2; `load_data:126–138`, `run_repetition:369–373` | Pemeriksaan indeks tidak menguji konten/entity independence |
| P08 | Asal duplikat/entitas | UNVERIFIED | Tidak ada ID sesi/pengguna asli untuk menafsirkan baris identik | CSV header baris 1; `load_data:138` | Tidak boleh mengasumsikan entitas sama atau independen |
| P09 | Baseline | PASS | Tanpa ROS dan class weighting | `fit_model:174–188` | Kontrol sesuai desain |
| P10 | ROS scope | PASS | Training saja setelah preprocessing; balanced counts | `fit_model:175–177,191–209`; metadata baris strategy ROS | Cal/test tetap natural sebelum shift |
| P11 | CW | PASS | Balanced pada model, n/(2n_c) | `fit_model:174,181–188,194–198` | Pembobotan sesuai desain |
| P12 | Konsistensi fitur | PASS | Fungsi preprocessor dan X_train yang sama untuk tiga strategi | `fit_model:170–172`; `run_repetition:417–418` | Tidak ada cabang feature engineering antarstrategi |
| P13 | Parameter fitted disimpan | UNVERIFIED | Tidak ada scaler/calibrator fitted artifact; kesamaan parameter tidak dicek ulang dengan fitting | `run_repetition:502–508` | Struktur terverifikasi, bukan inspeksi objek training historis |
| P14 | Calibration fitting | PASS | Hanya p_cal_raw,y_cal; base tidak direfit pada calibration | `run_repetition:419–421`; `fit_platt_scaler:222–227` | Tidak ada label test di calibrator |
| P15 | Oracle correction | PASS | Realized target prior dari label skenario, sengaja diketahui oracle | `run_repetition:444–453,469`; `prior_correct:256–270` | Sah untuk estimand oracle; tidak membuktikan adaptasi tanpa label |
| P16 | Fitur hulu/temporal | UNVERIFIED | Waktu dan sumber perhitungan PageValues/rates tidak bisa dipastikan dari CSV | `load_data:126–138`; metadata UCI, §4.5 | Generalisasi prediksi real-time belum aman diklaim |
| P17 | Antar-repetition | RISK | Reuse observasi dan fitting data antar-seed | `split_data:143–152`; `OVERLAP_SUMMARY.csv:2,6–7` | Pseudoreplikasi jika dianggap 30 sampel independen |
| P18 | Notebook | PASS | Analisis tabel output; tidak ada fit model/preprocessor | `notebooks/results_and_discussion.ipynb:124–127,795–801,1053` | Tidak memperkenalkan fitting leakage baru |
| P19 | Metrik | PASS | Implementasi scoring dan hasil verifikasi tersedia; bukan bukti hilangnya risiko provenance | `evaluate:305–315`; `scientific_validation_followup/independent_metric_verification.py:152–156`; `METRIC_RECOMPUTATION.csv` | Metrik numerik dapat benar walaupun independensi/provenance terbatas |

## 8. Scientific Validity Implications

**Validitas internal fitting:** didukung pemisahan indeks dan pembatasan input fit. Tidak ada alasan teknis dari source untuk menyatakan scaler/OHE atau calibrator telah memakai test labels saat fit. Namun general statement “bebas leakage” terlalu kuat karena duplikat konten dan pembentukan fitur hulu belum diselesaikan.

**Keadilan perbandingan:** ketiga strategi menerima representasi fitur dan skenario evaluasi identik. Pemilihan dtype untuk nominal codes berlaku sama pada semuanya, sehingga bukan perbedaan preprocessing antarstrategi. Meski demikian, representasi itu memengaruhi bentuk fungsi LR dan batas penerapan kesimpulan.

**Reliabilitas Brier/log loss/ECE:** source menghitung Brier/log loss dari probabilitas, F1 dari threshold, dan ECE dengan 10 equal-width bins (`288–315`). Verifikasi prediction-level yang sudah tersedia menunjukkan 3.240 perbandingan tanpa mismatch toleransi. Audit ini membaca bukti tersebut, tidak menghitung ulang eksperimen. Keakuratan perhitungan tidak membuktikan estimasi performa bebas bias duplikasi atau aman temporal.

**Platt dan prior correction:** Platt mempelajari transformasi skor pada calibration natural yang terpisah. Prior correction memakai prevalence oracle skenario, sehingga perubahan skor menggambarkan kondisi label-shift simulasi yang diketahui, bukan kemampuan menemukan prior tanpa label. Koreksi raw ROS/CW tidak boleh mendapat interpretasi teoretis setara probabilitas Platt yang sudah dikalibrasi.

**Reproduksibilitas:** routing berdasarkan dtype dapat diproduksi ulang dengan dependency lock. Klaim “semua kategorikal di-OHE” tidak mereproduksi source aktual dan harus diperbaiki. Overlap antarrepetition tetap membatasi inferensi; audit preprocessing ini tidak mengubah kesimpulan chronology maupun validitas p-value pada audit sebelumnya.

## 9. Recommendations

1. **Perbaiki dokumentasi Method:** sebutkan 15 kolom numerik/Boolean dan dua OHE secara eksplisit; jelaskan perlakuan numeric codes, tanpa menyatakan semua kategori di-OHE.
2. **Ungkapkan duplikasi:** laporkan 125 baris berlebih dan pemisahan berbasis ID. Telusuri apakah duplikat merupakan sesi independen atau record tersalin. Jangan menghapusnya dari frozen dataset.
3. **Tentukan prediction time dan provenance:** jelaskan kapan PageValues/rates tersedia dan apakah agregatnya dihitung dari informasi historis yang sah. Jika tidak tersedia, batasi klaim ke evaluasi offline atas fitur yang diberikan.
4. **Tidak perlu mengulang eksperimen hanya karena scaler/OHE:** audit tidak menemukan pelanggaran scope fit. Koreksi dokumentasi dan disclosure cukup untuk menyatakan implementasi yang benar.
5. **Eksperimen baru hanya bila pertanyaan berubah atau risiko terbukti:** jika investigasi membuktikan record sesi tersalin atau fitur menggunakan outcome masa depan, dibutuhkan desain baru dengan dedup/group split atau fitur yang tersedia saat keputusan. Jika penulis ingin memakai OHE untuk kode nominal, itu perubahan model/representasi yang memerlukan eksperimen baru berlabel terpisah, bukan koreksi diam-diam pada hasil frozen.
6. **Pertahankan interpretasi deskriptif:** jangan menganggap repeated splits independen; jangan memakai PASS preprocessing untuk mengangkat keseluruhan validitas ilmiah menjadi VALIDATED.

Diagnostik dapat direproduksi secara read-only dengan pandas dan sklearn dari lockfile: `D=pd.read_csv(...)`; `D.duplicated().sum()`; `D.duplicated(keep=False).sum()`; `X=D.drop(columns="Revenue")`; dua `train_test_split` pada indeks dengan stratifikasi y (test_size=0.2, seed s, lalu test_size=0.25, seed s+1); uji irisan set indeks; hitung irisan set hasil `pd.util.hash_pandas_object(D,index=False)` untuk setiap pasangan partisi. Ini tidak memerlukan fitting model atau menjalankan notebook.

## 10. Proposed Method Paragraph

The Revenue target was mapped to binary integer labels and excluded from the predictor matrix, while input records containing missing values were rejected rather than imputed. For each seed, the data were stratified into training, calibration, and test partitions comprising 60%, 20%, and 20% of the observations, respectively, and partition indices were checked for disjointness. Predictor routing was determined from the training-data dtypes: 15 numeric or Boolean columns, including OperatingSystems, Browser, Region, TrafficType, and Weekend, were standardized using StandardScaler, whereas Month and VisitorType were one-hot encoded with unknown categories ignored. Both transformations were fitted exclusively on the original training partition and reused through a fitted pipeline for calibration and test predictions. Random oversampling was applied only to transformed training observations to equalize the minority and majority class counts; the class-weighted alternative used balanced class weights without resampling, and the baseline used neither procedure. The base logistic regression model used L2 regularization with C=1, the liblinear solver, and a maximum of 2,000 iterations. A separate logistic calibration model was fitted to the clipped-probability log-odds and labels of the natural calibration partition. Test labels were used for class-stratified scenario construction and the realized target prior in the explicitly oracle-based probability correction, but were not supplied to the feature-transformer, base-model, or calibrator fitting procedures. Duplicate-valued records were retained, and partition disjointness was defined by row identifiers rather than content uniqueness.
