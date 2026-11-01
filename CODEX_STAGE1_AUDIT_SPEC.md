# CODEX TASK SPEC — Tahap 1: Audit Metodologi dan Source Code

**Proyek:** Assessing Probability Reliability under Class Prior Shift: The Effects of Imbalance Handling and Calibration in Online Purchase Prediction  
**Versi spesifikasi:** 1.0  
**Status:** Audit-only by default; jangan mengubah eksperimen tanpa persetujuan.  
**Dataset:** UCI Online Shoppers Purchasing Intention (12.330 sesi, 17 prediktor, target `Revenue`).

## 0. Misi dan batasan

Audit repository eksperimen yang telah menghasilkan 10 pengulangan (seed 42–51), 36 kombinasi/seed, 360 hasil evaluasi. Verifikasi metodologi, reproducibility, dan kualitas output dengan **bukti dari kode, tes, dan artefak**. Hasil terdahulu adalah *baseline historis*, bukan ground truth yang harus dipaksakan. Jangan mengklaim audit PASS hanya dari CSV. Jika file tidak tersedia, tandai `NOT_VERIFIABLE`, bukan PASS.

**Jangan:** mengganti dataset, menambah model/metode, mengubah parameter, menghapus file, melakukan tuning berdasarkan test set, mengubah data hasil, atau menjalankan eksperimen besar tanpa persetujuan. Hindari memperbaiki bug secara diam-diam. Perubahan yang tidak mengubah perilaku (tes, logging, dokumentasi) boleh dibuat setelah menjelaskan cakupannya; perbaikan perilaku buat proposal patch terpisah.

## 1. Input yang harus ditemukan

- Entry point eksperimen dan modul preprocessing, split, sampling, training, calibration, prior correction, evaluation.
- Dataset CSV dan sumbernya, atau petunjuk pengunduhan; cek hash SHA-256 jika tersedia.
- Config: `prevalences=[0.10,0.155,0.25]`, `test_size=0.2`, `calibration_size=0.2` dari **total** dataset, `seeds=42..51`, `n_bins=10`.
- Artefak historis bila tersedia: `all_repetitions.csv`, `aggregate_summary.csv`, `all_audits.csv`, laporan statistik, requirements/lockfile.
- Jika nama/path berbeda, gunakan yang benar-benar ditemukan; jangan membuat asumsi tentang struktur repo.

## 2. Prosedur awal Codex

1. Inventaris struktur repo, identifikasi command eksekusi dan versi dependency. Catat commit SHA (jika git), environment, hash dataset.
2. Baca seluruh jalur eksekusi dari data loading hingga penyimpanan CSV. Buat diagram dependency sederhana dan daftar fungsi/kelas yang terlibat.
3. Jalankan tes yang sudah ada. Jika tes belum ada, tambahkan tes terisolasi dengan fixture sintetis; jangan mengubah hasil historis.
4. Audit setiap kontrol di bawah. Untuk setiap temuan, tulis `ID`, `severity`, `status`, `evidence path:line`, `observed`, `expected`, `impact`, `recommended fix`, `verification test`.
5. Jalankan *smoke test* kecil yang reproducible hanya bila aman dan tidak menimpa artefak historis. Gunakan direktori output terpisah.
6. Ringkas keputusan GO/NO-GO untuk eksperimen konfirmasi 30 seed.

## 3. Checklist audit wajib

### A01 — Integritas dataset
- Pastikan `Revenue` biner; periksa shape, nama/tipe kolom, missingness, nilai kategori, distribusi target, sumber data.
- Dataset UCI asli: 12.330 baris dan 18 kolom termasuk target; bila berbeda, cari alasan dan dokumentasikan.
- Jangan deduplikasi otomatis: baris identik tidak selalu sesi yang sama.
- **Tes:** validasi schema dan checksum; cek tidak ada target masuk daftar fitur.

### A02 — Data splitting dan independensi
- Periksa `train/calibration/test` tidak overlap berdasarkan indeks/identitas baris, dan mencakup dataset yang diharapkan.
- Konfigurasi historis 60%/20%/20% total (7.398/2.466/2.466), dengan stratifikasi pada setiap split.
- Periksa tidak ada transformasi data global yang mempelajari statistik sebelum split.
- Periksa pemilihan hyperparameter, threshold, dan metode tidak menggunakan label test.
- **Tes:** disjoint index sets, ukuran, proporsi target, determinisme per seed.

### A03 — Preprocessing
- Imputer, scaler, encoder, dan pemilihan fitur hanya di-`fit` pada train; calibration/test hanya `transform`.
- Periksa fitur kategorikal (misalnya Month, VisitorType, Weekend) dan numeric diproses sesuai tipe, termasuk `handle_unknown`.
- Pastikan pipeline baseline/ROS/class weight memakai definisi fitur dan transformasi yang konsisten.
- **Tes:** ubah fitur test pada fixture dan pastikan statistik transform train tidak berubah.

