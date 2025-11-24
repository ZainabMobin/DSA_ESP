import os, glob, json, csv, string, time
import spacy

nlp = spacy.load("en_core_web_sm") #initializes spaCy lemmitization pipeline

lexicon = {}  # dict that saves word to wordID
word_id = 1
forbidden_substrings = ["@", ".", "/", "(", ")", "http", "https", "www", "%", "|", "=", "<", ">", "≥", "≤","±", ",", "*", "+", "&", "~", "[", "]", "×", ":", "£", '$', "#", "°", "ỹ", "˳", "ˆ", " •"]

# folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/"]
lexicon_path = "./processed_data/lexicon.csv"

doc_num = 1
folder_num = 1
start_time = time.time()

folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/"]

"""folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/", 
           "./dataset/comm_use_subset/comm_use_subset/pdf_json/",
           "./dataset/comm_use_subset/comm_use_subset/pmc_json/", 
           "./dataset/noncomm_use_subset/noncomm_use_subset/pdf_json/",
           "./dataset/noncomm_use_subset/noncomm_use_subset/pmc_json/", 
           "./dataset/custom_license/custom_license/pdf_json/", 
           "./dataset/custom_license/custom_license/pmc_json/"]"""

for folder in folders:
    pattern = os.path.join(folder, "*.json")

    for filepath in glob.glob(pattern):
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FILE BREAK {doc_num}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        with open(filepath, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)

        # combine all text
        content = ""

        if "metadata" in parsed_data:
            meta = parsed_data["metadata"]
            content += " " + (meta.get("title") or "")
            authors = meta.get("authors") or []
            for auth in authors:
                content += " " + (auth.get("first") or "")
                mid = auth.get(("middle") or "")
                if isinstance(mid, list):
                    mid = " ".join(mid)
                content += " " + (mid or "")
                content += " " + (auth.get("last") or "")
                content += " " + (auth.get("suffix") or "")
                content += " " + (auth.get("email") or "")
                
                affil = auth.get("affiliation") or {}
                content += " " + (affil.get("laboratory") or "")
                content += " " + (affil.get("institution") or "")
                loc = affil.get("location") or {}
                content += " " + (loc.get("postCode") or "")
                content += " " + (loc.get("settlement") or "")
                content += " " + (loc.get("country") or "")

        for section in ["abstract", "body_text", "back_matter"]:
            if section in parsed_data:
                for section in parsed_data[section]:
                    content += " " + (section.get("text") or "")

        if "bib_entries" in parsed_data:
            bib = parsed_data["bib_entries"]
            content += " " + (bib.get("title") or "")
            content += " " + (bib.get("venue") or "")
            for auth in bib.get("authors", []):
                content += " " + (auth.get("first") or "")
                mid = auth.get("middle") or ""
                if isinstance (mid, list):
                    mid = " ".join(mid)
                content += " " + mid
                content += " " + (auth.get("last") or "")
                content += " " + (auth.get("suffix") or "")

        if "ref_entries" in parsed_data:
            ref = parsed_data["ref_entries"]
            content += " " + (ref.get("title") or "")

        # split and clean words
        cleaned_words = set()
        for word in content.strip().split():
            w = word.lower().strip(string.punctuation)
            #if word is empty after stripping
            if not w:
                continue
            #filtering conditions       
            if not w.isascii() or not w.isalpha() or w.isdigit() or len(word) < 2 or all(c==word[0] for c in word):
                continue
            #check if unlemmatized word is already in lexicon
            if w in lexicon:
                continue
            cleaned_words.add(w)

        # lemmatize words stored in in cleaned_words
        #n_process=os.cpu_count() ---> multi core processing done in parallel
        for doc in nlp.pipe(cleaned_words, batch_size=1000, n_process=os.cpu_count(), disable=["parser", "ner"]):
            if len(doc) == 0:  # skip empty doc
                continue
            lemma = doc[0].lemma_

            if lemma in lexicon:
                continue
            #add lemmatized word in lexicon
            lexicon[lemma] = word_id
            print(f" {word_id} | {lemma}")
            word_id += 1

        doc_num += 1
        # if (doc_num > 100): 
        #     print("-------------------------Folder complete!---------------------")
        #     break
    
    print(f"########################################  FOLDER {folder_num} DONE ###################################################")
    folder_num +=1
    doc_num = 1

end_time = time.time()
print(f"\n Full Lexicon generation completed in {end_time - start_time:.2f} seconds for {folder_num-1} folders.")

# save lexicon to file
with open(lexicon_path, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    for lemma, word_id in lexicon.items():
        writer.writerow([word_id, lemma])
