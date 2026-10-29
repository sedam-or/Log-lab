> Draf adaptasi dari SRS v0.1.0 lama. ID requirement dan nomor bagian dipertahankan untuk traceability. Bukti implementasi lama bukan hasil uji repo ini. [Indeks SRS](index.md).

### 5.1 `event-pipeline`

**Baseline sumber:** PRD v1.0.0. **Rincian teknis:** bagian ini. **Dependensi:** tidak ada.

#### Tujuan dan penerimaan

| ID | Requirement | Acceptance dan bukti |
| --- | --- | --- |
| EP-01 | Backend menghasilkan satu event untuk setiap hasil autentikasi yang berhasil dicatat, dengan metadata aman. | Login benar/salah menghasilkan jenis/alasan sesuai hasil auth. Event tidak memuat password, token, IP/nama nyata. Periksa event dan counter offered/accepted/rejected. |
| EP-02 | Penerimaan lokal dikonfirmasi setelah event dan sequence commit ke outbox. | Kill/restart sesudah commit mempertahankan ID/payload/sequence; enqueue gagal tidak mengonsumsi sequence dan tidak mengubah hasil auth. Simpan state DB sebelum/sesudah. |
| EP-03 | Pengiriman at-least-once menghasilkan satu record operasional untuk satu identitas event. | Retry sebelum/sesudah commit receiver dan sebelum commit ACK source tetap menghasilkan satu event. Source hanya selesai sesudah receipt cocok dan commit ACK lokal. |
| EP-04 | Receiver memvalidasi autentikasi, schema, digest, ukuran, dan konflik identitas. | Uji token salah, body berlebih, field salah, digest salah, ID/sequence sama dengan isi berbeda; event awal tetap utuh dan alasan penolakan tercatat tanpa body secret. |
| EP-05 | Kapasitas dibatasi dan kegagalan pencatatan dapat direkonsiliasi. | Isi kapasitas hingga batas; event lama tetap utuh, event baru ditolak dan counter bertambah. `offered = accepted_local + enqueue_rejected`; bandingkan accepted, stored, ACK, pending, held. |
| EP-06 | Satu sender memulihkan pekerjaan durable setelah gangguan. | Putuskan monitor 60 detik, lanjutkan login, pulihkan/restart source dan monitor; semua event accepted-local terkirim dalam profil OP-04. Tidak ada dua sender aktif untuk DB yang sama. |
| EP-07 | Source mengirim status watermark dan kesehatan yang bertimestamp. | Heartbeat setiap 5 detik mencatat stream, committed/ACK sequence, backlog, penolakan, waktu source, dan waktu penerimaan monitor. Uji status hilang/usang serta sequence gap. |

#### Kontrak event v1

| Field | Tipe dan arti |
| --- | --- |
| `schema_version` | Integer `1`. |
| `source_id` | ID sumber lab yang dikonfigurasi; string nonkosong. |
| `event_id`, `stream_id` | UUID; stream tersimpan bersama DB dan sequence tidak reset pada reboot biasa. |
| `sequence` | Integer positif naik dalam `(source_id, stream_id)`; ditetapkan sekali pada commit lokal. |
| `occurred_at` | RFC 3339 UTC dengan akhiran `Z`; waktu backend menghasilkan hasil autentikasi. |
| `event_type` | `login.success` atau `login.failure`. |
| `account_token`, `client_token` | HMAC-SHA-256 hex dengan namespace terpisah; konsisten dalam satu dataset/lab. |
| `reason_code` | `SUCCESS` atau `INVALID_CREDENTIALS`; selaras dengan jenis event. |
| `event_digest` | SHA-256 hex dari JSON kanonis UTF-8, key terurut, separator tanpa spasi, tanpa field digest; field string dibatasi ASCII. |

