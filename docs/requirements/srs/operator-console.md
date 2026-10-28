> Draf adaptasi dari SRS v0.1.0 lama. ID requirement dan nomor bagian dipertahankan untuk traceability. Bukti implementasi lama bukan hasil uji repo ini. [Indeks SRS](index.md).

### 5.4 `operator-console`

**Baseline sumber:** PRD v1.0.0. **Rincian teknis:** bagian ini. **Dependensi:** pipeline, analysis, classifier.

#### Tujuan dan penerimaan

| ID | Requirement | Acceptance dan bukti |
| --- | --- | --- |
| UI-01 | Data monitoring hanya dapat dibaca melalui sesi operator yang sah. | Uji akses tanpa sesi, password salah/benar, masa berlaku, logout, dan sesi setelah restart; data terlindungi pada seluruh halaman/API. |
| UI-02 | Operator dapat mencari log melalui filter dan pagination yang terbatas. | Filter waktu, sumber, akun pseudonim, dan success/failure dapat digabungkan. Fixture 20.000 event menunjukkan hasil/order/page yang benar tanpa duplikasi/hilang antar-page pada dataset tetap. |
| UI-03 | Detail event menyajikan metadata aman dan waktu yang jelas. | Detail memuat ID/source/stream/sequence, occurred_at, received_at, jenis/alasan, dan pseudonim. Payload berisi karakter HTML/CRLF tampil aman sebagai teks; password/token tidak tampil. |
| UI-04 | Hasil rules dan ML dapat dibuka beserta input, versi, dan state. | Klik hasil membuka snapshot-revision dan event pendukung; model/fitur/rules version terlihat. Pending/failed/ineligible/model-unavailable tidak tampil sebagai normal. Revisi superseded tetap dapat ditinjau. |
| UI-05 | Dashboard membedakan keadaan sumber, delivery, dan analisis. | Uji idle sehat, source offline/stale, backlog, konflik/penolakan, serta analisis gagal. Timestamp pembaruan dan batas staleness terlihat; liveness HTTP 200 tidak menyatakan delivery berhasil. |

#### Alur dan batas UI

Halaman: login operator → ringkasan health/hasil terbaru → daftar event terfilter → detail event atau snapshot. Satu akun operator cukup; tidak ada CRUD role dosen/mahasiswa/tendik. Akun uji aplikasi sumber hanya menghasilkan perilaku login fiktif.

Filter default 24 jam dan rentang maksimum 7 hari; page default 50, maksimum 100. Panjang filter ID maksimal 64 karakter. Query maksimum 20 request/detik per sesi operator; kelebihan menghasilkan 429/Retry-After. Urutan event konsisten berdasarkan waktu yang diparse dan event_id. Waktu tampil sebagai UTC dengan label zona. Query invalid memberi pesan yang dapat ditindaklanjuti, bukan rentang tak terbatas.

Sesi server-side mempunyai idle timeout 30 menit, cookie `Secure`, `HttpOnly`, `SameSite=Strict`, rotasi ID saat login, serta logout yang mencabut sesi. Password disimpan dengan hash adaptif yang dikonfigurasi dalam desain teknis. Request yang mengubah state dilindungi terhadap CSRF. Login operator dibatasi 5 kegagalan/menit per client; login kembali diperbolehkan setelah jendela berlalu. Body, panjang filter, dan query diperiksa di server.

Endpoint liveness publik hanya menyampaikan status proses minimal; log, counters, konfigurasi, detail sumber, dan hasil analisis memerlukan sesi. Bearer token ingest tidak dapat dipakai sebagai sesi operator.

#### Validasi kegunaan

Anggota tim yang tidak menyiapkan fixture menjalankan dua tugas pada data 20.000 event: menemukan rangkaian kegagalan akun tertentu dan membuka evidence-nya; kemudian menentukan apakah sumber sehat, idle, atau stale dari dashboard. Target tiap tugas ≤5 menit tanpa SQL/terminal dan tanpa instruksi klik dari pengembang. Catat waktu, kegagalan, dan kebingungan yang terjadi. Hasil ini adalah validasi operator internal; belum mewakili staf IT nyata.

#### Verifikasi

Tes HTTP/integrasi mencakup proteksi seluruh route, cookie/session, batas query, filter, escaping, serta hasil/state. Uji manual browser menghasilkan screenshot yang diperiksa untuk memastikan tidak memuat secret. Pengukuran respons mengikuti OP-04. Perintah, antarmuka, dan gaya implementasi mengikuti [standar implementasi](../../architecture/standards.md); tampilan dapat memakai HTML yang dirender server.
