# Repository Evidence (Modul 5) - LogLab

Sumber editable untuk `LogLab_M05_Repository-Evidence.pdf`. Keadaan repository pada 3 November 2026, setelah PR #3 di-merge.

## 1. Lokasi/path repository

- Remote: https://github.com/sedam-or/Log-lab.git (publik)
- Clone pada VM: `/home/loglab/LogLab` (ditetapkan kontrak)
- Branch bawaan: `dev`; tag `mulai-v1` (baseline sejarah)

## 2. Ringkasan branch dan merge

| Branch | Commit | Fungsi |
| --- | --- | --- |
| dev | 029714b | Kerja harian; commit langsung per tahap |
| staging | e9766a4 | Uji dua VM; hanya lewat PR dari dev |
| production | c905828 | Demo final; hanya lewat PR dari staging |

| PR | Dari ke | Merge | Review tercatat |
| --- | --- | --- | --- |
| #1 login Source ke outbox | feat/erna-login-outbox ke main (lalu production) | c905828 | Tidak ada |
| #2 Monitor R-03 sampai R-06 | feat/arhasya-ingest ke main (lalu production) | 3963567 | Tidak ada |
| #3 Promosi dev ke staging | dev ke staging | e9766a4 | 2 approval (Erna, Arhasya) |

## 3. Cuplikan git log

`git log --graph --oneline --all --decorate=short`

```
*   e9766a4 (origin/staging) Merge pull request #3 from sedam-or/dev
|\  
| * 029714b (HEAD -> dev, origin/dev) Naikkan kontrak ke 1.1.0
| * db0129e Tambah bundle lab dan target make setup
| * f948b70 Tambah deployment Source
| * 62a4dd0 Tambah sender Source: kirim, receipt, retry, heartbeat
| * 7ac73cd Selaraskan route dan entrypoint Source dengan kontrak
| * 7c73494 Ganti alur branch ke dev/staging/production
|/  
*   c905828 (origin/production, production) Merge pull request #1 from acaa-asikk/feat/erna-login-outbox
|\  
| * 84f54e0 feat: route login, seed akun fiktif, dan tes E3-03 sampai E3-05
| * 6df465c refactor: samakan nama file dengan target (source_service, test_source)
| * 22e5369 feat: login source menulis event ke outbox sesuai kontrak v1
* |   3963567 Merge pull request #2 from chocoberryy/feat/arhasya-ingest
|\ \  
| |/  
|/|   
| * d000525 docs: catatan hasil Arhasya R-03 sampai R-06
| * ef3ee18 feat: deployment Monitor (setup, systemd, firewall, backup) (R-06)
| * fbc9334 feat: penerima event, startup, dan console operator (R-03, R-05)
| * 2d60e18 feat: window, kualitas snapshot, revisi, rules, dan model (R-04, R-05)
| * 1e670a3 feat: fitur login-window-v1 (R-04)
| * ddb62f1 feat: endpoint penerima event dan status monitor (R-03)
|/  
* e414695 (tag: mulai-v1) Prepare shared coding foundations and beginner setup guides
* 19edc10 Freeze versioned VM parameters and enforce configuration checks
* 05fe3c2 Simplify member navigation and define expected branch deliverables
* 92adf0f Explain member workflows for beginners with rendered Mermaid diagrams
* 9be8ba7 Refine member coding tasks and migrate indexed project documentation
* 85823c7 Document Debian baseline and collaborative repository structure
* a5e0c51 Initial commit
```

## 4. Contoh conflict dan penyelesaiannya

**LATIHAN, bukan kejadian nyata proyek.** Dua cabang sementara memperbaiki baris yang sama di `docs/ATURAN-SINGKAT.md`, lalu digabung di clone sementara (tidak di-push).

```
$ git switch -c latihan/konflik-a origin/staging
Switched to a new branch 'latihan/konflik-a'
branch 'latihan/konflik-a' set up to track 'origin/staging'.
$ git switch -c latihan/konflik-b origin/staging
Switched to a new branch 'latihan/konflik-b'
branch 'latihan/konflik-b' set up to track 'origin/staging'.
$ git switch latihan/konflik-a
Switched to branch 'latihan/konflik-a'
Your branch is ahead of 'origin/staging' by 1 commit.
  (use "git push" to publish your local commits)
$ git merge latihan/konflik-b
Auto-merging docs/ATURAN-SINGKAT.md
CONFLICT (content): Merge conflict in docs/ATURAN-SINGKAT.md
Automatic merge failed; fix conflicts and then commit the result.
$ git status --short
UU docs/ATURAN-SINGKAT.md
$ sed -n 6,12p docs/ATURAN-SINGKAT.md
<<<<<<< HEAD
2. **Python 3.13 tepat** dan `requirements.lock` (versi eksak, diperiksa CI). `make dev-setup` me...
=======
2. **Python 3.13 tepat** dan `requirements.lock` (jangan pakai versi lain di VM). `make dev-setup...
>>>>>>> latihan/konflik-b
3. **Kontrak** `config/contract.json` mengikat IP, port, nama env, endpoint, izin file. Ubah hany...
4. **Secret tidak masuk Git.** Env nyata di `/etc/loglab/*.env`, bundle lab di luar clone.
$ (resolusi: gabungkan kedua maksud menjadi satu baris, hapus penanda <<<<<<< ======= >>>>>>>)
$ sed -n 6,8p docs/ATURAN-SINGKAT.md
2. **Python 3.13 tepat** dan `requirements.lock` (versi eksak, diperiksa CI; jangan pakai versi l...
3. **Kontrak** `config/contract.json` mengikat IP, port, nama env, endpoint, izin file. Ubah hany...
4. **Secret tidak masuk Git.** Env nyata di `/etc/loglab/*.env`, bundle lab di luar clone.
$ git add docs/ATURAN-SINGKAT.md && git commit -m "Latihan: selesaikan konflik ATURAN-SINGKAT"
selesai
$ git log --graph --oneline -5
*   94e81af Latihan: selesaikan konflik ATURAN-SINGKAT
|\  
| * af88ea4 Latihan: tegaskan aturan Python di cabang B
* | 1c8bdd1 Latihan: tegaskan aturan Python di cabang A
|/  
*   e9766a4 Merge pull request #3 from sedam-or/dev
|\  
| * 029714b Naikkan kontrak ke 1.1.0
```

Penyelesaian: kedua maksud digabung menjadi satu baris, penanda konflik dihapus, lalu di-add dan di-commit sebagai merge commit.

## 5. Kontribusi anggota

| Pihak | Bukti di repository |
| --- | --- |
| Erna (acaa-asikk) | PR #1: 3 commit; menyetujui PR #3 |
| Arhasya (chocoberryy) | PR #2: 6 commit; menyetujui PR #3 |
| Integrator (sedam-or) | Membuat dan me-merge PR #3; menyusun branch; 6 commit di dev di-commit atas nama integrator |
| Claude Code (asisten AI) | Menulis kode 6 commit pada dev atas arahan integrator (Co-Authored-By); bukan anggota tim |

Kontribusi anggota di luar PR di atas tidak dapat diverifikasi dari repository dan diisi oleh anggota yang bersangkutan.

## Belum dilakukan

- Uji dua VM dari branch staging (I-02)
- PR staging ke production
- Tag v1.1.0
