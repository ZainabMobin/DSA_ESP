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
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time
import sys
import os

# -------------------------------------------------
# Add project root to Python path
# -------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.searchService import main_querying_function
from services.searchContext import SearchContext

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(title="DSA Search Service")

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

search_context: SearchContext | None = None

# -------------------------------------------------
# Request Model
# -------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    top_k: int = 100

# -------------------------------------------------
# Startup Event
# -------------------------------------------------
@app.on_event("startup")
async def startup_event():
    global search_context
    start_time = time.time()

    search_context = SearchContext()

    end_time = time.time()
    print(f"[INFO] All indices loaded in {end_time - start_time:.2f} seconds")

# -------------------------------------------------
# Serve index.html
# -------------------------------------------------
@app.get("/")
async def root():
    return FileResponse(os.path.join("frontend", "index.html"))

# -------------------------------------------------
# Autocomplete Endpoint
# -------------------------------------------------
@app.get("/autocomplete")
def autocomplete(q: str):
    if not q or len(q) < 2:
        return {"words": []}

    start = time.time()
    words = search_context.get_autocomplete_suggestions(q)
    end = time.time()

    print(f"[INFO] Autocomplete processed in {(end - start):.4f} seconds")

    return {"words": words}

# -------------------------------------------------
# Search Endpoint
# -------------------------------------------------
@app.post("/search")
async def search(req: QueryRequest):
    if not search_context:
        raise HTTPException(status_code=500, detail="Search context not initialized")

    start = time.time()
    results = main_querying_function(req.query, search_context, req.top_k)
    end = time.time()

    time_taken_ms = round((end - start) * 1000, 2)

    print(f"[INFO] Query processed in {time_taken_ms} ms")

    return {
        "results": results,
        "time_taken": time_taken_ms
    }

# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# -------------------------------------------------
# JSON File Serving Endpoint
# -------------------------------------------------
@app.get("/json/{file_path:path}")
def open_json(file_path: str):
    base_dir = os.path.abspath("data/docs")
    requested_path = os.path.abspath(os.path.join(base_dir, file_path))

    # Security check
    if not requested_path.startswith(base_dir):
        raise HTTPException(status_code=403, detail="Access forbidden")

    if not os.path.exists(requested_path):
        raise HTTPException(status_code=404, detail="JSON file not found")

    print(f"[INFO] Serving JSON file: {requested_path}")

    return FileResponse(
        requested_path,
        media_type="application/json",
        filename=os.path.basename(requested_path)
    )


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


