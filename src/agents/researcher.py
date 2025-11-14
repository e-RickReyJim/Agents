"""Web Research Agent"""

from crewai import Agent
from ..tools.web_search import web_search_tool


class WebResearcherAgent:
    """Web Research Specialist for finding academic papers"""
    
    @staticmethod
    def create(llm, citation_format: dict) -> Agent:
        """
        Create web researcher agent.
        
        Args:
            llm: Language model instance
            citation_format: Citation format dictionary from CITATION_FORMATS
        
        Returns:
            Configured Agent instance
        """
        format_info = citation_format
        
        return Agent(
            role="Web Research Specialist",
            goal=f"Search the internet for real, recent academic papers on the topic and format references in {format_info['name']} style",
            backstory=(
                f"You are an expert at finding published academic papers online. "
                f"You specialize in {format_info['name']} citation format.\n\n"
                f"Citation format: {format_info['name']}\n"
                f"In-text citation: {format_info['in_text']}\n"
                f"Reference format: {format_info['reference_format']}\n"
                f"Example: {format_info['example']}\n\n"
                "You MUST use the web search tool to find real papers from CrossRef. "
                "Extract actual author names, titles, journals, years, and DOIs. "
                "Format each reference exactly according to the style guide. "
                "Provide a comprehensive research summary with 5-7 properly cited sources."
            ),
            tools=[web_search_tool],
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
