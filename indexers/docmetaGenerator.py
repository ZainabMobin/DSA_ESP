import sys, os, time, pickle, gzip
from multiprocessing import Pool, cpu_count

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loaders.mapLoaders import load_docmap
from preprocessor import extract_metadata_only

DOCMETA_GZIP = "./processed_data/doc_meta.pkl.gz"

def process_doc(args):
    """Helper function for multiprocessing"""
    docID, fp = args
    meta = extract_metadata_only(fp)
    return docID, {
        "title": meta.get("title", ""),
        "authors": meta.get("authors", [])
    }


def create_meta_doc():
    """ Creates meta_doc which has relevant metadata for a document against its docID """
    docmap = load_docmap()  # {docID: filepath}

    args_list = list(docmap.items())

    # Use number of cores minus 1 to avoid freezing
    n_workers = max(1, cpu_count() - 1)
    print(f"[INFO] Using {n_workers} worker processes...")

    with Pool(n_workers) as pool:
        results = pool.map(process_doc, args_list)

    # Collect results into a dictionary
    docmeta = dict(results)

    # Atomic write to gzip
    tmp_path = DOCMETA_GZIP + ".tmp"
    print(f"[INFO] Writing metadata to {DOCMETA_GZIP} (atomic)...")
    with gzip.open(tmp_path, "wb") as f:
        pickle.dump(docmeta, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmp_path, DOCMETA_GZIP)
    print(f"[INFO] Metadata successfully written!")


if __name__ == "__main__":
    start = time.time()
    create_meta_doc()
    end = time.time()
    print(f"[INFO] Time taken: {end - start:.2f} s")
