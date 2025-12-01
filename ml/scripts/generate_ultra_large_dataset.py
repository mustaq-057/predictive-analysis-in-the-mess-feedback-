"""
Generate 200,000 Synthetic Mess Food Reviews for Training
Multilingual Dataset: Telugu, Kannada, Punjabi, Hindi, English (Transliterated)
"""

import pandas as pd
import random
import numpy as np

# Common Dishes (across all regions)
DISHES = [
    'biryani', 'dal', 'rice', 'roti', 'paratha', 'idli', 'dosa', 'sambar',
    'chole', 'rajma', 'paneer', 'chicken', 'sabzi', 'upma', 'poha', 'khichdi',
    'curd', 'salad', 'soup', 'dessert', 'mixed veg', 'chapati', 'vada', 'uttapam',
    'pulao', 'curry', 'pickle', 'chutney', 'raita', 'dal makhani', 'butter chicken',
    'palak paneer', 'aloo gobi', 'baingan bharta', 'kadai chicken', 'fish curry',
    'egg curry', 'mushroom masala', 'methi paratha', 'puri', 'bhatura', 'naan',
    'khana', 'food', 'meal', 'breakfast', 'lunch', 'dinner', 'oota', 'bhojanam'
]

MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'subah ka khana', 'raat ka khana', 'dopahar ka khana', 'madyana oota', 'ratri oota']

# --- LANGUAGE VOCABULARIES (Transliterated) ---

# 1. TELUGU
TELUGU_POS = ['bagundi', 'chala bagundi', 'super', 'keka', 'adhurs', 'kirrak', 'baga chesaru', 'ruchi ga undi', 'excellent ga undi']
TELUGU_NEG = ['baledu', 'chala baledu', 'daridram', 'worst ga undi', 'waste', 'chetta', 'asalu baledu', 'ruchi ledu', 'chandalanga undi']

# 2. KANNADA
KANNADA_POS = ['chennagide', 'sakath', 'super agide', 'tumba chennagide', 'ruchi agide', 'bombat', 'keka', 'mast agide']
KANNADA_NEG = ['chennagilla', 'kettadagide', 'thu', 'worst agide', 'ruchi illa', 'waste', 'bekar', 'sari illa']

# 3. PUNJABI
PUNJABI_POS = ['vadiya', 'att', 'sira', 'ghaint', 'swaad', 'bahut vadiya', 'mazza aa gaya', 'changa']
PUNJABI_NEG = ['bekar', 'ganda', 'swaad ni', 'fuddu', 'bekaar', 'maada', 'khatam', 'bakwaas']

# 4. HINDI / HINGLISH
HINDI_POS = ['mast', 'badiya', 'ek number', 'lajawab', 'gazab', 'jhakaas', 'badhiya', 'swadisht', 'zabardast', 'awesome', 'sahi hai']
HINDI_NEG = ['bekaar', 'bakwas', 'ghatiya', 'kharaab', 'chii', 'bekar', 'not good', 'khatam', 'mood kharab', 'waste']

# 5. ENGLISH (Standard & Slang)
ENGLISH_POS = ['amazing', 'excellent', 'delicious', 'tasty', 'great', 'perfect', 'superb', 'fantastic', 'wonderful', 'good', 'nice', 'op', 'osm']
ENGLISH_NEG = ['terrible', 'bad', 'horrible', 'awful', 'disgusting', 'poor', 'pathetic', 'worst', 'tasteless', 'bland', 'gross', 'nasty']

# --- TEMPLATES ---

# Multilingual Templates
# {dish} is the subject, {quality} is the sentiment word
TEMPLATES_POS = [
    # English/General
    "The {dish} was {quality}.",
    "{dish} is {quality}.",
    "Really {quality} {dish}.",
    "Loved the {dish}, it was {quality}.",
    
    # Telugu
    "{dish} {quality}.",          # Biryani bagundi
    "{dish} chala {quality}.",    # Rice chala bagundi
    "Eeroju {dish} {quality}.",   # Eeroju dal super
    "{dish} matram {quality}.",   # Dosa matram keka
    
    # Kannada
    "{dish} {quality}.",          # Idli chennagide
    "{dish} tumba {quality}.",    # Saaru tumba chennagide
    "Ivattu {dish} {quality}.",   # Ivattu palya sakath
    "{dish} full {quality}.",     # Roti full super
    
    # Punjabi
    "{dish} {quality} hai.",      # Paneer vadiya hai
    "{dish} pura {quality} hai.", # Chicken pura att hai
    "aaj {dish} {quality} si.",   # aaj dal ghaint si
    "{dish} {quality} lagya.",    # Roti swaad lagya
    
    # Hindi
    "{dish} {quality} hai.",      # Dal mast hai
    "{dish} bahut {quality} hai.",# Khana bahut badiya hai
    "aaj ka {dish} {quality} tha.",
    "{dish} kha ke maza aa gaya.", # Specific phrase
    
    # Mixed
    "{dish} was {quality} bhai.",
    "{dish} is full {quality}.",
    "{dish} {quality} taste.",
]

