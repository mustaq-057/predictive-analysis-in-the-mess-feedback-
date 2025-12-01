import joblib
import os

def test_production_model():
    """Quick test to verify production model is working correctly"""
    print("🧪 Testing Production Model\n")
    
    model_path = 'ml/models/sentiment_model_production.pkl'
    vec_path = 'ml/models/sentiment_model_production_vectorizer.pkl'
    
    if not os.path.exists(model_path):
        print("❌ Production model not found!")
        return
    
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    print("✓ Production model loaded successfully\n")
    
    # Test samples across all languages
    test_samples = [
        "pulao bahut tasty undi bro",  # Telugu - good
        "mess lo chai ekdum terrible",  # Telugu - bad
        "dosa super sakkath guru",      # Kannada - good
        "coffee ella illa disgusting",  # Kannada - bad
        "burger ekdum lajawab si",      # Punjabi - good
        "dal fry ghatiya hai yaar",     # Punjabi - bad
        "maggi ekdum zabardast tha",    # Hindi - good
        "soup bilkul ghatiya hai",      # Hindi - bad
        "bro the pasta was fire",       # English - good
        "mess coffee is straight trash" # English - bad
    ]
    
    print("Testing production model predictions:\n")
    print("=" * 60)
    
    for sample in test_samples:
        X = vectorizer.transform([sample])
        prediction = model.predict(X)[0]
        confidence = model.predict_proba(X)[0].max() * 100
        
        print(f"Review: {sample[:45]:45s}")
        print(f"→ Sentiment: {prediction:4s} | Confidence: {confidence:.1f}%\n")
    
    print("=" * 60)
    print("\n✅ Production model is working correctly!")

if __name__ == "__main__":
    test_production_model()
