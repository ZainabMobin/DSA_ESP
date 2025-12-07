import os
import pickle
import csv
from collections import defaultdict

BARREL_SIZE = 5000  #number of documents per barrel
BARREL_FOLDER = "./processed_data/barrels/"

def create_barrels(inverted_index, barrel_size=BARREL_SIZE, output_folder=BARREL_FOLDER):
    """
    Split inverted index into barrels by docID ranges and save as both pickle and CSV.

    Args:
        inverted_index: dict {wordID: list of (docID, freq)}
        barrel_size: int, number of docs per barrel
        output_folder: str, directory to save barrel files
    """
    barrels = defaultdict(lambda: defaultdict(list))
    #barrels[barrel_id][wordID] = list of (docID, freq)

    print("[INFO] Splitting inverted index into barrels...")

    for wordID, postings in inverted_index.items():
        for docID, freq in postings:
            barrel_id = docID // barrel_size
            barrels[barrel_id][wordID].append((docID, freq))

    os.makedirs(output_folder, exist_ok=True)

    print(f"[INFO] Saving barrels to folder: {output_folder}")
    for barrel_id, barrel_data in barrels.items():
        #save pickle
        barrel_pkl_path = os.path.join(output_folder, f"barrel_{barrel_id}.pkl")
        with open(barrel_pkl_path, "wb") as f:
            pickle.dump(barrel_data, f)

        #save CSV
        barrel_csv_path = os.path.join(output_folder, f"barrel_{barrel_id}.csv")
        with open(barrel_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["wordID", "docID", "frequency"])

            for wordID, postings_list in barrel_data.items():
                for docID, freq in postings_list:
                    writer.writerow([wordID, docID, freq])

        print(f"[SAVED] Barrel {barrel_id} with {len(barrel_data)} unique wordIDs (pickle + CSV).")

if __name__ == "__main__":
    inverted_pkl = "./processed_data/inverted_index.pkl"
    if not os.path.exists(inverted_pkl):
        print(f"[ERROR] Inverted index file not found: {inverted_pkl}")
        exit(1)

    print(f"[INFO] Loading inverted index from {inverted_pkl} ...")
    with open(inverted_pkl, "rb") as f:
        inverted_index = pickle.load(f)

    create_barrels(inverted_index)
    print("[INFO] Barrel creation complete.")
