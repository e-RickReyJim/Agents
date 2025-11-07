"""
Advanced Scientific Paper Writer with Multiple Citation Formats
Supports: IEEE, APA, Vancouver
Features: Real web search, RAG (local PDF search), PDF export, multiple citation styles
"""

import os
import warnings
import requests
import markdown
import time
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai_tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from rag_utils import RAGSystem, check_rag_ready

# Suppress warnings
warnings.filterwarnings('ignore')

# Rate limiting configuration
REQUEST_DELAY = 5  # seconds between major operations (to stay under 15 req/min)

# Load environment variables
load_dotenv()

# Citation format templates
CITATION_FORMATS = {
    'IEEE': {
        'name': 'IEEE',
        'description': 'Institute of Electrical and Electronics Engineers',
        'in_text': '[N]',
        'reference_format': '[N] Authors, "Title," Journal, vol. X, no. Y, pp. Z, Year.',
        'example': '[1] A. Author and B. Coauthor, "Article Title," Journal Name, vol. 10, no. 2, pp. 123-456, 2023.'
    },
    'APA': {
        'name': 'APA 7th',
        'description': 'American Psychological Association (7th edition)',
        'in_text': '(Authors, Year)',
        'reference_format': 'Authors (Year). Title. Journal, Volume(Issue), Pages. DOI',
        'example': 'Smith, J., & Doe, A. (2023). Article title. Journal Name, 10(2), 123-456. https://doi.org/10.1234/example'
    },
    'Vancouver': {
        'name': 'Vancouver',
        'description': 'International Committee of Medical Journal Editors',
        'in_text': '(N)',
        'reference_format': 'N. Authors. Title. Journal. Year;Volume(Issue):Pages.',
        'example': '1. Smith J, Doe A. Article title. Journal Name. 2023;10(2):123-456.'
    }
}

@tool("Web Search Tool")
def web_search_tool(query: str) -> str:
    """
    Search the web for recent academic papers and credible sources.
    Returns formatted results with titles, authors, and publication info.
    """
    try:
        # Using a simple Google Scholar-like search
        # In production, use Serper API, SerpAPI, or similar
        search_url = f"https://api.crossref.org/works?query={query}&rows=5"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for idx, item in enumerate(data.get('message', {}).get('items', [])[:5], 1):
                title = item.get('title', ['Unknown'])[0] if item.get('title') else 'Unknown'
                authors = []
                for author in item.get('author', [])[:3]:
                    given = author.get('given', '')
                    family = author.get('family', '')
                    if given and family:
                        authors.append(f"{given[0]}. {family}")
                
                authors_str = ', '.join(authors) if authors else 'Unknown Authors'
                journal = item.get('container-title', ['Unknown Journal'])[0] if item.get('container-title') else 'Unknown Journal'
                year = item.get('published', {}).get('date-parts', [[0]])[0][0] if item.get('published') else 'N/A'
                doi = item.get('DOI', 'N/A')
                
                results.append(f"{idx}. {authors_str}, \"{title}\", {journal}, {year}. DOI: {doi}")
            
            return "\n".join(results) if results else "No results found"
        else:
            return "Web search unavailable. Using general knowledge for references."
    
    except Exception as e:
        return f"Web search unavailable: {str(e)}. Using general knowledge for references."


@tool("Local PDF Search Tool")
def rag_search_tool(query: str) -> str:
    """
    Search local PDF library for relevant content.
    Returns formatted excerpts from your personal document collection.
    """
    try:
        rag = RAGSystem()
        
        if not rag.load_index():
            return "Local PDF library not available. Run 'python rag_setup.py' first to index your PDFs."
        
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


