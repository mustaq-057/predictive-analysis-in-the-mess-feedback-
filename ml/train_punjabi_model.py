import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. Load Data
print("Loading data...")
df = pd.read_csv('ml/data/multilingual_10k_reviews.csv')

# 2. Filter for Punjabi
print("Filtering for Punjabi reviews...")
punjabi_df = df[df['language'] == 'punjabi'].copy()
print(f"Found {len(punjabi_df)} Punjabi reviews.")

# 3. Preprocess
X = punjabi_df['review']
y = punjabi_df['sentiment']

# Vectorization
print("Vectorizing text...")
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_vectorized = vectorizer.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# 4. Train Model
print("Training Ensemble Model (RF + GB + LR)...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
lr = LogisticRegression(max_iter=1000, random_state=42)

ensemble = VotingClassifier(estimators=[
    ('rf', rf),
    ('gb', gb),
    ('lr', lr)
], voting='soft')

ensemble.fit(X_train, y_train)

# 5. Evaluate
print("\nEvaluating...")
y_pred = ensemble.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Punjabi Model Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save (Optional, but good practice)
# joblib.dump(ensemble, 'ml/models/punjabi_model.pkl')
# joblib.dump(vectorizer, 'ml/models/punjabi_vectorizer.pkl')
