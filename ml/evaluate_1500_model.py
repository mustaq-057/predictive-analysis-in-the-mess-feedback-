"""
Evaluate Multilingual Model (1500 Samples)
Tests the model across all 5 languages with specific test cases.
"""

import joblib
import os
import pandas as pd
from sklearn.metrics import accuracy_score

def evaluate_model():
    print("🚀 Starting Multilingual Model Evaluation...")
    
    # 1. Load Model
    model_path = 'ml/models/sentiment_model_1500.pkl'
    vec_path = 'ml/models/sentiment_model_1500_vectorizer.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(vec_path):
        print("❌ Model files not found. Please train the model first.")
        return
        
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    print("✓ Model loaded successfully")
    
    # 2. Define Test Cases
    test_cases = [
        # Telugu
        {'text': 'biryani chala bagundi', 'lang': 'Telugu', 'expected': 'good'},
        {'text': 'curry asalu baledu', 'lang': 'Telugu', 'expected': 'bad'},
        {'text': 'food super undi', 'lang': 'Telugu', 'expected': 'good'},
        {'text': 'taste daridram', 'lang': 'Telugu', 'expected': 'bad'},
        
        # Kannada
        {'text': 'oota sakath agide', 'lang': 'Kannada', 'expected': 'good'},
        {'text': 'saaru chennagilla', 'lang': 'Kannada', 'expected': 'bad'},
        {'text': 'idli tumba chennagide', 'lang': 'Kannada', 'expected': 'good'},
        {'text': 'palya thu', 'lang': 'Kannada', 'expected': 'bad'},
        
        # Punjabi
        {'text': 'paneer vadiya hai', 'lang': 'Punjabi', 'expected': 'good'},
        {'text': 'daal bekar si', 'lang': 'Punjabi', 'expected': 'bad'},
        {'text': 'chicken att hai', 'lang': 'Punjabi', 'expected': 'good'},
        {'text': 'roti ganda lagya', 'lang': 'Punjabi', 'expected': 'bad'},
        
        # Hindi
        {'text': 'khana mast tha', 'lang': 'Hindi', 'expected': 'good'},
        {'text': 'sabzi bakwas hai', 'lang': 'Hindi', 'expected': 'bad'},
        {'text': 'maza aa gaya', 'lang': 'Hindi', 'expected': 'good'},
        {'text': 'mood kharab ho gaya', 'lang': 'Hindi', 'expected': 'bad'},
        
        # English
        {'text': 'food was amazing', 'lang': 'English', 'expected': 'good'},
        {'text': 'terrible taste', 'lang': 'English', 'expected': 'bad'},
        {'text': 'really good meal', 'lang': 'English', 'expected': 'good'},
        {'text': 'awful experience', 'lang': 'English', 'expected': 'bad'}
    ]
    
    # 3. Run Predictions
    print("\nRunning Language Tests...")
    print("-" * 70)
    print(f"{'Language':<10} | {'Text':<25} | {'Pred':<8} | {'Exp':<8} | {'Status'}")
    print("-" * 70)
    
    correct_count = 0
    results_by_lang = {}
    
    for case in test_cases:
        text = case['text']
        lang = case['lang']
        expected = case['expected']
        
        # Transform and Predict
        X = vectorizer.transform([text])
        prediction = model.predict(X)[0]
        
        is_correct = prediction == expected
        if is_correct:
            correct_count += 1
            status = "✅"
        else:
            status = "❌"
            
        # Track by language
        if lang not in results_by_lang:
            results_by_lang[lang] = {'total': 0, 'correct': 0}
        results_by_lang[lang]['total'] += 1
        if is_correct:
            results_by_lang[lang]['correct'] += 1
            
        print(f"{lang:<10} | {text:<25} | {prediction.upper():<8} | {expected.upper():<8} | {status}")
        
    print("-" * 70)
    
    # 4. Summary
    total_accuracy = (correct_count / len(test_cases)) * 100
    print(f"\n📊 Overall Accuracy: {correct_count}/{len(test_cases)} ({total_accuracy:.1f}%)")
    
    print("\n🌍 Accuracy by Language:")
    for lang, stats in results_by_lang.items():
        acc = (stats['correct'] / stats['total']) * 100
        print(f"   - {lang}: {acc:.1f}% ({stats['correct']}/{stats['total']})")
        
    # Save results
    with open('ml/multilingual_1500_evaluation.txt', 'w') as f:
        f.write(f"Overall Accuracy: {total_accuracy:.1f}%\n")
        for lang, stats in results_by_lang.items():
            acc = (stats['correct'] / stats['total']) * 100
            f.write(f"{lang}: {acc:.1f}%\n")

if __name__ == "__main__":
    evaluate_model()
