# Tugas_Visual3_2210010610
Tugas/UTS Visual 3 M. Aldi Ripandi 2210010610

---

# Visual3 – CRUD Hukum (PySide6 + MySQL)

Aplikasi desktop sederhana untuk manajemen data hukum: **Pihak, Dasar Hukum, Objek KI, Lisensi, Pelanggaran, Pencatatan Lisensi,** dan **Perkara**. Dibuat dengan **PySide6** (Qt for Python) dan **MySQL** via **PyMySQL**.

## Fitur Utama

* Tabel dengan pencarian, muat ulang, dan seleksi baris.
* Form tambah/ubah/hapus tiap entitas.
* Query aman (parameterized), LIKE pakai `CONCAT('%%', %s, '%%')` biar gak bentrok sama formatter Python.
* Otomatis komit (autocommit) di DB.
* Semua form dibuka dari satu **Main Window**, tidak tumpang-tindih.

## Struktur Proyek (ringkas)

```
.
├── mainwindow.py
├── cruddb.py
├── PihakWidget.py
├── DasarHukumWidget.py
├── ObjekKIWidget.py
├── LisensiWidget.py
├── PelanggaranWidget.py
├── PencatatanLisensiWidget.py
├── PerkaraWidget.py
└── visual3_2210010610.sql
```

## Skema Basis Data

Nama DB: `visual3_2210010610`

* `dasar_hukum(id, sumber, pasal, ringkas)`
* `objek_ki(id, nama, jenis, deskripsi)`
* `lisensi(id, nomor, licensor_id, licensee_id, objek_id, dicatat, nomor_pencatatan, dasar_hukum_id, tanggal_mulai, tanggal_akhir)`
* `pelanggaran(id, perkara_id, pihak_pelanggar_id, jenis, uraian)`
* `pencatatan_lisensi(id, lisensi_id, nomor, tanggal, instansi)`
* `perkara(id, nomor_pn, nomor_ma, tgl_putusan_pn, tgl_putusan_ma, ringkas)`
* `pihak(id, nama, jenis, entitas)`

> Catatan: pada berkas SQL pastikan nama kolom konsisten, mis. `nomor_pencatatan` (pakai underscore).

## Prasyarat

* Python 3.11+
* MySQL Server 8.x (atau kompatibel)
* Paket Python:

  ```bash
  pip install PySide6 PyMySQL
  ```

## Setup Cepat

1. Buat database dan impor skema:

   ```sql
   CREATE DATABASE visual3_2210010610 CHARACTER SET utf8mb4;
   -- impor visual3_2210010610.sql lewat phpMyAdmin / mysql client
   ```
2. Atur koneksi di `cruddb.py`:

   ```python
   DB_CONFIG = {
       "host": "127.0.0.1",
       "user": "root",
       "password": "",          # ganti sesuai lokalmu
       "database": "visual3_2210010610",
       "charset": "utf8mb4",
       "autocommit": True,
       "cursorclass": pymysql.cursors.DictCursor,
   }
   ```
3. Jalankan aplikasi:

   ```bash
   python mainwindow.py
   ```

## Cara Pakai (singkat)

* Buka **Main Window** → klik modul yang diinginkan (Pihak, Dasar Hukum, dst).
* Di atas tabel: kolom cari + tombol **Cari** dan **Muat Ulang**.
* Form di bawah tabel: isi data → **Tambah / Ubah / Hapus**.
* Seleksi baris di tabel untuk mengisi form otomatis.
* Pengurutan default per **id DESC** (id terbesar di atas). Kalau mau id menaik, ubah `order_by="id ASC"` di masing-masing widget.

## Hal Teknis Penting

* Escape tanda persen di query Python:

  ```python
  "LOWER(sumber) LIKE CONCAT('%%', LOWER(%s), '%%')"
  ```
* Field tanggal: konversi ke string `YYYY-MM-DD` sebelum di-insert/update.
* Jangan commit file berat/venv ke Git. Tambahkan `.gitignore`:

  ```
  .qtcreator/
  venv/
  .venv/
  __pycache__/
  *.pyc
  ```
* Jika pakai GitHub Desktop dan kena limit 100 MB, artinya ada binary Qt/venv yang ikut ke-track. Hapus dari history atau inisialisasi ulang repo tanpa folder venv.

## Troubleshooting

* **Unknown column**: cek nama kolom di SQL vs kode widget.
* **Cannot import name Widget**: nama file/kelas harus konsisten (case sensitive).
* **LIKE error “unsupported format character”**: pastikan `%%` seperti contoh di atas.
* **Tidak bisa nambah data**: cek `autocommit=True` di `DB_CONFIG` atau hak akses user MySQL.

## Lisensi

Untuk tugas akademik. Gunakan seperlunya.

## Kredit

Dikembangkan untuk **Tugas Visual 3**. Dbuat Oleh Aldi.

---
