"""Writer Agent for drafting scientific papers"""

from crewai import Agent


class WriterAgent:
    """Scientific Paper Writer"""
    
    @staticmethod
    def create(llm, citation_format: dict, use_rag: bool = False) -> Agent:
        """
        Create writer agent.
        
        Args:
            llm: Language model instance
            citation_format: Citation format dictionary from CITATION_FORMATS
            use_rag: Whether RAG is enabled (affects backstory)
        
        Returns:
            Configured Agent instance
        """
        format_info = citation_format
        
        return Agent(
            role=f"Scientific Paper Writer ({format_info['name']} format)",
            goal=f"Write a well-structured scientific paper with proper {format_info['name']}-style citations using provided research",
            backstory=(
                f"You are an experienced academic writer specializing in {format_info['name']} format papers. "
                f"You structure papers with: Abstract, Introduction, Literature Review, Methodology, "
                f"Results/Discussion, Conclusion, and References.\n\n"
                f"You cite sources using {format_info['name']} in-text format: {format_info['in_text']}\n"
                f"You synthesize research from web sources" + (" and local documents" if use_rag else "") + ". "
                f"You ensure all references are properly formatted in {format_info['name']} style. "
                f"You use formal academic language and maintain technical accuracy."
            ),
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
