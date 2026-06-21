# 🚨 Incident Management Center

**Modern web application for registering and handling information security incidents.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

## ✨ Features

- **Incident registration** with automatic priority calculation (urgency × impact matrix)
- **Smart incident queue** with advanced filters and search
- **Detailed incident card** + full change history (audit log)
- **Beautiful dashboard statistics** with interactive pie chart
- **Dark / Light mode** support
- **Modern, responsive and clean UI** (glassmorphism + gradients)
- **One-click test data seeding** (25 realistic incidents)

## 🖼️ Screenshots

<img width="1025" height="2568" alt="127 0 0 1_5000_" src="https://github.com/user-attachments/assets/3cbbdb2c-427b-49fc-9a84-707b8dfacb8b" />
<img width="1025" height="2520" alt="127 0 0 1_5000_ (2)" src="https://github.com/user-attachments/assets/64e16209-9b60-41c8-9b67-aa6878fb2a19" />
<img width="1025" height="1440" alt="127 0 0 1_5000_incident_102" src="https://github.com/user-attachments/assets/39811eee-8e33-4ff4-87ec-d5c4a7648c88" />

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/CorvusDemon/incident_app.git
cd incident_app
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🛠️ Tech Stack

- **Backend**: Flask + SQLite3
- **Frontend**: HTML5, CSS3 (modern custom design), Jinja2
- **Key Features**: Priority matrix, audit trail, responsive design, flash notifications

## 📁 Project Structure

```
incident_app/
├── app.py                    # Main application logic
├── requirements.txt
├── templates/
│   ├── index.html            # Main page + registration form
│   └── incident.html         # Incident detail page
├── static/
│   └── style.css             # Modern UI + dark/light mode
└── incidents.db              # Database (do not commit in production)
```

## 🎯 Highlights

This project demonstrates:

- Full CRUD operations with SQLite
- Business logic for incident prioritization (highly valued in SOC / Cybersecurity)
- Clean, modern and user-friendly interface
- Audit logging and data visualization
- Professional Flask + Jinja2 development skills

