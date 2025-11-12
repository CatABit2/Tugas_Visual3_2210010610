from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt
from cruddb import Crud

SELECT_ROWS      = getattr(QAbstractItemView, "SelectRows", QAbstractItemView.SelectionBehavior.SelectRows)
SINGLE_SELECTION = getattr(QAbstractItemView, "SingleSelection", QAbstractItemView.SelectionMode.SingleSelection)
NO_EDIT_TRIGGERS = getattr(QAbstractItemView, "NoEditTriggers", QAbstractItemView.EditTrigger.NoEditTriggers)

repo_pelanggaran = Crud("pelanggaran", "id", ["perkara_id","pihak_pelanggar_id","jenis","uraian"])
repo_perkara     = Crud("perkara", "id", ["nomor_pn"])
repo_pihak       = Crud("pihak", "id", ["nama"])

class PelanggaranWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_id = None
        self._ui(); self._reload_sources(); self.load_table()

    def _ui(self):
        lay = QVBoxLayout(self); split = QSplitter(Qt.Vertical); lay.addWidget(split, 1)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID","Perkara","Pihak Pelanggar","Jenis","Uraian"])
        self.table.setSelectionBehavior(SELECT_ROWS)
        self.table.setSelectionMode(SINGLE_SELECTION)
        self.table.setEditTriggers(NO_EDIT_TRIGGERS)
        self.table.verticalHeader().setVisible(False)
        hh = self.table.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.Stretch)
        split.addWidget(self.table)

        gb = QGroupBox("Form Pelanggaran"); f = QFormLayout(gb)
        self.cb_perkara = QComboBox()
        self.cb_pelanggar = QComboBox()
        self.le_jenis = QLineEdit()
        self.te_uraian = QTextEdit()
        f.addRow("Perkara", self.cb_perkara)
        f.addRow("Pihak Pelanggar", self.cb_pelanggar)
        f.addRow("Jenis", self.le_jenis)
        f.addRow("Uraian", self.te_uraian)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Tambah"); self.btn_upd = QPushButton("Ubah"); self.btn_del = QPushButton("Hapus")
        btns.addStretch(); btns.addWidget(self.btn_add); btns.addWidget(self.btn_upd); btns.addWidget(self.btn_del)

        wrap = QWidget(); v = QVBoxLayout(wrap); v.setContentsMargins(0,0,0,0); v.addWidget(gb); v.addLayout(btns)
        split.addWidget(wrap); split.setStretchFactor(0,3); split.setStretchFactor(1,1)

        self.table.itemSelectionChanged.connect(self._on_select)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_upd.clicked.connect(self.on_upd)
        self.btn_del.clicked.connect(self.on_del)

    def _reload_sources(self):
        self.cb_perkara.clear()
        for r in repo_perkara.all(order_by="id"):
            label = f'{r.get("nomor_pn") or "-"} (ID {r["id"]})'
            self.cb_perkara.addItem(label, r["id"])
        self.cb_pelanggar.clear()
        for r in repo_pihak.all(order_by="nama"):
            self.cb_pelanggar.addItem(r["nama"], r["id"])

    def load_table(self):
        sql = """
        SELECT g.id, p.nomor_pn AS perkara, ph.nama AS pelanggar, g.jenis, g.uraian
        FROM pelanggaran g
        LEFT JOIN perkara p ON p.id = g.perkara_id
        LEFT JOIN pihak ph ON ph.id = g.pihak_pelanggar_id
        ORDER BY g.id
        """
        rows = repo_pelanggaran.raw(sql)
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount(); self.table.insertRow(i)
            self.table.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.table.setItem(i,1,QTableWidgetItem(r.get("perkara") or "-"))
            self.table.setItem(i,2,QTableWidgetItem(r.get("pelanggar") or "-"))
            self.table.setItem(i,3,QTableWidgetItem(r.get("jenis","") or ""))
            self.table.setItem(i,4,QTableWidgetItem(r.get("uraian","") or ""))
        self.selected_id = None

    def _on_select(self):
        row = self.table.currentRow()
        if row < 0: self.selected_id = None; return
        self.selected_id = int(self.table.item(row,0).text())
        # set combos by label
        perkara = self.table.item(row,1).text()
        for i in range(self.cb_perkara.count()):
            if self.cb_perkara.itemText(i).startswith(perkara):
                self.cb_perkara.setCurrentIndex(i); break
        pelanggar = self.table.item(row,2).text()
        for i in range(self.cb_pelanggar.count()):
            if self.cb_pelanggar.itemText(i) == pelanggar:
                self.cb_pelanggar.setCurrentIndex(i); break
        self.le_jenis.setText(self.table.item(row,3).text())
        self.te_uraian.setPlainText(self.table.item(row,4).text())

    def _collect(self):
        return {
            "perkara_id": self.cb_perkara.currentData(),
            "pihak_pelanggar_id": self.cb_pelanggar.currentData(),
            "jenis": self.le_jenis.text().strip() or None,
            "uraian": self.te_uraian.toPlainText().strip() or None
        }

    def on_add(self):
        repo_pelanggaran.insert(self._collect()); self.load_table()

    def on_upd(self):
        if not self.selected_id: QMessageBox.warning(self,"Info","Pilih baris dulu"); return
        repo_pelanggaran.update(self.selected_id, self._collect()); self.load_table()

    def on_del(self):
        if not self.selected_id: QMessageBox.warning(self,"Info","Pilih baris dulu"); return
        repo_pelanggaran.delete(self.selected_id); self.load_table()
