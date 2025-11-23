from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout
from mysql.connector import Error

class PetCommentsDialog(QDialog):
    """Dialog to view and edit pet comments"""
    def __init__(self, parent=None, pet_id=None, pet_name=None, comments=None):
        super().__init__(parent)
        self.parent_window = parent
        self.pet_id = pet_id
        self.pet_name = pet_name
        self.setWindowTitle(f"Pet Comments - {pet_name}")

        title = QLabel(f"Comments for {pet_name} (ID: {pet_id})")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: white; padding: 5px;")

        self.comments_edit = QTextEdit()
        self.comments_edit.setPlainText(comments or "")
        self.comments_edit.setPlaceholderText("Enter comments or notes about this pet...")
        self.comments_edit.setMinimumHeight(200)

        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save_comments)
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.comments_edit)
        layout.addLayout(btn_layout)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        self.setFixedSize(500, 350)

    def save_comments(self):
        new_comments = self.comments_edit.toPlainText().strip()
        try:
            if self.parent_window.connection and self.parent_window.connection.is_connected():
                cursor = self.parent_window.connection.cursor()
                cursor.execute(
                    "UPDATE pets SET comments = %s WHERE petId = %s",
                    (new_comments, self.pet_id)
                )
                self.parent_window.connection.commit()
                cursor.close()
                print(f"✓ Comments updated successfully for pet '{self.pet_name}' (ID: {self.pet_id})")
                self.accept()
            else:
                print("Error: No database connection")
        except Error as e:
            print(f"Database error updating comments: {e}")
            if self.parent_window.connection:
                self.parent_window.connection.rollback()
        except Exception as e:
            print(f"Error updating comments: {e}")
