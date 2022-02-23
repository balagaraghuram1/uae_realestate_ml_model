"""Sentiment analysis model for real estate market news and social media."""
import re, logging
from typing import Dict, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analyze sentiment of real estate news and market commentary."""

    POSITIVE_WORDS = {
        "growth", "boom", "increase", "rise", "surge", "profit", "gain", "strong",
        "positive", "bullish", "recovery", "demand", "opportunity", "outperform",
        "upgrade", "upgrade", "optimistic", "expansion", "milestone", "record",
    }
    NEGATIVE_WORDS = {
        "decline", "drop", "crash", "loss", "weakness", "bearish", "downturn",
        "slump", "recession", "negative", "risk", "concern", "oversupply",
        "default", "debt", "volatility", "uncertainty", "slowdown", "contraction",
    }
    INTENSIFIERS = {"very", "extremely", "significantly", "sharply", "dramatically"}
    NEGATORS = {"not", "no", "never", "neither", "nor", "barely", "hardly"}

    def __init__(self, lexicon_path: Optional[str] = None):
        self.custom_lexicon = {}
        if lexicon_path:
            self._load_custom_lexicon(lexicon_path)

    def _load_custom_lexicon(self, path: str):
        """Load custom sentiment lexicon."""
        import json
        try:
            with open(path) as f:
                self.custom_lexicon = json.load(f)
        except Exception as e:
            logger.warning("Failed to load lexicon: %s", e)

    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of a text."""
        tokens = self._tokenize(text)
        scores = self._compute_scores(tokens)
        return {
            "text": text[:200],
            "sentiment": self._label_sentiment(scores["compound"]),
            "scores": scores,
            "key_phrases": self._extract_key_phrases(tokens),
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for a batch of texts."""
        return [self.analyze(text) for text in texts]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize and clean text."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return text.split()

    def _compute_scores(self, tokens: List[str]) -> Dict:
        """Compute sentiment scores."""
        positive, negative, neutral = 0, 0, 0
        negated = False
        intensified = False
        for i, token in enumerate(tokens):
            if token in self.NEGATORS:
                negated = True
                continue
            if token in self.INTENSIFIERS:
                intensified = True
                continue
            weight = 2.0 if intensified else 1.0
            if token in self.custom_lexicon:
                score = self.custom_lexicon[token]
                if negated:
                    score *= -1
                if score > 0:
                    positive += score * weight
                else:
                    negative += abs(score) * weight
            elif token in self.POSITIVE_WORDS:
                if negated:
                    negative += 1.0 * weight
                else:
                    positive += 1.0 * weight
            elif token in self.NEGATIVE_WORDS:
                if negated:
                    positive += 0.5 * weight
                else:
                    negative += 1.0 * weight
            else:
                neutral += 1
            negated = False
            intensified = False
        total = positive + negative + neutral
        compound = (positive - negative) / max(total, 1)
        return {
            "positive": round(positive, 2),
            "negative": round(negative, 2),
            "neutral": round(neutral, 2),
            "compound": round(compound, 4),
            "pos_ratio": round(positive / max(positive + negative, 1), 4),
        }

    def _label_sentiment(self, compound: float) -> str:
        """Label compound score as positive/negative/neutral."""
        if compound >= 0.3:
            return "positive"
        elif compound <= -0.3:
            return "negative"
        return "neutral"

    def _extract_key_phrases(self, tokens: List[str]) -> List[str]:
        """Extract notable phrases from tokens."""
        key = [t for t in tokens if t in self.POSITIVE_WORDS or t in self.NEGATIVE_WORDS]
        return [word for word, _ in Counter(key).most_common(5)]

    def market_sentiment_summary(self, texts: List[str]) -> Dict:
        """Aggregate sentiment across multiple texts."""
        results = [self.analyze(text) for text in texts]
        sentiments = [r["sentiment"] for r in results]
        avg_compound = sum(r["scores"]["compound"] for r in results) / max(len(results), 1)
        return {
            "total_texts": len(texts),
            "distribution": {
                "positive": sentiments.count("positive"),
                "negative": sentiments.count("negative"),
                "neutral": sentiments.count("neutral"),
            },
            "avg_compound": round(avg_compound, 4),
            "overall_sentiment": self._label_sentiment(avg_compound),
        }
