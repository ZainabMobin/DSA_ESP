import csv, pickle, time
lexicon_path_csv = "./processed_data/lexicon.csv"
lexicon_path_pkl = "./processed_data/lexicon.pkl"

def load_lexicon():
    #first load lexiocn from .pkl
    lexicon = {}
    try:
        with open(lexicon_path_pkl, 'rb') as f:
            start = time.time()
            lexicon = pickle.load(f)
            end = time.time()
        print(f" lexicon with {len(lexicon)} loaded from pickle file in {end-start:.2f} time")
        return lexicon
    except (FileNotFoundError, EOFError):
        print("pkl file not found D:, loading from csv")
    #if lexicon not in .pkl file, load from .csv file and write to .pkl file too
    with open(lexicon_path_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) #skips first header line
        for row in reader:
            if len(row)<2:
                continue
            word_id, lemma = row
            lexicon[lemma] = int(word_id)

    with open(lexicon_path_pkl, 'wb') as f:
        pickle.dump(lexicon, f)
        print("Written into pickle file from csv file")
        
    print(f"loaded {len(lexicon)} words from lexicon.csv")
    return lexicon

if __name__ == "__main__":
    lexicon = load_lexicon()
    print("Sample entries:", list(lexicon.items())[:10])  # shows first 10 items