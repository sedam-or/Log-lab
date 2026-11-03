# Aturan singkat

Ringkasan satu halaman. Detail ada di dokumen yang ditautkan; bila berbeda, urutan acuan: `config/contract.json` > SRS > `docs/tugas` > `CONTRIBUTING.md`.

1. **Branch**: hanya `dev` (default), `staging`, `production`. Promosi lewat PR + merge commit + CI hijau + satu reviewer lain. [CONTRIBUTING](../CONTRIBUTING.md#branch-dan-promosi).
2. **Python 3.13 tepat** dan `requirements.lock`. `make dev-setup` memeriksanya.
3. **Kontrak** `config/contract.json` mengikat IP, port, nama env, endpoint, izin file. Ubah hanya lewat PR bersama dan naikkan versi (MAJOR ubah nama/nilai/endpoint, MINOR tambah, PATCH dokumentasi), lalu `python3 scripts/check_contract.py --sync`.
4. **Secret tidak masuk Git.** Env nyata di `/etc/loglab/*.env`, bundle lab di luar clone.
5. **Bukti jujur**: tulis perintah yang benar-benar dijalankan dan hasil aktualnya; bedakan simulasi, fixture dan uji dua VM.
6. **Pemasangan VM**: lihat [OPERASI-VM.md](OPERASI-VM.md) setelah tersedia.
