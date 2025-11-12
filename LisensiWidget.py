# LisensiWidget.py — satu file utuh, sudah aman dari error “unsupported format character”
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QCheckBox, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt, QDate
from cruddb import Crud

# Tabel: lisensi(id, nomor, licensor_id, licensee_id, objek_id, dicatat, nomor_pencatatan, dasar_hukum_id, tanggal_mulai, tanggal_akhir)
repo_lisensi = Crud(
    table="lisensi",
    pk="id",
    columns=["nomor", "licensor_id", "licensee_id", "objek_id", "dicatat",
             "nomor_pencatatan", "dasar_hukum_id", "tanggal_mulai", "tanggal_akhir"]
)

class LisensiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui()
        self._wire()
        self.load_table()

    # ================= UI =================
    def _ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("<b>Lisensi</b>")
        root.addWidget(title)

        # Bar cari
        bar = QHBoxLayout()
        self.ed_cari = QLineEdit()
        self.ed_cari.setPlaceholderText("Cari nomor / licensor_id / licensee_id / objek_id")
        self.btn_cari = QPushButton("Cari")
        self.btn_reload = QPushButton("Muat Ulang")
        bar.addWidget(self.ed_cari, 1)
        bar.addWidget(self.btn_cari)
        bar.addWidget(self.btn_reload)
        root.addLayout(bar)

        # Tabel
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nomor", "Licensor", "Licensee", "Objek",
            "Dicatat", "No. Pencatatan", "Dasar Hukum", "Tgl Mulai", "Tgl Akhir"
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

        self.ed_nomor = QLineEdit()
        self.sp_licensor  = QSpinBox(); self.sp_licensor.setMaximum(2_000_000_000)
        self.sp_licensee  = QSpinBox(); self.sp_licensee.setMaximum(2_000_000_000)
        self.sp_objek     = QSpinBox(); self.sp_objek.setMaximum(2_000_000_000)
        self.cb_dicatat   = QCheckBox("Dicatat")
        self.ed_no_catat  = QLineEdit()
        self.sp_dasar     = QSpinBox(); self.sp_dasar.setMaximum(2_000_000_000)

        self.de_mulai = QDateEdit()
        self.de_mulai.setDisplayFormat("yyyy-MM-dd")
        self.de_mulai.setCalendarPopup(True)
        self.de_mulai.setDate(QDate.currentDate())

        self.de_akhir = QDateEdit()
        self.de_akhir.setDisplayFormat("yyyy-MM-dd")
        self.de_akhir.setCalendarPopup(True)
        self.de_akhir.setDate(QDate.currentDate())

        r = 0
        form.addWidget(QLabel("Nomor"), r, 0); form.addWidget(self.ed_nomor, r, 1, 1, 3); r += 1
        form.addWidget(QLabel("Licensor ID"), r, 0); form.addWidget(self.sp_licensor, r, 1)
        form.addWidget(QLabel("Licensee ID"), r, 2); form.addWidget(self.sp_licensee, r, 3); r += 1
        form.addWidget(QLabel("Objek ID"), r, 0); form.addWidget(self.sp_objek, r, 1)
        form.addWidget(self.cb_dicatat, r, 2); r += 1
        form.addWidget(QLabel("No. Pencatatan"), r, 0); form.addWidget(self.ed_no_catat, r, 1)
        form.addWidget(QLabel("Dasar Hukum ID"), r, 2); form.addWidget(self.sp_dasar, r, 3); r += 1
        form.addWidget(QLabel("Tanggal Mulai"), r, 0); form.addWidget(self.de_mulai, r, 1)
        form.addWidget(QLabel("Tanggal Akhir"), r, 2); form.addWidget(self.de_akhir, r, 3); r += 1

        hb_btn = QHBoxLayout()
        self.btn_add = QPushButton("Tambah")
        self.btn_upd = QPushButton("Ubah")
        self.btn_del = QPushButton("Hapus")
        hb_btn.addStretch(1)
        hb_btn.addWidget(self.btn_add); hb_btn.addWidget(self.btn_upd); hb_btn.addWidget(self.btn_del)

        form.addLayout(hb_btn, r, 0, 1, 4)
        root.addWidget(gb)

    def _wire(self):
        self.btn_reload.clicked.connect(self.load_table)
        self.btn_cari.clicked.connect(self.load_table)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.btn_add.clicked.connect(self._add)
        self.btn_upd.clicked.connect(self._upd)
        self.btn_del.clicked.connect(self._del)

    # ================= UTIL =================
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
        self.ed_nomor.clear()
        self.sp_licensor.setValue(0)
        self.sp_licensee.setValue(0)
        self.sp_objek.setValue(0)
        self.cb_dicatat.setChecked(False)
        self.ed_no_catat.clear()
        self.sp_dasar.setValue(0)
        today = QDate.currentDate()
        self.de_mulai.setDate(today)
        self.de_akhir.setDate(today)

    def _date_str(self, de: QDateEdit):
        d = de.date()
        if not d.isValid():
            return None
        return d.toString("yyyy-MM-dd")

    def _collect(self):
        return {
            "nomor": self.ed_nomor.text().strip() or None,
            "licensor_id": int(self.sp_licensor.value()) or None,
            "licensee_id": int(self.sp_licensee.value()) or None,
            "objek_id": int(self.sp_objek.value()) or None,
            "dicatat": 1 if self.cb_dicatat.isChecked() else 0,
            "nomor_pencatatan": self.ed_no_catat.text().strip() or None,
            "dasar_hukum_id": int(self.sp_dasar.value()) or None,
            "tanggal_mulai": self._date_str(self.de_mulai),
            "tanggal_akhir": self._date_str(self.de_akhir),
        }

    def _set_cell(self, row, col, text):
        self.table.setItem(row, col, QTableWidgetItem("" if text is None else str(text)))

    # ================= DATA =================
    def load_table(self):
        q = (self.ed_cari.text() or "").strip()

        # Penting: semua literal '%' harus '%%' biar nggak diembat operator % milik PyMySQL
        sql = """
        SELECT
            id,
            nomor,
            licensor_id,
            licensee_id,
            objek_id,
            CASE WHEN dicatat IN (1,'1',TRUE) THEN 'Ya' ELSE 'Tidak' END AS dicatat_txt,
            nomor_pencatatan,
            dasar_hukum_id,
            DATE_FORMAT(tanggal_mulai, %s) AS tanggal_mulai,
            DATE_FORMAT(tanggal_akhir, %s)  AS tanggal_akhir
        FROM lisensi
        WHERE
            %s = '' OR
            LOWER(nomor) LIKE CONCAT('%%', LOWER(%s), '%%') OR
            CAST(licensor_id  AS CHAR) LIKE CONCAT('%%', %s, '%%') OR
            CAST(licensee_id  AS CHAR) LIKE CONCAT('%%', %s, '%%') OR
            CAST(objek_id     AS CHAR) LIKE CONCAT('%%', %s, '%%')
        ORDER BY id DESC
        """
        params = (
            '%Y-%m-%d', '%Y-%m-%d',
            q, q, q, q, q
        )
        rows = repo_lisensi.raw(sql, params)

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self._set_cell(i, 0, r.get("id"))
            self._set_cell(i, 1, r.get("nomor"))
            self._set_cell(i, 2, r.get("licensor_id"))
            self._set_cell(i, 3, r.get("licensee_id"))
            self._set_cell(i, 4, r.get("objek_id"))
            self._set_cell(i, 5, r.get("dicatat_txt"))
            self._set_cell(i, 6, r.get("nomor_pencatatan"))
            self._set_cell(i, 7, r.get("dasar_hukum_id"))
            self._set_cell(i, 8, r.get("tanggal_mulai"))
            self._set_cell(i, 9, r.get("tanggal_akhir"))

        if self.table.rowCount() > 0:
            self.table.selectRow(0)
        else:
            self._clear_form()

    # ================= TABLE → FORM =================
    def _on_select(self):
        r = self.table.currentRow()
        if r < 0:
            self._clear_form()
            return

        def cell(c):
            it = self.table.item(r, c)
            return "" if it is None else it.text()

        self.ed_nomor.setText(cell(1))
        self.sp_licensor.setValue(int(cell(2) or 0))
        self.sp_licensee.setValue(int(cell(3) or 0))
        self.sp_objek.setValue(int(cell(4) or 0))
        self.cb_dicatat.setChecked((cell(5) or "").lower() == "ya")
        self.ed_no_catat.setText(cell(6))
        self.sp_dasar.setValue(int(cell(7) or 0))

        def set_date_safe(de: QDateEdit, s: str):
            if s:
                de.setDate(QDate.fromString(s, "yyyy-MM-dd"))
            else:
                de.setDate(QDate.currentDate())
        set_date_safe(self.de_mulai, cell(8))
        set_date_safe(self.de_akhir, cell(9))

    # ================= CRUD =================
    def _add(self):
        data = self._collect()
        if not data["nomor"]:
            QMessageBox.warning(self, "Validasi", "Nomor wajib diisi.")
            return
        repo_lisensi.insert(data)
        self.load_table()

    def _upd(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        data = self._collect()
        repo_lisensi.update(pk, data)
        self.load_table()

    def _del(self):
        pk = self._selected_id()
        if not pk:
            QMessageBox.information(self, "Info", "Pilih baris dulu.")
            return
        if QMessageBox.question(self, "Konfirmasi", "Hapus data terpilih?") == QMessageBox.Yes:
            repo_lisensi.delete(pk)
            self.load_table()
