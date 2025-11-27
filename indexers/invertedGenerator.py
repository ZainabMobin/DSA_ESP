""" uses the results of forward index for quicker processing """

import pickle, time, multiprocessing as mp

#build postings for one chunk of doc_ids
def process_chunk(items):
    partial = {}
    for doc_id, tf_dict in items:
        for wid, tf in tf_dict.items():
            if wid not in partial:
                partial[wid] = []
            partial[wid].append((doc_id, tf))
    return partial

if __name__ == "__main__":

    try:
        forward_index = pickle.load(open("./processed_data/forward_index.pkl", "rb"))
    except:
        print("forward index not found :(")
        exit()

    start = time.time()
    inverted = {}

    #split work into chunks
    items = list(forward_index.items())
    n = mp.cpu_count()
    chunk_size = len(items) // n + 1
    chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]

    #parallel processing
    with mp.Pool(processes=n) as pool:
        results = pool.map(process_chunk, chunks)

    #merge results
    for partial in results:
        for wid, postings in partial.items():
            if wid not in inverted:
                inverted[wid] = postings
            else:
                inverted[wid].extend(postings)

    end = time.time()

    print(f"inverted terms: {len(inverted)}")
    print(f"time taken: {end-start:.2f} s")

    pickle.dump(inverted, open("./processed_data/inverted_index.pkl", 'wb'))
    print("saved inverted index!")
    