def get_gemini_llm():
    """Initialize and return the Gemini LLM with rate limiting"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables.\n"
            "Please create a .env file with your Google API key."
        )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7,
        google_api_key=api_key,
        max_retries=3,  # Retry on rate limit
        request_timeout=120  # 2 minute timeout
    )
    
    return llm


def create_agents(llm, citation_format, use_rag=False):
    """Create the three agents with format-specific instructions"""
    
    format_info = CITATION_FORMATS[citation_format]
    
    # Prepare tools - add RAG if enabled
    researcher_tools = [web_search_tool]
    if use_rag:
        researcher_tools.append(rag_search_tool)
    
    # Enhanced researcher role when RAG is enabled
    rag_addition = ""
    if use_rag:
        rag_addition = (
            "\n\nYou also have access to a local PDF library. "
            "Use BOTH web search AND local PDF search to find relevant sources. "
            "Combine findings from online papers and local documents. "
            "Clearly distinguish between web sources and local PDFs in your citations. "
            "Local PDF citations should be marked as 'Local Document' or 'Personal Library'."
        )
    
    researcher = Agent(
        role="Scientific Researcher with Web Search" + (" and Local PDF Library" if use_rag else ""),
        goal=f"Research {{{citation_format}}} topic using available tools to find real, recent academic papers and format references in {format_info['name']} style",
        backstory=(
            f"You are an expert researcher with access to research tools. "
            f"You find REAL, published academic papers and format citations in {format_info['name']} style.\n\n"
            f"Citation format: {format_info['name']}\n"
            f"In-text citation: {format_info['in_text']}\n"
            f"Reference format: {format_info['reference_format']}\n"
            f"Example: {format_info['example']}\n\n"
            "You MUST use the web search tool to find real papers. "
            "Extract actual author names, titles, journals, years, and DOIs. "
            "Format each reference exactly according to the style guide."
            f"{rag_addition}"
        ),
        tools=researcher_tools,
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    writer = Agent(
        role=f"Scientific Paper Writer ({format_info['name']} format)",
        goal=f"Write a well-structured scientific paper on {{{citation_format}}} topic with proper {format_info['name']}-style citations",
        backstory=(
            f"You are an experienced academic writer specializing in {format_info['name']} format papers. "
            f"You structure papers with: Abstract, Introduction, Literature Review, Methodology, "
            f"Results/Discussion, Conclusion, and References.\n\n"
            f"You cite sources using {format_info['name']} in-text format: {format_info['in_text']}\n"
            f"You ensure all references are properly formatted in {format_info['name']} style. "
            f"You use formal academic language and maintain technical accuracy."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    editor = Agent(
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
    
    return researcher, writer, editor


def create_tasks(researcher, writer, editor, citation_format, topic, use_rag=False):
    """Create the three tasks with format-specific instructions"""
    
    format_info = CITATION_FORMATS[citation_format]
    
    # Add RAG instructions if enabled
    rag_instructions = ""
    if use_rag:
        rag_instructions = (
            f"\n5. ALSO use the rag_search_tool to search your local PDF library\n"
            f"6. Combine web search results with local PDF findings\n"
            f"7. Format local sources appropriately:\n"
            f"   - Mark as 'Local Document' or from 'Personal Library'\n"
            f"   - Include filename and page number\n"
            f"   - Use same {format_info['name']} style but note the source type\n"
        )
    
    research_task = Task(
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
            f"   - Complete {format_info['name']}-formatted reference list"
            f"{rag_instructions}\n\n"
            f"Example {format_info['name']} reference:\n{format_info['example']}"
        ),
        expected_output=(
            f"A detailed research document containing:\n"
            f"- Summary of key findings from real papers\n"
            f"- 5-7 {format_info['name']}-formatted references from web search"
            + ("\n- Additional references from local PDF library (if found)" if use_rag else "")
            + f"\n- Key technical points for the paper"
        ),
        agent=researcher
    )
    
    write_task = Task(
        description=(
            f"Using the research findings, write a complete scientific paper on: {topic}\n\n"
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
            f"- Professional academic tone"
        ),
        agent=writer
    )
    
    edit_task = Task(
        description=(
            f"Review and edit the scientific paper for {format_info['name']} compliance.\n\n"
            f"Check:\n"
            f"1. All citations follow {format_info['name']} format exactly\n"
            f"2. In-text citations: {format_info['in_text']}\n"
            f"3. Reference list format: {format_info['reference_format']}\n"
            f"4. Grammar and clarity\n"
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
            f"- Clear, professional writing"
        ),
        agent=editor
    )
    
    return research_task, write_task, edit_task


def markdown_to_pdf(markdown_content, output_path, citation_format):
    """Convert markdown to PDF with proper formatting (Windows-compatible)"""
    
    # Method 1: Try reportlab (Windows-friendly)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
        import re
        
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=inch, leftMargin=inch,
                              topMargin=inch, bottomMargin=inch)
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=12, 
                                 fontName='Times-Roman', leading=14))
        styles.add(ParagraphStyle(name='PaperTitle', alignment=TA_CENTER, fontSize=18,
                                 fontName='Times-Bold', spaceAfter=30))
        styles.add(ParagraphStyle(name='PaperHeading', fontSize=14, fontName='Times-Bold',
                                 spaceAfter=12, spaceBefore=12))
        
        story = []
        
        # Simple markdown parsing
        lines = markdown_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.2*inch))
                continue
            
            # Title (# )
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, styles['PaperTitle']))
            # Heading (## )
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, styles['PaperHeading']))
            # Regular text
            else:
                # Escape special characters for reportlab
                text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(text, styles['Justify']))
        
        # Add footer
        footer_style = ParagraphStyle(name='Footer', fontSize=10, 
                                     alignment=TA_CENTER, textColor='gray')
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')} | Format: {citation_format}",
            footer_style
        ))
        
        doc.build(story)
        return True
        
    except ImportError:
        pass
    
    # Method 2: Try weasyprint (requires GTK3 on Windows)
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'toc']
        )
        
        # Add CSS styling based on citation format
        css_style = f"""
        @page {{
            size: letter;
            margin: 1in;
            @bottom-right {{
                content: counter(page);
            }}
        }}
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000;
        }}
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            text-align: center;
            margin-top: 0;
            margin-bottom: 20pt;
        }}
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            margin-top: 16pt;
            margin-bottom: 8pt;
        }}
        h3 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 12pt;
            margin-bottom: 6pt;
        }}
        p {{
            text-align: justify;
            margin-bottom: 12pt;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30pt;
        }}
        .footer {{
            text-align: center;
            font-size: 10pt;
            margin-top: 30pt;
            border-top: 1px solid #ccc;
            padding-top: 10pt;
        }}
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Scientific Paper - {citation_format} Format</title>
        </head>
        <body>
            {html_content}
            <div class="footer">
                Generated on {datetime.now().strftime('%B %d, %Y')} | Format: {citation_format}
            </div>
        </body>
        </html>
        """
        
        font_config = FontConfiguration()
        HTML(string=full_html).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_style, font_config=font_config)],
            font_config=font_config
        )
        
        return True
    except Exception as e:
        print(f"⚠️  PDF generation failed: {e}")
        print("   Markdown file saved successfully. Install WeasyPrint for PDF export:")
        print("   pip install weasyprint")
        return False


def main():
    """Main execution function"""
    
    print("="*80)
    print("ADVANCED SCIENTIFIC PAPER WRITER")
    print("Powered by Google Gemini and CrewAI")
    print("Features: Multiple citation formats, Web search, PDF export")
    print("="*80)
    print()
    
    # Select citation format
    print("Available citation formats:")
    format_list = list(CITATION_FORMATS.keys())
    for idx, key in enumerate(format_list, 1):
        fmt = CITATION_FORMATS[key]
        print(f"  {idx}. {key}: {fmt['name']} - {fmt['description']}")
    print()
    
    user_input = input("Select citation format (1-3 or IEEE/APA/Vancouver): ").strip()
    
    # Handle numeric input
    if user_input.isdigit():
        idx = int(user_input)
        if 1 <= idx <= len(format_list):
            citation_format = format_list[idx - 1]
        else:
            print(f"❌ Invalid number. Using IEEE as default.")
            citation_format = 'IEEE'
    else:
        # Handle text input
        citation_format = user_input.upper()
        if citation_format not in CITATION_FORMATS:
            print(f"❌ Invalid format. Using IEEE as default.")
            citation_format = 'IEEE'
    
    format_info = CITATION_FORMATS[citation_format]
    print(f"\n✅ Using {format_info['name']} format")
    print(f"   In-text: {format_info['in_text']}")
    print()
    
    # Get topic
    topic = input("Enter the research topic: ").strip()
    
    if not topic:
        print("❌ Error: Topic cannot be empty!")
        return
    
    # Check if RAG is available and ask user
    use_rag = False
    rag_ready, rag_message = check_rag_ready()
    
    if rag_ready:
        print(f"\n✅ {rag_message}")
        rag_input = input("Use local PDF library in addition to web search? (y/n): ").strip().lower()
        use_rag = (rag_input == 'y')
        
        if use_rag:
            print("📚 Will search both web AND local PDF library")
        else:
            print("🌐 Will search web only")
    else:
        print(f"\n⚠️  {rag_message}")
        print("   To enable local PDF search, run: python rag_setup.py")
        print("🌐 Will search web only")
    
    print(f"\n📚 Generating {format_info['name']}-style scientific paper on: {topic}")
    print("🔍 Searching for real academic references...")
    print("⏳ This may take several minutes...\n")
    
    try:
        # Initialize Gemini
        print("🔧 Initializing Gemini model...")
        llm = get_gemini_llm()
        
        # Create agents
        print(f"👥 Creating AI agents for {format_info['name']} format...")
        if use_rag:
            print("   + RAG-enhanced researcher (web + local PDFs)")
        researcher, writer, editor = create_agents(llm, citation_format, use_rag)
        
        # Create tasks
        print("📋 Setting up research, writing, and editing tasks...")
        research_task, write_task, edit_task = create_tasks(
            researcher, writer, editor, citation_format, topic, use_rag
        )
        
        # Create crew
        print("🚀 Assembling the crew and starting work...")
        print(f"⏱️  Using {REQUEST_DELAY}s delays between tasks to avoid rate limits\n")
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, write_task, edit_task],
            verbose=2
        )
        
        # Execute with rate limiting awareness
        print("📝 Starting paper generation (this may take 5-10 minutes)...\n")
        result = crew.kickoff(inputs={"topic": topic, citation_format: citation_format})
        
        # Save markdown
        safe_topic = topic.replace(' ', '_').replace('/', '_').lower()
        md_filename = f"paper_{citation_format.lower()}_{safe_topic}.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n" + "="*80)
        print("✅ PAPER GENERATION COMPLETE!")
        print("="*80)
        print(f"\n📄 Markdown saved to: {md_filename}")
        
        # Export to PDF
        export_pdf = input("\n📥 Export to PDF? (y/n): ").strip().lower()
        
        if export_pdf == 'y':
            pdf_filename = md_filename.replace('.md', '.pdf')
            print(f"\n🔄 Converting to PDF...")
            
            if markdown_to_pdf(result, pdf_filename, format_info['name']):
                print(f"✅ PDF saved to: {pdf_filename}")
            else:
                print(f"⚠️  PDF export failed, but markdown file is available")
        
        print("\n📋 Preview of the paper:")
        print("-"*80)
        print(result[:800] + "..." if len(result) > 800 else result)
        print("-"*80)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
