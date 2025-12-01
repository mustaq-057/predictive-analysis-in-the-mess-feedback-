import sys
import json
import joblib
import os
import re
import warnings

# Ignore annoying warnings to keep output clean
warnings.filterwarnings("ignore")

# This class handles loading the model and making predictions
class MessSentimentModel:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        # Words we want to ignore (stopwords) but keeping 'not' and 'no' is important
        self.stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}

    # Load the trained model files from the disk
    @staticmethod
    def load(model_path='ml/models', model_name='sentiment_model_production'):
        model_file = os.path.join(model_path, f'{model_name}.pkl')
        vectorizer_file = os.path.join(model_path, f'{model_name}_vectorizer.pkl')
        
        # If files are missing, we can't load the model
        if not os.path.exists(model_file) or not os.path.exists(vectorizer_file):
            return None
            
        instance = MessSentimentModel()
        try:
            # Use joblib to load the saved model objects
            instance.model = joblib.load(model_file)
            instance.vectorizer = joblib.load(vectorizer_file)
            return instance
        except Exception as e:
            return None

    # Clean the text before analyzing it
    def preprocess_text(self, text):
        text = str(text).lower()
        # Remove special characters, keep only letters and spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        words = text.split()
        
        # Keep important negation words like 'not' or 'never'
        important_words = {'not', 'no', 'never', 'nothing', 'nowhere', 'neither', 'nobody', 'none'}
        words = [word for word in words if word not in self.stop_words or word in important_words]
        
        return ' '.join(words)

    # Predict if the review is good or bad
    def predict(self, text, rating=None):
        if not self.model or not self.vectorizer:
            raise ValueError("Model not loaded")
        
        # Clean the text
        processed_text = self.preprocess_text(text)
        # Convert text to numbers using the vectorizer
        tfidf = self.vectorizer.transform([processed_text])
        
        # Get the prediction (good/bad) and the confidence score
        sentiment = self.model.predict(tfidf)[0]
        confidence = self.model.predict_proba(tfidf)[0].max()
        
        # If confidence is low, trust the user's star rating instead
        if rating is not None:
            rating_based = 'good' if rating >= 3 else 'bad'
            if confidence < 0.6 and sentiment != rating_based:
                sentiment = rating_based
                confidence = 0.65
        
        return sentiment, confidence

# This is the entry point when the script is run from the command line
if __name__ == "__main__":
    try:
        # Get arguments passed from Node.js (review text and rating)
        if len(sys.argv) < 2:
            print(json.dumps({"success": False, "error": "No text provided"}))
            sys.exit(1)
            
        text = sys.argv[1]
        rating = float(sys.argv[2]) if len(sys.argv) > 2 else None
        
        # Load the model
        model = MessSentimentModel.load()
        
        if model:
            # Make the prediction
            sentiment, confidence = model.predict(text, rating)
            
            # Print the result as JSON so Node.js can read it
            print(json.dumps({
                "success": True,
                "sentiment": sentiment,
                "confidence": float(confidence),
                "analysis": f"Rated as {sentiment} with {confidence:.1%} confidence."
            }))
        else:
            # Fallback if model loading fails
            print(json.dumps({
                "success": False, 
                "error": "Model loading failed"
            }))
            
    except Exception as e:
        # Catch any unexpected errors
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)
