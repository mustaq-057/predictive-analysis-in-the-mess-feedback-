import os
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('.env.local')
uri = os.getenv('MONGODB_URI')

try:
    client = MongoClient(uri)
    # Use 'test' database by default if not specified in URI
    try:
        db = client.get_database()
    except:
        db = client['test']
        
    collection = db['menuitems'] # Mongoose pluralizes 'MenuItem' to 'menuitems' usually, checking...
    
    # Check collection names
    print("Collections:", db.list_collection_names())
    if 'menuitems' not in db.list_collection_names():
        if 'menu_items' in db.list_collection_names():
            collection = db['menu_items']
        else:
            collection = db['menuitems'] # Default to this
            
    # Use IST date to match the user's local time
    ist_offset = datetime.timedelta(hours=5, minutes=30)
    ist_now = datetime.datetime.now(datetime.timezone.utc) + ist_offset
    today = ist_now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)
    
    # We store as UTC midnight for the given IST date to match API query logic
    # The API takes YYYY-MM-DD and creates a UTC range for that day.
    # So if it's Nov 30 IST, we want to store as Nov 30 UTC midnight.
    today = today.replace(tzinfo=None) # Make naive to avoid confusion, or keep aware if DB handles it.
    # Best practice: Store as UTC midnight.
    today = datetime.datetime(today.year, today.month, today.day, tzinfo=datetime.timezone.utc)
    
    # Clear existing items to avoid duplicates and mixed data
    collection.delete_many({})
    print("Cleared existing menu items.")

    menu_items = [
        # North Mess
        {
            "name": "Sunday Special Chicken Biryani",
            "messType": "North",
            "mealType": "lunch",
            "description": "Spicy hyderabadi biryani",
            "date": today,
            "isAvailable": True
        },
        {
            "name": "Paneer Butter Masala",
            "messType": "North",
            "mealType": "lunch",
            "description": "Rich creamy gravy",
            "date": today,
            "isAvailable": True
        },
        {
            "name": "Butter Naan",
            "messType": "North",
            "mealType": "lunch",
            "description": "Soft naan",
            "date": today,
            "isAvailable": True
        },
        
        # South Mess
        {
            "name": "Hyderabadi Chicken Dum Biryani",
            "messType": "South",
            "mealType": "lunch",
            "description": "Authentic style",
            "date": today,
            "isAvailable": True
        },
        {
            "name": "Gongura Mutton",
            "messType": "South",
            "mealType": "lunch",
            "description": "Spicy mutton curry",
            "date": today,
            "isAvailable": True
        },
        {
            "name": "Curd Rice",
            "messType": "South",
            "mealType": "lunch",
            "description": "Cooling curd rice",
            "date": today,
            "isAvailable": True
        },

        # Breakfast Items
        {
            "name": "Aloo Paratha",
            "messType": "North",
            "mealType": "breakfast",
            "description": "Stuffed paratha",
            "date": today,
            "isAvailable": True
        },
        {
            "name": "Masala Dosa",
            "messType": "South",
            "mealType": "breakfast",
            "description": "Crispy dosa",
            "date": today,
            "isAvailable": True
        }
    ]
    
    # Insert
    result = collection.insert_many(menu_items)
    print(f"Inserted {len(result.inserted_ids)} menu items for today ({today.date()})")
    
except Exception as e:
    print(f"Error: {e}")
