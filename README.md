# Class Imbalance, Calibration, and Class-Prior Shift

Kerangka eksperimen untuk dataset **UCI Online Shoppers Purchasing Intention**.
Program mengikuti diagram alur proyek:

1. stratified split menjadi training, calibration, dan test;
2. preprocessing hanya di-fit pada training;
3. Logistic Regression dengan baseline, random oversampling, atau class weighting;
4. probabilitas raw atau Platt scaling yang di-fit pada calibration set;
5. simulasi prevalensi positif test sebesar 10%, 15.5%, dan 25%;
6. evaluasi tanpa/dengan prior correction;
7. perbandingan Brier score, log loss, PR-AUC, F1, ECE, dan reliability diagram.

## Menjalankan

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_experiment.py
```

Eksperimen berulang dengan 10 seed:

```bash
python run_experiment.py --seeds 42 43 44 45 46 47 48 49 50 51
```

Hasil disimpan di `outputs/`:

- `experiment_results.csv`: satu baris untuk setiap kombinasi perlakuan;
- `split_summary.csv`: ukuran dan prevalensi setiap split;
- `reliability_diagrams.png`: kurva reliabilitas seluruh kombinasi;
- `metric_summary.png`: ringkasan Brier score dan log loss.
- `repetitions/seed_<N>/`: hasil, grafik, ringkasan split, dan audit leakage per seed;
- `all_repetitions.csv`: seluruh hasil per pengulangan;
- `aggregate_summary.csv`: mean, standard deviation, jumlah pengulangan, dan CI 95%;
- `all_audits.csv`: bukti pemisahan data dan identitas shifted test sample.
- `audit_results_10_seeds/`: folder mandiri untuk audit prior correction dan analisis statistik berpasangan.

Analisis statistik dapat direproduksi dengan:

```bash
python audit_and_paired_analysis.py
```

## Stage-1 remediation

Output baru membedakan jalur konfirmatori dan eksploratori. `Platt + prior correction`
adalah jalur utama; `raw + prior correction` diberi label `naive_exploratory`.
Target prior simulasi selalu diberi metadata `target_prior_source=oracle_simulator`.
Gunakan `average_precision` sebagai nama metrik; `pr_auc` dipertahankan hanya sebagai
alias kompatibilitas. Laporan dan smoke test tersedia di `audit_stage1/remediation/`.

Protokol konfirmatori 30 seed telah dibekukan dalam
`STATISTICAL_ANALYSIS_PLAN.md`, `confirmatory_protocol.json`, dan
`confirmatory_protocol_freeze.json`. Mode `--confirmatory` wajib memakai freeze
manifest dan akan menolak konfigurasi yang berbeda sebelum membuat output.

Contoh konfigurasi:

```bash
python run_experiment.py \
  --data online_shoppers_intention.csv \
  --prevalences 0.10 0.155 0.25 \
  --test-size 0.20 \
  --calibration-size 0.20 \
  --seeds 42 43 44 45 46 47 48 49 50 51
```

`--calibration-size 0.20` berarti 20% dari seluruh dataset. Training mendapat
sisa 60% ketika test juga 20%.

## Catatan metodologis

- Calibration dan test tidak pernah di-resample.
- Indeks train, calibration, dan test diaudit agar saling lepas pada setiap seed.
- Shifted test diaudit agar unik dan seluruh observasinya hanya berasal dari test set.
- Platt scaling dilatih pada calibration set terpisah, bukan data training.
- Simulasi shift hanya mengubah proporsi kelas dengan subsampling; distribusi
  fitur kondisional per kelas diasumsikan tetap (label/class-prior shift).
- Prior correction menggunakan prevalensi calibration set sebagai prior sumber.
  Ini membuat prior referensi konsisten antarmetode. Untuk model raw hasil
  oversampling/class weighting, asumsi probabilitas terkalibrasi mungkin tidak
  terpenuhi; justru efek pelanggaran tersebut merupakan bagian dari perbandingan.
- F1 memakai threshold 0.5. PR-AUC tidak berubah oleh prior correction monoton
  pada sampel uji yang sama, tetapi tetap dicatat untuk kelengkapan.

