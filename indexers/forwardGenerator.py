import glob, os, time, csv, pickle, json, sys
from multiprocessing import Pool, cpu_count
from collections import defaultdict

# add project root for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from loaders.lexiconLoader import load_lexicon
from preprocessor import read_file_return_list, clean_text_only   # clean function that only removes noise
import spacy


forward_pkl = "./processed_data/forward_index.pkl"
docmap_pkl = "./processed_data/doc_map.pkl"

#files for saving sample computed data for viewing purposes
forward_json = "./processed_data/forward_index.json"
docmap_csv = "./processed_data/doc_map.csv"

# Shared spaCy model loaded ONCE per worker
def init_worker(shared_lexicon, shared_lexicon_set):
    global lexicon, lexicon_set, nlp
    lexicon = shared_lexicon
    lexicon_set = shared_lexicon_set
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "textcat"])


def process_batch(file_batch):
    """
    file_batch = list of filepaths given to one worker.
    We load all files, convert each to raw text, send ALL to nlp.pipe at once.
    """
    global lexicon, lexicon_set, nlp

    cleaned_texts = []
    valid_files = []

    # Read & clean plain text (no lemmatizing here)
    for fp in file_batch:
        try:
            text_words = read_file_return_list(fp)         # returns list of tokens/words
            cleaned = clean_text_only(text_words)          # lightweight cleaning
            cleaned_texts.append(" ".join(cleaned))        # convert to single string
            valid_files.append(fp)
        except:
            pass  # skip bad files

    if not cleaned_texts:
        return []

    # Batch-process all texts at once
    docs = list(nlp.pipe(cleaned_texts, batch_size=64))   
    # batch_size must be balanced. 
    # Too small -> spacy overhead for individual batch takes lots of time
    # too large -> memory overflow error, spacy cant handle a million tokens at once 

    results = []

    # Lemma + TF building per file
    for doc, fp in zip(docs, valid_files):
        tf = defaultdict(int)

        for tok in doc:
            lemma = tok.lemma_.lower()

            if lemma in lexicon_set:
                wid = lexicon[lemma]
                if wid:
                    tf[wid] += 1

        results.append((fp, dict(tf)))

    return results

if __name__ == "__main__":

    folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/", 
            # "./dataset/comm_use_subset/comm_use_subset/pdf_json/",
            # "./dataset/comm_use_subset/comm_use_subset/pmc_json/", 
            # "./dataset/noncomm_use_subset/noncomm_use_subset/pdf_json/",
            # "./dataset/noncomm_use_subset/noncomm_use_subset/pmc_json/",
            # "./dataset/custom_license/custom_license/pdf_json/", 
            # "./dataset/custom_license/custom_license/pmc_json/"
            ]

    # Collect JSON files
    file_paths = []
    for f in folders:
        file_paths.extend(glob.glob(os.path.join(f, "*.json")))

    print(f"Total files: {len(file_paths)}")

    # Load lexicon
    lexicon = load_lexicon()
    lexicon_set = frozenset(lexicon)

    # How many files each worker should batch at once
    BATCH_SIZE = 5

    # Split file list into batches
    file_batches = [file_paths[i:i+BATCH_SIZE] for i in range(0, len(file_paths), BATCH_SIZE)]

    forward_index = {}
    doc_map = {}
    doc_id = 1

    start = time.time()
    print("Processing with multi-file batching...")

    with Pool(
        processes=cpu_count(),
        initializer=init_worker,
        initargs=(lexicon, lexicon_set)
    ) as pool:

        for batch_result in pool.imap_unordered(process_batch, file_batches):
            for fp, tf in batch_result:
                forward_index[doc_id] = tf
                doc_map[doc_id] = fp
                doc_id += 1

                if doc_id % 200 == 0:
                    print(f"Processed {doc_id} documents...")

    end = time.time()
    print(f"Forward index docs: {len(forward_index)}")
    print(f"Total time taken: {end-start:.2f} s")

    # SAVE FINAL OUTPUTS
    os.makedirs("./processed_data", exist_ok=True)
    pickle.dump(forward_index, open(forward_pkl, "wb"))
    pickle.dump(doc_map, open(docmap_pkl, "wb"))


    #SAVE SAMPLE OUTPUTS FOR SHOWCASING
    # first 50 entries of doc_map saved to CSV
    with open(docmap_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["doc_id", "filepath"])
        for doc_id, fp in list(doc_map.items())[:50]:
            writer.writerow([doc_id, fp])

    # Save only 1 full document entry of forward_index as JSON
    if forward_index:
        first_doc_id = next(iter(forward_index))  # get the first doc_id
        first_doc_entry = {first_doc_id: forward_index[first_doc_id]}  # just this doc's term frequencies

        with open(forward_json, "w", encoding="utf-8") as f:
            json.dump(first_doc_entry, f, indent=2)

    print("Saved forward index + doc map!")