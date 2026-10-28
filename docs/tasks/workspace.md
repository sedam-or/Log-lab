# Folder kerja dan terminal

Tujuan panduan ini adalah memastikan anggota tahu tempat menjalankan perintah dan file apa yang akan dikirim ke GitHub. “Host” berarti laptop fisik yang menjalankan VMware. “Guest” berarti Debian di dalam VM. SSH membuka terminal guest dari host, sehingga copy-paste perintah lebih nyaman ketika clipboard VMware bermasalah.

## Istilah yang dipakai dalam tugas

| Istilah | Arti praktis |
| --- | --- |
| Clone | Salinan repo Git di komputer/guest yang dapat diedit dan memiliki riwayat |
| Branch | Jalur perubahan sementara untuk satu pekerjaan; bukan VM atau folder baru |
| Commit / SHA | Rekaman perubahan; SHA mengidentifikasi versi persis yang direkam |
| Push / pull | Mengirim commit ke GitHub / mengambil dan menggabungkan versi dari GitHub |
| Pull Request (PR) | Permintaan review dan penggabungan perubahan branch ke main |
| Merge | Menggabungkan riwayat/perubahan file; tidak memindahkan VM |
| Service | Program latar belakang guest yang dikelola systemd |
| Fixture / mock | Data uji tetap / komponen pengganti untuk tes terisolasi |
| Outbox / receipt / ACK | Antrean tersimpan di A / jawaban penyimpanan dari B / konfirmasi lokal A sesudah memeriksa jawaban |
| Setup / verifikasi | Memasang dan mengatur komponen / memeriksa hasil dengan kondisi lulus yang jelas |
| Requirement / case | Kebutuhan yang harus dipenuhi / satu skenario pemeriksaan untuk membuktikannya |

## Workspace Erna dan Arhasya

| Lokasi | Erna | Arhasya |
| --- | --- | --- |
| Nama VM di VMware | `LogLab-Source-Erna` | `LogLab-Monitor-Arhasya` |
| Role VM | A / Source | B / Monitor |
| Akun guest standar yang direncanakan | `loglab` | `loglab` |
| Clone Git di dalam guest | `/home/loglab/LogLab` atau `~/LogLab` | `/home/loglab/LogLab` atau `~/LogLab` |
| Contoh branch PR pertama | `feat/erna-login-outbox` | `feat/arhasya-ingest` |
| Alamat pada profil integrasi | `172.16.202.21` | `172.16.202.22` |
| Direktori konfigurasi peran di Git | `deployment/source/`, `config/source.example.*` | `deployment/monitor/`, `config/monitor.example.*` |
| Catatan hasil peran yang aman | `docs/tasks/results/erna.md` | `docs/tasks/results/arhasya.md` |

Path `results/` dibuat saat ada hasil nyata. Kedua anggota menggunakan nama folder clone yang sama karena clone berada pada dua guest berbeda. Tidak perlu mengganti `src/` menjadi folder bernama anggota. Nama samaran dipakai pada branch dan bukti kontribusi; role tetap Source dan Monitor.

Folder VMware di host menyimpan `.vmx`/`.vmdk` dan dikelola VMware. Folder itu berbeda dari clone Git di dalam Debian. Jangan memasukkan file disk VM ke Git. Tidak perlu membuat salinan Git di host untuk pekerjaan ini; bila memilih meng-clone juga di host, pahami bahwa perubahan host tidak otomatis tersalin ke guest. Workflow utama adalah mengedit dan melakukan Git di satu clone guest melalui SSH atau console.

## Sebelum menjalankan perintah instalasi

Integrator harus mengisi baseline commit/tag, ISO dan SHA-256, versi Workstation yang diuji, dependency lock, command setup/verifikasi aktual, serta cara memperoleh konfigurasi privat. Data tersebut belum lengkap. Panduan ini menyediakan lokasi dan urutan kerja; belum merupakan installer yang siap dijalankan dari awal sampai akhir.

