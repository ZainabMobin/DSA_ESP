import csv
import pickle
from collections import defaultdict
import time
import os

FORWARD_CSV = "./processed_data/forward_index.csv"
INVERTED_PKL = "./processed_data/inverted_index.pkl"
INVERTED_CSV = "./processed_data/inverted_index.csv"

def build_inverted_index(forward_csv):
    inverted_index = defaultdict(list)
    with open(forward_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            docID = int(row["docID"])
            wordID = int(row["wordID"])
            freq = int(row["frequency"])
            inverted_index[wordID].append((docID, freq))
    return inverted_index

def save_inverted_index_pickle(inverted_index, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(inverted_index, f)

def save_inverted_index_csv(inverted_index, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["wordID", "postings"])  #postings as string
        for wordID, postings in inverted_index.items():
            postings_str = ";".join(f"{doc}:{freq}" for doc, freq in postings)
            writer.writerow([wordID, postings_str])

if __name__ == "__main__":
    os.makedirs("./processed_data", exist_ok=True)
    start = time.time()
    print("[INFO] Building inverted index from forward index...")
    inverted = build_inverted_index(FORWARD_CSV)
    print(f"[INFO] Built inverted index with {len(inverted)} entries")

    print("[INFO] Saving inverted index to pickle...")
    save_inverted_index_pickle(inverted, INVERTED_PKL)

    print("[INFO] Saving inverted index to CSV...")
    save_inverted_index_csv(inverted, INVERTED_CSV)

    print(f"[INFO] Inverted index saved. Time taken: {time.time() - start:.2f} seconds")
