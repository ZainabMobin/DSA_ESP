# import csv
# import pickle
# from collections import defaultdict
# import time
# import os

# FORWARD_CSV = "./processed_data/forward_index.csv"
# INVERTED_PKL = "./processed_data/inverted_index.pkl"
# INVERTED_CSV = "./processed_data/inverted_index.csv"

# def build_inverted_index(forward_csv):
#     inverted_index = defaultdict(list)
#     with open(forward_csv, "r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             docID = int(row["docID"])
#             wordID = int(row["wordID"])
#             freq = int(row["frequency"])
#             inverted_index[wordID].append((docID, freq))
#     return inverted_index

# def save_inverted_index_pickle(inverted_index, filepath):
#     with open(filepath, "wb") as f:
#         pickle.dump(inverted_index, f)

# def save_inverted_index_csv(inverted_index, filepath):
#     with open(filepath, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["wordID", "postings"])  #postings as string
#         for wordID, postings in inverted_index.items():
#             postings_str = ";".join(f"{doc}:{freq}" for doc, freq in postings)
#             writer.writerow([wordID, postings_str])

# if __name__ == "__main__":
#     os.makedirs("./processed_data", exist_ok=True)
#     start = time.time()
#     print("[INFO] Building inverted index from forward index...")
#     inverted = build_inverted_index(FORWARD_CSV)
#     print(f"[INFO] Built inverted index with {len(inverted)} entries")

#     print("[INFO] Saving inverted index to pickle...")
#     save_inverted_index_pickle(inverted, INVERTED_PKL)

#     print("[INFO] Saving inverted index to CSV...")
#     save_inverted_index_csv(inverted, INVERTED_CSV)

#     print(f"[INFO] Inverted index saved. Time taken: {time.time() - start:.2f} seconds")

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
    for docID, word_list in forward_index.items():
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