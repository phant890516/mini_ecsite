import mysql.connector
from flask import current_app

class DatabaseManager:
    def __init__(self):
        #use paramaters from current_app.config
        self.host = current_app.config['DB_HOST']
        self.user = current_app.config['DB_USER']
        self.passwd = current_app.config['DB_PASSWORD']
        self.db = current_app.config['DB_DATABASE']
        self.connection = None
        self.cursor = None

    def connect(self):
        # connect to mysql.connector , setting connection and cursor
        try:
            self.connection = mysql.connector.connect(
                host = self.host,
                user = self.user,
                passwd = self.passwd,
                db = self.db
            )
            self.cursor = self.connection.cursor(dictionary = True)
            print("データベースに接続しました。")
        except mysql.connector.Error as err:
            print(f'接続エラー:{err}')

    def disconnect(self):
        # shup cursor and connection down
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def query(self, sql, params=None, fetch_one=False):
        # Data Operations setting 'fetch'  
        if self.cursor is None:
                return None
            
        if fetch_one == False:        
            try:
                self.cursor.execute(sql,params or())
                return self.cursor.fetchall()
            except mysql.connector.Error as err:
                print(f'クエリエラ:{err}')
                return None
        else:
            try:
                self.cursor.execute(sql,params or())
                return self.cursor.fetchone()
            except mysql.connector.Error as err:
                print(f'クエリエラ:{err}')
                return None
        
    def execute(self, sql, params=None):
        # Data Operations setting 'others'
        if self.cursor is None:
            return False
        try:
            self.cursor.execute(sql,params or())
            self.connection.commit()
            print(f'クエリを実行し、コミットしました。')
            return True
        except mysql.connector.Error as err:
            print(f'クエリエラ:{err}')
            self.connection.rollback()
            return False