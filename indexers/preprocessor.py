import os, glob, time, sys
import json, pickle, string, gzip
from multiprocessing import Pool, cpu_count
import spacy
import tempfile

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from loaders.mapLoaders import load_docmap, load_batchmap

# Initialize SpaCy once
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# Paths
DOCMAP_GZIP = "./processed_data/doc_map.pkl.gz"
BATCHMAP_GZIP = "./processed_data/batch_map.pkl.gz"
os.makedirs("./batch_contents", exist_ok=True)


# ------------------------- Preprocessor Functions -------------------------

def extract_metadata_only(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        meta = data.get("metadata", data)
        title = meta.get("title", "")
        authors = []
        for a in meta.get("authors", []):
            if isinstance(a, dict):
                name = " ".join(filter(None, [
                    a.get("first"),
                    " ".join(a.get("middle", [])) if isinstance(a.get("middle"), list) else a.get("middle"),
                    a.get("last")
                ]))
            else:
                name = str(a)
            if name:
                authors.append(name)
        return {"title": title, "authors": authors}
    except Exception:
        return {"title": "", "authors": []}


def extract_text_from_json(parsed_data):
    content = ""
    if "metadata" in parsed_data:
        meta = parsed_data["metadata"]
        content += " " + (meta.get("title") or "")
        for auth in meta.get("authors", []):
            content += " " + (auth.get("first") or "")
            mid = auth.get("middle") or ""
            if isinstance(mid, list):
                mid = " ".join(mid)
            content += " " + mid
            content += " " + (auth.get("last") or "")
            content += " " + (auth.get("suffix") or "")
            content += " " + (auth.get("email") or "")
            affil = auth.get("affiliation") or {}
            content += " " + (affil.get("laboratory") or "")
            content += " " + (affil.get("institution") or "")
            loc = affil.get("location") or {}
            content += " " + (loc.get("postCode") or "")
            content += " " + (loc.get("settlement") or "")
            content += " " + (loc.get("country") or "")

    for section in ["abstract", "body_text", "back_matter"]:
        for sec in parsed_data.get(section, []):
            content += " " + (sec.get("text") or "")

    for bib in parsed_data.get("bib_entries", {}).values():
        content += " " + (bib.get("title") or "") + " " + (bib.get("venue") or "")
        for auth in bib.get("authors", []):
            content += " " + (auth.get("first") or "")
            mid = auth.get("middle") or ""
            if isinstance(mid, list):
                mid = " ".join(mid)
            content += " " + mid
            content += " " + (auth.get("last") or "")
            content += " " + (auth.get("suffix") or "")

    for ref in parsed_data.get("ref_entries", {}).values():
        content += " " + (ref.get("title") or "")

    return content


def read_file_return_list(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
        content = extract_text_from_json(parsed_data)
        return content.strip().split()
    except Exception as e:
        print(f"[WARN] Failed to read {filepath}: {e}")
        return []


def clean_and_lemmatize_list(full_list):
    cleaned_words = []
    for word in full_list:
        w = word.lower().strip(string.punctuation)
        if not w or not w.isascii() or not w.isalpha() or len(w) < 2 or all(c == w[0] for c in w):
            continue
        cleaned_words.append(w)
    lemmas = []
    for doc in nlp.pipe(cleaned_words, batch_size=1000):
        if len(doc) > 0:
            lemmas.append(doc[0].lemma_)
    return lemmas


def convert_to_pkl(args):
    fp, docID = args
    words = read_file_return_list(fp)
    lemmas = clean_and_lemmatize_list(words)
    return (docID, lemmas)


# ------------------------- Main Workflow -------------------------

if __name__ == "__main__":
    start_total = time.time()

    # Load existing maps or initialize
    docmap = {}
    batchmap = {}
    if os.path.exists(DOCMAP_GZIP):
        with gzip.open(DOCMAP_GZIP, "rb") as f:
            docmap = pickle.load(f)
    if os.path.exists(BATCHMAP_GZIP):
        with gzip.open(BATCHMAP_GZIP, "rb") as f:
            batchmap = pickle.load(f)

    last_docID = max(docmap.keys(), default=-1)
    last_batchID = max(batchmap.keys(), default=-1)

    print(f"LAST: docID {last_docID} batchID {last_batchID}")

    # Collect all JSON files
    folders = [
        "./dataset/biorxiv_medrxiv/biorxiv_medrxiv/temp/"
    ]
    file_paths = []
    for f in folders:
        file_paths.extend(glob.glob(os.path.join(f, "*.json")))

     # FILTER OUT FILES ALREADY PROCESSED FILES i.e., filepaths present in the Docmap 
    existing_files = set(docmap.values())  # set of already processed filepaths
    file_paths = [fp for fp in file_paths if fp not in existing_files]  # keep only new files

    # Assign docIDs
    tasks = [(fp, i + last_docID + 1) for i, fp in enumerate(file_paths)]
    if not tasks:
        print("[INFO] No new documents found.")
        exit(0)

    # Update docmap
    for fp, docID in tasks:
        docmap[docID] = fp

    # Save docmap atomically
    with tempfile.NamedTemporaryFile(delete=False) as tmpf:
        with gzip.GzipFile(fileobj=tmpf, mode="wb") as f:
            pickle.dump(docmap, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmpf.name, DOCMAP_GZIP)
    print(f"[INFO] docmap saved to {DOCMAP_GZIP}")

    # Batch processing
    batch_size = 100
    batch_num = last_batchID + 1
    batch = []

    print(f"[INFO] Starting multiprocessing for {len(tasks)} documents...")
    with Pool(cpu_count()) as pool:
        for result in pool.imap_unordered(convert_to_pkl, tasks):
            batch.append(result)
            if len(batch) >= batch_size:
                batch_path = f"./batch_contents/batch_{batch_num}.pkl"
                with open(batch_path, "wb") as f:
                    pickle.dump(batch, f, protocol=pickle.HIGHEST_PROTOCOL)
                batchmap[batch_num] = batch_path
                # Save batchmap atomically
                with tempfile.NamedTemporaryFile(delete=False) as tmpf:
                    with gzip.GzipFile(fileobj=tmpf, mode="wb") as f:
                        pickle.dump(batchmap, f, protocol=pickle.HIGHEST_PROTOCOL)
                os.replace(tmpf.name, BATCHMAP_GZIP)
                print(f"[SAVED] {batch_path} ({len(batch)} docs)")
                batch_num += 1
                batch = []

    # Save leftover batch
    if batch:
        batch_path = f"./batch_contents/batch_{batch_num}.pkl"
        with open(batch_path, "wb") as f:
            pickle.dump(batch, f, protocol=pickle.HIGHEST_PROTOCOL)
        batchmap[batch_num] = batch_path
        with tempfile.NamedTemporaryFile(delete=False) as tmpf:
            with gzip.GzipFile(fileobj=tmpf, mode="wb") as f:
                pickle.dump(batchmap, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmpf.name, BATCHMAP_GZIP)
        print(f"[SAVED] {batch_path} ({len(batch)} docs)")

    end_total = time.time()
    print(f"[INFO] Total processing time: {end_total - start_total:.2f} s")
