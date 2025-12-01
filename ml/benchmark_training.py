import pandas as pd
import time
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def benchmark():
    print("🚀 Starting Training Benchmark (100k Reviews)...")
    start_total = time.time()

    # 1. Load Data
    start_load = time.time()
    print("   Loading data...", end="", flush=True)
    df = pd.read_csv('ml/data/multilingual_100k_reviews.csv')
    end_load = time.time()
    print(f" Done ({end_load - start_load:.2f}s)")

    # 2. Preprocess
    X = df['review']
    y = df['sentiment']

    # Vectorization
    start_vec = time.time()
    print("   Vectorizing...", end="", flush=True)
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_vectorized = vectorizer.fit_transform(X)
    end_vec = time.time()
    print(f" Done ({end_vec - start_vec:.2f}s)")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

    # 3. Train Model
    print("   Training Ensemble Model...", end="", flush=True)
    start_train = time.time()
    
    rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1) 
    gb = GradientBoostingClassifier(n_estimators=50, random_state=42)
    lr = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)

    ensemble = VotingClassifier(estimators=[
        ('rf', rf),
        ('gb', gb),
        ('lr', lr)
    ], voting='soft')

    ensemble.fit(X_train, y_train)
    end_train = time.time()
    print(f" Done ({end_train - start_train:.2f}s)")

    # Total Time
    end_total = time.time()
    
    print("\n📊 Benchmark Results:")
    print(f"   - Data Loading: {end_load - start_load:.2f}s")
    print(f"   - Vectorization: {end_vec - start_vec:.2f}s")
    print(f"   - Training:      {end_train - start_train:.2f}s")
    print(f"   ---------------------------")
    print(f"   ✅ Total Time:   {end_total - start_total:.2f}s")

if __name__ == "__main__":
    benchmark()
