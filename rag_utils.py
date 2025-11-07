"""
RAG Utilities for Local PDF Document Retrieval
Handles PDF loading, chunking, embedding, and vector search
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

try:
    from pypdf import PdfReader
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("⚠️  RAG dependencies not installed. Run: pip install pypdf sentence-transformers faiss-cpu")
    raise


class RAGSystem:
    """Manages PDF indexing and retrieval using local embeddings"""
    
    def __init__(self, pdf_folder: str = "./pdf_library", db_folder: str = "./rag_db"):
        self.pdf_folder = Path(pdf_folder)
        self.db_folder = Path(db_folder)
        self.db_folder.mkdir(exist_ok=True)
        
        # Paths for saved data
        self.index_path = self.db_folder / "faiss_index.bin"
        self.chunks_path = self.db_folder / "chunks.pkl"
        self.metadata_path = self.db_folder / "metadata.json"
        
        # Initialize embedding model (local, no API needed)
        print("🔧 Loading embedding model (sentence-transformers)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight
        self.embedding_dim = 384  # Dimension of this model
        
        # Will load index if exists
        self.index = None
        self.chunks = []
        self.metadata = {}
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[str]:
        """Extract text from PDF file, return list of pages"""
        try:
            reader = PdfReader(str(pdf_path))
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    pages.append({
                        'text': text,
                        'page_num': i + 1,
                        'filename': pdf_path.name
                    })
            return pages
        except Exception as e:
            print(f"⚠️  Error reading {pdf_path.name}: {e}")
            return []
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # Skip very small chunks
                chunks.append(chunk)
        
        return chunks
    
    def index_pdfs(self, chunk_size: int = 500) -> Dict:
        """Index all PDFs in pdf_folder"""
        print(f"\n📚 Indexing PDFs from: {self.pdf_folder}")
        
        # Find all PDFs
        pdf_files = list(self.pdf_folder.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ No PDF files found in {self.pdf_folder}")
            print(f"   Please add PDF files to the folder and try again.")
            return {'success': False, 'message': 'No PDFs found'}
        
        print(f"   Found {len(pdf_files)} PDF files")
        
        all_chunks = []
        all_embeddings = []
        
        # Process each PDF
        for pdf_path in pdf_files:
            print(f"   📄 Processing: {pdf_path.name}")
            
            # Extract pages
            pages = self.extract_text_from_pdf(pdf_path)
            
            if not pages:
                continue
            
            # Chunk each page
            for page_data in pages:
                chunks = self.chunk_text(page_data['text'], chunk_size)
                
                for chunk_idx, chunk in enumerate(chunks):
                    # Store chunk with metadata
                    chunk_data = {
                        'text': chunk,
                        'filename': page_data['filename'],
                        'page_num': page_data['page_num'],
                        'chunk_idx': chunk_idx
                    }
                    all_chunks.append(chunk_data)
                    
                    # Create embedding
                    embedding = self.model.encode(chunk, show_progress_bar=False)
                    all_embeddings.append(embedding)
        
        if not all_chunks:
            print(f"❌ No text could be extracted from PDFs")
            return {'success': False, 'message': 'No text extracted'}
        
        print(f"\n✅ Created {len(all_chunks)} chunks from {len(pdf_files)} PDFs")
        
        # Create FAISS index
        print("🔧 Building FAISS index...")
        embeddings_array = np.array(all_embeddings).astype('float32')
        
        # Use flat index for small datasets (< 1000 docs)
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings_array)
        
        self.chunks = all_chunks
        
        # Save everything
        print("💾 Saving index and metadata...")
        faiss.write_index(self.index, str(self.index_path))
        
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        metadata = {
            'num_pdfs': len(pdf_files),
            'num_chunks': len(all_chunks),
            'pdf_files': [f.name for f in pdf_files],
            'chunk_size': chunk_size,
            'embedding_model': 'all-MiniLM-L6-v2'
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.metadata = metadata
        
        print(f"✅ RAG system indexed and saved to: {self.db_folder}")
        return {'success': True, 'metadata': metadata}
    
    def load_index(self) -> bool:
        """Load existing index from disk"""
        if not self.index_path.exists():
            return False
        
        try:
            print("📂 Loading existing RAG index...")
            self.index = faiss.read_index(str(self.index_path))
            
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
            
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            print(f"✅ Loaded index with {self.metadata['num_chunks']} chunks from {self.metadata['num_pdfs']} PDFs")
            return True
        
        except Exception as e:
            print(f"⚠️  Error loading index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant chunks"""
        if self.index is None:
            if not self.load_index():
                return []
        
        # Encode query
        query_embedding = self.model.encode(query, show_progress_bar=False)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                chunk_data = self.chunks[idx].copy()
                chunk_data['relevance_score'] = float(1.0 / (1.0 + distance))  # Convert distance to similarity
                results.append(chunk_data)
        
        return results
    
    def format_results_for_citation(self, results: List[Dict], citation_format: str) -> str:
        """Format search results as citations in specified format"""
        if not results:
            return "No relevant local documents found."
        
        formatted = []
        
        for i, result in enumerate(results, 1):
            filename = result['filename']
            page = result['page_num']
            text_preview = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
            
            # Format based on citation style
            if citation_format == 'IEEE':
                citation = f"[Local-{i}] {filename}, page {page}."
            elif citation_format == 'APA':
                citation = f"(Local Document: {filename}, p. {page})"
            elif citation_format == 'Vancouver':
                citation = f"L{i}. {filename}. Page {page}."
            else:
                citation = f"[{filename}, p. {page}]"
            
            formatted.append(f"{citation}\nRelevant excerpt: {text_preview}\n")
        
        return "\n".join(formatted)


def check_rag_ready(pdf_folder: str = "./pdf_library", db_folder: str = "./rag_db") -> Tuple[bool, str]:
    """Check if RAG system is ready to use"""
    pdf_path = Path(pdf_folder)
    db_path = Path(db_folder)
    
    # Check if PDFs exist
    if not pdf_path.exists():
        return False, f"PDF folder not found: {pdf_folder}"
    
    pdf_files = list(pdf_path.glob("*.pdf"))
    if not pdf_files:
        return False, f"No PDF files found in {pdf_folder}"
    
    # Check if index exists
    index_file = db_path / "faiss_index.bin"
    if not index_file.exists():
        return False, f"RAG index not found. Run 'python rag_setup.py' first."
    
    return True, f"RAG ready: {len(pdf_files)} PDFs indexed"


if __name__ == "__main__":
    # Quick test
    rag = RAGSystem()
    
    if not rag.load_index():
        print("No index found. Run rag_setup.py first.")
    else:
        # Test search
        query = "machine learning"
        results = rag.search(query, top_k=3)
        print(f"\n🔍 Test search for: '{query}'")
        print(rag.format_results_for_citation(results, 'IEEE'))
