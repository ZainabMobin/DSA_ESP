import os, sys, time

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pickle, gzip
from collections import defaultdict
from loaders.invertedLoader import load_inverted

BARREL_SIZE = 5000  # number of documents per barrel
BARREL_FOLDER = "./processed_data/barrels/"
LEXICON_GZIP = "./processed_data/lexicon_with_barrels.pkl.gz"# lexicon with barrel postings gzipped version

def create_barrels(inverted_index, barrel_size=BARREL_SIZE, output_folder=BARREL_FOLDER):
    """
    Split inverted index into sorted barrels by docID ranges, save as pickle and CSV,
    and update the lexicon with barrel information including start_idx.
    """
    barrels = defaultdict(lambda: defaultdict(list))  # barrel_id -> wordID -> postings list
    updated_lexicon = defaultdict(list)              # wordID -> list of {barrel_id, start_idx, length}

    print("[INFO] Splitting inverted index into barrels...")

    # Step 1: Assign postings to the correct barrel
    for wordID, postings in inverted_index.items():
        for docID, freq in postings:
            barrel_id = docID // barrel_size
            barrels[barrel_id][wordID].append((docID, freq))

    os.makedirs(output_folder, exist_ok=True)

    print(f"[INFO] Saving sorted barrels to folder: {output_folder}")
    for barrel_id, barrel_data in barrels.items():
        start_time = time.time()

        # Sort postings inside each wordID by docID
        for wordID in barrel_data:
            barrel_data[wordID].sort(key=lambda x: x[0])

        # Sort wordIDs in this barrel
        sorted_wordIDs = sorted(barrel_data.keys())

        # build flat barrel for correct start_idx ---
        barrel_postings = []  # flat list of all postings in this barrel
        for wordID in sorted_wordIDs:
            postings_list = barrel_data[wordID]
            start_idx = len(barrel_postings)   # starting position in flat list
            length = len(postings_list)

            # Append postings to flat barrel
            for docID, freq in postings_list:
                barrel_postings.append((wordID, docID, freq))

            # Update lexicon
            updated_lexicon[wordID].append({
                "barrel_id": barrel_id,
                "start_idx": start_idx,
                "length": length
            })

        # Save PICKLE (flat list)
        barrel_pkl_path = os.path.join(output_folder, f"barrel_{barrel_id}.pkl")
        with open(barrel_pkl_path, "wb") as f:
            pickle.dump(barrel_postings, f, protocol=pickle.HIGHEST_PROTOCOL)

        end_time = time.time()
        print(f"[TIME] Barrel {barrel_id} saved in {end_time - start_time:.4f} seconds.")
        print(f"[SAVED] Barrel {barrel_id} with {len(sorted_wordIDs)} sorted wordIDs (.pkl)")

    # Save the updated lexicon with barrel info
    with gzip.open(LEXICON_GZIP, "wb") as f:
        pickle.dump(updated_lexicon, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[INFO] Gzipped lexicon saved to {LEXICON_GZIP}")


if __name__ == "__main__":

    inverted_index = load_inverted()

    start_time = time.time()
    create_barrels(inverted_index)
    end_time = time.time()
    print(f"[INFO] Barrel creation complete in {end_time-start_time:.3f} s")