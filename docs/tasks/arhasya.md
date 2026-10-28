# Panduan Arhasya untuk kode dan VM B Monitor

Arhasya menulis kode Monitor, mengujinya, lalu memasangnya pada VM Debian miliknya. Monitor menerima event, menyimpannya sebelum memberi receipt, membentuk analisis, menjalankan inferensi model lokal, dan menampilkan dashboard. Training offline dan penyediaan paket model menjadi tugas integrator agar beban peran ini tetap terkendali. Arhasya tetap menulis jalur inferensi runtime dan penanganan kegagalannya.

Baca [workspace](workspace.md), [istilah](../requirements/srs/terms.md), lalu SRS per task: [event](../requirements/srs/event-pipeline.md), [analisis](../requirements/srs/activity-analysis.md), [model](../requirements/srs/ml-classifier.md), dan [console](../requirements/srs/operator-console.md). Command bootstrap final menunggu F-04; tidak ada klaim kode/tes peran sudah tersedia.

## Workspace dan file milik Arhasya

VM: `LogLab-Monitor-Arhasya`. Clone guest: `~/LogLab`. Gunakan branch per PR, misalnya `feat/arhasya-ingest`, `feat/arhasya-analysis`, dan `feat/arhasya-console`.

| File yang direncanakan | Yang ditulis Arhasya |
| --- | --- |
| `src/loglab/monitor_app.py`, `monitor_main.py` | Endpoint ingest/status, bootstrap aplikasi, sesi dan route dashboard memakai helper security |
| `src/loglab/analysis.py` | Window, snapshot/revision, kualitas, rules, penyimpanan hasil dan analisis loop |
| `src/loglab/features.py` | Ekstraktor tujuh fitur; **review bersama integrator wajib** karena dipakai training dan runtime |
| `src/loglab/model.py` | Loader paket numerik, hash/schema, inferensi dan penanganan model tidak tersedia |
| `tests/test_monitor_app.py`, `test_analysis.py`, `test_features.py`, `test_model.py` | Tes input, persistensi, analisis, fitur, model, serta akses console |
| `deployment/monitor/`, `config/monitor.example.*` | Service, firewall, dan template peran B |
| `docs/tasks/results/arhasya.md` | Hasil aktual, isu, dan batas tes Monitor |

Schema event, helper `db.py`/`security.py`/`config.py`, dependency, root Makefile dan training dikelola integrator. Pemilik dapat mengusulkan perubahan lewat PR bersama; jangan membuat kontrak/helper berbeda untuk Monitor.

## R-01 Pahami alur dan periksa laptop

**Tujuan:** Arhasya dapat menjelaskan mengapa HTTP sukses tidak cukup membuktikan data/analisis sehat. **Requirement:** EP-03/EP-04, AA-02, OP-01. Catat OS/VMware/resource host dan profil B: 2 vCPU, RAM 2 GiB, disk dinamis 20 GiB. Baca field receipt dan beda READY, incomplete/stale, serta hasil model. Selesai bila prasyarat dan alur ditulis di catatan Arhasya.

## R-02 Siapkan guest dan environment coding

**Dependensi:** F-04. Pasang ISO Debian/hash yang sama dengan Erna, akun `loglab`, jaringan host-only dan SSH opsional. Clone ke `~/LogLab`, buat branch dari SHA baseline dan ikuti bootstrap environment yang diterbitkan integrator. Periksa OS/Python, remote Git, branch dan tes fondasi. Tidak ada migrasi lewat folder shared host yang menjadi dependensi runtime.

## R-03 Tulis ingest dan status sumber

**Requirement:** EP-03/EP-04/EP-05/EP-07. **File:** endpoint Monitor, bootstrap, tes ingest. **Input:** schema, digest helper, DB helper dan fixture integrator.

