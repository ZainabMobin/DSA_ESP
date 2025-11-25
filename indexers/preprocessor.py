
import os
import json
import string
from multiprocessing import Pool, cpu_count
import spacy

# Initialize SpaCy once (shared)
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "tagger"])

FORBIDDEN_SUBSTRINGS = [
    "@", ".", "/", "(", ")", "http", "https", "www", "%", "|", "=", "<", ">", 
    "≥", "≤","±", ",", "*", "+", "&", "~", "[", "]", "×", ":", "£", '$', "#", 
    "°", "ỹ", "˳", "ˆ", "•"
]


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


def read_file(filepath):
    """Read one JSON file and return combined text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
        print(f"[DONE] {os.path.basename(filepath)}")  
        content = extract_text_from_json(parsed_data)
        file_set = set()
        for w in content.strip().split():
            file_set.add(w)

        return file_set
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return set() #returns empty set if error encountered


def clean_and_lemmatize(full_set):
    """Word filters + lemmatization"""
    cleaned_words = set()
    counter = 1
    
    for word in full_set:
        w = word.lower().strip(string.punctuation)
        if not w or not w.isascii() or not w.isalpha() or w.isdigit() or len(w) < 2 or all(c==w[0] for c in w) or any(sub in w for sub in FORBIDDEN_SUBSTRINGS):
            continue
        cleaned_words.add(w)
        counter += 1
        if counter % 50000 == 0:
            print(f"[DEBUG] cleaned {counter} words so far...")
    
    lemmas = set()

    counter = 0

    for doc in nlp.pipe(cleaned_words, batch_size=1000, disable=["parser", "ner"]):
        if len(doc) == 0:
            continue
        lemmas.add(doc[0].lemma_)

        counter += 1
        if counter % 50000 == 0:
            print(f"[DEBUG] Lemmatized {counter} words so far...")

    return lemmas


def preprocess_files(filepaths, n_process=None):
    """
    Preprocess a list of file paths.
    Stage 1: parallel reading + concatenation
    Stage 2: word filtering + lemmatization
    Returns: set of all lemmas
    """
    if n_process is None:
        n_process = cpu_count()
    
    # Stage 1: parallel reading
    with Pool(processes=n_process) as pool:
        file_set = pool.map(read_file, filepaths)  # each worker handles a subset of files
    print("Got all text")
    # concatenate all texts
    full_set = set().union(*file_set)
    

    #instead of joining the full texts of all 59k docs, better to join words form each in a set() 
    #caters for duplicates,
    print(f"    Starting cleaning + lemmatization...")  
    # Stage 2: word filtering + lemmatization
    lemmas = clean_and_lemmatize(full_set)
    
    return lemmas
