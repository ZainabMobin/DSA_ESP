# import gzip, pickle, os, time
# import numpy as np

# GLOVE_TXT = "./glove/glove.6B.100d.txt"
# GLOVE_GZIP = "./processed_data/glove_vec.pkl.gz"

# # 🟢 Load GloVe embeddings once (NumPy float32)
# def convert_glove_embeddings_gzip(path):
#     glove = {}
#     with open(path, "r", encoding="utf-8") as f:
#         for line in f:
#             parts = line.rstrip().split(" ")
#             word = parts[0]
#             vector = np.asarray(parts[1:], dtype=np.float32)  # float32 array is much smaller in space. taking lesser RAM than lists or arrays
#             glove[word] = vector
#     return glove

# def convert_to_gzip():
#     start = time.time()
#     glove = convert_glove_embeddings_gzip(GLOVE_TXT)

#     os.makedirs(os.path.dirname(GLOVE_GZIP), exist_ok=True)

#     with gzip.open(GLOVE_GZIP, "wb") as f:
#         pickle.dump(glove, f, protocol=pickle.HIGHEST_PROTOCOL)

#     end = time.time()
#     print(f"GloVe embeddings saved successfully in {end-start:.4f} s.")


# def load_glove_vec():
#     start = time.time()
    
#     with gzip.open(GLOVE_GZIP, "rb") as f:
#         vector = pickle.load(f)

#     end = time.time()
#     print(f"GloVe embeddings saved successfully in {end-start:.4f} s.")
#     return vector

# if __name__ == "__main__":

#     convert_to_gzip()
#     load_glove_vec()

import gzip, pickle, os, time
import numpy as np

GLOVE_TXT = "./glove/glove.6B.100d.txt"

# 🟢 NEW: split storage paths
WORDS_GZIP = "./processed_data/glove_words.pkl.gz"     # 🧠 words only
VECTORS_NPY = "./processed_data/glove_vectors.npy"    # ⚡ pure float32 matrix


# 🟢 Convert GloVe txt → words + matrix (order preserved)
def convert_glove_to_words_and_vectors(path):
    words = []     # 🧠 stores vocabulary
    vectors = []   # ⚡ stores raw numeric data

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip().split(" ")
            words.append(parts[0])          # 🧠 word at index i
            vectors.append(parts[1:])       # ⚡ vector at SAME index i

    # 🔥 single conversion → contiguous float32 matrix
    matrix = np.asarray(vectors, dtype=np.float32)

    return words, matrix


def convert_and_save():
    start = time.time()

    words, matrix = convert_glove_to_words_and_vectors(GLOVE_TXT)

    os.makedirs(os.path.dirname(WORDS_GZIP), exist_ok=True)

    # 🧠 save words (gzip works great on strings)
    with gzip.open(WORDS_GZIP, "wb") as f:
        pickle.dump(words, f, protocol=pickle.HIGHEST_PROTOCOL)

    # ⚡ save vectors (no pickle, raw NumPy binary)
    np.save(VECTORS_NPY, matrix)

    end = time.time()
    print(f"Words saved: {len(words)}")
    print(f"Matrix shape: {matrix.shape}")
    print(f"Conversion completed in {end-start:.4f} s.")


# 🟢 Load back (order is intact)
def load_glove_matrix():
    start = time.time()

    # 🧠 load words
    with gzip.open(WORDS_GZIP, "rb") as f:
        words = pickle.load(f)

    # ⚡ load vectors (can use mmap_mode='r' if needed)
    matrix = np.load(VECTORS_NPY)

    end = time.time()
    print(f"GloVe loaded in {end-start:.4f} s.")

    return words, matrix


if __name__ == "__main__":
    convert_and_save()
    words, matrix = load_glove_matrix()
