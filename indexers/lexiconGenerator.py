from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set
import sys
import os

#type aliases
DocID = int
TermID = int

#metadata path
METADATA_PATH = "sample.csv"

@dataclass
class LexiconEntry:
    term_id: TermID
    doc_freq: int = 0

#global data
lexicon: Dict[str, LexiconEntry] = {}
next_term_id: TermID = 1

def tokenize(s: str) -> List[str]:
    #clean non alphabet chars
    cleaned_chars = []
    for c in s:
        if c.isalpha() or c.isspace():
            cleaned_chars.append(c.lower())
        else:
            cleaned_chars.append(" ")
    cleaned = "".join(cleaned_chars)
    return [tok for tok in cleaned.split() if tok]

def parse_csv_line(line: str) -> List[str]:
    #simple csv parser with quote handling
    cols: List[str] = []
    cur: List[str] = []
    inq = False
    i = 0
    n = len(line)

    while i < n:
        c = line[i]
        if c == '"':
            if inq and i + 1 < n and line[i + 1] == '"':
                cur.append('"')
                i += 2
                continue
            else:
                inq = not inq
        elif c == "," and not inq:
            cols.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1

    cols.append("".join(cur))
    return cols

def index_doc(doc_id: DocID, text: str) -> None:
    #update lexicon for one document
    global next_term_id
    tokens = tokenize(text)
    seen: Set[str] = set()

    for t in tokens:
        if t in seen:
            continue
        entry = lexicon.get(t)
        if entry is None:
            lexicon[t] = LexiconEntry(term_id=next_term_id, doc_freq=1)
            next_term_id += 1
        else:
            entry.doc_freq += 1
        seen.add(t)

def main() -> int:
    #open metadata file
    try:
        fin = open(METADATA_PATH, "r", encoding="utf-8", errors="replace")
    except OSError:
        sys.stderr.write("metadata.csv not found\n")
        return 1

    header = fin.readline()
    if not header:
        sys.stderr.write("empty metadata.csv\n")
        return 1

    head = parse_csv_line(header.rstrip("\n\r"))

    #find required columns
    title_col = -1
    authors_col = -1
    abs_col = -1

    for i, h in enumerate(head):
        h_lower = "".join(ch.lower() for ch in h)
        if h_lower == "title":
            title_col = i
        if h_lower == "authors":
            authors_col = i
        if h_lower == "abstract":
            abs_col = i

    if title_col == -1 and abs_col == -1:
        sys.stderr.write("no title or abstract column found\n")
        return 1

    doc_id: DocID = 1

    #process rows
    for raw_line in fin:
        line = raw_line.rstrip("\n\r")
        if not line:
            continue

        cols = parse_csv_line(line)
        max_needed = max(title_col, abs_col)
        if authors_col != -1:
            max_needed = max(max_needed, authors_col)
        if len(cols) <= max_needed:
            doc_id += 1
            continue

        title = cols[title_col] if title_col != -1 else ""
        authors = cols[authors_col] if authors_col != -1 else ""
        abstract = cols[abs_col] if abs_col != -1 else ""

        if not title and not abstract:
            doc_id += 1
            continue

        text = f"{title} {authors} {abstract}"
        index_doc(doc_id, text)
        doc_id += 1

    fin.close()

    #write lexicon file
    try:
        fout = open("lexicon.txt", "w", encoding="utf-8")
    except OSError:
        sys.stderr.write("cannot write lexicon.txt\n")
        return 1

    for term, entry in lexicon.items():
        fout.write(f"{term} {entry.term_id} {entry.doc_freq}\n")

    fout.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
