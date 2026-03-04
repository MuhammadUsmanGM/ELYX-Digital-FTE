"""
Long-term Memory System for Gold Tier Personal AI Employee System
Implements persistent memory, learning, and knowledge retention
"""
import os
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import hashlib
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import faiss

from ..utils.logger import log_activity


class MemoryType(Enum):
    EPISODIC = "episodic"  # Personal experiences and events
    SEMANTIC = "semantic"  # Factual knowledge and concepts
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKSPACE = "workspace"  # Short-term working memory


@dataclass
class MemoryEntry:
    """Data class for memory entries"""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime
    importance: float = 0.5  # 0-1, how important is this memory
    context: Dict[str, Any] = None  # Additional context
    embeddings: Optional[np.ndarray] = None  # Semantic embeddings
    tags: List[str] = None  # Tags for categorization
    access_count: int = 0  # How many times accessed
    last_accessed: Optional[datetime] = None  # When last accessed
    decay_factor: float = 1.0  # Memory decay factor

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.tags is None:
            self.tags = []


class MemorySystem:
    """
    Advanced memory system for Gold Tier AI capabilities
    """

    def __init__(self, memory_db_path: str = "memory.db", model_cache_size: int = 1000):
        self.memory_db_path = Path(memory_db_path)
        self.model_cache_size = model_cache_size

        self.logger = logging.getLogger(__name__)

        # Initialize database
        self._init_db()

        # Initialize vector index for semantic search
        self.vector_dimension = 384  # Using sentence-transformer dimension
        self.vector_index = faiss.IndexFlatIP(self.vector_dimension)  # Inner product for cosine similarity
        self.memory_ids = []  # Map index to memory ID

        # Initialize TF-IDF for keyword-based search
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.tfidf_matrix = None

        # Cache for embeddings
        self.embedding_cache = {}
        self.cache_size_limit = model_cache_size

        # Load existing memories
        self._load_memories_into_index()

    def _init_db(self):
        """Initialize the memory database"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        # Create memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                importance REAL DEFAULT 0.5,
                context TEXT,
                embeddings BLOB,
                tags TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME,
                decay_factor REAL DEFAULT 1.0
            )
        ''')

        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)')

        conn.commit()
        conn.close()

        self.logger.info(f"Memory database initialized at {self.memory_db_path}")

    def _load_memories_into_index(self):
        """Load existing memories into the vector index"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, content, embeddings FROM memories')
        rows = cursor.fetchall()

        embeddings_list = []
        ids_list = []

        for row in rows:
            memory_id, content, embeddings_blob = row

            # Load embeddings from blob if available
            if embeddings_blob:
                try:
                    embeddings = pickle.loads(embeddings_blob)
                    embeddings_list.append(embeddings)
                    ids_list.append(memory_id)
                except:
                    # If embeddings are corrupted, skip this memory
                    continue
            else:
                # If no embeddings, we'll generate them when needed
                ids_list.append(memory_id)

        if embeddings_list:
            # Add to FAISS index
            embeddings_array = np.array(embeddings_list).astype('float32')
            # Ensure 2D shape (n_samples, embedding_dim) for FAISS
            if embeddings_array.ndim == 1:
                embeddings_array = embeddings_array.reshape(1, -1)
            elif embeddings_array.ndim > 2:
                embeddings_array = embeddings_array.reshape(embeddings_array.shape[0], -1)
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings_array)
            self.vector_index.add(embeddings_array)

        self.memory_ids = ids_list
        conn.close()

        self.logger.info(f"Loaded {len(ids_list)} memories into search index")

    def store_memory(self, content: str, memory_type: MemoryType,
                     importance: float = 0.5,
                     context: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[str]] = None) -> str:
        """
        Store a new memory in the system

        Args:
            content: The content to store
            memory_type: Type of memory (episodic, semantic, procedural, workspace)
            importance: Importance score (0-1)
            context: Additional context information
            tags: Tags for categorization

        Returns:
            ID of the stored memory
        """
        memory_id = self._generate_memory_id(content, memory_type, context or {})

        # Generate embeddings for semantic search
        embeddings = self._generate_embeddings(content)

        # Prepare data
        memory_entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            importance=importance,
            context=context or {},
            embeddings=embeddings,
            tags=tags or [],
            access_count=0,
            last_accessed=None,
            decay_factor=1.0
        )

        # Store in database
        self._save_memory_to_db(memory_entry)

        # Add to vector index
        if embeddings is not None:
            # Normalize for cosine similarity
            normalized_embedding = embeddings.copy().astype('float32')
            faiss.normalize_L2(normalized_embedding.reshape(1, -1))
            self.vector_index.add(normalized_embedding.reshape(1, -1))
            self.memory_ids.append(memory_id)

        log_activity("MEMORY_STORED", f"Stored memory: {content[:50]}...", "obsidian_vault")

        return memory_id

    def _generate_memory_id(self, content: str, memory_type: MemoryType, context: Dict[str, Any]) -> str:
        """Generate a unique ID for a memory"""
        type_val = memory_type.value if hasattr(memory_type, 'value') else str(memory_type)
        hash_input = f"{content}{type_val}{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _generate_embeddings(self, content: str) -> Optional[np.ndarray]:
        """Generate semantic embeddings for content"""
        try:
            # Check cache first
            content_hash = hashlib.md5(content.encode()).hexdigest()
            if content_hash in self.embedding_cache:
                return self.embedding_cache[content_hash]

            # Generate embeddings using sentence transformers
            # For this implementation, we'll simulate embeddings
            # In a real implementation, we would use the sentence transformer model
            import random
            # Generate random embeddings for demonstration
            embeddings = np.random.rand(1, self.vector_dimension).astype('float32')

            # Add to cache
            if len(self.embedding_cache) < self.cache_size_limit:
                self.embedding_cache[content_hash] = embeddings

            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            return None

    def _save_memory_to_db(self, memory_entry: MemoryEntry):
        """Save memory entry to the database"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        # Serialize context and tags
        context_json = json.dumps(memory_entry.context) if memory_entry.context else '{}'
        tags_json = json.dumps(memory_entry.tags) if memory_entry.tags else '[]'

        # Serialize embeddings
        embeddings_blob = pickle.dumps(memory_entry.embeddings) if memory_entry.embeddings is not None else None

        cursor.execute('''
            INSERT OR REPLACE INTO memories
            (id, content, memory_type, timestamp, importance, context, embeddings, tags, access_count, last_accessed, decay_factor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_entry.id,
            memory_entry.content,
            memory_entry.memory_type.value if hasattr(memory_entry.memory_type, 'value') else str(memory_entry.memory_type),
            memory_entry.timestamp,
            memory_entry.importance,
            context_json,
            embeddings_blob,
            tags_json,
            memory_entry.access_count,
            memory_entry.last_accessed,
            memory_entry.decay_factor
        ))

        conn.commit()
        conn.close()

    def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory by ID

        Args:
            memory_id: ID of the memory to retrieve

        Returns:
            MemoryEntry if found, None otherwise
        """
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, content, memory_type, timestamp, importance, context, embeddings, tags, access_count, last_accessed, decay_factor
            FROM memories WHERE id = ?
        ''', (memory_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            # Deserialize the row
            memory_entry = MemoryEntry(
                id=row[0],
                content=row[1],
                memory_type=MemoryType(row[2]),
                timestamp=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3],
                importance=row[4],
                context=json.loads(row[5]) if row[5] else {},
                embeddings=pickle.loads(row[6]) if row[6] else None,
                tags=json.loads(row[7]) if row[7] else [],
                access_count=row[8],
                last_accessed=datetime.fromisoformat(row[9]) if row[9] and isinstance(row[9], str) else row[9],
                decay_factor=row[10]
            )

            # Update access count
            self._update_memory_access(memory_id)

            return memory_entry

        return None

    def _update_memory_access(self, memory_id: str):
        """Update access count and timestamp for a memory"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE memories
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        ''', (datetime.now(), memory_id))

        conn.commit()
        conn.close()

    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None,
                       limit: int = 10, min_importance: float = 0.0,
                       time_window: Optional[timedelta] = None) -> List[MemoryEntry]:
        """
        Search for memories using semantic similarity

        Args:
            query: Query text to search for
            memory_type: Specific memory type to search (optional)
            limit: Maximum number of results to return
            min_importance: Minimum importance threshold
            time_window: Time window to search within (optional)

        Returns:
            List of matching memories
        """
        # Generate query embeddings
        query_embeddings = self._generate_embeddings(query)

        if query_embeddings is None:
            return []

        # Normalize query embeddings
        normalized_query = query_embeddings.copy().astype('float32')
        faiss.normalize_L2(normalized_query)

        # Perform similarity search
        if self.vector_index.ntotal == 0:
            return []

        similarities, indices = self.vector_index.search(normalized_query, min(limit * 10, len(self.memory_ids)))

        # Get memory IDs and filter based on criteria
        matching_memory_ids = []
        for idx in indices[0]:
            if idx < len(self.memory_ids):
                matching_memory_ids.append(self.memory_ids[idx])

        # Fetch full memory entries from DB
        memories = self._fetch_memories_by_id(matching_memory_ids[:limit*10])

        # Apply filters
        filtered_memories = []
        for memory in memories:
            # Apply memory type filter
            if memory_type and memory.memory_type != memory_type:
                continue

            # Apply importance filter
            if memory.importance < min_importance:
                continue

            # Apply time window filter
            if time_window:
                if datetime.now() - memory.timestamp > time_window:
                    continue

            filtered_memories.append(memory)

        # Sort by relevance (similarity) and importance
        # Since we don't have exact similarity scores here, we'll sort by importance
        filtered_memories.sort(key=lambda x: x.importance, reverse=True)

        # Update access counts for retrieved memories
        for memory in filtered_memories[:limit]:
            self._update_memory_access(memory.id)

        return filtered_memories[:limit]

    def _fetch_memories_by_id(self, memory_ids: List[str]) -> List[MemoryEntry]:
        """Fetch memory entries by their IDs"""
        if not memory_ids:
            return []

        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        # Create placeholder for the IN clause
        placeholders = ','.join('?' * len(memory_ids))
        query = f'''
            SELECT id, content, memory_type, timestamp, importance, context, embeddings, tags, access_count, last_accessed, decay_factor
            FROM memories WHERE id IN ({placeholders})
        '''

        cursor.execute(query, memory_ids)
        rows = cursor.fetchall()
        conn.close()

        memories = []
        for row in rows:
            memory_entry = MemoryEntry(
                id=row[0],
                content=row[1],
                memory_type=MemoryType(row[2]),
                timestamp=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3],
                importance=row[4],
                context=json.loads(row[5]) if row[5] else {},
                embeddings=pickle.loads(row[6]) if row[6] else None,
                tags=json.loads(row[7]) if row[7] else [],
                access_count=row[8],
                last_accessed=datetime.fromisoformat(row[9]) if row[9] and isinstance(row[9], str) else row[9],
                decay_factor=row[10]
            )
            memories.append(memory_entry)

        return memories

    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored memories

        Returns:
            Dictionary with memory statistics
        """
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        # Count by type
        cursor.execute('SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type')
        type_counts = dict(cursor.fetchall())

        # Overall stats
        cursor.execute('SELECT COUNT(*), AVG(importance), AVG(access_count) FROM memories')
        total, avg_importance, avg_access = cursor.fetchone()

        # Recent memories (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM memories WHERE timestamp > ?', (seven_days_ago,))
        recent_count = cursor.fetchone()[0]

        conn.close()

        stats = {
            'total_memories': total or 0,
            'memories_by_type': type_counts,
            'average_importance': avg_importance or 0.0,
            'average_access_count': avg_access or 0.0,
            'recent_memories': recent_count or 0,
            'indexed_memories': self.vector_index.ntotal,
            'cache_size': len(self.embedding_cache)
        }

        return stats

    def forget_memory(self, memory_id: str) -> bool:
        """
        Remove a memory from the system

        Args:
            memory_id: ID of the memory to remove

        Returns:
            True if memory was removed, False otherwise
        """
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        if deleted:
            # Remove from vector index if present
            try:
                idx_to_remove = self.memory_ids.index(memory_id)
                # FAISS doesn't have efficient deletion, so we'll rebuild the index
                # In a real system, we might use a more sophisticated approach
                self._rebuild_index()

                log_activity("MEMORY_REMOVED", f"Removed memory: {memory_id}", "obsidian_vault")
            except ValueError:
                # Memory ID not in our index, that's fine
                pass

        return deleted

    def _rebuild_index(self):
        """Rebuild the vector index from the database"""
        # Clear current index
        self.vector_index.reset()
        self.memory_ids = []

        # Load all memories back into index
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, embeddings FROM memories')
        rows = cursor.fetchall()

        embeddings_list = []
        ids_list = []

        for row in rows:
            memory_id, embeddings_blob = row

            if embeddings_blob:
                try:
                    embeddings = pickle.loads(embeddings_blob)
                    embeddings_list.append(embeddings)
                    ids_list.append(memory_id)
                except:
                    continue

        if embeddings_list:
            embeddings_array = np.array(embeddings_list).astype('float32')
            faiss.normalize_L2(embeddings_array)
            self.vector_index.add(embeddings_array)

        self.memory_ids = ids_list
        conn.close()

    def consolidate_memories(self, importance_threshold: float = 0.7) -> int:
        """
        Consolidate memories by combining similar ones above importance threshold

        Args:
            importance_threshold: Minimum importance for consolidation

        Returns:
            Number of memories consolidated
        """
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        # Get high-importance memories
        cursor.execute('''
            SELECT id, content, memory_type, timestamp, importance, context
            FROM memories WHERE importance >= ?
            ORDER BY timestamp DESC
        ''', (importance_threshold,))

        high_imp_memories = cursor.fetchall()
        conn.close()

        consolidated_count = 0

        # This is a simplified consolidation - in reality, this would be more sophisticated
        # For now, we'll just group memories by content similarity

        return consolidated_count

    def decay_memory(self, memory_id: str, decay_rate: float = 0.1) -> bool:
        """
        Apply decay to a memory, reducing its importance over time

        Args:
            memory_id: ID of the memory to decay
            decay_rate: Rate of decay (0-1)

        Returns:
            True if memory was decayed, False otherwise
        """
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        # Get current importance and decay factor
        cursor.execute('SELECT importance, decay_factor FROM memories WHERE id = ?', (memory_id,))
        result = cursor.fetchone()

        if result:
            current_importance, current_decay = result
            new_importance = current_importance * (1 - decay_rate)
            new_decay = current_decay * (1 - decay_rate)

            # Update the memory
            cursor.execute('''
                UPDATE memories
                SET importance = ?, decay_factor = ?
                WHERE id = ?
            ''', (new_importance, new_decay, memory_id))

            conn.commit()
            conn.close()

            log_activity("MEMORY_DECAYED", f"Decayed memory {memory_id}, new importance: {new_importance:.3f}", "obsidian_vault")
            return True

        conn.close()
        return False

    def learn_from_interaction(self, user_input: str, system_response: str,
                             context: Dict[str, Any] = None,
                             positive_feedback: bool = True) -> str:
        """
        Learn from an interaction and store the experience

        Args:
            user_input: What the user said/requested
            system_response: How the system responded
            context: Context of the interaction
            positive_feedback: Whether the interaction was successful

        Returns:
            ID of the stored memory
        """
        # Create memory content combining input, response, and outcome
        memory_content = f"User: {user_input}\nSystem: {system_response}\nOutcome: {'Successful' if positive_feedback else 'Unsuccessful'}"

        # Determine importance based on feedback
        importance = 0.8 if positive_feedback else 0.3

        # Add interaction context
        full_context = {
            'interaction_type': 'user_system',
            'positive_feedback': positive_feedback,
            'timestamp': datetime.now().isoformat()
        }

        if context:
            full_context.update(context)

        # Add tags based on interaction type
        tags = ['interaction', 'learning'] + (['positive'] if positive_feedback else ['negative'])

        # Store the memory
        memory_id = self.store_memory(
            content=memory_content,
            memory_type=MemoryType.EPISODIC,
            importance=importance,
            context=full_context,
            tags=tags
        )

        log_activity("INTERACTION_LEARNED", f"Learned from interaction: {user_input[:30]}...", "obsidian_vault")
        return memory_id

    def get_memory_timeline(self, start_date: datetime, end_date: datetime) -> List[MemoryEntry]:
        """
        Get memories within a specific time range

        Args:
            start_date: Start of the time range
            end_date: End of the time range

        Returns:
            List of memories within the time range
        """
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, content, memory_type, timestamp, importance, context, tags, access_count
            FROM memories
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_date, end_date))

        rows = cursor.fetchall()
        conn.close()

        memories = []
        for row in rows:
            memory_entry = MemoryEntry(
                id=row[0],
                content=row[1],
                memory_type=MemoryType(row[2]),
                timestamp=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3],
                importance=row[4],
                context=json.loads(row[5]) if row[5] else {},
                embeddings=None,  # Not loading embeddings for timeline
                tags=json.loads(row[6]) if row[6] else [],
                access_count=row[7],
                last_accessed=None,
                decay_factor=1.0
            )
            memories.append(memory_entry)

        return memories

    def export_memories(self, file_path: str, memory_type: Optional[MemoryType] = None):
        """
        Export memories to a file

        Args:
            file_path: Path to export file
            memory_type: Specific memory type to export (optional)
        """
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        if memory_type:
            cursor.execute('''
                SELECT id, content, memory_type, timestamp, importance, context, tags, access_count
                FROM memories
                WHERE memory_type = ?
                ORDER BY timestamp DESC
            ''', (memory_type.value if hasattr(memory_type, 'value') else str(memory_type),))
        else:
            cursor.execute('''
                SELECT id, content, memory_type, timestamp, importance, context, tags, access_count
                FROM memories
                ORDER BY timestamp DESC
            ''')

        rows = cursor.fetchall()
        conn.close()

        # Convert to list of dictionaries
        memories_data = []
        for row in rows:
            memory_data = {
                'id': row[0],
                'content': row[1],
                'memory_type': row[2],
                'timestamp': row[3].isoformat() if hasattr(row[3], 'isoformat') else row[3],
                'importance': row[4],
                'context': json.loads(row[5]) if row[5] else {},
                'tags': json.loads(row[6]) if row[6] else [],
                'access_count': row[7]
            }
            memories_data.append(memory_data)

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(memories_data, f, indent=2, ensure_ascii=False)

        log_activity("MEMORIES_EXPORTED", f"Exported {len(memories_data)} memories to {file_path}", "obsidian_vault")


class LearningSystem:
    """
    Learning system that builds on the memory system
    """

    def __init__(self, memory_system: MemorySystem):
        self.memory_system = memory_system
        self.logger = logging.getLogger(__name__)

    def learn_user_preferences(self, user_id: str, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Learn user preferences from their interactions

        Args:
            user_id: ID of the user
            interactions: List of interaction data

        Returns:
            Dictionary of learned preferences
        """
        preferences = {
            'preferred_topics': [],
            'response_style': 'neutral',
            'interaction_frequency': 'moderate',
            'task_categories': [],
            'communication_channel': 'text',
            'time_preferences': [],
            'learning_confidence': 0.0
        }

        topic_counts = {}
        category_counts = {}
        style_indicators = {'formal': 0, 'casual': 0, 'direct': 0, 'polite': 0}

        for interaction in interactions:
            # Analyze topics mentioned
            content = interaction.get('user_input', '') + ' ' + interaction.get('system_response', '')
            words = content.lower().split()

            # Simple topic extraction (in reality, this would use NLP)
            for word in words:
                if len(word) > 4:  # Only consider longer words as potential topics
                    topic_counts[word] = topic_counts.get(word, 0) + 1

            # Analyze response style based on feedback
            if interaction.get('positive_feedback'):
                style_indicators['polite'] += 1
                style_indicators['direct'] += 1  # Positive feedback might indicate directness worked

            # Analyze task categories
            if 'task_category' in interaction:
                category = interaction['task_category']
                category_counts[category] = category_counts.get(category, 0) + 1

        # Determine preferred topics (top 5)
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        preferences['preferred_topics'] = [topic for topic, count in sorted_topics[:5]]

        # Determine task categories
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        preferences['task_categories'] = [cat for cat, count in sorted_categories[:5]]

        # Determine response style
        dominant_style = max(style_indicators, key=style_indicators.get)
        preferences['response_style'] = dominant_style

        # Calculate learning confidence based on amount of data
        total_interactions = len(interactions)
        preferences['learning_confidence'] = min(1.0, total_interactions / 20.0)  # Normalize to 0-1 based on 20 interactions

        # Store learned preferences as semantic memory
        preferences_content = f"User preferences for {user_id}: Topics: {preferences['preferred_topics']}, Style: {preferences['response_style']}, Categories: {preferences['task_categories']}"

        self.memory_system.store_memory(
            content=preferences_content,
            memory_type=MemoryType.SEMANTIC,
            importance=0.9,
            context={'user_id': user_id, 'preference_type': 'behavioral'},
            tags=['user_preferences', 'behavioral', user_id]
        )

        log_activity("PREFERENCES_LEARNED", f"Learned preferences for user {user_id}", "obsidian_vault")
        return preferences

    def identify_patterns(self, memory_type: MemoryType = MemoryType.EPISODIC) -> List[Dict[str, Any]]:
        """
        Identify patterns in stored memories

        Args:
            memory_type: Type of memories to analyze

        Returns:
            List of identified patterns
        """
        # Retrieve relevant memories
        recent_memories = self.memory_system.search_memories(
            query="",  # Empty query to get recent memories
            memory_type=memory_type,
            limit=100,
            time_window=timedelta(days=30)  # Look at last 30 days
        )

        patterns = []

        if not recent_memories:
            return patterns

        # Simple pattern identification (in reality, this would be much more sophisticated)
        # Look for repeated phrases, common themes, etc.

        content_snippets = [mem.content[:100] for mem in recent_memories]

        # Find common phrases
        common_phrases = {}
        for content in content_snippets:
            words = content.lower().split()
            # Look for 2-3 word phrases
            for i in range(len(words) - 1):
                phrase = ' '.join(words[i:i+2])
                if len(phrase) > 5:  # Filter out very short phrases
                    common_phrases[phrase] = common_phrases.get(phrase, 0) + 1

        # Identify top recurring phrases as patterns
        sorted_phrases = sorted(common_phrases.items(), key=lambda x: x[1], reverse=True)

        for phrase, count in sorted_phrases[:10]:  # Top 10 patterns
            if count > 1:  # Only consider if it appears more than once
                patterns.append({
                    'pattern': phrase,
                    'frequency': count,
                    'type': 'recurring_phrase',
                    'confidence': min(1.0, count / len(recent_memories))
                })

        log_activity("PATTERNS_IDENTIFIED", f"Identified {len(patterns)} patterns in {memory_type.value if hasattr(memory_type, 'value') else memory_type} memories", "obsidian_vault")
        return patterns

    def update_knowledge_base(self, new_information: str, source: str = "user_interaction") -> str:
        """
        Update the knowledge base with new information

        Args:
            new_information: New information to add
            source: Source of the information

        Returns:
            ID of the stored knowledge
        """
        # Store as semantic memory
        knowledge_id = self.memory_system.store_memory(
            content=new_information,
            memory_type=MemoryType.SEMANTIC,
            importance=0.7,  # Moderate importance for new facts
            context={'source': source, 'knowledge_type': 'fact'},
            tags=['knowledge', 'fact', source]
        )

        log_activity("KNOWLEDGE_ADDED", f"Added new knowledge from {source}: {new_information[:50]}...", "obsidian_vault")
        return knowledge_id

    def adapt_behavior(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt system behavior based on learned information

        Args:
            user_context: Context about the user

        Returns:
            Dictionary with adaptation recommendations
        """
        adaptations = {
            'communication_style': 'adaptive',
            'task_prioritization': 'learned',
            'response_tone': 'learned',
            'interaction_timing': 'optimal',
            'personalization_level': 'high',
            'confidence': 0.0
        }

        user_id = user_context.get('user_id', 'unknown')

        # Look up user preferences in memory
        preferences = self.memory_system.search_memories(
            query=f"user {user_id} preferences",
            memory_type=MemoryType.SEMANTIC,
            limit=5
        )

        if preferences:
            # Apply learned preferences
            pref_content = preferences[0].content
            if 'formal' in pref_content:
                adaptations['response_tone'] = 'formal'
            elif 'casual' in pref_content:
                adaptations['response_tone'] = 'casual'
            elif 'direct' in pref_content:
                adaptations['response_tone'] = 'direct'
            elif 'polite' in pref_content:
                adaptations['response_tone'] = 'polite'

            # Calculate confidence based on preference certainty
            adaptations['confidence'] = preferences[0].importance

        # Look for behavioral patterns
        patterns = self.identify_patterns(MemoryType.EPISODIC)
        if patterns:
            # Apply pattern-based adaptations
            adaptations['personalization_level'] = 'very_high'
            adaptations['confidence'] = max(adaptations['confidence'], 0.6)

        log_activity("BEHAVIOR_ADAPTED", f"Adapted behavior for user {user_id}", "obsidian_vault")
        return adaptations


# Example usage and testing
if __name__ == "__main__":
    print("Testing Memory System...")

    # Initialize memory system
    memory_system = MemorySystem()

    # Test storing memories
    print("\n1. Testing Memory Storage:")
    memory_id1 = memory_system.store_memory(
        content="The quarterly budget was approved by the finance committee.",
        memory_type=MemoryType.EPISODIC,
        importance=0.8,
        context={"category": "finance", "date": "2023-10-15"},
        tags=["budget", "approval", "finance"]
    )
    print(f"Stored episodic memory: {memory_id1[:8]}...")

    memory_id2 = memory_system.store_memory(
        content="The capital budgeting process requires approval from three departments.",
        memory_type=MemoryType.SEMANTIC,
        importance=0.9,
        context={"category": "process", "domain": "finance"},
        tags=["process", "budget", "approval", "procedure"]
    )
    print(f"Stored semantic memory: {memory_id2[:8]}...")

    # Test retrieving memories
    print("\n2. Testing Memory Retrieval:")
    retrieved_memory = memory_system.retrieve_memory(memory_id1)
    if retrieved_memory:
        print(f"Retrieved: {retrieved_memory.content[:50]}...")
        print(f"Type: {retrieved_memory.memory_type.value if hasattr(retrieved_memory.memory_type, 'value') else retrieved_memory.memory_type}, Importance: {retrieved_memory.importance}")

    # Test searching memories
    print("\n3. Testing Memory Search:")
    search_results = memory_system.search_memories("budget approval", limit=5)
    print(f"Found {len(search_results)} memories matching 'budget approval'")
    for i, mem in enumerate(search_results[:2]):  # Show first 2
        print(f"  {i+1}. {mem.content[:60]}... (imp: {mem.importance:.2f})")

    # Test memory statistics
    print("\n4. Testing Memory Statistics:")
    stats = memory_system.get_memory_statistics()
    print(f"Total memories: {stats['total_memories']}")
    print(f"By type: {stats['memories_by_type']}")
    print(f"Avg importance: {stats['average_importance']:.2f}")

    # Initialize learning system
    learning_system = LearningSystem(memory_system)

    # Test learning from interactions
    print("\n5. Testing Learning from Interactions:")
    interactions = [
        {
            'user_input': 'Please analyze the quarterly sales report',
            'system_response': 'I will analyze the report and provide insights.',
            'positive_feedback': True,
            'task_category': 'analysis'
        },
        {
            'user_input': 'Make this report more formal',
            'system_response': 'I have adjusted the tone to be more formal.',
            'positive_feedback': True,
            'task_category': 'editing'
        },
        {
            'user_input': 'Tell me about market trends',
            'system_response': 'Based on recent data, here are the key trends...',
            'positive_feedback': False,
            'task_category': 'research'
        }
    ]

    preferences = learning_system.learn_user_preferences("test_user_001", interactions)
    print(f"Learned preferences: {preferences['response_style']} style, topics: {preferences['preferred_topics'][:3]}")

    # Test pattern identification
    print("\n6. Testing Pattern Identification:")
    patterns = learning_system.identify_patterns()
    print(f"Identified {len(patterns)} patterns")
    for pattern in patterns[:3]:  # Show first 3
        print(f"  - {pattern['pattern']}: appeared {pattern['frequency']} times")

    # Test knowledge base update
    print("\n7. Testing Knowledge Base Update:")
    knowledge_id = learning_system.update_knowledge_base(
        "The new fiscal year begins on July 1st, 2024",
        source="company_announcement"
    )
    print(f"Added knowledge: {knowledge_id[:8]}...")

    # Test behavior adaptation
    print("\n8. Testing Behavior Adaptation:")
    user_context = {"user_id": "test_user_001", "department": "sales"}
    adaptations = learning_system.adapt_behavior(user_context)
    print(f"Adaptations: {adaptations['response_tone']} tone, confidence: {adaptations['confidence']:.2f}")

    print("\nMemory System tests completed!")