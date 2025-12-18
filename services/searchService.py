# # BM25 + Semantic Re-ranking using GloVe vectors
# import spacy, time, sys, os, string
# from collections import defaultdict
# import math
# import numpy as np

# # Add project root to path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip
# from loaders.barrelLoader import fetch_barrel_results_binary_offset
# from loaders.forwardLoader import load_forward
# from loaders.mapLoaders import load_docmeta, load_docmap
# from loaders.gloveLoader import load_glove_matrix

# start = time.time()
# # 🔹 Load indices
# lexicon_gzip = load_lexicon_posting_gzip()
# lexicon = load_lexicon()
# forward_index = load_forward()
# doc_meta = load_docmeta()
# doc_map = load_docmap()
# glove_words, glove_matrix = load_glove_matrix()

# end = time.time()

# print(f"Total time: {end-start:.2f} (to load lexicon, forward, lexicon with barrels, docmap, batchmap, glove matrix)")

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

# # QUERYING FUNCTION CALLED FROM BACKEND
# def main_querying_function(query, top_k):
#     start = time.time()
    
#     raw_words = query.strip().split()
#     tokens = clean_and_lemmatize_query(raw_words)
#     print(f"\nLemmatized tokens: {tokens}")
    
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

#     # Build results with metadata
#     results = []
#     for docID, score in reranked_docs:
#         meta = doc_meta.get(docID, {})
#         results.append({
#             "docID": docID,
#             "score": round(score, 4),
#             "path": doc_map.get(docID, ""),
#             "title": meta.get("title", ""),
#             "authors": meta.get("authors", []),
#         })

#     end = time.time()
#     print(f"Query processed in {end - start:.4f} seconds")
#     return results

# # ⭕ MAIN EXECUTION WITH AUTOCOMPLETE
# if __name__ == "__main__":
#     top_k = 10
    
#     print(f"Words in lexicon: {len(lexicon)}")

# BM25 + Semantic Re-ranking using GloVe vectors
import spacy, time, sys, os, string
from collections import defaultdict
import math
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loaders.barrelLoader import fetch_barrel_results_binary_offset

# Load spaCy model for lemmatization
nlp = spacy.load("en_core_web_sm")


# ---------------- BM25 functions ----------------
def get_barrel_info(wordID, lexicon_gzip):
    if wordID not in lexicon_gzip:
        return None, 0
    
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


def get_word_bm25_ranking(query_tokens, lexicon, lexicon_gzip, forward_index, top_k=10):
    # 🔹 BM25 parameters

    N = len(forward_index)
    avgdl = sum(doc["length"] for doc in forward_index.values()) / N 
    k1 = 1.5
    b = 0.75

    scores = defaultdict(float)
    for token in query_tokens:
        wordID = lexicon.get(token)
        if not wordID:
            continue
        postings, df = get_barrel_info(wordID, lexicon_gzip)
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
def semantic_rerank(query_tokens, ranked_docs, forward_index, lexicon, glove_words, glove_matrix, top_k=10):
    """Use GloVe embeddings to rerank BM25 results based on cosine similarity"""

        # 🔹 build word → index mapping
    glove_word2idx = {w: i for i, w in enumerate(glove_words)}

    # 🔹 Normalize vectors once for cosine similarity
    glove_matrix_norm = glove_matrix / np.linalg.norm(glove_matrix, axis=1, keepdims=True)

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

# QUERYING FUNCTION CALLED FROM BACKEND
def main_querying_function(query, context, top_k):

    forward_index = context.forward_index
    doc_meta = context.doc_meta
    doc_map = context.doc_map
    lexicon_gzip = context.lexicon_gzip

    lexicon = context.lexicon
    glove_words = context.glove_words
    glove_matrix = context.glove_matrix

    start = time.time()
    
    raw_words = query.strip().split()
    tokens = clean_and_lemmatize_query(raw_words)
    print(f"\nLemmatized tokens: {tokens}")
    
    # 🟢 BM25 ranking
    ranked_docs = get_word_bm25_ranking(tokens, lexicon, lexicon_gzip, forward_index, top_k=top_k*5)  # get more for semantic rerank
    
    # 🟢 Semantic re-ranking
    reranked_docs = semantic_rerank(tokens, ranked_docs, forward_index, lexicon, glove_words, glove_matrix, top_k=top_k)
    
    print("[INFO] Top ranked documents after semantic rerank:")
    for docID, score in reranked_docs:
        meta = doc_meta.get(docID, {}) # returns empty dict if missing
        path = doc_map.get(docID, "N/A")  # in case doc_map missing too
        
        print(
            f"DocID: {docID}, Score: {score:.4f}, "
            f"Path: {doc_map[docID]}, "
            f"Title: {meta.get('title', '')}, "
            f"Authors: {', '.join(meta.get('authors', []))}, "
            f"Date: {meta.get('publish_time', '')}, "
            f"URL: {meta.get('url', '')}, "
        )

    # Build results with metadata
    results = []
    for docID, score in reranked_docs:
        meta = doc_meta.get(docID, {})
        results.append({
            "docID": docID,
            "score": round(score, 4),
            "path": doc_map.get(docID, ""),
            "title": meta.get("title", ""),
            "authors": meta.get("authors", []),
            "publish_time": meta.get("publish_time", ""),
            "url": meta.get("url", "")
        })

    end = time.time()
    print(f"[SEARCH SERVICE] Query processed in {end - start:.4f} seconds")
    return results


# # ⭕ MAIN EXECUTION WITH AUTOCOMPLETE
# if __name__ == "__main__":
#     top_k = 10
    
#     print(f"Words in lexicon: {len(lexicon)}")