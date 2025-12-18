import pickle, gzip, os, time, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from loaders.mapLoaders import load_docmap

RAW_META_GZIP = "./processed_data/raw_metadata.pkl.gz"
DOCMETA_GZIP = "./processed_data/doc_meta.pkl.gz"

if __name__ == "__main__":

    start = time.time()

    # Load docmap (docID -> filepath)
    docmap = load_docmap()

    # Build sha -> docID map
    sha_to_docid = {}
    for docID, filepath in docmap.items():
        sha = os.path.splitext(os.path.basename(filepath))[0]
        sha_to_docid[sha] = docID

    # Load raw metadata (sha -> meta)
    st = time.time()
    with gzip.open(RAW_META_GZIP, "rb") as f:
        raw_meta = pickle.load(f)
    end = time.time()

    print(f"Loaded raw_metadata in {end-st:.2f} s")

    # Build docmeta (docID -> meta)
    docmeta = {}
    for sha, meta in raw_meta.items():
        docID = sha_to_docid.get(sha)
        if docID is not None:
            docmeta[docID] = meta

    # Save docmeta
    with gzip.open(DOCMETA_GZIP, "wb") as f:
        pickle.dump(docmeta, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"[INFO] docmeta saved to {DOCMETA_GZIP}")
    print(f"[INFO] time taken: {time.time() - start:.2f} s")
