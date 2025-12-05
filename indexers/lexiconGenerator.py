from multiprocessing import Pool, cpu_count
from preprocessor import load_batchmap
import time, os, csv, pickle


def process_batch(batch_tuple):
    """
    Read a batch pickle and return a SET of lemmas from that batch.
    """
    batchID, fp = batch_tuple

    try:
        batch_docs = pickle.load(open(fp, "rb"))
    except Exception as e:
        print(f"[ERROR] Failed to load batch {batchID}: {e}")
        return set()

    local_lemmas = set()

    for docID, lemmas in batch_docs:
        if not lemmas:
            print(f"[WARNING] No lemmas found in doc {docID}")
            continue

        # Add all lemmas to this batch's local set
        for lemma in lemmas:
            local_lemmas.add(lemma)

    return local_lemmas


if __name__ == "__main__":
    batchmap = load_batchmap()
    lexicon = set()

    lexicon_csv = "./processed_data/lexicon.csv"
    lexicon_pkl = "./processed_data/lexicon.pkl"

    print(f"[INFO] Loaded {len(batchmap)} batches.")

    start = time.time()

    # --- MULTIPROCESSING ---
    with Pool(cpu_count()) as pool:
        batch_lemma_sets = pool.map(process_batch, batchmap.items())
    
    # Merge all returned sets
    for lemma_set in batch_lemma_sets:
        lexicon.update(lemma_set)

    end = time.time()

    print(f"[INFO] Total unique lemmas: {len(lexicon)}")
    print(f"[INFO] Time taken: {end-start:.2f} seconds")

    os.makedirs("./processed_data", exist_ok=True)

    # --- SAVE CSV ---
    with open(lexicon_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word_id", "word"])  # correct header
        for word_id, lemma in enumerate(lexicon, start=1):
            writer.writerow([word_id, lemma])

    # --- SAVE PICKLE ---
    with open(lexicon_pkl, "wb") as f:
        pickle.dump(lexicon, f)

    print("[INFO] Lexicon saved to CSV and PKL.")
