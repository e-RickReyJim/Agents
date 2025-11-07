"""
RAG Setup Script - One-time PDF indexing
Run this script once to index your local PDF library
"""

import os
import sys
from pathlib import Path
from rag_utils import RAGSystem, check_rag_ready


def main():
    """Run one-time setup to index PDFs"""
    print("=" * 60)
    print("🔧 RAG System Setup - Local PDF Indexing")
    print("=" * 60)
    
    # Configuration
    pdf_folder = "./pdf_library"
    db_folder = "./rag_db"
    chunk_size = 500  # Words per chunk
    
    # Check if PDF folder exists
    pdf_path = Path(pdf_folder)
    if not pdf_path.exists():
        print(f"\n📁 Creating PDF library folder: {pdf_folder}")
        pdf_path.mkdir(exist_ok=True)
        print(f"\n❌ No PDFs found!")
        print(f"   Please add your PDF files to: {pdf_folder}")
        print(f"   Then run this script again.")
        return
    
    # Check for PDFs
    pdf_files = list(pdf_path.glob("*.pdf"))
    if not pdf_files:
        print(f"\n❌ No PDF files found in {pdf_folder}")
        print(f"   Please add your PDF files to that folder and try again.")
        return
    
    print(f"\n📚 Found {len(pdf_files)} PDF files:")
    for i, pdf in enumerate(pdf_files, 1):
        size_kb = pdf.stat().st_size / 1024
        print(f"   {i}. {pdf.name} ({size_kb:.1f} KB)")
    
    # Check if already indexed
    db_path = Path(db_folder)
    if db_path.exists() and (db_path / "faiss_index.bin").exists():
        print(f"\n⚠️  RAG index already exists in {db_folder}")
        response = input("   Re-index all PDFs? This will overwrite existing index (y/n): ")
        if response.lower() != 'y':
            print("   Cancelled. Using existing index.")
            return
        print("   Re-indexing...")
    
    # Create RAG system and index
    print(f"\n🚀 Starting indexing process...")
    print(f"   Chunk size: {chunk_size} words")
    print(f"   Embedding model: all-MiniLM-L6-v2 (local, no API)")
    print(f"   This may take 1-2 minutes depending on PDF size...\n")
    
    try:
        rag = RAGSystem(pdf_folder=pdf_folder, db_folder=db_folder)
        result = rag.index_pdfs(chunk_size=chunk_size)
        
        if result['success']:
            metadata = result['metadata']
            print(f"\n{'=' * 60}")
            print("✅ RAG SETUP COMPLETE!")
            print(f"{'=' * 60}")
            print(f"   📚 Indexed: {metadata['num_pdfs']} PDFs")
            print(f"   📄 Created: {metadata['num_chunks']} searchable chunks")
            print(f"   💾 Saved to: {db_folder}")
            print(f"\n📝 PDF files indexed:")
            for pdf in metadata['pdf_files']:
                print(f"   - {pdf}")
            print(f"\n✅ You can now use RAG in scientific_paper_writer.py")
            print(f"   The system will automatically search these PDFs when enabled.")
            
        else:
            print(f"\n❌ Setup failed: {result.get('message', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print(f"   Make sure all dependencies are installed:")
        print(f"   pip install pypdf sentence-transformers faiss-cpu numpy")
        sys.exit(1)
    
    # Test search
    print(f"\n🧪 Running test search...")
    test_query = "machine learning artificial intelligence data science"
    results = rag.search(test_query, top_k=3)
    
    if results:
        print(f"✅ Test search successful! Found {len(results)} relevant chunks.")
        print(f"\nSample result:")
        print(f"   File: {results[0]['filename']}")
        print(f"   Page: {results[0]['page_num']}")
        print(f"   Preview: {results[0]['text'][:150]}...")
    else:
        print(f"⚠️  Test search found no results (this is OK if PDFs don't contain test keywords)")
    
    print(f"\n{'=' * 60}")
    print("🎉 Setup complete! Run: python scientific_paper_writer.py")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
