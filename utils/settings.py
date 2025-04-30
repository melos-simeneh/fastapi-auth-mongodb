from decouple import config
from os import path

BASE_DIR = path.dirname(path.dirname(path.realpath(__file__)))

MONGO_URI = config('MONGO_URI')
MONGO_DB_NAME = config('MONGO_DB_NAME')
MONGO_TEST_DB_NAME = config('MONGO_TEST_DB_NAME')

SECRET_KEY = config('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES',cast=int)
