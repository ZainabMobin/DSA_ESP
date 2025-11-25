#works with preprocessing of data, scripts run when search engine server is fired up initially (for dynamic indices, new document data is added to existing indices and lexicon in this layer)

#Role is pretty static for pre-built indices
# just loads and returns indices, lexicon to the service layer.

import time
from loaders.lexiconLoader import load_lexicon

def get_lexicon():
    #for time-metric measurement
    start_time = time.time()
    lexicon = load_lexicon() #loads lexicon in RAM
    end_time = time.time()

    print(f" imported lexicon in {end_time - start_time:.2f} s")
    return lexicon

