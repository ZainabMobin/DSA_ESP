#BM25 SEARCH AND RANKING ALGORITHM APPLIED
import spacy, time, sys, os, string
from collections import defaultdict
import math  # 🟢 added for BM25 computation

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip
from loaders.barrelLoader import fetch_barrel_results_binary_offset
from loaders.forwardLoader import load_forward  # 🟢 added for BM25
from loaders.mapLoaders import load_docmeta, load_docmap

# Load lexicon(s) once
lexicon_gzip = load_lexicon_posting_gzip()
lexicon = load_lexicon()
forward_index = load_forward()
doc_meta = load_docmeta()
doc_map = load_docmap()

# Precompute average document length
N = len(forward_index)
avgdl = sum(doc["length"] for doc in forward_index.values()) / N

# BM25 parameters
k1 = 1.5
b = 0.75

def get_barrel_info(wordID):
    """Retrieve barrel information for a given wordID from the lexicon_gzip."""
    if wordID not in lexicon_gzip:
        return None
    
    meta = lexicon_gzip[wordID]
    postings = []
    df = 0  # document frequency

    for b in meta:
        barrel_id = b['barrel_id']
        offset = b['offset']
        length_bytes = b['length_bytes']
        
        barrel_info = fetch_barrel_results_binary_offset(barrel_id, offset, length_bytes)
        df = df + len(barrel_info)  # accumulate document frequency

        for docID, tf in barrel_info:
             postings.append((docID, tf))

    return postings, df


def clean_and_lemmatize_query(words_list):  # 🟥 new function
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


def get_word_bm25_ranking(query_tokens, top_k=10):
    scores = defaultdict(float)

    for token in query_tokens:
        wordID = lexicon.get(token)
        if not wordID:
            continue

        postings, df = get_barrel_info(wordID)
        if df == 0:
            continue

        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

        for docID, tf in postings:
            dl = forward_index[docID]["length"]
            score = idf * ( (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl)) )
            scores[docID] += score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]


def querying_function(query, top_k):
    """
    function recieves query as a string, processes words, 
    gets relevant docInfo from postings,
    calculates bm ranking of each result and returns top k results 
    """

    start = time.time()
    
    raw_words = query.strip().split()
    tokens = clean_and_lemmatize_query(raw_words)
    
    print(f"Lemmatized tokens: {tokens}")
    
    # 🟢 BM25 ranking
    ranked_docs = get_word_bm25_ranking(tokens, top_k)
    
    print("[INFO] Top ranked documents:")
    for docID, score in ranked_docs:
        meta = doc_meta[docID]
        print(
            f"DocID: {docID}, Score: {score:.4f}, "
            f"Path: {doc_map[docID]}, "
            f"Title: {meta.get('title', '')}, "
            f"Authors: {', '.join(meta.get('authors', []))}, "
        )

    end = time.time()
    print(f"Query processed in {end - start:.4f} seconds")


def run_query(top_k):
    query = input("Enter your search query: ")
    querying_function(query, top_k)


if __name__ == "__main__":
    top_k = 10  # Number of top documents to retrieve
    run_query(top_k)