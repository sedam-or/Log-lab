# Standar implementasi dan evidence

Diadaptasi dari standar proyek lama untuk digunakan pada repo baru. Command tes di bawah hanya berlaku setelah source, tests, dan dependency sudah dimigrasikan. Perintah setup masih menunggu implementasi. [Indeks](index.md).

### 2. Gaya kode dan kontrak publik

- Empat spasi, UTF-8, `snake_case` untuk fungsi/modul/variabel, `PascalCase` untuk class, konstanta global `UPPER_SNAKE_CASE`.
- Gunakan type hint pada fungsi kontrak publik, return type eksplisit, dataclass/TypedDict hanya jika memperjelas schema. Fungsi domain kecil dan deterministik; hindari global mutable dan side effect saat import.
- Validasi di batas luar, lalu berikan data bertipe ke domain. Timestamp selalu UTC timezone-aware; konversi ke ISO 8601 hanya saat masuk/keluar storage/API.
- Konstanta window, retry, ukuran, dan threshold diberi nama dan satu sumber konfigurasi. Nilai yang memengaruhi output dicatat dalam event/snapshot/model/run manifest.
- Error untuk pengguna berupa kode stabil dan pesan aman. Log internal tidak menyimpan password, authorization header, cookie, token, isi body sensitif, atau event mentah lengkap.
- Jangan menambahkan formatter/linter atau dependency hanya untuk preferensi gaya. Match format sekitar, gunakan standard library lebih dahulu, dan catat dependency baru dengan alasan.

### 3. Database, transaksi, dan event

- Setiap VM memakai satu file SQLite lokal dengan schema version dan migrasi bernomor. DB tidak berada pada shared folder, jaringan, atau repo.
- Tulis event outbox, sequence, dan counter terkait dalam satu transaksi source. Status `accepted_local` hanya setelah commit sukses. Hasil auth tidak diubah karena B mati atau pencatatan gagal; kegagalan lokal tetap punya counter/status.
- Di B, validasi token/schema/digest sebelum insert; unique `(source_id,event_id)` serta `(source_id,stream_id,sequence)`. Commit insert/receipt sebelum merespons. Retry digest sama menjadi duplicate; konflik tidak mengubah data sebelumnya.
- Sequence tidak di-reset saat restart biasa. Restore source lama harus merekonsiliasi watermark; stream baru diperlukan jika sequence berpotensi digunakan ulang.
- Snapshot menyimpan revision, membership event ID/digest, quality state/reason, feature version, input hash, dan seal evidence. Analisis ulang input identik idempoten; event terlambat membuat revision baru.
- Gunakan transaksi pendek. Jangan menahan transaksi ingest saat menghitung fitur, rules, atau prediksi. Hasil ML memiliki unique key `(snapshot_id, revision, model_hash)` dan state terpisah dari label.

### 4. API, jaringan, dan keamanan

- Endpoint v1: `POST /api/v1/events`, `POST /api/v1/source-status`; dashboard dan login berjalan pada VM masing-masing. Payload event maksimal 8 KiB; pagination maksimal 100; ukuran/filter/rate limit mengikuti kontrak API pada SRS nomor bagian 5.1 dan 5.4.
- Semua endpoint aplikasi pada acceptance memakai HTTPS/8443 dan sertifikat CA lab yang hostname/IP SAN-nya diperiksa. Client selalu memverifikasi CA dan identitas server; opsi skip TLS verification dilarang.
- A→B memakai bearer token sumber terpisah dari credential operator. Jawaban receipt hanya dianggap sah jika source/event/digest cocok. Kode error HTTP mengikuti kontrak `event-pipeline` pada SRS nomor bagian 5.1.
- Network VMware host-only dan firewall default-deny. A boleh konek ke B untuk event/status; host gateway boleh akses UI dan SSH yang disetujui. Port database tidak diekspos. Tidak ada public bind atau port forwarding.
- Akun uji memakai password hash; pseudonim akun/client memakai HMAC domain terpisah. Event tidak membawa password, cookie, token, username nyata, atau IP mentah.
- Dashboard memeriksa sesi pada setiap route data. Cookie HTTPS `Secure`, `HttpOnly`, `SameSite=Strict`, expiry, logout, CSRF/origin protection; semua log yang dirender di-escape.
- Secret runtime ditempatkan di `/etc/loglab/*.env` atau secret file setara dengan owner khusus dan permission ketat. Secret tidak masuk Git, terminal transcript, screenshot, backup laporan, atau example config.

