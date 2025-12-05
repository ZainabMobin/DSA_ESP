# calls loaders initailly to load lexicon and lindices into RAM 
# handles search queries,and prompts information retreival from the queried words 
# run time oriented

from services.documentService import get_lexicon
lexicon = get_lexicon() #lexicon (dict, word -> word_id)

def some_querying_func():
    print("This is a function")