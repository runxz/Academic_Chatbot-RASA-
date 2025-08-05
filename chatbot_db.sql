-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 05, 2025 at 01:54 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `chatbot_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `files`
--

CREATE TABLE `files` (
  `id` int(11) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `tahun` year(4) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `link` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `files`
--

INSERT INTO `files` (`id`, `nama`, `tahun`, `deskripsi`, `link`) VALUES
(1, 'Materi Jaringan Komputer Dasar', '2022', 'File PDF pembelajaran jaringan dasar', 'https://example.com/jaringan-dasar.pdf'),
(2, 'Skripsi Tentang Keamanan Jaringan', '2023', 'Penelitian tentang firewall dan IDS', 'https://example.com/skripsi-keamanan.pdf');

-- --------------------------------------------------------

--
-- Table structure for table `informasi`
--

CREATE TABLE `informasi` (
  `id` int(11) NOT NULL,
  `kategori_id` int(11) NOT NULL,
  `judul` varchar(255) NOT NULL,
  `deskripsi` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `informasi`
--

INSERT INTO `informasi` (`id`, `kategori_id`, `judul`, `deskripsi`) VALUES
(1, 1, 'Cara Mendaftar', 'Calon mahasiswa dapat mendaftar melalui website resmi dengan mengisi formulir pendaftaran dan mengunggah dokumen yang diperlukan.'),
(2, 1, 'Dokumen yang Diperlukan', 'Dokumen yang dibutuhkan antara lain: KTP, Ijazah terakhir, dan pas foto ukuran 3x4.'),
(3, 2, 'Tanggal Pendaftaran Dibuka', 'Pendaftaran dibuka mulai 1 Januari hingga 30 April setiap tahunnya.'),
(4, 2, 'Jadwal Seleksi', 'Seleksi tahap pertama dilakukan pada bulan Mei, dan tahap kedua pada bulan Juni.'),
(5, 3, 'UKT dan SPP', 'Biaya kuliah terdiri dari Uang Kuliah Tunggal (UKT) dan Sumbangan Pengembangan Pendidikan (SPP) yang dapat dicicil setiap semester.'),
(6, 3, 'Sistem Pembayaran', 'Pembayaran dapat dilakukan melalui transfer bank atau layanan online seperti Virtual Account.'),
(7, 4, 'Syarat Pendaftaran Mahasiswa Baru', 'Syarat pendaftaran meliputi ijazah SMA/sederajat, KTP, dan bukti pembayaran pendaftaran.'),
(8, 4, 'Persyaratan Nilai Rapor', 'Nilai rata-rata minimal 75 untuk jalur undangan dan 65 untuk jalur reguler.'),
(9, 5, 'Tahapan Seleksi', 'Seleksi dilakukan dalam dua tahap: tes tulis dan wawancara.'),
(10, 5, 'Materi Ujian Masuk', 'Materi ujian meliputi Matematika, Bahasa Inggris, dan Tes Potensi Akademik.'),
(11, 6, 'Profil Prodi Komputer Jaringan', 'Program studi ini berfokus pada pengembangan jaringan komputer, keamanan siber, dan administrasi server.'),
(12, 6, 'Keunggulan Prodi', 'Lulusan memiliki peluang karir di bidang jaringan, cloud computing, dan keamanan informasi.'),
(13, 7, 'Struktur Kurikulum', 'Kurikulum terdiri dari mata kuliah dasar, mata kuliah peminatan, dan proyek akhir.'),
(14, 7, 'Mata Kuliah Pilihan', 'Mahasiswa dapat memilih mata kuliah seperti Keamanan Jaringan, Cloud Computing, dan Internet of Things.'),
(15, 8, 'Laboratorium Komputer Jaringan', 'Laboratorium dilengkapi dengan router, switch, dan server untuk praktik mahasiswa.'),
(16, 8, 'Akses ke Perangkat Lunak', 'Mahasiswa mendapatkan akses ke perangkat lunak seperti Cisco Packet Tracer dan Wireshark.'),
(17, 9, 'Peluang Karir Setelah Lulus', 'Lulusan dapat bekerja sebagai Network Engineer, Cyber Security Analyst, atau System Administrator.'),
(18, 9, 'Sertifikasi yang Direkomendasikan', 'Sertifikasi yang disarankan adalah CCNA, CEH, dan CompTIA Security+.'),
(19, 10, 'Akreditasi Program Studi', 'Program studi ini telah terakreditasi A oleh BAN-PT.'),
(20, 10, 'Prestasi Mahasiswa', 'Mahasiswa telah memenangkan berbagai kompetisi jaringan tingkat nasional dan internasional.'),
(21, 11, 'Organisasi Mahasiswa', 'Mahasiswa dapat bergabung dengan Himpunan Mahasiswa Komputer Jaringan (HMKJ).'),
(22, 11, 'Kegiatan Ekstrakurikuler', 'Terdapat berbagai kegiatan seperti workshop, seminar, dan hackathon.'),
(23, 12, 'Alamat Kampus', 'Kampus berlokasi di Jl. Informatika No.10, Jakarta.'),
(24, 12, 'Kontak Resmi', 'Hubungi kami melalui email di info@kampus.ac.id atau telepon (021) 12345678.'),
(25, 13, 'Jenis Beasiswa', 'Beasiswa tersedia untuk mahasiswa berprestasi dan mahasiswa kurang mampu.'),
(26, 13, 'Cara Mengajukan Beasiswa', 'Pengajuan beasiswa dapat dilakukan melalui portal akademik dengan mengunggah dokumen pendukung.'),
(27, 14, 'Jadwal Kuliah Semester Ini', 'Jadwal kuliah semester ini dapat dilihat melalui portal akademik di website kampus.'),
(28, 14, 'Perubahan Jadwal Kuliah', 'Jika ada perubahan jadwal, mahasiswa akan mendapatkan pemberitahuan melalui email dan sistem akademik.'),
(29, 14, 'Waktu Mulai Kuliah', 'Perkuliahan biasanya dimulai pukul 07.30 WIB dan berakhir pukul 17.00 WIB.'),
(30, 14, 'Libur Kuliah', 'Libur semester biasanya berlangsung selama 1 bulan setelah ujian akhir semester.'),
(31, 14, 'Kuliah Online', 'Untuk mahasiswa yang mengambil kelas online, jadwal perkuliahan dapat diakses melalui Learning Management System (LMS).'),
(32, 14, 'Jadwal Kuliah Akhir Pekan', 'Beberapa kelas untuk mahasiswa kelas karyawan tersedia pada hari Sabtu dan Minggu.'),
(33, 14, 'Kalender Akademik', 'Kalender akademik lengkap dengan jadwal kuliah dan ujian dapat diunduh dari website resmi kampus.');

-- --------------------------------------------------------

--
-- Table structure for table `kategori_intent`
--

CREATE TABLE `kategori_intent` (
  `id` int(11) NOT NULL,
  `nama_kategori` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `kategori_intent`
--

INSERT INTO `kategori_intent` (`id`, `nama_kategori`) VALUES
(10, 'akreditasi_prestasi'),
(13, 'beasiswa_dan_bantuan_keuangan'),
(3, 'biaya_kuliah'),
(8, 'fasilitas_laboratorium'),
(1, 'informasi_pendaftaran'),
(6, 'informasi_prodi'),
(14, 'jadwal_kuliah'),
(2, 'jadwal_pendaftaran'),
(11, 'kegiatan_mahasiswa'),
(12, 'kontak_lokasi'),
(7, 'kurikulum_mata_kuliah'),
(9, 'peluang_kerja'),
(4, 'persyaratan_pendaftaran'),
(5, 'prosedur_seleksi');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `files`
--
ALTER TABLE `files`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `informasi`
--
ALTER TABLE `informasi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `kategori_id` (`kategori_id`);

--
-- Indexes for table `kategori_intent`
--
ALTER TABLE `kategori_intent`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nama_kategori` (`nama_kategori`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `files`
--
ALTER TABLE `files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `informasi`
--
ALTER TABLE `informasi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `kategori_intent`
--
ALTER TABLE `kategori_intent`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `informasi`
--
ALTER TABLE `informasi`
  ADD CONSTRAINT `informasi_ibfk_1` FOREIGN KEY (`kategori_id`) REFERENCES `kategori_intent` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