TEMPLATES_NEG = [
    # English/General
    "The {dish} was {quality}.",
    "{dish} is {quality}.",
    "Really {quality} {dish}.",
    "Hated the {dish}, it was {quality}.",
    
    # Telugu
    "{dish} {quality}.",          # Biryani baledu
    "{dish} chala {quality}.",    # Rice chala daridram
    "Eeroju {dish} {quality}.",   # Eeroju dal worst
    "{dish} asalu {quality}.",    # Dosa asalu baledu
    
    # Kannada
    "{dish} {quality}.",          # Idli chennagilla
    "{dish} tumba {quality}.",    # Saaru tumba kettadagide
    "Ivattu {dish} {quality}.",   # Ivattu palya thu
    "{dish} full {quality}.",     # Roti full waste
    
    # Punjabi
    "{dish} {quality} hai.",      # Paneer bekar hai
    "{dish} jama {quality} hai.", # Chicken jama ganda hai
    "aaj {dish} {quality} si.",   # aaj dal bekar si
    "{dish} {quality} lagya.",    # Roti ganda lagya
    
    # Hindi
    "{dish} {quality} hai.",      # Dal bakwas hai
    "{dish} bahut {quality} hai.",# Khana bahut ghatiya hai
    "aaj ka {dish} {quality} tha.",
    "{dish} kha ke mood kharab.", # Specific phrase
    
    # Mixed
    "{dish} was {quality} bhai.",
    "{dish} is full {quality}.",
    "{dish} {quality} taste.",
]

def get_random_quality(sentiment):
    """Get a random quality word from any language"""
    lang = random.choice(['telugu', 'kannada', 'punjabi', 'hindi', 'english'])
    
    if sentiment == 'good':
        if lang == 'telugu': return random.choice(TELUGU_POS)
        if lang == 'kannada': return random.choice(KANNADA_POS)
        if lang == 'punjabi': return random.choice(PUNJABI_POS)
        if lang == 'hindi': return random.choice(HINDI_POS)
        return random.choice(ENGLISH_POS)
    else:
        if lang == 'telugu': return random.choice(TELUGU_NEG)
        if lang == 'kannada': return random.choice(KANNADA_NEG)
        if lang == 'punjabi': return random.choice(PUNJABI_NEG)
        if lang == 'hindi': return random.choice(HINDI_NEG)
        return random.choice(ENGLISH_NEG)

def introduce_typos(text):
    """Randomly introduce typos"""
    if random.random() > 0.3: return text
    
    typo_map = {
        'the': 'da', 'is': 'iz', 'was': 'ws', 'very': 'vry', 'good': 'gud',
        'bad': 'bd', 'hai': 'h', 'tha': 'th', 'bhai': 'bro', 'and': 'nd'
    }
    
    words = text.split()
    new_words = []
    for word in words:
        if word.lower() in typo_map and random.random() < 0.5:
            new_words.append(typo_map[word.lower()])
        else:
            new_words.append(word)
    return ' '.join(new_words)

def generate_review(sentiment):
    """Generate a single review"""
    if sentiment == 'good':
        template = random.choice(TEMPLATES_POS)
        quality = get_random_quality('good')
    else:
        template = random.choice(TEMPLATES_NEG)
        quality = get_random_quality('bad')
        
    dish = random.choice(DISHES)
    
    # Construct review
    review = template.format(dish=dish, quality=quality)
    
    # Add typos
    review = introduce_typos(review)
    
    # Random casing
    if random.random() < 0.5:
        review = review.lower()
        
    # Assign rating
    if sentiment == 'good':
        rating = random.choices([4, 5], weights=[30, 70])[0]
    else:
        rating = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        
    return review, rating, sentiment

def generate_dataset(num_samples=200000):
    """Generate balanced multilingual dataset"""
    print(f"🔄 Generating {num_samples:,} Multilingual Mess Reviews...")
    print("   Languages: Telugu, Kannada, Punjabi, Hindi, English\n")
    
    reviews = []
    num_good = num_samples // 2
    num_bad = num_samples - num_good
    
    # Generate good reviews
    print(f"✓ Generating {num_good:,} positive reviews...")
    for i in range(num_good):
        if (i + 1) % 50000 == 0: print(f"  Progress: {i+1:,}/{num_good:,}")
        review, rating, sentiment = generate_review('good')
        reviews.append({'review': review, 'rating': rating, 'sentiment': sentiment})
    
    # Generate bad reviews
    print(f"\n✓ Generating {num_bad:,} negative reviews...")
    for i in range(num_bad):
        if (i + 1) % 50000 == 0: print(f"  Progress: {i+1:,}/{num_bad:,}")
        review, rating, sentiment = generate_review('bad')
        reviews.append({'review': review, 'rating': rating, 'sentiment': sentiment})
    
    # Shuffle
    print("\n✓ Shuffling dataset...")
    random.shuffle(reviews)
    
    df = pd.DataFrame(reviews)
    
    output_file = 'ml/data/ultra_large_reviews.csv'
    print(f"\n💾 Saving to {output_file}...")
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Dataset generation complete!")
    print(f"📊 Statistics:")
    print(f"   Total reviews: {len(df):,}")
    
    print(f"\n📝 Sample Reviews:")
    print(df[['review', 'sentiment']].head(10).to_string())

if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    generate_dataset(200000)
