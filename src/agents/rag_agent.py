"""RAG Agent for local PDF search"""

from crewai import Agent
from ..tools.rag_search import rag_search_tool


class RAGAgent:
    """Local Document Specialist for searching PDF library"""
    
    @staticmethod
    def create(llm, citation_format: dict) -> Agent:
        """
        Create RAG agent for local PDF search.
        
        Args:
            llm: Language model instance
            citation_format: Citation format dictionary from CITATION_FORMATS
        
        Returns:
            Configured Agent instance
        """
        format_info = citation_format
        
        return Agent(
            role="Local Document Specialist",
            goal=f"Search local PDF library for relevant context and format findings in {format_info['name']} style",
            backstory=(
                f"You are an expert at analyzing local PDF documents in the personal library. "
                f"You search through uploaded PDFs to find relevant context that can ground the research. "
                f"You specialize in {format_info['name']} citation format.\n\n"
                f"Citation format: {format_info['name']}\n"
                f"In-text citation for local docs: {format_info['in_text']} with 'Local:' prefix\n"
                f"Reference format: {format_info['reference_format']}\n\n"
                "You use the RAG search tool to find relevant excerpts from local PDFs. "
                "You provide context, key findings, and properly formatted citations for local documents. "
                "You clearly mark sources as 'Local Document' or 'Personal Library'. "
                "You provide filename, page numbers, and relevant excerpts."
            ),
            tools=[rag_search_tool],
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
