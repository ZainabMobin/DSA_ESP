import pickle, gzip, os, sys
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from loaders.forwardLoader import load_forward

INVERTED_PKL_GZ = "./processed_data/inverted_index.pkl.gz"

def build_inverted_index(forward_index):
    inverted_index = defaultdict(list)
    for docID, doc_data in forward_index.items():
        for wordID, freq in doc_data["terms"]:
            inverted_index[wordID].append((docID, freq))
    return inverted_index


def update_inverted_index():
    forward_index = load_forward()
    inverted_index = build_inverted_index(forward_index)

    os.makedirs("./processed_data", exist_ok=True)
    with gzip.open(INVERTED_PKL_GZ, "wb") as f:
        pickle.dump(dict(inverted_index), f)

    print(f"[INFO] Inverted index updated with {len(inverted_index)} entries")
    return inverted_index
