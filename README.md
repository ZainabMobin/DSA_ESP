
- initial design for pre-built indices
- CORD 2020-4-10 dataset contains 51k+ papers with 59k+ text_parses

installation codes for spaCy:
- pip install spacy
- python -m spacy download en_core_web_sm


LEXICON:
    saved in csv for speed, space and simple structure
    Later saved in pickle file (binary encoding) for fast loading. .pkl file loaded from .csv reduces discrepancies 
        csv loading -> 49810 words -> 0.7 s
        pkl loading -> 49810 words -> 0.2 s

  csv -> compact, efficient for flat/simple data, faster in reading and writing than json
      trend: logarithmic, time decreases as files increase

  json -> space taking, efficient for heirarchial/structured data, rel slower in reading and writing cus of extra formatting overheads

  word filters:
  lowercased -> punctuation removed -> isascii() and isalpha() & not digit() & len>2 & not repeating letters & not in forbidden substrings -> spaCy lemmatization -> add word from words if not in lexicon
                   
  METRICS:
  Processing files sequentialy in order:
      1(100) files -> 21.84s -> 10965 words -> 4.45 files/s ||| 3hr 35m 53 s  for 59311 files
      7(100) files -> 104.92s -> 40140 words -> 6.7 files/s ||| 2hr 28m 10s for 59311 files
      1(1625) files -> 192.71s -> 49810 -> 8.4 files/s ||| 1hr 57m 14s for 59311 files

  FUTURE: 
  include multiprocessing on cpu cores for optimized lexicon generation for full dataset
  nlp pipe -> supports n_process which parallizes processes accross multiple cores
  multicore parallel processing -> faster lexicon generation
Target: 30-35 mins
