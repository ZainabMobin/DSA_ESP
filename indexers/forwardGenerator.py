from collections import defaultdict, Counter
from multiprocessing import Pool, cpu_count
from functools import partial
import sys, os, time
import pickle, gzip

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessor import load_docmap, load_batchmap
from loaders.lexiconLoader import load_lexicon

# Load mappings
docmap = load_docmap()
batchmap = load_batchmap()
lexicon = load_lexicon()

# Output path
FORWARD_GZIP = "./processed_data/forward_index.pkl.gz"

def process_batch(batch_tuple, lexicon):
    """
    Convert a batch pickle to nested forward index format: docID -> list of (wordID, freq)
    Returns a dict for this batch.
    """
    batchID, fp = batch_tuple
    batch_docs = pickle.load(open(fp, "rb"))
    batch_forward = {}

    for docID, lemmas in batch_docs:
        # Convert lemmas to wordIDs if present in lexicon
        wordIDs = [lexicon[word] for word in lemmas if word in lexicon]
        if not wordIDs:
            continue
        freq = Counter(wordIDs)
        batch_forward[docID] = list(freq.items())

    return batch_forward

def merge_batch_into_index(batch_dict, forward_index):
    """
    Merge a batch dictionary into the main nested forward index.
    """
    forward_index.update(batch_dict)

if __name__ == "__main__":
    forward_index_nested = defaultdict(list)
    total_batches = len(batchmap)  # added for progress tracking
    processed_batches = 0         

    start = time.time()

    # partial function to avoid PicklingError (pkl.gzip could not be pickled thorugh Lambda which was done previously)
    func = partial(process_batch, lexicon=lexicon)  

    # Multiprocessing: process batches in parallel
    with Pool(cpu_count()) as pool:
        for batch_dict in pool.imap_unordered(func, batchmap.items()):
            merge_batch_into_index(batch_dict, forward_index_nested)  # merge loaded batch with forward index immediately
            processed_batches += 1
            print(f"[INFO] Processed batch {processed_batches}/{total_batches}")  #  prints progress in processing batches
    
    end = time.time()
    print(f"[INFO] Built nested forward index in {end-start:.4f} s.")

    # Save compressed pickle directly
    with gzip.open(FORWARD_GZIP, 'wb') as f:
        pickle.dump(dict(forward_index_nested), f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"[INFO] Nested forward index saved to {FORWARD_GZIP}")

    # Print sample entry
    sample_docs = list(forward_index_nested.items())[:1]
    print("Sample entry:", sample_docs)
