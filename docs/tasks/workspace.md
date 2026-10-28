# Menentukan folder kerja dan tempat menjalankan perintah

Kamu akan memakai laptop, VMware, Debian, terminal, dan GitHub. Masing-masing mempunyai fungsi berbeda. Memahami perbedaan ini membantu menghindari kesalahan seperti menjalankan perintah Debian di PowerShell atau mencari file Python di folder disk VMware.

## Laptop host dan Debian guest

**Host** adalah laptop fisik yang kamu gunakan. VMware Workstation adalah aplikasi pada laptop itu. **Virtual machine**, disingkat VM, adalah komputer virtual yang dijalankan VMware. Sistem operasi di dalam VM disebut **guest**. Pada proyek ini, guest yang dipakai adalah Debian.

Di host, kamu membuka VMware dan browser. Di guest, kamu memasang Python, menulis kode, menjalankan tes, dan menjalankan aplikasi LogLab. Kedua lingkungan mempunyai filesystem sendiri. File yang dibuat di Debian tidak otomatis muncul sebagai file terpisah di folder Documents Windows.

![Terminal host mengendalikan Debian melalui SSH](../architecture/assets/learning/host-ssh.png)

[Sumber Mermaid](../architecture/assets/learning/host-ssh.mmd).

## Mengapa memakai SSH

SSH membuka sesi terminal ke guest dari terminal host. Sesudah tersambung, perintah yang kamu ketik dijalankan di Debian. Ini memungkinkan kamu menyalin perintah dari panduan lalu menempelkannya di PowerShell/terminal host tanpa bergantung pada clipboard console VMware.

Penggunaan SSH direkomendasikan pemilik proyek untuk kenyamanan copy-paste. Kamu tetap boleh memakai terminal melalui console VMware. Jika SSH bermasalah, console berguna untuk memperbaiki jaringan atau service SSH pada guest.

SSH host-ke-guest berbeda dari autentikasi GitHub. Berhasil masuk Debian lewat SSH belum otomatis memberi izin push ke GitHub. Izin repo diberikan ke akun GitHub masing-masing anggota.

## Folder VMware dan folder proyek

Folder VM di host menyimpan file seperti `.vmx` untuk konfigurasi VM dan `.vmdk` untuk disk virtual. VMware menggunakan file tersebut untuk menjalankan guest. Kamu tidak menulis source Python di folder itu.

Folder proyek adalah hasil **clone** Git di dalam guest. Kita memakai `~/LogLab`. Simbol `~` berarti home akun yang sedang login. Jika akun guest bernama `loglab`, `~/LogLab` sama dengan `/home/loglab/LogLab`. Di folder inilah ada `src/`, `tests/`, `docs/`, dan riwayat `.git/`.

| Yang perlu dibedakan | Erna | Arhasya |
| --- | --- | --- |
| Nama VM pada VMware | `LogLab-Source-Erna` | `LogLab-Monitor-Arhasya` |
| Peran aplikasi | Source atau VM A | Monitor atau VM B |
| Akun Debian yang direncanakan | `loglab` | `loglab` |
| Clone di dalam guest | `~/LogLab` | `~/LogLab` |
| Branch task pertama | `feat/erna-login-outbox` | `feat/arhasya-ingest` |
| IP pada profil integrasi | `172.16.202.21` | `172.16.202.22` |

Nama clone boleh sama karena kedua folder berada pada guest berbeda. Nama branch berbeda untuk menunjukkan pekerjaan yang akan diperiksa. Membuat branch tidak membuat VM atau folder baru.

## Persiapan yang diberikan integrator

Sebelum task coding dimulai, integrator harus memberikan ISO Debian beserta checksum, versi Python/dependency, cara bootstrap environment, commit awal, dan fixture uji. **Checksum SHA-256** adalah sidik jari file untuk memeriksa bahwa ISO yang digunakan sama dengan ISO acuan.

Commit awal yang disepakati disebut **baseline**. Commit itu harus dicatat sebagai SHA lengkap atau tag yang dapat diperiksa. Kedua anggota mulai dari baseline yang sama agar struktur dan helper sesuai. Saat ini baseline pengembangan tersebut belum dilepas; membaca dokumentasi dan mencatat resource laptop dapat dilakukan lebih dahulu.

## Memasang SSH setelah guest dan jaringan siap

Bagian ini dijalankan setelah Debian terpasang, akun tersedia, dan guest memiliki jaringan. Command berikut adalah persiapan alat umum; command ini tidak memasang aplikasi LogLab.

Di **terminal guest Debian**, jalankan:

```bash
sudo apt update
sudo apt install openssh-server git make
sudo systemctl enable --now ssh
ip -br address
```

`apt update` memperbarui daftar paket. Perintah berikutnya memasang server SSH, Git dan Make. `systemctl` mengaktifkan layanan SSH sekarang serta saat guest boot. `ip -br address` menampilkan alamat antarmuka jaringan.

