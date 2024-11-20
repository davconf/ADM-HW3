# textprocessor.py
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer

# 'punkt' is for tokenizing text into sentences
# 'stopwords' is for a list of common words to remove
# 'punk_tab' is specifically designed for processing text where sentences are separated by tabs
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# Use english stopwords. This line defines a set of common English words that are often removed
# during text preprocessing, as they don't usually carry much meaning (e.g., "the," "a," "is").
stop_words = set(stopwords.words('english'))

# Initialize the stemmer
stemmer = SnowballStemmer("english")

import re

def cleaner(desc):
  
  # Convert "-" to whitespace (for the cases like 'Michelin-starred', 'owner-chef'...)
  desc = desc.replace('-', ' ')

  # Remove punctuation
  desc = re.sub(r'[^\w\s]', '', desc)

  # Convert to lowercase
  desc = desc.lower()

  # Remove leading and trailing whitespaces
  desc = desc.strip()

  # Remove multiple whitespaces
  desc = re.sub(' +', ' ', desc)

  # Remove stopwords and perform stemming
  tokens = word_tokenize(desc)
  cleaned_tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
  cleaned_desc = ' '.join(cleaned_tokens)

  return cleaned_desc