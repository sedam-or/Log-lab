# Pengujian

Direktori ini akan berisi unit tests, contract tests, dan integration tests. Konvensi awal mengikuti proyek Python sebelumnya: `unittest`, file `test_*.py`, dan method `test_*`. Command final ditetapkan setelah paket dan dependency tersedia; saat ini belum ada tes yang dapat dijalankan di repo ini.

Tes kontrak memakai schema/fixture yang sama untuk producer A dan consumer B. Tes peran di laptop anggota boleh memakai mock yang diberi label. Acceptance dua VM harus memeriksa HTTPS, penyimpanan dan receipt, retry/duplikat, analisis/dashboard, serta startup setelah reboot pada jaringan integrasi sebenarnya.

Bukti menyebut commit, lingkungan, input, command, output, dan status aktual. Tidak ada klaim lulus hanya karena direktori atau dokumen tes sudah dibuat.
