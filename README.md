
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

---

## TODO
- Add **semantic search**, refine query function, add **autocomplete**  
- Add **runtime indexing** function for processing uploaded documents  
- Add relevant backend for **querying** and uploading added files to the backend server  
- Add role for **admin** (hardcoded credentials for now) to sign in and upload files  
- Add **frontend** for admin portal and file uploading from local machine

