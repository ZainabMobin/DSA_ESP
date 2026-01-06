from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time, sys, os, json

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
# Startup Event loads required data structures for searching
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
@app.get("/json/{docID:int}")
def open_json(docID: int):
    print("🔥HIT /json ROUTE doc_id: ", docID)
    fp = search_context.get_file_content(docID)
    if fp is None:
        print("JSON parse NOT found")
        raise HTTPException(status_code=404, detail="File Not Found")
    print("JSON parse found!")
    print("TYPE OF fp:", type(fp))
    return fp

@app.get("/about.html")
async def about_page():
    return FileResponse(os.path.join("frontend", "about.html"))

@app.get("/safety.html")
async def safety_page():
    return FileResponse(os.path.join("frontend", "safety.html"))

    
@app.get("/index.html")
async def index_page():
    return FileResponse(os.path.join("frontend", "index.html"))


# add document
DOCUMENT_DIR = "documents"
os.makedirs(DOCUMENT_DIR, exist_ok=True)

def add_document(file=None, text=None):
    timestamp = int(time.time())
    filename = f"doc_{timestamp}.txt"
    path = os.path.join(DOCUMENT_DIR, filename)

    if file:
        ext = file.filename.split(".")[-1]

        if ext == "txt":
            content = file.read().decode("utf-8")

        elif ext == "json":
            data = json.loads(file.read().decode("utf-8"))
            content = json.dumps(data, indent=2)

        else:
            return "Unsupported file type"

    elif text:
        content = text

    else:
        return "No document provided"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return "Document added successfully"
