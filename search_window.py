from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
from mysql.connector import Error
from comments_dialog import PetCommentsDialog

class SearchWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Search Pets")

        title = QLabel("Search Pet Records")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: white; padding: 5px;")

        self.searchLE = QLineEdit()
        self.searchLE.setPlaceholderText("Enter pet ID, name, species, breed, age, or shelter")
        self.searchLE.setStyleSheet("padding:5px;")

        btn_search = QPushButton("Search")
        btn_clear = QPushButton("Clear")
        btn_close = QPushButton("Close")
        btn_search.clicked.connect(self.search_pet)
        btn_clear.clicked.connect(self.clear_fields)
        btn_close.clicked.connect(self.close)

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_search); btn_row.addWidget(btn_clear); btn_row.addWidget(btn_close)

        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Species", "Breed", "Age",
            "Gender", "Size", "Shelter", "Fee", "Status", "Change Status", "View"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.searchLE)
        layout.addLayout(btn_row)
        layout.addWidget(self.table)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        self.setFixedSize(1000, 600)

    def clear_fields(self):
        self.searchLE.clear()
        self.table.setRowCount(0)

    def search_pet(self):
        query = self.searchLE.text().strip().lower()
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                if query == "":
                    cursor.execute("""
                        SELECT petId, petName, species, breed, age, 
                               gender, size, shelter, adoptionFee, status, comments 
                        FROM pets ORDER BY petId
                    """)
                else:
                    search_query = """
                        SELECT petId, petName, species, breed, age, 
                               gender, size, shelter, adoptionFee, status, comments 
                        FROM pets 
                        WHERE LOWER(petName) LIKE %s 
                           OR LOWER(species) LIKE %s 
                           OR LOWER(breed) LIKE %s 
                           OR LOWER(shelter) LIKE %s 
                           OR LOWER(status) LIKE %s
                           OR CAST(petId AS CHAR) LIKE %s
                           OR CAST(age AS CHAR) LIKE %s
                        ORDER BY petId
                    """
                    term = f"%{query}%"
                    cursor.execute(search_query, (term, term, term, term, term, term, term))

                records = cursor.fetchall()
                cursor.close()

                self.table.setRowCount(len(records))
                for row_idx, record in enumerate(records):
                    petId, petName, species, breed, age, gender, size, shelter, adoptionFee, status, comments = record

                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(petId)))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(petName))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(species))
                    self.table.setItem(row_idx, 3, QTableWidgetItem(breed))
                    self.table.setItem(row_idx, 4, QTableWidgetItem(str(age)))
                    self.table.setItem(row_idx, 5, QTableWidgetItem(gender))
                    self.table.setItem(row_idx, 6, QTableWidgetItem(size))
                    self.table.setItem(row_idx, 7, QTableWidgetItem(shelter))
                    self.table.setItem(row_idx, 8, QTableWidgetItem(f"${adoptionFee}"))
                    self.table.setItem(row_idx, 9, QTableWidgetItem(status))

                    status_combo = QComboBox()
                    status_combo.addItems(["Available", "Pending", "Adopted"])
                    status_combo.setCurrentText(status)
                    status_combo.currentTextChanged.connect(
                        lambda new_status, pid=petId, pname=petName: self.change_pet_status(pid, pname, new_status)
                    )
                    self.table.setCellWidget(row_idx, 10, status_combo)

                    view_btn = QPushButton("View")
                    view_btn.clicked.connect(
                        lambda checked, pid=petId, pname=petName, comm=comments: self.view_comments(pid, pname, comm)
                    )
                    self.table.setCellWidget(row_idx, 11, view_btn)

                if not records:
                    self.table.setRowCount(1)
                    self.table.setItem(0, 0, QTableWidgetItem("No pets found"))
            else:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No database connection"))
        except Error as e:
            print(f"Database error: {e}")
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Error: {e}"))
        except Exception as e:
            print(f"Error: {e}")
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Error: {e}"))

    def change_pet_status(self, pet_id, pet_name, new_status):
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute("UPDATE pets SET status = %s WHERE petId = %s", (new_status, pet_id))
                self.parent_window.connection.commit()
                cursor.close()
                print(f"✓ Status updated: Pet '{pet_name}' (ID: {pet_id}) → {new_status}")
            else:
                print("Error: No database connection")
        except Error as e:
            print(f"Database error updating status: {e}")
            if self.parent_window.connection:
                self.parent_window.connection.rollback()
        except Exception as e:
            print(f"Error updating status: {e}")

    def view_comments(self, pet_id, pet_name, comments):
        dialog = PetCommentsDialog(self.parent_window, pet_id, pet_name, comments)
        if dialog.exec():
            self.search_pet()
