import pickle, gzip

# Load forward index
with gzip.open("./processed_data/forward_index.pkl.gz", "rb") as f:
    forward_index = pickle.load(f)

# Load docmap to get filenames
with gzip.open("./processed_data/doc_map.pkl.gz", "rb") as f:
    docmap = pickle.load(f)

# Get last document ID
last_docID = max(forward_index.keys())
print(f"Last document ID: {last_docID}")
print(f"Filename: {docmap[last_docID]}")