1. Validasi TLS/auth, ukuran request, schema, digest dan identitas sumber sesuai kontrak.
2. Simpan event/receipt pada transaksi sebelum mengirim jawaban. Event identik yang dikirim ulang menjadi duplicate; konflik identitas tidak menimpa record awal.
3. Simpan status sumber dan watermark dengan waktu penerimaan sendiri. Status sumber bukan event login.
4. Tes valid, duplicate, konflik ID/sequence, token salah, digest invalid, body berlebih dan kapasitas. Cocokkan field/status dengan fixture yang sama dengan Erna.
5. Kirim PR `feat/arhasya-ingest`. **Lulus:** record/count benar, receipt sesuai, dan input tidak sah ditolak tanpa body secret di log. Ini belum memerlukan koneksi laptop Erna.

## R-04 Tulis fitur, snapshot dan rules

**Requirement:** AA-01–AA-05. **File:** `analysis.py`, `features.py`, tes fitur/analisis. Buat PR terpisah atau beberapa PR kecil untuk fitur dahulu, kemudian snapshot/kualitas/rules.

Implementasikan window 60 detik, membership/urutan deterministik, tujuh fitur sesuai urutan kontrak, kualitas input dan revisi immutable. Tes batas window, event terlambat, heartbeat usang, watermark/gap, clock offset dan input kosong. Hanya READY dapat dianalisis. Terapkan rules serta alasan dan event pendukung sesuai threshold SRS, tanpa mengganti label ground truth dataset.

**Lulus:** fixture manual menghasilkan fitur yang benar, hasil/versi/revisi dapat ditelusuri, state tidak layak terlihat, dan tes batas lulus. Integrator mereview `features.py` sebelum menyiapkan paket model karena training harus memakai fitur yang sama. Temuan ambigu dilaporkan sebagai pertanyaan kontrak, tidak diputuskan berbeda sendiri.

## R-05 Tulis inferensi dan dashboard

**Requirement:** ML-05/ML-06 dan UI-01–UI-05. **Input:** paket model numerik, checksum dan expected prediction dari integrator; helper sesi/security. Training/dataset/evaluasi ML-01–ML-04 diselesaikan integrator pada F-05 menggunakan fitur R-04 yang sudah diterima.

Tulis loader dan inferensi pada `model.py`. Validasi hash/schema/urutan fitur/angka, kunci identitas paket saat proses hidup, dan simpan hasil per revisi/model. Tes prediksi terhadap fixture integrator, paket hilang/korup/schema salah dan restart. Kegagalan tidak menghasilkan label normal.

Pada PR console terpisah, tulis login/logout operator, route data yang dilindungi sesi, filter/pagination, detail event, hasil rules/ML/version dan kualitas/health. Gunakan helper security; jangan menyimpan secret dalam HTML/log. Tes akses tanpa sesi, query invalid, batas pagination, escaping dan tampilan state. **Lulus:** operator dapat menelusuri input hingga hasil; data belum layak/model gagal dibedakan dari normal.

## R-06 Buat deployment Monitor dan uji operasi

**Requirement:** OP-01–OP-03/OP-06. Tulis service, firewall dan template peran. Koordinasikan root Makefile dengan integrator untuk `make setup-monitor`. Jalankan setup, ulangi setup, periksa HTTPS dari host, reboot guest, backup konsisten dan restore terisolasi. Jangan menyalin DB aktif atau mengubah threshold untuk memperbaiki skor fixture.

**Lulus:** service/IP/data/model kembali, konfigurasi tidak bergantung path host, secret tidak tertimpa, dan prosedur recovery dapat diulang. Kirim PR `feat/arhasya-monitor-deployment` dengan hasil aktual.

## R-07 Serahkan hasil dan ikut integrasi

Kirim PR kecil, file yang menjadi scope, requirement, command/expected/actual, commit, output aman dan isu tersisa. Screenshot VMware harus asli; hasil SSH dicatat sebagai bukti terminal. Arhasya ikut [integrasi pasangan](integration.md) untuk memeriksa data sebenarnya dari Source Erna, receipt, outage, analisis dan dashboard pada satu host. Fixture ingest yang lulus belum menggantikan pengujian kedua VM.
