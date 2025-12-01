"""
Sentiment Analysis Model Training Script for Mess Food Reviews

This script trains a machine learning model to classify mess food reviews 
as 'good' or 'bad' with high accuracy.
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
    """Custom sentiment analysis model for mess food reviews"""
    
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        """Clean and preprocess review text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenization
        tokens = word_tokenize(text)
        
        # Remove stopwords (but keep important negative words)
        important_words = {'not', 'no', 'never', 'nothing', 'nowhere', 'neither', 'nobody', 'none'}
        tokens = [word for word in tokens if word not in self.stop_words or word in important_words]
        
        # Join back
        return ' '.join(tokens)
    
    def train(self, X_train, y_train):
        """Train the sentiment analysis model"""
        print("🔧 Preprocessing training data...")
        X_train_processed = [self.preprocess_text(text) for text in X_train]
        
        # Feature extraction using TF-IDF
        print("📊 Extracting features using TF-IDF...")
        self.vectorizer = TfidfVectorizer(
            max_features=2000,  # Increased features
            ngram_range=(1, 3),  # Unigrams, bigrams, and trigrams for better context
            min_df=2,
            max_df=0.85
        )
        X_train_tfidf = self.vectorizer.fit_transform(X_train_processed)
        
        # Try multiple classifiers
        print("🤖 Training multiple classifiers...")
        
        # 1. Naive Bayes
        nb_model = MultinomialNB(alpha=0.1)
        nb_model.fit(X_train_tfidf, y_train)
        nb_score = cross_val_score(nb_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ Naive Bayes CV Score: {nb_score:.4f}")
        
        # 2. Logistic Regression
        lr_model = LogisticRegression(max_iter=1000, C=1.0)
        lr_model.fit(X_train_tfidf, y_train)
        lr_score = cross_val_score(lr_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ Logistic Regression CV Score: {lr_score:.4f}")
        
        # 3. SVM
        svm_model = SVC(kernel='linear', C=1.0, probability=True)
        svm_model.fit(X_train_tfidf, y_train)
        svm_score = cross_val_score(svm_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ SVM CV Score: {svm_score:.4f}")
        
        # 4. Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf_model.fit(X_train_tfidf, y_train)
        rf_score = cross_val_score(rf_model, X_train_tfidf, y_train, cv=5).mean()
        print(f"   ✓ Random Forest CV Score: {rf_score:.4f}")
        
        # 5. Ensemble (Voting Classifier)
        print("🎯 Creating ensemble model with GridSearch...")
        
        # Optimize individual classifiers first
        from sklearn.model_selection import GridSearchCV
        
        # Optimize SVM
        svm_params = {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']}
        svm_grid = GridSearchCV(SVC(probability=True), svm_params, cv=3)
        svm_grid.fit(X_train_tfidf, y_train)
        best_svm = svm_grid.best_estimator_
        print(f"   ✓ Best SVM params: {svm_grid.best_params_}")
        
        # Optimize Random Forest
        rf_params = {'n_estimators': [50, 100, 200], 'max_depth': [10, 20, None]}
        rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=3)
        rf_grid.fit(X_train_tfidf, y_train)
        best_rf = rf_grid.best_estimator_
        print(f"   ✓ Best RF params: {rf_grid.best_params_}")
        
        self.model = VotingClassifier(
            estimators=[
                ('nb', nb_model),
                ('lr', lr_model),
                ('svm', best_svm),
                ('rf', best_rf)
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
        
        return accuracy
    
    def predict(self, text, rating=None):
        """Predict sentiment for a single review"""
        if not self.model or not self.vectorizer:
            raise ValueError("Model not trained yet!")
        
        # Preprocess
        processed = self.preprocess_text(text)
        
        # Transform
        tfidf = self.vectorizer.transform([processed])
        
        # Predict
        sentiment = self.model.predict(tfidf)[0]
        confidence = self.model.predict_proba(tfidf)[0].max()
        
        # If rating is provided, use it to validate/adjust
        if rating is not None:
            rating_based = 'good' if rating >= 3 else 'bad'
            # If confidence is low and rating disagrees, trust the rating
            if confidence < 0.6 and sentiment != rating_based:
                sentiment = rating_based
                confidence = 0.7  # Medium confidence
        
        return sentiment, confidence
    
    def save(self, model_path='ml/models', model_name='sentiment_model'):
        """Save trained model and vectorizer"""
        os.makedirs(model_path, exist_ok=True)
        
        model_file = os.path.join(model_path, f'{model_name}.pkl')
        vectorizer_file = os.path.join(model_path, f'{model_name}_vectorizer.pkl')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.vectorizer, vectorizer_file)
        
        print(f"\n💾 Model saved to: {model_file}")
        print(f"💾 Vectorizer saved to: {vectorizer_file}")
    
    @staticmethod
    def load(model_path='ml/models', model_name='sentiment_model'):
        """Load trained model and vectorizer"""
        model_file = os.path.join(model_path, f'{model_name}.pkl')
        vectorizer_file = os.path.join(model_path, f'{model_name}_vectorizer.pkl')
        
        instance = MessSentimentModel()
        instance.model = joblib.load(model_file)
        instance.vectorizer = joblib.load(vectorizer_file)
        
        return instance


def main():
    """Main training pipeline"""
    print("=" * 70)
    print("🍽️  MESS FOOD REVIEW SENTIMENT ANALYSIS MODEL TRAINING")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading training data...")
    data_path = 'ml/data/augmented_reviews.csv'
    
    if not os.path.exists(data_path):
        print(f"⚠️ Augmented data not found, falling back to sample data...")
        data_path = 'ml/data/sample_reviews.csv'
        print(f"❌ Error: Data file not found at {data_path}")
        return
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} reviews")
    print(f"  - Good reviews: {(df['sentiment'] == 'good').sum()}")
    print(f"  - Bad reviews: {(df['sentiment'] == 'bad').sum()}")
    
    # Split data
    print("\n✂️  Splitting data (80% train, 20% test)...")
    X = df['review'].values
    y = df['sentiment'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Test samples: {len(X_test)}")
    
    # Train model
    print("\n" + "=" * 70)
    model = MessSentimentModel()
    cv_score = model.train(X_train, y_train)
    
    # Evaluate
    test_accuracy = model.evaluate(X_test, y_test)
    
    # Save model
    print("\n" + "=" * 70)
    model.save()
    
    # Test on sample reviews
    print("\n" + "=" * 70)
    print("🧪 Testing on sample reviews:")
    print("=" * 70)
    
    test_samples = [
        ("The food was amazing and fresh!", 5),
        ("Terrible meal. Food was cold and tasteless.", 1),
        ("Average food. Nothing special.", 3),
        ("Loved the biryani today. Delicious!", 5),
        ("Food quality is very poor. Not acceptable.", 2)
    ]
    
    for review, rating in test_samples:
        sentiment, confidence = model.predict(review, rating)
        print(f"\nReview: \"{review}\"")
        print(f"Rating: {rating}/5")
        print(f"Predicted: {sentiment.upper()} (confidence: {confidence:.2%})")
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print(f"📊 Final Metrics:")
    print(f"   - Cross-validation score: {cv_score:.4f}")
    print(f"   - Test accuracy: {test_accuracy:.4f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
