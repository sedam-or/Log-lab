# Inventaris dan keputusan migrasi

Inventaris dibuat 28 Oktober 2026. Path asal di tabel adalah provenance dari workspace praktikum, bukan dependensi instalasi pada laptop anggota. SHA-256 mengidentifikasi berkas sumber yang diperiksa; berkas adaptasi memang dapat memiliki hash berbeda.

Dokumen aktif kebutuhan dan standar dipindahkan atau dipecah. Riwayat implementasi dirangkum dengan konteksnya. PDF/Word/Excel lama tidak langsung diberi label final karena dapat merujuk host, path, status, dan bukti lama. Berkas sumber lama dipertahankan pada workspace asal; migrasi ini tidak menghapusnya.

| Sumber | Keputusan | SHA-256 sumber |
| --- | --- | --- |
| `log-monitoring/docs/OPERATIONS.md` | Disintesis pada history/index.md dan panduan operasi baru; sumber lengkap tetap workspace lama | `8abe9865037ea8d0dca9972771f283f8fd8b789a094e4bef187ef53ae690e697` |
| `log-monitoring/docs/artifact-3/NAMA_TIM_M03_Architecture.docx` | Dicatat; perlu refresh/sanitasi sebelum diterbitkan ulang, tidak disalin sebagai baseline baru | `00c304cf90ab38ea707a23f960e961370085c56e1913b14c01a9992a3ea006ee` |
| `log-monitoring/docs/artifact-3/NAMA_TIM_M03_Architecture.pdf` | Dicatat; perlu refresh/sanitasi sebelum diterbitkan ulang, tidak disalin sebagai baseline baru | `bca8eefd84bc0a9654a28a6dc047a4dcc9742f7deb8a568f9aae1d593015b338` |
| `log-monitoring/docs/artifact-3/README.md` | Referensi/inventaris; periksa relevansi dan tautan sebelum migrasi lanjutan | `abc0a18d4f279a1dad149dc014b1a19a993061c8994343d0549f1df32e9c7dbf` |
| `log-monitoring/docs/artifact-3/logical-architecture.mmd` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `779846862f7314d67334b083b6b08b740223096244e54aa0b36b6c850668d8c8` |
| `log-monitoring/docs/artifact-3/logical-architecture.png` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `1b7fb285a5318e924f30c446b15d41d8e7e88d6fd8a0e99716da18f4edf88a77` |
| `log-monitoring/docs/artifact-3/physical-deployment-architecture.mmd` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `c0d814b7744f7825d12a28ba843279b24b86c81660dc9b12d8137a30385d82e6` |
| `log-monitoring/docs/artifact-3/physical-deployment-architecture.png` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `07ddffec72fd28e88dc0dc5879d0ef25d5bd4ea3fc41f06eb86d0dbde498332e` |
| `log-monitoring/docs/restart/IMPLEMENTATION_AUDIT.md` | Disintesis pada history/index.md dan panduan operasi baru; sumber lengkap tetap workspace lama | `73e9e279d80a8b493c0be1acd7ca2b04747626600853b64fa9cba994e81dee09` |
| `log-monitoring/docs/restart/IMPLEMENTATION_GUIDE.md` | Standar digunakan ulang; task selesai lama diganti task tim baru | `a2ad116afa82cc20fe091083ad8f26b5706e77b4d22887a30ad297747264c6b7` |
| `log-monitoring/docs/restart/LAPORAN_ACCEPTANCE_ARSITEKTUR.mmd` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `2814cfff794596de6f46eff62b2092f66bbaa19e9fd3d941f1c0259f85f414ea` |
| `log-monitoring/docs/restart/LAPORAN_ACCEPTANCE_ARSITEKTUR.svg` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `83115dbff6a8c92bdbc73e6b8ccbb36e535bbb7236fbf5bc10a66d3351951fc7` |
| `log-monitoring/docs/restart/LAPORAN_ACCEPTANCE_LOGLAB_V1.md` | Disintesis pada history/index.md dan panduan operasi baru; sumber lengkap tetap workspace lama | `ef80b59e310f1b96101fac2b00f3608705bcd33f6c58733eeb39541d7b3f54b8` |
| `log-monitoring/docs/restart/LAPORAN_ACCEPTANCE_LOGLAB_V1.pdf` | Dicatat; perlu refresh/sanitasi sebelum diterbitkan ulang, tidak disalin sebagai baseline baru | `d4bc2e5ab20f3612f1982458fd40a9fcbe47e5d6d2c2e2563f2048caaa20dece` |
| `log-monitoring/docs/restart/LogLab_M02_Requirement-Specification.xlsx` | Dicatat; perlu refresh/sanitasi sebelum diterbitkan ulang, tidak disalin sebagai baseline baru | `e31e9e3e0509def39e47c21b278bf28b8f2f2076156a4582946a2376a6f8504b` |
| `log-monitoring/docs/restart/MODUL_REKAYASA_SISTEM.md` | Referensi/inventaris; periksa relevansi dan tautan sebelum migrasi lanjutan | `82d110fef442618fd1c5debe56bfbe7975b0b8e6778774a617569e1d7a49b94e` |
| `log-monitoring/docs/restart/PRD.md` | Diadaptasi ke docs/requirements/PRD.md | `36820fd631db60448499fed3db0a34a35ab71758051526251620cf9c663b1bbe` |
| `log-monitoring/docs/restart/PRD.pdf` | Dicatat; perlu refresh/sanitasi sebelum diterbitkan ulang, tidak disalin sebagai baseline baru | `ad2f40eb645a1f8d64f8b44f088fe4c5497a587e148d7b7a7ecbdf4b03e032e9` |
| `log-monitoring/docs/restart/PRD_ALUR_PRODUK.mmd` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `75926f001480a9bd4d92849c8839ab7eb0399cf78fcef11af8d0612f0d681c32` |
| `log-monitoring/docs/restart/PRD_ALUR_PRODUK.svg` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `f1fa631446e073388a339f4c30346f423696672654566588fab0871566d0e2f1` |
| `log-monitoring/docs/restart/PROJECT_CONTROL.md` | Disintesis pada history/index.md dan panduan operasi baru; sumber lengkap tetap workspace lama | `e0b98c1998c3a74a57777474e9d86c968860750e84aaefdb45192ffc219b50b1` |
| `log-monitoring/docs/restart/README.md` | Referensi/inventaris; periksa relevansi dan tautan sebelum migrasi lanjutan | `90e9af019a8d15acfd0bad670301fffaa8c30175b748f8f85ffba0970bf10104` |
| `log-monitoring/docs/restart/REQUIREMENT_DISPOSITION.csv` | Referensi/inventaris; periksa relevansi dan tautan sebelum migrasi lanjutan | `ad527f925bd96654cbae859ba25782d32a94d163782ef18cf268924d985fb1fd` |
| `log-monitoring/docs/restart/SRS.md` | Dipecah ke docs/requirements/srs/ dengan index | `864762ebc0f974de47fa0cd43e001bd2fe912023561b7b97d866093a05e92a10` |
| `log-monitoring/docs/restart/SRS.pdf` | Dicatat; perlu refresh/sanitasi sebelum diterbitkan ulang, tidak disalin sebagai baseline baru | `434b2e2a00a3cbd182b2443546a9179a1d52b21bc05db4c533a84b2cdcf950cd` |
| `log-monitoring/docs/restart/SRS_ALUR_EVENT.mmd` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `dcb6666afb412a93a1e47891a7a08bf1150aa520060fc06328395a5cd437f9f1` |
| `log-monitoring/docs/restart/SRS_ALUR_EVENT.svg` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `e964fe8ce55651cc88d293fb70ec8b07fe0e4458d1e8392bef8da6500657b0fa` |
| `log-monitoring/docs/restart/SRS_PETA_KEMAMPUAN.mmd` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `0c4d870af3a2311bb0b6d850d8db9ad8473760ef19c041abc18d3ff5815dd52f` |
| `log-monitoring/docs/restart/SRS_PETA_KEMAMPUAN.svg` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `5fc8af87e538f4ac2bc32a9b1763e143e9f3572a6270c2071f99fb8e5f44a100` |
| `log-monitoring/docs/restart/SRS_VM_DAN_KOMUNIKASI.mmd` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `e20a1f77df9a6f51d29a492c81a39c978904ccf7264e5e57d7cd57d2dfd98ddd` |
| `log-monitoring/docs/restart/SRS_VM_DAN_KOMUNIKASI.svg` | Assets produk/SRS/Modul 3 dipindahkan ke docs/architecture/assets/; diagram laporan acceptance dipertahankan pada workspace historis | `e589862b15184404b7874042ea31604b778c4d456ceeed2b71d2397152160ada` |
| `log-monitoring/docs/restart/TRACEABILITY_SUMMARY.json` | Referensi/inventaris; periksa relevansi dan tautan sebelum migrasi lanjutan | `c49b48ed47005289ce27df3b56d2d0bb3b8658acd24bb30bd09ea8388e0fccfd` |
| `log-monitoring/docs/restart/VMWARE_PORTABILITY_RESEARCH.md` | Disintesis pada history/index.md dan panduan operasi baru; sumber lengkap tetap workspace lama | `e270a436e6897d8b82028abbcd12c89231ebc24c126ba128274d871499425f71` |
| `log-monitoring/docs/system-architech.pdf` | Dicatat; perlu refresh/sanitasi sebelum diterbitkan ulang, tidak disalin sebagai baseline baru | `6b7782862c8f81dac05f6b09fbb2d46e7b8c53f9c23aedfa66bbc37465d557d2` |