Receiver menambahkan `received_at` UTC dan tidak mempercayainya dari request. Set field harus persis sesuai kontrak. Batas payload satu event 8 KiB; `source_id` maksimal 64 karakter; UUID kanonis lowercase; token/digest 64 karakter hex lowercase. Identitas dan payload tetap pada seluruh retry. Counter offered menghitung hasil autentikasi yang benar-benar diputuskan backend; request malformed yang belum menjalankan auth dihitung terpisah. Restore DB lama yang akan dipakai menghasilkan event baru harus memverifikasi watermark monitor; bila sequence dapat terulang, gunakan stream baru tanpa mengubah event pending lama.

#### Kontrak API penyedia

`POST /api/v1/events` menerima satu event dan bearer token sumber melalui TLS. Sesudah commit, receipt berisi `status` (`stored`/`duplicate`), `source_id`, `event_id`, dan `event_digest`. Duplicate hanya sah bila digest sama. Identitas sequence yang bertabrakan juga ditolak. HTTP: 401 autentikasi; 400 JSON rusak; 422 schema/digest; 409 konflik; 413 ukuran; 429 rate limit; 503 kapasitas/layanan sementara. Validasi gagal tetap menghasilkan counter dan alasan aman yang terbatas.

`POST /api/v1/source-status` menerima tepat sepuluh field berautentikasi: `source_id`, `stream_id`, `committed_sequence`, `acknowledged_sequence`, `pending_count`, `held_count`, `rejected_count`, `offered_count`, `accepted_local_count`, dan `source_time`. Counter/watermark adalah integer 0 sampai 2^63-1, bukan boolean; ACK tidak boleh melebihi committed. Monitor mencatat `received_at` sendiri. Respons HTTP 200 berisi `status: accepted`, `source_id`, `received_at`, serta `clock_offset_ms` sebagai perkiraan selisih waktu penerimaan Monitor dikurangi source_time, dalam milidetik. Nilai itu mencakup waktu transit jaringan dan tidak membuktikan sinkronisasi jam. Offset tidak dikirim sebagai field request tambahan. ACK watermark adalah sequence tertinggi yang seluruh pendahulunya sudah ACK, bukan sekadar ACK terbesar yang pernah terlihat. Sequence watermark nol sah sebelum event pertama. Status bukan event dan tidak menaikkan sequence event.

Rate limit usulan: login sumber maksimal 20 request/detik per client, ingest maksimal 50 request/detik per sumber sah, status maksimal 1 request/detik per sumber. Kelebihan menghasilkan 429/Retry-After; request login yang ditolak sebelum auth tidak masuk offered-auth dan mempunyai counter request-rejected terpisah. Receiver membatasi panjang/tipe counter status dan ukuran body seperti event.

Satu sender mencoba ulang timeout/429/5xx dengan backoff 1, 2, 4, … maksimal 30 detik, jitter 0-20%, serta timeout request 3 detik. Retry sementara tidak menghapus event. Respons permanen menahan event untuk inspeksi, menampilkan alasan, dan menurunkan kualitas data; operator dapat mencoba ulang setelah penyebab diperbaiki. Receipt yang tidak cocok diperlakukan sebagai kegagalan, bukan ACK.

Kapasitas awal outbox adalah 10.000 event atau 64 MiB payload tersimpan, termasuk record ACK yang belum dibersihkan. Monitor maksimal 100.000 event atau 256 MiB payload. Pembersihan mengikuti OP-06; tidak ada penghapusan event lama diam-diam untuk memberi ruang.

#### Verifikasi

`unittest` menguji kontrak, commit/ACK, konflik, counters, dan restart. Uji fault serta evidence dua VM mengikuti OP-04/OP-05. Layout, commands, dan gaya mengikuti standar pada [standar implementasi](../../architecture/standards.md). Implementasi mekanisme transaksi/penguncian dipilih dalam desain teknis; kontrak di atas tetap mengikat.

[IP, port, source ID dan nama konfigurasi yang wajib dipakai](../../interface-contracts/index.md) ditetapkan terpisah agar kedua peran memakai nilai yang sama.
