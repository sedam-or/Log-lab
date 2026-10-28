# LogLab

LogLab adalah praktikum Rekayasa Sistem untuk mencatat login akun fiktif di VM Source, mengirim event ke VM Monitor, lalu menampilkan rules dan satu classifier Logistic Regression lokal pada dashboard.

**Erna menangani VM A Source. Arhasya menangani VM B Monitor.** Keduanya menulis kode, tests dan deployment peran. Integrator menyiapkan fondasi/kontrak bersama, training offline dan penyatuan hasil. Nama anggota adalah samaran kerja. Setiap anggota memakai clone repo di `~/LogLab` dalam guest Debian masing-masing; SSH direkomendasikan agar copy-paste dari terminal host lebih mudah.

## Mulai belajar proyek

Jika baru belajar software engineering, buka [dasar proyek](docs/tasks/basics.md) untuk memahami satu percobaan login dari Source sampai dashboard. Sesudah itu buka [folder kerja dan SSH](docs/tasks/workspace.md) agar jelas di mana kamu menulis kode dan menjalankan command.

## Mulai sesuai peran

- **Erna:** [panduan Source](docs/tasks/erna.md).
- **Arhasya:** [panduan Monitor](docs/tasks/arhasya.md).
- **Integrator:** [fondasi dan integrasi](docs/tasks/integration.md).
- **Semua dokumen:** [docs/index.md](docs/index.md), termasuk PRD, SRS per bagian, diagram, standar, dan inventaris lama.

## Status repo

Dokumen kebutuhan, standar, dan assets lama telah diadaptasi; task anggota telah dirinci untuk review. Source aplikasi, dependency, installer, fixture executable, dan PDF baru belum diterbitkan. `make setup-source`/`make setup-monitor` masih target rencana. Jangan mengklaim hasil uji lama berlaku untuk repo atau build anggota ini.

## Struktur menurut materi

```text
src/                        source aplikasi
tests/                     pengujian
docs/
   index.md                 navigasi peran
   requirements/            PRD dan SRS yang dipecah per kemampuan
   architecture/            baseline, standar, assets dan diagram
   interface-contracts/     rujukan kontrak dan fixture bersama
   tasks/                   Erna, Arhasya, workspace, dan integrasi
   history/                 inventaris dan konteks implementasi lama
config/                    template aman tanpa secret
scripts/                   alat bantu pengembangan
deployment/                provisioning guest, service, firewall
```

Nama direktori utama mengikuti contoh Pertemuan 5 slide 6. `docs/` mempunyai index pada setiap kelompok yang memerlukan navigasi. Tidak ada repo atau paket source terpisah per anggota. Source/Monitor dibedakan oleh konfigurasi dan target setup yang diuji pada Debian target, dengan host integrasi akhir Windows 11.

Alur branch dan PR ada di [CONTRIBUTING.md](CONTRIBUTING.md). [Daftar task](docs/tasks/index.md) menjadi satu tempat status tim. Secret, database, log privat, file VM, OVA dan backup tidak disimpan di Git.
