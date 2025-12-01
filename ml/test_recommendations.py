import joblib
import os
import pandas as pd
import numpy as np

# This script tests if the model gives good recommendations on tricky examples
def test_recommendations():
    print("🎯 Testing AI Recommendation Quality\n")
    
    # Load the production model (the one currently used by the app)
    model_path = 'ml/models/sentiment_model_production.pkl'
    vec_path = 'ml/models/sentiment_model_production_vectorizer.pkl'
    
    # Check if model files exist
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    # Load the model and vectorizer
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    print("✓ Model loaded\n")
    
    # These are tricky test cases with slang and mixed languages
    test_cases = [
        # Good Reviews
        ("food was bussin", "good"),
        ("absolutely fire taste", "good"),
        ("no cap best meal ever", "good"),
        ("lit af", "good"),
        ("superb ga undi bro", "good"),  # Telugu
        ("maja aa gaya", "good"),        # Hindi
        ("full sakkath", "good"),        # Kannada
        ("lajawab si", "good"),          # Punjabi
        ("hits different", "good"),
        ("top tier food", "good"),
        ("legendary stuff", "good"),
        ("crazy good", "good"),
        
        # Bad Reviews
        ("straight trash", "bad"),
        ("mid af", "bad"),
        ("L food", "bad"),
        ("disgusting fr", "bad"),
        ("taste leka", "bad"),           # Telugu
        ("bekagilla", "bad"),            # Kannada
        ("ghatiya si", "bad"),           # Punjabi
        ("paisa barbaad", "bad"),        # Hindi
        ("zero stars", "bad"),
        ("not it", "bad"),
        ("ruined my day", "bad"),
        ("garbage", "bad")
    ]
    
    correct = 0
    total = len(test_cases)
    results = []
    
    print("=" * 50)
    print(f"{'Review':<30} | {'Pred':<8} | {'Conf':<6} | {'Status'}")
    print("=" * 50)
    
    # Loop through each test case
    for text, expected in test_cases:
        # Convert text to numbers
        vec = vectorizer.transform([text])
        # Predict sentiment
        pred = model.predict(vec)[0]
        # Get confidence score
        prob = model.predict_proba(vec)[0].max()
        
        # Check if prediction matches expected result
        is_correct = pred == expected
        if is_correct:
            correct += 1
            
        status = "✅" if is_correct else "❌"
        print(f"{text:<30} | {pred:<8} | {prob:.0%}   | {status}")
        
        results.append({
            'text': text,
            'expected': expected,
            'predicted': pred,
            'confidence': prob,
            'correct': is_correct
        })
    
    print("-" * 50)
    
    # Calculate final scores
    accuracy = (correct / total) * 100
    avg_conf = np.mean([r['confidence'] for r in results]) * 100
    
    print(f"\n📊 RESULTS")
    print(f"   Total Tests: {total}")
    print(f"   Correct Predictions: {correct}")
    print(f"   Accuracy: {accuracy:.2f}%")
    print(f"   Average Confidence: {avg_conf:.2f}%")
    
    # Save the results to a file
    with open('ml/recommendation_quality.txt', 'w') as f:
        f.write("AI RECOMMENDATION QUALITY REPORT\n")
        f.write("================================\n\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
        f.write(f"Average Confidence: {avg_conf:.2f}%\n\n")
        f.write("Detailed Results:\n")
        for r in results:
            status = "CORRECT" if r['correct'] else "WRONG"
            f.write(f"[{status}] '{r['text']}' -> Predicted: {r['predicted']} ({r['confidence']:.2f})\n")
            
    print("\n✅ Recommendation testing complete!")

# Run the test
if __name__ == "__main__":
    test_recommendations()
