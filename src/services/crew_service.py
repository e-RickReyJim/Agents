"""Crew Service for managing agent and task orchestration"""

import time
from crewai import Crew, Process
from ..agents.researcher import WebResearcherAgent
from ..agents.rag_agent import RAGAgent
from ..agents.writer import WriterAgent
from ..agents.editor import EditorAgent
from ..tasks.research_tasks import create_research_task, create_rag_task
from ..tasks.writing_tasks import create_write_task, create_edit_task
from ..config.settings import Settings


class CrewService:
    """Service for orchestrating multi-agent crew execution"""
    
    def __init__(self, llm):
        """
        Initialize crew service.
        
        Args:
            llm: Language model instance
        """
        self.llm = llm
        self.settings = Settings
    
    def create_crew(
        self,
        topic: str,
        citation_format: dict,
        use_rag: bool = False
    ) -> tuple:
        """
        Create agents and tasks for paper generation.
        
        Args:
            topic: Research topic
            citation_format: Citation format dictionary from CITATION_FORMATS
            use_rag: Whether to use RAG for local PDF search
        
        Returns:
            Tuple of (crew, final_paper_content)
        """
        # Create agents
        web_researcher = WebResearcherAgent.create(self.llm, citation_format)
        writer = WriterAgent.create(self.llm, citation_format, use_rag)
        editor = EditorAgent.create(self.llm, citation_format)
        
        rag_agent = None
        if use_rag:
            rag_agent = RAGAgent.create(self.llm, citation_format)
        
        # Create tasks
        web_research_task = create_research_task(topic, citation_format, web_researcher)
        
        rag_task = None
        if use_rag and rag_agent:
            rag_task = create_rag_task(topic, citation_format, rag_agent)
        
        write_task = create_write_task(
            topic, citation_format, writer, 
            web_research_task, rag_task
        )
        
        edit_task = create_edit_task(citation_format, editor, use_rag)
        
        # Build task list
        if use_rag:
            tasks = [web_research_task, rag_task, write_task, edit_task]
            agents = [web_researcher, rag_agent, writer, editor]
        else:
            tasks = [web_research_task, write_task, edit_task]
            agents = [web_researcher, writer, editor]
        
        # Create crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        return crew, tasks
    
    def execute_crew(self, crew: Crew, topic: str) -> str:
        """
        Execute crew and return final paper.
        
        Args:
            crew: Crew instance to execute
            topic: Research topic (for input)
        
        Returns:
            Final paper content as string
        """
        print("\n" + "="*80)
        print("🚀 Starting multi-agent paper generation...")
        print("="*80 + "\n")
        
        # Rate limiting delay
        time.sleep(self.settings.REQUEST_DELAY)
        
        # Execute crew
        result = crew.kickoff(inputs={"topic": topic})
        
        print("\n" + "="*80)
        print("✅ Paper generation complete!")
        print("="*80 + "\n")
        
        # Extract final paper content
        if hasattr(result, 'raw'):
            return result.raw
        elif hasattr(result, 'output'):
            return result.output
        else:
            return str(result)
