# Secure-Medical-Records-Management-Using-Blockchain

SecureChain is a web application designed to manage electronic health records (EHR) with a focus on security, patient control, and auditability. It uses a Flask backend, a PostgreSQL database for storing patient data, and a custom-built, in-memory blockchain to create an immutable audit log of all critical actions.

This system provides distinct roles (Admin, Doctor, Patient) each with specific capabilities, ensuring that patients have full control over who can access their sensitive medical information.

**Features**

**General**

  * **Role-Based Access Control:** A secure login system that directs Admins, Doctors, and Patients to their respective dashboards.

**Patient Role 🧑‍⚕️**

  * **View Medical Profile:** Patients can view their own medical details, including disease history and prescriptions.
  * **Manage Access:** Patients have full control to **grant** or **revoke** access to their records for specific doctors.
  * **View Access Requests:** See a list of pending access requests from doctors.
  * **Audit Log:** View a complete, immutable access log (powered by the blockchain) showing exactly which doctor accessed their file and when.

**Doctor Role 🩺**

  * **Patient Dashboard:** View a list of all patients they are currently authorized to access.
  * **Request Access:** Can request access to the records of any patient in the system.
  * **View & Update Records:** Once access is granted, doctors can view and update a patient's medical details (e.g., add new prescriptions, update disease details). All updates are logged on the blockchain.

**Admin Role 🖥️**

  * **User Management:** Admins can add new Doctors and Patients to the system, setting up their initial accounts.
  * **System-Wide Audit:** Has access to view the raw data of the entire blockchain, providing a complete audit trail for all actions taken within the application.

**Blockchain & Security**

  * **Immutable Ledger:** Every critical action is recorded as a transaction on a blockchain.

  * **Tracked Actions Include:**
    
      * User Login (login)
      * Access Requests (access\_requested)
      * Access Grants (access\_granted)
      * Access Revocations (access\_revoked)
      * Record Views (file\_accessed)
      * Record Updates (patient\_record\_updated)

  * **Data Integrity:** All updates to patient records are logged with the new data, creating a verifiable history of changes.

**Technical Stack**

  * **Backend:** **Flask**
  * **Database:** **PostgreSQL** (via psycopg2-binary)
  * **ORM:** **Flask-SQLAlchemy**
  * **Authentication:** **Flask-Login**
  * **Migrations:** **Flask-Migrate**
  * **Containerization:** **Docker** & **Docker Compose**
  * **WSGI Server:** **Gunicorn**
  * **Blockchain:** Custom Python implementation (using hashlib and json)

**🚀 Getting Started**

This project is fully containerized with Docker, making setup quick and easy.

**Prerequisites**

  * [Docker](https://www.docker.com/get-started)
  * [Docker Compose](https://docs.docker.com/compose/install/)

**Installation & Running**

1.  **Clone the repository:**
    Bash
    git clone \<your-repository-url\>
    cd \<repository-directory\>

2.  Build and run the services:
    This single command will build the Flask-Gunicorn image, start the PostgreSQL database container, and run the web application.
    Bash
    docker-compose up --build

3.  Database Initialization:
    The Docker container is configured to automatically run the init\_db.py script on startup. This script will:
    
      * Clean up any old data.
      * Standardize all default passwords.
      * Seed the database with default admin, doctor, and patient users.

4.  Access the Application:
    Once the containers are running, you can access the web application in your browser at:
    http://localhost:5000

**Usage (Default Logins)**

The init\_db.py script populates the database with the following users:

| **Role** | **Username** | **Password** |
| :------: | :----------: | :----------: |
| Admin    | admin        | admin123     |
| Doctor   | dr\_smith    | doctor123    |
| Doctor   | dr\_jones    | doctor123    |
| Patient  | patient1     | patient123   |
| Patient  | patient2     | patient123   |

**⚠️ Project Limitations**

This project is a proof-of-concept and has two key limitations:

1.  **In-Memory Blockchain:** The blockchain (blockchain.py) is stored in a Python class instance. **This means the entire audit log is reset every time the web server restarts.** For a production system, this would need to be replaced with a persistent blockchain or a database-backed immutable ledger.
2.  **Simplified Proof-of-Work:** The Proof-of-Work (PoW) is bypassed in the routes (routes.py), where a hardcoded proof (12345) is used to create new blocks. This is for demonstration purposes and does not represent a secure mining process.

**Project File Structure**

.
├── app/
│   ├── \_\_init\_\_.py \# Flask app factory, initializes app and extensions
│   ├── blockchain.py \# Class for the in-memory blockchain ledger
│   ├── models.py \# SQLAlchemy DB models (User, Patient, AccessPermission)
│   ├── routes.py \# All application routes and view logic
│   └── templates/ \# (Your HTML templates would go here)
├── docker-compose.yml \# Orchestrates the web and db services
├── dockerfile \# Build instructions for the Flask app image
├── init\_db.py \# Primary script to clean and seed the database
├── requirements.txt \# Python dependencies
├── cleanup\_db.py \# Helper script for DB cleanup
└── reset\_password.py \# Helper script to reset all passwords


To run the docker file go to the root folder of the project in the terminal and then type the following command:
```docker-compose up --build```

**During the 1st time it shall take some time, since it shall download the images required for running it.**

To delete/remove the containers just use:
```docker-compose down -v```

It deletes all the containers along with volumes created.

