> Draf adaptasi dari SRS v0.1.0 lama. ID requirement dan nomor bagian dipertahankan untuk traceability. Bukti implementasi lama bukan hasil uji repo ini. [Indeks SRS](index.md).

## 6. Traceability dan verifikasi

| Kelompok ID | Kapabilitas | Lokasi kontrak | Bukti utama |
| --- | --- | --- | --- |
| EP-01–EP-07 | Event Pipeline | [kontrak event](event-pipeline.md) | Fixture schema/digest, uji outbox, receipt, retry, rekonsiliasi dan status sumber. |
| AA-01–AA-05 | Activity Analysis | [analisis aktivitas](activity-analysis.md) | Fixture batas window, state kualitas, fitur, rules, revisi snapshot, dan pemulihan. |
| ML-01–ML-06 | Machine Learning Classifier | [classifier](ml-classifier.md) | Dataset card, manifest split, metrik, model card, parity inferensi, dan batas hasil. |
| UI-01–UI-05 | Operator Console | [console](operator-console.md) | Uji sesi, filter, escaping, hasil/state, freshness, dan walkthrough operator. |
| OP-01–OP-06 | Lab Operations | [operasi](lab-operations.md) | Konfigurasi VM, pemeriksaan jaringan/TLS, profil numerik, backup/restore, manifest run. |

Workbook Modul 02 merangkum sebagian kebutuhan untuk format tugas kuliah. SRS ini adalah sumber rincian teknis; workbook tidak boleh dipakai untuk menyimpulkan detail yang tidak dicantumkannya. [standar implementasi](../../architecture/standards.md) memetakan ID tersebut ke fase dan task. [catatan migrasi](../../history/index.md) menyimpan keputusan, temuan, dan lokasi evidence.

Setiap acceptance run mencatat requirement dan case ID, commit serta kondisi working tree, versi runtime dan konfigurasi tanpa secret, hash input, waktu, langkah, hasil mentah, status lulus/gagal/pengecualian, dan reviewer. Bukti layar hanya dihitung sebagai screenshot bila ditangkap langsung dari framebuffer VMware; output terminal atau hasil script bukan screenshot VMware. Simpan rahasia, token, private key, dan data sensitif di luar dokumen dan evidence yang dibagikan.
