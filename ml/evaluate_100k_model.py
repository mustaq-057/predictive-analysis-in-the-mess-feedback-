import joblib
import pandas as pd
from sklearn.metrics import accuracy_score

# 1. Load Model and Vectorizer
print("Loading 100k model and vectorizer...")
model = joblib.load('ml/models/sentiment_model_100k.pkl')
vectorizer = joblib.load('ml/models/sentiment_model_100k_vectorizer.pkl')

# 2. Define Test Data (Multilingual)
test_cases = [
    # Telugu
    {"text": "Bhojanam chala bagundi", "label": "good", "lang": "Telugu"},
    {"text": "Food asalu baledu", "label": "bad", "lang": "Telugu"},
    {"text": "Biryani keka", "label": "good", "lang": "Telugu"},
    {"text": "Curry daridram", "label": "bad", "lang": "Telugu"},
    
    # Kannada
    {"text": "Oota tumba chennagide", "label": "good", "lang": "Kannada"},
    {"text": "Saaru sakath", "label": "good", "lang": "Kannada"},
    {"text": "Food tumba keka", "label": "good", "lang": "Kannada"},
    {"text": "Rice sari illa", "label": "bad", "lang": "Kannada"},
    {"text": "Palya thu", "label": "bad", "lang": "Kannada"},

    # Punjabi
    {"text": "Khana bahut vadiya si", "label": "good", "lang": "Punjabi"},
    {"text": "Roti sira hai", "label": "good", "lang": "Punjabi"},
    {"text": "Dal ganda lagya", "label": "bad", "lang": "Punjabi"},
    {"text": "Sabzi swaad ni", "label": "bad", "lang": "Punjabi"},
    {"text": "Paneer ghaint hai", "label": "good", "lang": "Punjabi"},

    # Hindi
    {"text": "Khana bahut swadisht hai", "label": "good", "lang": "Hindi"},
    {"text": "Maza aa gaya", "label": "good", "lang": "Hindi"},
    {"text": "Sabzi bekaar hai", "label": "bad", "lang": "Hindi"},
    {"text": "Roti ekdum ghatiya", "label": "bad", "lang": "Hindi"},

    # English
    {"text": "The food was amazing", "label": "good", "lang": "English"},
    {"text": "Terrible service", "label": "bad", "lang": "English"},
    {"text": "I loved the biryani", "label": "good", "lang": "English"},
    {"text": "The curry was bland", "label": "bad", "lang": "English"}
]

# 3. Predict
print("\nRunning predictions...")
texts = [t['text'] for t in test_cases]
true_labels = [t['label'] for t in test_cases]

X = vectorizer.transform(texts)
predictions = model.predict(X)

# 4. Report
correct = 0
print(f"\n{'Text':<30} | {'Lang':<10} | {'True':<6} | {'Pred':<6} | {'Result'}")
print("-" * 75)

for i, (text, pred) in enumerate(zip(texts, predictions)):
    is_correct = pred == true_labels[i]
    if is_correct: correct += 1
    result_icon = "✅" if is_correct else "❌"
    print(f"{text:<30} | {test_cases[i]['lang']:<10} | {true_labels[i]:<6} | {pred:<6} | {result_icon}")

accuracy = (correct / len(test_cases)) * 100
print("-" * 75)
print(f"Overall Accuracy: {accuracy:.2f}% ({correct}/{len(test_cases)})")

# Language-wise accuracy
lang_stats = {}
for i, t in enumerate(test_cases):
    lang = t['lang']
    if lang not in lang_stats: lang_stats[lang] = {'total': 0, 'correct': 0}
    lang_stats[lang]['total'] += 1
    if predictions[i] == true_labels[i]:
        lang_stats[lang]['correct'] += 1

print("\nLanguage-wise Accuracy:")
for lang, stats in lang_stats.items():
    acc = (stats['correct'] / stats['total']) * 100
    print(f"{lang:<10}: {acc:.2f}%")
