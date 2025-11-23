from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QTextEdit, QComboBox, QFormLayout, QHBoxLayout, QVBoxLayout, QPushButton
from mysql.connector import Error

class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Register Pet")

        title = QLabel("Register a Pet for Adoption")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: white; padding: 5px;")

        # Inputs
        self.petIdLE = QLineEdit()
        self.petNameLE = QLineEdit()
        self.speciesLE = QLineEdit()
        self.breedLE = QLineEdit()
        self.ageLE = QLineEdit()
        self.genderLE = QLineEdit()
        self.sizeLE = QLineEdit()
        self.shelterLE = QLineEdit()

        self.statusCombo = QComboBox()
        self.statusCombo.addItems(["Available", "Pending", "Adopted"])

        self.commentsTE = QTextEdit()
        self.commentsTE.setPlaceholderText("Enter any comments or notes about this pet...")
        self.commentsTE.setMaximumHeight(100)

        form = QFormLayout()
        form.addRow("Pet ID:", self.petIdLE)
        form.addRow("Pet Name:", self.petNameLE)
        form.addRow("Species (cat/dog/other):", self.speciesLE)
        form.addRow("Breed:", self.breedLE)
        form.addRow("Age:", self.ageLE)
        form.addRow("Gender:", self.genderLE)
        form.addRow("Size:", self.sizeLE)
        form.addRow("Shelter:", self.shelterLE)
        form.addRow("Status:", self.statusCombo)
        form.addRow("Comments:", self.commentsTE)

        save_btn = QPushButton("Save")
        reset_btn = QPushButton("Reset")
        close_btn = QPushButton("Close")

        save_btn.clicked.connect(self.add_pet)
        reset_btn.clicked.connect(self.reset_fields)
        close_btn.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(close_btn)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        self.setFixedWidth(450)
        self.adjustSize()

    def reset_fields(self):
        self.petIdLE.clear(); self.petNameLE.clear(); self.speciesLE.clear(); self.breedLE.clear()
        self.ageLE.clear(); self.genderLE.clear(); self.sizeLE.clear(); self.shelterLE.clear()
        self.statusCombo.setCurrentIndex(0); self.commentsTE.clear()

    def add_pet(self):
        try:
            petId = int(self.petIdLE.text())
            petName = self.petNameLE.text()
            species = self.speciesLE.text().lower()
            breed = self.breedLE.text()
            age = int(self.ageLE.text())
            gender = self.genderLE.text()
            size = self.sizeLE.text()
            shelter = self.shelterLE.text()
            status = self.statusCombo.currentText()
            comments = self.commentsTE.toPlainText().strip()

            if not petName or not species or not breed:
                print("Error: Name, Species, and Breed are required fields")
                return

            if species == "dog":
                adoptionFee = 250.00
            elif species == "cat":
                adoptionFee = 150.00
            else:
                adoptionFee = 0.00

            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()

                cursor.execute("SELECT petId FROM pets WHERE petId = %s", (petId,))
                existing_pet = cursor.fetchone()

                if existing_pet:
                    cursor.execute("""
                        UPDATE pets 
                        SET petName=%s, species=%s, breed=%s, age=%s, gender=%s,
                            size=%s, shelter=%s, adoptionFee=%s, status=%s, comments=%s
                        WHERE petId=%s
                    """, (petName, species, breed, age, gender, size, shelter, adoptionFee, status, comments, petId))
                    print(f"Pet updated in database: ID={petId}, Name={petName}")
                else:
                    cursor.execute("""
                        INSERT INTO pets (petId, petName, species, breed, age, 
                                         gender, size, shelter, adoptionFee, status, comments) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (petId, petName, species, breed, age, gender, size, shelter, adoptionFee, status, comments))
                    print(f"Pet registered successfully in database: ID={petId}, Name={petName}")

                self.parent_window.connection.commit()
                cursor.close()
                print(f"✓ Pet '{petName}' saved successfully to database!")
            else:
                print("Error: Database connection not available.")
                return

            self.reset_fields()
        except ValueError as ve:
            print(f"Invalid input - ID and age must be numbers: {ve}")
        except Error as e:
            print(f"Database error: {e}")
            if self.parent_window.connection:
                self.parent_window.connection.rollback()
        except Exception as e:
            print(f"Unexpected error: {e}")