Hasil yang dicari adalah alamat guest pada adapter host-only. `127.0.0.1` adalah alamat mesin itu sendiri dan tidak dipakai host untuk menyambung ke guest. IP `.21` dan `.22` pada panduan merupakan alamat rencana; gunakan setelah profil tersebut benar-benar dikonfigurasi. Cara memasang alamat statis dan memilih VMnet akan difinalkan bersama baseline, karena nama adapter pada setiap mesin dapat berbeda.

Di console guest, periksa fingerprint server SSH:

```bash
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Sekarang buka **PowerShell atau terminal host**. Untuk contoh Erna yang sudah mempunyai IP `.21`, jalankan:

```powershell
ssh loglab@172.16.202.21
```

Arhasya menggunakan `.22`. Pada koneksi pertama, SSH meminta pemeriksaan fingerprint. Cocokkan dengan fingerprint dari console guest. Jika sama, terima lalu login menggunakan metode autentikasi yang sudah disiapkan. Password dimasukkan secara interaktif bila login password diizinkan; konfigurasi yang hanya menerima public key memerlukan pemasangan key terlebih dahulu.

Sesudah tersambung, jalankan dua command berikut **di sesi SSH**:

```bash
hostname
pwd
```

`hostname` menunjukkan nama guest. `pwd` menunjukkan folder tempat terminal berada. Kedua hasil itu membantu memastikan bahwa command berikutnya dijalankan pada mesin yang benar. `exit` keluar dari sesi SSH menuju host; guest tetap berjalan.

Jika muncul `Permission denied (publickey)`, akses kembali melalui console lalu ikuti pemasangan public key yang ditentukan pada baseline. Jangan menyalin private key ke anggota lain. Jika koneksi timeout atau ditolak, periksa IP, adapter host-only, service SSH dan firewall dari console.

## Clone repo di Debian

Setelah Git tersedia, jalankan di **guest**, baik melalui SSH maupun console:

```bash
cd ~
git clone https://github.com/sedam-or/Log-lab.git LogLab
cd ~/LogLab
git remote -v
git status --short --branch
```

Command clone mengunduh repo dan membuat folder `LogLab`. Nama di GitHub adalah `Log-lab`, tetapi argumen terakhir memilih nama folder lokal `LogLab`. `git remote -v` harus menunjuk repo `sedam-or/Log-lab`. Status Git menunjukkan branch serta perubahan lokal.

Bila `~/LogLab` sudah ada, periksa isinya dan remote lebih dahulu. Gunakan clone yang benar, bukan menimpa atau menghapus folder tanpa pemeriksaan. Pekerjaan utama dilakukan pada satu clone guest ini. Jika kamu juga meng-clone di host, kedua clone merupakan salinan berbeda; perubahan tidak tersinkron otomatis.

## Cara membaca path file

Path seperti `src/loglab/source_app.py` dihitung dari root repo. Setelah `cd ~/LogLab`, path tersebut berarti `/home/loglab/LogLab/src/loglab/source_app.py`. Path `docs/tasks/erna.md` menunjuk panduan Erna pada clone yang sama.

Saat kode sudah tersedia, kamu dapat membuka file menggunakan editor di guest atau editor host yang mengakses guest. Pilih cara yang kamu pahami dan pastikan editor benar-benar menyimpan pada clone guest. Jika ingin memeriksa perubahan tersimpan, gunakan `git diff` dari `~/LogLab`.

## Membuat branch dan memulai task

Integrator akan memberikan SHA baseline pada F-04. Contoh berikut menjelaskan bentuk command, sehingga `SHA_BASELINE` wajib diganti sebelum dijalankan:

```text
git switch -c feat/erna-login-outbox SHA_BASELINE
```

Erna membuat branch sesuai tasknya; Arhasya memakai `feat/arhasya-ingest`. Setelah task pertama selesai dan masuk main, task berikutnya dimulai dari main terbaru melalui branch baru. Langkah commit, push, PR dan sinkronisasi dijelaskan pelan-pelan pada [panduan kontribusi](../../CONTRIBUTING.md).

## Jika task berhenti karena masalah

Tuliskan task ID, mesin tempat command dijalankan, folder kerja, command, hasil yang diharapkan dan pesan aktual. Contoh: “E-02, guest Source, `~/LogLab`, bootstrap gagal karena dependency belum diterbitkan.” Dengan konteks ini, integrator dapat membedakan masalah kode, paket, jaringan, atau panduan.

Jika yang belum tersedia adalah fondasi F-03/F-04, catat sebagai **blocked**, yaitu pekerjaan belum dapat dilanjutkan karena membutuhkan hasil pekerjaan lain. Jika kode sudah dapat dijalankan tetapi perilakunya salah, catat sebagai **fail**, lalu perbaiki dan tes kembali. Status **pass** hanya dipakai setelah syarat pemeriksaan terpenuhi.
