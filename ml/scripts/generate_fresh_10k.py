import pandas as pd
import random
import os

# Fresh vocabulary - completely different from existing datasets
DISHES = [
    'pulao', 'fried rice', 'poori', 'aloo paratha', 'gobi paratha', 'pav bhaji',
    'vada pav', 'bhel puri', 'dhokla', 'kachori', 'samosa', 'jalebi', 'gulab jamun',
    'rasgulla', 'lassi', 'chai', 'coffee', 'omelette', 'boiled egg', 'scrambled egg',
    'momos', 'manchurian', 'cutlet', 'pakoda', 'bhajji', 'bonda', 'medu vada',
    'bajji', 'appam', 'puttu', 'pongal', 'kesari', 'halwa', 'sheera', 'uppit',
    'noodles', 'pasta', 'pizza', 'burger', 'sandwich', 'toast', 'maggi', 'soup',
    'dal fry', 'tadka dal', 'masoor dal', 'moong dal', 'chana dal', 'toor dal'
]

# Language-specific adjectives with fresh vocabulary
ADJECTIVES = {
    'telugu': {
        'good': ['manchi', 'baga tasty', 'full enjoy', 'mast undi', 'superb ga undi', 'perfect ga undi', 'tasty ga undi'],
        'bad': ['taste leka', 'pani pattadu', 'mood off', 'baledu bro', 'disgusting', 'khali waste', 'eat cheyaleka']
    },
    'kannada': {
        'good': ['full sakkath', 'tasty bandu', 'super aithu', 'maja bandide', 'perfect', 'yummy', 'nalla aithu'],
        'bad': ['taste illa bro', 'ella illa', 'kemp agide', 'disgusting aithu', 'bekagilla', 'waste piece', 'mood spoil']
    },
    'punjabi': {
        'good': ['full mast', 'lajawab si', 'daab aa gayi', 'kamaal', 'zabardast si', 'ekdum perfect', 'solid taste'],
        'bad': ['ghatiya si', 'mood kharab ho gayi', 'faltu', 'zahar', 'na khao', 'regret ho reha', 'taste zero']
    },
    'hindi': {
        'good': ['ekdum zabardast', 'full mast', 'bahut tasty', 'lajawab', 'kamaal ka', 'perfect tha', 'maja aa gaya full'],
        'bad': ['bilkul ghatiya', 'bohot kharab', 'paisa barbaad', 'ulti aa gayi', 'khana hi nahi', 'regret', 'bewakoof banaya']
    },
    'english': {
        'good': ['lit', 'fire', 'bussin', 'slaps', 'top tier', 'crazy good', 'absolutely fire', 'no cap good', 'legendary'],
        'bad': ['mid', 'trash', 'disgusting af', 'straight garbage', 'not it', 'L food', 'zero stars', 'ruined my day']
    }
}

