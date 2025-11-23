import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog
)
from mysql.connector import Error

from db import get_connection
from comments_dialog import PetCommentsDialog
from register_window import RegisterWindow
from adopt_window import AdoptWindow
from search_window import SearchWindow
from applicants_window import ApplicantsWindow

class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pet Adoption System")

        # DB
        self.connection = get_connection()

        # Title
        title = QLabel("Pet Adoption System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")

        # Buttons
        btn_register = QPushButton("Register Pet")
        btn_search = QPushButton("Search Pets")
        btn_adopt = QPushButton("Adopt a Pet")
        btn_load_db = QPushButton("Load All Pets from Database")
        btn_applicants = QPushButton("View Applicants")
        btn_exit = QPushButton("Exit")

        btn_register.clicked.connect(self.open_register)
        btn_search.clicked.connect(self.open_search)
        btn_adopt.clicked.connect(self.open_adopt)
        btn_load_db.clicked.connect(self.load_from_database)
        btn_applicants.clicked.connect(self.open_applicants)
        btn_exit.clicked.connect(self.close)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Species", "Breed", "Age",
            "Gender", "Size", "Shelter", "Fee", "Status", "View"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(btn_register)
        layout.addWidget(btn_search)
        layout.addWidget(btn_adopt)
        layout.addWidget(QLabel("Pet Records from Database:"))
        layout.addWidget(self.table)
        layout.addWidget(btn_load_db)
        layout.addWidget(btn_applicants)
        layout.addWidget(btn_exit)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 30, 40, 30)

        container = QWidget(); container.setLayout(layout)
        self.setCentralWidget(container)
        self.setFixedSize(900, 700)

    # --- Navigation ---
    def open_register(self):
        RegisterWindow(self).exec()

    def open_search(self):
        SearchWindow(self).exec()

    def open_adopt(self):
        AdoptWindow(self).exec()

    def open_applicants(self):
        ApplicantsWindow(self).exec()

    # --- Table loading ---
    def load_from_database(self):
        try:
            self.table.setRowCount(0)
            self.table.setSortingEnabled(False)

            if self.connection and self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT petId, petName, species, breed, age, 
                           gender, size, shelter, adoptionFee, status, comments 
                    FROM pets ORDER BY petId
                """)
                records = cursor.fetchall()
                cursor.close()

                self.table.setRowCount(len(records))
                for row_idx, record in enumerate(records):
                    (petId, petName, species, breed, age, gender,
                     size, shelter, adoptionFee, status, comments) = record

                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(petId)))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(str(petName)))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(str(species)))
                    self.table.setItem(row_idx, 3, QTableWidgetItem(str(breed)))
                    self.table.setItem(row_idx, 4, QTableWidgetItem(str(age)))
                    self.table.setItem(row_idx, 5, QTableWidgetItem(str(gender)))
                    self.table.setItem(row_idx, 6, QTableWidgetItem(str(size)))
                    self.table.setItem(row_idx, 7, QTableWidgetItem(str(shelter)))
                    self.table.setItem(row_idx, 8, QTableWidgetItem(str(adoptionFee)))
                    self.table.setItem(row_idx, 9, QTableWidgetItem(str(status)))

                    view_btn = QPushButton("View")
                    view_btn.clicked.connect(lambda checked, pid=petId, pname=petName, comm=comments:
                                             self.view_comments(pid, pname, comm))
                    self.table.setCellWidget(row_idx, 10, view_btn)
            else:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No database connection"))

            self.table.setSortingEnabled(True)
        except Error as e:
            print(f"Database error: {e}")
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Error: {e}"))

    def view_comments(self, pet_id, pet_name, comments):
        dlg = PetCommentsDialog(self, pet_id, pet_name, comments)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_from_database()

    def closeEvent(self, event):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuWindow()
    window.show()
    sys.exit(app.exec())
