import pickle, gzip, time
FORWARD_GZIP = "./processed_data/forward_index.pkl.gz"

def load_forward():
    print("[INFO] Loading nested forward index...")

    start = time.time()
    with gzip.open(FORWARD_GZIP, "rb") as f:
        forward_index = pickle.load(f)
    end = time.time()

    print(f"[INFO] Loaded forward index in {end-start:.2f} seconds")
    return forward_index