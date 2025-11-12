# PencatatanLisensiWidget.py — satu file utuh, fix “QTableWidgetItem(date)” dengan konversi string
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt, QDate
from cruddb import Crud

# Tabel: pencatatan_lisensi(id, lisensi_id, nomor, tanggal, instansi)
repo_catat = Crud(
    table="pencatatan_lisensi",
    pk="id",
    columns=["lisensi_id", "nomor", "tanggal", "instansi"]
)

class PencatatanLisensiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui()
        self._wire()
        self.load_table()

    # ============== UI ==============
    def _ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("<b>Pencatatan Lisensi</b>")
        root.addWidget(title)

        # Bar cari
        bar = QHBoxLayout()
        self.le_cari = QLineEdit()
        self.le_cari.setPlaceholderText("Cari nomor / lisensi_id / instansi")
        self.btn_cari = QPushButton("Cari")
        self.btn_reload = QPushButton("Muat Ulang")
        bar.addWidget(self.le_cari, 1)
        bar.addWidget(self.btn_cari)
        bar.addWidget(self.btn_reload)
        root.addLayout(bar)

        # Tabel
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Lisensi ID", "Nomor", "Tanggal", "Instansi"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        root.addWidget(self.table, 1)

        # Form
        gb = QGroupBox("Form")
        form = QGridLayout(gb)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(6)

        self.sp_lisensi = QSpinBox(); self.sp_lisensi.setMaximum(2_000_000_000)
        self.le_nomor = QLineEdit()
        self.de_tanggal = QDateEdit()
        self.de_tanggal.setDisplayFormat("yyyy-MM-dd")
        self.de_tanggal.setCalendarPopup(True)
        self.de_tanggal.setDate(QDate.currentDate())
        self.le_instansi = QLineEdit()

        r = 0
        form.addWidget(QLabel("Lisensi ID"), r, 0); form.addWidget(self.sp_lisensi, r, 1); r += 1
        form.addWidget(QLabel("Nomor"),     r, 0); form.addWidget(self.le_nomor, r, 1); r += 1
        form.addWidget(QLabel("Tanggal"),   r, 0); form.addWidget(self.de_tanggal, r, 1); r += 1
        form.addWidget(QLabel("Instansi"),  r, 0); form.addWidget(self.le_instansi, r, 1); r += 1

        hb = QHBoxLayout()
        self.btn_add = QPushButton("Tambah")
        self.btn_upd = QPushButton("Ubah")
        self.btn_del = QPushButton("Hapus")
        hb.addStretch(1); hb.addWidget(self.btn_add); hb.addWidget(self.btn_upd); hb.addWidget(self.btn_del)

        form.addLayout(hb, r, 0, 1, 2)
        root.addWidget(gb)

    def _wire(self):
        self.btn_reload.clicked.connect(self.load_table)
        self.btn_cari.clicked.connect(self.load_table)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.btn_add.clicked.connect(self._add)
        self.btn_upd.clicked.connect(self._upd)
        self.btn_del.clicked.connect(self._del)

    # ============== UTIL ==============
    def _selected_id(self):
        r = self.table.currentRow()
        if r < 0:
            return None
        it = self.table.item(r, 0)
        try:
            return int(it.text()) if it and it.text() else None
        except Exception:
            return None

    def _clear_form(self):
        self.sp_lisensi.setValue(0)
        self.le_nomor.clear()
        self.de_tanggal.setDate(QDate.currentDate())
        self.le_instansi.clear()

    def _date_str(self, de: QDateEdit):
        d = de.date()
        return d.toString("yyyy-MM-dd") if d.isValid() else None

    def _set_cell(self, row, col, val):
        self.table.setItem(row, col, QTableWidgetItem("" if val is None else str(val)))

    # ============== DATA ==============
    def load_table(self):
        q = (self.le_cari.text() or "").strip()
        # Penting: semua '%' digandakan '%%' agar tidak bentrok dengan operator % pada PyMySQL
        sql = """
        SELECT
            id,
            lisensi_id,
            nomor,
            DATE_FORMAT(tanggal, %s) AS tanggal,
            instansi
        FROM pencatatan_lisensi
        WHERE
            %s = '' OR
            LOWER(nomor) LIKE CONCAT('%%', LOWER(%s), '%%') OR
            CAST(lisensi_id AS CHAR) LIKE CONCAT('%%', %s, '%%') OR
            LOWER(instansi) LIKE CONCAT('%%', LOWER(%s), '%%')
        ORDER BY id DESC
        """
        params = ('%Y-%m-%d', q, q, q, q)
        rows = repo_catat.raw(sql, params)

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            # Pastikan semua nilai jadi string normal
            self._set_cell(i, 0, r.get("id"))
            self._set_cell(i, 1, r.get("lisensi_id"))
            self._set_cell(i, 2, r.get("nomor"))
            self._set_cell(i, 3, r.get("tanggal"))       # sudah string via DATE_FORMAT
            self._set_cell(i, 4, r.get("instansi"))

        if self.table.rowCount() > 0:
            self.table.selectRow(0)
        else:
            self._clear_form()

    # ============== TABLE -> FORM ==============
    def _on_select(self):
        r = self.table.currentRow()
        if r < 0:
            self._clear_form()
            return

        def cell(c):
            it = self.table.item(r, c)
            return "" if it is None else it.text()

        self.sp_lisensi.setValue(int(cell(1) or 0))
        self.le_nomor.setText(cell(2))
        # tanggal aman
        s = cell(3)
        if s:
            self.de_tanggal.setDate(QDate.fromString(s, "yyyy-MM-dd"))
        else:
            self.de_tanggal.setDate(QDate.currentDate())
        self.le_instansi.setText(cell(4))

    # ============== CRUD ==============
    def _collect(self):
        return {
            "lisensi_id": int(self.sp_lisensi.value()) or None,
            "nomor": (self.le_nomor.text() or "").strip() or None,
            "tanggal": self._date_str(self.de_tanggal),
            "instansi": (self.le_instansi.text() or "").strip() or None
        }

    def _add(self):
        data = self._collect()
        if not data["nomor"]:
            QMessageBox.warning(self, "Validasi", "Nomor wajib diisi.")
            return
        repo_catat.insert(data)
        self.load_table()

    def _upd(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        data = self._collect()
        repo_catat.update(pk, data)
        self.load_table()

    def _del(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        if QMessageBox.question(self, "Konfirmasi", "Hapus data terpilih?") == QMessageBox.Yes:
            repo_catat.delete(pk)
            self.load_table()
