import os
import datetime
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('.env.local')
uri = os.getenv('MONGODB_URI')

print("--- DATABASE CHECK ---")
try:
    client = MongoClient(uri)
    db = client.test if 'test' in client.list_database_names() else client.get_database()
    collection = db['menuitems']
    
    # Check for breakfast items
    query = {'mealType': 'breakfast'}
    items = list(collection.find(query))
    print(f"Found {len(items)} breakfast items in DB.")
    for item in items:
        print(f" - {item['name']} | Mess: {item['messType']} | Date: {item['date']} (Type: {type(item['date'])})")
        
except Exception as e:
    print(f"DB Error: {e}")

print("\n--- API CHECK ---")
try:
    # Construct URL matching the frontend request
    # Date: 2025-11-30 (IST)
    url = "http://localhost:3005/api/menu?date=2025-11-30&mealType=breakfast&messType=North&isAvailable=true"
    print(f"Fetching: {url}")
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    data = response.json()
    print("Response JSON:")
    print(data)
    
    if data.get('success') and data.get('data'):
        print(f"API returned {len(data['data'])} items.")
    else:
        print("API returned NO items.")
        
except Exception as e:
    print(f"API Error: {e}")
