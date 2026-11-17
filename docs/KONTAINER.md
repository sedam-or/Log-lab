# Baseline container LogLab (Modul 7)

Dokumen ini adalah sumber untuk Lembar Artefak Modul 7 (`LogLab_M07_Engineering-Baseline`). Jalur resmi tetap systemd di dua VM (lihat [OPERASI-VM.md](OPERASI-VM.md)). Container adalah baseline yang dapat direproduksi di laptop dengan Docker. Container **tidak** membuktikan aplikasi berjalan di VM; itu tetap menunggu I-02.

## File

| File | Fungsi |
| --- | --- |
| `deployment/container/Dockerfile` | Satu image untuk peran Source dan Monitor, base image dikunci digest, dependency dari `requirements.lock` dengan hash |
| `deployment/container/Dockerfile.dockerignore` | Membuang secret, folder privat, database, dan folder dokumentasi dari konteks build |
| `deployment/container/compose.yaml` | Dua service dengan IP kontrak (`172.16.202.21` Source, `172.16.202.22` Monitor), jaringan internal, tanpa port publik |
| `deployment/container/make-private.sh` | Membuat folder privat uji: env dari `config/*.example.env`, TLS lab, akun uji, dan kata sandi operator acak |
| `deployment/container/smoke-e2e.sh` | Uji e2e: build, start, health, verifikasi hash operator, seed akun, login, dan cek event di Monitor |

Env tidak dibuat ulang untuk container. Nilai yang dipakai sama dengan VM (kontrak 1.1.0 tidak diubah), sehingga `Settings.from_env` memvalidasinya seperti biasa.

## Perintah

Dari root repo, dengan Docker terpasang. Folder privat berada di luar Git (default `~/loglab-private`).

```bash
make container-private LOGLAB_PRIVATE_DIR=$HOME/loglab-private   # sekali; folder harus kosong
make container-build   LOGLAB_PRIVATE_DIR=$HOME/loglab-private   # build image loglab-app:1.1.0
make container-up      LOGLAB_PRIVATE_DIR=$HOME/loglab-private   # start dua service
make container-check   LOGLAB_PRIVATE_DIR=$HOME/loglab-private   # status dan health
make container-e2e     LOGLAB_PRIVATE_DIR=$HOME/loglab-private   # uji e2e lengkap
make container-down    LOGLAB_PRIVATE_DIR=$HOME/loglab-private   # stop dan hapus container (volume tetap)
```

Untuk menghapus data uji sepenuhnya: `docker compose -f deployment/container/compose.yaml down -v`. Perintah ini menghapus volume DB, jadi jalankan hanya pada laptop uji.

## Bukti (laptop, 16 November 2026; dijalankan ulang 17 November 2026)

Bukti ini berasal dari laptop host, bukan VM. Nilai secret tidak dicatat di sini.

| Pemeriksaan | Hasil |
| --- | --- |
| Build image `loglab-app:1.1.0` | Berhasil; image ID `6d753a81a963`, ukuran 213 MB, user `10001:10001` |
| `docker compose config` tanpa peringatan interpolasi | Tidak ada peringatan setelah `$` pada hash di-escape |
| Health Source dan Monitor (HTTPS, verifikasi CA lab, dari dalam container) | `{"service":"loglab-source","state":"ready","contract_version":"1.1.0"}` dan versi serupa untuk Monitor |
| Hash operator cocok dengan kata sandi di folder privat | `operator hash cocok: True` |
| Seed dua akun uji dan login lewat Source | `Akun baru ditambahkan: 2 dari 2`; login `{"result":"success"}` |
| Event sampai di Monitor | `event di Monitor: 1` (`monitor_events`) |
| Restart kedua container | Keduanya kembali `healthy`; event tetap `1` (volume bertahan) |
| Hardening | `user=10001:10001`, `readonly=true`, `caps_drop=[ALL]`, `no-new-privileges:true`, tanpa port publik |
| Tes statis | 216 tes lulus dalam image Python 3.13, 1 dilewati (`nft -c`, sudah ada sebelumnya); `check_contract.py` PASS |

