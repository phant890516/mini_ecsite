import os

class Config:
    # Session Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_key_for_py24'
    
    # Database connect setting
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_DATABASE = 'py24_ec_db'