> Draf adaptasi dari SRS v0.1.0 lama. ID requirement dan nomor bagian dipertahankan untuk traceability. Bukti implementasi lama bukan hasil uji repo ini. [Indeks SRS](index.md).

### 5.3 `ml-classifier`

**Baseline sumber:** PRD v1.0.0. **Rincian teknis:** bagian ini. **Dependensi:** `activity-analysis`.

#### Tujuan dan penerimaan

| ID | Requirement | Acceptance dan bukti |
| --- | --- | --- |
| ML-01 | Dataset lab mempunyai label yang dapat dipertanggungjawabkan. | Dataset card mencatat skenario, run, seed, event/snapshot hashes, alasan label, peninjau, serta unknown/ambigu. Audit semua keluarga skenario dan ≥20% sampel tiap kelas; seluruh kasus ambigu direview. |
| ML-02 | Split memisahkan grup independen dan mengecualikan metadata identitas dari fitur. | Manifest menunjukkan tidak ada run/event/revisi bersama atau replay identik lintas split; kedua kelas tersedia pada tiap split. Pemeriksaan overlap dan kolom fitur harus lulus sebelum fit. |
| ML-03 | Satu Logistic Regression dilatih offline dengan konfigurasi dibekukan. | Fit preprocessing/koefisien hanya dari train; threshold dari validation. Jalankan ulang input/config/seed identik dan bandingkan parameter numerik serta prediksi hingga toleransi 1e-8; timestamp/hash paket run baru boleh berbeda. |
| ML-04 | Evaluasi final membandingkan ML, rules, dan Dummy secara adil. | Simpan prediksi per snapshot, confusion matrix, support, metrik terdefinisi/undefined, UP/UN, coverage aktual, hasil per-run, dan interval bootstrap. Ketiga metode memakai test yang sama sesudah kandidat dibekukan. |
| ML-05 | Paket lokal mempunyai identitas dan schema yang diverifikasi sebelum digunakan. | Hash/schema/urutan fitur/angka tidak valid ditolak. Prediksi paket sama dengan pipeline hasil fit hingga toleransi skor 1e-8. Perubahan paket/config menuntut restart dan menghasilkan versi eksplisit. |
| ML-06 | Inferensi lokal menghasilkan hasil yang terkait revisi input dan state proses. | Hanya snapshot READY diberi label. Crash/restart menghasilkan satu hasil per snapshot-revision/model hash. Paket tidak tersedia, input invalid, atau inferensi gagal menghasilkan label kosong dan alasan yang terlihat. |

#### Data dan label

Satu sampel adalah snapshot, bukan event. Target `normal`/`suspicious` berarti pola lab sesuai rubrik yang ditetapkan sebelum dataset final. Target tersebut tidak menyatakan niat manusia atau insiden nyata.

Keluarga skenario minimal: login sukses biasa; salah ketik lalu sukses; banyak pengguna dengan aktivitas wajar; kegagalan berulang satu akun; burst lintas akun; dan kasus sekitar ambang/batas window. Variasikan akun fiktif, jeda, urutan, volume, dan parameter antar-run. Label berasal dari rubrik dan pola yang benar-benar terlihat; menyalin keluaran rules menjadi label dilarang. Input identik yang mendapat label bertentangan dicatat sebagai ambigu. Unknown tidak diberi label 0.

Dataset offline boleh memakai simulasi waktu untuk menghemat durasi; event harus melalui kontrak dan ekstraktor yang sama. Bedakan bukti simulasi offline dari acceptance runtime dua VM. Pisahkan skenario gangguan/quality dari evaluasi klasifikasi dan sertakan keduanya dalam uji state hasil.

Target awal: ≥300 snapshot berlabel dari ≥50 run independen. Test memuat ≥30 snapshot dan ≥5 run berbeda pada masing-masing kelas; validation mempunyai kedua kelas. Ini batas demonstrasi proyek yang diusulkan, bukan jaminan daya statistik atau generalisasi. Bila support tidak cukup, tambah data atau revisi baseline sebelum membuka test.

CSV training memakai `sample_id`, `run_id`, `snapshot_id`, `revision`, `label`, serta tujuh kolom fitur berurutan AA-04. `label` adalah 0=normal, 1=suspicious, kosong=unknown; nilai lain ditolak. Manifest dataset menghubungkan sample ke event hashes, schema, skenario, label basis/reviewer, dan asal replay. Manifest split mencatat daftar sample/run per partisi, seed, rasio aktual, hash dataset, serta hasil pemeriksaan overlap. Metadata tambahan dinyatakan di manifest; input model tetap persis tujuh fitur.

