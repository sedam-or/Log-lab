# Kebutuhan Produk LogLab

**Versi produk sumber:** 1.0.0
**Adaptasi repository:** 28 Oktober 2026; draf migrasi untuk review. Persetujuan produk historis tidak berarti installer repo baru sudah tersedia atau diuji.
**Status:** baseline produk disetujui pemilik proyek pada 11 Oktober 2026. Rubrik dosen rinci belum tersedia.
**Cakupan dokumen:** tujuan, pengguna, hasil, batas produk, dan kriteria keberhasilan tingkat produk. Rincian teknis ada di SRS.

## 1. Masalah dan tujuan

LogLab adalah demonstrator untuk memperlihatkan bagaimana hasil login aplikasi uji dapat menjadi log yang bisa diperiksa dan dianalisis. Tanpa alur yang dapat diulang, tim sulit menunjukkan bahwa hasil analisis berasal dari aktivitas tertentu, data lengkap, dan aturan yang dapat ditinjau. Produk ini menghubungkan login fiktif, pencatatan, analisis pola sederhana, dan pemeriksaan oleh operator dalam satu demonstrasi.

Tujuannya bukan mendeteksi insiden pada pengguna nyata. LogLab dipakai untuk mempelajari rekayasa sistem, memeriksa aliran data antarkomponen, dan membuktikan cara kerja analisis dengan data yang aman.

## 2. Pengguna dan kebutuhan

| Pengguna | Kebutuhan |
| --- | --- |
| Penguji login | Membuat login berhasil dan gagal memakai akun fiktif, lalu melihat hasil autentikasi. |
| Operator lab | Menelusuri event dan memahami hasil rules, klasifikasi, serta kondisi sumber. |
| Tim proyek dan penguji | Mengulang demonstrasi, memulihkan data, dan menghubungkan klaim hasil dengan bukti. |

## 3. Hasil produk

Satu demonstrasi yang berhasil memperlihatkan rangkaian berikut: penguji mencoba login fiktif; sistem mencatat hasilnya; layanan monitoring menerima dan menganalisis log; operator membuka hasil beserta konteks yang menjelaskannya. Jika data belum lengkap atau analisis gagal, operator dapat membedakan keadaan itu dari hasil normal.

Produk menyediakan dua cara analisis yang dapat dibandingkan: rules yang deterministik dan satu classifier machine learning lokal. Hasil classifier harus dapat ditinjau sebagai eksperimen pada dataset yang disiapkan untuk proyek. Produk tidak membuat keputusan pemblokiran otomatis.

![Alur produk dari percobaan login sampai tinjauan operator](../architecture/assets/PRD_ALUR_PRODUK.svg)

Sumber diagram: [`../architecture/assets/PRD_ALUR_PRODUK.mmd`](../architecture/assets/PRD_ALUR_PRODUK.mmd).

## 4. Lingkup dan batas produk

Versi 1 mencakup aplikasi login dengan akun fiktif, pencatatan hasil login, pengiriman log antara dua mesin virtual (VM) lab, analisis aktivitas login, satu classifier lokal, dan dashboard operator. Data akun, alamat, dan skenario bersifat fiktif. Sistem dijalankan sebagai demonstrator terisolasi.

Versi 1 tidak mencakup model bahasa besar atau penyedia kecerdasan buatan, log sistem operasi/secure shell/cloud, data akun kampus nyata, dataset Los Alamos National Laboratory wajib, broker atau worker terpisah, antarmuka web satu halaman, multi-tenant, layanan publik, registry model dengan UI, maupun pemblokiran otomatis. Klaim kinerja atau deteksi di luar hasil uji tidak termasuk.

## 5. Peta kemampuan dan requirement

ID requirement dipertahankan agar workbook Modul 02, task, hasil acceptance, dan bukti yang sudah ada tetap dapat ditelusuri. Setiap ID teknis memiliki kontrak dan kriteria verifikasi di SRS.

| Kemampuan | Hasil yang dijanjikan kepada pengguna | ID requirement |
| --- | --- | --- |
| Event Pipeline (EP) | Hasil login dicatat dan dapat ditelusuri sampai diterima layanan monitoring. | EP-01–EP-07 |
| Activity Analysis (AA) | Log lengkap dikelompokkan menjadi aktivitas dan pola yang dapat dijelaskan. | AA-01–AA-05 |
| Machine Learning Classifier (ML) | Satu model lokal dievaluasi secara terukur dan hasilnya tidak disajikan sebagai kepastian dunia nyata. | ML-01–ML-06 |
| Operator Console (UI) | Operator dapat mencari log, memeriksa hasil, dan mengetahui kondisi sistem. | UI-01–UI-05 |
| Lab Operations (OP) | Demonstrasi dapat dipasang, dijalankan, diuji, dan dipulihkan dengan bukti yang tertata. | OP-01–OP-06 |

## 6. Kriteria keberhasilan

Versi 1 berhasil bila alur dari login sampai tinjauan operator dapat diulang; hasil yang belum layak dianalisis tidak dilabeli normal; penjelasan rules dan model dapat ditelusuri ke data masukan; dan pengujian deployment serta pemulihan mempunyai bukti yang sesuai. Kriteria teknis, angka batas, keadaan sistem, dan metode pengujiannya ditetapkan pada SRS.

Laporan harus membedakan hasil model dari rules, menyebut sumber dan batas dataset, serta tidak mengklaim performa pada traffic nyata. Klaim acceptance hanya berlaku pada konfigurasi dan lingkungan yang tercatat di manifest pengujian.

## 7. Asumsi dan keputusan produk

LogLab menggunakan satu aplikasi sumber login fiktif, dua mesin virtual pada jaringan lab privat, satu layanan monitoring, satu operator, dan satu Logistic Regression yang berjalan lokal. Model dilatih offline; traffic runtime tidak dipakai untuk pembelajaran otomatis. Detail alokasi VM, protokol, format data, aturan analisis, model, keamanan, serta target acceptance diatur oleh SRS.

Baseline produk v1.0.0 disetujui pemilik proyek. Persetujuan tersebut bukan bukti bahwa dosen telah menyetujui semua keputusan rinci. Target host integrasi repository ini adalah Windows 11, sesuai keputusan pemilik pada 28 Oktober 2026. Pengujian aktual pada host tersebut belum dilakukan untuk repo ini. Usulan teknis lain dari dokumen lama tetap terpisah di catatan usulan SRS sampai ditinjau.

## 8. Hirarki dokumen

PRD ini menetapkan alasan, pengguna, hasil, dan batas produk. SRS menerjemahkan batas tersebut menjadi kebutuhan sistem, state, interface, kualitas, serta metode verifikasi. Jika perubahan teknis memengaruhi hasil atau lingkup produk, PRD harus diperbarui lebih dahulu; perubahan teknis yang tidak mengubah lingkup dicatat di SRS. Workbook Modul 02 merangkum kebutuhan dan keterlacakan untuk tugas kuliah. [Panduan tugas](../tugas/index.md) mencatat fase dan task; [riwayat migrasi](../history/index.md) mencatat konteks lama dan keputusan penyesuaian.

Markdown adalah sumber kanonis. PDF adalah salinan baca yang dibangun dari Markdown. Jika berbeda, gunakan Markdown dan bangun ulang PDF.

Navigasi dokumen ada di [index kebutuhan](index.md) dan [inventaris migrasi](../history/inventory.md). Workbook, panduan implementasi, dan catatan kontrol mempunyai peran turunan yang dijelaskan di README; semuanya tetap menjaga ID requirement yang sama.
