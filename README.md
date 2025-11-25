- Design for pre-built indices
- CORD 2020-4-10 dataset contains 51k+ papers with 59k+ text_parses

installation codes for spaCy:

    pip install spacy
    python -m spacy download en_core_web_sm

LEXICON:

Saved in csv for speed, space and simple structure

Saved in pickle file (binary encoding) for fast loading. 

*FULL LEXICON LOADING IN RAM*:

        csv loading -> 1,068,517 words -> 1.32 s
        pkl loading -> 1,068,517 words -> 0.38 s

csv -> compact, efficient for flat/simple data, faster in reading and writing than json
    trend: logarithmic, time decreases as files increase

json -> space taking, efficient for heirarchial/structured data, slower in reading and writing (extra formatting overheads)

*STRATEGY:*
 
    2 level multi-core Processing done for optimized lexicon generation for full dataset

    - Initially, content is read from files in parallel
    - Read Content is processed and filtered words are stored in a dict. Batch Lemmitization is done with multi-core processing

*COMPARISON METRICS:*
    
    (PREVIOUS) SEQUENTIAL PROCESSING: 1625 files -> 235.56s -> 93261 words -> 6.9 files/s ||| 2h 23m 17s for 5931 files
    
    Used Giant concatenated string: 10,000 ~ files -> 403.23 s -> 405050 words

    (CURRENT) MULTICORE PROCESSING: 1625 files -> 50.11s -> 93261 words -> 32.4 files/s ||| 30m 29s for 59311 files
    
    Content string from each file -> cleaned and saved in set() -> all sets are joined (union)
    

*MULTICORE PARALLEL PROCESSING METRICS:*

    10,000 ~ files -> 155.23 s (1m 55s) -> 360,067 words
    
    22787 files -> 245.79s (4m 6s) -> 470,578 words
    
    32806 files -> 321.23 s (5m 21s) -> 662,799 words 

    FULL TEXT LEXICON | TASK MANAGER METRICS: [ ~40% CPU ~60% Memory]
    
    59311 files -> 1038.45 s (17m 19s) -> 1,068,517 words   

FUTURE WORK:

- Create Forward and Inverted Indices
- Upload Dataset (compressed) i.e provide a way to access it with identical folder structure (compatibility with written code)
- Scale system to accomodate dynamic indexing (processing added files, done at runtime)
