# Diagram untuk memahami proses kerja

Diagram berikut ditulis menggunakan Mermaid. Markdown panduan memakai PNG yang sudah dirender agar gambar tetap terbaca di GitHub atau saat nanti diekspor. File `.mmd` adalah sumber yang dapat diedit; PNG adalah gambar hasil render, bukan screenshot VMware.

| Sumber Mermaid | Gambar | Yang dijelaskan |
| --- | --- | --- |
| [host-ssh.mmd](host-ssh.mmd) | [PNG](host-ssh.png) | Terminal host, console, SSH, guest dan folder proyek |
| [event-journey.mmd](event-journey.mmd) | [PNG](event-journey.png) | Login, commit, sender, receipt, ACK dan analisis |
| [git-journey.mmd](git-journey.mmd) | [PNG](git-journey.png) | Branch, tes, PR, sinkronisasi, merge dan deployment |
| [erna-journey.mmd](erna-journey.mmd) | [PNG](erna-journey.png) | Urutan task Erna sampai handoff dan uji bersama |
| [arhasya-journey.mmd](arhasya-journey.mmd) | [PNG](arhasya-journey.png) | Task Arhasya dan dependency training integrator |
| [integration-journey.mmd](integration-journey.mmd) | [PNG](integration-journey.png) | Fondasi, coding paralel, audit, uji pasangan dan rilis |
| [local-and-integration.mmd](local-and-integration.mmd) | [PNG](local-and-integration.png) | Dua laptop pengembangan dan satu host integrasi |

Render dibuat menggunakan Mermaid CLI 12.0.0 dan browser lokal. Untuk render ulang, gunakan versi tool yang sama bila ingin menyamakan layout. Tool ini diperlukan untuk mengubah diagram, bukan dependency runtime aplikasi di VM. Dari root repo, contoh command pada CLI yang mendukung `--size` adalah:

```bash
mmdc -i docs/architecture/assets/learning/host-ssh.mmd \
     -o docs/architecture/assets/learning/host-ssh.png \
     --size 1800 -s 1.5 -b white
```

Periksa `mmdc --help` pada versi tool yang dipakai; nama opsi ukuran dapat berbeda antarversi. Setelah sumber berubah, render ulang dan periksa gambar agar tidak ada teks terpotong atau panah yang mengaburkan makna.