### A04 — Imbalance handling
- Baseline: tanpa resampling/weighting; ROS: hanya train; class weighting: hanya model, tidak double count dengan ROS.
- Verifikasi class weight dihitung dari training fold, jumlah dan prevalensi pasca-ROS tercatat.
- Catat apakah ROS dilakukan sebelum/ sesudah encoding dan konsekuensinya; untuk ROS, replikasi baris train saja.
- **Tes:** calibration/test tidak berubah akibat ROS; label distribusi pada train sesuai desain.

### A05 — Model dan probability calibration
- Verifikasi LogisticRegression config, solver, `max_iter`, konvergensi, random_state dan prediksi probabilitas raw.
- Platt scaling harus di-`fit` pada calibration set alami yang terpisah, dari skor model yang dibekukan; tidak refit base model dengan calibration secara tidak sengaja.
- Dokumentasikan input kalibrator: decision_function/logit atau probability; konsisten pada inferensi.
- Periksa calibration set belum pernah di-resample, tidak menjadi bagian training, dan tidak digunakan untuk memilih hasil terbaik setelah melihat test.
- **Tes:** input/target calibration sesuai indeks, output probabilitas finite dalam [0,1], tidak ada akses ke label test.

### A06 — Simulasi *class prior shift*
- Bentuk skenario dari test pool saja, dengan sampling acak bersyarat kelas; jangan berdasarkan skor/fitur.
- Simpan `seed`, target prevalence, actual prevalence, `n_positive`, `n_negative`, `n_total`, hash/indeks sampel.
- Periksa keunikan indeks dalam skenario jika sampling tanpa replacement; overlap antarskenario boleh terjadi dan harus diakui.
- Periksa kelayakan jumlah sampel dan apakah `P(X|Y)` tidak sengaja diubah oleh sampling berbasis fitur.
- **Tes:** semua indeks skenario subset test pool; prevalensi aktual sesuai toleransi rounding; tidak ada duplikasi dalam satu skenario.
- **Batasan:** subsampling dari satu test pool hanya mensimulasikan prior shift secara kondisional, bukan bukti adanya shift nyata dalam produksi.

### A07 — Prior probability correction (kritikal)
- Verifikasi fungsi odds correction untuk `0 < pi_source, pi_target < 1`:
  `alpha = (pi_target/(1-pi_target))/(pi_source/(1-pi_source))`
  `p_target = alpha*p_source/(alpha*p_source + 1-p_source)`.
- `pi_source` harus prevalensi **distribusi yang direpresentasikan oleh probabilitas yang sudah terkalibrasi**, bukan otomatis prevalensi train setelah ROS. Untuk Platt pada calibration alami, gunakan prevalensi sumber alami/calibration yang sesuai, dengan catatan finite-sample calibration error.
- Jangan memperlakukan probabilitas raw dari ROS/class weighting sebagai probabilitas sumber terkalibrasi. Jika hasil historis raw+correction tetap dianalisis, labeli `naive / exploratory`, bukan jalur utama.
- Periksa tidak ada penggunaan label test untuk mengestimasi prior target pada skenario yang diklaim unsupervised. Jika target prior diberikan oleh simulator, tandai `oracle-known target prior`.
- **Tes unit:** identity (`pi_source==pi_target`), monotonicity, output bounds, kenaikan/penurunan odds saat prior target berubah, kasus p dekat 0/1, nilai non-finite ditangani.
- **Tes matematis:** bandingkan implementasi odds dengan bentuk `expit(logit(p)+logit(pi_target)-logit(pi_source))` pada fixture.
- **Asumsi:** prior shift mengandaikan `P_target(X|Y)=P_source(X|Y)`; probabilitas sumber cukup terkalibrasi dan label-shift target diketahui/diestimasi secara sah.

### A08 — Metrik dan output
- Brier dan log loss dihitung dari probabilitas, bukan label thresholded; pastikan clipping numerik untuk log loss.
- ECE: definisikan binning equal-width/equal-frequency, interval tepi, penanganan bin kosong dan `n_bins=10`.
- PR-AUC: bedakan `average_precision_score` (AP) dari trapezoidal area; labeli dengan tepat.
- F1: dokumentasikan threshold (mis. 0.5) dan `zero_division`.
- Pastikan setiap baris memiliki seed, model, strategy, calibration, prevalence, prior_correction, n_test, prior_source, prior_target, metrik.
- Periksa uniknya kunci konfigurasi dan kelengkapan kombinasi; hasil historis diharapkan 10×36=360, tetapi audit **jangan** memaksakan 36 jika definisi desain berubah.
- Agregasi harus dihitung dari baris eksperimen, bukan mencampur skenario secara tidak sengaja; laporkan per-prevalensi dan per-strategi, bukan hanya grand mean.
- **Tes:** hitung ulang metrik pada fixture dengan sklearn dan verifikasi agregasi terhadap raw rows.

