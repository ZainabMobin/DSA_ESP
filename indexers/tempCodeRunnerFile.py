from multiprocessing import Pool, cpu_count
import csv, pickle
import time, sys, os
from collections import Counter
from functools import partial
# Add project root to Python path so 'loaders' is visible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessor import load_docmap, load_batchmap
from loaders.lexiconLoader import load_lexicon

docmap = load_docmap()
batchmap = load_batchmap()
lexicon = load_lexicon()

FORWARD_CSV = "./processed_data/forward_index.csv"
FORWARD_PKL = "./processed_data/forward_index.pkl"  

with open(FORWARD_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['docID', 'wordID', 'frequency'])

#batch filepath and batchID passed as parameter in a tuple
def process_batch(batch_tuple, lexicon):
    """
    Read a batch pickle and return a list of (docID, wordID, frequency) for that batch
    """
    print(f"[DEBUG] type of lexicon in worker: {type(lexicon)}")
    batchID, fp = batch_tuple
    batch_docs = pickle.load(open(fp, "rb"))
    batch_rows = []

    for docID, lemmas in batch_docs:
        if not lemmas:
            print(f"[WARNING] No lemmas found in doc {docID}")

        # Count frequency of each wordID in the doc
        wordIDs = [lexicon[word] for word in lemmas if word in lexicon]
        freq = Counter(wordIDs)
        for wordID, count in freq.items():
            batch_rows.append((docID, wordID, count))

    print(f"[DEBUG] done batch {docID%100} {batchID}")
    return batch_rows


if __name__ == "__main__":
    start = time.time()

    # Open CSV for writing
    with open(FORWARD_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['docID', 'wordID', 'frequency'])

        # Multiprocessing: process batches in parallel
        with Pool(cpu_count()) as pool:
            func = partial(process_batch, lexicon=lexicon)
            results = pool.map(func, batchmap.items())

        # Write results to CSV
        for batch_rows in results:
            writer.writerows(batch_rows)

    end = time.time()
    print(f"Forward index created in {end-start:.2f} s")