"""Input Handler for user interaction"""

from ..config.citation_formats import CITATION_FORMATS
from ..rag.rag_system import check_rag_ready


class InputHandler:
    """Handles user input and validation"""
    
    @staticmethod
    def select_citation_format() -> str:
        """
        Prompt user to select citation format.
        
        Returns:
            Citation format key (IEEE, APA, or Vancouver)
        """
        print("\nAvailable citation formats:")
        format_list = list(CITATION_FORMATS.keys())
        
        for idx, key in enumerate(format_list, 1):
            fmt = CITATION_FORMATS[key]
            print(f"  {idx}. {key}: {fmt['name']} - {fmt['description']}")
        print()
        
        user_input = input("Select citation format (1-3 or IEEE/APA/Vancouver): ").strip()
        
        # Handle numeric input
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(format_list):
                return format_list[idx]
        
        # Handle text input
        user_input_upper = user_input.upper()
        if user_input_upper in CITATION_FORMATS:
            return user_input_upper
        
        # Default to IEEE
        print("⚠️  Invalid selection. Defaulting to IEEE format.")
        return 'IEEE'
    
    @staticmethod
    def get_topic() -> str:
        """
        Prompt user for research topic.
        
        Returns:
            Research topic string
        """
        print("\nEnter your research topic:")
        topic = input("> ").strip()
        
        if not topic:
            raise ValueError("Topic cannot be empty")
        
        return topic
    
    @staticmethod
    def get_filename(topic: str) -> str:
        """
        Prompt user for output filename.
        
        Args:
            topic: Research topic (used for default filename)
        
        Returns:
            Output filename (without extension)
        """
        default_filename = topic.replace(" ", "_")[:50]
        
        print(f"\nEnter output filename (press Enter for '{default_filename}'):")
        filename = input("> ").strip()
        
        if not filename:
            filename = default_filename
        
        # Clean filename
        filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        return filename
    
    @staticmethod
    def ask_use_rag() -> bool:
        """
        Ask user if they want to use RAG for local PDF search.
        
        Returns:
            True if user wants to use RAG, False otherwise
        """
        # Check if RAG is ready
        ready, message = check_rag_ready()
        
        if not ready:
            print(f"\n⚠️  RAG not available: {message}")
            print("   Continuing with web search only.")
            return False
        
        print(f"\n✅ {message}")
        print("\nDo you want to search local PDFs for additional context? (y/n)")
        response = input("> ").strip().lower()
        
        return response in ['y', 'yes']
    
    @staticmethod
    def ask_export_pdf() -> bool:
        """
        Ask user if they want to export PDF.
        
        Returns:
            True if user wants PDF export, False otherwise
        """
        print("\nExport to PDF? (y/n, default: y)")
        response = input("> ").strip().lower()
        
        # Default to yes
        if not response:
            return True
        
        return response in ['y', 'yes']
