import glob, os, time, pickle, json, sys
from multiprocessing import Pool, cpu_count
# add project root to be able to import loaders
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from loaders.lexiconLoader import load_lexicon
from preprocessor import extract_text_from_json, nlp, FORBIDDEN_SUBSTRINGS

#check tokens
def clean_token(t):
    w = t.lower().strip()
    if not w.isascii() or not w.isalpha() or any(s in w for s in FORBIDDEN_SUBSTRINGS):
        return None
    return w

def load_json_file(fp):
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = extract_text_from_json(data)
        return (fp, text)
    except:
        return (fp, None)

if __name__ == "__main__":

    folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/", 
               "./dataset/comm_use_subset/comm_use_subset/pdf_json/",
               "./dataset/comm_use_subset/comm_use_subset/pmc_json/", 
               "./dataset/noncomm_use_subset/noncomm_use_subset/pdf_json/",
               "./dataset/noncomm_use_subset/noncomm_use_subset/pmc_json/",
               "./dataset/custom_license/custom_license/pdf_json/", 
               "./dataset/custom_license/custom_license/pmc_json/"]

    #list all json files
    file_paths = []
    for f in folders:
        file_paths.extend(glob.glob(os.path.join(f + "*.json")))

    lexicon = load_lexicon()
    forward_index = {}
    doc_map = {}
    doc_id = 1

    print(f"Total files: {len(file_paths)}")
    start = time.time()

    print("Loading files in parallel.")
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(load_json_file, file_paths)

    valid_docs = [(fp, text) for fp, text in results if text]

    print(f"Loaded {len(valid_docs)} valid documents.")

    texts = [t for _, t in valid_docs]

    for doc, (fp, _) in zip(nlp.pipe(texts, batch_size=50), valid_docs):

        tf = {}
        for tok in doc:
            w = clean_token(tok.text)
            if not w:
                continue

            lemma = tok.lemma_.lower()
            wid = lexicon.get(lemma)
            if wid:
                tf[wid] = tf.get(wid, 0) + 1

        if tf:
            forward_index[doc_id] = tf
            doc_map[doc_id] = fp
            doc_id += 1

    end = time.time()
    print(f"forward index docs: {len(forward_index)}")
    print(f"time taken: {end-start:.2f} s")

    #write pickle files
    pickle.dump(forward_index, open("./processed_data/forward_index.pkl", "wb"))
    pickle.dump(doc_map, open("./processed_data/doc_map.pkl", "wb"))
    print("saved forward index + doc map!")
