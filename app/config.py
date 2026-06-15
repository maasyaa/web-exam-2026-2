import os

SECRET_KEY = 'your-secret-key-here'

SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
DEBUG = True

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'media',
    'images'
)