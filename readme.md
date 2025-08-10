# System Health Monitor

## Overview

This project is a cross-platform system utility combined with a backend and admin dashboard to monitor and report system health across machines.

---

## Features

### System Utility (Client)
- Collects system health data across macOS, Windows, and Linux.
- Checks disk encryption, OS update status, antivirus presence, and sleep timeout.
- Runs as a background daemon and reports changes to the backend API.

### Backend Server (API + Storage)
- Receives system data from clients securely via HTTP.
- Stores machine status with timestamps.
- Provides APIs for listing and filtering machines.
- CSV export of machine reports (with authentication).

### Admin Dashboard (Frontend)
- Web UI to view all reporting machines.
- Highlights issues with disk encryption, OS updates, antivirus, and sleep timeout.
- Filtering by OS and issue.
- Secure login for admin access.

---

## Technologies Used
- Python (Flask, Flask-RESTful, SQLAlchemy)
- SQLite (Database)
- Bootstrap 5 (Frontend styling)
- JavaScript (Optional for enhancements)

---

## Setup and Run

### Backend
1. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask app:
    ```bash
    python app.py
    ```

4. Access the admin dashboard at:
    ```
    http://localhost:5000/
    ```
    Use admin credentials configured in `app.py`.

### Client Utility
- Cross-platform utility to be installed on client machines (refer to client docs).

---

## Authentication
- Basic HTTP Authentication protects the admin dashboard and CSV export endpoint.

---

## Notes
- The system checks run every 15-60 minutes and only send data on change to reduce resource use.
- Designed for minimal dependencies and ease of deployment.

---


