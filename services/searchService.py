# #BM25 SEARCH AND RANKING ALGORITHM APPLIED
# import spacy, time, sys, os, string
# from collections import defaultdict
# import math  # 🟢 added for BM25 computation

# # Add project root to path if needed
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip
# from loaders.barrelLoader import fetch_barrel_results_binary_offset
# from loaders.forwardLoader import load_forward  # 🟢 added for BM25
# from loaders.mapLoaders import load_docmeta, load_docmap

# # Load lexicon(s) once
# lexicon_gzip = load_lexicon_posting_gzip()
# lexicon = load_lexicon()
# forward_index = load_forward()
# doc_meta = load_docmeta()
# doc_map = load_docmap()

# # Precompute average document length
# N = len(forward_index)
# avgdl = sum(doc["length"] for doc in forward_index.values()) / N

# # BM25 parameters
# k1 = 1.5
# b = 0.75

# def get_barrel_info(wordID):
#     """Retrieve barrel information for a given wordID from the lexicon_gzip."""
#     if wordID not in lexicon_gzip:
#         return None
    
#     meta = lexicon_gzip[wordID]
#     postings = []
#     df = 0  # document frequency

#     for b in meta:
#         barrel_id = b['barrel_id']
#         offset = b['offset']
#         length_bytes = b['length_bytes']
        
#         barrel_info = fetch_barrel_results_binary_offset(barrel_id, offset, length_bytes)
#         df = df + len(barrel_info)  # accumulate document frequency

#         for docID, tf in barrel_info:
#              postings.append((docID, tf))

#     return postings, df


# def clean_and_lemmatize_query(words_list):  # 🟥 new function
#     """Filters and lemmatize query words"""
#     cleaned_words = []
    
#     for word in words_list:
#         w = word.lower().strip(string.punctuation)
#         if not w or not w.isascii() or not w.isalpha() or len(w) < 2 or all(c == w[0] for c in w):
#             continue
#         cleaned_words.append(w)
    
#     lemmas = []
#     for doc in nlp.pipe(cleaned_words, batch_size=1000):
#         if len(doc) == 0:
#             continue
#         lemmas.append(doc[0].lemma_)
    
#     return lemmas

# # Load spaCy model
# nlp = spacy.load("en_core_web_sm")


# def get_word_bm25_ranking(query_tokens, top_k=10):
#     scores = defaultdict(float)

#     for token in query_tokens:
#         wordID = lexicon.get(token)
#         if not wordID:
#             continue

#         postings, df = get_barrel_info(wordID)
#         if df == 0:
#             continue

#         idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

#         for docID, tf in postings:
#             dl = forward_index[docID]["length"]
#             score = idf * ( (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl)) )
#             scores[docID] += score

#     return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]


# def querying_function(query, top_k):
#     """
#     function recieves query as a string, processes words, 
#     gets relevant docInfo from postings,
#     calculates bm ranking of each result and returns top k results 
#     """

#     start = time.time()
    
#     raw_words = query.strip().split()
#     tokens = clean_and_lemmatize_query(raw_words)
    
#     print(f"Lemmatized tokens: {tokens}")
    
#     # 🟢 BM25 ranking
#     ranked_docs = get_word_bm25_ranking(tokens, top_k)
    
#     print("[INFO] Top ranked documents:")
#     for docID, score in ranked_docs:
#         meta = doc_meta[docID]
#         print(
#             f"DocID: {docID}, Score: {score:.4f}, "
#             f"Path: {doc_map[docID]}, "
#             f"Title: {meta.get('title', '')}, "
#             f"Authors: {', '.join(meta.get('authors', []))}, "
#         )

#     end = time.time()
#     print(f"Query processed in {end - start:.4f} seconds")


# def run_query(top_k):
#     query = input("Enter your search query: ")
#     querying_function(query, top_k)


# if __name__ == "__main__":
#     top_k = 10  # Number of top documents to retrieve
#     run_query(top_k)


