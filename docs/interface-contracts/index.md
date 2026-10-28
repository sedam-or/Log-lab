# Kontrak antarlayanan

Erna membuat dan mengirim event; Arhasya menerima serta memberi receipt. Keduanya membaca [kontrak event yang sama](../requirements/srs/event-pipeline.md). Jangan menyalin definisi field secara terpisah ke panduan peran.

Dokumen SRS adalah definisi teknis. Folder ini akan berisi schema JSON, contoh request/response, dan fixture yang dapat dijalankan untuk membuktikannya. File executable tersebut belum tersedia. Sebelum pekerjaan aplikasi paralel, integrator harus menyediakan event valid, digest kanonis, duplikat identik, konflik identitas, error autentikasi/schema, contoh status sumber, dan receipt yang cocok/tidak cocok.

Satu set fixture dipakai tes producer dan consumer. Perubahan schema/error/retry diajukan melalui PR bersama, ditinjau Erna dan Arhasya, lalu diikuti perubahan konsumen yang terdampak. Arhasya dapat menguji ingest dengan fixture tanpa menunggu laptop Erna; Erna dapat menguji sender menggunakan receiver uji yang disediakan integrator. Uji mock belum berarti A–B sudah terintegrasi.
