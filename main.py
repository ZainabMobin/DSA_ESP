# MAIN QUERYING FUNCTION

#  from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# import os 
# from pydantic import BaseModel

# from services.searchService import main_querying_function
# from services.trieService import TrieAutocomplete, initialize_trie

# app = FastAPI()

# # ----------------------
# # Request model for search
# # ----------------------
# class SearchQuery(BaseModel):
#     query: str

# trie_auto = TrieAutocomplete()


# # Serve /static for CSS, JS, images, etc.
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

# # Serve index.html at / landing page
# @app.get("/")
# def serve_index():
#     return FileResponse(os.path.join("frontend", "index.html"))


# # ----------------------
# # Endpoint 1: Get continual auto complete suggestions WIP
# # ----------------------
# # @app.post("autocomplete")


# # Needs frontend formatting!!!!!
# # ----------------------
# # Endpoint 2: Search Query
# # ----------------------
# @app.post("/search-query")
# def search_query(data: SearchQuery):
#     # search service function
#     results = main_querying_function(data.query, top_k=10)
#     return {"results": results}


# # ----------------------
# # Endpoint 3: Fetch & Parse Document
# # ----------------------
# @app.get("/fetch-doc-parse/{doc_id}")
# def fetch_doc_parse(doc_id: int):
#     # Replace this with your actual document fetch/parse service function
#     parsed = your_doc_parse_service(doc_id)
#     if not parsed:
#         raise HTTPException(status_code=404, detail="Document not found")
#     return {"parsed": parsed}

# def your_doc_parse_service(doc_id: int):
#     # Your real doc parsing logic goes here
#     return {"id": doc_id, "title": "Sample doc", "content": "Sample content"}

# # ----------------------
# # Endpoint 4: Dynamic Indexing of Document
# # ----------------------

# # Save trie on shutdown ----------------------
# @app.on_event("shutdown")
# def shutdown_event():
#     trie_auto.save_trie()


# app.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time, sys, os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.searchService import main_querying_function
from services.searchContext import SearchContext

# ----------------- FastAPI app -----------------
app = FastAPI(title="DSA Search Service")

# Mount the frontend folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

search_context: SearchContext = None  # Will be initialized at startup

# ----------------- Request Querying model -----------------
class QueryRequest(BaseModel):
    query: str
    top_k: int = 100

# ----------------- Startup Event -----------------
@app.on_event("startup")
async def startup_event():
    global search_context
    start_time = time.time()

    # Create an instance — this runs all loading in __init__
    search_context = SearchContext()

    end_time = time.time()
    print(f"[INFO] All indices loaded in {end_time - start_time:.2f} seconds")

# Serve index.html at the root
@app.get("/")
async def root():
    index_path = os.path.join("frontend", "index.html")
    return FileResponse(index_path)


@app.get("/autocomplete")
def autocomplete(q: str):

    st = time.time()

    if not q or len(q)<2:
        return {"words": []}

    end = time.time()
    print(f"Time to load suggestions: {end-st:.2f} s")

    return {"words": search_context.get_autocomplete_suggestions(q)}


# ----------------- Search Endpoint -----------------
@app.post("/search")
async def search(req: QueryRequest):
    if not search_context:
        return {"error": "Search context not initialized."}

    start = time.time()
    results = main_querying_function(req.query, search_context, req.top_k)
    end = time.time()
    print(f"[INFO] Query processed in {end - start:.4f} seconds")
    return {"results": results}


# ----------------- Health Check -----------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# import os, time
# from pydantic import BaseModel
# from services.searchService import main_querying_function
# from services.trieService import TrieAutocomplete, initialize_trie
# from services.trieService import initialize_trie, get_autocomplete

# app = FastAPI()

# # ----------------------
# # Request model for search
# # ----------------------
# class SearchQuery(BaseModel):
#     query: str

# @app.on_event("startup")
# def startup_event():
#     st = time.time()
#     initialize_trie()
#     end = time.time()

#     print(f"Time to load Trie: {end-st:.2f} s")

# @app.on_event("shutdown")
# def shutdown_event():
#     from services.trieService import trie_autocomplete
#     trie_autocomplete.save_trie()

# @app.get("/autocomplete")
# def autocomplete(q: str):

#     st = time.time()

#     if not q:
#         return {"words": []}
#     end = time.time()

#     print(f"Time to load Trie: {end-st:.2f} s")
    
#     return {"words": get_autocomplete(q)}

# # ----------------------
# # Endpoint 2: Search Query
# # ----------------------
# @app.post("/search-query")
# def search_query(data: SearchQuery):
#     # search service function
#     results = main_querying_function(data.query, top_k=10)
#     return {"results": results}


