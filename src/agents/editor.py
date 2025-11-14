"""Editor Agent for polishing scientific papers"""

from crewai import Agent


class EditorAgent:
    """Technical Editor specializing in citation formats"""
    
    @staticmethod
    def create(llm, citation_format: dict) -> Agent:
        """
        Create editor agent.
        
        Args:
            llm: Language model instance
            citation_format: Citation format dictionary from CITATION_FORMATS
        
        Returns:
            Configured Agent instance
        """
        format_info = citation_format
        
        return Agent(
            role=f"Technical Editor ({format_info['name']} specialist)",
            goal=f"Review and refine the scientific paper to meet {format_info['name']} publication standards",
            backstory=(
                f"You are a meticulous technical editor specializing in {format_info['name']} formatting. "
                f"You ensure:\n"
                f"- All citations follow {format_info['name']} style exactly\n"
                f"- Reference list is properly formatted\n"
                f"- In-text citations match the reference list\n"
                f"- Grammar and technical writing are excellent\n"
                f"- Paper structure follows academic standards\n"
                f"You maintain the formal academic tone required for scientific publications."
            ),
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
