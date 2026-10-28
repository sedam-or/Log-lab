> Draf adaptasi dari SRS v0.1.0 lama. ID requirement dan nomor bagian dipertahankan untuk traceability. Bukti implementasi lama bukan hasil uji repo ini. [Indeks SRS](index.md).

### 5.2 `activity-analysis`

**Baseline sumber:** PRD v1.0.0. **Rincian teknis:** bagian ini. **Dependensi:** `event-pipeline`.

#### Tujuan dan penerimaan

| ID | Requirement | Acceptance dan bukti |
| --- | --- | --- |
| AA-01 | Event unik dikelompokkan deterministik dalam window event-time. | Fixture lintas batas menit, source/stream/client, urutan tiba, dan timestamp seri menghasilkan membership yang sama. Window kosong tidak menghasilkan label normal. |
| AA-02 | Snapshot mempunyai kualitas eksplisit sebelum memperoleh hasil analisis. | Uji window terbuka, backlog/gap, heartbeat stale, skew berlebih, dan input sah lengkap. Hanya `READY` dapat diberi label; alasan ketidaklayakan terlihat. |
| AA-03 | Input analisis tersimpan sebagai revisi immutable yang dapat direproduksi. | Analisis ulang input identik tidak menambah revisi; event terlambat/perubahan kelas kualitas membentuk revisi baru. Revisi lama, hash, membership, serta hasil lama tetap tersedia dan ditandai superseded. |
| AA-04 | Training dan runtime memakai satu schema tujuh fitur. | Nilai fixture dihitung manual lalu dibandingkan ekstraktor kedua jalur. Field hilang/NaN/tipe salah ditolak; tidak diganti nol. |
| AA-05 | Rules menghasilkan alasan dan event pendukung pada snapshot yang layak. | Uji 9/10 kegagalan dan 4/5 akun; rule, threshold, versi, revision, hitungan, serta event IDs tersimpan dan konsisten. |

#### Window dan kualitas

Tumbling window 60 detik, interval `[start, end)`, berdasarkan `occurred_at` UTC dan key `(source_id, stream_id, client_token)`. Urutan event menggunakan waktu yang telah diparse, lalu `event_id`; urutan string waktu tidak menjadi algoritme pengurutan. Source dan monitor menyimpan waktu terjadinya event serta waktu penerimaan secara terpisah, mengikuti semantik yang juga dibedakan dalam [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/).

Evaluasi penutupan paling awal `end + 10 detik`. Status:

- `OPEN`: batas penutupan belum tercapai.
- `STALE`: heartbeat terakhir diterima lebih dari 20 detik lalu atau belum pernah ada.
- `INCOMPLETE`: watermark belum membuktikan pengiriman selesai, ada gap/held event, atau offset jam belum terukur/melebihi 2 detik.
- `READY`: nonkosong, batas penutupan tercapai, status masih segar, waktu source dalam status sudah melewati `end + 10`, ACK sequence sama dengan committed sequence, seluruh sequence hingga watermark itu tersedia di monitor, dan offset jam terukur maksimal 2 detik.

Kualitas berlaku pada bukti yang disimpan untuk revisi tersebut. Heartbeat yang menjadi stale di masa berikutnya mengubah health live; itu tidak mengubah revisi immutable lama. Event terlambat atau perubahan kelas kualitas seperti INCOMPLETE→READY menciptakan revisi baru. Heartbeat rutin yang hanya memperbarui timestamp/watermark tidak menciptakan revisi baru. Hash input mencakup membership event-ID/digest terurut, feature version, dan kelas kualitas; bukti heartbeat penyegelan disimpan sebagai metadata. Snapshot juga menyimpan alasan kualitas serta timestamp penyegelan. READY menyatakan kelengkapan event accepted-local sampai watermark yang dicatat; event sebelum commit lokal berada di luar jaminan. Event invalid ditolak pipeline dan dicatat sebagai kegagalan/counter; tidak diberi snapshot berlabel normal.

#### Schema fitur `login-window-v1`

| Fitur | Tipe, unit, dan rumus |
| --- | --- |
| `event_count` | Integer ≥1; jumlah event unik. |
| `failure_count` | Integer; jumlah `login.failure`. |
| `success_count` | Integer; jumlah `login.success`; jumlah kedua hasil sama dengan event_count. |
| `failure_ratio` | Float [0,1]; failure_count/event_count. |
| `distinct_accounts` | Integer ≥1; akun pseudonim unik. |
| `max_consecutive_failures` | Integer; rentetan gagal terpanjang menurut urutan event. |
| `active_span_seconds` | Float ≥0 dan <60; waktu event terakhir dikurangi pertama; satu event bernilai 0 secara sah. |

Urutan tabel adalah urutan kolom model. Statistik gap, jam siklik, normal-profile terpisah, dan success-after-failure dikeluarkan dari schema awal untuk mengurangi nilai yang tidak terdefinisi serta train/runtime drift. Semua fitur terdefinisi pada snapshot nonkosong yang valid. Identitas, label, run/scenario ID, dan seed hanya menjadi metadata, bukan fitur.

Rules versi `rules-v1`: `REPEATED_FAILURES` bila failure_count ≥10; `ACCOUNT_SWEEP` bila failure_count ≥10 dan distinct_accounts ≥5. Hasil rules tidak menjadi sumber label ground truth ML. Label ML mengikuti rubrik skenario yang direview pada [kontrak ML](ml-classifier.md).

#### Verifikasi

Tes unit memeriksa membership, rumus, batas waktu, quality-state, dan aturan. Tes integrasi memeriksa revisi, hash, hasil lama, serta pemulihan setelah crash. Standar implementasi kode tercatat pada [standar implementasi](../../architecture/standards.md). Persistensi snapshot tidak mensyaratkan queue atau tabel AI-job.
