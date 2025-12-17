from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os 
from pydantic import BaseModel

from services.searchService import main_querying_function
from services.trieService import TrieAutocomplete, initialize_trie

app = FastAPI()

# ----------------------
# Request model for search
# ----------------------
class SearchQuery(BaseModel):
    query: str

trie_auto = TrieAutocomplete()


# Serve /static for CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at / landing page
@app.get("/")
def serve_index():
    return FileResponse(os.path.join("frontend", "index.html"))


# ----------------------
# Endpoint 1: Get continual auto complete suggestions WIP
# ----------------------
# @app.post("autocomplete")


# Needs frontend formatting!!!!!
# ----------------------
# Endpoint 2: Search Query
# ----------------------
@app.post("/search-query")
def search_query(data: SearchQuery):
    # search service function
    results = main_querying_function(data.query, top_k=10)
    return {"results": results}


# ----------------------
# Endpoint 3: Fetch & Parse Document
# ----------------------
@app.get("/fetch-doc-parse/{doc_id}")
def fetch_doc_parse(doc_id: int):
    # Replace this with your actual document fetch/parse service function
    parsed = your_doc_parse_service(doc_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"parsed": parsed}

def your_doc_parse_service(doc_id: int):
    # Your real doc parsing logic goes here
    return {"id": doc_id, "title": "Sample doc", "content": "Sample content"}

# ----------------------
# Endpoint 4: Dynamic Indexing of Document
# ----------------------

# Save trie on shutdown ----------------------
@app.on_event("shutdown")
def shutdown_event():
    trie_auto.save_trie()