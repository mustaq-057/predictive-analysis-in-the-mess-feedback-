"""
Production Model Training Script - Train with 5000 Samples

This script trains the final production model with 5000 samples
for maximum accuracy and robustness.
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from datetime import datetime

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class MessSentimentModel:
    """Production sentiment analysis model for mess food reviews"""
    
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        """Clean and preprocess review text"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = word_tokenize(text)
        important_words = {'not', 'no', 'never', 'nothing', 'nowhere', 'neither', 'nobody', 'none'}
        tokens = [word for word in tokens if word not in self.stop_words or word in important_words]
        return ' '.join(tokens)
    
    def train(self, X_train, y_train):
        """Train the production sentiment analysis model"""
        print("🔧 Preprocessing training data...")
        X_train_processed = [self.preprocess_text(text) for text in X_train]
        
        # Feature extraction using TF-IDF
        print("📊 Extracting features using TF-IDF...")
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.85
        )
        X_train_tfidf = self.vectorizer.fit_transform(X_train_processed)
        
        print("🤖 Training ensemble model...")
        
        # Train individual classifiers
        nb_model = MultinomialNB(alpha=0.1)
        nb_model.fit(X_train_tfidf, y_train)
        nb_score = cross_val_score(nb_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ Naive Bayes CV Score: {nb_score:.4f}")
        
        lr_model = LogisticRegression(max_iter=1000, C=1.0)
        lr_model.fit(X_train_tfidf, y_train)
        lr_score = cross_val_score(lr_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ Logistic Regression CV Score: {lr_score:.4f}")
        
        svm_model = SVC(kernel='linear', C=1.0, probability=True)
        svm_model.fit(X_train_tfidf, y_train)
        svm_score = cross_val_score(svm_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ SVM CV Score: {svm_score:.4f}")
        
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf_model.fit(X_train_tfidf, y_train)
        rf_score = cross_val_score(rf_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ Random Forest CV Score: {rf_score:.4f}")
        
        # Create ensemble
        print("🎯 Creating production ensemble model...")
        self.model = VotingClassifier(
            estimators=[
                ('nb', nb_model),
                ('lr', lr_model),
                ('svm', svm_model),
                ('rf', rf_model)
            ],
            voting='soft',
            weights=[1, 1, 2, 1]  # Give more weight to SVM
        )
        self.model.fit(X_train_tfidf, y_train)
        ensemble_score = cross_val_score(self.model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ Ensemble CV Score: {ensemble_score:.4f}")
        
        return ensemble_score
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set"""
        print("\n📈 Evaluating on test set...")
        X_test_processed = [self.preprocess_text(text) for text in X_test]
        X_test_tfidf = self.vectorizer.transform(X_test_processed)
        
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n🎯 Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred))
        print("\n📉 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        return accuracy, y_pred
    
    def save(self, model_path='ml/models', model_name='sentiment_model_production'):
        """Save trained production model"""
        os.makedirs(model_path, exist_ok=True)
        
        model_file = os.path.join(model_path, f'{model_name}.pkl')
        vectorizer_file = os.path.join(model_path, f'{model_name}_vectorizer.pkl')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.vectorizer, vectorizer_file)
        
        print(f"\n💾 Model saved to: {model_file}")
        print(f"💾 Vectorizer saved to: {vectorizer_file}")


def main():
    """Train production model with 5000 samples"""
    print("=" * 80)
    print("🍽️  PRODUCTION MODEL TRAINING - 5000 SAMPLES")
    print("=" * 80)
    
    # Dataset
    data_path = 'ml/data/ultra_large_reviews.csv'
    
    if not os.path.exists(data_path):
        print(f"❌ Data not found at {data_path}")
        return
    
    print(f"\n📂 Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"✓ Total reviews available: {len(df)}")
    
    # Use 5000 for training + 1000 for testing
    total_needed = 6000
    df_sample = df.sample(n=total_needed, random_state=42).reset_index(drop=True)
    
    print(f"  - Good reviews: {(df_sample['sentiment'] == 'good').sum()}")
    print(f"  - Bad reviews: {(df_sample['sentiment'] == 'bad').sum()}")
    
    # Split data
    print(f"\n✂️  Splitting data (5000 train, 1000 test)...")
    X = df_sample['review'].values
    y = df_sample['sentiment'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=5000, test_size=1000, 
        random_state=42, stratify=y
    )
    
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Test samples: {len(X_test)}")
    
    # Train model
    print("\n" + "=" * 80)
    model = MessSentimentModel()
    cv_score = model.train(X_train, y_train)
    
    # Evaluate
    accuracy, predictions = model.evaluate(X_test, y_test)
    
    # Save production model
    print("\n" + "=" * 80)
    print("💾 SAVING PRODUCTION MODEL")
    print("=" * 80)
    model.save(model_name='sentiment_model_production')
    
    # Test on sample reviews
    print("\n" + "=" * 80)
    print("🧪 Testing on sample reviews:")
    print("=" * 80)
    
    test_samples = [
        ("The food was amazing and fresh!", 5),
        ("Terrible meal. Food was cold and tasteless.", 1),
        ("Average food. Nothing special.", 3),
        ("Loved the biryani today. Delicious!", 5),
        ("Food quality is very poor. Not acceptable.", 2),
        ("Excellent breakfast today. Everything was perfect!", 5),
        ("Dal was watery and roti was burnt.", 1)
    ]
    
    for review, rating in test_samples:
        # Simple prediction
        processed = model.preprocess_text(review)
        tfidf = model.vectorizer.transform([processed])
        sentiment = model.model.predict(tfidf)[0]
        confidence = model.model.predict_proba(tfidf)[0].max()
        
        print(f"\nReview: \"{review}\"")
        print(f"Rating: {rating}/5")
        print(f"Predicted: {sentiment.upper()} (confidence: {confidence:.2%})")
    
    # Final summary
    print("\n" + "=" * 80)
    print("✅ PRODUCTION MODEL TRAINING COMPLETE!")
    print("=" * 80)
    print(f"📊 Final Metrics:")
    print(f"   - Training samples: 5000")
    print(f"   - Test samples: 1000")
    print(f"   - Cross-validation score: {cv_score:.4f}")
    print(f"   - Test accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   - Model saved as: sentiment_model_production.pkl")
    print(f"   - Trained at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
