# 🏅 YLY HR Evaluation System

A premium, bilingual (Arabic & English) Human Resources Management & Evaluation platform designed for **YLY (Youth Leading Youth)**. This system allows HR administrators to track member performance, review activity submissions, and provide detailed evaluations through a modern, responsive interface.

---

## ✨ Key Features

### 👨‍💼 Admin Dashboard (The Nerve Center)
- **Card-Based UI/UX**: Overhauled from standard tables to a modern, responsive grid of member cards.
- **Activity Statistics**: Real-time tracking of individual member counts for Meetings, Events, and Tasks.
- **Submission Workflow**: Review pending "Evidence" (screenshots) with easy Approve/Reject actions.
- **Precision Evaluation**: Fine-grained scoring for Hierarchy, Behavior, Group Interaction, and Follower Rapport.
- **Dynamic Settings**: Configure global targets for meetings, events, and tasks directly from the UI.
- **Score Hardening**: Automatic capping of technical and HR scores to prevent data entry errors.

### 👥 Member Dashboard
- **Performance at a Glance**: Visual "Score Badge" and progress indicators.
- **Submission Portal**: Easily submit proof of work (Meetings, Events, Tasks) with screenshots.
- **Bilingual Support**: All activity types are labeled in both Arabic and English (e.g., *اجتماع - Meeting*).
- **Evaluation History**: Comprehensive table showing past grades and performance totals.

### 🛡️ Security & Privacy
- **Draft Workflow**: Evaluations are saved as drafts and only become visible to members when "Published" by an admin.
- **Secure Authentication**: Robust login system powered by Flask-Login and Bcrypt password hashing.
- **Developer Disclaimer**: Integrated footer ensuring the platform is recognized as an unofficial aid for the YLY HR community.

---

## 🛠️ Technology Stack
- **Backend**: Python, Flask, SQLAlchemy (ORM)
- **Database**: SQLite (Instance-based)
- **Frontend**: Vanilla HTML5, Modern CSS3 (CSS Variables, Flex/Grid), JavaScript
- **Localization**: Arabic Reshaper, Python-Bidi
- **Design**: Premium gradients, micro-animations, and responsive layouts.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SeifNady/YLY_HR_Evaluation.git
   cd YLY_HR_Evaluation
   ```
2. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-bcrypt python-dotenv arabic-reshaper python-bidi
   ```

### 3. Run the Application
```bash
python backend/app.py
```
Default Admin Credentials: `admin` / `admin123`

---

## 📝 Developer Note
Developed with ❤️ by **Seif Nady** to assist the HR team in managing the Youth Leading Youth community more efficiently. This project is a personal initiative and is not an official Ministry of Youth and Sports platform.

---


- **Member Dash**: Personal progress tracking.
- **Bilingual UI**: Seamless Arabic/English integration.

---
© 2026 Seif Nady. All rights reserved.
