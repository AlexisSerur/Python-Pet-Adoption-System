# Python-Pet-Adoption-System
A desktop app for shelters to manage pets, handle adoptions, and track applications. Built with Python 3.13, PyQt6, and MySQL.
Pet Adoption System (PyQt6 + MySQL)
A desktop app for shelters to manage pets, handle adoptions, and track applications.
Built with Python 3.13, PyQt6, and MySQL.
Core flows: Register pets → Search/filter → Click to adopt (QTextBrowser links) → Submit form → Review applicants (approve/deny).
Extra: Inline status changes and editable comments.
# Features
Register Pets: Add/update pets (status + comments saved to DB).
Search: Filter by name/species/breed/age/shelter; per-row Change Status and View buttons.
Adopt: Results shown in QTextBrowser with clickable links:
view:{petId} → open comments dialog
adopt:{petId} → open application dialog
Applicants Dashboard: View, Approve, Deny; auto-updates pet status.
Comments Dialog: View/edit comments on any pet.
Robust DB Ops: Transactions + error handling.
#Tech Stack
Python 3.13 (macOS primary, works on Windows)
PyQt6
mysql-connector-python
MySQL Server (PetAdoptionDB)
