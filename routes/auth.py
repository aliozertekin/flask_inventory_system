from flask import Blueprint, request, redirect, render_template, session, url_for, flash
import cx_Oracle

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        dsn = "FREE"  # Oracle SID/TNS alias

        try:
            test_conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
            test_conn.close()

            # Giriş başarılı
            session['user'] = username
            session['password'] = password
            return redirect(url_for('index.index'))

        except cx_Oracle.DatabaseError as e:
            flash('Giriş başarısız: Kullanıcı adı veya şifre yanlış.')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@auth_bp.route('/help')
def help():
    return render_template('help.html')