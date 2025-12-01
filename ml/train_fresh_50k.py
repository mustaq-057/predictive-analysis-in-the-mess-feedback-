import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def train_model():
    print("🚀 Training on Fresh 50k Dataset...")
    
    # Load dataset
    data_path = 'ml/data/fresh_50k_reviews.csv'
    if not os.path.exists(data_path):
        print(f"❌ Dataset not found: {data_path}")
        return
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} reviews")
    print(f"  Languages: {df['language'].value_counts().to_dict()}")
    
    # TF-IDF vectorization - converts text to numerical features
    print("✓ Vectorizing text...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)  # Unigrams + bigrams for context
    )
    
    X = vectorizer.fit_transform(df['review'])
    y = df['sentiment']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"✓ Split: {X_train.shape[0]} train, {X_test.shape[0]} test")
    
    # Ensemble model - combines three classifiers for better accuracy
    print("✓ Training ensemble model...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    lr = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
    
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('lr', lr)],
        voting='soft'  # Uses probability averaging
    )
    
    ensemble.fit(X_train, y_train)
    
    # Evaluate model
    print("\n📊 Evaluation Results:")
    y_pred = ensemble.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   Test Accuracy: {accuracy*100:.2f}%")
    
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\n   Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model and vectorizer
    model_dir = 'ml/models'
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'sentiment_model_fresh_50k.pkl')
    vec_path = os.path.join(model_dir, 'sentiment_model_fresh_50k_vectorizer.pkl')
    
    joblib.dump(ensemble, model_path)
    joblib.dump(vectorizer, vec_path)
    print(f"\n💾 Model saved to {model_path}")
    
    # Save results for reference
    results_path = 'ml/fresh_50k_results.txt'
    with open(results_path, 'w') as f:
        f.write("FRESH 50K MULTILINGUAL MODEL RESULTS\n")
        f.write("====================================\n\n")
        f.write(f"Dataset: 50,000 reviews (10k per language)\n")
        f.write(f"Languages: Telugu, Kannada, Punjabi, Hindi, English\n\n")
        f.write(f"Test Accuracy: {accuracy*100:.2f}%\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_test, y_pred))
        f.write("\n\nConfusion Matrix:\n")
        f.write(str(confusion_matrix(y_test, y_pred)))
    
    print(f"📄 Results saved to {results_path}")
    print("\n✅ Training complete!")

if __name__ == "__main__":
    train_model()
