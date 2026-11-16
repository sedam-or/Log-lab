# Lampiran Lembar Modul 7: Engineering Baseline

Keadaan repository pada 16 November 2026, setelah commit baseline dibuat. Tidak memuat password, token, private key, atau data sensitif.

## 1. Commit dan tag baseline

| Ketentuan | Isi |
| --- | --- |
| Branch | `dev` |
| Commit dasar | `e340722` (artefak Modul 5 dan 6) |
| Commit baseline | `3c83b3b` (Tambah baseline container Modul 7) |
| Tag baseline | `baseline-m07` (anotasi, lokal) |
| Push | Belum dilakukan. |

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

Bukti dari laptop host, bukan VM.

| Pemeriksaan | Hasil |
| --- | --- |
| Health Source dan Monitor (HTTPS, CA lab, dari dalam container) | `{"service":"loglab-source","state":"ready","contract_version":"1.1.0"}` dan `loglab-monitor` serupa |
| Hash operator cocok dengan kata sandi di folder privat | `operator hash cocok: True` |
| Seed dua akun uji dan login lewat Source | `Akun baru ditambahkan: 2 dari 2`; login `{"result":"success"}` |
| Event sampai di Monitor | `event di Monitor: 1` |
| Restart kedua container | Keduanya kembali `healthy`; event tetap 1 |
| Hardening | `user=10001:10001`, `readonly=true`, `caps_drop=[ALL]`, `no-new-privileges:true`, tanpa port publik |
| Tes statis dalam image Python 3.13 | 216 lulus, 1 dilewati (`nft -c`, sudah ada sebelumnya) |
| `check_contract.py` | PASS kontrak 1.1.0 |

Status `docker compose ps`: `loglab-source` dan `loglab-monitor`, keduanya `Up ... (healthy)`, tanpa port yang dipublikasikan.

## 5. Catatan masalah dan perbaikan

1. **Health gagal: sertifikat tanpa Authority Key Identifier.** Python 3.13 dengan OpenSSL 3 menolak sertifikat tersebut. Perbaikan: `make-private.sh` menambahkan SKID dan AKID.
2. **Hash operator rusak di container.** Compose menginterpolasi `$` pada `env_file`. Perbaikan: folder privat menulis `$$`; hash diverifikasi ulang di container.
3. **`PermissionError` pada kunci TLS.** Izin direktori bind mount tidak terbaca oleh UID 10001. Perbaikan khusus lab: direktori `0755`, kunci `0644`. Di VM dipakai `root:loglab-svc` dan `0640`; izin lab ini tidak dipakai di VM.
4. **Subnet kontrak bertabrakan dengan jaringan host.** `172.16.202.0/24` sudah dipakai `vmnet1` di laptop. Perbaikan: jaringan container `internal: true`. Rute host tetap lewat `vmnet1`. Pemeriksaan dilakukan dari dalam container.
5. **Monitor sehat, tetapi model belum ada.** `model.json` tidak ada, sehingga status analisis `model_not_configured`. Sesuai status F-05.

Yang belum dilakukan:
- Belum diuji di VM. Ini menjadi bagian I-02.
- Tidak ada pemindaian image (slide 20 menyarankan).
- Tidak ada registry. Jika image dibawa ke VM, jalurnya `docker save` lalu `docker load`; belum diuji.
- Dashboard belum dapat dibuka dari browser host, karena port tidak dipublikasikan.
