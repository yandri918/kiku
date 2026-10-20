# KikuLog — Blueprint Hackathon Week 3

**Asisten jurnal dan agenda kerja krisan berdasarkan pengalaman bekerja di Jepang**

- Pemilik konsep: Andriyanto.
- Tanggal dokumen: 20 Oktober 2026.
- Tema: **Slow and Steady**.
- Kategori yang ditargetkan: **Best Use of Tinker** dan **Best Use of Render**.
- Status: rancangan produk dan eksperimen; aplikasi, pelatihan, dan hasil evaluasi belum dilaksanakan.
- Bahasa dokumen: Indonesia. Artikel submission final direncanakan dalam bahasa Inggris.

> Ceritakan pekerjaan yang dilakukan. Periksa hasilnya. Biarkan KikuLog merapikan jurnal dan menyiapkan agenda berikutnya.

## 1. Ringkasan keputusan

KikuLog membantu pekerja krisan mengubah catatan informal menjadi jurnal terstruktur per house dan siklus tanam. Aplikasi menggabungkan posisi pekerjaan setiap lahan dengan jadwal potong, packing, dan pemeliharaan net.

Tinker digunakan untuk supervised fine-tuning model open-weight pada tugas pemahaman catatan kerja krisan. Render menjalankan aplikasi web dan backend yang digunakan untuk memasukkan catatan, meninjau hasil, menyimpan jurnal, dan melihat agenda. Perhitungan jadwal dilakukan oleh kode deterministik, bukan ditebak oleh model.

Prinsip kendali: **AI menyiapkan draf; pengguna menyetujui perubahan.** Sistem tidak otomatis menyatakan pekerjaan selesai, mengubah rencana operasional, atau memberikan instruksi budidaya baru.

MVP berfokus pada input teks Indonesia dengan istilah Jepang yang benar-benar digunakan pengguna. Input suara menjadi fitur tambahan setelah alur teks dan evaluasi model stabil.

## 2. Masalah pengguna dan manfaat

### 2.1 Konteks nyata

Andriyanto bekerja dengan tanaman krisan di Jepang. Kegiatan mencakup pemotongan bunga, packing, penanaman mingguan, pembersihan tanaman lama, persiapan lahan, serta pemasangan dan kenaikan net.

Setiap house dapat berada pada tahap berbeda. Ada pekerjaan dengan hari tetap, pekerjaan berdasarkan tanggal tanam, pekerjaan berdasarkan selesainya tahap sebelumnya, serta pekerjaan yang mengikuti kondisi tanaman.

### 2.2 Hipotesis masalah yang akan diuji

- Mencatat ulang pekerjaan setelah aktivitas fisik membutuhkan usaha tambahan.
- Mengingat tahap setiap house dan pekerjaan tertunda dapat membebani pengguna.
- Catatan pendek seperti “B sudah dibuka, pupuk selesai, besok olah lagi” membutuhkan konteks agar tidak salah dipahami.
- Istilah yang sama muncul pada tahap berbeda: pengolahan pertama/kedua, penutupan plastik pertama/setelah tanam, serta pemasangan/kenaikan net.

Cara pencatatan yang digunakan tempat kerja sekarang belum dikonfirmasi. Jangan mengklaim bahwa perusahaan memakai kertas, Excel, atau belum memiliki sistem.

### 2.3 Manfaat yang hendak dibuktikan

Mengurangi waktu dan jumlah koreksi saat membuat jurnal, sekaligus menghasilkan agenda yang dapat ditelusuri ke catatan pengguna. Klaim penghematan hanya dibuat setelah pengukuran.

## 3. Kesesuaian dengan hackathon

Ringkasan aturan dari materi yang diberikan dan halaman resmi [1]: tema menekankan pengurangan pekerjaan berulang; komponen AI terbuka harus penting bagi produk; kualitas tulisan berbobot terbesar. Buat proyek dan repositori baru selama periode challenge, sertakan demo dan penjelasan manfaat pendekatan terbuka. Artikel berbahasa Inggris diperlukan untuk kelayakan hadiah. Kategori partner harus disebutkan dan benar-benar digunakan. Satu submission hanya dapat menang sekali.

