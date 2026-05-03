
# app.py
import os
import uuid
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ---------------------------
# App & DB Configuration
# ---------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'prodigy_vault.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------
# Models
# ---------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    accounts = db.relationship('Account', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'bank', 'digital_wallet', 'cash', 'savings'
    balance = db.Column(db.Float, default=0.0, nullable=False)

    transactions = db.relationship('Transaction', backref='account', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income', 'expense', 'transfer_out', 'transfer_in'
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(200), default='')
    # For transfers: link the paired entries
    transfer_group_id = db.Column(db.String(36), nullable=True)
    related_account_id = db.Column(db.Integer, nullable=True)  # id of the other account in transfer

# ---------------------------
# Helper / Decorator
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or get_current_user() is None:
            session.clear()
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    return db.session.get(User, user_id)

def get_week_range():
    """Return (monday, sunday) for the current week (assuming Monday start)."""
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

# ---------------------------
# Routes: Authentication
# ---------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.flush()  # obtain user.id

        # Auto-create the 4 default vaults
        default_accounts = [
            {'name': 'Canara Bank', 'type': 'bank'},
            {'name': 'Airtel Bank', 'type': 'digital_wallet'},
            {'name': 'Cash', 'type': 'cash'},
            {'name': 'Savings Hub', 'type': 'savings'}
        ]
        for acct in default_accounts:
            db.session.add(Account(user_id=new_user.id, name=acct['name'],
                                   type=acct['type'], balance=0.0))
        db.session.commit()
        flash('Registration successful. Complete onboarding next.', 'success')
        session['user_id'] = new_user.id
        return redirect(url_for('onboarding'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    user = get_current_user()
    accounts = Account.query.filter_by(user_id=user.id).all()
    if request.method == 'POST':
        field_map = {
            'Canara Bank': ['canara_balance'],
            'Airtel Bank': ['airtel_balance'],
            'Cash': ['cash_balance'],
            'Savings Hub': ['savings_balance']
        }
        for account in accounts:
            raw_value = None
            candidate_keys = [f'balance_{account.id}'] + field_map.get(account.name, [])
            for key in candidate_keys:
                if key in request.form:
                    raw_value = request.form.get(key)
                    break
            if raw_value is not None:
                try:
                    account.balance = float(raw_value)
                except (TypeError, ValueError):
                    account.balance = 0.0
        db.session.commit()
        flash('Starting balances saved.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('onboarding.html', accounts=accounts)


@app.route('/api/accounts/initialize', methods=['POST'])
@login_required
def api_initialize_accounts():
    user = get_current_user()
    data = request.get_json() or {}
    accounts_payload = data.get('accounts', [])
    accounts = {account.name: account for account in Account.query.filter_by(user_id=user.id).all()}
    for item in accounts_payload:
        name = (item.get('name') or '').strip()
        if name in accounts:
            try:
                accounts[name].balance = float(item.get('balance', 0.0))
            except (TypeError, ValueError):
                accounts[name].balance = 0.0
    db.session.commit()
    return jsonify({'success': True})

# ---------------------------
# Routes: Pages (Templates expected in /templates)
# ---------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/add')
@login_required
def add_page():
    return redirect(url_for('dashboard') + '#add')

@app.route('/transfer')
@login_required
def transfer_page():
    return redirect(url_for('dashboard') + '#transfer')

@app.route('/profile')
@login_required
def profile_page():
    return redirect(url_for('dashboard'))

@app.route('/statement')
@login_required
def statement():
    return render_template('statement.html')

# ---------------------------
# API Routes (JSON)
# ---------------------------
@app.route('/api/dashboard')
@login_required
def api_dashboard():
    user = get_current_user()
    accounts = Account.query.filter_by(user_id=user.id).all()
    accounts_data = [{'id': a.id, 'name': a.name, 'type': a.type,
                      'balance': round(a.balance, 2)} for a in accounts]

    # Weekly income & expense (current week)
    monday, sunday = get_week_range()
    week_start = datetime.combine(monday, datetime.min.time())
    week_end = datetime.combine(sunday, datetime.max.time())

    income_week = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user.id,
        Transaction.type == 'income',
        Transaction.date >= week_start,
        Transaction.date <= week_end
    ).scalar() or 0.0

    expense_week = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user.id,
        Transaction.type == 'expense',
        Transaction.date >= week_start,
        Transaction.date <= week_end
    ).scalar() or 0.0

    saved_week = income_week - expense_week  # simplistic: saved = income - expenses

    # Recent transactions (last 5)
    recent_txns = Transaction.query.filter_by(user_id=user.id)\
        .order_by(Transaction.date.desc()).limit(5).all()
    tx_list = []
    for t in recent_txns:
        tx_list.append({
            'id': t.id,
            'type': t.type,
            'amount': round(t.amount, 2),
            'date': t.date.isoformat(),
            'description': t.description,
            'account_name': t.account.name,
            'related_account_name': db.session.get(Account, t.related_account_id).name if t.related_account_id else None
        })

    return jsonify({
        'accounts': accounts_data,
        'weekly_income': round(income_week, 2),
        'weekly_expense': round(expense_week, 2),
        'weekly_saved': round(saved_week, 2),
        'recent_transactions': tx_list
    })

@app.route('/api/monthly_summary')
@login_required
def api_monthly_summary():
    user = get_current_user()
    month_ago = datetime.utcnow() - timedelta(days=30)
    income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user.id,
        Transaction.type == 'income',
        Transaction.date >= month_ago
    ).scalar() or 0.0
    expense = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user.id,
        Transaction.type == 'expense',
        Transaction.date >= month_ago
    ).scalar() or 0.0
    savings_account = Account.query.filter_by(user_id=user.id, name='Savings Hub').first()
    savings = 0.0
    if savings_account:
        savings = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.account_id == savings_account.id,
            Transaction.date >= month_ago
        ).scalar() or 0.0
    return jsonify({
        'income': round(income, 2),
        'expense': round(expense, 2),
        'savings': round(savings, 2)
    })

