
**Refined Pipeline**

Batch Process content -> Save in Batches with bAtchmap and DocMap -> Create docmeta from docmap -> Create Lexicon from Processed data -> Create nested forward index -> Create Inverted index -> Create barrels and lexicon with barrel postings (lexicon_with_ barrels)


**DRIVE DOWNLOAD LINKS:**
- Batch_Content: https://drive.google.com/drive/folders/1Zsd_K8D4pN_S7_3VCEHcUJ-gxoFMMK0z?usp=sharing
- Refined Data Structure Overview: https://docs.google.com/spreadsheets/d/1jKqQZzippl7SMyg0yTrYjWqUqTngqF5FFzuWc-p0yfM/edit?usp=sharing


## Features

- Efficient **batch-based document processing** for scalable indexing and search.
- **Docmap & Batchmap:** Track documents and batches; IDs remain consistent when adding/resuming files.  
- **Batch Preprocessing:** Processes files in batches of 100 to reduce I/O overhead and improve scalability.  
- **Docmeta:** maps relevant meta data against docID
- **Lexicon & Forward Index:**  
  - Forward index uses a **nested structure** (`docID → [(wordID, freq), ...]`) for faster access per document/word
  
  - Lexicon with **barrel postings** allows fast word lookup during runtime 
- **Barrels:** Split inverted index into fixed-size barrels (`barrel_size=5000`) for efficient document retrieval

- `.pkl.gz` used for lexicons, forward/inverted indexes for compression, while barrels remain `.pkl` for speed.

---
## Updates

### Preprocessor
- Checks if a file path is already in the `docmap`; if yes, skips processing.
- Saves `docmap` and `batchmap` in **gzip** format for efficient storage.
- Adds `doc-meta` for file metadata including **title** and **authors**, mapped to `docID`.

### Search Algorithm
- Implements a **query search** function:
  - Takes input words and **cleans/lemmatizes** them.
  - Retrieves postings from the `lexicon_with_barrel`.
  - Computes frequencies from the **forward index**.
  - Calculates **BM25 ranking**.
  - Returns **top-k results** for the query.

### Summary
These updates improve preprocessing efficiency, add metadata tracking, and provide a full-text search capability with ranked results.
- Added **semantic search**, refine query function, add **autocomplete**  
- metadata.csv not read because there's no guarentee that it will be uploaded along with teh dynamic files. Reduces tight coupling
---

## TODO
- Add **runtime indexing** function for processing uploaded documents  
- Add relevant backend for **querying** and uploading added files to the backend server  
- Add role for **admin** (hardcoded credentials for now) to sign in and upload files  
- Add **frontend** for admin portal and file uploading from local machine



pre-trained GloVe embeddings and implement semantic similarity logic manually using cosine similarity
“Pre-trained GloVe vectors were converted to a compressed binary format to reduce memory footprint and speed up system initialization.”

NumPy is fastest because it stores float32 vectors in contiguous C memory and performs math in compiled code instead of Python.

Save two files instead of one (word, vectors)
The order is preserved because words and vectors are created and saved in the same loop, making index i the permanent link between them.

No Python dict overhead (saves ~30–40% space)

⚡ Pure float32 matrix → fastest cosine similarity

🔒 Order is guaranteed: words[i] ↔ matrix[i]

🚀 Easier memory-mapping & scaling later

Separating words and vectors removes Python dict overhead while preserving order, giving you smaller storage and faster vector math.

FULL PIPELINE SUMMARY (High-Level)
Stage	Description
1. Input	User enters a query
2. Preprocessing	Clean + lemmatize query
3. BM25 Retrieval	Fast lexical search over inverted index
4. Candidate Pool	Top 50 BM25 docs (if top_k=10)
5. Semantic Reranking	GloVe-based cosine similarity
6. Hybrid Score	70% BM25 + 30% semantic
7. Final Ranking	Top_k results returned
8. Metadata Display	Title, authors, path

1. User enters a query
The pipeline starts when the user types something like:

Code
Enter your search query: machine learning algorithms
This string is passed to:

python
querying_function(query, top_k)
🔵 2. Query preprocessing
2.1 Tokenization
python
raw_words = query.strip().split()
Splits into:

Code
["machine", "learning", "algorithms"]
2.2 Cleaning + Lemmatization
clean_and_lemmatize_query() does:

lowercase

remove punctuation

remove non-alphabetic

remove weird tokens

spaCy lemmatization

Example:

Code
["machine", "learning", "algorithm"]
These are your final query tokens.

🔵 3. BM25 Retrieval (Lexical Search)
3.1 For each token
You look up its wordID in the lexicon:

python
wordID = lexicon.get(token)
If the word exists, you fetch its postings list:

python
postings, df = get_barrel_info(wordID)
This retrieves:

all documents containing the word

term frequency (tf) for each doc

document frequency (df)

3.2 BM25 scoring
For each (docID, tf) pair:

python
score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl)))
scores[docID] += score
Where:

idf = inverse document frequency

tf = term frequency

dl = document length

avgdl = average document length

3.3 BM25 output
You sort by score and keep the top:

python
ranked_docs = get_word_bm25_ranking(tokens, top_k * 5)
You intentionally fetch more (5×) because semantic reranking needs a larger pool.

🔵 4. Semantic Re-ranking (GloVe Embeddings)
This is the second stage.

4.1 Build query vector
For each query token:

check if it exists in GloVe

retrieve its normalized embedding

average them:

query_vec = mean(glove_vectors)
This gives a semantic representation of the query.

4.2 Build document vectors

For each BM25 candidate document:

get its term list from forward_index[docID]["terms"]

convert each term to a word using lexicon.get(wordID)

if the word exists in GloVe, add its embedding

Then average:

doc_vec = mean(doc_glove_vectors)

4.3 Compute cosine similarity

cosine_sim = dot(query_vec, doc_vec)

4.4 Combine BM25 + semantic score

combined_score = 0.7 * bm25_score + 0.3 * cosine_sim

This gives a hybrid ranking:

- 70% lexical relevance

- 30% semantic similarity

4.5 Sort and keep top_k
python
reranked_docs = sorted(doc_scores, reverse=True)[:top_k]
These are your final results.

🔵 5. Final Output
For each document:

docID
combined score
file path
title
authors

Printed as:
DocID: 123, Score: 4.3921, Path: /docs/abc.pdf, Title: Deep Learning