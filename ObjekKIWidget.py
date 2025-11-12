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

repo_objek = Crud("objek_ki", "id", ["nama","jenis","deskripsi"])

class ObjekKIWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_id = None
        self._ui(); self.load_table()

    def _ui(self):
        lay = QVBoxLayout(self); split = QSplitter(Qt.Vertical); lay.addWidget(split, 1)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID","Nama","Jenis","Deskripsi"])
        self.table.setSelectionBehavior(SELECT_ROWS)
        self.table.setSelectionMode(SINGLE_SELECTION)
        self.table.setEditTriggers(NO_EDIT_TRIGGERS)
        self.table.verticalHeader().setVisible(False)
        hh = self.table.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        split.addWidget(self.table)

        gb = QGroupBox("Form Objek KI"); f = QFormLayout(gb)
        self.le_nama = QLineEdit()
        self.cb_jenis = QComboBox()
        self.cb_jenis.addItems(["hak_cipta","hak_terkait","merek","paten","desain_industri","rahasia_dagang","indikasi_geografis"])
        self.te_deskripsi = QTextEdit()
        f.addRow("Nama", self.le_nama)
        f.addRow("Jenis", self.cb_jenis)
        f.addRow("Deskripsi", self.te_deskripsi)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Tambah"); self.btn_upd = QPushButton("Ubah"); self.btn_del = QPushButton("Hapus")
        btns.addStretch(); btns.addWidget(self.btn_add); btns.addWidget(self.btn_upd); btns.addWidget(self.btn_del)

        wrap = QWidget(); v = QVBoxLayout(wrap); v.setContentsMargins(0,0,0,0); v.addWidget(gb); v.addLayout(btns)
        split.addWidget(wrap); split.setStretchFactor(0,3); split.setStretchFactor(1,1)

        self.table.itemSelectionChanged.connect(self._on_select)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_upd.clicked.connect(self.on_upd)
        self.btn_del.clicked.connect(self.on_del)

    def load_table(self):
        rows = repo_objek.all(order_by="id")
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount(); self.table.insertRow(i)
            self.table.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.table.setItem(i,1,QTableWidgetItem(r.get("nama","")))
            self.table.setItem(i,2,QTableWidgetItem(r.get("jenis","")))
            self.table.setItem(i,3,QTableWidgetItem(r.get("deskripsi","")))
        self.selected_id = None

    def _on_select(self):
        row = self.table.currentRow()
        if row < 0: self.selected_id = None; return
        self.selected_id = int(self.table.item(row,0).text())
        self.le_nama.setText(self.table.item(row,1).text())
        self.cb_jenis.setCurrentText(self.table.item(row,2).text())
        self.te_deskripsi.setPlainText(self.table.item(row,3).text())

    def on_add(self):
        data = {"nama": self.le_nama.text().strip(),
                "jenis": self.cb_jenis.currentText(),
                "deskripsi": self.te_deskripsi.toPlainText().strip()}
        if not data["nama"]:
            QMessageBox.warning(self,"Validasi","Nama wajib diisi"); return
        repo_objek.insert(data); self.load_table()

    def on_upd(self):
        if not self.selected_id: QMessageBox.warning(self,"Info","Pilih baris dulu"); return
        data = {"nama": self.le_nama.text().strip(),
                "jenis": self.cb_jenis.currentText(),
                "deskripsi": self.te_deskripsi.toPlainText().strip()}
        repo_objek.update(self.selected_id, data); self.load_table()

    def on_del(self):
        if not self.selected_id: QMessageBox.warning(self,"Info","Pilih baris dulu"); return
        repo_objek.delete(self.selected_id); self.load_table()
