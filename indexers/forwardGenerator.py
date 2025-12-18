from collections import Counter
from multiprocessing import Pool, cpu_count
from functools import partial
import pickle, gzip, os

FORWARD_GZIP = "./processed_data/forward_index.pkl.gz"

def process_batch(batch_tuple, lexicon):
    # This logic is preserved
    batchID, fp = batch_tuple
    batch_docs = pickle.load(open(fp, "rb"))
    batch_forward = {}
    for docID, lemmas in batch_docs:
        wordIDs = [lexicon[w] for w in lemmas if w in lexicon]
        if not wordIDs:
            continue
        freq = Counter(wordIDs)
        batch_forward[docID] = {"length": sum(freq.values()), "terms": list(freq.items())}
    return batch_forward

def update_forward_index(new_batches, lexicon):
    # --- TYPE CONVERTER (Same as Lexicon fix) ---
    if isinstance(new_batches, tuple) and len(new_batches) > 0:
        new_batches = new_batches[0]
    
    if isinstance(new_batches, list):
        new_batches = {i: path for i, path in enumerate(new_batches)}

    if not isinstance(new_batches, dict):
        print(f"[ERROR] new_batches must be list or dict, got {type(new_batches)}")
        return {}
    # --------------------------------------------

    if os.path.exists(FORWARD_GZIP):
        with gzip.open(FORWARD_GZIP, "rb") as f:
            forward_index_nested = pickle.load(f)
    else:
        forward_index_nested = {}

    func = partial(process_batch, lexicon=lexicon)
    
    with Pool(cpu_count()) as pool:
        # Now .items() will work because new_batches is guaranteed to be a dict
        for batch_dict in pool.imap_unordered(func, new_batches.items()):
            forward_index_nested.update(batch_dict)

    os.makedirs("./processed_data", exist_ok=True)
    with gzip.open(FORWARD_GZIP, "wb") as f:
        pickle.dump(forward_index_nested, f)

    print(f"[INFO] Forward index updated. Total docs: {len(forward_index_nested)}")
    return forward_index_nested
