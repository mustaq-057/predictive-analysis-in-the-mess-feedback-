import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pprint

load_dotenv('.env.local')
uri = os.getenv('MONGODB_URI')

client = MongoClient(uri)
try:
    db = client.get_database()
except:
    db = client['test']

# Try both collection names
if 'menuitems' in db.list_collection_names():
    collection = db['menuitems']
elif 'menu_items' in db.list_collection_names():
    collection = db['menu_items']
else:
    print("No menu collection found!")
    exit()

print(f"Connected to database: {db.name}")
print(f"Collection: {collection.name}")

items = list(collection.find({}))
print(f"Found {len(items)} items.")
for item in items:
    print(f"Name: {item.get('name')}, Date: {item.get('date')}, Mess: {item.get('messType')}, Meal: {item.get('mealType')}")
