
**Refined Pipeline**

Batch Process content -> Save in Batches with bAtchmap and DocMap -> Create docmeta (title, authors, url, year) from docmap -> Create Lexicon from Processed data -> Create nested forward index -> Create Inverted index -> Create barrels and lexicon with barrel postings (lexicon_with_ barrels)


**DRIVE DOWNLOAD LINKS:**

- Batch_Content: https://drive.google.com/drive/folders/1Zsd_K8D4pN_S7_3VCEHcUJ-gxoFMMK0z?usp=sharing
- Updated processed_data: https://drive.google.com/file/d/1OCBj_PRGXN8H74Qg5Fl06wUTxAkq5Tcx/view?usp=sharing
- Additional files for adding into the dataset: https://drive.google.com/file/d/1jsFo2-hH6wUBKkGCIZABirbIRsnnAyAX/view?usp=drive_link 
- Refined Data Structure Overview with Metrics: https://docs.google.com/spreadsheets/d/1jKqQZzippl7SMyg0yTrYjWqUqTngqF5FFzuWc-p0yfM/edit?usp=sharing

---
## Updates

- Read metadata.csv (converted to .pkl.gz for efficiency) for meta data extraction instead of relying on doc text parses (tight coupling and not really suitable for added random parses without entries in the metadata)
- Fully implemented autocompete logic with last word suggestions
- Querying function time went up drastically (from 20ms to 800ms for single word, most probaly becaues of more fields in the metadata. 5 word query timed to be 1.2s < 1.5 s)
- Added all metadata fields to search results (docID, score, path, title, authors, publish_time, url) and ensured missing values are handled safely

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
- **Query Search Function:**  
  - Cleans and lemmatizes user input.  
  - Retrieves postings and computes frequencies from forward index.  
  - Calculates **BM25 ranking** and selects top candidates for reranking.
- **Semantic Reranking:**  
  - Uses **GloVe embeddings** to build query and document vectors.  
  - Computes **cosine similarity** to capture semantic relevance.  
  - Combines scores: **70% BM25 + 30% semantic** for hybrid ranking.
- **Autocomplete (Trie-based):**  
  - Loads or builds a **Trie** from lexicon.  
  - Inserts words with metrics: `frequency`, `doc_frequency`, `quality_score`, `last_updated`.  
  - Provides **prefix search** and ranked suggestions.  
  - Saves Trie to disk in **pkl.gz** for fast future loads.

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
  - Performs **semantic reranking** using **GloVe embeddings**:
    - Builds query and document vectors.
    - Computes cosine similarity.
    - Combines **70% BM25 + 30% semantic score** for hybrid ranking.
  - Returns **top-k results** with **title, authors, and path**.

### Trie Autocomplete
- Loads or builds a **Trie** from the lexicon.
- Inserts words with metrics:
  - `frequency` (term occurrences)
  - `doc_frequency` (number of documents)
  - `quality_score` (confidence metric)
  - `last_updated` timestamp
- Provides **prefix search** and ranked **autocomplete suggestions**.
- Saves the trie to disk in **pkl.gz** format for fast future loads.


---

## Update Details
**Main Querying Function**

1. Input	User enters a query
2. Preprocessing	Clean + lemmatize query
3. BM25 Retrieval	Fast lexical search over inverted index
4. Candidate Pool	Top 50 BM25 docs (if top_k=10)
5. Semantic Reranking	GloVe-based cosine similarity
6. Hybrid Score	70% BM25 + 30% semantic
7. Final Ranking	Top_k results returned
8. Metadata Display	Title, authors, path


User submits a query string

Query is tokenized, cleaned, and lemmatized

BM25 retrieves top lexical matches

Semantic reranking refines results using GloVe embeddings

Hybrid score combines BM25 + cosine similarity

Final ranked documents returned with metadata

- Query Preprocessing

Tokenize query into individual terms

["machine", "learning", "algorithms"]

- Clean + lemmatize tokens