Tenggat yang tercantum: **25 Oktober 2026, 23.59 PDT**, setara **26 Oktober 2026, 15.59 JST/WIT**. Target internal: kirim pada 25 Oktober waktu Jepang. Periksa kembali template dan aturan resmi sebelum publikasi.

### Pemetaan produk ke tema

| Unsur | Bukti yang akan disiapkan |
|---|---|
| Slow and Steady | Catatan singkat menghasilkan jurnal dan agenda tanpa pengetikan ulang setiap field |
| AI terbuka sebagai inti | Model open-weight hasil fine-tuning menafsirkan catatan kerja |
| Best Use of Tinker | Run pelatihan, checkpoint, dataset terdokumentasi, dan evaluasi terhadap baseline |
| Best Use of Render | Aplikasi/API benar-benar berjalan di Render dan dapat diperagakan |
| Kreativitas | Istilah kerja krisan, konteks per house, dan tahap berulang yang harus dibedakan |
| Eksekusi teknis | Validasi output, persetujuan pengguna, penyimpanan, jadwal, dan penanganan gagal |
| Kualitas tulisan | Masalah personal, keputusan desain, hasil pengukuran, serta keterbatasan |

Nama “KikuLog” merupakan nama kerja, belum diperiksa ketersediaan merek atau domainnya.

## 4. Pengetahuan operasional yang sudah dikonfirmasi

Semua pola di bagian ini berasal dari penjelasan pengguna. Ini adalah workflow tempat kerjanya, **bukan pedoman agronomi universal**.

### 4.1 Ritme kegiatan

| Kegiatan | Pola yang dikonfirmasi | Aturan rancangan |
|---|---|---|
| Potong bunga | Setiap dua hari | Memerlukan tanggal acuan dan cakupan house |
| Packing | Selasa, Kamis, Minggu | Jadwal mingguan tetap, terpisah dari jadwal potong |
| Penanaman | Setiap minggu | Hari ditetapkan pengguna; jangan mengarang hari tetap |
| Bongkar house | Mencabut/membersihkan tanaman krisan lama di dalam house | Tidak berarti membongkar bangunan |
| Membuka plastik setelah tanam | 14 hari setelah tanam | Mengacu ke tanggal tanam aktual |
| Memasang net | 14 hari setelah tanam | Status terpisah dari pembukaan plastik |
| Menaikkan net | Berkala sesuai tinggi tanaman | Tidak menetapkan interval atau ambang tinggi tanpa konfigurasi |

### 4.2 Urutan persiapan dan pemeliharaan awal

| No. | Kode kegiatan | Pekerjaan | Ketergantungan/acuan |
|---|---|---|---|
| 1 | clear_old_plants | Membersihkan tanaman lama | Awal persiapan siklus baru |
| 2 | remove_net | Melepas net | Setelah pembersihan |
| 3 | remove_stakes | Melepas pasak | Setelah pelepasan net |
| 4 | tillage_1 | Pengolahan pertama | Setelah pelepasan pasak |
| 5 | cover_plastic_1 | Penutupan plastik pertama | Setelah pengolahan pertama |
| 6 | uncover_plastic_1 | Membuka plastik pertama | 3–4 hari setelah penutupan pertama |
| 7 | basal_fertilization | Pemupukan awal | Setelah pembukaan pertama |
| 8 | tillage_2 | Pengolahan kedua | Setelah pemupukan awal |
| 9 | make_beds | Pembuatan bedengan | Setelah pengolahan kedua |
| 10 | planting | Penanaman krisan | Setelah bedengan siap |
| 11 | cover_plastic_2 | Penutupan plastik setelah tanam | Setelah penanaman |
| 12 | uncover_plastic_2 | Pembukaan plastik setelah tanam | 14 HST |
| 13 | install_net | Pemasangan net | 14 HST; catatan terpisah |
| 14+ | inspect_net / raise_net | Pemeriksaan/kenaikan net | Sesuai kondisi dan tinggi tanaman |

Belum ditentukan: kapan pasak dipasang kembali, lama tanaman hingga siap potong, rincian varietas, target mutu, serta tahapan lain yang tidak disebutkan. Jangan menambahkan jadwal otomatis untuk hal-hal tersebut.

Jika pengguna mencatat tahap lanjut tanpa riwayat tahap sebelumnya, aplikasi meminta pemeriksaan atau mencatat kekosongan riwayat. Jangan otomatis mengisi tahap sebelumnya sebagai selesai; pekerjaan mungkin dilakukan orang lain atau belum dicatat.

