from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import sys

#type aliases
DocID = int
TermID = int

@dataclass
class Posting:
    doc_id: DocID
    pos: List[int]

#inverted index map
inv: Dict[TermID, List[Posting]] = {}

def ltrim(s: str) -> str:
    #remove leading spaces
    return s.lstrip(" \t\r")

def main() -> int:
    #open forward index file
    try:
        fin = open("forward_index.txt", "r", encoding="utf-8", errors="replace")
    except OSError:
        sys.stderr.write("forward_index.txt not found\n")
        return 1

    #read lines
    for raw_line in fin:
        line = raw_line.rstrip("\n\r")
        if not line:
            continue

        parts = line.split(maxsplit=2)
        if len(parts) < 3:
            continue

        try:
            d = int(parts[0])
        except ValueError:
            continue

        rest = ltrim(parts[2])
        if not rest:
            continue

        #parse term blocks tid:pos,pos
        for block in rest.split(";"):
            block = ltrim(block)
            if not block or ":" not in block:
                continue

            tid_str, pos_str = block.split(":", 1)

            try:
                tid = int(tid_str)
            except ValueError:
                continue

            positions: List[int] = []
            for t in pos_str.split(","):
                t = ltrim(t)
                if t:
                    try:
                        positions.append(int(t))
                    except ValueError:
                        continue

            if not positions:
                continue

            inv.setdefault(tid, []).append(Posting(doc_id=d, pos=positions))

    fin.close()

    #sort postings by doc id
    for plist in inv.values():
        plist.sort(key=lambda p: p.doc_id)

    #write inverted index
    try:
        fout = open("inverted_index.txt", "w", encoding="utf-8")
    except OSError:
        sys.stderr.write("cannot write inverted_index.txt\n")
        return 1

    for tid in sorted(inv.keys()):
        plist = inv[tid]
        fout.write(f"{tid} {len(plist)} ")

        blocks = []
        for posting in plist:
            pos_str = ",".join(str(p) for p in posting.pos)
            blocks.append(f"{posting.doc_id}:{pos_str}")

        fout.write(";".join(blocks))
        fout.write("\n")

    fout.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
