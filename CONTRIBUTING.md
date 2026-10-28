# Cara berkontribusi

Tim bekerja pada satu repository. Integrator menjaga kontrak dan berkas bersama; Erna mengerjakan Source, sedangkan Arhasya mengerjakan Monitor. Nama anggota ditambahkan ketika pembagian tugas dibagikan.

## Branch dan perubahan bersama

Kerangka dokumentasi awal dicatat langsung di `main` atas instruksi pemilik. Sesudah fondasi ini, pekerjaan anggota memakai branch singkat dan PR ke `main`. Semua anggota mulai dari baseline commit yang sama, yang hash-nya dicatat pada task setelah baseline diterima.

```bash
git clone https://github.com/sedam-or/Log-lab.git
cd Log-lab
git switch main
git pull --ff-only origin main
git switch -c feat/erna-login-outbox
```

Arhasya memakai `feat/arhasya-ingest`. Pecah pekerjaan besar menjadi PR yang dapat ditinjau sendiri, misalnya provisioning dahulu, kemudian startup dan verifikasi. Commit memakai subjek singkat yang menjelaskan perubahan, misalnya `Document Source setup prerequisites`.

Batas file mengikuti tabel pada [baseline](docs/architecture/BASELINE.md). Perubahan kontrak, dependency lock, konfigurasi bersama, atau target root Makefile dikoordinasikan melalui PR bersama terlebih dahulu. Jangan mengubahnya berbeda-beda pada branch A dan B.

## Pemeriksaan PR

Deskripsi PR menyebut task ID, tujuan, file utama, perintah verifikasi beserta hasil aktual, dan keterbatasan. Tandai bagian yang belum diuji. Minimal satu anggota lain meninjau perubahan sebelum integrator melakukan merge. Pengaturan GitHub untuk perlindungan `main` masih perlu dikonfigurasi; aturan tertulis ini belum berarti proteksi server sudah aktif.

Periksa `git status`, `git diff`, dan `git diff --cached` sebelum commit. Jangan stage seluruh workspace praktikum. Pastikan tidak ada secret, database, file VM, atau evidence privat. Screenshot yang diklaim sebagai layar VMware harus berasal langsung dari layar/framebuffer VMware. Output SSH disimpan sebagai bukti terminal dengan penamaan yang sesuai.

## Sinkronisasi dan merge

Merge PR satu per satu. Setelah PR Erna masuk, Arhasya memperbarui branch-nya dari `main` dan mengulang verifikasi yang terdampak. Cara sinkronisasi yang disarankan untuk branch kolaboratif:

```bash
git fetch origin
git switch feat/arhasya-ingest
git merge origin/main
# Jika ada konflik: periksa kedua perubahan, edit, lalu git add <file>.
# Jika konflik memang terjadi: akhiri resolusi dengan git commit.
git push origin feat/arhasya-ingest
```

Jangan memakai force-push atau memilih seluruh sisi konflik tanpa memahami perubahan. Jika resolusi mengubah kontrak, tinjau bersama kedua pemilik VM. Gunakan merge commit pada PR agar graph branch mudah dibaca untuk Modul 5. Pilihan merge di GitHub perlu diverifikasi saat repo dikonfigurasi.

Tidak adanya konflik Git belum membuktikan layanan kompatibel. Sesudah kedua PR masuk, deploy kedua peran pada satu host integrasi dan uji aliran A–B. Tag rilis hanya dibuat setelah acceptance pasangan selesai; hash commit dan hasil uji dicatat.

## Bukti Modul 5

Kumpulkan PR/commit nyata atas nama anggota yang mengerjakannya. Jangan mengarang kontribusi, hasil tes, atau kejadian konflik. Jika tidak ada konflik alami, lakukan latihan konflik pada file dokumentasi khusus di branch latihan; beri label bahwa itu latihan. PDF evidence merangkum riwayat repo dan tetap menyertakan sumber editable.

## Panduan pekerjaan

[Erna](docs/tasks/erna.md) dan [Arhasya](docs/tasks/arhasya.md) memakai task peran terpisah, dengan satu [index status](docs/tasks/index.md). Keduanya mengikuti [workspace guest](docs/tasks/workspace.md). Nama branch contoh dapat disesuaikan ke task kecil berikutnya, tanpa membuat branch peran permanen.
