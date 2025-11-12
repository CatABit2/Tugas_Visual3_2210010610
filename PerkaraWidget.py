# PerkaraWidget.py — versi beres: tanggal dikonversi ke string sebelum dimasukkan ke QTableWidgetItem
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from cruddb import Crud

# Tabel: perkara(id, nomor_pn, nomor_ma, tgl_putusan_pn, tgl_putusan_ma, ringkas)
repo_perkara = Crud(
    table="perkara",
    pk="id",
    columns=["nomor_pn", "nomor_ma", "tgl_putusan_pn", "tgl_putusan_ma", "ringkas"]
)

def _to_str_date(v):
    """Konversi Python date/datetime atau string ke 'yyyy-MM-dd' untuk ditampilkan."""
    if v is None:
        return ""
    # PyMySQL biasanya kasih datetime.date/datetime.datetime
    try:
        # kalau objek punya strftime
        return v.strftime("%Y-%m-%d")
    except Exception:
        # kalau sudah string, kembalikan apa adanya
        return str(v)

class PerkaraWidget(QWidget):
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

        title = QLabel("<b>Perkara</b>")
        root.addWidget(title)

        # Bar cari
        bar = QHBoxLayout()
        self.le_cari = QLineEdit()
        self.le_cari.setPlaceholderText("Cari nomor PN / nomor MA / ringkasan")
        self.btn_cari = QPushButton("Cari")
        self.btn_reload = QPushButton("Muat Ulang")
        bar.addWidget(self.le_cari, 1)
        bar.addWidget(self.btn_cari)
        bar.addWidget(self.btn_reload)
        root.addLayout(bar)

        # Tabel
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nomor PN", "Nomor MA", "Putusan PN", "Putusan MA", "Ringkas"
        ])
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

        self.le_nomor_pn = QLineEdit()
        self.le_nomor_ma = QLineEdit()

        self.de_putusan_pn = QDateEdit()
        self.de_putusan_pn.setDisplayFormat("yyyy-MM-dd")
        self.de_putusan_pn.setCalendarPopup(True)
        self.de_putusan_pn.setDate(QDate.currentDate())

        self.de_putusan_ma = QDateEdit()
        self.de_putusan_ma.setDisplayFormat("yyyy-MM-dd")
        self.de_putusan_ma.setCalendarPopup(True)
        self.de_putusan_ma.setDate(QDate.currentDate())

        self.te_ringkas = QTextEdit()
        self.te_ringkas.setPlaceholderText("Ringkasan singkat perkara...")

        r = 0
        form.addWidget(QLabel("Nomor PN"),   r, 0); form.addWidget(self.le_nomor_pn, r, 1); r += 1
        form.addWidget(QLabel("Nomor MA"),   r, 0); form.addWidget(self.le_nomor_ma, r, 1); r += 1
        form.addWidget(QLabel("Putusan PN"), r, 0); form.addWidget(self.de_putusan_pn, r, 1); r += 1
        form.addWidget(QLabel("Putusan MA"), r, 0); form.addWidget(self.de_putusan_ma, r, 1); r += 1
        form.addWidget(QLabel("Ringkas"),    r, 0); form.addWidget(self.te_ringkas,  r, 1); r += 1

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
        self.le_nomor_pn.clear()
        self.le_nomor_ma.clear()
        self.de_putusan_pn.setDate(QDate.currentDate())
        self.de_putusan_ma.setDate(QDate.currentDate())
        self.te_ringkas.clear()

    def _date_str(self, de: QDateEdit):
        d = de.date()
        return d.toString("yyyy-MM-dd") if d.isValid() else None

    def _set_cell(self, row, col, val):
        self.table.setItem(row, col, QTableWidgetItem("" if val is None else str(val)))

    # ============== DATA ==============
    def load_table(self):
        q = (self.le_cari.text() or "").strip()

        # Gunakan LIKE dengan CONCAT. Perhatikan placeholder % yang aman di PyMySQL.
        sql = """
        SELECT id, nomor_pn, nomor_ma, tgl_putusan_pn, tgl_putusan_ma, ringkas
        FROM perkara
        WHERE
            %s = '' OR
            LOWER(nomor_pn) LIKE CONCAT('%%', LOWER(%s), '%%') OR
            LOWER(nomor_ma) LIKE CONCAT('%%', LOWER(%s), '%%') OR
            LOWER(ringkas)  LIKE CONCAT('%%', LOWER(%s), '%%')
        ORDER BY id DESC
        """
        rows = repo_perkara.raw(sql, (q, q, q, q))

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self._set_cell(i, 0, r.get("id"))
            self._set_cell(i, 1, r.get("nomor_pn"))
            self._set_cell(i, 2, r.get("nomor_ma"))
            self._set_cell(i, 3, _to_str_date(r.get("tgl_putusan_pn")))
            self._set_cell(i, 4, _to_str_date(r.get("tgl_putusan_ma")))
            # ringkas dipotong biar tabel ga kepanjangan, detailnya tetap di form
            ringkas = r.get("ringkas") or ""
            self._set_cell(i, 5, ringkas if len(ringkas) <= 120 else ringkas[:117] + "...")
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

        self.le_nomor_pn.setText(cell(1))
        self.le_nomor_ma.setText(cell(2))

        s_pn = cell(3)
        self.de_putusan_pn.setDate(QDate.fromString(s_pn, "yyyy-MM-dd") if s_pn else QDate.currentDate())

        s_ma = cell(4)
        self.de_putusan_ma.setDate(QDate.fromString(s_ma, "yyyy-MM-dd") if s_ma else QDate.currentDate())

        # untuk ringkas, ambil dari DB lagi biar tidak terpotong
        pk = self._selected_id()
        row = repo_perkara.get(pk)
        self.te_ringkas.setPlainText((row or {}).get("ringkas") or "")

    # ============== VALIDASI ==============
    def _valid(self):
        if not (self.le_nomor_pn.text().strip() or self.le_nomor_ma.text().strip()):
            QMessageBox.warning(self, "Validasi", "Minimal isi Nomor PN atau Nomor MA.")
            return False
        return True

    # ============== CRUD ==============
    def _collect(self):
        return {
            "nomor_pn": (self.le_nomor_pn.text() or "").strip() or None,
            "nomor_ma": (self.le_nomor_ma.text() or "").strip() or None,
            "tgl_putusan_pn": self._date_str(self.de_putusan_pn),
            "tgl_putusan_ma": self._date_str(self.de_putusan_ma),
            "ringkas": self.te_ringkas.toPlainText().strip() or None
        }

    def _add(self):
        if not self._valid():
            return
        data = self._collect()
        repo_perkara.insert(data)
        self.load_table()

    def _upd(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        if not self._valid():
            return
        data = self._collect()
        repo_perkara.update(pk, data)
        self.load_table()

    def _del(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        if QMessageBox.question(self, "Konfirmasi", "Hapus data terpilih?") == QMessageBox.Yes:
            repo_perkara.delete(pk)
            self.load_table()