# # BM25 + Semantic Re-ranking using GloVe vectors
# import spacy, time, sys, os, string
# from collections import defaultdict
# import math
# import numpy as np
# import gzip, pickle

# # Add project root to path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip
# from loaders.barrelLoader import fetch_barrel_results_binary_offset
# from loaders.forwardLoader import load_forward
# from loaders.mapLoaders import load_docmeta, load_docmap
# from loaders.gloveLoader import load_glove_matrix

# # 🔹 Load indices
# lexicon_gzip = load_lexicon_posting_gzip()
# lexicon = load_lexicon()
# forward_index = load_forward()
# doc_meta = load_docmeta()
# doc_map = load_docmap()
# glove_words, glove_matrix = load_glove_matrix()

# # 🔹 BM25 parameters
# N = len(forward_index)
# avgdl = sum(doc["length"] for doc in forward_index.values()) / N
# k1 = 1.5
# b = 0.75

# # 🔹 build word → index mapping
# glove_word2idx = {w: i for i, w in enumerate(glove_words)}

# # 🔹 Normalize vectors once for cosine similarity
# glove_matrix_norm = glove_matrix / np.linalg.norm(glove_matrix, axis=1, keepdims=True)

# # Load spaCy model
# nlp = spacy.load("en_core_web_sm")

# # ---------------- BM25 functions ----------------
# def get_barrel_info(wordID):
#     if wordID not in lexicon_gzip:
#         return None
    
#     meta = lexicon_gzip[wordID]
#     postings = []
#     df = 0
#     for b in meta:
#         barrel_id = b['barrel_id']
#         offset = b['offset']
#         length_bytes = b['length_bytes']
#         barrel_info = fetch_barrel_results_binary_offset(barrel_id, offset, length_bytes)
#         df += len(barrel_info)
#         postings.extend(barrel_info)
#     return postings, df

# def clean_and_lemmatize_query(words_list):
#     cleaned_words = []
#     for word in words_list:
#         w = word.lower().strip(string.punctuation)
#         if not w or not w.isascii() or not w.isalpha() or len(w) < 2 or all(c == w[0] for c in w):
#             continue
#         cleaned_words.append(w)
    
#     # Filter out stop words before lemmatization gives more optimization
#     filtered_words = [w for w in cleaned_words if w not in nlp.Defaults.stop_words]

#     lemmas = []
#     for doc in nlp.pipe(filtered_words, batch_size=1000):
#         if len(doc) == 0:
#             continue
#         lemmas.append(doc[0].lemma_)
    
#     return lemmas

# def get_word_bm25_ranking(query_tokens, top_k=10):
#     scores = defaultdict(float)
#     for token in query_tokens:
#         wordID = lexicon.get(token)
#         if not wordID:
#             continue
#         postings, df = get_barrel_info(wordID)
#         if df == 0:
#             continue
#         idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
#         for docID, tf in postings:
#             dl = forward_index[docID]["length"]
#             score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl)))
#             scores[docID] += score

#         print(f" DOC {docID} Score {scores[docID]}")

#     return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

# # ---------------- Semantic re-ranking ----------------
# def semantic_rerank(query_tokens, ranked_docs, top_k=10):
#     """Use GloVe embeddings to rerank BM25 results based on cosine similarity"""
#     # Build query vector by averaging embeddings
#     vectors = []
#     for token in query_tokens:
#         idx = glove_word2idx.get(token)
#         if idx is not None:
#             vectors.append(glove_matrix_norm[idx])
#     if not vectors:
#         return ranked_docs  # fallback to BM25 if no embeddings
    
#     query_vec = np.mean(np.stack(vectors), axis=0)
#     doc_scores = []
    
#     for docID, bm25_score in ranked_docs:
#         # 🔹 Build document vector (average of tokens in doc)
#         doc_info = forward_index[docID]
#         doc_vecs = []
#         for wordID, freq in doc_info["terms"]:
#             word = lexicon.get(wordID)
#             if word in glove_word2idx:
#                 doc_vecs.append(glove_matrix_norm[glove_word2idx[word]])
        
