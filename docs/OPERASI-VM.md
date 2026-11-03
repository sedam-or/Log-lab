# Operasi VM: pasang, verifikasi, pindah branch, reset

Panduan ini untuk dua VM host-only (Source `172.16.202.21`, Monitor `172.16.202.22`) dan host `172.16.202.1`. Semua perintah di VM dijalankan sebagai user `loglab` dari `/home/loglab/LogLab` kecuali tertulis `sudo`. Hasil yang Anda catat harus berupa output nyata; skrip hanya membuktikan proses hidup, bukan delivery.

## 1. Di host: buat bundle

```bash
make lab-bundle                       # menulis ~/loglab-bundle (ubah dengan LOGLAB_BUNDLE_OUT=...)
```

Bundle berisi `ca.crt`, `source/` (env, TLS, `test-accounts.json`), `monitor/` (env, TLS) dan `KREDENSIAL-PRIVAT.txt` (password operator dan akun demo; satu-satunya tempat password asli). Folder harus di luar Git dan tidak boleh dikirim lewat chat atau laporan. Private key CA dibuang setelah penandatanganan; untuk memperbarui sertifikat, buat bundle baru dan pasang ulang di kedua VM (token, CA, dan sertifikat berubah bersama).

```bash
ssh loglab@172.16.202.21 'mkdir -p ~/bundle' && scp -r ~/loglab-bundle/source ~/loglab-bundle/ca.crt loglab@172.16.202.21:~/bundle/
ssh loglab@172.16.202.22 'mkdir -p ~/bundle' && scp -r ~/loglab-bundle/monitor ~/loglab-bundle/ca.crt loglab@172.16.202.22:~/bundle/
```

Hasilnya di VM: `~/bundle/ca.crt` dan `~/bundle/source/` (VM A) atau `~/bundle/monitor/` (VM B). Jangan menyalin `monitor/` ke VM A atau `source/` ke VM B. Hapus `~/bundle` di VM setelah setup berhasil (berkas sudah disalin ke `/etc/loglab`).

## 2. Di tiap VM: ambil kode dan siapkan Python

```bash
git clone --branch staging https://github.com/sedam-or/Log-lab.git ~/LogLab   # pertama kali
cd ~/LogLab && git fetch origin && git switch staging && git pull --ff-only    # berikutnya
make dev-setup                       # butuh internet sementara (NAT) untuk pip; matikan sesudahnya
```

## 3. Pasang peran

VM A (Source) dan VM B (Monitor). Skrip idempoten dan tidak menimpa berkas yang sudah ada di `/etc/loglab`.

```bash
sudo make setup-source  LOGLAB_BUNDLE=$HOME/bundle    # VM A
sudo make setup-monitor LOGLAB_BUNDLE=$HOME/bundle    # VM B
# Bila masih SSH lewat NAT dan firewall belum boleh aktif: tambahkan LOGLAB_SKIP_FIREWALL=1
```

Kode keluar khusus: `3` = IP host-only belum terpasang di VM; `4` = `/etc/loglab/test-accounts.json` belum ada (Source). Setelah diperbaiki, jalankan perintah yang sama lagi.

## 4. Verifikasi (catat output aktualnya)

```bash
# dari host
curl --cacert ~/loglab-bundle/ca.crt https://172.16.202.21:8443/health
curl --cacert ~/loglab-bundle/ca.crt https://172.16.202.22:8443/health
# login benar dan salah (password ada di KREDENSIAL-PRIVAT.txt)
curl --cacert ~/loglab-bundle/ca.crt -H 'Content-Type: application/json' \
     -d '{"username":"demo-user-01","password":"<password>"}' https://172.16.202.21:8443/api/v1/login
```

Lalu: buka `https://172.16.202.21:8443/login` dan coba akun demo; pastikan event tiba di Monitor (di VM B: `sudo -u loglab-svc sqlite3 /var/lib/loglab/monitor.sqlite3 'select count(*) from monitor_events'`, perlu paket `sqlite3`; halaman dashboard operator baru dapat dipakai setelah rutenya ada di Monitor, lihat status R-04..R-06 di `docs/tugas/index.md`); matikan Monitor 60 detik (`sudo systemctl stop loglab-monitor` di VM B), buat beberapa login, hidupkan lagi, dan pastikan semua event terkirim tanpa duplikat; reboot kedua VM dan cek ulang `/health`; dari VM A pastikan SSH ke VM B ditolak. Status service: `systemctl status loglab-source` / `loglab-monitor`, log: `journalctl -u loglab-source -n 50`.

Batasan yang diketahui: event berstatus `held` (ditolak permanen oleh Monitor) tidak punya jalur pelepasan otomatis; mereka tetap di outbox dan tampil di `held_count`.

## 5. Pindah branch (staging ke production)

Staging dan production memakai VM yang sama. Pindah branch tidak menghapus `/var/lib/loglab`, jadi data uji ikut terbawa bila tidak direset.

```bash
cd ~/LogLab && git fetch origin && git switch production && git pull --ff-only
make dev-setup                       # hanya bila requirements.lock berubah
sudo make setup-source   # VM A, atau setup-monitor di VM B (tanpa LOGLAB_BUNDLE bila /etc/loglab sudah terisi)
```

## 6. Backup dan reset data sebelum demo

Monitor membuat backup harian di `/var/backups/loglab/daily.sqlite3` (timer `loglab-monitor-backup.timer`). Untuk reset yang aman, simpan salinan dulu, bukan menghapus:

```bash
# VM B
sudo systemctl stop loglab-monitor
sudo install -d -m 0700 /var/backups/loglab/staging-$(date +%F)
sudo mv /var/lib/loglab/monitor.sqlite3* /var/backups/loglab/staging-$(date +%F)/
sudo systemctl start loglab-monitor     # database kosong dibuat ulang saat start
# VM A
sudo systemctl stop loglab-source
sudo install -d -m 0700 /var/backups/loglab/staging-$(date +%F)
sudo mv /var/lib/loglab/source.sqlite3* /var/backups/loglab/staging-$(date +%F)/
sudo make setup-source                  # seed ulang akun demo dari /etc/loglab/test-accounts.json
```

Reset Source dan Monitor bersamaan. Source yang direset memulai `stream_id` dan sequence baru; bila hanya satu sisi yang direset, data kedua VM tidak lagi saling sesuai dan hasil uji sulit ditafsirkan. Latihan restore Monitor (tanpa menyentuh data aktif): `.venv/bin/python deployment/monitor/restore_drill.py`.
