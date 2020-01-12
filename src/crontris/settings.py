"""
This is the config file for fintrist, containing various parameters the user may
wish to modify.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class ConfigObj():
    APP_HOST = os.getenv('COMPUTERNAME')
    DATABASE_NAME = os.getenv('DB_NAME') or 'Fintrist_DB'
    USERNAME = os.getenv('DB_USERNAME')
    PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST') or 'mongodb'
    DB_PORT = int(os.getenv('DB_PORT') or 27017)
    RABBIT_HOST = os.getenv('RABBIT_HOST') or 'rabbitmq'

Config = ConfigObj()
