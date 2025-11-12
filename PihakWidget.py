# PihakWidget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from cruddb import Crud

# Kompat untuk berbagai versi PySide6
SELECT_ROWS      = getattr(QAbstractItemView, "SelectRows", QAbstractItemView.SelectionBehavior.SelectRows)
SINGLE_SELECTION = getattr(QAbstractItemView, "SingleSelection", QAbstractItemView.SelectionMode.SingleSelection)
NO_EDIT_TRIGGERS = getattr(QAbstractItemView, "NoEditTriggers", QAbstractItemView.EditTrigger.NoEditTriggers)

JENIS = ["licensor", "licensee", "pihak_ketiga"]
repo_pihak = Crud(table="pihak", pk="id", columns=["nama", "jenis", "entitas"])

class PihakWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_id = None
        self._build_ui()
        self.load_table()

    # ================= UI =================
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Judul
        lbl_title = QLabel("Manajemen Pihak")
        f = QFont()
        f.setPointSize(12)
        f.setBold(True)
        lbl_title.setFont(f)
        root.addWidget(lbl_title)

        # Toolbar cari + filter
        toolbar = QHBoxLayout()
        self.le_cari = QLineEdit()
        self.le_cari.setPlaceholderText("Cari: id/nama/entitas/jenis")
        self.cb_filter = QComboBox()
        self.cb_filter.addItems(["Semua"] + JENIS)
        btn_cari = QPushButton("Cari")
        btn_refresh = QPushButton("Muat Ulang")

        toolbar.addWidget(QLabel("Filter Jenis"))
        toolbar.addWidget(self.cb_filter, 0)
        toolbar.addSpacing(8)
        toolbar.addWidget(self.le_cari, 1)
        toolbar.addWidget(btn_cari, 0)
        toolbar.addWidget(btn_refresh, 0)
        root.addLayout(toolbar)

        # Tabel
        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Jenis", "Entitas"])
        self.table.setSelectionBehavior(SELECT_ROWS)
        self.table.setSelectionMode(SINGLE_SELECTION)
        self.table.setEditTriggers(NO_EDIT_TRIGGERS)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        hh = self.table.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        root.addWidget(self.table, 1)

        # Form di GroupBox
        gb = QGroupBox("Form")
        fl = QFormLayout(gb)
        self.le_nama = QLineEdit()
        self.le_nama.setPlaceholderText("Nama pihak")
        self.cb_jenis = QComboBox()
        self.cb_jenis.addItems(JENIS)
        self.le_entitas = QLineEdit()
        self.le_entitas.setPlaceholderText("Entitas (opsional)")
        fl.addRow("Nama", self.le_nama)
        fl.addRow("Jenis", self.cb_jenis)
        fl.addRow("Entitas", self.le_entitas)
        root.addWidget(gb, 0)

        # Tombol CRUD
        btns = QHBoxLayout()
        btns.addStretch()
        self.btn_tambah = QPushButton("Tambah")
        self.btn_ubah   = QPushButton("Ubah")
        self.btn_hapus  = QPushButton("Hapus")
        for b in (self.btn_tambah, self.btn_ubah, self.btn_hapus):
            btns.addWidget(b)
        root.addLayout(btns)

        # Status
        self.lbl_status = QLabel("0 baris")
        self.lbl_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        root.addWidget(self.lbl_status)

        # Wiring events
        self.table.itemSelectionChanged.connect(self._on_select)
        btn_cari.clicked.connect(self.on_cari)
        btn_refresh.clicked.connect(self.load_table)
        self.cb_filter.currentIndexChanged.connect(self.on_cari)
        self.le_cari.returnPressed.connect(self.on_cari)
        self.btn_tambah.clicked.connect(self.on_tambah)
        self.btn_ubah.clicked.connect(self.on_ubah)
        self.btn_hapus.clicked.connect(self.on_hapus)

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.btn_tambah.click)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.btn_ubah.click)
        QShortcut(QKeySequence("Delete"), self, activated=self.btn_hapus.click)

        self.resize(900, 560)

    # ============== DATA OPS ==============
    def _query_rows(self, keyword: str, jenis_filter: str):
        keyword = (keyword or "").strip()
        jf = jenis_filter.strip().lower() if jenis_filter else ""
        if jf and jf in JENIS:
            if keyword:
                where = "jenis=%s AND (CAST(id AS CHAR) LIKE %s OR nama LIKE %s OR entitas LIKE %s)"
                kw = f"%{keyword}%"
                return repo_pihak.find(where, (jf, kw, kw, kw), order_by="id")
            else:
                return repo_pihak.find("jenis=%s", (jf,), order_by="id")
        else:
            if keyword:
                return repo_pihak.like_any(["id", "nama", "entitas", "jenis"], keyword, order_by="id")
            return repo_pihak.all(order_by="id")

    def load_table(self):
        self.table.setSortingEnabled(False)
        rows = self._query_rows("", "Semua")
        self._fill_table(rows)
        self.table.setSortingEnabled(True)
        self._set_status(rows)

    def on_cari(self):
        self.table.setSortingEnabled(False)
        rows = self._query_rows(self.le_cari.text(), self.cb_filter.currentText())
        self._fill_table(rows)
        self.table.setSortingEnabled(True)
        self._set_status(rows)

    def _fill_table(self, rows):
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(r.get("id", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(r.get("nama") or ""))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("jenis") or ""))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("entitas") or ""))
        self._clear_form()

    def _set_status(self, rows):
        self.lbl_status.setText(f"{len(rows)} baris")

    # ============== CRUD ==============
    def on_tambah(self):
        if not self._valid():
            return
        repo_pihak.insert({
            "nama": self.le_nama.text().strip(),
            "jenis": self.cb_jenis.currentText(),
            "entitas": self.le_entitas.text().strip()
        })
        self.on_cari()

    def on_ubah(self):
        if self.selected_id is None:
            QMessageBox.information(self, "Info", "Pilih baris dulu")
            return
        if not self._valid():
            return
        repo_pihak.update(self.selected_id, {
            "nama": self.le_nama.text().strip(),
            "jenis": self.cb_jenis.currentText(),
            "entitas": self.le_entitas.text().strip()
        })
        self.on_cari()

    def on_hapus(self):
        if self.selected_id is None:
            QMessageBox.information(self, "Info", "Pilih baris dulu")
            return
        if QMessageBox.question(self, "Konfirmasi", "Hapus data ini?") == QMessageBox.Yes:
            repo_pihak.delete(self.selected_id)
            self.on_cari()

    # ============== Helper ==============
    def _on_select(self):
        rng = self.table.selectedRanges()
        if not rng:
            self.selected_id = None
            return
        row = rng[0].topRow()
        self.selected_id = int(self.table.item(row, 0).text())
        self.le_nama.setText(self.table.item(row, 1).text())
        self.cb_jenis.setCurrentText(self.table.item(row, 2).text())
        self.le_entitas.setText(self.table.item(row, 3).text())

    def _valid(self):
        if not self.le_nama.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama wajib diisi")
            return False
        if self.cb_jenis.currentText() not in JENIS:
            QMessageBox.warning(self, "Validasi", "Jenis tidak valid")
            return False
        return True

    def _clear_form(self):
        self.selected_id = None
        self.le_nama.clear()
        self.le_entitas.clear()
        self.cb_jenis.setCurrentIndex(0)
        self.table.clearSelection()
