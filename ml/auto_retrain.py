import os
import json
import joblib
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime
import shutil
from dotenv import load_dotenv

load_dotenv('.env.local')

# Configuration
MONGO_URI = os.getenv('MONGODB_URI')
MODEL_DIR = 'ml/models'
DATA_DIR = 'ml/data'
BASE_DATA_FILE = os.path.join(DATA_DIR, 'fresh_50k_reviews.csv')
CURRENT_MODEL_PATH = os.path.join(MODEL_DIR, 'sentiment_model_production.pkl')
CURRENT_VECTORIZER_PATH = os.path.join(MODEL_DIR, 'sentiment_model_production_vectorizer.pkl')
MIN_ACCURACY_THRESHOLD = 0.90
MIN_IMPROVEMENT = 0.001

def fetch_new_data():
    """Fetch verified reviews from MongoDB to augment training data"""
    print("Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        try:
            db = client.get_database()
        except:
            db = client['test']
            
        collection = db['reviews']
        
        # Fetch reviews with valid sentiment - can add manual_correction filter for quality
        cursor = collection.find({
            'sentiment': {'$in': ['good', 'bad']},
            'review': {'$exists': True, '$ne': ''}
        })
        
        reviews = []
        for doc in cursor:
            reviews.append({
                'review': doc['review'],
                'sentiment': doc['sentiment'],
                'source': 'user_feedback'
            })
            
        print(f"Fetched {len(reviews)} new reviews from database")
        return pd.DataFrame(reviews)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def train_candidate_model(combined_data):
    """Train new model on combined base + user data"""
    print("Training candidate model...")
    
    # Use same vectorization params as production model
    vectorizer = TfidfVectorizer(
        max_features=5000, 
        stop_words='english',
        ngram_range=(1, 2)
    )
    X = vectorizer.fit_transform(combined_data['review'])
    y = combined_data['sentiment']
    
    # Split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Ensemble model matching production architecture
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    lr = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
    
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('lr', lr)],
        voting='soft'
    )
    
    ensemble.fit(X_train, y_train)
    
    # Evaluate candidate model
    y_pred = ensemble.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return ensemble, vectorizer, accuracy

def evaluate_current_model(test_data):
    """Evaluate current production model on new test data for comparison"""
    if not os.path.exists(CURRENT_MODEL_PATH):
        return 0.0
        
    try:
        model = joblib.load(CURRENT_MODEL_PATH)
        vectorizer = joblib.load(CURRENT_VECTORIZER_PATH)
        
        X_test = vectorizer.transform(test_data['review'])
        y_test = test_data['sentiment']
        y_pred = model.predict(X_test)
        
        return accuracy_score(y_test, y_pred)
    except Exception as e:
        print(f"Error evaluating current model: {e}")
        return 0.0

def main():
    print(f"Starting auto-retraining process at {datetime.now()}")
    
    # Load base training data
    if os.path.exists(BASE_DATA_FILE):
        base_df = pd.read_csv(BASE_DATA_FILE)
        print(f"Loaded {len(base_df)} base samples")
    else:
        print("Base data not found!")
        return

    # Fetch new user-generated reviews from database
    new_df = fetch_new_data()
    
    if len(new_df) == 0:
        print("No new data found. Skipping retraining.")
        return

    # Combine base synthetic data with real user feedback
    combined_df = pd.concat([base_df[['review', 'sentiment']], new_df[['review', 'sentiment']]])
    print(f"Total training samples: {len(combined_df)}")
    
    # Train candidate model
    candidate_model, candidate_vectorizer, candidate_accuracy = train_candidate_model(combined_df)
    print(f"Candidate Model Accuracy: {candidate_accuracy:.4f}")
    
    # Safety check: ensure new model meets minimum quality threshold
    if candidate_accuracy < MIN_ACCURACY_THRESHOLD:
        print(f"❌ Candidate accuracy ({candidate_accuracy:.4f}) below threshold ({MIN_ACCURACY_THRESHOLD}). Discarding.")
        return

    print("✅ Candidate model passed safety checks.")
    
    # Backup current production model before replacing
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(MODEL_DIR, 'archive')
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(CURRENT_MODEL_PATH):
        shutil.copy(CURRENT_MODEL_PATH, os.path.join(backup_dir, f'model_{timestamp}.pkl'))
        shutil.copy(CURRENT_VECTORIZER_PATH, os.path.join(backup_dir, f'vectorizer_{timestamp}.pkl'))
        print("Backed up current model.")
        
    # Deploy new model to production
    joblib.dump(candidate_model, CURRENT_MODEL_PATH)
    joblib.dump(candidate_vectorizer, CURRENT_VECTORIZER_PATH)
    print(f"🚀 Deployed new model version {timestamp}")
    
    # Log retraining event
    with open('ml/training_log.txt', 'a') as f:
        f.write(f"{timestamp}: Retrained on {len(combined_df)} samples. Accuracy: {candidate_accuracy:.4f}\n")

if __name__ == "__main__":
    main()
