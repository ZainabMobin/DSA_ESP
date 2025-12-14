import os, time
import pickle, gzip

DOCMETA_GZIP = "./processed_data/doc_meta.pkl.gz"
DOCMAP_GZIP = "./processed_data/doc_map.pkl.gz"
BATCHMAP_GZIP = "./processed_data/batch_map.pkl.gz"

#for backup checks
# DOCMAP_GZIP = "D:/processed_data/doc_map.pkl.gz"
# BATCHMAP_GZIP = "D:/processed_data/batch_map.pkl.gz"

os.makedirs("./batch_contents", exist_ok=True)

def load_docmap():
    """Load the docmap from gzip pickle. Returns {docID: filepath}"""
    if not os.path.exists(DOCMAP_GZIP):
        return {}
    try:
        with gzip.open(DOCMAP_GZIP, "rb") as f:
            docmap = pickle.load(f)
        return docmap
    except Exception as e:
        print(f"[WARN] Failed to load docmap: {e}")
        return {}


def load_batchmap():
    """Load the batchmap from gzip pickle. Returns {batchID: batch_path}"""
    if not os.path.exists(BATCHMAP_GZIP):
        return {}
    try:
        with gzip.open(BATCHMAP_GZIP, "rb") as f:
            batchmap = pickle.load(f)
        return batchmap
    except Exception as e:
        print(f"[WARN] Failed to load batchmap: {e}")
        return {}


def load_docmeta():
    if not os.path.exists(DOCMETA_GZIP):
        print("[WARN] doc_meta file not found.")
        return {}
    with gzip.open(DOCMETA_GZIP, "rb") as f:
        docmeta = pickle.load(f)
    return docmeta


if __name__ == "__main__":

    start = time.time()
    docmap = load_docmap()
    end = time.time()

    print(f"[INFO] Loaded docmap in {end - start:.4f} seconds")
    for key, value in list(docmap.items())[1]:
        print(f"docID: {key}, Filepath: {value}")
    
    
    start = time.time()
    batchmap = load_batchmap()
    end = time.time()

    print(f"[INFO] Loaded batchmap in {end - start:.4f} seconds")
    for key, value in list(batchmap.items())[1]:
        print(f"BatchID: {key}, Filepath: {value}")


    start = time.time()
    docmeta = load_docmeta()
    end = time.time()
        
    print(f"[INFO] Loaded docmeta in {end - start:.4f} seconds")
    for key, value in list(docmeta.items())[:1]:
        print(f"docID: {key}, meta-data: {value}") 