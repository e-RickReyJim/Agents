"""
Scientific Paper Writer - Main Entry Point
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.citation_formats import CITATION_FORMATS
from src.services.llm_service import LLMService
from src.services.crew_service import CrewService
from src.services.export_service import ExportService
from src.utils.input_handler import InputHandler


def main():
    """Main execution function"""
    
    print("="*80)
    print("ADVANCED SCIENTIFIC PAPER WRITER")
    print("Powered by Google Gemini and CrewAI")
    print("Features: Multiple citation formats, Web search, RAG, PDF export")
    print("="*80)
    print()
    
    try:
        # Get user inputs
        citation_format_key = InputHandler.select_citation_format()
        citation_format = CITATION_FORMATS[citation_format_key]
        
        topic = InputHandler.get_topic()
        filename = InputHandler.get_filename(topic)
        use_rag = InputHandler.ask_use_rag()
        export_pdf = InputHandler.ask_export_pdf()
        
        # Display configuration
        print("\n" + "="*80)
        print("CONFIGURATION")
        print("="*80)
        print(f"Topic: {topic}")
        print(f"Citation Format: {citation_format['name']}")
        print(f"RAG (Local PDF Search): {'Yes' if use_rag else 'No'}")
        print(f"Export PDF: {'Yes' if export_pdf else 'No'}")
        print(f"Output Filename: {filename}")
        print("="*80 + "\n")
        
        # Initialize services
        print("🔧 Initializing services...")
        llm_service = LLMService()
        llm = llm_service.get_llm()
        print(f"✅ LLM initialized: {llm_service.model_name}")
        
        crew_service = CrewService(llm)
        export_service = ExportService()
        
        # Create and execute crew
        print("🤖 Creating multi-agent crew...")
        crew, tasks = crew_service.create_crew(topic, citation_format, use_rag)
        
        agent_count = 4 if use_rag else 3
        print(f"✅ Crew ready with {agent_count} agents and {len(tasks)} tasks\n")
        
        # Execute
        final_paper = crew_service.execute_crew(crew, topic)
        
        # Export results
        print("\n" + "="*80)
        print("EXPORTING RESULTS")
        print("="*80)
        
        results = export_service.export_paper(
            final_paper,
            filename,
            citation_format_key,
            export_pdf
        )
        
        # Success message
        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"Markdown: {results['markdown']}")
        if results['pdf']:
            print(f"PDF: {results['pdf']}")
        print("="*80 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
