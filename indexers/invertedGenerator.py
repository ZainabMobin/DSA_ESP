import glob
import os
import csv
from collections import defaultdict, Counter
from preprocessor import preprocess_files, read_file, clean_and_lemmatize
import time

def build_lexicon(file_paths):
    lemmas = set()
    doc_words = []
    
    for doc_id, filepath in enumerate(file_paths):
        words_in_doc = read_file(filepath)
        lemmas.update(words_in_doc)
        doc_words.append((doc_id, words_in_doc))
        
    lemmas = clean_and_lemmatize(lemmas)
    
    lemma_to_id = {word: idx+1 for idx, word in enumerate(sorted(lemmas))}
    
    return lemma_to_id, doc_words

def inverted_index(file_paths, output_path="./processed_data/inverted_index.csv"):
    lemma_to_id, doc_words = build_lexicon(file_paths)
    
    inverted = defaultdict(lambda: defaultdict(int))  # word_id -> doc_id -> freq
    
    for doc_id, words in doc_words:
        lemmas_in_doc = [word for word in words if word in lemma_to_id]
        freq = Counter(lemmas_in_doc)
        for lemma, count in freq.items():
            word_id = lemma_to_id[lemma]
            inverted[word_id][doc_id] = count
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['word_id', 'doc_id', 'frequency'])
        
        for word_id, doc_freqs in inverted.items():
            for doc_id, freq in doc_freqs.items():
                writer.writerow([word_id, doc_id, freq])

if __name__ == "__main__":
    folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/"]
    file_paths = []
    for f in folders:
        file_paths.extend(glob.glob(os.path.join(f + "*.json")))
    
    start = time.time()
    inverted_index(file_paths)
    print(f"Inverted index created in {time.time() - start:.2f} seconds")
