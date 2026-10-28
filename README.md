# LogLab

LogLab adalah proyek praktikum Rekayasa Sistem untuk mencatat login akun fiktif, mengirim event dari VM A ke VM B, lalu menampilkan analisis rules dan satu model Logistic Regression lokal pada dashboard operator.

**Status 28 Oktober 2026:** repository ini berisi kerangka dokumentasi dan pembagian pekerjaan. Source aplikasi, skrip setup, dependency lock, pengujian, dan PDF tugas belum diterbitkan di sini. Belum ada perintah `make setup` yang dapat dijalankan. Implementasi dan evidence pada workspace sebelumnya belum otomatis menjadi bukti untuk repo ini.

## Mulai membaca

1. [Baseline kerja](docs/architecture/BASELINE.md): dua VM, OS, jaringan, batas reproducibility, dan pembagian file.
2. [Daftar pekerjaan](docs/TASKS.md): dokumen yang perlu ditulis, task A/B, dependensi, serta bukti penyelesaian.
3. [Cara berkontribusi](CONTRIBUTING.md): branch, PR, sinkronisasi, dan integrasi.

Kebutuhan produk dan sistem akan berada di [docs/requirements/](docs/requirements/). Rencana kontrak teknis A–B ada di [docs/interface-contracts/](docs/interface-contracts/).

## Struktur repository

Mengikuti contoh pada materi Pertemuan 5, slide 6. Setiap direktori saat ini memuat catatan cakupan; kode dan skrip ditambahkan melalui task yang tercatat.

```text
Log-lab/
├── src/                      # source aplikasi
├── tests/                    # unit, contract, dan integration tests
├── docs/
│   ├── requirements/         # PRD dan SRS
│   ├── architecture/         # baseline dan diagram arsitektur
│   ├── interface-contracts/  # schema/API dan fixture kontrak
│   └── TASKS.md              # satu daftar pekerjaan tim
├── config/                   # template konfigurasi tanpa secret
├── scripts/                  # alat bantu pengembangan dan evidence
├── deployment/               # provisioning dan konfigurasi dua VM
├── .gitignore
├── .gitattributes
├── AGENTS.md
├── CONTRIBUTING.md
├── README.md
└── CHANGELOG.md
```

Satu repository digunakan oleh kedua VM. Target setup Source dan Monitor akan berbeda; masing-masing memakai commit atau tag pasangan yang sudah diuji. Nama direktori deployment adalah `deployment/`, sesuai contoh materi; jangan menambahkan direktori `deploy/` kedua.

## SSH dari host

SSH direkomendasikan untuk memudahkan copy-paste perintah dari terminal host ketika clipboard console VMware tidak nyaman atau bermasalah. Anggota tetap boleh menjalankan perintah melalui console guest. SSH adalah akses administrasi host ke guest; aplikasi A mengirim event ke B melalui HTTPS.

## Acuan materi

Struktur mengikuti *Pertemuan 5 — Version Control & Collaborative Engineering*, terutama slide 6, 15–17, dan 21. Kontrak teknis mengikuti pembahasan interface pada *Pertemuan 4 — System Modeling and Documentation*. Berkas materi kuliah tidak diunggah ulang ke repo. Lembar Artefak Modul 5 menetapkan repository sebagai bukti utama, dengan PDF ringkas untuk lokasi repo, branch/merge, git log, konflik/resolusi, dan kontribusi anggota.
