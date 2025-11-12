# mainwindow.py
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt

# Import form-form kamu
from PihakWidget import PihakWidget
from DasarHukumWidget import DasarHukumWidget
from ObjekKIWidget import ObjekKIWidget
from LisensiWidget import LisensiWidget
from PelanggaranWidget import PelanggaranWidget
from PencatatanLisensiWidget import PencatatanLisensiWidget
from PerkaraWidget import PerkaraWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual3 - CRUD Hukum")
        self.resize(1100, 680)

        # ====== ROOT LAYOUT (sidebar kiri + area konten kanan) ======
        root = QWidget(self)
        self.setCentralWidget(root)
        hl = QHBoxLayout(root)
        hl.setContentsMargins(10, 10, 10, 10)
        hl.setSpacing(10)

        # ----- Sidebar tombol -----
        sidebar = QVBoxLayout()
        sidebar.setSpacing(8)

        # tombol helper
        def mkbtn(text):
            b = QPushButton(text)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setCursor(Qt.PointingHandCursor)
            return b

        self.btn_pihak       = mkbtn("Pihak")
        self.btn_dasar       = mkbtn("Dasar Hukum")
        self.btn_objek       = mkbtn("Objek KI")
        self.btn_lisensi     = mkbtn("Lisensi")
        self.btn_pelanggaran = mkbtn("Pelanggaran")
        self.btn_catat       = mkbtn("Pencatatan Lisensi")
        self.btn_perkara     = mkbtn("Perkara")

        for b in (
            self.btn_pihak, self.btn_dasar, self.btn_objek, self.btn_lisensi,
            self.btn_pelanggaran, self.btn_catat, self.btn_perkara
        ):
            sidebar.addWidget(b)

        sidebar.addStretch(1)

        # ----- Area konten dengan QStackedWidget -----
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)

        # buat instance form sekali saja
        self.pages = {
            "pihak":       PihakWidget(self),
            "dasar":       DasarHukumWidget(self),
            "objek":       ObjekKIWidget(self),
            "lisensi":     LisensiWidget(self),
            "pelanggaran": PelanggaranWidget(self),
            "catat":       PencatatanLisensiWidget(self),
            "perkara":     PerkaraWidget(self),
        }

        # masukkan ke stack dan simpan index
        self.index = {}
        for key, w in self.pages.items():
            self.index[key] = self.stack.addWidget(w)

        # pasang ke root layout
        left = QWidget(); left.setLayout(sidebar)
        left.setFixedWidth(200)  # biar sidebar gak melebar liar
        hl.addWidget(left)
        hl.addWidget(self.stack, 1)  # konten ambil sisa ruang

        # koneksi tombol -> switch halaman
        self.btn_pihak.clicked.connect(lambda: self._switch("pihak"))
        self.btn_dasar.clicked.connect(lambda: self._switch("dasar"))
        self.btn_objek.clicked.connect(lambda: self._switch("objek"))
        self.btn_lisensi.clicked.connect(lambda: self._switch("lisensi"))
        self.btn_pelanggaran.clicked.connect(lambda: self._switch("pelanggaran"))
        self.btn_catat.clicked.connect(lambda: self._switch("catat"))
        self.btn_perkara.clicked.connect(lambda: self._switch("perkara"))

        # tampilkan halaman default
        self._switch("pihak")

    def _switch(self, key: str):
        """Ganti halaman tanpa buka jendela baru. Anti tumpang tindih."""
        idx = self.index.get(key)
        if idx is not None:
            self.stack.setCurrentIndex(idx)
            # opsional: update judul jendela
            titles = {
                "pihak": "Manajemen Pihak",
                "dasar": "Dasar Hukum",
                "objek": "Objek Kekayaan Intelektual",
                "lisensi": "Lisensi",
                "pelanggaran": "Pelanggaran",
                "catat": "Pencatatan Lisensi",
                "perkara": "Perkara",
            }
            self.setWindowTitle(f"Visual3 - {titles.get(key, 'CRUD Hukum')}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
