from decouple import config
from os import path

BASE_DIR = path.dirname(path.dirname(path.realpath(__file__)))

MONGO_URI = config('MONGO_URI')