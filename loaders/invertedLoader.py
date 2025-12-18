import pickle, gzip, time, os
INVERTED_GZIP = "./processed_data/inverted_index.pkl.gz"

def load_inverted():
    print("[INFO] Loading inverted index...")

    start = time.time()
    if not os.path.exists(INVERTED_GZIP):
        raise FileNotFoundError(f"Inverted Index file not found: {INVERTED_GZIP}")

    with gzip.open(INVERTED_GZIP, "rb") as f:
        inverted_index = pickle.load(f)
    end = time.time()

    print(f"[INFO] Loaded inverted index in {end-start:.2f} seconds")
    # print("Sample entries: ", list(inverted_index.items())[:1])
    return inverted_index


if __name__ == "__main__":
    inverted_index = load_inverted()
    print("Sample entries Lexicon: ", list(inverted_index.items())[:1])  # shows first item from inverted index