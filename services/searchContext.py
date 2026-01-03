from loaders.lexiconLoader import load_lexicon, load_lexicon_posting_gzip
from loaders.forwardLoader import load_forward
from loaders.mapLoaders import load_docmap, load_docmeta
from loaders.gloveLoader import load_glove_matrix
from services.trieService import TrieAutocomplete
from indexers.preprocessor import fetch_file_parse

class SearchContext:
    def __init__(self):
        # Load all necessary data once
        self.lexicon_gzip = load_lexicon_posting_gzip()
        self.lexicon = load_lexicon()
        self.forward_index = load_forward()
        self.doc_map = load_docmap()
        self.doc_meta = load_docmeta()
        self.glove_words, self.glove_matrix = load_glove_matrix()

        self.trie = TrieAutocomplete()
        
        # Initialize trie (uses lexicon and lexicon_gzip)
        self.trie.initialize_trie(self.lexicon, self.lexicon_gzip)

    # Method to expose autocomplete
    def get_autocomplete_suggestions(self, query: str):
        if not query or len(query) < 2:
            return []
        words = query.split(" ")
        last_word = words[-1]
        return self.trie.autocomplete(last_word)
    
    #method to get fileparse from docID 
    def get_file_content(self, docID: int):
        try:
            fp = self.doc_map.get(docID)
            # Filepath not found
            if not fp: return None
            return fetch_file_parse(fp)
        except Exception:
            return None
    