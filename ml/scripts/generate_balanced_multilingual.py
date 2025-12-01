"""
Generate Balanced Multilingual Dataset (10k Reviews)
2000 Reviews Per Language (1000 Good, 1000 Bad)
Languages: Telugu, Kannada, Punjabi, Hindi, English
"""

import pandas as pd
import random
import numpy as np
import os

# --- VOCABULARY ---

DISHES = [
    'biryani', 'dal', 'rice', 'roti', 'paratha', 'idli', 'dosa', 'sambar',
    'chole', 'rajma', 'paneer', 'chicken', 'sabzi', 'upma', 'poha', 'khichdi',
    'curd', 'salad', 'soup', 'dessert', 'mixed veg', 'chapati', 'vada', 'uttapam',
    'pulao', 'curry', 'pickle', 'chutney', 'raita', 'dal makhani', 'butter chicken',
    'palak paneer', 'aloo gobi', 'baingan bharta', 'kadai chicken', 'fish curry',
    'egg curry', 'mushroom masala', 'methi paratha', 'puri', 'bhatura', 'naan',
    'khana', 'food', 'meal', 'breakfast', 'lunch', 'dinner', 'oota', 'bhojanam'
]

ENGLISH_SUBJECTS = DISHES + ['experience', 'service', 'mess', 'place', 'quality', 'staff', 'atmosphere', 'vibe']

# Adjectives
ADJECTIVES = {
    'telugu': {
        'good': ['bagundi', 'chala bagundi', 'super', 'keka', 'adhurs', 'kirrak', 'baga chesaru', 'ruchi ga undi', 'excellent ga undi'],
        'bad': ['baledu', 'chala baledu', 'daridram', 'worst ga undi', 'waste', 'chetta', 'asalu baledu', 'ruchi ledu', 'chandalanga undi']
    },
    'kannada': {
        'good': ['chennagide', 'sakath', 'super agide', 'tumba chennagide', 'ruchi agide', 'bombat', 'keka', 'mast agide'],
        'bad': ['chennagilla', 'kettadagide', 'thu', 'worst agide', 'ruchi illa', 'waste', 'bekar', 'sari illa']
    },
    'punjabi': {
        'good': ['vadiya', 'att', 'sira', 'ghaint', 'swaad', 'bahut vadiya', 'mazza aa gaya', 'changa'],
        'bad': ['bekar', 'ganda', 'swaad ni', 'fuddu', 'bekaar', 'maada', 'khatam', 'bakwaas']
    },
    'hindi': {
        'good': ['mast', 'badiya', 'ek number', 'lajawab', 'gazab', 'jhakaas', 'badhiya', 'swadisht', 'zabardast', 'awesome', 'sahi hai'],
        'bad': ['bekaar', 'bakwas', 'ghatiya', 'kharaab', 'chii', 'bekar', 'not good', 'khatam', 'mood kharab', 'waste']
    },
    'english': {
        'good': ['amazing', 'excellent', 'delicious', 'tasty', 'great', 'perfect', 'superb', 'fantastic', 'wonderful', 'good', 'nice', 'op', 'osm', 'lovely', 'brilliant', 'outstanding'],
        'bad': ['terrible', 'bad', 'horrible', 'awful', 'disgusting', 'poor', 'pathetic', 'worst', 'tasteless', 'bland', 'gross', 'nasty', 'unpleasant', 'dreadful']
    }
}

