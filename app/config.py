import os

class Config:
    SECRET_KEY = 'dev-secret-key-change-in-production'

    # Datos fijos de Railway (conexión directa para prueba)
    DB_HOST = 'centerbeam.proxy.rlwy.net'
    DB_PORT = '10485'
    DB_USER = 'root'
    DB_PASSWORD = 'szMZkSJLZRTVbGaVOiyMyzfXRESrROuB'   # tu contraseña exacta
    DB_NAME = 'railway'

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False