"""Full-text search for property listings."""
import re, logging
from typing import List, Dict, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class PropertySearch:
    """Full-text search engine for properties."""

    STOP_WORDS = {"the", "a", "an", "in", "of", "for", "and", "or", "is", "at", "to"}

    def __init__(self):
        self.index: Dict[str, set] = {}
        self.documents: Dict[int, Dict] = {}

    def index_property(self, property_id: int, data: Dict):
        """Index a property for search."""
        self.documents[property_id] = data
        text = " ".join(str(v) for v in data.values() if isinstance(v, str))
        tokens = self._tokenize(text)
        for token in tokens:
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(property_id)

    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search properties by text query."""
        tokens = self._tokenize(query)
        candidate_ids = None
        for token in tokens:
            matches = self.index.get(token, set())
            if candidate_ids is None:
                candidate_ids = matches.copy()
            else:
                candidate_ids &= matches
        if not candidate_ids:
            return []
        scored = []
        for pid in candidate_ids:
            doc = self.documents[pid]
            score = sum(1 for t in tokens if t in " ".join(str(v) for v in doc.values()).lower())
            scored.append({"id": pid, "score": score, **doc})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize and clean text."""
        text = text.lower()
        tokens = re.findall(r"\w+", text)
        return [t for t in tokens if t not in self.STOP_WORDS and len(t) > 2]

    def suggest(self, partial: str, limit: int = 5) -> List[str]:
        """Suggest completions for partial queries."""
        partial = partial.lower()
        suggestions = [token for token in self.index.keys() if token.startswith(partial)]
        freq = {s: len(self.index[s]) for s in suggestions}
        return sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:limit]