#         if not doc_vecs:
#             doc_scores.append((docID, bm25_score))
#             continue

#         doc_vec = np.mean(np.stack(doc_vecs), axis=0)
#         cosine_sim = np.dot(query_vec, doc_vec)
#         combined_score = 0.7 * bm25_score + 0.3 * cosine_sim  # 🔹 combine BM25 + semantic
#         doc_scores.append((docID, combined_score))
    
#         print(f" DOC {docID} Score {combined_score}")

#     return sorted(doc_scores, key=lambda x: x[1], reverse=True)[:top_k]

# # ---------------- Querying ----------------
# def querying_function(query, top_k):
#     start = time.time()
    
#     raw_words = query.strip().split()
#     tokens = clean_and_lemmatize_query(raw_words)
#     print(f"Lemmatized tokens: {tokens}")
    
#     # 🟢 BM25 ranking
#     ranked_docs = get_word_bm25_ranking(tokens, top_k=top_k*5)  # get more for semantic rerank
    
#     # 🟢 Semantic re-ranking
#     reranked_docs = semantic_rerank(tokens, ranked_docs, top_k=top_k)
    
#     print("[INFO] Top ranked documents after semantic rerank:")
#     for docID, score in reranked_docs:
#         meta = doc_meta[docID]
#         print(
#             f"DocID: {docID}, Score: {score:.4f}, "
#             f"Path: {doc_map[docID]}, "
#             f"Title: {meta.get('title', '')}, "
#             f"Authors: {', '.join(meta.get('authors', []))}, "
#         )
#     end = time.time()
#     print(f"Query processed in {end - start:.4f} seconds")

# def run_query(top_k):
#     query = input("Enter your search query: ")
#     querying_function(query, top_k)

# if __name__ == "__main__":
#     top_k = 10
#     run_query(top_k)


    
# BM25 + Semantic Re-ranking using GloVe vectors
import spacy, time, sys, os, string
from collections import defaultdict
import math
import numpy as np
import gzip, pickle
import json
import pickle as pkl  # ⭕ Added for saving/loading trie

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip
from loaders.barrelLoader import fetch_barrel_results_binary_offset
from loaders.forwardLoader import load_forward
from loaders.mapLoaders import load_docmeta, load_docmap
from loaders.gloveLoader import load_glove_matrix

# 🔹 Load indices
lexicon_gzip = load_lexicon_posting_gzip()
lexicon = load_lexicon()
forward_index = load_forward()
doc_meta = load_docmeta()
doc_map = load_docmap()
glove_words, glove_matrix = load_glove_matrix()

# 🔹 BM25 parameters
N = len(forward_index)
avgdl = sum(doc["length"] for doc in forward_index.values()) / N
k1 = 1.5
b = 0.75

# 🔹 build word → index mapping
glove_word2idx = {w: i for i, w in enumerate(glove_words)}

# 🔹 Normalize vectors once for cosine similarity
glove_matrix_norm = glove_matrix / np.linalg.norm(glove_matrix, axis=1, keepdims=True)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# ⭕ TRIE IMPLEMENTATION STARTS HERE
class TrieNode:
    """Trie node for autocomplete"""
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.frequency = 0  # How many times this word appears
        self.doc_freq = 0   # In how many documents it appears
        self.last_updated = time.time() # when the word was updated
        self.quality_score = 1.0  # Confidence/quality metric

