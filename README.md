# Prodigy Vault 🏦

Prodigy Vault is a sleek, mobile-first personal finance application designed to help students track cash flow, monitor real-world accounts, and build wealth. It moves away from complex budgeting and instead uses a dual-entry ledger system to track money across specific vaults.

## 🚀 Core Features

*   **Custom Financial Vaults:** Automatically provisions 4 specific ledgers:
    *   **Canara Bank:** Main holding vault.
    *   **Airtel Bank:** Daily operations and spending firewall.
    *   **Cash:** Physical pocket money.
    *   **Savings Hub:** Locked wealth for future investments.
*   **Dual-Entry Transfer System:** Move money between vaults (e.g., Canara to Airtel) without altering your total net worth. 
*   **"Pay Yourself First" Engine:** Automatically suggests moving 10% of any newly received income directly into your Savings Hub to encourage consistent investing.
*   **Mobile-Native UI/UX:** Features a fixed bottom navigation bar, slide-up modals (bottom sheets) for quick transactions, and a native-feeling dark/light mode toggle.
*   **Interactive Dashboard:** Real-time net worth calculation, weekly spent vs. saved metrics, and dynamic `Chart.js` cash flow visualizations.
*   **Ledger History:** A dedicated statement page with filters for Income, Expenses, and Transfers.

## 🛠 Tech Stack

*   **Backend:** Python 3, Flask, Werkzeug (Security)
*   **Database:** SQLite (via Flask-SQLAlchemy)
*   **Frontend:** HTML5, Vanilla JavaScript
*   **Styling & UI:** Tailwind CSS (via CDN), FontAwesome
*   **Data Visualization:** Chart.js

## 💻 Local Development Setup

To run Prodigy Vault locally on your machine:

1. **Clone the repository (or download the source code):**
   ```bash
   git clone [https://github.com/yourusername/prodigy-vault.git](https://github.com/yourusername/prodigy-vault.git)
   cd prodigy-vault
Create and activate a virtual environment:

Bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt


4. **Run the application:**
   ```bash
   python app.py
Note: The database (prodigy_vault.db) and necessary tables will be created automatically on the first run.

Access the app: Open your browser and navigate to http://127.0.0.1:5000.

☁️ Deployment (PythonAnywhere)
Prodigy Vault is optimized for zero-cost hosting on PythonAnywhere to preserve the local SQLite database.

Upload the project files to your PythonAnywhere account (e.g., /home/yourusername/prodigy_vault).

Open a Bash console and install requirements:

Bash
pip3 install --user -r requirements.txt
Navigate to the Web tab and create a new Manual configuration app running Python 3.10+.

Edit the WSGI configuration file to point to your app:

Python
import sys
import os

# Update this path to your actual project directory
project_home = '/home/yourusername/prodigy_vault'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set a secure secret key for production
os.environ['SECRET_KEY'] = 'your-super-secret-key-here'

from app import app as application
Reload the web app from the dashboard. Your database tables will initialize automatically on the first request.

🔒 Security Note
Never commit your prodigy_vault.db file or your hardcoded SECRET_KEY to a public repository. Ensure .env and *.db are included in your .gitignore file.