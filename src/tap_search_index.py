# -*- coding: utf-8 -*-
"""
tap_search_index.py
=====================
TAP v5.3.2 — Encyclopedia Search Index.

Builds a TF-IDF search index over the full encyclopedia
(287+ entries), enabling keyword search across:
  - Scripts
  - Docs
  - Constants
  - Predictions
  - Concepts
  - Assets

Uses TF-IDF (Term Frequency-Inverse Document Frequency)
for ranking. Output is a simple JSON index that can be
queried at any time.

Each query returns:
  - Top N matches with scores
  - Document type
  - Path/reference
"""

import os
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime


def tokenize(text: str) -> list:
    """Tokenize text into lowercase words."""
    return re.findall(r'[a-zA-Z0-9_]+', text.lower())


def compute_tf(tokens: list) -> dict:
    """Compute term frequency."""
    counter = Counter(tokens)
    total = len(tokens)
    return {k: v / total for k, v in counter.items()}


class TFIDFIndex:
    """TF-IDF search index."""

    def __init__(self):
        self.documents = []  # list of {id, text, type, name, path}
        self.tf = []  # list of dicts
        self.idf = {}  # word -> idf score
        self.doc_freq = defaultdict(int)  # word -> # docs containing

    def add_document(self, doc_id: str, text: str, doc_type: str,
                     name: str, path: str = ""):
        """Add a document to the index."""
        tokens = tokenize(text)
        tf = compute_tf(tokens)
        self.documents.append({
            "id": doc_id,
            "text": text,
            "type": doc_type,
            "name": name,
            "path": path,
            "n_tokens": len(tokens),
        })
        self.tf.append(tf)
        # Update document frequency
        for word in set(tokens):
            self.doc_freq[word] += 1

    def build(self):
        """Build the IDF table."""
        n = len(self.documents)
        for word, df in self.doc_freq.items():
            self.idf[word] = math.log(n / (1 + df)) + 1

    def search(self, query: str, top_k: int = 10) -> list:
        """Search for top_k documents matching the query."""
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        q_tf = compute_tf(q_tokens)
        # Score each document
        scores = []
        for i, doc in enumerate(self.documents):
            score = 0.0
            for word, q_count in q_tf.items():
                if word in self.tf[i]:
                    score += q_count * self.idf.get(word, 0) * self.tf[i][word]
            if score > 0:
                scores.append((score, i))
        scores.sort(reverse=True)
        return [
            {
                "score": round(s, 4),
                "id": self.documents[i]["id"],
                "type": self.documents[i]["type"],
                "name": self.documents[i]["name"],
                "path": self.documents[i]["path"],
                "snippet": self.documents[i]["text"][:120],
            }
            for s, i in scores[:top_k]
        ]


def main():
    print("=" * 80)
    print("  TAP ENCYCLOPEDIA SEARCH INDEX (TF-IDF)")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')

    # Load encyclopedia
    enc_path = os.path.join(assets_dir, 'tap_encyclopedia_full.json')
    with open(enc_path, 'r') as f:
        encyclopedia = json.load(f)

    # Build index
    print("  [1/4] BUILDING TF-IDF INDEX:")
    idx = TFIDFIndex()

    # Add constants
    for k, c in encyclopedia.get("constants", {}).items():
        text = f"{c['name']} {c.get('formula', '')} {c.get('status', '')}"
        idx.add_document(f"const:{k}", text, "constant", c['name'])

    # Add predictions
    for k, p in encyclopedia.get("predictions", {}).items():
        text = f"{k} {p['name']} {p.get('category', '')} {p.get('status', '')}"
        idx.add_document(f"pred:{k}", text, "prediction", p['name'])

    # Add concepts
    for k, c in encyclopedia.get("concepts", {}).items():
        text = f"{c['name']} {c.get('definition', '')}"
        idx.add_document(f"conc:{k}", text, "concept", c['name'])

    # Add scripts
    for s in encyclopedia.get("scripts", []):
        text = f"{s['name']} {s.get('category', '')} {s.get('purpose', '')}"
        idx.add_document(f"script:{s['name']}", text, "script", s['name'], f"src/{s['name']}")

    # Add docs
    for d in encyclopedia.get("docs", []):
        text = f"{d['name']} {d.get('title', '')}"
        idx.add_document(f"doc:{d['name']}", text, "doc", d['name'], f"docs/{d['name']}")

    print(f"    Indexed {len(idx.documents)} documents")
    idx.build()
    print(f"    IDF table size: {len(idx.idf)} words")
    print()

    # Test queries
    print("  [2/4] TEST QUERIES:")
    queries = [
        "breath clock tick φ⁻¹³",
        "P17 plastic cube root",
        "Nami-ryu body listening practice",
        "framework coherence audit",
        "5-year seismic sweep",
        "Tap root tarot",
        "α⁻¹ fine structure 137",
        "sm-hnsw hnsw_sm",
    ]
    for q in queries:
        results = idx.search(q, top_k=5)
        print(f"    Query: {q!r}")
        if not results:
            print(f"      (no results)")
        for r in results:
            print(f"      [{r['score']:>7.4f}] {r['type']:10s} {r['name'][:50]}")
    print()

    # Test specific concept lookup
    print("  [3/4] CONCEPT-SPECIFIC LOOKUP:")
    concept_queries = [
        "P17",
        "P2",
        "φ⁻⁴",
        "Plastic",
        "Nami-ryu",
    ]
    for q in concept_queries:
        results = idx.search(q, top_k=3)
        print(f"    {q}:")
        for r in results:
            print(f"      [{r['score']:>7.4f}] {r['type']:10s} {r['name'][:50]}")
    print()

    # Save index
    print("  [4/4] SAVING INDEX:")
    out_path = os.path.join(assets_dir, 'tap_search_index.json')
    out_data = {
        "timestamp": datetime.now().isoformat(),
        "n_documents": len(idx.documents),
        "n_unique_words": len(idx.idf),
        "documents": [
            {
                "id": d["id"],
                "type": d["type"],
                "name": d["name"],
                "path": d["path"],
                "n_tokens": d["n_tokens"],
            }
            for d in idx.documents
        ],
        "idf_table": idx.idf,
        "tf_table": [
            {k: round(v, 4) for k, v in tf.items()}
            for tf in idx.tf
        ],
    }
    with open(out_path, 'w') as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"    [EXPORT] -> {out_path}")
    print(f"    Index size: {os.path.getsize(out_path):,} bytes")
    print(f"    Total documents: {len(idx.documents)}")
    print(f"    Unique words: {len(idx.idf)}")
    print()

    # Stats
    doc_lengths = [d["n_tokens"] for d in idx.documents]
    print(f"  DOCUMENT LENGTH STATS:")
    print(f"    Min tokens: {min(doc_lengths)}")
    print(f"    Max tokens: {max(doc_lengths)}")
    print(f"    Mean: {statistics.mean(doc_lengths):.1f}")
    print(f"    Median: {statistics.median(doc_lengths):.1f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
