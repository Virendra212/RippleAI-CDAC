from pymongo import MongoClient
import os

def get_database():
   client = MongoClient(os.getenv("MONGO_DB_URL"))
   return client['rippleAI']
  