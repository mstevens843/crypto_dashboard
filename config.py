import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://development@localhost/my_crypto_dashboard'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
