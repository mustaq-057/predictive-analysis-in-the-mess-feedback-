"""
Test Script to Compare Model Accuracy with Different Training Dataset Sizes

This script will:
1. Test model with 1000 reviews
2. Train with 500 samples and measure accuracy
3. Train with 1000 samples and measure accuracy
4. Compare the results
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
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
    """Sentiment analysis model for mess food reviews"""
    
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
    
    def train(self, X_train, y_train, verbose=True):
        """Train the sentiment analysis model"""
        if verbose:
            print("🔧 Preprocessing training data...")
        X_train_processed = [self.preprocess_text(text) for text in X_train]
        
        # Feature extraction using TF-IDF
        if verbose:
            print("📊 Extracting features using TF-IDF...")
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.85
        )
        X_train_tfidf = self.vectorizer.fit_transform(X_train_processed)
        
        # Train classifiers
        if verbose:
            print("🤖 Training classifiers...")
        
        nb_model = MultinomialNB(alpha=0.1)
        nb_model.fit(X_train_tfidf, y_train)
        
        lr_model = LogisticRegression(max_iter=1000, C=1.0)
        lr_model.fit(X_train_tfidf, y_train)
        
        svm_model = SVC(kernel='linear', C=1.0, probability=True)
        svm_model.fit(X_train_tfidf, y_train)
        
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf_model.fit(X_train_tfidf, y_train)
        
        # Create ensemble
        self.model = VotingClassifier(
            estimators=[
                ('nb', nb_model),
                ('lr', lr_model),
                ('svm', svm_model),
                ('rf', rf_model)
            ],
            voting='soft',
            weights=[1, 1, 2, 1]
        )
        self.model.fit(X_train_tfidf, y_train)
    
    def evaluate(self, X_test, y_test, verbose=True):
        """Evaluate model on test set"""
        X_test_processed = [self.preprocess_text(text) for text in X_test]
        X_test_tfidf = self.vectorizer.transform(X_test_processed)
        
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        
        if verbose:
            print(f"\n🎯 Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
            print("\n📊 Classification Report:")
            print(classification_report(y_test, y_pred))
            print("\n📉 Confusion Matrix:")
            print(confusion_matrix(y_test, y_pred))
        
        return accuracy, y_pred


def run_experiment(data_path, train_size, test_size=200, experiment_name="Experiment"):
    """Run a single training experiment"""
    print("\n" + "=" * 70)
    print(f"{experiment_name}")
    print("=" * 70)
    
    # Load data
    print(f"\n📂 Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"✓ Total reviews available: {len(df)}")
    
    # Limit dataset to train_size + test_size
    total_needed = train_size + test_size
    if len(df) < total_needed:
        print(f"⚠️ Warning: Only {len(df)} reviews available, need {total_needed}")
        df = df
    else:
        df = df.sample(n=total_needed, random_state=42).reset_index(drop=True)
    
    print(f"  - Good reviews: {(df['sentiment'] == 'good').sum()}")
    print(f"  - Bad reviews: {(df['sentiment'] == 'bad').sum()}")
    
    # Split data
    print(f"\n✂️  Splitting data ({train_size} train, {test_size} test)...")
    X = df['review'].values
    y = df['sentiment'].values
    
    # Custom split to get exact train_size
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=train_size, test_size=test_size, 
        random_state=42, stratify=y
    )
    
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Test samples: {len(X_test)}")
    
    # Train model
    model = MessSentimentModel()
    model.train(X_train, y_train, verbose=True)
    
    # Evaluate model
    accuracy, predictions = model.evaluate(X_test, y_test, verbose=True)
    
    return {
        'train_size': len(X_train),
        'test_size': len(X_test),
        'accuracy': accuracy,
        'accuracy_percent': accuracy * 100
    }


def main():
    """Main testing pipeline"""
    print("=" * 80)
    print("🍽️  MESS SENTIMENT MODEL - ACCURACY COMPARISON TEST")
    print("=" * 80)
    
    # Use ultra_large_reviews.csv as primary dataset
    data_path = 'ml/data/ultra_large_reviews.csv'
    
    # Check if data exists
    if not os.path.exists(data_path):
        print(f"⚠️ Data not found at {data_path}")
        # Try augmented dataset as fallback
        data_path = 'ml/data/augmented_reviews.csv'
        if not os.path.exists(data_path):
            print(f"❌ No data found!")
            return
    
    print(f"📊 Using dataset: {data_path}\n")
    
    results = []
    
    # Test 1: Train with 500 samples
    print("\n" + "🔬 TEST 1: Training with 500 reviews" + "\n")
    result_500 = run_experiment(
        data_path=data_path,
        train_size=500,
        test_size=200,
        experiment_name="📊 Experiment 1: 500 Training Samples"
    )
    results.append(('500 samples', result_500))
    
    # Test 2: Train with 1000 samples
    print("\n" + "🔬 TEST 2: Training with 1000 reviews" + "\n")
    result_1000 = run_experiment(
        data_path=data_path,
        train_size=1000,
        test_size=200,
        experiment_name="📊 Experiment 2: 1000 Training Samples"
    )
    results.append(('1000 samples', result_1000))
    
    # Comparison
    print("\n" + "=" * 80)
    print("📈 FINAL COMPARISON RESULTS")
    print("=" * 80)
    
    for name, result in results:
        print(f"\n{name}:")
        print(f"  - Training Size: {result['train_size']}")
        print(f"  - Test Size: {result['test_size']}")
        print(f"  - Accuracy: {result['accuracy']:.4f} ({result['accuracy_percent']:.2f}%)")
    
    # Calculate improvement
    if len(results) == 2:
        acc_500 = results[0][1]['accuracy_percent']
        acc_1000 = results[1][1]['accuracy_percent']
        improvement = acc_1000 - acc_500
        
        print("\n" + "=" * 80)
        print("📊 ANALYSIS")
        print("=" * 80)
        print(f"Accuracy with 500 samples: {acc_500:.2f}%")
        print(f"Accuracy with 1000 samples: {acc_1000:.2f}%")
        print(f"Improvement: {improvement:+.2f}%")
        
        if improvement > 0:
            print(f"\n✅ Model accuracy IMPROVED by {improvement:.2f}% with more training data!")
        elif improvement < 0:
            print(f"\n⚠️ Model accuracy DECREASED by {abs(improvement):.2f}% (possible overfitting)")
        else:
            print(f"\n➡️ No significant change in accuracy")
        
        print("\n💡 Recommendation:")
        if improvement > 2:
            print("   Training with more data significantly helps. Consider using even larger datasets.")
        elif improvement > 0:
            print("   Small improvement observed. More data helps slightly.")
        else:
            print("   Model may have reached optimal performance. Focus on feature engineering.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
