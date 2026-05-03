Here’s your **clean, copy-pasteable version** (properly formatted for README / GitHub):

---

# 🏦 Prodigy Vault

**Prodigy Vault** is a sleek, mobile-first personal finance application designed to help students track cash flow, monitor real-world accounts, and build wealth. It avoids complex budgeting and instead uses a dual-entry ledger system to track money across specific vaults.

---

## 🚀 Core Features

### 💼 Custom Financial Vaults

Automatically provisions 4 specific ledgers:

* **Canara Bank** → Main holding vault
* **Airtel Bank** → Daily operations and spending firewall
* **Cash** → Physical pocket money
* **Savings Hub** → Locked wealth for future investments

### 🔄 Dual-Entry Transfer System

Move money between vaults (e.g., Canara → Airtel) without altering total net worth.

### 💰 "Pay Yourself First" Engine

Automatically suggests allocating **10% of new income** into the **Savings Hub**.

### 📱 Mobile-Native UI/UX

* Fixed bottom navigation bar
* Slide-up modals (bottom sheets)
* Dark / Light mode toggle

### 📊 Interactive Dashboard

* Real-time net worth calculation
* Weekly spent vs saved metrics
* Dynamic **Chart.js** cash flow visualizations

### 📜 Ledger History

* Full transaction history
* Filters: Income / Expenses / Transfers

---

## 🛠 Tech Stack

**Backend**

* Python 3
* Flask
* Werkzeug (Security)

**Database**

* SQLite (Flask-SQLAlchemy)

**Frontend**

* HTML5
* Vanilla JavaScript

**Styling & UI**

* Tailwind CSS (CDN)
* FontAwesome

**Data Visualization**

* Chart.js

---

## 💻 Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/prodigy-vault.git
cd prodigy-vault
```

### 2. Create & Activate Virtual Environment

**Windows**

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

📌 **Note:**
The database (`prodigy_vault.db`) and tables will be created automatically on first run.

### 5. Access the App

Open your browser:

```
http://127.0.0.1:5000
```

---

## ☁️ Deployment (PythonAnywhere)

### 1. Upload Project Files

Upload to:

```
/home/yourusername/prodigy_vault
```

### 2. Install Dependencies

```bash
pip3 install --user -r requirements.txt
```

### 3. Configure Web App

* Go to **Web Tab**
* Create **Manual Configuration (Python 3.10+)**

### 4. Edit WSGI File

```python
import sys
import os

project_home = '/home/yourusername/prodigy_vault'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set secure key
os.environ['SECRET_KEY'] = 'your-super-secret-key-here'

from app import app as application
```

### 5. Reload Web App

* Reload from dashboard
* Database initializes on first request

---

## 🔒 Security Note

⚠️ Never commit:

* `prodigy_vault.db`
* `SECRET_KEY`

✅ Add to `.gitignore`:

```
.env
*.db
```

---

If you want, I can also:

* Make a **GitHub README badge version**
* Add **screenshots section**
* Or convert this into a **portfolio project page** 🔥
