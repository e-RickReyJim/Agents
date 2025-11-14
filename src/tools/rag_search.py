"""RAG search tool for querying local PDF library"""

from crewai_tools import tool
from ..rag.rag_system import RAGSystem


@tool("Local PDF Search Tool")
def rag_search_tool(query: str) -> str:
    """
    Search local PDF library for relevant content.
    Returns formatted excerpts from your personal document collection.
    Requires RAG index to be built first (run rag_setup.py).
    """
    try:
        rag = RAGSystem()
        
        if not rag.load_index():
            return "Local PDF library not available. Run 'python scripts/rag_setup.py' first to index your PDFs."
        
        # Search for relevant chunks
        results = rag.search(query, top_k=5)
        
        if not results:
            return "No relevant content found in local PDF library."
        
        # Format results with excerpts
        formatted = ["=== LOCAL PDF LIBRARY RESULTS ===\n"]
        
        for i, result in enumerate(results, 1):
            filename = result['filename']
            page = result['page_num']
            text = result['text']
            score = result.get('relevance_score', 0)
            
            # Truncate long excerpts
            excerpt = text[:300] + "..." if len(text) > 300 else text
            
            formatted.append(
                f"[Local-{i}] {filename} (page {page}, relevance: {score:.2f})\n"
                f"Excerpt: {excerpt}\n"
            )
        
        return "\n".join(formatted)
    
    except Exception as e:
        return f"Error accessing local PDF library: {str(e)}"
