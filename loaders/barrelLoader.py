import os, pickle

BARREL_FOLDER = "./processed_data/barrels/"

def fetch_barrel_results_binary_offset(barrelID, offset, length_bytes):
    """
    Load a word's postings from a barrel given its byte offset and length.
    """
    barrel_file = os.path.join(BARREL_FOLDER, f"barrel_{barrelID}.pkl")
    with open(barrel_file, "rb") as f:
        f.seek(offset)                  # move to the byte offset while reading file
        data = f.read(length_bytes)     # read exact bytes
        postings_list = pickle.loads(data)  # deserialize postings list frmo binary form
    return postings_list
