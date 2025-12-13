import os, sys, time, pickle, gzip

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import defaultdict
from loaders.invertedLoader import load_inverted


BARREL_SIZE = 5000  # number of documents per barrel
BARREL_FOLDER = "./processed_data/barrels/"
LEXICON_GZIP = "./processed_data/lexicon_with_barrels.pkl.gz"  # lexicon with barrel postings gzipped version

def create_barrels_with_byte_offsets(inverted_index, barrel_size=BARREL_SIZE, output_folder=BARREL_FOLDER):
    """
    Split inverted index into sorted barrels by docID ranges, save each barrel as a binary file,
    and update lexicon with byte offsets for each word's postings.
    """
    barrels = defaultdict(lambda: defaultdict(list))  # barrel_id -> wordID -> postings list
    updated_lexicon = defaultdict(list)              # wordID -> list of {barrel_id, offset, length_bytes}

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

        # Sort wordIDs
        sorted_wordIDs = sorted(barrel_data.keys())

        barrel_pkl_path = os.path.join(output_folder, f"barrel_{barrel_id}.pkl")
        with open(barrel_pkl_path, "wb") as f:

            # Write each word's postings individually
            for wordID in sorted_wordIDs:
                postings_list = barrel_data[wordID]
                
                offset = f.tell()             # current byte position
                data = pickle.dumps(postings_list, protocol=pickle.HIGHEST_PROTOCOL)
                f.write(data)
                length_bytes = len(data)

                # Store byte offset info in lexicon
                updated_lexicon[wordID].append({
                    "barrel_id": barrel_id,
                    "offset": offset,
                    "length_bytes": length_bytes
                })

        end_time = time.time()
        print(f"[TIME] Barrel {barrel_id} saved in {end_time - start_time:.4f} seconds.")
        print(f"[SAVED] Barrel {barrel_id} with {len(sorted_wordIDs)} words (.pkl)")

    # Save the updated lexicon with barrel info (byte offsets)
    with gzip.open(LEXICON_GZIP, "wb") as f:
        pickle.dump(updated_lexicon, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[INFO] Gzipped lexicon saved to {LEXICON_GZIP}")

if __name__ == "__main__":

    inverted_index = load_inverted()

    start_time = time.time()
    create_barrels_with_byte_offsets(inverted_index)
    end_time = time.time()
    print(f"[INFO] Barrel creation complete in {end_time-start_time:.3f} s")