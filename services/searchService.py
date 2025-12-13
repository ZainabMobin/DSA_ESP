import spacy, time, sys, os, string

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip

# Load lexicon(s) once
lexicon_gzip = load_lexicon_posting_gzip()
lexicon = load_lexicon()


def clean_and_lemmatize_query(words_list):  # 🟥 new function, same logic as preprocessing
    """Filters and lemmatize query words"""
    cleaned_words = []
    
    for word in words_list:
        w = word.lower().strip(string.punctuation)
        if not w or not w.isascii() or not w.isalpha() or len(w) < 2 or all(c == w[0] for c in w):
            continue
        cleaned_words.append(w)
    
    lemmas = []
    for doc in nlp.pipe(cleaned_words, batch_size=1000):
        if len(doc) == 0:
            continue
        lemmas.append(doc[0].lemma_)
    
    return lemmas

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def some_querying_func():
    query = input("Enter your search query: ")
    start = time.time()
    
    # Lemmatize query
    raw_words = query.strip().split()
    tokens = clean_and_lemmatize_query(raw_words)
    
    print(f"Lemmatized tokens: {tokens}")
    
    # Lookup in lexicon and show barrel info
    for token in tokens:
        entry = lexicon.get(token) ################################################################################
        if entry:
            print(f"'{entry}-{token}' found in lexicon:")
            # entry (wordID) has a list of barrel postings
            for i, b in enumerate(lexicon_gzip[entry]):
                print(f"  Barrel {i}: barrel_id={b['barrel_id']}, start_idx={b['start_idx']}, length={b['length']}")
        else:
            print(f"'{token}' not found in lexicon")
    
    end = time.time()
    print(f"Query processed in {end - start:.4f} seconds")

# Example usage
if __name__ == "__main__":
    some_querying_func()