## 5. Aturan jadwal dan status

### 5.1 Tanggal dan zona waktu

- Gunakan zona waktu lokasi kerja **Asia/Tokyo** untuk tanggal operasional.
- Simpan timestamp teknis dalam UTC dan tanggal kerja lokal secara eksplisit.
- HST dihitung sebagai selisih tanggal lokal; tanggal tanam adalah hari 0.
- Contoh sintetis: tanam 1 November → 14 HST pada 15 November.
- Pembukaan plastik pertama memiliki rentang tanggal: tanggal penutupan +3 sampai +4 hari.
- Tanggal relatif seperti “besok” ditafsirkan terhadap waktu catatan atau tanggal kerja yang dipilih pengguna.
- Catatan terlambat harus memiliki `occurred_on` yang berbeda dari waktu input bila diperlukan.

### 5.2 Pengulangan

- Jadwal potong menggunakan tanggal acuan yang dikonfirmasi. Jika ada penundaan, tanyakan apakah hanya kejadian itu yang berubah atau seluruh seri bergeser.
- Packing selalu seri terpisah: Selasa, Kamis, Minggu. Jangan menggesernya otomatis mengikuti potong.
- Penanaman mingguan memerlukan hari/tanggal aktual per lokasi.
- Kenaikan net adalah event berulang. Kenaikan baru tidak menimpa riwayat kenaikan sebelumnya.
- Pemeriksaan net dapat diberi pengingat dengan interval pilihan pengguna; tidak ada interval agronomis bawaan.

### 5.3 Status

Pisahkan status rencana (`planned`, `in_progress`, `done`, `postponed`, `cancelled`) dari pekerjaan yang belum pernah dilaporkan. Tidak ada catatan bukan berarti pekerjaan pasti belum dilakukan.

- “Sudah” → draf selesai.
- “Tinggal sedikit” → sedang berjalan.
- “Besok” → rencana, bukan selesai.
- “Belum” → belum selesai sesuai pernyataan pengguna.
- “Ditunda” → ditunda; tanggal baru boleh kosong.
- Lewat tanggal → tugas lewat jadwal, bukan otomatis selesai.

Perubahan tanggal tanam atau penutupan harus menampilkan pratinjau dampak pada agenda sebelum disetujui. Catatan historis tidak dihapus.

## 6. Batas produk dan tampilan

### Wajib untuk MVP

1. Daftar house dan siklus tanam aktif.
2. Input teks dan pemilihan tanggal kerja.
3. Ekstraksi beberapa kegiatan dari satu catatan.
4. Bukti kutipan sumber untuk setiap hasil ekstraksi.
5. Klarifikasi bila lokasi, tahap, jumlah, atau tanggal ambigu.
6. Koreksi dan persetujuan sebelum penyimpanan.
7. Jurnal per house dan agenda gabungan.
8. Ekspor CSV.
9. Halaman perbandingan baseline dan model fine-tuning.
10. Demo dengan data sintetis berlabel.

### Tambahan jika waktu cukup

Input suara, filter varietas, tampilan kalender mingguan, dan unduhan ringkasan. Suara dievaluasi terpisah agar kesalahan transkripsi tidak disalahartikan sebagai kesalahan model ekstraksi.

### Di luar MVP

Diagnosis penyakit, rekomendasi dosis pupuk, kontrol alat, prediksi hasil panen, integrasi WhatsApp, multi-agent, IoT, serta optimasi tenaga kerja otomatis. Tidak ada klaim bahwa aplikasi menggantikan prosedur perusahaan.

### Tiga area antarmuka

| Area | Isi |
|---|---|
| Hari ini | Pekerjaan terjadwal, tertunda, jendela pembukaan plastik, dan pekerjaan bertepatan |
| Catat dan jurnal | Input, hasil AI, klarifikasi, persetujuan, riwayat per house |
| Evaluasi | Perbandingan model, skor yang benar-benar terukur, contoh gagal, latensi |

Gunakan label produk sederhana. Istilah checkpoint, JSON, dan training loss cukup di area evaluasi/teknis, tidak perlu tampil pada alur pencatatan pekerja.

## 7. Kontrak keluaran model

