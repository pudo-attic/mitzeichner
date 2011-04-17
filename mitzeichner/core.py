from sqlite3 import connect
from flask import Flask
app = Flask('mitzeichner')

_db = None

def db():
    global _db
    if _db is None:
        _db = connect('mitzeichner.db', check_same_thread=False)
    return _db



