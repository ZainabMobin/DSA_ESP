import os, glob, time
import json, csv, pickle, string
from multiprocessing import Pool, cpu_count
import spacy

# Initialize SpaCy once (shared)
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

docmap_csv = "./processed_data/doc_map.csv"
batchmap_csv = "./processed_data/batch_map.csv"
os.makedirs("./batch_contents", exist_ok=True)


def extract_text_from_json(parsed_data):
    """Combine all textual content from a JSON document"""
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
        if section in parsed_data:
            for sec in parsed_data[section]:
                content += " " + (sec.get("text") or "")

    if "bib_entries" in parsed_data:
        for entry in parsed_data["bib_entries"].values():
            content += " " + (entry.get("title") or "")
            content += " " + (entry.get("venue") or "")
            for auth in entry.get("authors", []):
                content += " " + (auth.get("first") or "")
                mid = auth.get("middle") or ""
                if isinstance(mid, list):
                    mid = " ".join(mid)
                content += " " + mid
                content += " " + (auth.get("last") or "")
                content += " " + (auth.get("suffix") or "")

    if "ref_entries" in parsed_data:
        for ref in parsed_data["ref_entries"].values():
            content += " " + (ref.get("title") or "")

    return content


def read_file_return_list(filepath):
    """read one filepath and return list of words"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
        content = extract_text_from_json(parsed_data)
        return content.strip().split()  # returns list of words
    except Exception as e:
        print(f"Error reading filepath {filepath}: {e}")
        return []


def clean_and_lemmatize_list(full_list):
    """Word filters + lemmatization"""
    cleaned_words = []
    
    for word in full_list:
        w = word.lower().strip(string.punctuation)
        if not w or not w.isascii() or not w.isalpha() or len(w) < 2 or all(c==w[0] for c in w):
            continue
        cleaned_words.append(w)
    
    lemmas = []
    for doc in nlp.pipe(cleaned_words, batch_size=1000, disable=["parser", "ner"]):
        if len(doc) == 0:
            continue
        lemmas.append(doc[0].lemma_)

    return lemmas


def load_docmap():
    docmap = {}
    if os.path.exists(docmap_csv):
        with open(docmap_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                docmap[int(row["docID"])] = row["filepath"]
    return docmap


def load_batchmap():
    batchmap = {}
    if os.path.exists(batchmap_csv):
        with open(batchmap_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                batchmap[int(row["batchID"])] = row["filepath"]
    return batchmap


# Worker: reads, cleans, lemmatizes and returns the contents of a single document
def convert_to_pkl(args):
    fp, docID = args
    words = read_file_return_list(fp)
    lemmas = clean_and_lemmatize_list(words)
    return (docID, lemmas)

#cleans and lemmatizes contents of all files, and saves batches per 100 files
if __name__ == "__main__":

    folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/",
            "./dataset/noncomm_use_subset/comm_use_subset/pdf_json/",
            "./dataset/noncomm_use_subset/comm_use_subset/pmc_json/",
            "./dataset/noncomm_use_subset/noncomm_use_subset/pdf_json/",
            "./dataset/noncomm_use_subset/noncomm_use_subset/pmc_json/",
            "./dataset/custom_license/custom_license/pdf_json/", 
            "./dataset/custom_license/custom_license/pmc_json/"]

    file_paths = []
    for f in folders:
        file_paths.extend(glob.glob(os.path.join(f, "*.json")))

    last_docID = -1
    docmap = load_docmap()
    last_batchID = -1
    batchmap = load_batchmap()

    if docmap:
        last_docID = len(docmap)-1
    if batchmap:
        last_batchID = len(batchmap)-1

    # Assign docIDs
    tasks = [(fp, i+last_docID+1) for i, fp in enumerate(file_paths)]
    if not tasks:
        print("[INFO] No new documents found.")
        exit(0)

    # Write doc_map.csv
    with open(docmap_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        #write initial line if empty
        if last_docID == -1:
            w.writerow(["docID", "filepath"])
        for i, fp in enumerate(file_paths):
            w.writerow([i+last_docID+1, fp])

    # Write doc_map.csv header line if empty
    if last_batchID == -1: 
        with open(batchmap_csv, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["batchID", "filepath"])

    batch_size = 100
    batch_num = last_batchID+1
    batch = []

    start_time_total = time.time()

    print(f"\n[INFO] Starting multiprocessing for {len(tasks)} documents...")
    with Pool(cpu_count()) as pool:
        for result in pool.imap_unordered(convert_to_pkl, tasks):
            if result is None:
                continue
            batch.append(result)

            # Save batch when full
            if len(batch) >= batch_size:
                batch_path = f"./batch_contents/batch_{batch_num}.pkl"
                with open(batch_path, "wb") as f:
                    pickle.dump(batch, f)
                print(f"[SAVED] {batch_path} ({len(batch)} docs)")

                # Update batch_map.csv
                with open(batchmap_csv, "a", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow([batch_num, batch_path])

                batch_num += 1
                batch = []

    # Save leftover batch
    if batch:
        batch_path = f"./batch_contents/batch_{batch_num}.pkl"
        with open(batch_path, "wb") as f:
            pickle.dump(batch, f)
        print(f"[SAVED] {batch_path} ({len(batch)} docs)")

        with open(batchmap_csv, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([batch_num, batch_path])

    end_time_total = time.time()
    print(f"\n[INFO] Total processing time: {end_time_total - start_time_total:.2f} s")