Model menerima teks, tanggal referensi, daftar alias house, dan ringkasan siklus relevan. Model menghasilkan draf event, bukan menjalankan perubahan database.

Contoh sintetis:

> “House tiga sudah bongkar, net sudah dicopot, pasak belum.”

```json
{
  "events": [
    {
      "house_id": "house_3",
      "cycle_id": null,
      "activity": "clear_old_plants",
      "status": "done",
      "occurred_on": null,
      "evidence": "House tiga sudah bongkar"
    },
    {
      "house_id": "house_3",
      "cycle_id": null,
      "activity": "remove_net",
      "status": "done",
      "occurred_on": null,
      "evidence": "net sudah dicopot"
    },
    {
      "house_id": "house_3",
      "cycle_id": null,
      "activity": "remove_stakes",
      "status": "not_done",
      "occurred_on": null,
      "evidence": "pasak belum"
    }
  ],
  "clarifications": [
    "Konfirmasi tanggal pekerjaan dan siklus terkait jika belum dipilih pada formulir."
  ]
}
```

`not_done` adalah hasil pengamatan dari catatan; aplikasi memetakannya ke tugas yang masih terbuka, bukan otomatis membuat tanggal rencana. `cycle_id` diselesaikan dari konteks valid atau konfirmasi pengguna. Tanggal pada formulir dapat menjadi default yang terlihat jelas dan dapat dikoreksi.

Field tambahan opsional: jumlah, satuan, varietas, warna, tanggal rencana, serta kutipan koreksi. Informasi yang tidak ada bernilai null; jangan menyamakan warna dengan varietas atau mengonversi ikat/kotak ke batang tanpa konfigurasi.

## 8. Rencana fine-tuning Tinker

### 8.1 Tujuan

Meningkatkan kemampuan model open-weight dalam mengekstrak kegiatan krisan, lokasi, status, waktu, dan kebutuhan klarifikasi dari bahasa kerja informal.

Tinker menyediakan LoRA untuk pelatihan model dan kemampuan sampling; bobot hasil pelatihan dapat diekspor menurut dokumentasinya [2][3]. Tinker adalah layanan pelatihan, bukan nama model dasar. Model dipilih dari yang benar-benar tersedia di akun saat implementasi.

### 8.2 Pemilihan model

- Mulai dari model kecil yang mendukung bahasa Indonesia dan keluaran terstruktur dengan cukup baik.
- Periksa dukungan Tinker, lisensi model, biaya, serta akses sampling checkpoint.
- Jalankan baseline pada 30–50 contoh pengembangan sebelum memilih konfigurasi.
- Jangan menjanjikan Gemma atau model tertentu sebelum dukungannya dikonfirmasi.
- Gunakan supervised fine-tuning; reinforcement learning bukan kebutuhan MVP.

### 8.3 Dataset awal yang diusulkan

| Split | Jumlah awal | Kegunaan |
|---|---:|---|
| Train | 500 | Melatih adapter |
| Validation | 100 | Memilih konfigurasi/checkpoint |
| Test terkunci | 100 | Evaluasi akhir satu kali setelah pemilihan |

Angka ini target awal, bukan jaminan cukup. Mulai dengan pilot berlabel yang lebih kecil untuk memeriksa schema, lalu perluas bila diperlukan.

Komposisi mencakup seluruh siklus, beberapa house dalam satu catatan, pekerjaan belum selesai, koreksi, pengulangan net, tanggal relatif, istilah Indonesia/Jepang yang dikonfirmasi, serta kasus di luar cakupan.

Contoh penting:

| Input | Perilaku yang diharapkan |
|---|---|
| “House B sudah dibuka” tanpa konteks | Klarifikasi jenis pembukaan plastik |
| “B sudah dibuka” dengan riwayat cover_plastic_1 | Usulkan uncover_plastic_1 dengan bukti konteks |
| “Net A naik, B belum” | Dua lokasi dan dua status berbeda |
| “Bukan house dua, house tiga” | Koreksi lokasi, bukan dua event selesai |
| “Packing tinggal sedikit” | in_progress |
| “Tanam Jumat bukan Kamis” | Koreksi tanggal rencana |
| “Bongkar house” | Pembersihan tanaman lama |
| “Besok olah lagi” tanpa konteks | Klarifikasi tahap; jangan otomatis memilih pengolahan kedua |

