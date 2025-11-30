from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import sys

#type aliases
DocID = int
TermID = int

#metadata path
METADATA_PATH = "sample.csv"

@dataclass
class TermOcc:
    tid: TermID
    pos: List[int]

#global maps
term_to_id: Dict[str, TermID] = {}
forward_index: Dict[DocID, List[TermOcc]] = {}

def parse_csv_line(line: str) -> List[str]:
    #simple csv parser for quoted fields
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

def tokenize(s: str) -> List[str]:
    #keep alphabets and spaces only
    cleaned_chars: List[str] = []
    for c in s:
        if c.isalpha() or c.isspace():
            cleaned_chars.append(c.lower())
        else:
            cleaned_chars.append(" ")
    cleaned = "".join(cleaned_chars)
    return [tok for tok in cleaned.split() if tok]

def load_lexicon() -> None:
    #load term ids
    try:
        lx = open("lexicon.txt", "r", encoding="utf-8", errors="replace")
    except OSError:
        sys.stderr.write("lexicon.txt not found\n")
        sys.exit(1)

    for line in lx:
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        term = parts[0]
        try:
            tid = int(parts[1])
        except ValueError:
            continue
        term_to_id[term] = tid

    lx.close()

def main() -> int:
    load_lexicon()

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

    #find column indexes
    title_col = -1
    authors_col = -1
    abs_col = -1

    for i, h in enumerate(head):
        h_lower = "".join(ch.lower() for ch in h)
        if h_lower == "title":
            title_col = i
        elif h_lower == "authors":
            authors_col = i
        elif h_lower == "abstract":
            abs_col = i

    if title_col == -1 and abs_col == -1:
        sys.stderr.write("no title or abstract column found\n")
        return 1

    doc_id: DocID = 1
    max_id: DocID = 0

    #read rows
    for raw_line in fin:
        line = raw_line.rstrip("\n\r")
        if not line:
            doc_id += 1
            continue

        cols = parse_csv_line(line)
        max_needed = max(title_col, abs_col)
        if authors_col != -1:
            max_needed = max(max_needed, authors_col)
        if len(cols) <= max_needed:
            doc_id += 1
            continue

        #extract fields
        title = cols[title_col] if title_col != -1 else ""
        authors = cols[authors_col] if authors_col != -1 else ""
        abstract = cols[abs_col] if abs_col != -1 else ""

        text = f"{title} {authors} {abstract}"
        tokens = tokenize(text)

        #store positions
        term_positions: Dict[TermID, List[int]] = {}
        for pos, tok in enumerate(tokens):
            tid = term_to_id.get(tok)
            if tid is None:
                continue
            term_positions.setdefault(tid, []).append(pos)

        if term_positions:
            occs = [
                TermOcc(tid=tid, pos=sorted(positions))
                for tid, positions in sorted(term_positions.items())
            ]
            forward_index[doc_id] = occs
            max_id = max(max_id, doc_id)

        doc_id += 1

    fin.close()

    #write output
    try:
        fout = open("forward_index.txt", "w", encoding="utf-8")
    except OSError:
        sys.stderr.write("cannot write forward_index.txt\n")
        return 1

    for d in range(1, max_id + 1):
        terms = forward_index.get(d)
        if not terms:
            continue

        fout.write(f"{d} {len(terms)} ")
        blocks = []
        for occ in terms:
            positions_str = ",".join(str(p) for p in occ.pos)
            blocks.append(f"{occ.tid}:{positions_str}")
        fout.write(";".join(blocks))
        fout.write("\n")

    fout.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
