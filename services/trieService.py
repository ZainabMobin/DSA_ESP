import spacy, time, sys, os, string
from collections import defaultdict
import math
import numpy as np
import gzip, pickle # Added for saving/loading trie in pkl.gz file


# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loaders.barrelLoader import fetch_barrel_results_binary_offset

# TRIE IMPLEMENTATION STARTS HERE
class TrieNode:
    """Trie node for autocomplete"""
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.frequency = 0  # How many times this word appears
        self.doc_freq = 0   # In how many documents it appears
        self.last_updated = time.time() # when the word was updated
        self.quality_score = 1.0  # Confidence/quality metric   
        

class TrieAutocomplete:
    """Trie-based autocomplete with forward index metrics"""
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0
        self.trie_file = "./processed_data/trie_data.pkl.gz"
        
        os.makedirs("./processed_data", exist_ok=True)
        os.makedirs(os.path.dirname(self.trie_file), exist_ok=True)

    
    def build_from_lexicon_and_save(self, lexicon, lexicon_gzip):
        """Build trie from scratch with the lexicon and forward index frequencies as context/relevance
            then saves it in pkl.gz file"""

        start = time.time()
        print(f"[TRIE] Building trie with {len(lexicon)} lexicon entries...")
        
        # lexicon is the reverse lexicon: word -> wordID
        for word, wordID in lexicon.items():
            # Get document frequency from lexicon_gzip
            if wordID in lexicon_gzip:
                df = 0
                for b in lexicon_gzip[wordID]:
                    # Get actual document frequency from barrel
                    barrel_info = fetch_barrel_results_binary_offset(b['barrel_id'], b['offset'], b['length_bytes'])
                    df += len(barrel_info)
                
                # Insert with frequency metrics
                self.insert(word, frequency=df, doc_frequency=df)
        self.save_trie()
        end = time.time()
        print(f"[TRIE] Built and saved trie with {self.word_count} words in {end-start:.2f} s")


    def insert(self, word, frequency=1, doc_frequency=1, quality_score=1.0):
        """Insert a word into trie with metrics"""
        node = self.root
        word_lower = word.lower()
        
        for char in word_lower:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Update metrics if word already exists
        if node.is_end:
            node.frequency += frequency
            node.doc_freq += doc_frequency
            node.quality_score = max(node.quality_score, quality_score)
        else:
            node.is_end = True
            node.frequency = frequency
            node.doc_freq = doc_frequency
            node.quality_score = quality_score
            self.word_count += 1
        
        node.last_updated = time.time()


    def load_or_build_trie(self, lexicon, lexicon_gzip):
        """Load existing trie or build from lexicon if missing/empty"""
        if not os.path.exists(self.trie_file):
            print("[TRIE] Trie file not found. Building from lexicon...")
            self.build_from_lexicon_and_save(lexicon, lexicon_gzip)
            return

        try:
            with gzip.open(self.trie_file, 'rb') as f:
                self.root = pickle.load(f)

            if not self.root.children:  # empty trie
                print("[TRIE] Trie file empty. Building from lexicon...")
                self.build_from_lexicon_and_save(lexicon, lexicon_gzip)
                return

            print(f"[TRIE] Loaded {self.word_count} words from {self.trie_file}")
        except Exception as e:
            print(f"[TRIE] Failed to load trie: {e}. Rebuilding from lexicon...")
            self.build_from_lexicon_and_save(lexicon, lexicon_gzip)


    def initialize_trie(self, lexicon, lexicon_gzip):
        """Call this once on startup"""
        print("[TRIE] Initializing autocomplete system...")
        self.load_or_build_trie(lexicon, lexicon_gzip)
        print("[TRIE] Autocomplete system ready!")


    def _collect_words(self, node, current_word, results):
        """DFS to collect words from node"""
        if node.is_end:
            results.append({
                'word': current_word,
                'frequency': node.frequency,
                'doc_freq': node.doc_freq,
                'quality': node.quality_score,
                'last_updated': node.last_updated
            })
        
        for char, child_node in node.children.items():
            self._collect_words(child_node, current_word + char, results)
    

    def search_prefix(self, prefix):
        """Find all words with given prefix"""
        node = self.root
        prefix_lower = prefix.lower()
        
        # Navigate to prefix node
        for char in prefix_lower:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all words from this node
        results = []
        self._collect_words(node, prefix_lower, results)
        return results
    

    def autocomplete(self, prefix, limit=3, min_freq=1, min_quality=0.1):
        """Get autocomplete suggestions with ranking"""
        words = self.search_prefix(prefix)
        
        if not words:
            return []
        
        # Filter by frequency and quality
        filtered = [
            w for w in words 
            if w['frequency'] >= min_freq and w['quality'] >= min_quality
        ]
        
        # Rank by: 1. Prefix exactness, 2. Frequency, 3. Quality 4. Recency
        def rank_score(word_data):
            word = word_data['word']
            freq = word_data['frequency']
            quality = word_data['quality']
            
            # Exact prefix match bonus
            prefix_bonus = 10 if word.startswith(prefix.lower()) else 0
            
            # Logarithmic frequency scaling (diminishing returns)
            freq_score = math.log1p(freq)
            
            # Quality multiplier
            quality_mult = word_data['quality']
            
            # Recency bonus (recently updated words get small boost)
            recency = (time.time() - word_data['last_updated']) / 86400  # days
            recency_bonus = max(0, 1 - (recency / 30))  # decays over 30 days
            
            return (prefix_bonus + freq_score * quality_mult + recency_bonus)        
        
        # Sort by ranking score
        filtered.sort(key=rank_score, reverse=True)
        # Return words
        return [w['word'] for w in filtered[:limit]]
    

    def save_trie(self):
        """Save trie to disk"""
        try:
            with gzip.open(self.trie_file, 'wb') as f:
                pickle.dump(self.root, f)
            
            print(f"[TRIE] Saved {self.word_count} words to {self.trie_file}")
        except Exception as e:
            print(f"[TRIE] Error saving trie: {e}")