### 8.4 Pelabelan dan pencegahan kebocoran

- Pengguna memeriksa istilah dan kebenaran alur kerja.
- Tandai asal contoh: sintetis, catatan alami, atau adaptasi anonim.
- Pisahkan skenario/keluarga parafrasa sebelum generasi variasi. Jangan menaruh template identik dengan angka berbeda pada train dan test.
- Hapus duplikat dan periksa kemiripan antar-split.
- Sisihkan catatan alami yang ditulis pengguna tanpa melihat contoh pelatihan.
- Jangan melatih ulang menggunakan jawaban test. Jika test sudah digunakan untuk tuning, jadikan development set dan buat test baru.
- Koreksi pengguna di aplikasi tidak otomatis menjadi data pelatihan; perlu seleksi dan versi dataset baru.

### 8.5 Eksperimen

1. Tetapkan schema, metrik, split, dan aturan penilaian.
2. Rekam baseline dengan prompt yang layak dan konteks yang memadai.
3. Jalankan pilot SFT melalui Tinker.
4. Periksa validation; lakukan sedikit eksperimen dengan batas biaya.
5. Pilih checkpoint menggunakan validation saja.
6. Jalankan baseline dan checkpoint terpilih pada test yang sama.
7. Simpan prediksi mentah, skor, biaya, dan konfigurasi.

Rekam base model ID, versi SDK, hash dataset, seed bila tersedia, parameter LoRA, learning rate, batch, steps/epochs, checkpoint, dan waktu run. Nilainya belum ditentukan; jangan mencantumkan angka seolah sudah dijalankan.

## 9. Bukti peningkatan dan evaluasi

Prioritas kategori Tinker adalah peningkatan **kinerja tugas**. Penurunan latensi atau biaya merupakan hasil tambahan jika terukur, bukan janji.

| Metrik | Definisi |
|---|---|
| Event exact match — utama | Proporsi catatan yang seluruh event pentingnya tepat: kegiatan, lokasi, status, tanggal eksplisit, tanpa event tambahan |
| Field precision/recall/F1 | Ketepatan field/event dengan pencocokan yang terdokumentasi |
| Schema validity | Persentase output valid terhadap schema yang sama |
| Klarifikasi precision/recall | Kemampuan meminta klarifikasi saat perlu tanpa terlalu sering bertanya |
| Unsupported claim rate | Proporsi output yang menambahkan informasi tanpa dasar |
| Koreksi pengguna | Jumlah field yang diperbaiki sebelum persetujuan |
| Latensi p50/p95 | Waktu inferensi dengan konfigurasi dan kondisi uji dicatat |
| Waktu pencatatan | Durasi input hingga catatan benar tersimpan |
| Biaya | Pelatihan dan inferensi dilaporkan terpisah |

Perbandingan utama menggunakan base model yang sama, konteks sama, pengaturan decoding sebanding, serta validasi dan retry yang sama. Jika prompt fine-tuned lebih pendek, laporkan sebagai eksperimen terpisah agar dampaknya tidak tercampur.

Untuk sampel terbatas, laporkan pembilang/penyebut dan bila memungkinkan interval ketidakpastian dengan bootstrap berpasangan. Jangan menyebut satu perubahan skor sebagai peningkatan pasti tanpa memeriksa pola kesalahan.

### Template hasil — belum diisi

| Ukuran | Baseline | Fine-tuned | Perubahan |
|---|---|---|---|
| Event exact match | Belum diuji | Belum diuji | — |
| Schema validity | Belum diuji | Belum diuji | — |
| Klarifikasi F1 | Belum diuji | Belum diuji | — |
| Unsupported claim rate | Belum diuji | Belum diuji | — |
| Latensi p50/p95 | Belum diuji | Belum diuji | — |
| Koreksi per catatan | Belum diuji | Belum diuji | — |

Uji manfaat dengan tugas manual dan aplikasi yang setara, urutan bergantian, serta kriteria catatan benar yang sama. Jika hanya diuji oleh satu orang, nyatakan sebagai studi awal satu pengguna. Jangan mengklaim dampak pada produktivitas perusahaan.

Jika fine-tuning tidak mengungguli baseline, dokumentasikan hasilnya dan revisi menggunakan validation. Jangan membuat angka keberhasilan atau menyembunyikan baseline kuat.

