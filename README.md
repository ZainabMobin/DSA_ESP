Document Processing Pipeline: Efficient batch-based document processing for scalable indexing and search.

DRIVE DOWNLOAD LINKS:
- Full forward Index: https://drive.google.com/file/d/13HByszFfK3bbwCB8krjHAvZkSTk5KxEW/view?usp=drive_link
- Batch_Content: https://drive.google.com/drive/folders/1Zsd_K8D4pN_S7_3VCEHcUJ-gxoFMMK0z?usp=sharing
- for inverted index run the invertedGenerator.py file in loader 
- for barrell builder  run the build_barrels  file in loader 
- also u can adjust total doc per barrel  by changig size in initial of build barrel.py file 
 BARREL_SIZE = 5000  #number of documents per barrel

**Features**

Docmap & Batchmap: Track documents and batches; IDs remain consistent when adding/resuming files.

Batch Preprocessing: Processes files in batches of 100 to reduce I/O overhead and improve scalability.

Lexicon & Forward Index: Fast generation; .pkl files give ~3x compression over JSON.

Performance
Step	Time
Batch preprocessing (all files)	3–4 hrs
Lexicon generation	21 s
Forward index creation	90 s

Batching ensures smooth processing and avoids disk I/O issues with large datasets.
