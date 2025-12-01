import pandas as pd
import joblib
import os
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def test_language_accuracy():
    print("🧪 Testing Per-Language Accuracy\n")
    
    # Load trained model
    model_path = 'ml/models/sentiment_model_fresh_50k.pkl'
    vec_path = 'ml/models/sentiment_model_fresh_50k_vectorizer.pkl'
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    print("✓ Model loaded\n")
    
    # Load test dataset
    data_path = 'ml/data/fresh_50k_reviews.csv'
    df = pd.read_csv(data_path)
    
    languages = ['telugu', 'kannada', 'punjabi', 'hindi', 'english']
    results = []
    
    print("=" * 60)
    
    # Test each language separately
    for lang in languages:
        print(f"\n📊 Testing {lang.upper()}")
        print("-" * 60)
        
        # Filter reviews for this language
        lang_df = df[df['language'] == lang]
        
        # Transform and predict
        X = vectorizer.transform(lang_df['review'])
        y_true = lang_df['sentiment']
        y_pred = model.predict(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        
        print(f"   Total Reviews: {len(lang_df)}")
        print(f"   Accuracy: {accuracy*100:.2f}%")
        
        # Per-sentiment breakdown
        good_mask = y_true == 'good'
        bad_mask = y_true == 'bad'
        
        good_accuracy = accuracy_score(y_true[good_mask], y_pred[good_mask]) * 100
        bad_accuracy = accuracy_score(y_true[bad_mask], y_pred[bad_mask]) * 100
        
        print(f"   Good Reviews Accuracy: {good_accuracy:.2f}%")
        print(f"   Bad Reviews Accuracy: {bad_accuracy:.2f}%")
        
        results.append({
            'language': lang,
            'total_reviews': len(lang_df),
            'accuracy': accuracy * 100,
            'good_accuracy': good_accuracy,
            'bad_accuracy': bad_accuracy
        })
    
    print("\n" + "=" * 60)
    
    # Overall multilingual accuracy
    print("\n🌐 OVERALL MULTILINGUAL PERFORMANCE")
    print("-" * 60)
    X_all = vectorizer.transform(df['review'])
    y_all_true = df['sentiment']
    y_all_pred = model.predict(X_all)
    overall_accuracy = accuracy_score(y_all_true, y_all_pred) * 100
    
    print(f"   Total Reviews: {len(df)}")
    print(f"   Overall Accuracy: {overall_accuracy:.2f}%")
    
    print("\n   Classification Report:")
    print(classification_report(y_all_true, y_all_pred))
    
    # Save results
    results_df = pd.DataFrame(results)
    results_path = 'ml/per_language_accuracy.txt'
    
    with open(results_path, 'w', encoding='utf-8') as f:
        f.write("PER-LANGUAGE ACCURACY RESULTS\n")
        f.write("=" * 60 + "\n\n")
        
        for result in results:
            f.write(f"{result['language'].upper()}\n")
            f.write(f"  Total Reviews: {result['total_reviews']}\n")
            f.write(f"  Overall Accuracy: {result['accuracy']:.2f}%\n")
            f.write(f"  Good Reviews: {result['good_accuracy']:.2f}%\n")
            f.write(f"  Bad Reviews: {result['bad_accuracy']:.2f}%\n\n")
        
        f.write("=" * 60 + "\n")
        f.write(f"OVERALL MULTILINGUAL ACCURACY: {overall_accuracy:.2f}%\n")
        f.write("=" * 60 + "\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_all_true, y_all_pred))
    
    print(f"\n💾 Results saved to {results_path}")
    print("\n✅ Accuracy testing complete!\n")
    
    # Return summary for display
    return results_df

if __name__ == "__main__":
    test_language_accuracy()
