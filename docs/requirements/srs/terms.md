> Draf adaptasi dari SRS v0.1.0 lama. ID requirement dan nomor bagian dipertahankan untuk traceability. Bukti implementasi lama bukan hasil uji repo ini. [Indeks SRS](index.md).

## 2. Istilah dan ID requirement

Baca [arsitektur sistem](system.md) untuk batas sistem dan diagram komponen, [komunikasi sistem](system.md) untuk pertukaran event, lalu Bagian 5 untuk kontrak per kemampuan. [verifikasi](verification.md) menghubungkan kontrak dengan bukti; Lampiran A memuat usulan yang belum disetujui.

Requirement memakai ID stabil dengan format prefix-modul dan nomor. Workbook Modul 02, task, acceptance, dan evidence menggunakan ID yang sama. Requirement induk menjelaskan hasil yang diminta; kriteria dan kontrak rinci di bawahnya menjelaskan cara membuktikan hasil tersebut.

### Definisi istilah dan ID

ID requirement memakai format `<prefix>-<nomor>`. Prefix menunjukkan modul yang memiliki requirement; nomor adalah rujukan stabil yang dapat dipakai ulang pada workbook, task, acceptance, dan evidence. Sebagai contoh, `EP-03` adalah requirement ketiga pada modul Event Pipeline.

| Istilah | Arti pada LogLab |
| --- | --- |
| `EP` | **Event Pipeline:** pembuatan event login, penyimpanan lokal, pengiriman A→B, validasi receipt, dan penyimpanan event di B. |
| `AA` | **Activity Analysis:** pengelompokan event ke window, pemeriksaan kelengkapan, perhitungan fitur, dan rules. |
| `ML` | **Machine Learning Classifier:** data berlabel, training offline, evaluasi, dan prediksi Logistic Regression lokal. |
| `UI` | **Operator Console:** sesi operator dan tampilan pencarian, status, hasil, serta bukti. |
| `OP` | **Lab Operations:** pemasangan dan pengoperasian dua VM, keamanan jaringan, backup, pemulihan, dan acceptance. |
| Event | Satu catatan hasil percobaan login yang dibuat dari keputusan backend autentikasi. |
| Outbox | Penyimpanan SQLite di VM A yang menahan event setelah commit lokal hingga status pengirimannya selesai atau ditahan untuk pemeriksaan. |
| Receipt | Jawaban VM B setelah transaksi event tersimpan. `stored` berarti event baru; `duplicate` hanya berlaku jika ID dan digest cocok. |
| Digest | Ringkasan kriptografis payload untuk memeriksa integritas dan mengenali pengiriman ulang yang isinya identik. |
| Sequence dan ACK watermark | Sequence adalah nomor berurutan dalam satu source/stream. ACK watermark adalah sequence tertinggi yang sudah dikonfirmasi secara kontigu setelah receipt B diperiksa dan ACK lokal di-commit. |
| Snapshot dan revision | Snapshot mengikat event pada window beserta metadata analisis. Revision adalah versi immutable yang dibuat saat anggota atau kelas kualitas window berubah. |
| `READY` | State kualitas snapshot yang hanya diberikan setelah bukti sumber dan rekonsiliasi sequence memenuhi kontrak activity-analysis; ini bukan label ML. |

### Singkatan teknis

| Singkatan | Arti dan pemakaian |
| --- | --- |
| PRD / SRS | Product Requirements Document menetapkan hasil dan batas produk; Software Requirements Specification merinci kontrak teknis dan verifikasinya. |
| API | Antarmuka pemrograman yang dipakai aplikasi untuk bertukar request dan response. |
| ACK | Acknowledgment, konfirmasi bahwa event telah tersimpan dan receipt cocok. |
| CA / SAN | Certificate Authority menerbitkan sertifikat tepercaya; Subject Alternative Name mencantumkan alamat yang dicakup sertifikat. |
| CSRF | Cross-Site Request Forgery, serangan yang mencoba mengirim perubahan melalui sesi browser korban tanpa izin. |
| CPU / vCPU / RAM | Central Processing Unit dan Random Access Memory; vCPU adalah kapasitas prosesor virtual yang dialokasikan ke VM. |
| CRUD / CRLF | Create, Read, Update, Delete adalah operasi data; Carriage Return dan Line Feed adalah karakter kontrol akhir baris pada log. |
| DB / SQL / SQLite / WAL | Database menyimpan data terstruktur; Structured Query Language mengakses database relasional; SQLite adalah database lokal LogLab dan WAL adalah mode jurnalnya. |
| F1 / FPR / AP | F1 adalah rata-rata harmonik precision dan recall; FPR adalah false positive rate. Average Precision (AP) merangkum precision dengan pembobot kenaikan recall, dihitung dengan `average_precision_score`; ia tidak dihitung sebagai luas trapezoid. Kelas dan denominator disebut pada hasil. |
| HMAC / SHA-256 / UUID | HMAC membuat pseudonim dengan secret; SHA-256 adalah fungsi hash 256-bit; UUID adalah identifier 128-bit untuk event dan stream. |
| HTML / JSON | HyperText Markup Language membentuk halaman dashboard; JavaScript Object Notation adalah format teks request dan event. |
| HTTP / HTTPS / TLS | Hypertext Transfer Protocol; HTTPS melindungi komunikasi HTTP menggunakan Transport Layer Security. |
| IP / MAC / NAT | Internet Protocol address mengidentifikasi host jaringan; Media Access Control address mengidentifikasi antarmuka; Network Address Translation menerjemahkan alamat dan hanya dipakai sementara saat instalasi. |
| ISO / LUKS / OVA | ISO adalah image pemasangan OS; Linux Unified Key Setup mengenkripsi disk; Open Virtualization Appliance adalah paket impor VM yang riwayat snapshot-nya tetap harus diperiksa. |
| OOM / RSS | Out of Memory berarti proses/VM kehabisan memori; Resident Set Size adalah memori proses yang berada di RAM saat diukur. |
| p95 | Persentil ke-95: 95 persen hasil pengukuran berada pada atau di bawah nilai tersebut. |
| RPO | Recovery Point Objective, batas umur data terakhir yang dapat dipulihkan dari backup. |
| RFC 3339 / UTC | RFC 3339 adalah format timestamp; Coordinated Universal Time adalah acuan zona waktunya. |
| SSH | Secure Shell, protokol akses terminal jarak jauh untuk administrator lab. |
| UP / UN | Contoh positif/negatif yang layak tetapi tidak memiliki prediksi sah; keduanya dipakai saat menghitung coverage dan effective recall. |
| VM | Virtual Machine, guest yang berjalan di bawah VMware Workstation. |
