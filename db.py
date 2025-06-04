# db.py
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['Dream_house_Architecture']
users_collection = db['users']
designs_collection = db['design']