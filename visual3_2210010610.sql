-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 12 Nov 2025 pada 09.40
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `visual3_2210010610`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `dasar_hukum`
--

CREATE TABLE `dasar_hukum` (
  `id` int(11) NOT NULL,
  `sumber` varchar(200) NOT NULL,
  `pasal` varchar(50) DEFAULT NULL,
  `ringkas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `dasar_hukum`
--

INSERT INTO `dasar_hukum` (`id`, `sumber`, `pasal`, `ringkas`) VALUES
(1, 'KUHPerdata', 'Pasal 1365', 'Perbuatan melawan hukum'),
(2, 'UU 28/2014 Hak Cipta', 'Pasal 83(1)-(3)', 'Pencatatan lisensi agar mengikat pihak ketiga'),
(3, 'PP 36/2018', 'Pasal 15(4)', 'Lisensi yang tidak dicatat tidak berakibat hukum kepada pihak ketiga');

-- --------------------------------------------------------

--
-- Struktur dari tabel `lisensi`
--

CREATE TABLE `lisensi` (
  `id` int(11) NOT NULL,
  `nomor` varchar(100) NOT NULL,
  `tanggal_mulai` date DEFAULT NULL,
  `tanggal_akhir` date DEFAULT NULL,
  `licensor_id` int(11) NOT NULL,
  `licensee_id` int(11) NOT NULL,
  `objek_id` int(11) DEFAULT NULL,
  `dicatat` tinyint(1) DEFAULT 0,
  `nomor_pencatatan` varchar(100) DEFAULT NULL,
  `dasar_hukum_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `lisensi`
--

INSERT INTO `lisensi` (`id`, `nomor`, `tanggal_mulai`, `tanggal_akhir`, `licensor_id`, `licensee_id`, `objek_id`, `dicatat`, `nomor_pencatatan`, `dasar_hukum_id`) VALUES
(1, 'LIS-FIFA-2011-05-05', '2011-05-05', '2014-12-31', 1, 2, 1, 1, 'No.092/dn-hc/TMP-ISM/V/014', 2);

-- --------------------------------------------------------

--
-- Struktur dari tabel `objek_ki`
--

CREATE TABLE `objek_ki` (
  `id` int(11) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `jenis` enum('hak_cipta','hak_terkait','merek','patent','lainnya') NOT NULL,
  `deskripsi` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `objek_ki`
--

INSERT INTO `objek_ki` (`id`, `nama`, `jenis`, `deskripsi`) VALUES
(1, 'Hak Siar Piala Dunia 2014', 'hak_terkait', 'Hak siar/penyiaran tayangan Piala Dunia 2014');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pelanggaran`
--

CREATE TABLE `pelanggaran` (
  `id` int(11) NOT NULL,
  `perkara_id` int(11) NOT NULL,
  `pihak_pelanggar_id` int(11) NOT NULL,
  `jenis` enum('pelanggaran_hak_cipta','pelanggaran_hak_terkait','lainnya') NOT NULL,
  `uraian` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `pelanggaran`
--

INSERT INTO `pelanggaran` (`id`, `perkara_id`, `pihak_pelanggar_id`, `jenis`, `uraian`) VALUES
(1, 1, 3, 'pelanggaran_hak_terkait', 'Penayangan tayangan Piala Dunia (FTA) di showing room hotel tanpa izin/licensing yang sah');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pencatatan_lisensi`
--

CREATE TABLE `pencatatan_lisensi` (
  `id` int(11) NOT NULL,
  `lisensi_id` int(11) NOT NULL,
  `nomor` varchar(100) NOT NULL,
  `tanggal` date NOT NULL,
  `instansi` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `pencatatan_lisensi`
--

INSERT INTO `pencatatan_lisensi` (`id`, `lisensi_id`, `nomor`, `tanggal`, `instansi`) VALUES
(1, 1, 'No.092/dn-hc/TMP-ISM/V/014', '2014-05-23', 'DJKI Kemenkumham');

-- --------------------------------------------------------

--
-- Struktur dari tabel `perkara`
--

CREATE TABLE `perkara` (
  `id` int(11) NOT NULL,
  `nomor_pn` varchar(100) DEFAULT NULL,
  `nomor_ma` varchar(100) DEFAULT NULL,
  `tgl_putusan_pn` date DEFAULT NULL,
  `tgl_putusan_ma` date DEFAULT NULL,
  `ringkas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `perkara`
--

INSERT INTO `perkara` (`id`, `nomor_pn`, `nomor_ma`, `tgl_putusan_pn`, `tgl_putusan_ma`, `ringkas`) VALUES
(1, '4/Pdt.Sus-HKI/2019/PN.Smg', '882.K/Pdt.Sus-HKI/2019', '2019-04-01', '2019-12-01', 'Hotel memutar siaran Piala Dunia di area komersial tanpa izin dari pemegang lisensi; dinyatakan PMH');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pihak`
--

CREATE TABLE `pihak` (
  `id` int(11) NOT NULL,
  `nama` varchar(200) NOT NULL,
  `jenis` enum('licensor','licensee','pihak_ketiga') NOT NULL,
  `entitas` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `pihak`
--

INSERT INTO `pihak` (`id`, `nama`, `jenis`, `entitas`) VALUES
(1, 'FIFA', 'licensor', 'lembaga internasional'),
(2, 'PT Inter Sports Marketing (PT ISM)', 'licensee', 'perusahaan'),
(3, 'Hotel Grand Tjokro Yogyakarta', 'pihak_ketiga', 'perusahaan');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `dasar_hukum`
--
ALTER TABLE `dasar_hukum`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `lisensi`
--
ALTER TABLE `lisensi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_lisensi_lic` (`licensor_id`),
  ADD KEY `fk_lisensi_licee` (`licensee_id`),
  ADD KEY `fk_lisensi_objek` (`objek_id`),
  ADD KEY `fk_lisensi_dh` (`dasar_hukum_id`);

--
-- Indeks untuk tabel `objek_ki`
--
ALTER TABLE `objek_ki`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_objek_ki_nama` (`nama`);

--
-- Indeks untuk tabel `pelanggaran`
--
ALTER TABLE `pelanggaran`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_pel_perkara` (`perkara_id`),
  ADD KEY `fk_pel_pihak` (`pihak_pelanggar_id`);

--
-- Indeks untuk tabel `pencatatan_lisensi`
--
ALTER TABLE `pencatatan_lisensi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_pl_lisensi` (`lisensi_id`);

--
-- Indeks untuk tabel `perkara`
--
ALTER TABLE `perkara`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `pihak`
--
ALTER TABLE `pihak`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `dasar_hukum`
--
ALTER TABLE `dasar_hukum`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `lisensi`
--
ALTER TABLE `lisensi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `objek_ki`
--
ALTER TABLE `objek_ki`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `pelanggaran`
--
ALTER TABLE `pelanggaran`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `pencatatan_lisensi`
--
ALTER TABLE `pencatatan_lisensi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `perkara`
--
ALTER TABLE `perkara`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `pihak`
--
ALTER TABLE `pihak`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `lisensi`
--
ALTER TABLE `lisensi`
  ADD CONSTRAINT `fk_lisensi_dh` FOREIGN KEY (`dasar_hukum_id`) REFERENCES `dasar_hukum` (`id`),
  ADD CONSTRAINT `fk_lisensi_lic` FOREIGN KEY (`licensor_id`) REFERENCES `pihak` (`id`),
  ADD CONSTRAINT `fk_lisensi_licee` FOREIGN KEY (`licensee_id`) REFERENCES `pihak` (`id`),
  ADD CONSTRAINT `fk_lisensi_objek` FOREIGN KEY (`objek_id`) REFERENCES `objek_ki` (`id`);

--
-- Ketidakleluasaan untuk tabel `pelanggaran`
--
ALTER TABLE `pelanggaran`
  ADD CONSTRAINT `fk_pel_perkara` FOREIGN KEY (`perkara_id`) REFERENCES `perkara` (`id`),
  ADD CONSTRAINT `fk_pel_pihak` FOREIGN KEY (`pihak_pelanggar_id`) REFERENCES `pihak` (`id`);

--
-- Ketidakleluasaan untuk tabel `pencatatan_lisensi`
--
ALTER TABLE `pencatatan_lisensi`
  ADD CONSTRAINT `fk_pl_lisensi` FOREIGN KEY (`lisensi_id`) REFERENCES `lisensi` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
