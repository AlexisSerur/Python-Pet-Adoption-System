# applicants_window.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QTextEdit, QFormLayout, QScrollArea, QWidget
)
from mysql.connector import Error

class ApplicantsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("View Applicants")

        title = QLabel("Adoption Applications")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: white; padding: 5px;")

        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "App ID", "Pet ID", "Pet Name", "Adopter", "Email", "Phone",
            "Status", "Submitted", "View", "Approve", "Deny"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)

        refresh_btn = QPushButton("Refresh")
        close_btn = QPushButton("Close")
        refresh_btn.clicked.connect(self.load_applications)
        close_btn.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        self.setFixedSize(1100, 650)

        self.load_applications()

    def load_applications(self):
        self.table.setRowCount(0)
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute("""
                    SELECT appId, petId, petName, adopterName, adopterEmail, adopterPhone,
                           appStatus, submittedAt
                    FROM applications
                    ORDER BY appId DESC
                """)
                records = cursor.fetchall()
                cursor.close()

                self.table.setRowCount(len(records))
                for row_idx, record in enumerate(records):
                    appId, petId, petName, adopterName, adopterEmail, adopterPhone, appStatus, submittedAt = record

                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(appId)))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(str(petId)))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(petName))
                    self.table.setItem(row_idx, 3, QTableWidgetItem(adopterName))
                    self.table.setItem(row_idx, 4, QTableWidgetItem(adopterEmail))
                    self.table.setItem(row_idx, 5, QTableWidgetItem(adopterPhone))
                    self.table.setItem(row_idx, 6, QTableWidgetItem(appStatus))
                    self.table.setItem(row_idx, 7, QTableWidgetItem(str(submittedAt)))

                    view_btn = QPushButton("View")
                    view_btn.clicked.connect(lambda checked, a=appId: self.view_application(a))
                    self.table.setCellWidget(row_idx, 8, view_btn)

                    approve_btn = QPushButton("Approve")
                    approve_btn.clicked.connect(lambda checked, a=appId, p=petId: self.approve_application(a, p))
                    self.table.setCellWidget(row_idx, 9, approve_btn)

                    deny_btn = QPushButton("Deny")
                    deny_btn.clicked.connect(lambda checked, a=appId, p=petId: self.deny_application(a, p))
                    self.table.setCellWidget(row_idx, 10, deny_btn)
        except Error as e:
            print(f"Database error loading applications: {e}")
        except Exception as e:
            print(f"Error loading applications: {e}")

    def view_application(self, app_id):
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute("""
                    SELECT appId, petId, petName, adopterName, adopterEmail, adopterPhone,
                           ownedBefore, awareNeeds, readyCosts, adoptionDate,
                           ownOtherPets, otherPetsType, livingSituation, fencedYard,
                           primaryCaregiver, notes, appStatus, submittedAt
                    FROM applications
                    WHERE appId = %s
                """, (app_id,))
                app_data = cursor.fetchone()
                cursor.close()
                if app_data:
                    ApplicationDetailsWindow(self.parent_window, app_data).exec()
                else:
                    print(f"Application {app_id} not found")
        except Error as e:
            print(f"Database error viewing application: {e}")
        except Exception as e:
            print(f"Error viewing application: {e}")

    def approve_application(self, app_id, pet_id):
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute("UPDATE applications SET appStatus = 'Approved' WHERE appId = %s", (app_id,))
                cursor.execute("UPDATE pets SET status = 'Adopted' WHERE petId = %s", (pet_id,))
                self.parent_window.connection.commit()
                cursor.close()
                print(f"✓ Application #{app_id} approved. Pet #{pet_id} status set to Adopted.")
                self.load_applications()
        except Error as e:
            print(f"Database error: {e}")
            if self.parent_window.connection:
                self.parent_window.connection.rollback()

    def deny_application(self, app_id, pet_id):
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute("UPDATE applications SET appStatus = 'Denied' WHERE appId = %s", (app_id,))
                cursor.execute("UPDATE pets SET status = 'Available' WHERE petId = %s", (pet_id,))
                self.parent_window.connection.commit()
                cursor.close()
                print(f"✓ Application #{app_id} denied. Pet #{pet_id} status set back to Available.")
                self.load_applications()
        except Error as e:
            print(f"Database error: {e}")
            if self.parent_window.connection:
                self.parent_window.connection.rollback()

class ApplicationDetailsWindow(QDialog):
    """Read-only view of a single application"""
    def __init__(self, parent=None, app_data=None):
        super().__init__(parent)
        self.setWindowTitle("Application Details")

        (appId, petId, petName, adopterName, adopterEmail, adopterPhone,
         ownedBefore, awareNeeds, readyCosts, adoptionDate,
         ownOtherPets, otherPetsType, livingSituation, fencedYard,
         primaryCaregiver, notes, appStatus, submittedAt) = app_data

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll_content = QWidget()

        title = QLabel(f"Application #{appId} — {adopterName}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: green; padding: 5px;")

        def ro_line(value):
            le = QLineEdit(str(value) if value is not None else "")
            le.setReadOnly(True)
            le.setStyleSheet("background-color: #000000;")
            return le

        form = QFormLayout()

        app_info_label = QLabel("Application Information:")
        app_info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; color: #4CAF50;")
        form.addRow(app_info_label)
        form.addRow("App ID:", ro_line(appId))
        form.addRow("Submitted:", ro_line(submittedAt))
        form.addRow("Status:", ro_line(appStatus))

        pet_info_label = QLabel("Pet Information:")
        pet_info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #4CAF50;")
        form.addRow(pet_info_label)
        form.addRow("Pet ID:", ro_line(petId))
        form.addRow("Pet Name:", ro_line(petName))

        adopter_info_label = QLabel("Adopter Information:")
        adopter_info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #4CAF50;")
        form.addRow(adopter_info_label)
        form.addRow("Name:", ro_line(adopterName))
        form.addRow("Email:", ro_line(adopterEmail))
        form.addRow("Phone:", ro_line(adopterPhone))

        quest_label = QLabel("Adoption Commitment:")
        quest_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #4CAF50;")
        form.addRow(quest_label)
        form.addRow("Owned Before:", ro_line(ownedBefore))
        form.addRow("Aware of Needs:", ro_line(awareNeeds))
        form.addRow("Ready for Costs:", ro_line(readyCosts))
        form.addRow("Preferred Date:", ro_line(adoptionDate))
        form.addRow("Own Other Pets:", ro_line(ownOtherPets))
        form.addRow("Other Pets Type:", ro_line(otherPetsType))
        form.addRow("Living Situation:", ro_line(livingSituation))
        form.addRow("Fenced Yard:", ro_line(fencedYard))
        form.addRow("Primary Caregiver:", ro_line(primaryCaregiver))

        notes_view = QTextEdit(); notes_view.setReadOnly(True)
        notes_view.setPlainText(notes or ""); notes_view.setMaximumHeight(100)
        form.addRow("Notes:", notes_view)

        close_btn = QPushButton("Close"); close_btn.clicked.connect(self.close)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addLayout(form)
        main_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.setContentsMargins(20, 20, 20, 20)

        scroll_content.setLayout(main_layout)
        scroll.setWidget(scroll_content)

        window_layout = QVBoxLayout()
        window_layout.addWidget(scroll)
        window_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(window_layout)
        self.setFixedSize(600, 700)
