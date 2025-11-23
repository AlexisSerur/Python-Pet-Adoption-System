# adopt_window.py
from PyQt6.QtCore import Qt, QUrl, QDate
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QComboBox, QFormLayout,
    QHBoxLayout, QVBoxLayout, QPushButton, QTextBrowser, QDateEdit, QScrollArea, QWidget, QCheckBox
)
from mysql.connector import Error
from comments_dialog import PetCommentsDialog

class AdoptWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Adopt a Pet")

        title = QLabel("Adopt a Pet")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: white; padding: 5px;")

        self.speciesLE = QLineEdit(); self.breedLE = QLineEdit(); self.ageLE = QLineEdit()
        self.speciesLE.setPlaceholderText("cat / dog / other")
        self.breedLE.setPlaceholderText("e.g., Husky, Calico")
        self.ageLE.setPlaceholderText("number (years)")

        form = QFormLayout()
        form.addRow("Species:", self.speciesLE)
        form.addRow("Breed:", self.breedLE)
        form.addRow("Age:", self.ageLE)

        btn_search = QPushButton("Search Available")
        btn_reset = QPushButton("Reset")
        btn_close = QPushButton("Close")
        btn_search.clicked.connect(self.adopt_search)
        btn_reset.clicked.connect(self.reset_fields)
        btn_close.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_search)
        btn_layout.addWidget(btn_reset)
        btn_layout.addWidget(btn_close)

        self.results = QTextBrowser()
        self.results.setReadOnly(True)
        self.results.setOpenLinks(False)
        self.results.setOpenExternalLinks(False)
        self.results.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse |
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.results.setHtml("<h1>Available Pets</h1><p>Enter species, breed, or age and click Search.</p>")
        self.results.anchorClicked.connect(self.handle_link_click)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        layout.addWidget(self.results)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        self.setFixedWidth(720)
        self.adjustSize()

    def reset_fields(self):
        self.speciesLE.clear(); self.breedLE.clear(); self.ageLE.clear()
        self.results.setHtml("<h1>Available Pets</h1><p>Enter species, breed, or age and click Search.</p>")

    def adopt_search(self):
        species = self.speciesLE.text().strip().lower()
        breed = self.breedLE.text().strip().lower()
        age_text = self.ageLE.text().strip()
        header = "<h1>Available Pets</h1>"

        where_clauses, params = [], []
        base_where = "status = 'Available'"

        if species:
            where_clauses.append("LOWER(species) LIKE %s")
            params.append(f"%{species}%")
        if breed:
            where_clauses.append("LOWER(breed) LIKE %s")
            params.append(f"%{breed}%")
        if age_text:
            try:
                age_val = int(age_text)
                where_clauses.append("age = %s")
                params.append(age_val)
            except ValueError:
                self.results.setHtml(header + "<p style='color:red;'>Age must be a number.</p>")
                return

        where_sql = f"{base_where}" + ((" AND (" + " OR ".join(where_clauses) + ")") if where_clauses else "")
        sql = f"""
            SELECT petId, petName, species, breed, age, gender, size, shelter, adoptionFee, status, comments
            FROM pets WHERE {where_sql} ORDER BY petId
        """

        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute(sql, tuple(params))
                records = cursor.fetchall()
                cursor.close()

                table = (
                    "<table border='1' cellspacing='0' cellpadding='6' style='width:100%; border-collapse:collapse;'>"
                    "<tr style='background-color:#4CAF50; color:white;'>"
                    "<th>ID</th><th>Name</th><th>Species</th><th>Breed</th><th>Age</th>"
                    "<th>Gender</th><th>Size</th><th>Shelter</th><th>Fee</th><th>View</th><th>Action</th></tr>"
                )
                for r in records:
                    petId, petName, sp, br, ag, g, sz, sh, fee, st, comments = r
                    table += (
                        f"<tr>"
                        f"<td>{petId}</td><td>{petName}</td><td>{sp}</td><td>{br}</td>"
                        f"<td>{ag}</td><td>{g}</td><td>{sz}</td><td>{sh}</td>"
                        f"<td>${fee}</td>"
                        f"<td><a href='view:{petId}'>View</a></td>"
                        f"<td><a href='adopt:{petId}'>Submit Application</a></td>"
                        f"</tr>"
                    )
                table += "</table>"

                if records:
                    self.results.setHtml(header + f"<p><strong>Found {len(records)} available pet(s)</strong></p>{table}")
                else:
                    self.results.setHtml(header + "<p style='color:orange;'>No available pets matched your search.</p>")
            else:
                self.results.setHtml(header + "<p style='color:red;'>No database connection.</p>")
        except Error as e:
            self.results.setHtml(header + f"<p style='color:red;'>Database error: {e}</p>")
        except Exception as e:
            self.results.setHtml(header + f"<p style='color:red;'>Error: {e}</p>")

    def handle_link_click(self, url: QUrl):
        scheme = url.scheme()
        pet_id_str = url.path() or url.toString().split(':', 1)[1]
        try:
            pet_id = int(pet_id_str)
        except ValueError:
            print(f"Bad pet id in URL: {url.toString()}")
            return

        if scheme == 'view':
            self.view_pet_comments(pet_id)
        elif scheme == 'adopt':
            self.open_submit_window(pet_id)

    def view_pet_comments(self, pet_id):
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute("SELECT petName, comments FROM pets WHERE petId = %s", (pet_id,))
                row = cursor.fetchone()
                cursor.close()
                if row:
                    pet_name, comments = row
                    PetCommentsDialog(self.parent_window, pet_id, pet_name, comments).exec()
                else:
                    print(f"Error: Pet ID {pet_id} not found in database")
            else:
                print("Error: No database connection")
        except Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def open_submit_window(self, pet_id):
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute("""
                    SELECT petId, petName, species, breed, age, gender, size, shelter, adoptionFee, status
                    FROM pets WHERE petId = %s
                """, (pet_id,))
                pet_data = cursor.fetchone()
                cursor.close()
                if pet_data:
                    SubmitApplicationWindow(self.parent_window, pet_data).exec()
                    self.adopt_search()
                else:
                    print(f"Error: Pet ID {pet_id} not found in database")
            else:
                print("Error: No database connection")
        except Error as e:
            print(f"Database error in open_submit_window: {e}")
        except Exception as e:
            print(f"Unexpected error in open_submit_window: {e}")