## 10. Arsitektur dan deployment Render

### Rancangan minimal

| Komponen | Pilihan rancangan |
|---|---|
| Web UI | Antarmuka responsif sederhana; dapat disajikan oleh backend untuk mengurangi jumlah layanan |
| Backend | Python/FastAPI dengan validasi schema |
| Hosting | Render Web Service |
| Database | PostgreSQL persisten; Render Postgres sebagai pilihan |
| Model | Sampling checkpoint Tinker setelah akses dan latensi diverifikasi |
| Training controller | Script Python lokal/Colab yang mengirim operasi pelatihan ke Tinker |
| Dataset/evaluasi | File JSONL dan script reproduksi dalam repo baru |

Render mendokumentasikan web service dan background worker sebagai jenis layanan terpisah [4][5]. MVP tidak memerlukan worker hanya untuk menghitung agenda; agenda dapat dihitung saat dibuka. Tambahkan worker bila ada pekerjaan panjang yang benar-benar memerlukannya.

### Alur permintaan

1. Pengguna mengirim catatan dan konteks lokasi.
2. Backend mengambil konteks siklus yang relevan.
3. Backend memanggil model dan memvalidasi keluaran.
4. UI menampilkan draf, bukti sumber, dan pertanyaan klarifikasi.
5. Pengguna menyetujui atau mengoreksi.
6. Backend menyimpan event dan menghitung ulang agenda terkait.

### Kegagalan dan integritas

- Timeout/inferensi gagal: tampilkan pesan dan formulir manual; jangan menyajikan hasil palsu.
- Output invalid: retry terbatas, kemudian minta input manual; catat retry dalam pengukuran.
- Submit ulang: gunakan idempotency key agar event tidak ganda.
- Koreksi: simpan audit trail dan relasi ke catatan asal.
- Database persisten diperlukan; jangan mengandalkan file lokal sementara layanan.
- API key hanya di environment server, tidak pada frontend atau repo.
- Demo publik memakai data sintetis terisolasi, pembatasan permintaan, dan akses tulis terkendali.
- Catatan nyata hanya berada dalam akses pengguna yang berwenang.
- Health endpoint dan log aplikasi disiapkan tanpa merekam rahasia.

Tidak menjanjikan inferensi GPU lokal di Render. Jika sampling Tinker tidak sesuai kebutuhan aplikasi, evaluasi penyedia inferensi kompatibel untuk bobot hasil pelatihan. Nyatakan lokasi pemrosesan dan biaya aktual. Rancangan cloud ini tidak boleh diklaim offline.

## 11. Model data minimum

| Entitas | Field utama |
|---|---|
| House | id, nama tampilan, alias, aktif |
| CropCycle | id, house_id, tanggal tanam, status, varietas opsional |
| RawNote | id, teks, waktu input, tanggal kerja, penulis, asal demo/nyata |
| DraftExtraction | note_id, model_version, hasil, klarifikasi, status review |
| WorkEvent | cycle_id, house_id, activity, status, occurred_on, planned_on, jumlah/satuan opsional, evidence, approved_by |
| ScheduleRule | jenis, hari mingguan, interval, tanggal acuan, scope |
| Task | sumber event/rule, jendela tanggal, status, relasi house/cycle |
| AuditLog | perubahan sebelum/sesudah, waktu, pelaku |
| EvaluationRun | model/checkpoint, dataset hash, konfigurasi, hasil, biaya |

Packing dapat menjadi kegiatan bersama tanpa house spesifik. Jangan memaksa semua kegiatan terkait satu house. Event harus terikat ke siklus yang tepat agar tanggal 14 HST tidak memakai penanaman lama.

## 12. Skenario penerimaan

MVP dianggap berfungsi jika:

- Catatan multi-kegiatan dapat ditinjau dan disimpan.
- “Bongkar house” dipetakan ke pembersihan tanaman lama.
- Dua jenis pengolahan dan dua jenis penutupan/pembukaan plastik dibedakan.
- Jadwal pembukaan pertama memakai rentang +3 sampai +4 hari.
- Jadwal 14 HST berasal dari tanggal tanam aktual.
- Pembukaan plastik dan pemasangan net memiliki status independen.
- Kenaikan net tersimpan berulang dan tidak mengarang tinggi tanaman.
- Jadwal packing tidak bergeser ketika jadwal potong berubah.
- Catatan ambigu meminta klarifikasi.
- Input ulang tidak menggandakan event.
- Gangguan model tetap memungkinkan pencatatan manual.
- Halaman evaluasi menampilkan hasil nyata dan contoh kesalahan.

