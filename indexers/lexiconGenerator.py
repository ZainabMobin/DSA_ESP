from multiprocessing import Pool, cpu_count
from preprocessor import load_batchmap
import time, os, csv, pickle, gzip


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

    LEXICON_GZIP = "./processed_data/lexicon.pkl.gz"

    print(f"[INFO] Loaded {len(batchmap)} batches.")

    start = time.time()

    # --- MULTIPROCESSING ---
    with Pool(cpu_count()) as pool:
        batch_lemma_sets = pool.map(process_batch, batchmap.items())
    
    # Merge all returned sets
    for lemma_set in batch_lemma_sets:
        lexicon.update(lemma_set)

    print(f"[INFO] Total unique lemmas: {len(lexicon)}")

    # Build dictionary mapping lemma → word_id (sorted for stable ordering)
    lexicon_dict = {lemma: word_id for word_id, lemma in enumerate(sorted(lexicon), start=1)}

    end = time.time()
    print(f"[INFO] Time taken: {end-start:.2f} seconds")

    os.makedirs("./processed_data", exist_ok=True)

    # --- SAVE GZIP PICKLE ---
    with gzip.open(LEXICON_GZIP, "wb") as f:
        pickle.dump(lexicon_dict, f)

    print("[INFO] Lexicon saved to PKL.GZIP")