@app.route('/api/accounts')
@login_required
def api_accounts():
    user = get_current_user()
    accounts = Account.query.filter_by(user_id=user.id).all()
    return jsonify([{'id': a.id, 'name': a.name, 'type': a.type,
                     'balance': round(a.balance, 2)} for a in accounts])

@app.route('/api/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    user = get_current_user()
    data = request.get_json() or {}
    account_id = data.get('account_id')
    tx_type = data.get('type')          # 'income' or 'expense'
    amount = data.get('amount')
    description = data.get('description', '')

    # Validate
    if tx_type not in ('income', 'expense'):
        return jsonify({'error': 'Type must be income or expense'}), 400
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({'error': 'Valid positive amount required'}), 400

    account = Account.query.filter_by(id=account_id, user_id=user.id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    if tx_type == 'expense' and account.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400

    # Update balance
    if tx_type == 'income':
        account.balance += amount
    else:
        account.balance -= amount

    txn = Transaction(
        user_id=user.id,
        account_id=account.id,
        type=tx_type,
        amount=amount,
        description=description,
        date=datetime.utcnow()
    )
    db.session.add(txn)
    db.session.commit()

    # Pay Yourself First trigger: every income gets a 10% suggestion.
    pay_yourself_eligible = tx_type == 'income'
    suggested_transfer = round(amount * 0.10, 2) if tx_type == 'income' else 0.0

    return jsonify({
        'id': txn.id,
        'account_balance': round(account.balance, 2),
        'pay_yourself_eligible': pay_yourself_eligible,
        'suggested_transfer': suggested_transfer,
        'suggested_amount': suggested_transfer
    }), 201

@app.route('/api/transfer', methods=['POST'])
@login_required
def transfer():
    user = get_current_user()
    data = request.get_json() or {}
    from_id = data.get('from_account_id')
    to_id = data.get('to_account_id')
    amount = data.get('amount')
    description = data.get('description', 'Transfer')

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({'error': 'Valid positive amount required'}), 400

    if from_id == to_id:
        return jsonify({'error': 'Cannot transfer to the same account'}), 400

    from_account = Account.query.filter_by(id=from_id, user_id=user.id).first()
    to_account = Account.query.filter_by(id=to_id, user_id=user.id).first()

    if not from_account or not to_account:
        return jsonify({'error': 'One or both accounts not found'}), 404

    if from_account.balance < amount:
        return jsonify({'error': 'Insufficient balance in source account'}), 400

    # Perform transfer: two transaction entries, linked by transfer_group_id
    group_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Debit source
    from_account.balance -= amount
    txn_out = Transaction(
        user_id=user.id,
        account_id=from_account.id,
        type='transfer_out',
        amount=amount,
        date=now,
        description=description,
        transfer_group_id=group_id,
        related_account_id=to_account.id
    )
    db.session.add(txn_out)

    # Credit destination
    to_account.balance += amount
    txn_in = Transaction(
        user_id=user.id,
        account_id=to_account.id,
        type='transfer_in',
        amount=amount,
        date=now,
        description=description,
        transfer_group_id=group_id,
        related_account_id=from_account.id
    )
    db.session.add(txn_in)

    db.session.commit()

    return jsonify({
        'success': True,
        'from_balance': round(from_account.balance, 2),
        'to_balance': round(to_account.balance, 2),
        'transfer_group_id': group_id
    }), 201

@app.route('/api/transactions')
@login_required
def get_transactions():
    """Return paginated transaction history (optional)."""
    user = get_current_user()
    tx_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Transaction.query.filter_by(user_id=user.id)
    if tx_type == 'income':
        query = query.filter(Transaction.type == 'income')
    elif tx_type == 'expense':
        query = query.filter(Transaction.type == 'expense')
    elif tx_type == 'transfer':
        query = query.filter(Transaction.type.in_(['transfer_out', 'transfer_in']))
    pagination = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    txns = []
    for t in pagination.items:
        txns.append({
            'id': t.id,
            'account_name': t.account.name,
            'type': t.type,
            'amount': round(t.amount, 2),
            'date': t.date.isoformat(),
            'description': t.description,
            'related_account_name': db.session.get(Account, t.related_account_id).name if t.related_account_id else None,
            'transfer_group_id': t.transfer_group_id
        })
    return jsonify({
        'transactions': txns,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'page': pagination.page,
        'pages': pagination.pages
    })

# ---------------------------
# Run
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist
    app.run(debug=True, host='0.0.0.0', port=5000)
