# Environment Strategy LogLab

Dokumen ini adalah sumber untuk Lembar Artefak Modul 6 (`<Tim>_M06_Environment-Strategy.xlsx`) dan mengikuti materi Pertemuan 6 (Environment Engineering). Tidak ada nilai secret di sini; hanya nama variabel dan lokasi.

## Environment dan branch

Materi membedakan empat environment; repo memakai tiga branch (syarat dosen). Pemetaannya:

| Environment | Di LogLab | Branch / tempat | Data dan konfigurasi | Akses | Perubahan |
| --- | --- | --- | --- | --- | --- |
| Development | Laptop host, `.venv` dari `make dev-setup` | `dev` | DB sementara, `Settings.for_test`, tanpa secret nyata | Pengembang | Sering |
| Testing | GitHub Actions (Python 3.13) dan `make test` lokal | push/PR ke `dev` | `tests/fixtures`, DB temporer; terpisah dari data VM | Terbatas | Terkelola |
| Staging | Dua VM host-only (Source `.21`, Monitor `.22`), uji pasangan I-02 | `staging` | env privat dari bundle, akun `demo-user-01/02`, TLS CA lab | Terkontrol | Terjadwal (PR promosi) |
| Production | Dua VM yang sama untuk demo final | `production` | struktur env sama dengan staging, DB dikosongkan sebelum demo | Sangat terkontrol | Terkendali (PR + tag) |
| Container (laptop, Modul 7) | Laptop host, image `loglab-app:1.1.0` lewat `docker compose` | `dev` (tag `baseline-m07`) | env dari `config/*.example.env` dan folder privat di luar Git (`make container-private`) | Pengembang laptop | Terkelola per commit; belum diuji di VM |

Staging dan production memakai VM yang sama karena hanya ada dua VM. Perbedaannya disengaja dan terdokumentasi: branch yang di-checkout dan data. Pindah branch tidak menghapus `/var/lib/loglab`; lihat prosedur backup dan reset di [OPERASI-VM.md](OPERASI-VM.md).

## Profil container laptop (Modul 7)

Profil container adalah baseline yang bisa direproduksi di laptop dengan Docker, bukan pengganti jalur VM. Image `loglab-app:1.1.0` memakai base `python:3.13-slim` dengan digest yang dikunci, dan dependency dipasang dari `requirements.lock` dengan hash. Dua service memakai IP kontrak (`172.16.202.21` dan `172.16.202.22`) pada jaringan internal tanpa NAT dan tanpa port publik. Nilai env sama dengan VM, sehingga kontrak 1.1.0 tidak berubah. Rincian perintah, bukti uji, dan masalah yang sudah diperbaiki ada di [KONTAINER.md](KONTAINER.md). Uji di VM tetap menjadi bagian I-02.

## Parity dan promotion

- Runtime sama di semua environment: Python 3.13 dan `requirements.lock` (versi terkunci), Debian 13 pada VM.
- Struktur konfigurasi sama: 15 variabel `LOGLAB_*` pada [config/contract.json](../config/contract.json); hanya nilai dan lokasi file yang berbeda.
- Resource boleh berbeda dan harus tercatat: laptop host bebas; Source 1 vCPU/1 GiB, Monitor 2 vCPU/2 GiB.
- Promotion memindahkan versi artefak yang sudah diperiksa (commit + hasil tes + konfigurasi + dependency) lewat PR `dev` → `staging` → `production`, bukan menyalin folder.

## Dependency

Sumber: `requirements.in`, `requirements.lock`, `pyproject.toml` (`requires-python >=3.13,<3.14`). Paket sistem VM: `nftables acl curl openssl ca-certificates`. Lock-file dikelola dengan versi eksak; perubahan versi melalui PR bersama.

## Peta konfigurasi

Daftar nama, fungsi dan lokasi ada di [config/contract.md](../config/contract.md) dan [interface-contracts/index.md](interface-contracts/index.md). Secret (`LOGLAB_SOURCE_TOKEN`, `LOGLAB_PSEUDONYM_KEY`, `LOGLAB_OPERATOR_PASSWORD_HASH`) hanya ada di `/etc/loglab/*.env` (root, 0600) dan bundle privat di luar Git. Template aman yang dilacak Git: `config/source.example.env`, `config/monitor.example.env`.
