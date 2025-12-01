"""
Train Multilingual Sentiment Model on 1500 Reviews
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import nltk
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def train_model():
    print("🚀 Starting training on 1500 multilingual reviews...")
    
    # 1. Load Data
    data_path = 'ml/data/multilingual_1500_reviews.csv'
    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        return
        
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} reviews")
    
    # 2. Preprocessing
    print("✓ Preprocessing data...")
    stop_words = list(stopwords.words('english'))
    # Add custom stopwords if needed, but for transliterated text standard english stopwords might not be enough
    # However, for this scale, simple TF-IDF is robust enough
    
    vectorizer = TfidfVectorizer(
        max_features=3000,  # Reduced features for smaller dataset to prevent overfitting
        stop_words=stop_words,
        ngram_range=(1, 2)    # Include bigrams for context (e.g., "not good")
    )
    
    X = vectorizer.fit_transform(df['review'])
    y = df['sentiment']
    
    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"✓ Split data: {X_train.shape[0]} training, {X_test.shape[0]} testing samples")
    
    # 4. Define Models
    print("✓ Initializing ensemble models...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    lr = LogisticRegression(max_iter=1000, random_state=42)
    
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('lr', lr)],
        voting='soft'
    )
    
    # 5. Train
    print("✓ Training model...")
    ensemble.fit(X_train, y_train)
    
    # 6. Evaluate
    print("\n📊 Evaluation Results:")
    y_pred = ensemble.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   Test Accuracy: {accuracy*100:.2f}%")
    
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # 7. Save
    model_dir = 'ml/models'
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'sentiment_model_1500.pkl')
    vec_path = os.path.join(model_dir, 'sentiment_model_1500_vectorizer.pkl')
    
    joblib.dump(ensemble, model_path)
    joblib.dump(vectorizer, vec_path)
    print(f"\n💾 Model saved to {model_path}")
    
    # Save results to text file
    with open('ml/multilingual_1500_results.txt', 'w') as f:
        f.write("MULTILINGUAL MODEL (1500 SAMPLES) RESULTS\n")
        f.write("=========================================\n")
        f.write(f"Test Accuracy: {accuracy*100:.2f}%\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_test, y_pred))

if __name__ == "__main__":
    train_model()
