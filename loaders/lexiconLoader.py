import csv, pickle, time
lexicon_path_csv = "./processed_data/lexicon.csv"
lexicon_path_pkl = "./processed_data/lexicon.pkl"

def load_lexicon():
    lexicon = {}
    try:
        with open(lexicon_path_pkl, 'rb') as f:
            st = time.time()
            lexicon = pickle.load(f)
            end = time.time()
        print(f" lexicon with {len(lexicon)} loaded from pickle file in {end-st:.2f} s!")
        return lexicon
    except (FileNotFoundError, EOFError):
        print("file not found :(")
    
    with open(lexicon_path_csv, newline='', encoding='utf-8') as f:
        st = time.time()
        reader = csv.reader(f)
        next(reader) #skips first header line
        for row in reader:
            if len(row)<2:
                continue
            word_id, lemma = row
            lexicon[lemma] = int(word_id)
        end = time.time()
        print(f" loaded {len(lexicon)} words in {end-st:.2f} s (Loaded from csv)")

    with open(lexicon_path_pkl, 'wb') as f:
        pickle.dump(lexicon, f)
        print("Written into pickle file from csv file")
        
    return lexicon

if __name__ == "__main__":
    lexicon = load_lexicon()
    print("Sample entries:", list(lexicon.items())[:10])  # shows first 10 items