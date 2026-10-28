# Daftar pekerjaan tim

Satu daftar ini mencatat dokumentasi dan fondasi yang diperlukan sebelum anggota membangun VM. Checkbox hanya diubah setelah kriteria selesai terpenuhi. Nama anggota, tenggat, dan hash baseline diisi saat pembagian tugas ditetapkan; jangan mengarang nilainya.

## Fase 0 Dokumentasi dan fondasi bersama

| ID | Status | Penanggung jawab | Pekerjaan dan kriteria selesai |
| --- | --- | --- | --- |
| D-01 | Selesai | Integrator | Catat struktur sesuai materi, tujuan SSH, pembagian file, dan alur branch/merge. Bukti: commit dokumentasi awal repo. |
| D-02 | Belum | Integrator + review tim | Terbitkan `docs/requirements/PRD.md` dan `SRS.md` yang diselaraskan. PRD menetapkan scope; SRS menetapkan kontrak teknis. ID requirement lama dipertahankan, istilah dijelaskan, status persetujuan jelas, dan path/host lama diperiksa. |
| D-03 | Belum | Integrator + A/B | Bekukan kontrak A–B di `docs/interface-contracts/`, schema dan fixture bersama. Semua field, status HTTP, receipt, TLS/auth, retry, dan batas payload punya contoh valid/invalid serta hasil yang diharapkan. Dependensi: D-02. |
| D-04 | Belum | Integrator | Tetapkan ISO Debian+SHA-256, Python/dependency lock, template konfigurasi, target setup/verifikasi, dan kepemilikan modul aktual. Verifikasi prasyarat pada Debian target; jangan hanya menulis command yang belum pernah diperiksa. Dependensi: D-02/D-03. |
| D-05 | Belum | Integrator | Konfigurasikan review `main` dan pemeriksaan PR; catat pengaturan yang benar-benar aktif. Uji kontrak disiapkan sebelum pekerjaan A/B paralel. Dependensi: D-03/D-04. |

Checkpoint: D-02 sampai D-05 diterima dalam repo; catat hash commit baseline yang dipakai kedua anggota. Dokumen desain bukan bukti bahwa implementasi sudah tersedia atau sudah diuji.

## Fase 1 Panduan tugas anggota

- [ ] **D-06 — Task VM A.** Tulis `docs/tasks/VM-A.md`, lalu render `VM-A.pdf` dari sumber yang sama. Cantumkan identitas anggota, baseline commit, prasyarat host/guest, urutan instalasi Debian, clone, konfigurasi, setup Source, pemeriksaan, reboot, troubleshooting, rollback, serta cara menyerahkan PR. SSH direkomendasikan untuk copy-paste dari host; console menjadi alternatif. Dependensi: checkpoint Fase 0.
- [ ] **D-07 — Task VM B.** Tulis `docs/tasks/VM-B.md`, lalu render `VM-B.pdf`. Struktur panduan sama, dengan ingest, database, analisis, paket model, dashboard, dan fixture Source untuk uji terisolasi. Dependensi: checkpoint Fase 0.

Setiap langkah panduan menyebut lokasi menjalankan perintah (host/guest), perubahan yang dibuat, hasil yang diharapkan, dan tindakan saat gagal. Bedakan command yang tersedia dengan target yang masih harus dibuat. Masukkan diagram sebagai gambar ter-render yang terbaca. Sumber Markdown tetap kanonis; PDF adalah salinan baca. Simpan bukti terminal terpisah dari capture layar VMware asli. Kedua PDF tidak berisi kredensial atau private key.

## Fase 2 Pekerjaan paralel A dan B

- [ ] **A-01 — Source.** Anggota A bekerja di branch Source dari baseline yang sama: provisioning peran, startup, uji login/outbox/sender, retry memakai receiver uji, dan reboot. Kirim PR dengan hasil aktual dan masalah yang belum selesai.
- [ ] **B-01 — Monitor.** Anggota B bekerja di branch Monitor: provisioning peran, startup, uji ingest dengan fixture, hasil rules/ML, dashboard, dan reboot. Kirim PR dengan hasil aktual dan masalah yang belum selesai.

Masing-masing PR membatasi perubahan pada file perannya. Perubahan file bersama dibahas dan masuk melalui PR terpisah. Pemeriksaan lokal memakai tes yang sudah dibekukan; uji memakai mock harus diberi label mock.

## Fase 3 Integrasi dan rilis

- [ ] **I-01 — Merge dan acceptance pasangan.** Review lalu merge PR berurutan. Sinkronkan branch yang tersisa dengan `main`, ulangi pemeriksaan terdampak, lalu pasang kedua VM pada satu host integrasi. Rekonsiliasi event dan receipt, TLS, retry/duplikat, analisis, dashboard, serta reboot. Catat commit, environment, perintah, output, dan pass/fail. Hanya setelah lulus, beri tag rilis.
- [ ] **I-02 — Bukti Modul 5.** Catat lokasi repo, ringkasan branch/merge, `git log --graph`, konflik dan resolusi nyata atau latihan berlabel, serta kontribusi masing-masing anggota. Buat `docs/evidence/M05_Repository-Evidence.md` dan `<Tim>_M05_Repository-Evidence.pdf` setelah nama tim dan bukti tersedia. Jangan mengisi hasil yang belum terjadi.

## Catatan keputusan dan masalah

| Tanggal | Temuan/keputusan | Tindak lanjut |
| --- | --- | --- |
| 2026-10-28 | Repo awal hanya berisi README dan initial commit; implementasi lokal belum dipindahkan. | D-02/D-04 menentukan migrasi terpilih, bukan menyalin seluruh folder praktikum. |
| 2026-10-28 | SSH direkomendasikan pemilik untuk mempermudah copy-paste dari terminal host. | Tulis langkah SSH opsional pada D-06/D-07. |
| 2026-10-28 | Materi memakai `deployment/`; workspace lama memakai `deploy/`. | Pakai `deployment/` di repo ini; periksa path saat migrasi. |
| 2026-10-28 | Windows 11 menjadi host integrasi; masing-masing anggota boleh membangun guest pada laptopnya. | Selaraskan SRS dan bedakan evidence peran dengan evidence pasangan. |
| 2026-10-28 | ISO/hash, nama anggota, baseline commit untuk instalasi, dan setup yang tervalidasi belum ditetapkan. | Selesaikan Fase 0 sebelum membagikan task instalasi final. |