Pengujian diprioritaskan pada risiko tersebut; tidak perlu memperluas suite di luar kebutuhan MVP.

## 13. Demo 90–120 detik

1. Tampilkan tiga house sintetis pada tahap berbeda.
2. Masukkan catatan: “House tiga sudah bongkar, net sudah dicopot, pasak belum.”
3. Perlihatkan draf, kutipan sumber, dan persetujuan pengguna.
4. Tampilkan house lain yang mencapai 14 HST dan tugas buka plastik/pasang net yang terpisah.
5. Masukkan “Net house dua sudah dinaikkan, house satu besok cek.”
6. Tampilkan agenda packing dan potong bersama pekerjaan lahan.
7. Perlihatkan satu contoh test yang sama untuk baseline dan fine-tuned, lalu tabel hasil keseluruhan.
8. Akhiri dengan lokasi deployment Render dan bukti run Tinker.

Contoh demo boleh dipilih agar mudah dipahami, tetapi beri tahu bahwa skor keseluruhan berasal dari test lengkap. Jangan memilih contoh sukses sebagai pengganti evaluasi.

## 14. Artikel submission

Judul kerja:

**KikuLog: Less Typing After a Day Among Chrysanthemums — Fine-Tuned with Tinker, Deployed on Render**

Gunakan template resmi sebagai struktur utama, kemudian isi:

1. Pengalaman pribadi bekerja dengan krisan di Jepang.
2. Pekerjaan pencatatan yang ingin dipermudah.
3. Demo alur sebelum/sesudah.
4. Mengapa konteks house dan tahap tanaman penting.
5. Dataset, model dasar, fine-tuning, dan evaluasi yang adil.
6. Hasil terukur, kegagalan, serta keterbatasan.
7. Peran Tinker dan Render yang dapat diverifikasi.
8. Mengapa model terbuka bermanfaat: penyesuaian istilah, evaluasi yang dapat direproduksi, dan opsi portabilitas bobot sesuai lisensi.
9. Cara menjalankan proyek dan mencoba demo.
10. Kategori yang diikuti, kredit sumber, dan penggunaan bantuan AI.

Hindari klaim “gratis”, “sepenuhnya privat”, “offline”, “siap produksi”, atau penghematan persentase tanpa bukti. Tinker/Render sebagai layanan cloud tidak otomatis menjadikan seluruh sistem open-source. Jelaskan lisensi kode aplikasi dan model secara terpisah.

## 15. Struktur repo yang disarankan

```text
kikulog/
  README.md
  LICENSE
  .env.example
  render.yaml
  app/
    main.py
    schemas.py
    extraction.py
    scheduling.py
    persistence.py
    ui/
  training/
    prepare_data.py
    train_sft.py
    configs/
  evaluation/
    run_eval.py
    score.py
    reports/
  data/
    dataset_card.md
    synthetic_examples.jsonl
  tests/
  docs/
    model_card.md
    architecture.md
    demo_script.md
    submission_draft.md
```

Data test yang belum dibuka dapat disimpan terpisah selama pengembangan. Publikasikan hanya data yang boleh dibagikan. Model card mencantumkan lisensi dasar, adaptasi yang dibuat, bahasa, metrik, keterbatasan, serta cara mengakses bobot bila diizinkan.

## 16. Rencana pengerjaan 20–25 Oktober

| Tanggal | Fokus | Hasil wajib |
|---|---|---|
| 20 Oktober | Finalisasi schema, akses Tinker/Render, repo baru, contoh pilot | Definisi tugas dan baseline awal |
| 21 Oktober | Dataset dan aplikasi catatan dasar | Split dataset serta input–review–save |
| 22 Oktober | Pilot SFT dan mesin jadwal | Checkpoint awal dan aturan waktu yang diuji |
| 23 Oktober | Evaluasi validation, pilihan checkpoint, deployment | Aplikasi Render dan konfigurasi final |
| 24 Oktober | Test terkunci, uji pengguna, rekaman demo | Bukti hasil, biaya, dan keterbatasan |
| 25 Oktober | Artikel Inggris, README, pemeriksaan, submission | Submission lengkap sebelum tenggat |

