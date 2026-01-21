from flask import Blueprint, render_template, request, session, redirect, url_for, make_response
from app.db import DatabaseManager

# build Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # show Login page while request is GET
    if request.method == 'GET':
        error= ""
        account={}
        return render_template('auth/login.html',error=error,account=account)

    # execute login authentication while request is POST
    if request.method == 'POST':
    # get input data
        account = request.form
        error = ""
        ecnt = 0
        stbl = {"username":"username","password":"password"}
        #error event
        for key,value in account.items():
            if not value:
                ecnt +=1
                error = "ユーザー名またはパスワードを入力してください"
            if ecnt != 0:
                return render_template('auth/login.html',error=error,account=account)
        
        db = DatabaseManager()
        login_user = []
        db.connect()
        if db.connection:
            sql = "SELECT * FROM users WHERE username = %s;"
            params = (account['username'],)
            login_user = db.query(sql,params,True)
            print("login_user",login_user)
    if not login_user or login_user['password']!= account['password']:
        error = "正しいユーザー名またはパスワードを入力してください"
        return render_template('auth/login.html',error=error,account=account)
    
    session['ID'] = login_user['id']
    session['username'] = login_user['username']
    session['role'] = login_user['role']
    return render_template('index.html',username = session.get('username'),role = session.get('role'),ID = session.get('ID'))

@auth_bp.route('/logout')
def logout():
    # Logout event
    # clear session after logout
    session.pop('username', None)
    session.pop('role', None)
    session.pop('cart_json', None)
    session.pop('ID', None)
    return render_template('index.html')
    