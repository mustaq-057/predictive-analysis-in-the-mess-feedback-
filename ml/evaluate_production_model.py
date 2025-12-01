"""
Evaluate Production Model Accuracy
Tests the saved production model on a large held-out dataset
"""

import pandas as pd
import joblib
import os
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Ensure NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class MessSentimentModel:
    """Class to load and use the saved model"""
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        # Must match training preprocessing exactly
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = word_tokenize(text)
        important_words = {'not', 'no', 'never', 'nothing', 'nowhere', 'neither', 'nobody', 'none'}
        tokens = [word for word in tokens if word not in self.stop_words or word in important_words]
        return ' '.join(tokens)
    
    def load(self, model_path='ml/models', model_name='sentiment_model_production'):
        model_file = os.path.join(model_path, f'{model_name}.pkl')
        vectorizer_file = os.path.join(model_path, f'{model_name}_vectorizer.pkl')
        
        print(f"Loading model from {model_file}...")
        self.model = joblib.load(model_file)
        self.vectorizer = joblib.load(vectorizer_file)

    def evaluate(self, X_test, y_test):
        print("Preprocessing test data...")
        X_test_processed = [self.preprocess_text(text) for text in X_test]
        X_test_tfidf = self.vectorizer.transform(X_test_processed)
        
        print("Predicting...")
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n🎯 Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred))
        
        print("\n📉 Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        return accuracy

def main():
    print("=" * 80)
    print("📊 EVALUATING PRODUCTION MODEL ACCURACY")
    print("=" * 80)
    
    # Load data
    data_path = 'ml/data/ultra_large_reviews.csv'
    print(f"📂 Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Sample 2000 reviews for testing (using a different random state than training)
    # Training used random_state=42 for sampling 6000 rows.
    # We'll sample 2000 rows with random_state=999 to ensure we get mostly unseen data
    df_test = df.sample(n=2000, random_state=999).reset_index(drop=True)
    
    print(f"✓ Testing on {len(df_test)} random samples")
    print(f"  - Good reviews: {(df_test['sentiment'] == 'good').sum()}")
    print(f"  - Bad reviews: {(df_test['sentiment'] == 'bad').sum()}")
    
    # Evaluate
    model = MessSentimentModel()
    model.load()
    model.evaluate(df_test['review'].values, df_test['sentiment'].values)
    print("=" * 80)

if __name__ == "__main__":
    main()
