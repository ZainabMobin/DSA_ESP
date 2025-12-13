Efficient batch-based document processing for scalable indexing and search.

**Refined Pipeline**

Batch Process content -> Save in Batches with bAtchmap and DocMap -> Create Lexicon from Processed data -> Create nested forward index -> Create Inverted index -> Create barrels and lexicon with barrel postings (lexicon_with_ barrels)


DRIVE DOWNLOAD LINKS:
- Batch_Content: https://drive.google.com/drive/folders/1Zsd_K8D4pN_S7_3VCEHcUJ-gxoFMMK0z?usp=sharing
- Refined Data Structure Overview: https://docs.google.com/spreadsheets/d/1jKqQZzippl7SMyg0yTrYjWqUqTngqF5FFzuWc-p0yfM/edit?usp=sharing


## Features

- **Docmap & Batchmap:** Track documents and batches; IDs remain consistent when adding/resuming files.  
- **Batch Preprocessing:** Processes files in batches of 100 to reduce I/O overhead and improve scalability.  
- **Lexicon & Forward Index:**  
  - Forward index uses a **nested structure** (`docID → [(wordID, freq), ...]`) and is saved as `.pkl.gz`.  
  - Lexicon with **barrel postings** allows fast word lookup during runtime; barrel postings are saved as `.pkl` for fast loading.  
- **Barrels:** Split inverted index into fixed-size barrels (`barrel_size=5000`) for efficient document retrieval.  

---

## Improved Features

- Created **Lexicon with barrel postings** for fast word lookup at runtime.  
- Nested Forward and Inverted index to ensure easier and faster access per document/word.  
- `.pkl.gz` used for lexicons, forward/inverted indexes for compression, while barrels remain `.pkl` for speed.

---

## TODO

- Add **semantic search**, refine query function, add **autocomplete**  
- Add **runtime indexing** function for processing uploaded documents  
- Add relevant backend for **querying** and uploading added files to the backend server  
- Add role for **admin** (hardcoded credentials for now) to sign in and upload files  
- Add **frontend** for admin portal and file uploading from local machine