# Templates per language
TEMPLATES = {
    'telugu': {
        'good': [
            "{dish} {quality}.",
            "{dish} chala {quality}.",
            "Eeroju {dish} {quality}.",
            "{dish} matram {quality}.",
            "{dish} tinte {quality} anipinchindi."
        ],
        'bad': [
            "{dish} {quality}.",
            "{dish} chala {quality}.",
            "Eeroju {dish} {quality}.",
            "{dish} asalu {quality}.",
            "{dish} tinte {quality} anipinchindi."
        ]
    },
    'kannada': {
        'good': [
            "{dish} {quality}.",
            "{dish} tumba {quality}.",
            "Ivattu {dish} {quality}.",
            "{dish} full {quality}.",
            "{dish} nodoke {quality}."
        ],
        'bad': [
            "{dish} {quality}.",
            "{dish} tumba {quality}.",
            "Ivattu {dish} {quality}.",
            "{dish} full {quality}.",
            "{dish} nodoke {quality}."
        ]
    },
    'punjabi': {
        'good': [
            "{dish} {quality} hai.",
            "{dish} pura {quality} hai.",
            "aaj {dish} {quality} si.",
            "{dish} {quality} lagya.",
            "{dish} kha ke {quality} feel hoya."
        ],
        'bad': [
            "{dish} {quality} hai.",
            "{dish} jama {quality} hai.",
            "aaj {dish} {quality} si.",
            "{dish} {quality} lagya.",
            "{dish} kha ke {quality} feel hoya."
        ]
    },
    'hindi': {
        'good': [
            "{dish} {quality} hai.",
            "{dish} bahut {quality} hai.",
            "aaj ka {dish} {quality} tha.",
            "{dish} kha ke maza aa gaya.",
            "{dish} ekdum {quality} hai."
        ],
        'bad': [
            "{dish} {quality} hai.",
            "{dish} bahut {quality} hai.",
            "aaj ka {dish} {quality} tha.",
            "{dish} kha ke mood kharab.",
            "{dish} ekdum {quality} hai."
        ]
    },
    'english': {
        'good': [
            "The {dish} was {quality}.",
            "{dish} is {quality}.",
            "Really {quality} {dish}.",
            "Loved the {dish}, it was {quality}.",
            "Such a {quality} {dish}.",
            "{dish} was absolutely {quality}.",
            "I had a {quality} {dish}.",
            "The {dish} tasted {quality}."
        ],
        'bad': [
            "The {dish} was {quality}.",
            "{dish} is {quality}.",
            "Really {quality} {dish}.",
            "Hated the {dish}, it was {quality}.",
            "Such a {quality} {dish}.",
            "{dish} was absolutely {quality}.",
            "I had a {quality} {dish}.",
            "The {dish} tasted {quality}."
        ]
    }
}

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

def generate_reviews_for_language(lang, count):
    """Generate balanced reviews for a specific language"""
    reviews = []
    num_good = count // 2
    num_bad = count - num_good
    
    # Good reviews
    for _ in range(num_good):
        template = random.choice(TEMPLATES[lang]['good'])
        quality = random.choice(ADJECTIVES[lang]['good'])
        dish = random.choice(ENGLISH_SUBJECTS if lang == 'english' else DISHES)
        
        review = template.format(dish=dish, quality=quality)
        review = introduce_typos(review)
        if random.random() < 0.5: review = review.lower()
        
        rating = random.choices([4, 5], weights=[30, 70])[0]
        reviews.append({'review': review, 'rating': rating, 'sentiment': 'good', 'language': lang})
        
    # Bad reviews
    for _ in range(num_bad):
        template = random.choice(TEMPLATES[lang]['bad'])
        quality = random.choice(ADJECTIVES[lang]['bad'])
        dish = random.choice(ENGLISH_SUBJECTS if lang == 'english' else DISHES)
        
        review = template.format(dish=dish, quality=quality)
        review = introduce_typos(review)
        if random.random() < 0.5: review = review.lower()
        
        rating = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        reviews.append({'review': review, 'rating': rating, 'sentiment': 'bad', 'language': lang})
        
    return reviews

def main():
    print("🚀 Generating 100,000 Multilingual Reviews (20,000 per language)...")
    
    all_reviews = []
    languages = ['telugu', 'kannada', 'punjabi', 'hindi', 'english']
    
    for lang in languages:
        print(f"   Generating {lang.capitalize()}...")
        reviews = generate_reviews_for_language(lang, 20000)
        all_reviews.extend(reviews)
        
    # Shuffle
    random.shuffle(all_reviews)
    
    df = pd.DataFrame(all_reviews)
    
    # Save
    output_dir = 'ml/data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'multilingual_100k_reviews.csv')
    
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Saved {len(df)} reviews to {output_path}")
    print("\n📊 Distribution:")
    print(df['language'].value_counts())
    print("\nSentiment:")
    print(df['sentiment'].value_counts())

if __name__ == "__main__":
    main()