Jika waktu sempit, potong fitur suara dan tampilan tambahan. Pertahankan satu alur yang berfungsi, pelatihan nyata, evaluasi adil, dan artikel yang jelas.

## 17. Biaya, akses, dan hal yang masih terbuka

Belum ada persetujuan pembelian atau deployment berbayar dalam blueprint ini. Sebelum menjalankan pelatihan/hosting berbayar, tentukan batas total eksperimen, kredit tersedia, dan biaya layanan berdasarkan harga aktual [6]. Jangan menganggap kredit promosi sudah aktif.

Hal yang perlu dikonfirmasi saat implementasi:

- Model dan sampling checkpoint yang tersedia dalam akun Tinker.
- Batas biaya dan pilihan paket Render/database.
- Nama/alias house, apakah satu house memiliki beberapa blok/siklus.
- Cakupan pemotongan setiap dua hari dan tanggal acuannya.
- Hari penanaman mingguan atau penetapan manual per minggu.
- Istilah Jepang yang benar-benar dipakai.
- Apakah tanam satu house dapat berlangsung lebih dari satu hari; bila ya, gunakan unit blok/batch untuk acuan HST.
- Interval pemeriksaan net bila pengingat pemeriksaan dibutuhkan.
- Arti perubahan seri jadwal saat ada penundaan.
- Izin memakai catatan/foto/data tempat kerja; default demo adalah data sintetis anonim.

Pertanyaan tersebut tidak menghalangi pembangunan prototipe dengan konfigurasi manual dan contoh sintetis.

## 18. Checklist submission

- [ ] Proyek dan repositori baru dalam jendela challenge.
- [ ] Aplikasi berfungsi pada Render; tautan dapat diakses sesuai mode demo.
- [ ] Fine-tuning Tinker benar-benar dijalankan dan checkpoint dicatat.
- [ ] Baseline yang layak dan test terpisah tersedia.
- [ ] Hasil, biaya, dan keterbatasan dilaporkan jujur.
- [ ] Semua contoh sintetis diberi label.
- [ ] Data/rahasia perusahaan dan API key tidak ikut dipublikasikan.
- [ ] README menyediakan setup dan reproduksi evaluasi.
- [ ] Lisensi kode/model dan atribusi penggunaan kode terdahulu jelas.
- [ ] Artikel Inggris mengikuti template resmi dan tag yang diminta.
- [ ] Best Use of Tinker dan Best Use of Render disebutkan.
- [ ] Rekaman demo dan screenshot menunjukkan fungsi nyata.
- [ ] Perubahan commit setelah deadline ditandai sesuai aturan resmi.
- [ ] Persyaratan peserta dan aturan resmi diperiksa sebelum submission.

## 19. Sumber dan dasar dokumen

Informasi workflow krisan berasal dari percakapan Andriyanto pada 20 Oktober 2026. Contoh house, tanggal, dan catatan dalam dokumen merupakan ilustrasi sintetis.

1. [DEV — Hacktoberfest Open-Source AI Challenge Week 3](https://dev.to/challenges/hacktoberfest-week3-2026-10-19). Materi pengguna dan halaman resmi yang diperiksa dalam pembahasan.
2. [Tinker Documentation](https://tinker-docs.thinkingmachines.ai/). Kemampuan pelatihan LoRA, model open-weight, dan ekspor bobot.
3. [Tinker — Get Started](https://tinker-docs.thinkingmachines.ai/tinker/quickstart/). Alur supervised fine-tuning dan sampling.
4. [Render — Service Types](https://render.com/docs/service-types). Pilihan layanan deployment.
5. [Render — Background Workers](https://render.com/docs/background-workers). Pekerjaan latar belakang.
6. [Tinker — Models and Pricing](https://tinker-docs.thinkingmachines.ai/tinker/models/). Periksa model, lisensi terkait, dan biaya saat implementasi.

Dokumentasi layanan dapat berubah. Blueprint ini tidak menetapkan harga, model tertentu, atau hasil eksperimen yang belum diverifikasi.
