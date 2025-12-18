import os
import glob
import pickle
import string
from multiprocessing import Pool, cpu_count
import spacy

# Initialize SpaCy once
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

BATCH_DIR = "./batch_contents"
BATCH_SIZE = 100

# ------------------------- Existing convert_to_pkl -------------------------
def read_file_return_list(filepath):
    try:
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)

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
        for section in ["abstract", "body_text", "back_matter"]:
            for sec in parsed_data.get(section, []):
                content += " " + (sec.get("text") or "")
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
    print(f"[DEBUG] Processing file: {fp} as docID {docID}")
    words = read_file_return_list(fp)
    lemmas = clean_and_lemmatize_list(words)
    return (docID, lemmas)

# ------------------------- Dynamic preprocessing -------------------------
def dynamic_preprocess(folder_path):
    """
    Preprocess new documents in folder_path into batches.
    Returns: dict of {batchID: batch_path}
    """
    print("[INFO] Starting dynamic preprocessing...")
    print("[INFO] Folder path:", folder_path)

    os.makedirs(BATCH_DIR, exist_ok=True)
    print("[INFO] Batch folder:", os.path.abspath(BATCH_DIR))

    # Load existing batchmap if available
    try:
        from loaders.mapLoaders import load_batchmap
        batchmap = load_batchmap()
    except Exception:
        print("[WARN] Could not load batchmap, starting fresh.")
        batchmap = {}

    last_batchID = max(batchmap.keys(), default=-1)
    batch_num = last_batchID + 1

    # Collect JSON files
    file_paths = glob.glob(os.path.join(folder_path, "*.json"))
    print("[DEBUG] JSON files found:", len(file_paths))
    if file_paths:
        print("[DEBUG] Files:", file_paths)
    else:
        print("[INFO] No JSON files found in the folder.")
        return {}

    # Assign temporary docIDs
    last_docID = 0
    tasks = [(fp, i + last_docID + 1) for i, fp in enumerate(file_paths)]

    new_batches = {}
    batch = []

    # Multiprocessing
    with Pool(cpu_count()) as pool:
        for result in pool.imap_unordered(convert_to_pkl, tasks):
            batch.append(result)
            if len(batch) >= BATCH_SIZE:
                batch_path = f"{BATCH_DIR}/batch_{batch_num}.pkl"
                with open(batch_path, "wb") as f:
                    pickle.dump(batch, f, protocol=pickle.HIGHEST_PROTOCOL)
                new_batches[batch_num] = batch_path
                print(f"[DEBUG] Saved batch {batch_num} with {len(batch)} docs")
                batch_num += 1
                batch = []

    # Save leftover batch
    if batch:
        batch_path = f"{BATCH_DIR}/batch_{batch_num}.pkl"
        with open(batch_path, "wb") as f:
            pickle.dump(batch, f, protocol=pickle.HIGHEST_PROTOCOL)
        new_batches[batch_num] = batch_path
        print(f"[DEBUG] Saved leftover batch {batch_num} with {len(batch)} docs")

    print("[INFO] Dynamic preprocessing completed.")
    return new_batches

# ------------------------- Safe entry point for Windows -------------------------
if __name__ == "__main__":
    folder_path = os.path.join(os.path.dirname(__file__), "new_docs")
    batches = dynamic_preprocess(folder_path)
    print("Batches created:", batches)

