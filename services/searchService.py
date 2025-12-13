import spacy, time, sys, os, string

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip
from loaders.barrelLoader import fetch_barrel_results_binary_offset
# Load lexicon(s) once
lexicon_gzip = load_lexicon_posting_gzip()
lexicon = load_lexicon()

def get_barrel_info(wordID):
    """Retrieve barrel information for a given wordID from the lexicon_gzip."""
    if wordID not in lexicon_gzip:
        return None
    
    meta = lexicon_gzip[wordID]
    #process the word to look into all given barrels

    for i, b in enumerate(meta):
        barrel_id = b['barrel_id']
        offset = b['offset']
        length_bytes = b['length_bytes']
        print(f"Barrel {i}: barrel_id={barrel_id}, offset={offset}, length={length_bytes}")
        
        #fetch revelevant barrel info
        info = fetch_barrel_results_binary_offset(barrel_id, offset, length_bytes)
        #display info for first barrel only, Huge print statements halt the process and take up more time
        if i==1:
            print(f"  Barrel {i} info: {info}")

        #combine docIDs to be prosessed from the forward index in multiprocess/pool for ranking, 
        # rank top docs and return top 10 (get the top 10 docIDs, get the doc filepaths, return 
        # title and relevant metadata for fast display from the file paths (maybe implement meta 
        # data in forward index but it is already so full, have to look into a solution ), finally 
        # return the text parse if the button is clicked on a specific file on the engine and 
        # display the parsed results at frontend

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

# Load spaCy model for lemmatization
nlp = spacy.load("en_core_web_sm")

def some_querying_func():
    query = input("Enter your search query: ")
    start = time.time()
    
    # clean and Lemmatize query words
    raw_words = query.strip().split()
    tokens = clean_and_lemmatize_query(raw_words)
    
    print(f"Lemmatized tokens: {tokens}")
    
    # Lookup word in lexicon to get wordID and extract barrel info
    for token in tokens:
        entry = lexicon.get(token) 
        if entry:
            get_barrel_info(entry)
            #print(f"'{entry}-{token}' found in lexicon:")
            # entry (wordID) has a list of barrel postings
            # for i, b in enumerate(lexicon_gzip[entry]):
            #     print(f"  Barrel {i}: barrel_id={b['barrel_id']}, offset={b['offset']}, length={b['length']}")
        else:
            print(f"'{token}' not found in lexicon")
            
    end = time.time()
    print(f"Query processed in {end - start:.4f} seconds")

# Example usage
if __name__ == "__main__":
    some_querying_func()