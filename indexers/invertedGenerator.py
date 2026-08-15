import time, os, sys
# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pickle, gzip
from collections import defaultdict
from loaders.forwardLoader import load_forward


INVERTED_PKL_GZ = "./processed_data/inverted_index.pkl.gz"

def build_inverted_index(forward_index):
    """
    Build inverted index from nested forward index.
    forward_index: dict of docID -> list of (wordID, freq)
    Returns: dict of wordID -> list of (docID, freq)
    """
    inverted_index = defaultdict(list)
    for docID, doc_data in forward_index.items():
        word_list = doc_data["terms"]
        for wordID, freq in word_list:
            inverted_index[wordID].append((docID, freq))
    return inverted_index

def save_inverted_index_gzip(inverted_index, filepath):
    with gzip.open(filepath, "wb") as f:  
        pickle.dump(dict(inverted_index), f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    os.makedirs("./processed_data", exist_ok=True)

    forward_index = load_forward()
    start = time.time()

    inverted_index = build_inverted_index(forward_index)

    print(f"[INFO] Inverted index built with {len(inverted_index)} entries")

    save_inverted_index_gzip(inverted_index, INVERTED_PKL_GZ)
    print(f"[INFO] Inverted index saved to {INVERTED_PKL_GZ}")

    # Print first entry for verification
    first_entry = next(iter(inverted_index.items()))
    print("[INFO] Sample inverted index entry:", first_entry)

    print(f"[INFO] Total time taken: {time.time() - start:.2f} seconds")