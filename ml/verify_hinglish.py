"""
Verification Script for Hinglish & Messy Reviews
Tests the production model on specific edge cases
"""

import joblib
import os
import sys
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Ensure NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class MessSentimentModel:
    """Minimal class for loading the model"""
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = word_tokenize(text)
        important_words = {'not', 'no', 'never', 'nothing', 'nowhere', 'neither', 'nobody', 'none'}
        tokens = [word for word in tokens if word not in self.stop_words or word in important_words]
        return ' '.join(tokens)
    
    @staticmethod
    def load(model_path='ml/models', model_name='sentiment_model_production'):
        model_file = os.path.join(model_path, f'{model_name}.pkl')
        vectorizer_file = os.path.join(model_path, f'{model_name}_vectorizer.pkl')
        
        instance = MessSentimentModel()
        instance.model = joblib.load(model_file)
        instance.vectorizer = joblib.load(vectorizer_file)
        return instance
    
    def predict(self, text):
        processed = self.preprocess_text(text)
        tfidf = self.vectorizer.transform([processed])
        sentiment = self.model.predict(tfidf)[0]
        confidence = self.model.predict_proba(tfidf)[0].max()
        return sentiment, confidence

def main():
    print("=" * 60)
    print("🧪 HINGLISH & MESSY REVIEW VERIFICATION")
    print("=" * 60)
    
    try:
        model = MessSentimentModel.load()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    test_cases = [
        # Hinglish Positive
        ("aaj ka khana badiya tha", "good"),
        ("paneer mast hai bhai", "good"),
        ("ek number biryani", "good"),
        ("maza aa gaya kha ke", "good"),
        
        # Hinglish Negative
        ("bilkul bekaar taste", "bad"),
        ("khana thanda tha", "bad"),
        ("ghatiya quality food", "bad"),
        ("mood kharab ho gaya", "bad"),
        
        # Typos Positive
        ("fud ws vry gud", "good"),
        ("amzing taste", "good"),
        ("luv da chiken", "good"),
        
        # Typos Negative
        ("terible srvice", "bad"),
        ("not gud at all", "bad"),
        ("vry bad exprience", "bad"),
        
        # Broken English
        ("rice not cooked well", "bad"),
        ("very bad quality", "bad"),
        ("food good", "good"),
        ("nice meal", "good")
    ]
    
    correct = 0
    print("\nRunning tests...")
    print("-" * 60)
    
    for text, expected in test_cases:
        sentiment, confidence = model.predict(text)
        is_correct = sentiment == expected
        if is_correct:
            correct += 1
            icon = "✅"
        else:
            icon = "❌"
            
        print(f"{icon} Text: \"{text}\"")
        print(f"   Pred: {sentiment.upper()} ({confidence:.1%}) | Exp: {expected.upper()}")
        print("-" * 60)
        
    accuracy = correct / len(test_cases) * 100
    print(f"\n📊 Final Score: {correct}/{len(test_cases)} ({accuracy:.1f}%)")
    
    if accuracy >= 90:
        print("\n✨ PASSED: Model handles Hinglish and messy text well!")
    else:
        print("\n⚠️ WARNING: Model struggled with some examples.")

if __name__ == "__main__":
    main()
