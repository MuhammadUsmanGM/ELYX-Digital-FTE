"""
Advanced NLP Processor for ELYX AI Service.
Provides text analysis, entity extraction, sentiment analysis, and intent classification.
"""
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AdvancedNLPProcessor:
    """NLP processor for task text analysis using keyword-based heuristics."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # Sentiment keywords
        self._positive = {'good', 'great', 'excellent', 'happy', 'success', 'completed', 'done', 'approved', 'profit', 'growth'}
        self._negative = {'bad', 'fail', 'error', 'urgent', 'overdue', 'rejected', 'loss', 'issue', 'problem', 'critical'}

        # Intent patterns
        self._intent_patterns = {
            'task_creation': ['create', 'add', 'new', 'setup', 'build', 'make'],
            'task_completion': ['complete', 'finish', 'done', 'close', 'resolve'],
            'information_request': ['what', 'how', 'why', 'when', 'where', 'status', 'check', 'find'],
            'strategic_planning': ['plan', 'strategy', 'forecast', 'goal', 'roadmap', 'schedule'],
            'communication': ['send', 'email', 'message', 'reply', 'respond', 'contact', 'whatsapp'],
            'financial': ['invoice', 'payment', 'budget', 'expense', 'revenue', 'salary'],
        }

    def process_multi_modal_content(self, text: str = "", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze text content and return NLP insights.

        Args:
            text: Input text to analyze
            metadata: Optional metadata for context

        Returns:
            Dictionary with entities, sentiment, intent, and keywords
        """
        if not text:
            return self._empty_result()

        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        entities = self._extract_entities(text)
        sentiment = self._analyze_sentiment(words)
        intent = self._classify_intent(words)
        keywords = self._extract_keywords(words)

        return {
            'entities': entities,
            'sentiment': sentiment,
            'intent': intent,
            'keywords': keywords,
            'word_count': len(words),
            'processed_at': datetime.now().isoformat(),
        }

    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities (emails, phone numbers, dates, monetary values)."""
        entities = []

        # Email addresses
        for match in re.finditer(r'[\w.+-]+@[\w-]+\.[\w.-]+', text):
            entities.append({'type': 'EMAIL', 'value': match.group(), 'start': match.start()})

        # Phone numbers
        for match in re.finditer(r'[\+]?[\d\s\-\(\)]{10,}', text):
            entities.append({'type': 'PHONE', 'value': match.group().strip(), 'start': match.start()})

        # Monetary values
        for match in re.finditer(r'[\$€£₹]\s?[\d,]+(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|PKR)', text):
            entities.append({'type': 'MONEY', 'value': match.group(), 'start': match.start()})

        # Dates (basic patterns)
        for match in re.finditer(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}', text):
            entities.append({'type': 'DATE', 'value': match.group(), 'start': match.start()})

        return entities

    def _analyze_sentiment(self, words: List[str]) -> Dict[str, Any]:
        """Simple keyword-based sentiment scoring."""
        pos = sum(1 for w in words if w in self._positive)
        neg = sum(1 for w in words if w in self._negative)
        total = pos + neg

        if total == 0:
            return {'label': 'neutral', 'score': 0.0, 'positive': 0, 'negative': 0}

        score = (pos - neg) / total
        label = 'positive' if score > 0.2 else ('negative' if score < -0.2 else 'neutral')

        return {'label': label, 'score': round(score, 3), 'positive': pos, 'negative': neg}

    def _classify_intent(self, words: List[str]) -> Dict[str, Any]:
        """Classify the primary intent of the text."""
        scores = {}
        for intent, keywords in self._intent_patterns.items():
            score = sum(1 for w in words if w in keywords)
            if score > 0:
                scores[intent] = score

        if not scores:
            return {'intent': 'general', 'confidence': 0.3, 'all_intents': {}}

        best = max(scores, key=scores.get)
        total = sum(scores.values())

        return {
            'intent': best,
            'confidence': round(scores[best] / max(total, 1), 3),
            'all_intents': scores,
        }

    def _extract_keywords(self, words: List[str], top_k: int = 10) -> List[str]:
        """Extract top keywords by frequency, excluding stop words."""
        stop = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'to', 'of',
                'and', 'or', 'in', 'on', 'at', 'for', 'with', 'this', 'that', 'it', 'from'}
        freq: Dict[str, int] = {}
        for w in words:
            if len(w) > 2 and w not in stop:
                freq[w] = freq.get(w, 0) + 1
        return sorted(freq, key=freq.get, reverse=True)[:top_k]

    def _empty_result(self) -> Dict[str, Any]:
        return {'entities': [], 'sentiment': {'label': 'neutral', 'score': 0.0},
                'intent': {'intent': 'unknown', 'confidence': 0.0}, 'keywords': [], 'word_count': 0}
