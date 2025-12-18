import os
import time
from preprocessor import dynamic_preprocess
from lexiconGenerator import update_lexicon
from forwardGenerator import update_forward_index
from invertedGenerator import build_inverted_index

if __name__ == "__main__":  # <--- Windows-safe entry point

    print("[INFO] Starting dynamic indexing process...")

    # ---------------- STEP 1: Preprocess new documents ----------------
    folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../new_docs"))
    print("[DEBUG] Looking for new documents in:", folder_path)

    new_batches = dynamic_preprocess(folder_path)  # returns list of (batchID, batch_path)

    if not new_batches:
        print("[INFO] No new documents found. Exiting.")
        exit(0)

    print(f"[INFO] {len(new_batches)} new batches created.")

    # ---------------- STEP 2: Update lexicon ----------------
    print("[STEP 2] Updating lexicon...")
    lexicon = update_lexicon(new_batches)  # accepts list of (batchID, path)
    print(f"[INFO] Lexicon now contains {len(lexicon)} unique terms.")

    # ---------------- STEP 3: Update forward index ----------------
    print("[STEP 3] Updating forward index...")
    forward_index = update_forward_index(new_batches, lexicon)
    print(f"[INFO] Forward index updated. Total docs: {len(forward_index)}")

    # ---------------- STEP 4: Build inverted index ----------------
    print("[STEP 4] Building inverted index...")
    inverted_index = build_inverted_index(forward_index)
    print("[INFO] Dynamic indexing completed successfully!")
    print(f"[INFO] Total documents indexed: {len(forward_index)}")
    print(f"[INFO] Total unique terms in lexicon: {len(lexicon)}")
    print(f"[INFO] Total terms in inverted index: {len(inverted_index)}")
