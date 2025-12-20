from flask import Blueprint, render_template, request, redirect, session, url_for

auth_bp = Blueprint('auth', __name__)
USERS = {
    'translator1': {'role': 'translator'},
    'editor1': {'role': 'editor'},
    'admin1': {'role': 'admin'}
}

@auth_bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('translation.translate'))
    else:
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username in USERS:
            session['user'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('translation.dashboard'))
        else:
            return render_template('login.html', error="User not found")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))