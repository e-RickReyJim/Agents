"""Research tasks - Web search and RAG search"""

from crewai import Task


def create_research_task(topic: str, citation_format: dict, web_researcher) -> Task:
    """
    Create web research task for finding academic papers.
    
    Args:
        topic: Research topic
        citation_format: Citation format dictionary from CITATION_FORMATS
        web_researcher: Web Researcher agent instance
    
    Returns:
        Task for web research
    """
    format_info = citation_format
    
    return Task(
        description=(
            f"Research the topic: {topic}\n\n"
            f"REQUIRED STEPS:\n"
            f"1. Use the web_search_tool to find 5-7 REAL, recent academic papers on {topic}\n"
            f"2. For each paper found, extract:\n"
            f"   - Complete author names\n"
            f"   - Full title\n"
            f"   - Journal/Conference name\n"
            f"   - Year of publication\n"
            f"   - Volume, issue, page numbers (if available)\n"
            f"   - DOI or URL\n"
            f"3. Format each reference in {format_info['name']} style:\n"
            f"   {format_info['reference_format']}\n"
            f"4. Create a research brief with:\n"
            f"   - Key concepts and definitions from the papers\n"
            f"   - Current state of research\n"
            f"   - Research gaps\n"
            f"   - Complete {format_info['name']}-formatted reference list\n\n"
            f"Example {format_info['name']} reference:\n{format_info['example']}"
        ),
        expected_output=(
            f"A detailed research document containing:\n"
            f"- Summary of key findings from real papers\n"
            f"- 5-7 {format_info['name']}-formatted references from web search\n"
            f"- Key technical points for the paper"
        ),
        agent=web_researcher
    )


def create_rag_task(topic: str, citation_format: dict, rag_agent) -> Task:
    """
    Create RAG task for searching local PDF library.
    
    Args:
        topic: Research topic
        citation_format: Citation format dictionary from CITATION_FORMATS
        rag_agent: RAG Agent instance
    
    Returns:
        Task for local PDF search
    """
    format_info = citation_format
    
    return Task(
        description=(
            f"Search local PDF library for content related to: {topic}\n\n"
            f"REQUIRED STEPS:\n"
            f"1. Use the rag_search_tool to search local PDFs for relevant content\n"
            f"2. Find 3-5 most relevant excerpts from local documents\n"
            f"3. For each excerpt, record:\n"
            f"   - Filename\n"
            f"   - Page number\n"
            f"   - Relevant text excerpt (200-300 words)\n"
            f"   - How it relates to the topic\n"
            f"4. Format local document citations in {format_info['name']} style:\n"
            f"   Mark as 'Local Document:' or 'Personal Library:'\n"
            f"   Example: [Local-1] Filename.pdf, page X.\n"
            f"5. Provide context on how these local sources ground the research\n\n"
            f"Your findings will be combined with web research to create a well-grounded paper."
        ),
        expected_output=(
            f"A local document research report containing:\n"
            f"- 3-5 relevant excerpts from local PDFs\n"
            f"- Properly formatted local document citations\n"
            f"- Context on how local sources relate to the topic\n"
            f"- Clear distinction from web sources"
        ),
        agent=rag_agent
    )
