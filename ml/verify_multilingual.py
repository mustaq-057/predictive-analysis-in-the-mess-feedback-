"""
Verification Script for Multilingual Reviews
Tests the production model on Telugu, Kannada, Punjabi, Hindi, and English
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
        text = str(text).lower()
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
    print("🌍 MULTILINGUAL REVIEW VERIFICATION")
    print("=" * 60)
    
    try:
        model = MessSentimentModel.load()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    test_cases = [
        # Telugu
        ("biryani chala bagundi", "good", "Telugu"),
        ("curry asalu baledu", "bad", "Telugu"),
        ("food super undi", "good", "Telugu"),
        ("taste daridram", "bad", "Telugu"),
        
        # Kannada
        ("oota sakath agide", "good", "Kannada"),
        ("saaru chennagilla", "bad", "Kannada"),
        ("idli tumba chennagide", "good", "Kannada"),
        ("palya thu", "bad", "Kannada"),
        
        # Punjabi
        ("paneer vadiya hai", "good", "Punjabi"),
        ("daal bekar si", "bad", "Punjabi"),
        ("chicken att hai", "good", "Punjabi"),
        ("roti ganda lagya", "bad", "Punjabi"),
        
        # Hindi
        ("khana mast tha", "good", "Hindi"),
        ("sabzi bakwas hai", "bad", "Hindi"),
        ("maza aa gaya", "good", "Hindi"),
        ("mood kharab ho gaya", "bad", "Hindi"),
        
        # English
        ("food was amazing", "good", "English"),
        ("terrible taste", "bad", "English")
    ]
    
    correct = 0
    print("\nRunning tests...")
    print("-" * 70)
    print(f"{'Language':<10} | {'Text':<25} | {'Pred':<10} | {'Exp':<10}")
    print("-" * 70)
    
    for text, expected, lang in test_cases:
        sentiment, confidence = model.predict(text)
        is_correct = sentiment == expected
        if is_correct:
            correct += 1
            icon = "✅"
        else:
            icon = "❌"
            
        print(f"{lang:<10} | {text:<25} | {sentiment.upper():<5} {icon} | {expected.upper()}")
        
    accuracy = correct / len(test_cases) * 100
    print("-" * 70)
    print(f"📊 Final Score: {correct}/{len(test_cases)} ({accuracy:.1f}%)")
    
    if accuracy >= 90:
        print("\n✨ PASSED: Model handles all 5 languages well!")
    else:
        print("\n⚠️ WARNING: Model struggled with some languages.")

if __name__ == "__main__":
    main()