### 5. Activity analysis dan rules

- Gunakan window tumbling event-time `[start,end)` 60 detik dan grouping `(source_id,stream_id,client_token)`. Tie-break memakai `event_id`, bukan urutan leksikografis timestamp.
- Window ditutup untuk evaluasi paling cepat `end+10s`; heartbeat stale setelah 20s; offset jam maksimal 2s; seluruh watermark harus kontigu. Snapshot yang tidak layak tidak menerima label normal.
- Runtime dan training berbagi `login-window-v1` tujuh fitur sesuai kontrak `activity-analysis` pada SRS nomor bagian 5.2. Kolom, urutan, unit, range, dan versi schema harus sama; nilai hilang/NaN ditolak, tidak dipaksa menjadi nol.
- Rules v1: `REPEATED_FAILURES` saat failure ≥10; `ACCOUNT_SWEEP` saat failure ≥10 dan distinct account ≥5. Hasil menyimpan versi rule, snapshot revision, reason, counts, dan evidence IDs.

### 6. ML, data, dan klaim hasil

- Model v1 hanya StandardScaler + Logistic Regression dengan konfigurasi SRS; training offline dengan seed/config/data/split hash tercatat. Tidak ada online learning, hyperparameter sweep, atau data test dalam pemilihan fitur/threshold.
- Label dibuat dari rubrik skenario yang direview, bukan hasil rules; kasus ambigu diberi unknown. Identitas, seed, run/scenario IDs, label, dan event IDs dilarang menjadi fitur.
- Split grouped sebelum fit: run/replay dan semua revision yang berbagi event berada di partisi yang sama. Test dibuka sekali sesudah kandidat/rules/threshold dibekukan.
- Bandingkan ML, rules, dan Dummy pada sample test yang identik. Simpan prediksi per sample dan metrik mentah termasuk unknown, ineligible, UP/UN, denominator, support, per-run, serta interval bootstrap sesuai kontrak `ml-classifier` pada SRS nomor bagian 5.3.
- Model package numerik dan data-only; tidak meng-unpickle atau mengeksekusi kode dari artefak. Load menolak hash/schema/order/angka yang invalid. Runtime tidak pernah auto-train.
- Hasil di UI selalu menyebut `experimental` dan versi. Hasil yang gagal, belum ada paket, atau input tidak READY tidak pernah ditampilkan sebagai label normal. Klaim performa hanya boleh mengikuti laporan test final.

### 7. Uji, acceptance, dan evidence

- Framework `unittest`; file `tests/test_*.py`, kelas `*Tests`, metode `test_*`. Jalankan dari root clone guest `~/LogLab` setelah kode dan dependensi diterbitkan:

  ```bash
  PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
  ```

- Setiap bug/perubahan perilaku menambah tes kontrak atau regresi yang paling dekat. Uji minimal mencakup transaksi/restart, retry/idempotensi, konflik, quality state, snapshot revision, label/split leakage, model parity, sesi, escaping, backup/restore, serta fault injection dua VM.
- Sebelum test, catat requirement/case, commit dan dirty state, OS/runtime, resource, dependency lock, config non-secret, dataset/config hash, serta waktu. Uji sistem menyimpan raw output; ringkasan tidak boleh mengubah hasil mentah.
- Simpan artefak hasil di luar tree yang dikomit secara default. Hanya fixture/dokumen non-sensitif boleh dikomit. Screenshot VMware asli boleh disanitasi pada salinan berbagi, dengan catatan perubahan; pastikan tidak menampilkan credential, personal path, secret, atau data yang tidak diperlukan.
- Jangan menafsirkan health HTTP 200 sebagai delivery, classifier, atau restore lulus. Setiap klaim memakai acceptance result yang sesuai.

### 8. Git, review, dan perubahan

- Commit subject singkat dan imperatif, misalnya `Persist source heartbeat watermark`.
- Satu perubahan memuat requirement IDs, alasan, metode verifikasi, hasil aktual, dan link run manifest. Perubahan API/schema/model/threshold/config kritis membutuhkan review anggota kedua.
- Perubahan baseline mencatat keputusan, requirement terdampak, evidence baru, dampak resource/jadwal dan test ulang. Jangan mengedit hasil test setelah kandidat/test final dibuka.
- Jangan commit `.env`, DB runtime, private keys, VM disk, dataset terunduh, paket model eksperimen yang belum disanitasi, token, atau raw evidence sensitif.
