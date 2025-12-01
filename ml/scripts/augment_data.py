"""
Advanced Data Augmentation Script for Mess Reviews

Generates extensive variations of reviews to reach 500+ samples.
"""

import pandas as pd
import random
import os

def generate_synthetic_reviews():
    """Generate completely new synthetic reviews"""
    
    templates = [
        "The {food} was {quality_adj} and {temp_adj}.",
        "Really {sentiment_adj} {meal} today. {food} was {quality_adj}.",
        "{sentiment_adj} experience. The {food} was {quality_adj}.",
        "Found the {food} to be {quality_adj} but {temp_adj}.",
        "{meal} was {sentiment_adj}. {food} tasted {quality_adj}.",
        "Very {sentiment_adj} with the {meal}. {food} was {quality_adj}.",
        "The {food} served for {meal} was {quality_adj}.",
        "Absolute {sentiment_adj} {meal}. {food} was {quality_adj}.",
        "{food} quality is {quality_adj}. {sentiment_adj} job.",
        "Not happy with {meal}. {food} was {quality_adj}."
    ]
    
    items = {
        'food': ['dal', 'rice', 'roti', 'sabzi', 'paneer', 'chicken', 'curd', 'salad', 'soup', 'dessert', 'rajma', 'chole', 'biryani', 'idli', 'dosa', 'sambar', 'upma', 'poha', 'paratha', 'khichdi'],
        'meal': ['breakfast', 'lunch', 'dinner', 'meal', 'food'],
    }
    
    adjectives = {
        'good': {
            'quality_adj': ['delicious', 'tasty', 'fresh', 'excellent', 'amazing', 'great', 'flavorful', 'perfect', 'yummy', 'superb', 'authentic', 'rich', 'spicy', 'crispy', 'soft'],
            'temp_adj': ['hot', 'warm', 'piping hot', 'freshly made'],
            'sentiment_adj': ['happy', 'satisfied', 'pleased', 'delighted', 'impressed', 'good', 'great', 'fantastic', 'wonderful']
        },
        'bad': {
            'quality_adj': ['stale', 'bland', 'tasteless', 'bad', 'terrible', 'awful', 'poor', 'horrible', 'disgusting', 'undercooked', 'overcooked', 'burnt', 'salty', 'oily', 'hard'],
            'temp_adj': ['cold', 'lukewarm', 'chilled', 'frozen'],
            'sentiment_adj': ['disappointed', 'unhappy', 'upset', 'frustrated', 'bad', 'terrible', 'horrible', 'poor', 'pathetic']
        }
    }
    
    new_reviews = []
    
    # Generate 200 good reviews
    for _ in range(200):
        template = random.choice(templates)
        food = random.choice(items['food'])
        meal = random.choice(items['meal'])
        
        quality = random.choice(adjectives['good']['quality_adj'])
        temp = random.choice(adjectives['good']['temp_adj'])
        sentiment_adj = random.choice(adjectives['good']['sentiment_adj'])
        
        review = template.format(
            food=food, meal=meal, 
            quality_adj=quality, temp_adj=temp, 
            sentiment_adj=sentiment_adj
        )
        
        new_reviews.append({
            'review': review,
            'rating': random.randint(4, 5),
            'sentiment': 'good'
        })
        
    # Generate 200 bad reviews
    for _ in range(200):
        template = random.choice(templates)
        food = random.choice(items['food'])
        meal = random.choice(items['meal'])
        
        quality = random.choice(adjectives['bad']['quality_adj'])
        temp = random.choice(adjectives['bad']['temp_adj'])
        sentiment_adj = random.choice(adjectives['bad']['sentiment_adj'])
        
        review = template.format(
            food=food, meal=meal, 
            quality_adj=quality, temp_adj=temp, 
            sentiment_adj=sentiment_adj
        )
        
        new_reviews.append({
            'review': review,
            'rating': random.randint(1, 2),
            'sentiment': 'bad'
        })
        
    return new_reviews

def main():
    print("🚀 Starting advanced data generation...")
    
    input_path = 'ml/data/sample_reviews.csv'
    output_path = 'ml/data/augmented_reviews.csv'
    
    # Load original
    if os.path.exists(input_path):
        df = pd.read_csv(input_path)
        original_reviews = df.to_dict('records')
    else:
        original_reviews = []
        
    # Generate synthetic
    synthetic_reviews = generate_synthetic_reviews()
    
    # Combine
    all_reviews = original_reviews + synthetic_reviews
    
    # Create dataframe
    final_df = pd.DataFrame(all_reviews)
    
    # Shuffle
    final_df = final_df.sample(frac=1).reset_index(drop=True)
    
    # Save
    final_df.to_csv(output_path, index=False)
    
    print(f"\n📊 Generation Results:")
    print(f"   - Original: {len(original_reviews)}")
    print(f"   - Synthetic: {len(synthetic_reviews)}")
    print(f"   - Total: {len(final_df)}")
    print(f"\n💾 Saved to {output_path}")

if __name__ == "__main__":
    main()
