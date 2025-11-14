"""Writing tasks - Write and edit paper"""

from crewai import Task


def create_write_task(
    topic: str,
    citation_format: dict,
    writer,
    web_research_task: Task,
    rag_task: Task = None
) -> Task:
    """
    Create writing task for drafting scientific paper.
    
    Args:
        topic: Research topic
        citation_format: Citation format dictionary from CITATION_FORMATS
        writer: Writer agent instance
        web_research_task: Completed web research task
        rag_task: Optional RAG research task
    
    Returns:
        Task for writing paper
    """
    format_info = citation_format
    use_rag = rag_task is not None
    
    write_task_context = "web research" + (" and local document findings" if use_rag else "")
    
    return Task(
        description=(
            f"Using the {write_task_context}, write a complete scientific paper on: {topic}\n\n"
            f"Structure:\n"
            f"1. Title - Clear and descriptive\n"
            f"2. Abstract (150-200 words)\n"
            f"3. Introduction - Context, motivation, contributions\n"
            f"4. Literature Review - Survey existing research with {format_info['name']} citations\n"
            f"5. Methodology - Technical approach\n"
            f"6. Results and Discussion - Findings and implications\n"
            f"7. Conclusion - Summary and future work\n"
            f"8. References - {format_info['name']}-formatted list\n\n"
            f"Citation Requirements:\n"
            f"- Use {format_info['name']} in-text format: {format_info['in_text']}\n"
            f"- Cite BOTH web sources" + (" AND local documents" if use_rag else "") + "\n"
            f"- Clearly distinguish web vs local sources in references\n"
            f"- Include minimum 5 properly cited references\n"
            f"- All citations must match the reference list\n"
            f"- Use formal academic language\n"
            f"- Each section: 2-4 paragraphs"
        ),
        expected_output=(
            f"A complete scientific paper in markdown format with:\n"
            f"- All required sections\n"
            f"- {format_info['name']} in-text citations throughout\n"
            f"- Complete reference list in {format_info['name']} format\n"
            + ("- Mixed references (web + local sources)\n" if use_rag else "")
            + f"- Professional academic tone"
        ),
        agent=writer,
        context=[web_research_task] + ([rag_task] if rag_task else [])
    )


def create_edit_task(
    citation_format: dict,
    editor,
    use_rag: bool = False
) -> Task:
    """
    Create editing task for polishing scientific paper.
    
    Args:
        citation_format: Citation format dictionary from CITATION_FORMATS
        editor: Editor agent instance
        use_rag: Whether RAG was used (affects checklist)
    
    Returns:
        Task for editing paper
    """
    format_info = citation_format
    
    return Task(
        description=(
            f"Review and edit the scientific paper for {format_info['name']} compliance.\n\n"
            f"Check:\n"
            f"1. All citations follow {format_info['name']} format exactly\n"
            f"2. In-text citations: {format_info['in_text']}\n"
            f"3. Reference list format: {format_info['reference_format']}\n"
            + ("4. Local sources clearly marked and properly formatted\n" if use_rag else "")
            + f"4. Grammar and clarity\n"
            f"5. Technical accuracy\n"
            f"6. Proper paper structure\n"
            f"7. All in-text citations have corresponding references\n"
            f"8. Professional academic tone\n"
            f"9. Consistent terminology\n"
            f"10. Logical flow between sections"
        ),
        expected_output=(
            f"A polished, publication-ready scientific paper with:\n"
            f"- Perfect {format_info['name']} formatting\n"
            f"- Correct grammar and style\n"
            f"- Properly formatted citations and references\n"
            + ("- Clear distinction between web and local sources\n" if use_rag else "")
            + f"- Clear, professional writing"
        ),
        agent=editor
    )
