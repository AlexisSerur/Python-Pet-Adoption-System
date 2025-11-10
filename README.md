# Pet Adoption System 

A clean, easy-to-use desktop app built with **Python (PyQt6)** and **MySQL** that helps animal shelters manage pets, process adoptions, and keep track of applicants.  

It’s designed to feel simple for staff — register a pet, search or filter, and handle adoptions in just a few clicks.  
Every pet and application is stored safely in a MySQL database, so nothing gets lost.

---

## 💡 What It Does

- **Register Pets** — Add or update pet records, including comments and status (Available / Pending / Adopted).  
- **Search Pets** — Filter by name, species, breed, or shelter. Each row has:
  - A **Change Status** dropdown (updates instantly in the database)
  - A **View** button to open editable comments
-  **Adopt a Pet** — Search available pets, then click:
  - **View** → to see comments, or  
  - **Submit Application** → to fill out the adoption form
- **Applications Dashboard** — Review submitted applications, approve or deny them, and automatically update the pet’s status.
- **Comments Dialog** — Edit notes for each pet anytime.
- **Error Handling** — Safe database updates with proper rollbacks.

---

## Tech Stack

- **Python 3.13**
- **PyQt6**
- **MySQL Server**
- **mysql-connector-python**

Runs smoothly on macOS and Windows.

---

## How to Run It

```bash
# 1. Clone this repo
git clone https://github.com/<your-username>/pet-adoption-system.git
cd pet-adoption-system

# 2. Install dependencies
pip install pyqt6 mysql-connector-python

# 3. Create the database in MySQL 
CREATE DATABASE IF NOT EXISTS PetAdoptionDB;
USE PetAdoptionDB;

CREATE TABLE pets (
  petId INT PRIMARY KEY,
  petName VARCHAR(100) NOT NULL,
  species VARCHAR(50) NOT NULL,
  breed VARCHAR(100) NOT NULL,
  age INT NOT NULL,
  gender VARCHAR(20),
  size VARCHAR(20),
  shelter VARCHAR(100),
  adoptionFee DECIMAL(10,2) DEFAULT 0.00,
  status ENUM('Available','Pending','Adopted') DEFAULT 'Available',
  comments TEXT
);

CREATE TABLE applications (
  appId INT AUTO_INCREMENT PRIMARY KEY,
  petId INT NOT NULL,
  petName VARCHAR(100) NOT NULL,
  adopterName VARCHAR(100) NOT NULL,
  adopterEmail VARCHAR(120) NOT NULL,
  adopterPhone VARCHAR(60) NOT NULL,
  ownedBefore VARCHAR(10) NOT NULL,
  awareNeeds VARCHAR(10) NOT NULL,
  readyCosts VARCHAR(10) NOT NULL,
  adoptionDate DATE NOT NULL,
  ownOtherPets VARCHAR(10) NOT NULL,
  otherPetsType VARCHAR(200),
  livingSituation VARCHAR(30) NOT NULL,
  fencedYard VARCHAR(10) NOT NULL,
  primaryCaregiver VARCHAR(120) NOT NULL,
  notes TEXT,
  appStatus ENUM('Submitted','Approved','Denied') DEFAULT 'Submitted',
  submittedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX (petId),
  INDEX (appStatus)
);

# 4. Run the program
python main.py
