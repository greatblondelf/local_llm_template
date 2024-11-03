from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')  # For JWT signing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SSL_CERTIFICATE = os.getenv('SSL_CERTIFICATE_PATH')
    SSL_KEY = os.getenv('SSL_KEY_PATH')