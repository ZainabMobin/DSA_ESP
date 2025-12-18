import csv, pickle, time, os, gzip

LEXICON_GZIP = "./processed_data/lexicon.pkl.gz"
LEXICON_BARREL_GZIP = "./processed_data/lexicon_with_barrels.pkl.gz"

def load_lexicon():
    """
    Loads the lexicon containing Words and WordIDs.
    Returns: wordID -> word
    """
    start_time = time.time()
    
    if not os.path.exists(LEXICON_GZIP):
        raise FileNotFoundError(f"Lexicon file not found: {LEXICON_GZIP}")

    with gzip.open(LEXICON_GZIP, "rb") as f:
        lexicon = pickle.load(f)

    end_time = time.time()
    print(f"[INFO] Loaded lexicon in {end_time - start_time:.2f} s from PKL.GZIP")
    print("Sample entries: ", list(lexicon.items())[:2])
    return lexicon
    

def load_lexicon_posting_gzip():
    """
    Loads the lexicon containing barrel pointers and posting info.
    Returns:
        dict: wordID -> list of {barrel_id, start_idx, length}
    """
    start_time = time.time()
    
    if not os.path.exists(LEXICON_BARREL_GZIP):
        raise FileNotFoundError(f"Lexicon file not found: {LEXICON_BARREL_GZIP}")

    with gzip.open(LEXICON_BARREL_GZIP, "rb") as f:
        lexicon = pickle.load(f)

    end_time = time.time()
    print(f"[INFO] Loaded lexicon with barrel pointers in {end_time - start_time:.2f} s from PKL.GZIP")
    print("Sample entries: ", list(lexicon.items())[:2])
    return lexicon


if __name__ == "__main__":
    lexicon = load_lexicon()
    lexicon_postings = load_lexicon_posting_gzip()
    print("Sample entries Lexicon: ", list(lexicon.items())[:2])  # shows first 5 items from lexicon
    print("Sample entries Lexicon_Postings: ", list(lexicon_postings.items())[:2])  # shows first 5 items from lexicon_postings