### A09 — Reproduksibilitas
- Dokumentasikan versi Python, numpy, pandas, sklearn, imbalanced-learn, library lain; konfigurasi model, hash dataset, seed, commit SHA.
- Periksa setiap sumber randomness di-supply seed yang relevan (split, ROS, scenario sampling, model jika stochastic).
- Ulangi satu seed ke output sementara dan bandingkan hasil dengan toleransi numerik yang didefinisikan.
- Jangan overwrite file eksperimen historis; keluaran audit di folder terpisah.

### A10 — Audit statistik (scope terbatas)
- Verifikasi pasangan berasal dari seed/split/skenario yang sama dan tanda selisih metrik konsisten.
- Cek apakah keluarga uji Holm dan hipotesis ditentukan jelas; catat banyaknya uji dan keterbatasan n=10.
- Ingat: 10 seed pada satu dataset **bukan** 10 populasi independen; CI antarseed tidak boleh dipresentasikan sebagai generalisasi populasi.
- Tahap ini memeriksa *traceability* statistik; **jangan** mengubah keputusan hipotesis utama tanpa Tahap 2.

## 4. Status dan severity

Status: `PASS`, `FAIL`, `NEEDS_REVIEW`, `NOT_VERIFIABLE`, `NOT_APPLICABLE`.
Severity: `CRITICAL` (leakage, salah prior correction, test label leakage, metrik salah), `HIGH` (calibration fit salah, sampling bias, reproduksi gagal), `MEDIUM` (metadata/logging/aggregation ambiguity), `LOW` (format dokumentasi).

GO untuk eksperimen konfirmasi hanya jika tidak ada `CRITICAL` atau `HIGH` unresolved, dan semua pemeriksaan kritis dapat diverifikasi. Jika belum, putuskan `NO-GO` disertai langkah perbaikan.

## 5. Artefak yang harus dihasilkan

Buat di `audit_stage1/` (atau lokasi setara sesuai repo):

```text
audit_stage1/
  audit_report.md
  audit_findings.csv
  audit_checks.json
  pipeline_map.md
  reproducibility_manifest.json
  proposed_fixes.md
  smoke_test_results/
```

`audit_findings.csv`: `id,category,severity,status,file,line,observed,expected,impact,recommendation,test_reference`.

`audit_checks.json`: machine-readable list audit checks, status, evidence, notes, executed_at, command, exit_code.

`audit_report.md` wajib berisi: ringkasan eksekutif; scope; artefak yang tersedia/hilang; matriks PASS/FAIL; detail temuan dengan bukti `path:line`; hasil tes; dampak pada 360 hasil historis (valid / perlu re-run / belum dapat dipastikan); rekomendasi patch; keputusan GO/NO-GO.

## 6. Acceptance criteria

- [ ] Jalur data dan kode eksperimen dipetakan dengan bukti path:line.
- [ ] Audit A01–A10 memiliki status dan evidence; tidak ada PASS tanpa bukti.
- [ ] Tes untuk split isolation, leakage, prior correction, scenario sampling, metric correctness tersedia dan berjalan.
- [ ] Semua output historis dipertahankan tanpa modifikasi.
- [ ] Hasil smoke test dapat direproduksi, atau alasan kegagalan dijelaskan.
- [ ] Prior correction raw vs calibrated dibedakan secara eksplisit.
- [ ] Laporan menyatakan keputusan GO/NO-GO serta patch yang diperlukan.

## 7. Instruksi eksekusi untuk Codex

> Audit repository ini berdasarkan `CODEX_STAGE1_AUDIT_SPEC.md`. Mulai dengan membaca struktur repository, konfigurasi, source code, dan artefak eksperimen yang benar-benar tersedia. Lakukan audit A01–A10 dengan bukti file dan nomor baris. Jangan mengubah algoritma, dataset, parameter, atau hasil historis. Tambahkan tes non-destruktif bila diperlukan dan jalankan smoke test pada output terpisah. Hasilkan seluruh artefak `audit_stage1/` serta ringkasan temuan kritis, dampak terhadap hasil 10 seed, dan keputusan GO/NO-GO. Untuk perubahan yang memengaruhi perilaku eksperimen, buat proposal patch dan tunggu persetujuan sebelum menerapkannya.