Split `60/20/20` dihitung terhadap jumlah grup semula: test dan validation masing-masing `ceil(0,2 × N)`, sisanya train. Manifest memuat daftar grup dan rasio aktual. Seed 42; grouping berdasarkan run serta asal replay yang sama. Pemilihan manifest dapat menyeimbangkan kelas sebelum hasil model dilihat. Semua window/revisi satu run tetap satu split. Parameter persis/trace yang disalin tidak boleh tersebar lintas split.

#### Fit dan evaluasi

Kandidat tunggal: StandardScaler → Logistic Regression (`C=1`, `class_weight=balanced`, `solver=lbfgs`, `max_iter=1000`, seed 42). Tidak ada pencarian banyak model atau online learning. Threshold dipilih dari 0,05 sampai 0,95 dengan langkah 0,05 pada validation berdasarkan F1 suspicious; seri memilih threshold lebih tinggi. Tujuh fitur mengikuti AA-04; NaN atau field hilang ditolak.

Train/validation dipisahkan sebelum fitting transformasi; test tidak dipakai memilih konfigurasi, fitur, atau threshold. Prinsip ini mengikuti [panduan data leakage scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html). Pemisahan seluruh sampel dalam satu grup mengikuti [panduan grouped data](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data).

Bekukan kandidat, rules, manifest, dan threshold sebelum satu evaluasi test bersama. Baseline rules mengikuti AA-05; Dummy memakai kelas mayoritas train. Catat TP, FP, TN, FN, UP (positif eligible tanpa prediksi sah), UN (negatif eligible tanpa prediksi sah), unknown, dan ineligible. Unknown/ineligible tidak disisipkan ke denominator eligible.

`precision=TP/(TP+FP)`; `effective_recall=TP/(TP+FN+UP)`; `coverage=(TP+FP+TN+FN)/(TP+FP+TN+FN+UP+UN)`. Laporkan pula conditional recall, F1 suspicious, macro-F1, accuracy, FPR, dan Average Precision (AP) pada prediksi sah bila kedua kelas tersedia. Field keluaran AP bernama `average_precision`. Denominator nol menghasilkan undefined beserta alasannya. Simpan per-run counts dan interval 95% group-bootstrap dari 1.000 resample run (seed 42); laporkan jumlah resample tanpa metrik terdefinisi.

Keberhasilan ML adalah prosedur serta hasil yang sah dan dapat diulang. Usulan baseline tidak mensyaratkan keunggulan F1 tertentu atau skor 0,90. Model eksperimen boleh ditampilkan di lab dengan hasil evaluasi dan keterbatasannya terlihat. Kesimpulan “lebih baik” hanya ditulis jika hasil mendukung; hasil setara/lebih buruk tetap dilaporkan. Perubahan kandidat setelah test membutuhkan test baru yang belum dibuka.

#### Paket dan runtime

Paket immutable terdiri dari payload numerik `model.json`, `model-manifest.json`, dan checksum terpisah. Payload mencatat model/schema version, fitur dan urutannya, scaler, parameter numerik, threshold, serta hash dataset/split. Manifest mengikat hash payload, data, split, evaluasi, versi Python/dependency, commit dan dirty state bila Git tersedia, hash source aktual, serta waktu training. Source hash tetap wajib ketika deployment copy tidak mempunyai metadata Git. Metadata waktu/platform boleh berbeda antar-run; pembandingan reproducibility memakai data/split dan parameter/prediksi sesuai toleransi ML-03. Berkas JSON/CSV ditulis dengan akhir baris LF eksplisit agar perubahan OS tidak mengubah bytes karena konversi akhir baris. Loader wajib mencocokkan sidecar `model.json.sha256` dan mengunci identitas model ketika proses mulai; paket yang berubah ditolak sampai restart. Loader menerima format data numerik yang divalidasi tanpa menjalankan kode dari artefak. Pemilihan/rollback paket dilakukan manual melalui konfigurasi dan restart; tidak ada registry UI atau hot-swap.

Satu loop analisis lokal menghitung di luar transaksi ingest. Identitas hasil adalah `(snapshot_id, revision, model_hash)`; commit memeriksa hash input dan uniqueness. State hasil: `pending`, `succeeded`, `failed`, `ineligible`; label hanya ada pada succeeded. Startup melanjutkan revisi yang belum punya hasil. Kegagalan tercatat dapat dicoba ulang secara eksplisit setelah penyebab diperbaiki. Tidak ada dispatcher, lease AI-job, atau concurrency worker yang dikonfigurasi pengguna. Skor ditampilkan sebagai skor classifier, tanpa klaim risiko dunia nyata yang terkalibrasi.

#### Verifikasi

Tes mencakup overlap, fitur terlarang, split support, fit train-only, threshold validation, metrik abstain/denominator nol, train/runtime parity, hash, serta crash di sekitar commit hasil. Artefak eksperimen aktual mengikuti OP-05. Standar implementasi kode tercatat pada [standar implementasi](../../architecture/standards.md).
