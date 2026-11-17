# Lampiran Lembar Modul 7: Engineering Baseline

Keadaan repository pada 17 November 2026. Tidak memuat password, token, private key, atau data sensitif.

## 1. Commit dan tag baseline

| Ketentuan | Isi |
| --- | --- |
| Branch | `dev` |
| Commit dasar | `e340722` (artefak Modul 5 dan 6) |
| Commit baseline | `3c83b3b` (Tambah baseline container Modul 7) |
| Tag baseline | `baseline-m07` (anotasi, lokal, menunjuk `3c83b3b`) |
| Push ke `origin` | Belum dilakukan (commit `e340722` dan `3c83b3b` serta tag masih lokal). |

Isi commit baseline `3c83b3b`: `deployment/container/` (Dockerfile, Dockerfile.dockerignore, compose.yaml, make-private.sh, smoke-e2e.sh), `docs/KONTAINER.md`, `tests/test_container_files.py`, target `container-*` di `Makefile`, entri `CHANGELOG.md`, dan baris I-04 di `docs/tugas/index.md`.

## 2. Dockerfile dan Compose yang dipakai

| File | Fungsi |
| --- | --- |
| `deployment/container/Dockerfile` | Satu image untuk peran Source dan Monitor |
| `deployment/container/Dockerfile.dockerignore` | Membuang secret, folder privat, database, dan dokumentasi dari konteks build |
| `deployment/container/compose.yaml` | Dua service dengan IP kontrak, jaringan internal, tanpa port publik |
| `deployment/container/make-private.sh` | Membuat folder privat uji di luar Git |
| `deployment/container/smoke-e2e.sh` | Uji e2e: build, start, health, login, dan event di Monitor |

Poin penting Dockerfile:
- Base image `python:3.13-slim` dikunci digest `sha256:e48f59cd...`.
- Dependency dipasang dengan `pip install --require-hashes --no-deps -r requirements.lock`.
- Berjalan sebagai `10001:10001`, bukan root.
- Entrypoint `python -m uvicorn`. Peran dan IP dipilih oleh `command` di compose.

Poin penting Compose:
- Source `172.16.202.21` dan Monitor `172.16.202.22`, sama dengan kontrak 1.1.0. Env tidak diubah.
- Jaringan `loglab-net` bersifat `internal: true`, tanpa NAT dan tanpa port publik (`runtime_nat_enabled: false`).
- `read_only: true`, `cap_drop: ALL`, `no-new-privileges:true`.
- Env dan TLS diambil dari folder privat (`LOGLAB_PRIVATE_DIR`), bukan dari repo.

## 3. Perintah build dan run

```
make container-private LOGLAB_PRIVATE_DIR=$HOME/loglab-private
make container-build   LOGLAB_PRIVATE_DIR=$HOME/loglab-private
make container-up      LOGLAB_PRIVATE_DIR=$HOME/loglab-private
make container-e2e     LOGLAB_PRIVATE_DIR=$HOME/loglab-private
make container-down    LOGLAB_PRIVATE_DIR=$HOME/loglab-private
```

Build image menghasilkan `loglab-app:1.1.0` (image ID `6d753a81a963`, 213 MB). Perintah `docker compose config` tidak memberi peringatan interpolasi.

## 4. Bukti service berjalan

Bukti dari laptop host, bukan VM. Dijalankan ulang pada 17 November 2026 dari keadaan bersih: volume uji dihapus dengan `docker compose down -v`, lalu folder privat baru dibuat di `~/loglab-private` dengan `make container-private`.

| Pemeriksaan | Hasil |
| --- | --- |
| Health Source dan Monitor (HTTPS, CA lab, dari dalam container) | `{"service":"loglab-source","state":"ready","contract_version":"1.1.0"}` dan `loglab-monitor` serupa |
| Hash operator cocok dengan kata sandi di folder privat | `operator hash cocok: True` |
| Seed dua akun uji dan login lewat Source | `Akun baru ditambahkan: 2 dari 2`; login `{"result":"success"}` |
| Event sampai di Monitor | `event di Monitor: 1` |
| Restart kedua container (`docker compose restart`) | Keduanya kembali `healthy`; `monitor_events` tetap 1 |
| Hardening | `user=10001:10001`, `ReadonlyRootfs=true`, `CapDrop=[ALL]`, `no-new-privileges:true` |
| Port ke host | `HostConfig.PortBindings` kosong; `8443/tcp` hanya `EXPOSE` tanpa binding |
| Tes dalam image Python 3.13 | 216 lulus, 1 dilewati (`nft -c`, sudah ada sebelumnya) |
| Tes container di host (`tests/test_container_files.py`) | 14 lulus |
| `scripts/check_contract.py` dalam image | PASS kontrak 1.1.0 |

Status `docker compose ps`: `loglab-source` dan `loglab-monitor`, keduanya `Up ... (healthy)`, dengan `8443/tcp` tanpa pemetaan ke host.

## 5. Catatan masalah dan perbaikan

1. **Health gagal: sertifikat tanpa Authority Key Identifier.** Python 3.13 dengan OpenSSL 3 menolak sertifikat tersebut. Perbaikan: `make-private.sh` menambahkan SKID dan AKID.
2. **Hash operator rusak di container.** Compose menginterpolasi `$` pada `env_file`. Perbaikan: folder privat menulis `$$`; hash diverifikasi ulang di container.
3. **`PermissionError` pada kunci TLS.** Izin direktori bind mount tidak terbaca oleh UID 10001. Perbaikan khusus lab: direktori `0755`, kunci `0644`. Di VM dipakai `root:loglab-svc` dan `0640`; izin lab ini tidak dipakai di VM.
4. **Subnet kontrak bertabrakan dengan jaringan host.** `172.16.202.0/24` sudah dipakai `vmnet1` di laptop. Perbaikan: jaringan container `internal: true`. Rute host tetap lewat `vmnet1`. Pemeriksaan dilakukan dari dalam container.
5. **Monitor sehat, tetapi model belum ada.** `model.json` tidak ada, sehingga status analisis `model_not_configured`. Sesuai status F-05.
6. **Folder privat uji tidak lagi tersedia (17 November).** Container yang masih berjalan memasang sertifikat dari folder uji sementara yang sudah dihapus, sehingga kedua service gagal start dengan `FileNotFoundError` saat memuat sertifikat. Perbaikan: `make container-down`, buat folder privat tetap di `~/loglab-private` dengan `make container-private`, lalu jalankan e2e ulang.
7. **Akun uji lama tersisa di volume (17 November).** Setelah folder privat diganti, seed menjawab `0 dari 2` dan login mendapat HTTP 401, karena kata sandi di volume tidak lagi cocok dengan folder baru. Perbaikan: `docker compose -f deployment/container/compose.yaml down -v` pada laptop uji, lalu e2e dari awal. Perintah ini menghapus volume data uji, bukan data VM.

Yang belum dilakukan:
- Belum diuji di VM. Ini menjadi bagian I-02.
- Tidak ada pemindaian image (slide 20 menyarankan).
- Tidak ada registry. Jika image dibawa ke VM, jalurnya `docker save` lalu `docker load`; belum diuji.
- Dashboard belum dapat dibuka dari browser host, karena port tidak dipublikasikan.
- Commit dan tag `baseline-m07` belum di-push ke `origin`.
