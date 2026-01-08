"""
RAG Engine - Lightweight implementation using OpenAI embeddings
Retrieves relevant documentation chunks for context injection
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from openai import OpenAI


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine
    Uses OpenAI embeddings for semantic search over documentation
    """
    
    def __init__(self, kb_dir: Path = None):
        """
        Initialize RAG engine
        
        Args:
            kb_dir: Knowledge base directory (default: .kb/)
        """
        self.kb_dir = kb_dir or Path(".kb")
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.kb_dir / "index.json"
        self.embeddings_file = self.kb_dir / "embeddings.json"
        
        self.client = OpenAI()  # Uses OPENAI_API_KEY
        
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        
        # Load existing index if available
        if self.index_file.exists():
            self._load_index()
    
    def build(self, docs_dir: Path) -> None:
        """
        Build knowledge base from documentation directory
        
        Args:
            docs_dir: Directory containing documentation files
        """
        print(f"Building knowledge base from {docs_dir}...")
        
        # Clear existing data
        self.chunks = []
        self.embeddings = []
        
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
        
        # Generate embeddings
        print("Generating embeddings...")
        self._generate_embeddings()
        
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
    
    def _generate_embeddings(self) -> None:
        """Generate embeddings for all chunks using OpenAI"""
        # Batch process for efficiency
        batch_size = 100
        
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i + batch_size]
            texts = [self._chunk_to_text(chunk) for chunk in batch]
            
            # Call OpenAI embeddings API
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            self.embeddings.extend(batch_embeddings)
            
            print(f"  Processed {min(i + batch_size, len(self.chunks))}/{len(self.chunks)} chunks")
    
    def _chunk_to_text(self, chunk: Dict[str, Any]) -> str:
        """Convert chunk to text for embedding"""
        return f"{chunk['file']} - {chunk['section']}: {chunk['content'][:500]}"
    
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
        
        # Generate query embedding
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=[query_text]
        )
        query_embedding = response.data[0].embedding
        
        # Compute cosine similarity with all chunks
        similarities = []
        for idx, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((idx, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top K results
        results = []
        for idx, score in similarities[:top_k]:
            result = self.chunks[idx].copy()
            result["relevance"] = score
            results.append(result)
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0
    
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
        
        # Save embeddings
        with open(self.embeddings_file, 'w') as f:
            json.dump(self.embeddings, f)
        
        print(f"Index saved to {self.kb_dir}")
    
    def _load_index(self) -> None:
        """Load index from disk"""
        try:
            with open(self.index_file, 'r') as f:
                self.chunks = json.load(f)
            
            with open(self.embeddings_file, 'r') as f:
                self.embeddings = json.load(f)
            
            print(f"Loaded index: {len(self.chunks)} chunks")
        except Exception as e:
            print(f"Warning: Failed to load index: {e}")
            self.chunks = []
            self.embeddings = []
    
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
            "index_file": str(self.index_file),
            "embeddings_file": str(self.embeddings_file)
        }
