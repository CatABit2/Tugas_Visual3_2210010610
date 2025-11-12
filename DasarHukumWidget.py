# DasarHukumWidget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QLabel, QGroupBox, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt
from cruddb import Crud

# Tabel: dasar_hukum(id, sumber, pasal, ringkas)
repo_dasar = Crud(
    table="dasar_hukum",
    pk="id",
    columns=["sumber", "pasal", "ringkas"]
)

class DasarHukumWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._wire()
        self.load_table()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("<b>Dasar Hukum</b>")
        root.addWidget(title)

        # bar cari
        hb = QHBoxLayout()
        self.ed_cari = QLineEdit()
        self.ed_cari.setPlaceholderText("Cari sumber / pasal / ringkas")
        self.btn_cari = QPushButton("Cari")
        self.btn_reload = QPushButton("Muat Ulang")
        hb.addWidget(self.ed_cari, 1)
        hb.addWidget(self.btn_cari)
        hb.addWidget(self.btn_reload)
        root.addLayout(hb)

        # tabel (tanpa kolom No, urut ID ASC)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Sumber", "Pasal", "Ringkas"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        root.addWidget(self.table, 1)

        # form
        gb = QGroupBox("Form")
        form = QGridLayout(gb); form.setHorizontalSpacing(8); form.setVerticalSpacing(6)

        self.ed_sumber  = QLineEdit()
        self.ed_pasal   = QLineEdit()
        self.ed_ringkas = QLineEdit()

        form.addWidget(QLabel("Sumber"),  0, 0); form.addWidget(self.ed_sumber,  0, 1, 1, 3)
        form.addWidget(QLabel("Pasal"),   1, 0); form.addWidget(self.ed_pasal,   1, 1, 1, 3)
        form.addWidget(QLabel("Ringkas"), 2, 0); form.addWidget(self.ed_ringkas, 2, 1, 1, 3)

        hb2 = QHBoxLayout()
        self.btn_add = QPushButton("Tambah")
        self.btn_upd = QPushButton("Ubah")
        self.btn_del = QPushButton("Hapus")
        hb2.addStretch(1); hb2.addWidget(self.btn_add); hb2.addWidget(self.btn_upd); hb2.addWidget(self.btn_del)
        form.addLayout(hb2, 3, 0, 1, 4)

        root.addWidget(gb)

    def _wire(self):
        self.btn_reload.clicked.connect(self.load_table)
        self.btn_cari.clicked.connect(self.load_table)
        self.table.itemSelectionChanged.connect(self._on_select)

        self.btn_add.clicked.connect(self._add)
        self.btn_upd.clicked.connect(self._upd)
        self.btn_del.clicked.connect(self._del)

    # ===== util =====
    def _selected_id(self):
        r = self.table.currentRow()
        if r < 0: return None
        it = self.table.item(r, 0)  # kolom 0 = ID
        return int(it.text()) if it and it.text().isdigit() else None

    def _cell(self, row, col):
        it = self.table.item(row, col)
        return "" if it is None else it.text()

    def _on_select(self):
        r = self.table.currentRow()
        if r < 0:
            self._clear_form()
            return
        self.ed_sumber.setText(self._cell(r, 1))
        self.ed_pasal.setText(self._cell(r, 2))
        self.ed_ringkas.setText(self._cell(r, 3))

    def _clear_form(self):
        self.ed_sumber.clear()
        self.ed_pasal.clear()
        self.ed_ringkas.clear()

    def _collect(self):
        return {
            "sumber":  self.ed_sumber.text().strip() or None,
            "pasal":   self.ed_pasal.text().strip() or None,
            "ringkas": self.ed_ringkas.text().strip() or None
        }

    # ===== data =====
    def load_table(self):
        q = (self.ed_cari.text() or "").strip()
        if q:
            rows = repo_dasar.raw(
                (
                    "SELECT id, sumber, pasal, ringkas "
                    "FROM dasar_hukum "
                    "WHERE LOWER(sumber)  LIKE CONCAT('%%', LOWER(%s), '%%') "
                    "   OR LOWER(pasal)   LIKE CONCAT('%%', LOWER(%s), '%%') "
                    "   OR LOWER(ringkas) LIKE CONCAT('%%', LOWER(%s), '%%') "
                    "ORDER BY id ASC"
                ),
                (q, q, q)
            )
        else:
            rows = repo_dasar.all(order_by="id ASC")

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(r.get("id") or "")))
            self.table.setItem(i, 1, QTableWidgetItem(r.get("sumber") or ""))
            self.table.setItem(i, 2, QTableWidgetItem(r.get("pasal") or ""))
            self.table.setItem(i, 3, QTableWidgetItem(r.get("ringkas") or ""))

        if self.table.rowCount() > 0:
            self.table.selectRow(0)
        else:
            self._clear_form()

    # ===== crud =====
    def _add(self):
        data = self._collect()
        if not data["sumber"]:
            QMessageBox.warning(self, "Validasi", "Sumber wajib diisi.")
            return
        repo_dasar.insert(data)
        self.load_table()

    def _upd(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        data = self._collect()
        repo_dasar.update(pk, data)
        self.load_table()

    def _del(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        repo_dasar.delete(pk)
        self.load_table()
