import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('.env.local')
uri = os.getenv('MONGODB_URI')

try:
    client = MongoClient(uri)
    print("Databases:", client.list_database_names())
    
    
    db_name = 'test' 
    if 'mess-app' in client.list_database_names():
        db_name = 'mess-app'
    
    db = client[db_name]
    print(f"Using database: {db_name}")
    print("Collections:", db.list_collection_names())
    
    count = db.reviews.count_documents({})
    print(f"Reviews count: {count}")
    
    if count > 0:
        print("Sample review:", db.reviews.find_one())
        
except Exception as e:
    print(f"Error: {e}")
