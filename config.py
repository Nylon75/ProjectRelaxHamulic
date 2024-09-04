import os

class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'Relax.Hamulic@gmail.com'
    MAIL_PASSWORD = 'tcaornolambznhkb'
    MAIL_DEFAULT_SENDER = 'Relax.Hamulic@gmail.com'
    
    UPLOAD_FOLDER = 'static/uploads'