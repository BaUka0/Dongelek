import nltk
import numpy as np
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    """Clean and preprocess text input"""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation except question marks
    text = re.sub(r'[^\w\s\?]', '', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Lemmatize tokens
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmatized_tokens

def bag_of_words(tokenized_sentence, all_words):
    """
    Return bag of words array:
    1 for each known word that exists in the sentence, 0 otherwise
    """
    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, word in enumerate(all_words):
        if word in tokenized_sentence:
            bag[idx] = 1.0
    return bag

def match_intent(user_input, intents):
    """
    Basic intent matcher using pattern matching
    Returns the matched intent or None
    """
    user_tokens = set(preprocess_text(user_input))
    
    best_match = None
    max_score = 0
    
    for intent in intents:
        # Split patterns and convert to lower case
        patterns = [p.lower().strip() for p in intent.pattern.split(',')]
        
        # Check for exact matches first
        for pattern in patterns:
            if pattern.lower() in user_input.lower():
                return intent
        
        # If no exact match, try token matching
        for pattern in patterns:
            pattern_tokens = set(preprocess_text(pattern))
            if not pattern_tokens:
                continue
                
            # Calculate matching score
            common_tokens = user_tokens.intersection(pattern_tokens)
            score = len(common_tokens) / len(pattern_tokens)
            
            if score > 0.5 and score > max_score:  # Threshold for match
                max_score = score
                best_match = intent
    
    return best_match