["machine", "learning", "algorithm"]
BM25 Retrieval
Lookup tokens in lexicon → get wordID

- Fetch postings lists (tf, df)

- Compute BM25 score

    score = idf * ((tf*(k1+1)) / (tf + k1*(1 - b + b*dl/avgdl)))

- Sort by BM25 score

Keep top candidates (top_k * 5)

- Semantic Re-ranking

Compute query vector (avg GloVe embeddings)

Compute document vectors

Compute cosine similarity

- Hybrid score:

    combined_score = 0.7 * bm25_score + 0.3 * cosine_sim

Keep final top_k documents

- Results

Each result includes:

    docID
    Combined score
    File path
    Title
    Authors

Example:

    DocID: 123
    Score: 4.3921
    Path: /docs/abc.pdf
    Title: Deep Learning
    Authors: Ian Goodfellow, Yoshua Bengio


**Semantic Search: GloVe**

pre-trained GloVe embeddings and implement semantic similarity logic manually using cosine similarity, converted to a compressed binary format to reduce memory footprint and speed up system initialization.

NumPy is fastest because it stores float32 vectors in contiguous C memory and performs math in compiled code instead of Python.

Save two files instead of one (word, vectors)

The order is preserved because words and vectors are created and saved in the same loop, making index i the permanent link between them.

No Python dict overhead (saves ~30–40% space)

Pure float32 matrix → fastest cosine similarity

Order is guaranteed: words[i] ↔ matrix[i]

Easier memory-mapping & scaling later

Separating words and vectors removes Python dict overhead while preserving order, giving you smaller storage and faster vector math.


**Trie Logic and Flow**

1. Lexicon Load      Load lexicon and lexicon_gzip from disk
2. Trie Initialization   Create TrieAutocomplete object with empty root node
3. Load or Build Trie    Try loading existing trie from trie_data.pkl.gz; if missing/empty/fails, build from lexicon
4. Build from Lexicon    Iterate words → get doc frequencies → insert each word with metrics (frequency, doc_freq, quality_score, last_updated)
5. Insert Word           Traverse trie nodes per character; mark end node; update metrics if word exists
6. Save Trie             Serialize trie to disk using pickle + gzip for faster future loads
7. Search Prefix         Traverse trie to prefix node; collect all descendant words
8. Autocomplete          Filter by frequency/quality; rank by prefix match, frequency, quality, recency; return top suggestions

- Trie Confidence Metric (`quality_score`)

Each word in the trie has an associated `quality_score`, representing the confidence or reliability of the word for autocomplete suggestions. This metric is used to rank suggestions when multiple words match a prefix.

**Definition:**

- `quality_score` is a floating-point value (default `1.0` for new words).
- Higher values indicate **more reliable or frequently relevant terms**.
- Can be updated dynamically based on:
  - **Frequency of usage**: Words that appear more often in the indexed corpus get higher scores.
  - **Document coverage**: Words appearing in more documents increase reliability.
  - **User interaction (optional)**: If the system tracks which suggestions are selected, those words can have their score incremented.
  
**Usage in Autocomplete:**

- When generating suggestions, words are filtered and ranked by:
  1. Prefix match
  2. Term frequency
  3. `quality_score`
  4. Recency (`last_updated`)
- Words below a minimum `quality_score` threshold can be excluded to reduce noise.

### Summary
These updates improve preprocessing efficiency, add metadata tracking, and provide a full-text search capability with ranked results.
- Added **semantic search**, refine query function, add **autocomplete**  
- metadata.csv not read because there's no guarentee that it will be uploaded along with the dynamic files. Reduces tight coupling
---

## TODO
- Add **runtime indexing** function for processing uploaded documents  
- Add role for **admin** (hardcoded credentials for now) to sign in and upload files  
- Add relevant backend for uploading added files to the backend server  
- Add **frontend** for admin portal and file uploading from local machine
- Refine Autocomplete function and integrate backend with frontend