import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# This function trains the machine learning model
def train_model():
    print("🚀 Training on Fresh 500k Dataset (1 Lakh per Language)...")
    
    # Check if the dataset file exists
    data_path = 'ml/data/fresh_500k_reviews.csv'
    if not os.path.exists(data_path):
        print(f"❌ Dataset not found: {data_path}")
        return
    
    # Load the data from the CSV file
    print("   Loading data...", end="", flush=True)
    df = pd.read_csv(data_path)
    print(f" Done. Loaded {len(df)} reviews")
    print(f"   Languages: {df['language'].value_counts().to_dict()}")
    
    # Convert text reviews into numbers so the computer can understand them
    print("✓ Vectorizing text (max_features=10000)...")
    vectorizer = TfidfVectorizer(
        max_features=10000,  # We look at the top 10,000 most common words
        stop_words='english',
        ngram_range=(1, 2)   # We look at single words and pairs of words
    )
    
    # Prepare the input (X) and output (y) data
    X = vectorizer.fit_transform(df['review'])
    y = df['sentiment']
    
    # Split data: 80% for training, 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"✓ Split: {X_train.shape[0]} train, {X_test.shape[0]} test")
    
    # Create an ensemble model (combining 3 different models for better accuracy)
    print("✓ Training ensemble model (this may take a few minutes)...")
    
    # Model 1: Random Forest (good for complex patterns)
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    
    # Model 2: Gradient Boosting (good for accuracy)
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    
    # Model 3: Logistic Regression (fast and simple)
    lr = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
    
    # Combine them all into one voting classifier
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('lr', lr)],
        voting='soft'
    )
    
    # Train the model on the training data
    ensemble.fit(X_train, y_train)
    
    # Test the model to see how accurate it is
    print("\n📊 Evaluation Results:")
    y_pred = ensemble.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   Test Accuracy: {accuracy*100:.2f}%")
    
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Create the folder to save the model if it doesn't exist
    model_dir = 'ml/models'
    os.makedirs(model_dir, exist_ok=True)
    
    # Define where to save the model files
    model_path = os.path.join(model_dir, 'sentiment_model_fresh_500k.pkl')
    vec_path = os.path.join(model_dir, 'sentiment_model_fresh_500k_vectorizer.pkl')
    
    # Save the trained model and vectorizer to disk
    print(f"✓ Saving model to {model_path}...")
    joblib.dump(ensemble, model_path)
    joblib.dump(vectorizer, vec_path)
    print("✓ Model saved")
    
    # Save the results to a text file for reference
    results_path = 'ml/fresh_500k_results.txt'
    with open(results_path, 'w') as f:
        f.write("FRESH 500K MULTILINGUAL MODEL RESULTS\n")
        f.write("=====================================\n\n")
        f.write(f"Dataset: 500,000 reviews (100k per language)\n")
        f.write(f"Languages: Telugu, Kannada, Punjabi, Hindi, English\n\n")
        f.write(f"Test Accuracy: {accuracy*100:.2f}%\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_test, y_pred))
    
    print(f"📄 Results saved to {results_path}")
    print("\n✅ Training complete!")

# Run the training function
if __name__ == "__main__":
    train_model()
