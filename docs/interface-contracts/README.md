# Kontrak teknis Source dan Monitor

**Status:** daftar rincian yang harus dibekukan melalui D-03, belum kontrak rilis yang diverifikasi pada repo ini. SRS lama menjadi bahan awal, bukan alasan untuk mengklaim kode dan tes sudah tersedia.

Kontrak menjelaskan request, response, validasi, autentikasi, error, dan perilaku pemulihan antar-service. Kontrak bukan sekadar tampilan layar. Sebelum A dan B mulai bekerja paralel, kedua pemilik harus meninjau contoh dan fixture yang sama.

| Bagian | Rincian yang perlu ditulis dan diverifikasi |
| --- | --- |
| Pengiriman event | `POST /api/v1/events`, HTTPS, bearer token sumber, satu event JSON, batas ukuran, versi schema, dan identitas sumber |
| Field event v1 | `schema_version`, `source_id`, `event_id`, `stream_id`, `sequence`, `occurred_at`, `event_type`, `account_token`, `client_token`, `reason_code`, `event_digest` beserta tipe, format, dan batasnya |
| Receipt | Field `status`, `source_id`, `event_id`, `event_digest`; arti `stored` dan `duplicate`; syarat A boleh menyelesaikan pengiriman |
| Error dan retry | Pemetaan status HTTP permanen/sementara, konflik identitas, backoff, timeout, dan data yang ditahan agar tidak hilang |
| Status sumber | `POST /api/v1/source-status`, counter, sequence/watermark, timestamp, freshness, dan validasinya |
| Keamanan | Trust CA dan SAN alamat, konfigurasi token, pseudonim, serta field rahasia yang tidak boleh masuk event/log |
| Kompatibilitas | Versi kontrak, aturan perubahan yang memutus kompatibilitas, serta pasangan commit/tag yang diuji |
| Fixture | Event valid/invalid, digest kanonis, duplikat identik, konflik ID, contoh receipt, dan skenario receiver tidak tersedia |

Schema dan fixture harus dapat dijalankan oleh pengujian kedua sisi. Jangan menduplikasi definisi dengan nilai berbeda dalam panduan A/B. Perubahan kontrak masuk melalui PR bersama sebelum konsumennya diperbarui.
