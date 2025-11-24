import csv, json, pickle
lexicon_path_csv = "./processed_data/lexicon.csv"
lexicon_path_pkl = "./processed_data/lexicon.pkl"

def load_lexicon():
    lexicon = {}
    try:
        with open(lexicon_path_pkl, 'rb') as f:
            lexicon = pickle.load(f)
        print(f" lexicon with {len(lexicon)} loaded from pickle file!")
        return lexicon
    except (FileNotFoundError, EOFError):
        print("file not found :(")
    
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
        print("Written into pickle file form csv file")
        
    print(f"loaded {len(lexicon)} words from lexicon.csv")
    return lexicon

if __name__ == "__main__":
    lexicon = load_lexicon()
    print("Sample entries:", list(lexicon.items())[:10])  # shows first 10 items