class TrieAutocomplete:
    """Trie-based autocomplete with forward index metrics"""
    def __init__(self, lexicon_data=None):
        self.root = TrieNode()
        self.word_count = 0
        self.trie_file = "/processed_data/trie_data.pkl"
        self.metrics_file = "trie_metrics.json"
        
        # Load forward index metrics
        self.load_or_build_trie(lexicon_data)
    
    def load_or_build_trie(self, lexicon_data):
        """Load existing trie or build from lexicon"""
        if os.path.exists(self.trie_file) and os.path.exists(self.metrics_file):
            try:
                print(f"[TRIE] Loading existing trie from {self.trie_file}")
                with open(self.trie_file, 'rb') as f:
                    self.root = pkl.load(f)
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
                    self.word_count = metrics['word_count']
                print(f"[TRIE] Loaded {self.word_count} words from saved trie")
                return
            except Exception as e:
                print(f"[TRIE] Error loading trie: {e}")
        
        # Build new trie from lexicon
        if lexicon_data:
            print(f"[TRIE] Building new trie from lexicon...")
            self.build_from_lexicon(lexicon_data)
    
    def build_from_lexicon(self, lexicon_data):
        """Build trie from lexicon with forward index frequencies"""
        print(f"[TRIE] Building trie with {len(lexicon_data)} lexicon entries...")
        
        # lexicon_data is the reverse lexicon: word -> wordID
        for word, wordID in lexicon_data.items():
            # Get document frequency from lexicon_gzip
            if wordID in lexicon_gzip:
                df = 0
                for b in lexicon_gzip[wordID]:
                    # Get actual document frequency from barrel
                    barrel_info = fetch_barrel_results_binary_offset(
                        b['barrel_id'], b['offset'], b['length_bytes']
                    )
                    df += len(barrel_info)
                
                # Insert with frequency metrics
                self.insert(word, frequency=df, doc_frequency=df)
        
        self.save_trie()
        print(f"[TRIE] Built trie with {self.word_count} words")
    
    def insert(self, word, frequency=1, doc_frequency=1, quality_score=1.0):
        """Insert a word into trie with metrics"""
        node = self.root
        word_lower = word.lower()
        
        for char in word_lower:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Update metrics if word already exists
        if node.is_end:
            node.frequency += frequency
            node.doc_freq += doc_frequency
            node.quality_score = max(node.quality_score, quality_score)
        else:
            node.is_end = True
            node.frequency = frequency
            node.doc_freq = doc_frequency
            node.quality_score = quality_score
            self.word_count += 1
        
        node.last_updated = time.time()
    
    def search_prefix(self, prefix):
        """Find all words with given prefix"""
        node = self.root
        prefix_lower = prefix.lower()
        
        # Navigate to prefix node
        for char in prefix_lower:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all words from this node
        results = []
        self._collect_words(node, prefix_lower, results)
        return results
    
    def _collect_words(self, node, current_word, results):
        """DFS to collect words from node"""
        if node.is_end:
            results.append({
                'word': current_word,
                'frequency': node.frequency,
                'doc_freq': node.doc_freq,
                'quality': node.quality_score,
                'last_updated': node.last_updated
            })
        
        for char, child_node in node.children.items():
            self._collect_words(child_node, current_word + char, results)
    
    def autocomplete(self, prefix, limit=10, min_freq=1, min_quality=0.1):
        """Get autocomplete suggestions with ranking"""
        words = self.search_prefix(prefix)
        
        if not words:
            return []
        
        # Filter by frequency and quality
        filtered = [
            w for w in words 
            if w['frequency'] >= min_freq and w['quality'] >= min_quality
        ]
        
        # Rank by: 1. Prefix exactness, 2. Frequency, 3. Quality
        def rank_score(word_data):
            word = word_data['word']
            freq = word_data['frequency']
            quality = word_data['quality']
            
            # Exact prefix match bonus
            prefix_bonus = 10 if word.startswith(prefix.lower()) else 0
            
            # Logarithmic frequency scaling (diminishing returns)
            freq_score = math.log1p(freq)
            
            # Quality multiplier
            quality_mult = word_data['quality']
            
            # Recency bonus (recently updated words get small boost)
            recency = (time.time() - word_data['last_updated']) / 86400  # days
            recency_bonus = max(0, 1 - (recency / 30))  # decays over 30 days
            
            return (prefix_bonus + freq_score * quality_mult + recency_bonus)
        
        # Sort by ranking score
        filtered.sort(key=rank_score, reverse=True)
        
        # Return just the words
        return [w['word'] for w in filtered[:limit]]
    
    def save_trie(self):
        """Save trie to disk"""
        try:
            with open(self.trie_file, 'wb') as f:
                pkl.dump(self.root, f)
            
            metrics = {
                'word_count': self.word_count,
                'saved_at': time.time(),
                'version': '1.0'
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f)
            
            print(f"[TRIE] Saved {self.word_count} words to {self.trie_file}")
        except Exception as e:
            print(f"[TRIE] Error saving trie: {e}")
    
    def get_stats(self):
        """Get trie statistics"""
        return {
            'total_words': self.word_count,
            'avg_frequency': self._calculate_avg_frequency(),
            'quality_distribution': self._get_quality_distribution()
        }
    
    def _calculate_avg_frequency(self):
        """Calculate average word frequency"""
        # This would require traversing the trie
        # For simplicity, we'll return a placeholder
        return self.word_count
    
    def _get_quality_distribution(self):
        """Get quality score distribution"""
        return {'placeholder': 'Would require full trie traversal'}

