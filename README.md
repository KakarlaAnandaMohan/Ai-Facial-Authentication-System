# AI Facial Authentication System

An AI-powered facial authentication system that enables secure user registration, login, and identity verification using facial recognition. The project consists of a Python backend with REST APIs and a responsive frontend for user interaction.

---

## Features

* 🔐 User Registration
* 😊 Face Enrollment
* 👤 Facial Authentication Login
* 🛡 Secure Authentication APIs
* 📊 Admin Dashboard
* 📈 User Analytics
* 🗄 SQLite Database Integration
* 🐳 Docker Support
* 🧪 Unit Testing with Pytest
* 🌐 RESTful API Architecture

---

## Project Structure

```
AI-Facial-Authentication-System/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── register.html
│   ├── dashboard.html
│   └── admin.html
│
├── docker-compose.yml
├── walkthrough.md
└── README.md
```

---

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* SQLite
* JWT Authentication
* Pytest

### Frontend

* HTML5
* CSS3
* JavaScript

### DevOps

* Docker
* Docker Compose
* Git
* GitHub

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/KakarlaAnandaMohan/Ai-Facial-Authentication-System.git

cd Ai-Facial-Authentication-System
```

---

### 2. Create a Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
cd backend

pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file inside the `backend` folder.

Example:

```env
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///facial_auth.db
```

---

### 5. Run the Backend

```bash
uvicorn app.main:app --reload
```

Backend URL

```
http://127.0.0.1:8000
```

API Documentation

```
http://127.0.0.1:8000/docs
```

---

### 6. Run the Frontend

Open the `frontend/index.html` file in your browser.

Or serve it using a local HTTP server.

Example:

```bash
python -m http.server 5500
```

---

## Running with Docker

```bash
docker-compose up --build
```

---

## Running Tests

```bash
cd backend

pytest
```

---

## API Modules

* Authentication APIs
* Face Registration APIs
* Face Verification APIs
* User Management APIs
* Admin APIs
* Analytics APIs

---

## Security Features

* JWT Authentication
* Password Hashing
* Secure User Sessions
* Environment Variable Configuration
* API Validation
* Face-based Identity Verification

---

## Future Enhancements

* Face Liveness Detection
* Multi-Factor Authentication (MFA)
* PostgreSQL Support
* Cloud Storage Integration
* Email Verification
* Password Reset
* Role-Based Access Control
* Audit Logging
* CI/CD Pipeline
* Deployment to AWS/Azure

---

## Screenshots

Add screenshots here after running the application.

Example:

```
screenshots/
├── login.png
├── register.png
├── dashboard.png
└── admin.png
```

---

## Author

**Ananda Mohan Kakarla**

GitHub: https://github.com/KakarlaAnandaMohan

---

## License

This project is licensed under the MIT License.

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push your branch

```bash
git push origin feature/new-feature
```

5. Open a Pull Request.

---

## Acknowledgements

This project was developed to demonstrate modern AI-based facial authentication using Python, FastAPI, computer vision concepts, and secure backend development practices.
