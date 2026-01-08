"""
Local RAG Engine - No external API dependencies
Uses TF-IDF and cosine similarity for document retrieval
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter
import math


class LocalRAGEngine:
    """
    Local Retrieval-Augmented Generation Engine
    Uses TF-IDF for semantic search without external APIs
    """
    
    def __init__(self, kb_dir: Path = None):
        """
        Initialize local RAG engine
        
        Args:
            kb_dir: Knowledge base directory (default: .kb_local/)
        """
        self.kb_dir = kb_dir or Path(".kb_local")
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.kb_dir / "index.json"
        self.tfidf_file = self.kb_dir / "tfidf.json"
        
        self.chunks: List[Dict[str, Any]] = []
        self.tfidf_vectors: List[Dict[str, float]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        
        # Load existing index if available
        if self.index_file.exists():
            self._load_index()
    
    def build(self, docs_dir: Path) -> None:
        """
        Build knowledge base from documentation directory
        
        Args:
            docs_dir: Directory containing documentation files
        """
        print(f"Building local knowledge base from {docs_dir}...")
        
        # Clear existing data
        self.chunks = []
        self.tfidf_vectors = []
        self.vocabulary = {}
        self.idf = {}
        
        # Find all markdown and text files
        doc_files = list(docs_dir.rglob("*.md")) + list(docs_dir.rglob("*.txt"))
        doc_files += list(docs_dir.glob("*.md"))  # Include root level
        
        # Also include key JavaScript files
        js_files = list(docs_dir.rglob("*.js"))
        doc_files += js_files
        
        print(f"Found {len(doc_files)} documentation files")
        
        # Process each file
        for doc_file in doc_files:
            self._process_file(doc_file, docs_dir)
        
        print(f"Extracted {len(self.chunks)} chunks")
        
        # Build TF-IDF index
        print("Building TF-IDF index...")
        self._build_tfidf()
        
        # Save index
        self._save_index()
        
        print(f"Knowledge base built successfully: {len(self.chunks)} chunks indexed")
    
    def _process_file(self, file_path: Path, base_dir: Path) -> None:
        """Process a single documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get relative path for reference
            rel_path = file_path.relative_to(base_dir.parent)
            
            # Split into chunks based on file type
            if file_path.suffix == '.md':
                chunks = self._chunk_markdown(content, str(rel_path))
            elif file_path.suffix == '.js':
                chunks = self._chunk_code(content, str(rel_path))
            else:
                chunks = self._chunk_text(content, str(rel_path))
            
            self.chunks.extend(chunks)
            
        except Exception as e:
            print(f"Warning: Failed to process {file_path}: {e}")
    
    def _chunk_markdown(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Split markdown into chunks by sections"""
        chunks = []
        
        # Split by headers
        sections = re.split(r'\n(?=#{1,3} )', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            # Extract section title
            title_match = re.match(r'^#{1,3} (.+)', section)
            section_title = title_match.group(1) if title_match else "Introduction"
            
            # Create chunk
            chunk = {
                "file": file_path,
                "section": section_title,
                "content": section.strip(),
                "type": "markdown"
            }
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_code(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Chunk code files (keep as single chunk with metadata)"""
        # Extract function/service names for better retrieval
        functions = re.findall(r'function\s+(\w+)|Service:\s*(\w+)', content)
        function_names = [f[0] or f[1] for f in functions]
        
        chunk = {
            "file": file_path,
            "section": "Code",
            "content": content.strip(),
            "type": "code",
            "functions": function_names
        }
        
        return [chunk]
    
    def _chunk_text(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Chunk plain text by paragraphs"""
        chunks = []
        
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        
        for idx, para in enumerate(paragraphs):
            if not para.strip():
                continue
            
            chunk = {
                "file": file_path,
                "section": f"Section {idx + 1}",
                "content": para.strip(),
                "type": "text"
            }
            chunks.append(chunk)
        
        return chunks
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def _build_tfidf(self) -> None:
        """Build TF-IDF index for all chunks"""
        # Build vocabulary and document frequency
        doc_freq = Counter()
        all_tokens = []
        
        for chunk in self.chunks:
            text = f"{chunk['file']} {chunk['section']} {chunk['content']}"
            tokens = self._tokenize(text)
            all_tokens.append(tokens)
            
            # Count unique tokens for IDF
            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freq[token] += 1
        
        # Build vocabulary
        self.vocabulary = {token: idx for idx, token in enumerate(doc_freq.keys())}
        
        # Calculate IDF
        num_docs = len(self.chunks)
        self.idf = {
            token: math.log(num_docs / (freq + 1))
            for token, freq in doc_freq.items()
        }
        
        # Calculate TF-IDF vectors
        self.tfidf_vectors = []
        
        for tokens in all_tokens:
            # Calculate term frequency
            tf = Counter(tokens)
            total_terms = len(tokens)
            
            # Calculate TF-IDF vector
            tfidf_vector = {}
            for token, count in tf.items():
                tf_score = count / total_terms
                idf_score = self.idf.get(token, 0)
                tfidf_vector[token] = tf_score * idf_score
            
            self.tfidf_vectors.append(tfidf_vector)
    
    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the knowledge base
        
        Args:
            query_text: Query string
            top_k: Number of top results to return
            
        Returns:
            List of relevant chunks with relevance scores
        """
        if not self.chunks:
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query_text)
        
        # Calculate query TF-IDF
        tf = Counter(query_tokens)
        total_terms = len(query_tokens)
        
        query_vector = {}
        for token, count in tf.items():
            if token in self.vocabulary:
                tf_score = count / total_terms
                idf_score = self.idf.get(token, 0)
                query_vector[token] = tf_score * idf_score
        
        # Compute cosine similarity with all chunks
        similarities = []
        for idx, doc_vector in enumerate(self.tfidf_vectors):
            similarity = self._cosine_similarity(query_vector, doc_vector)
            similarities.append((idx, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top K results
        results = []
        for idx, score in similarities[:top_k]:
            if score > 0:  # Only return results with some similarity
                result = self.chunks[idx].copy()
                result["relevance"] = score
                results.append(result)
        
        return results
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between two sparse vectors"""
        # Compute dot product
        dot_product = 0.0
        for token in vec1:
            if token in vec2:
                dot_product += vec1[token] * vec2[token]
        
        # Compute norms
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_context(self, query_text: str, max_tokens: int = 2000) -> Tuple[str, List[Dict]]:
        """
        Get context string for RAG injection
        
        Args:
            query_text: Query string
            max_tokens: Maximum tokens for context (approximate)
            
        Returns:
            Tuple of (context_string, sources_list)
        """
        results = self.query(query_text, top_k=5)
        
        context_parts = []
        sources = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough approximation
        
        for result in results:
            chunk_text = f"[{result['file']} - {result['section']}]\n{result['content']}\n"
            
            if total_chars + len(chunk_text) > max_chars:
                break
            
            context_parts.append(chunk_text)
            total_chars += len(chunk_text)
            
            sources.append({
                "file": result["file"],
                "section": result["section"],
                "relevance": result["relevance"]
            })
        
        context_string = "\n---\n".join(context_parts)
        return context_string, sources
    
    def _save_index(self) -> None:
        """Save index to disk"""
        # Save chunks
        with open(self.index_file, 'w') as f:
            json.dump(self.chunks, f, indent=2)
        
        # Save TF-IDF data
        tfidf_data = {
            "vocabulary": self.vocabulary,
            "idf": self.idf,
            "vectors": self.tfidf_vectors
        }
        with open(self.tfidf_file, 'w') as f:
            json.dump(tfidf_data, f)
        
        print(f"Index saved to {self.kb_dir}")
    
    def _load_index(self) -> None:
        """Load index from disk"""
        try:
            with open(self.index_file, 'r') as f:
                self.chunks = json.load(f)
            
            with open(self.tfidf_file, 'r') as f:
                tfidf_data = json.load(f)
                self.vocabulary = tfidf_data["vocabulary"]
                self.idf = tfidf_data["idf"]
                self.tfidf_vectors = tfidf_data["vectors"]
            
            print(f"Loaded index: {len(self.chunks)} chunks")
        except Exception as e:
            print(f"Warning: Failed to load index: {e}")
            self.chunks = []
            self.tfidf_vectors = []
            self.vocabulary = {}
            self.idf = {}
    
    def stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        if not self.chunks:
            return {"status": "empty"}
        
        files = set(chunk["file"] for chunk in self.chunks)
        types = {}
        for chunk in self.chunks:
            chunk_type = chunk.get("type", "unknown")
            types[chunk_type] = types.get(chunk_type, 0) + 1
        
        return {
            "total_chunks": len(self.chunks),
            "total_files": len(files),
            "chunk_types": types,
            "vocabulary_size": len(self.vocabulary),
            "index_file": str(self.index_file),
            "tfidf_file": str(self.tfidf_file)
        }