## Kelompok sumber lain

- `log-monitoring/how-to-use.md`: bahan panduan operasi; command host Linux dan symlink lama harus diadaptasi untuk Windows/guest clone.
- Materi Pertemuan 3/4/5 dan lembar tugas di root workspace: acuan kuliah; tidak diunggah ulang. Materi 5 slide 6 mengendalikan nama direktori repo.
- Artefak Modul 4 buatan tim: bahan desain console; referensi PRD review lama dan status tes perlu diselaraskan sebelum diterbitkan ulang.
- Rencana awal AI-enabled, workbook v0.3 di root, serta `docs/restart/archive/`: historis, bukan scope aktif; tidak diaktifkan kembali.
- `evidence-local/`, kredensial, vault, backup-pc, disk/OVA: privat atau besar; tidak dimigrasikan ke Git.

## Tindak lanjut format pengumpulan

Workbook Modul 2 memerlukan pembaruan referensi ke SRS yang kini terpecah. DOCX/PDF Modul 3 perlu memastikan link dan status rancangan sesuai repo; assets gambar sudah tersedia. Modul 4 perlu sinkronisasi referensi dengan kebutuhan saat ini. Modul 5 dibuat dari riwayat kontribusi Erna dan Arhasya yang benar-benar terjadi. PRD/SRS dan panduan tugas baru akan diekspor sesudah review isi; jangan mengunggah PDF lama yang belum diselaraskan sebagai padanan Markdown baru.