Log mentah disimpan di luar repo (`<scratchpad>/m7/logs/`) dan tidak dikomit.

## Masalah dan perbaikan

Semua masalah di bawah muncul saat uji dan sudah diperbaiki kecuali yang ditandai terbuka.

1. **Health gagal: `CERTIFICATE_VERIFY_FAILED ... Missing Authority Key Identifier`.** Python 3.13 dengan OpenSSL 3 menolak sertifikat tanpa AKID/SKID. Perbaikan: `make-private.sh` menambahkan `subjectKeyIdentifier` pada CA dan `authorityKeyIdentifier` pada sertifikat peran.
2. **Hash operator rusak di container.** Compose menginterpolasi `$` pada `env_file`, sehingga bagian `$16384$8$1$<salt>` hilang dan login operator akan gagal. Perbaikan: `monitor.env` di folder privat menulis `$$`; Compose mengembalikannya ke `$`. Verifikasi `operator hash cocok: True` membuktikannya. File `config/monitor.example.env` tidak diubah.
3. **`PermissionError` saat membaca kunci TLS.** Direktori bind mount berizin `0700` milik UID host (1000), sehingga UID container 10001 tidak bisa masuk. Perbaikan khusus lab: direktori `0755`, berkas kunci `0644`. Di VM, `deployment/source/setup.sh` memakai `root:loglab-svc` dengan `0640`; izin lab ini **tidak** dipakai di VM.
4. **Subnet kontrak bersinggungan dengan jaringan host.** `172.16.202.0/24` sudah dipakai `vmnet1` pada laptop ini. Keputusan: jaringan container memakai subnet kontrak tetapi `internal: true`, tanpa gateway NAT, dan tanpa port publik. Rute host ke `172.16.202.0/24` tetap lewat `vmnet1` (dicek dengan `ip route get`). Container saling terhubung lewat bridge. Akibatnya, pemeriksaan dilakukan dari dalam container (`docker compose exec`), bukan dari browser host.
5. **Monitor sehat tetapi analisis ML belum aktif.** `model.json` tidak ada (`model_absent`), sehingga Monitor berjalan dengan `model_not_configured`. Ini sesuai status F-05 (paket model belum ada). Health 200 tidak membuktikan analisis, sebagaimana tertulis di docstring `/health` Monitor.
6. **Container lama menunjuk folder yang sudah hilang (17 November).** Bind mount TLS masih mengarah ke folder scratchpad uji. Setelah folder itu hilang, kedua service crash-loop dengan `FileNotFoundError` saat memuat sertifikat. Perbaikan: `make container-down`, lalu folder privat tetap di `~/loglab-private` dan e2e ulang.
7. **Akun uji lama tersisa di volume (17 November).** Seed menjawab `0 dari 2` dan login mendapat HTTP 401, karena kata sandi di volume tidak cocok dengan folder privat baru. Perbaikan: `docker compose -f deployment/container/compose.yaml down -v` pada laptop uji, lalu e2e dari awal. Perintah ini hanya menghapus volume uji di laptop.

## Batas dan yang belum dilakukan

- **Belum dibuktikan di VM.** Container tidak menggantikan I-02. Jalur VM tetap `make setup-source` dan `make setup-monitor` dengan bundle.
- **Tidak ada akses dari browser host.** Port tidak dipublikasikan agar tidak mengekspos layanan. Dashboard hanya bisa dibuka dari dalam jaringan container atau lewat tunnel yang disepakati tim (belum diuji).
- **Tidak ada pemindaian image.** Slide 20 menyarankan image scanning; belum dilakukan.
- **Tidak ada registry.** VM tidak punya internet saat runtime (`runtime_nat_enabled: false`). Jika image dibawa ke VM, jalurnya `docker save` lalu `docker load`; belum diuji.
- **Kunci dan CA hanya untuk uji.** CA dibuat sementara oleh `make-private.sh` dan kuncinya dihapus. CA lab untuk VM dibuat dengan jalur bundle, bukan skrip ini.
- **Modul 5 perlu dibuat ulang** setelah commit baseline ini masuk, supaya git log yang dilampirkan mencakupnya.