# New templates for natural variation
TEMPLATES = {
    'telugu': {
        'good': [
            "{dish} try chesthe {quality}",
            "bro {dish} {quality}",
            "mess lo {dish} {quality} undi",
            "{dish} tini tarvata feel {quality}",
            "ninna {dish} tinte {quality} anipinchindi"
        ],
        'bad': [
            "{dish} {quality} undi bro",
            "mess {dish} {quality}",
            "{dish} try cheyakandi {quality}",
            "{dish} tini tarvata {quality}",
            "seriously {dish} {quality}"
        ]
    },
    'kannada': {
        'good': [
            "{dish} try madi {quality}",
            "bro {dish} {quality} aithu",
            "mess alli {dish} {quality}",
            "{dish} tinda mele {quality} feel aaithu",
            "full {dish} {quality} bro"
        ],
        'bad': [
            "{dish} {quality} guru",
            "mess {dish} full {quality}",
            "{dish} skip maadi {quality}",
            "{dish} tinda mele {quality}",
            "seriously bro {dish} {quality}"
        ]
    },
    'punjabi': {
        'good': [
            "{dish} try karo {quality}",
            "bhai {dish} {quality} hai",
            "mess ch {dish} {quality} si",
            "{dish} khake {quality} feel hoya",
            "yaar {dish} ekdum {quality} si"
        ],
        'bad': [
            "{dish} {quality} hai yaar",
            "mess da {dish} {quality}",
            "{dish} skip karo {quality} hai",
            "{dish} khake {quality} feel",
            "bhai seriously {dish} {quality}"
        ]
    },
    'hindi': {
        'good': [
            "{dish} try karo {quality} hai",
            "bhai {dish} {quality}",
            "mess mein {dish} {quality} tha",
            "{dish} khake {quality} feel aaya",
            "yaar {dish} to ekdum {quality}"
        ],
        'bad': [
            "{dish} {quality} hai bhai",
            "mess ka {dish} {quality}",
            "{dish} mat khao {quality} hai",
            "{dish} khake {quality} feel",
            "bhai sach mein {dish} {quality}"
        ]
    },
    'english': {
        'good': [
            "bro the {dish} was {quality}",
            "{dish} hits different {quality}",
            "mess {dish} is {quality}",
            "tried {dish} and it was {quality}",
            "yo {dish} was straight up {quality}"
        ],
        'bad': [
            "bro {dish} was {quality}",
            "{dish} is straight {quality}",
            "mess {dish} lowkey {quality}",
            "tried {dish} regret {quality}",
            "nah {dish} is {quality}"
        ]
    }
}

def add_natural_variation(text):
    """Add typos and case variation for realism"""
    if random.random() < 0.4:
        text = text.lower()
    if random.random() < 0.2:
        # Common texting shortcuts
        shortcuts = {'the': 'da', 'bro': 'bruh', 'is': 'iz', 'hai': 'h', 'very': 'vry'}
        for old, new in shortcuts.items():
            if old in text and random.random() < 0.4:
                text = text.replace(old, new)
    return text

def generate_reviews(lang, count):
    """Generate balanced reviews for one language"""
    reviews = []
    good_count = count // 2
    bad_count = count - good_count
    
    # Generate good reviews
    for _ in range(good_count):
        template = random.choice(TEMPLATES[lang]['good'])
        quality = random.choice(ADJECTIVES[lang]['good'])
        dish = random.choice(DISHES)
        review = template.format(dish=dish, quality=quality)
        review = add_natural_variation(review)
        rating = random.choices([4, 5], weights=[35, 65])[0]
        reviews.append({
            'review': review,
            'rating': rating,
            'sentiment': 'good',
            'language': lang
        })
    
    # Generate bad reviews
    for _ in range(bad_count):
        template = random.choice(TEMPLATES[lang]['bad'])
        quality = random.choice(ADJECTIVES[lang]['bad'])
        dish = random.choice(DISHES)
        review = template.format(dish=dish, quality=quality)
        review = add_natural_variation(review)
        rating = random.choices([1, 2, 3], weights=[55, 35, 10])[0]
        reviews.append({
            'review': review,
            'rating': rating,
            'sentiment': 'bad',
            'language': lang
        })
    
    return reviews

def main():
    print("🚀 Generating Fresh 50k Dataset (10k per language)...")
    
    languages = ['telugu', 'kannada', 'punjabi', 'hindi', 'english']
    all_reviews = []
    
    # Generate 10,000 per language
    for lang in languages:
        print(f"   Generating {lang.capitalize()}: 10,000 reviews")
        reviews = generate_reviews(lang, 10000)
        all_reviews.extend(reviews)
    
    random.shuffle(all_reviews)
    df = pd.DataFrame(all_reviews)
    
    # Save dataset
    output_dir = 'ml/data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'fresh_50k_reviews.csv')
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Generated {len(df)} reviews")
    print(f"💾 Saved to {output_path}")
    print("\n📊 Distribution:")
    print(f"   Languages: {df['language'].value_counts().to_dict()}")
    print(f"   Sentiments: {df['sentiment'].value_counts().to_dict()}")
    print(f"   Ratings: {df['rating'].value_counts().sort_index().to_dict()}")

if __name__ == "__main__":
    main()
