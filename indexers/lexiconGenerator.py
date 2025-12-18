import os, pickle, gzip
from multiprocessing import Pool, cpu_count

LEXICON_GZIP = "./processed_data/lexicon.pkl.gz"

def process_batch(batch_tuple):
    # Expects (batchID, batch_path)
    batchID, fp = batch_tuple
    try:
        batch_docs = pickle.load(open(fp, "rb"))
    except Exception as e:
        print(f"[ERROR] Failed to load batch {batchID}: {e}")
        return set()
    
    lemmas_set = set()
    for docID, lemmas in batch_docs:
        if lemmas:
            lemmas_set.update(lemmas)
    return lemmas_set

def update_lexicon(new_batches):
    """
    Updates lexicon with new batches.
    new_batches can be:
        - dict {batchID: batch_path}
        - list of paths
        - tuple wrapping a list/dict
    """
    # ---------------- Type Safety ----------------
    if isinstance(new_batches, tuple) and len(new_batches) > 0:
        new_batches = new_batches[0]
    
    if isinstance(new_batches, list):
        new_batches = {i: path for i, path in enumerate(new_batches)}
    
    if not isinstance(new_batches, dict):
        print(f"[ERROR] Could not process {type(new_batches)}. Expected dictionary.")
        return {}
    # --------------------------------------------

    # Load existing lexicon or start empty
    if os.path.exists(LEXICON_GZIP):
        with gzip.open(LEXICON_GZIP, "rb") as f:
            lexicon = pickle.load(f)
    else:
        lexicon = {}

    # Process all batches
    with Pool(cpu_count()) as pool:
        batch_lemma_sets = pool.map(process_batch, new_batches.items())

    # Merge all new lemmas
    all_new_lemmas = set()
    for s in batch_lemma_sets:
        all_new_lemmas.update(s)

    # Add new lemmas to lexicon
    current_max_id = max(lexicon.values(), default=0)
    for lemma in sorted(all_new_lemmas):
        if lemma not in lexicon:
            current_max_id += 1
            lexicon[lemma] = current_max_id

    # Save updated lexicon
    os.makedirs("./processed_data", exist_ok=True)
    with gzip.open(LEXICON_GZIP, "wb") as f:
        pickle.dump(lexicon, f)

    print(f"[INFO] Lexicon updated. Total lemmas: {len(lexicon)}")
    return lexicon