# ⭕ Initialize trie autocomplete system
print("[TRIE] Initializing autocomplete system...")
trie_autocomplete = TrieAutocomplete(lexicon_data=lexicon)
print("[TRIE] Autocomplete system ready")

# ⭕ INTERACTIVE AUTOCOMPLETE FUNCTION
def interactive_autocomplete():
    """Interactive mode for testing autocomplete"""
    print("\n" + "="*50)
    print("TRIE AUTOCOMPLETE MODE")
    print("Enter prefixes to get suggestions (type 'exit' to quit)")
    print("="*50)
    
    while True:
        try:
            prefix = input("\nEnter prefix: ").strip()
            if prefix.lower() == 'exit':
                break
            
            if not prefix:
                continue
            
            start_time = time.time()
            suggestions = trie_autocomplete.autocomplete(prefix, limit=10)
            elapsed = time.time() - start_time
            
            if suggestions:
                print(f"\nFound {len(suggestions)} suggestions in {elapsed*1000:.2f}ms:")
                for i, word in enumerate(suggestions, 1):
                    print(f"  {i:2}. {word}")
            else:
                print(f"\nNo suggestions found for '{prefix}'")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

# ---------------- BM25 functions ----------------
def get_barrel_info(wordID):
    if wordID not in lexicon_gzip:
        return None
    
    meta = lexicon_gzip[wordID]
    postings = []
    df = 0
    for b in meta:
        barrel_id = b['barrel_id']
        offset = b['offset']
        length_bytes = b['length_bytes']
        barrel_info = fetch_barrel_results_binary_offset(barrel_id, offset, length_bytes)
        df += len(barrel_info)
        postings.extend(barrel_info)
    return postings, df

def clean_and_lemmatize_query(words_list):
    cleaned_words = []
    for word in words_list:
        w = word.lower().strip(string.punctuation)
        if not w or not w.isascii() or not w.isalpha() or len(w) < 2 or all(c == w[0] for c in w):
            continue
        cleaned_words.append(w)
    
    # Filter out stop words before lemmatization gives more optimization
    filtered_words = [w for w in cleaned_words if w not in nlp.Defaults.stop_words]

    lemmas = []
    for doc in nlp.pipe(filtered_words, batch_size=1000):
        if len(doc) == 0:
            continue
        lemmas.append(doc[0].lemma_)
    
    return lemmas

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
            score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl)))
            scores[docID] += score

        print(f" DOC {docID} Score {scores[docID]}")

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