Erna dan Arhasya dapat mencatat versi OS host, versi VMware, memori/disk tersedia, dukungan virtualisasi dan resource yang akan dialokasikan. Gunakan guest Debian amd64 yang sama. Saat instalasi, akun `loglab` sebaiknya memiliki hak `sudo` sesuai panduan final, dan folder home harus dapat ditulis akun tersebut.

## SSH opsional yang direkomendasikan

Setelah Debian terpasang dan jaringan telah disiapkan, langkah berikut dijalankan **di console guest Debian**. Ini adalah command standar persiapan SSH; paket proyek bukan bagian dari langkah ini.

```bash
sudo apt update
sudo apt install openssh-server git make
sudo systemctl enable --now ssh
ip -br address
```

Catat IP host-only guest yang benar. Jangan memilih `127.0.0.1` atau menyalin contoh IP jika belum dikonfigurasi. Periksa fingerprint host key langsung di console guest:

```bash
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Lalu buka **PowerShell/terminal host** dan sambungkan ke alamat guest. Contoh untuk profil Erna setelah IP `.21` benar-benar terpasang:

```powershell
ssh loglab@172.16.202.21
```

Untuk Arhasya, gunakan `.22`. Bandingkan fingerprint pada prompt SSH dengan yang diperiksa di console sebelum menerima. Masukkan password akun guest secara interaktif bila login password sementara diaktifkan. Jika muncul `Permission denied (publickey)`, pasang public key milik host melalui console guest sesuai panduan final; jangan membagikan private key atau menganggap SSH selalu menerima password. Setup key dan aturan SSH/firewall akan diverifikasi integrator sebelum F-04. Pengguna yang tidak memakai SSH tetap dapat memakai terminal Debian di console VMware.

Sesudah login SSH, `hostname` dan `pwd` membantu memeriksa mesin/lokasi kerja. `exit` keluar dari sesi SSH menuju terminal host; itu tidak mematikan VM. Mengubah firewall atau SSH harus menyisakan akses console pemulihan.

## Clone dan branch di guest

Bagian ini berlaku untuk Git. Baseline F-04 menyediakan environment untuk menulis kode. Setup aplikasi penuh baru diuji setelah kode/deployment E-05 dan R-06 tersedia. Login GitHub memakai identitas masing-masing; nama samaran tugas bukan alasan berbagi akun atau token.

```bash
# Di Debian guest, melalui SSH atau console:
cd ~
git clone https://github.com/sedam-or/Log-lab.git LogLab
cd ~/LogLab
git status --short --branch
```

Jika folder `~/LogLab` sudah ada, periksa dulu apakah benar clone repo ini dengan `git remote -v`; jangan clone di atas folder itu atau menghapus isinya. Sebelum baseline dilepas, anggota cukup membaca dokumentasi. Saat F-04 sudah siap, integrator memberikan SHA baseline dan instruksi `git switch -c <branch-peran> <SHA>` yang sudah terisi. Jangan menulis `<SHA>` secara literal ke terminal.

`git add` hanya file task sendiri setelah `git diff` diperiksa. Commit/push dijalankan di `~/LogLab`, lalu buka PR menurut [panduan kontribusi](../../CONTRIBUTING.md). Token GitHub dimasukkan melalui mekanisme autentikasi GitHub yang tersedia, tidak ditulis pada URL repo, screenshot, atau panduan.

## Ketika ada masalah

Catat lokasi terminal (host/guest), task ID, perintah, pesan error tanpa secret, hasil yang diharapkan, serta hasil aktual. Jika bootstrap environment belum ada, laporkan dependensi F-03/F-04. Skrip setup aplikasi ditulis pada E-05/R-06 menurut antarmuka bersama; jangan mengubah Makefile/kontrak tanpa koordinasi. Jika akses SSH gagal, kembali ke console untuk memeriksa IP dan service `ssh`. Jika koneksi A–B gagal pada laptop berbeda, baca batas host-only pada panduan integrasi.