class SubmitApplicationWindow(QDialog):
    def __init__(self, parent=None, pet_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.pet_data = pet_data
        self.setWindowTitle("Submit Adoption Application")

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll_content = QWidget()

        title = QLabel("Submit Adoption Application")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: white; padding: 5px;")

        if pet_data:
            petId, petName, species, breed, age, gender, size, shelter, adoptionFee, status = pet_data
        else:
            petId = petName = species = breed = age = gender = size = shelter = adoptionFee = status = "N/A"

        pet_info_label = QLabel("Pet Information:")
        pet_info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; color: #2986cc;")

        self.petIdLE = QLineEdit(str(petId)); self.petNameLE = QLineEdit(petName)
        self.speciesLE = QLineEdit(species); self.breedLE = QLineEdit(breed)
        self.ageLE = QLineEdit(str(age)); self.genderLE = QLineEdit(gender)
        self.sizeLE = QLineEdit(size); self.shelterLE = QLineEdit(shelter)
        self.adoptionFeeLE = QLineEdit(f"${adoptionFee}"); self.statusLE = QLineEdit(status)
        for field in [self.petIdLE, self.petNameLE, self.speciesLE, self.breedLE, self.ageLE, self.genderLE,
                      self.sizeLE, self.shelterLE, self.adoptionFeeLE, self.statusLE]:
            field.setReadOnly(True)
            field.setStyleSheet("background-color: #000000;")

        form = QFormLayout()
        form.addRow(pet_info_label)
        form.addRow("Pet ID:", self.petIdLE)
        form.addRow("Pet Name:", self.petNameLE)
        form.addRow("Species:", self.speciesLE)
        form.addRow("Breed:", self.breedLE)
        form.addRow("Age:", self.ageLE)
        form.addRow("Gender:", self.genderLE)
        form.addRow("Size:", self.sizeLE)
        form.addRow("Shelter:", self.shelterLE)
        form.addRow("Adoption Fee:", self.adoptionFeeLE)
        form.addRow("Current Status:", self.statusLE)

        adopter_label = QLabel("Your Contact Information:")
        adopter_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #2986cc;")
        self.adopterNameLE = QLineEdit(); self.adopterEmailLE = QLineEdit(); self.adopterPhoneLE = QLineEdit()
        self.adopterNameLE.setPlaceholderText("Your full name")
        self.adopterEmailLE.setPlaceholderText("your.email@example.com")
        self.adopterPhoneLE.setPlaceholderText("555-1234")
        form.addRow(adopter_label)
        form.addRow("Your Name:*", self.adopterNameLE)
        form.addRow("Your Email:*", self.adopterEmailLE)
        form.addRow("Your Phone:*", self.adopterPhoneLE)

        commitment_label = QLabel("Adoption Commitment:")
        commitment_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #2986cc;")
        form.addRow(commitment_label)

        self.ownedPetBeforeCombo = QComboBox(); self.ownedPetBeforeCombo.addItems(["Select...", "Yes", "No"])
        form.addRow("Have you owned a pet before?*", self.ownedPetBeforeCombo)

        self.awareOfNeedsCombo = QComboBox(); self.awareOfNeedsCombo.addItems(["Select...", "Yes", "No"])
        form.addRow("Aware of pet's needs (feeding, vet, grooming)?*", self.awareOfNeedsCombo)

        self.readyForCostsCombo = QComboBox(); self.readyForCostsCombo.addItems(["Select...", "Yes", "No"])
        form.addRow("Ready for costs of pet care?*", self.readyForCostsCombo)

        self.adoptionDateEdit = QDateEdit(); self.adoptionDateEdit.setDate(QDate.currentDate())
        self.adoptionDateEdit.setCalendarPopup(True); self.adoptionDateEdit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Preferred Adoption Date:*", self.adoptionDateEdit)

        self.ownOtherPetsCombo = QComboBox(); self.ownOtherPetsCombo.addItems(["Select...", "Yes", "No"])
        form.addRow("Do you currently own other pets?*", self.ownOtherPetsCombo)

        self.otherPetsTypeLE = QLineEdit(); self.otherPetsTypeLE.setPlaceholderText("e.g., 2 cats, 1 dog (if applicable)")
        form.addRow("If yes, specify type:", self.otherPetsTypeLE)

        self.livingSituationCombo = QComboBox(); self.livingSituationCombo.addItems(["Select...", "House", "Apartment", "Condo", "Other"])
        form.addRow("Do you live in a house or apartment?*", self.livingSituationCombo)

        self.fencedYardCombo = QComboBox(); self.fencedYardCombo.addItems(["Select...", "Yes", "No", "N/A"])
        form.addRow("Do you have a fenced yard? (for dogs)*", self.fencedYardCombo)

        self.primaryCaregiverLE = QLineEdit(); self.primaryCaregiverLE.setPlaceholderText("Name of primary caregiver")
        form.addRow("Who will be the primary caregiver?*", self.primaryCaregiverLE)

        self.questionsNotesTE = QTextEdit(); self.questionsNotesTE.setPlaceholderText("Any questions or notes (optional)")
        self.questionsNotesTE.setMaximumHeight(80)
        form.addRow("Questions/Notes (optional):", self.questionsNotesTE)

        self.certificationCheckbox = QCheckBox(
            "I certify that the above information is true and that \nI understand the responsibilities of pet ownership."
        )
        self.certificationCheckbox.setStyleSheet("margin-top: 10px; font-weight: bold;")
        form.addRow(self.certificationCheckbox)

        submit_btn = QPushButton("Submit Application")
        cancel_btn = QPushButton("Cancel")
        submit_btn.clicked.connect(self.submit_application)
        cancel_btn.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addLayout(form)
        main_layout.addLayout(btn_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)

        scroll_content.setLayout(main_layout)
        scroll.setWidget(scroll_content)

        window_layout = QVBoxLayout()
        window_layout.addWidget(scroll)
        window_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(window_layout)
        self.setFixedSize(600, 700)

    def submit_application(self):
        adopter_name = self.adopterNameLE.text().strip()
        adopter_email = self.adopterEmailLE.text().strip()
        adopter_phone = self.adopterPhoneLE.text().strip()

        owned_before = self.ownedPetBeforeCombo.currentText()
        aware_needs = self.awareOfNeedsCombo.currentText()
        ready_costs = self.readyForCostsCombo.currentText()
        adoption_date = self.adoptionDateEdit.date().toString("yyyy-MM-dd")
        own_other_pets = self.ownOtherPetsCombo.currentText()
        other_pets_type = self.otherPetsTypeLE.text().strip()
        living_situation = self.livingSituationCombo.currentText()
        fenced_yard = self.fencedYardCombo.currentText()
        primary_caregiver = self.primaryCaregiverLE.text().strip()
        questions_notes = self.questionsNotesTE.toPlainText().strip()
        is_certified = self.certificationCheckbox.isChecked()

        if not adopter_name or not adopter_email or not adopter_phone:
            print("Error: Please fill in all contact information (Name, Email, Phone)"); return
        if owned_before == "Select..." or aware_needs == "Select..." or ready_costs == "Select...":
            print("Error: Please answer all pet ownership experience questions"); return
        if own_other_pets == "Select..." or living_situation == "Select..." or fenced_yard == "Select...":
            print("Error: Please answer all living situation questions"); return
        if not primary_caregiver:
            print("Error: Please specify who will be the primary caregiver"); return
        if not is_certified:
            print("Error: You must certify the information"); return

        try:
            pet_id = int(self.petIdLE.text())
            pet_name = self.petNameLE.text()

            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()

                cursor.execute("SELECT status FROM pets WHERE petId = %s", (pet_id,))
                result = cursor.fetchone()

                if not result:
                    print(f"Error: Pet ID {pet_id} not found.")
                elif (result[0] or "").lower() != "available":
                    print(f"Error: Pet ID {pet_id} is no longer available for adoption.")
                else:
                    cursor.execute("""
                        INSERT INTO applications (
                            petId, petName, adopterName, adopterEmail, adopterPhone,
                            ownedBefore, awareNeeds, readyCosts, adoptionDate,
                            ownOtherPets, otherPetsType, livingSituation, fencedYard,
                            primaryCaregiver, notes, appStatus
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Submitted')
                    """, (pet_id, pet_name, adopter_name, adopter_email, adopter_phone, owned_before, aware_needs,
                          ready_costs, adoption_date, own_other_pets, other_pets_type, living_situation, fenced_yard,
                          primary_caregiver, questions_notes))
                    cursor.execute("UPDATE pets SET status = 'Pending' WHERE petId = %s", (pet_id,))
                    self.parent_window.connection.commit()
                    print(f"✓ Application submitted successfully! Updated Pet #{pet_id} to Pending.")
                    self.close()
                cursor.close()
            else:
                print("Error: No database connection.")
        except ValueError:
            print("Error: Invalid Pet ID")
        except Error as e:
            print(f"Database error: {e}")
            if self.parent_window.connection:
                self.parent_window.connection.rollback()
        except Exception as e:
            print(f"Unexpected error: {e}")
