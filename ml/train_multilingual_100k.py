import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os

# Ensure models directory exists
os.makedirs('ml/models', exist_ok=True)

# 1. Load Data
print("Loading 100k dataset...")
df = pd.read_csv('ml/data/multilingual_100k_reviews.csv')
print(f"Loaded {len(df)} reviews.")

# 2. Preprocess
X = df['review']
y = df['sentiment']

# Vectorization
print("Vectorizing text...")
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_vectorized = vectorizer.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# 3. Train Model
print("Training Ensemble Model (RF + GB + LR)...")
# Reduced estimators slightly for speed on large dataset, but still robust
rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1) 
gb = GradientBoostingClassifier(n_estimators=50, random_state=42)
lr = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)

ensemble = VotingClassifier(estimators=[
    ('rf', rf),
    ('gb', gb),
    ('lr', lr)
], voting='soft')

ensemble.fit(X_train, y_train)

# 4. Evaluate
print("\nEvaluating...")
y_pred = ensemble.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Model Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 5. Save
print("Saving model...")
joblib.dump(ensemble, 'ml/models/sentiment_model_100k.pkl')
joblib.dump(vectorizer, 'ml/models/sentiment_model_100k_vectorizer.pkl')
print("Saved to ml/models/sentiment_model_100k.pkl")
