INSERT INTO kategori_intent (id, nama_kategori) VALUES
(1, 'informasi_pendaftaran'),
(2, 'jadwal_pendaftaran'),
(3, 'biaya_kuliah'),
(4, 'persyaratan_pendaftaran'),
(5, 'prosedur_seleksi'),
(6, 'informasi_prodi'),
(7, 'kurikulum_mata_kuliah'),
(8, 'fasilitas_laboratorium'),
(9, 'peluang_kerja'),
(10, 'akreditasi_prestasi'),
(11, 'kegiatan_mahasiswa'),
(12, 'kontak_lokasi'),
(13, 'beasiswa_bantuan_keuangan'),
(14, 'jadwal_kuliah');

INSERT INTO informasi (kategori_id, judul, deskripsi) VALUES
-- 1. Informasi Pendaftaran
(1, 'Informasi Pendaftaran', 'Pendaftaran mahasiswa baru dibuka setiap tahun ajaran baru, biasanya mulai bulan Mei hingga Agustus.'),

-- 2. Jadwal Pendaftaran
(2, 'Jadwal Pendaftaran', 'Gelombang 1: 1 Mei - 30 Juni; Gelombang 2: 1 Juli - 15 Agustus; Pendaftaran online melalui portal resmi.'),

-- 3. Biaya Kuliah
(3, 'Biaya Kuliah', 'Biaya kuliah per semester untuk Program Sarjana adalah Rp 5.000.000, belum termasuk biaya praktikum dan kegiatan mahasiswa.'),

-- 4. Persyaratan Pendaftaran
(4, 'Persyaratan Pendaftaran', 'Fotokopi ijazah SMA/SMK sederajat, pas foto 3x4, fotokopi KTP, serta membayar biaya pendaftaran sebesar Rp 300.000.'),

-- 5. Prosedur Seleksi
(5, 'Prosedur Seleksi', 'Seleksi terdiri dari tes tertulis dan wawancara. Tes tertulis meliputi matematika dasar, logika, dan bahasa Inggris.'),

-- 6. Informasi Prodi
(6, 'Program Studi Teknologi Rekayasa Komputer Jaringan', 'Prodi ini mempelajari perancangan, implementasi, dan pengelolaan jaringan komputer berskala kecil hingga besar.'),

-- 7. Kurikulum Mata Kuliah
(7, 'Kurikulum Mata Kuliah', 'Semester 1: Pemrograman Dasar, Matematika Diskrit; Semester 2: Jaringan Komputer, Sistem Operasi; Semester 3: Keamanan Jaringan, Cloud Computing; dst.'),

-- 8. Fasilitas Laboratorium
(8, 'Fasilitas Laboratorium', 'Tersedia 3 laboratorium jaringan, 1 laboratorium server, dan 1 laboratorium keamanan siber.'),

-- 9. Peluang Kerja
(9, 'Peluang Kerja', 'Lulusan dapat bekerja sebagai network engineer, system administrator, IT consultant, atau teknisi keamanan jaringan.'),

-- 10. Akreditasi dan Prestasi
(10, 'Akreditasi dan Prestasi', 'Program studi memiliki akreditasi B dari BAN-PT dan telah meraih juara 1 lomba keamanan jaringan tingkat nasional tahun 2023.'),

-- 11. Kegiatan Mahasiswa
(11, 'Kegiatan Mahasiswa', 'Mahasiswa dapat mengikuti organisasi seperti Himpunan Mahasiswa TRKJ, komunitas jaringan, dan kompetisi hacking.'),

-- 12. Kontak dan Lokasi
(12, 'Kontak dan Lokasi', 'Alamat: Jl. Pendidikan No. 10, Kota Edukasi. Telepon: (021) 555-1234. Email: info@kampus.ac.id'),

-- 13. Beasiswa dan Bantuan Keuangan
(13, 'Beasiswa dan Bantuan Keuangan', 'Tersedia beasiswa prestasi, beasiswa bidikmisi, dan bantuan UKT bagi mahasiswa yang memenuhi syarat.'),

-- 14. Jadwal Kuliah
(14, 'Jadwal Kuliah', 'Kuliah dilaksanakan Senin-Jumat pukul 08.00-16.00. Praktikum biasanya dilaksanakan sore atau akhir pekan.');
