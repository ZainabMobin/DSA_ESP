from preprocessor import preprocess_files
import glob, time, os, csv

if __name__ == "__main__":

    folders = ["./dataset/biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/", 
                "./dataset/comm_use_subset/comm_use_subset/pdf_json/",
                "./dataset/comm_use_subset/comm_use_subset/pmc_json/", 
                "./dataset/noncomm_use_subset/noncomm_use_subset/pdf_json/",
                "./dataset/noncomm_use_subset/noncomm_use_subset/pmc_json/",
                "./dataset/custom_license/custom_license/pdf_json/", 
                "./dataset/custom_license/custom_license/pmc_json/"]
 
    lexicon_path = "./processed_data/lexicon.csv"
    lexicon_path_pkl = "./processed_data/lexicon.pkl"
    word_id = 1
    file_paths = []

    #list all file-paths from all folders
    for f in folders:
        file_paths.extend(glob.glob(os.path.join(f + "*.json")))
    
    print("got all file paths, preparing to lemmatize")

    start = time.time()
    #gets all lemmas
    lemmas = preprocess_files(file_paths, n_process=8)
    end = time.time()
    print(f"Total unique lemmas: {len(lemmas)}")
    print(f"Total time taken: {end-start:.2f} s")

    #writes lexicon to csv file
    with open(lexicon_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["word_id","word"])
        for word in lemmas:
            writer.writerow([word_id, word])
            word_id += 1