# ---------------- Semantic re-ranking ----------------
def semantic_rerank(query_tokens, ranked_docs, top_k=10):
    """Use GloVe embeddings to rerank BM25 results based on cosine similarity"""
    # Build query vector by averaging embeddings
    vectors = []
    for token in query_tokens:
        idx = glove_word2idx.get(token)
        if idx is not None:
            vectors.append(glove_matrix_norm[idx])
    if not vectors:
        return ranked_docs  # fallback to BM25 if no embeddings
    
    query_vec = np.mean(np.stack(vectors), axis=0)
    doc_scores = []
    
    for docID, bm25_score in ranked_docs:
        # 🔹 Build document vector (average of tokens in doc)
        doc_info = forward_index[docID]
        doc_vecs = []
        for wordID, freq in doc_info["terms"]:
            word = lexicon.get(wordID)
            if word in glove_word2idx:
                doc_vecs.append(glove_matrix_norm[glove_word2idx[word]])
        
        if not doc_vecs:
            doc_scores.append((docID, bm25_score))
            continue

        doc_vec = np.mean(np.stack(doc_vecs), axis=0)
        cosine_sim = np.dot(query_vec, doc_vec)
        combined_score = 0.7 * bm25_score + 0.3 * cosine_sim  # 🔹 combine BM25 + semantic
        doc_scores.append((docID, combined_score))
    
        print(f" DOC {docID} Score {combined_score}")

    return sorted(doc_scores, key=lambda x: x[1], reverse=True)[:top_k]

# ⭕ ENHANCED QUERYING WITH AUTOCOMPLETE SUGGESTIONS
def querying_function(query, top_k):
    start = time.time()
    
    # ⭕ Get autocomplete suggestions as user types
    print(f"\n[TRIE] Autocomplete suggestions for query:")
    query_words = query.strip().split()
    
    # Show suggestions for each word as user types
    for i, word in enumerate(query_words):
        if len(word) >= 2:  # Only suggest for words with 2+ chars
            suggestions = trie_autocomplete.autocomplete(word, limit=3)
            if suggestions:
                print(f"  '{word}': {', '.join(suggestions)}")
    
    raw_words = query.strip().split()
    tokens = clean_and_lemmatize_query(raw_words)
    print(f"\nLemmatized tokens: {tokens}")
    
    # 🟢 BM25 ranking
    ranked_docs = get_word_bm25_ranking(tokens, top_k=top_k*5)  # get more for semantic rerank
    
    # 🟢 Semantic re-ranking
    reranked_docs = semantic_rerank(tokens, ranked_docs, top_k=top_k)
    
    print("[INFO] Top ranked documents after semantic rerank:")
    for docID, score in reranked_docs:
        meta = doc_meta[docID]
        print(
            f"DocID: {docID}, Score: {score:.4f}, "
            f"Path: {doc_map[docID]}, "
            f"Title: {meta.get('title', '')}, "
            f"Authors: {', '.join(meta.get('authors', []))}, "
        )
    end = time.time()
    print(f"Query processed in {end - start:.4f} seconds")

# ⭕ ENHANCED RUN QUERY WITH AUTOCOMPLETE MODE
def run_query(top_k):
    print("\n" + "="*50)
    print("SEARCH SYSTEM WITH TRIE AUTOCOMPLETE")
    print("="*50)
    print("Options:")
    print("  1. Search with BM25 + Semantic ranking")
    print("  2. Interactive autocomplete testing")
    print("  3. Exit")
    print("="*50)
    
    while True:
        try:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                query = input("Enter your search query: ")
                if query.lower() == 'exit':
                    continue
                querying_function(query, top_k)
            
            elif choice == "2":
                interactive_autocomplete()
            
            elif choice == "3":
                print("Exiting...")
                # Save trie before exiting
                trie_autocomplete.save_trie()
                break
            
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            trie_autocomplete.save_trie()
            break
        except Exception as e:
            print(f"Error: {e}")

# ⭕ MAIN EXECUTION WITH AUTOCOMPLETE
if __name__ == "__main__":
    top_k = 10
    
    # Print trie statistics
    stats = trie_autocomplete.get_stats()
    print(f"\n[TRIE STATISTICS]")
    print(f"Total words in trie: {stats['total_words']}")
    print(f"Words in lexicon: {len(lexicon)}")
    print(f"Documents in index: {N}")
    
    run_query(top_k)