"""
IEEE Scientific Paper Writer using CrewAI and Google Gemini

This script uses three AI agents to research, write, and edit an IEEE-style 
scientific paper with proper references.
"""

import os
import warnings
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

def get_gemini_llm():
    """Initialize and return the Gemini LLM"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables.\n"
            "Please create a .env file with your Google API key:\n"
            "GOOGLE_API_KEY=your_api_key_here"
        )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",  # or "gemini-1.5-flash", "gemini-1.5-pro"
        temperature=0.7,
        google_api_key=api_key
    )
    
    return llm

def create_agents(llm):
    """Create the three agents: Researcher, Writer, and Editor"""
    
    researcher = Agent(
        role="Scientific Researcher",
        goal="Research and gather comprehensive, factually accurate information on {topic} with proper citations",
        backstory=(
            "You are an expert scientific researcher with years of experience "
            "in academic research. You excel at finding relevant studies, data, "
            "and credible sources. You always track and format references in IEEE style. "
            "You gather information from recent publications, technical reports, "
            "and authoritative sources in the field of {topic}."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    writer = Agent(
        role="Scientific Paper Writer",
        goal="Write a well-structured IEEE-style scientific paper on {topic} with proper citations",
        backstory=(
            "You are an experienced academic writer specializing in IEEE-format papers. "
            "You craft clear, concise, and technically accurate papers following IEEE standards. "
            "You structure papers with: Abstract, Introduction, Related Work, Methodology, "
            "Results/Discussion, Conclusion, and References. You use formal academic language "
            "and cite sources using IEEE citation format [1], [2], etc. "
            "You work closely with the researcher's findings to create compelling content."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    editor = Agent(
        role="Technical Editor",
        goal="Review and refine the scientific paper to meet IEEE publication standards",
        backstory=(
            "You are a meticulous technical editor for IEEE publications. "
            "You ensure papers meet IEEE formatting standards, have proper grammar, "
            "clear technical writing, accurate citations, and logical flow. "
            "You check for consistency in terminology, proper section structure, "
            "and that all claims are supported by citations. You maintain the formal "
            "academic tone required for IEEE papers."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    return researcher, writer, editor

def create_tasks(researcher, writer, editor):
    """Create the three tasks: Research, Write, and Edit"""
    
    research_task = Task(
        description=(
            "1. Research the latest developments, key findings, and important work on {topic}.\n"
            "2. Identify 5-10 credible sources including recent papers, technical reports, and authoritative publications.\n"
            "3. For each source, note: Authors, Title, Publication/Conference, Year, and key findings.\n"
            "4. Format references in IEEE style: [1] A. Author, 'Title,' Journal, vol. X, no. Y, pp. Z, Year.\n"
            "5. Create a comprehensive research brief with:\n"
            "   - Key concepts and definitions\n"
            "   - Current state of the art\n"
            "   - Research gaps or challenges\n"
            "   - Recent innovations or breakthroughs\n"
            "   - List of formatted IEEE references"
        ),
        expected_output=(
            "A detailed research document containing:\n"
            "- Summary of key concepts\n"
            "- Overview of current research landscape\n"
            "- 5-10 IEEE-formatted references with brief descriptions\n"
            "- Key technical points to address in the paper"
        ),
        agent=researcher
    )
    
    write_task = Task(
        description=(
            "Using the research findings, write a complete IEEE-style scientific paper on {topic}.\n\n"
            "Structure:\n"
            "1. Title - Clear and descriptive\n"
            "2. Abstract (150-200 words) - Concise summary of the paper\n"
            "3. Introduction - Context, motivation, and paper contributions\n"
            "4. Related Work - Survey of existing research with citations\n"
            "5. Methodology/Approach - Technical details and methods\n"
            "6. Results and Discussion - Findings and their implications\n"
            "7. Conclusion - Summary and future work\n"
            "8. References - IEEE-formatted citation list\n\n"
            "Requirements:\n"
            "- Use formal academic language\n"
            "- Include in-text citations as [1], [2], etc.\n"
            "- Each section should be 2-4 paragraphs\n"
            "- Technical accuracy is paramount\n"
            "- Follow IEEE formatting conventions\n"
            "- Minimum 5 properly cited references"
        ),
        expected_output=(
            "A complete IEEE-style scientific paper in markdown format with:\n"
            "- All required sections properly formatted\n"
            "- In-text citations throughout\n"
            "- Complete reference list in IEEE format\n"
            "- Professional academic tone\n"
            "- Ready for submission to an IEEE conference or journal"
        ),
        agent=writer
    )
    
    edit_task = Task(
        description=(
            "Review and edit the scientific paper to ensure it meets IEEE publication standards.\n\n"
            "Check for:\n"
            "1. Proper IEEE paper structure and formatting\n"
            "2. Grammatical correctness and clarity\n"
            "3. Technical accuracy and consistency\n"
            "4. All claims are properly cited\n"
            "5. Citations are in correct IEEE format [1], [2], etc.\n"
            "6. Reference list is complete and properly formatted\n"
            "7. Abstract is concise and informative\n"
            "8. Logical flow between sections\n"
            "9. Professional academic tone throughout\n"
            "10. No informal language or unsupported claims"
        ),
        expected_output=(
            "A polished, publication-ready IEEE-style scientific paper with:\n"
            "- Perfect grammar and formatting\n"
            "- Consistent technical terminology\n"
            "- Properly formatted citations and references\n"
            "- Clear, professional academic writing\n"
            "- Ready for IEEE journal or conference submission"
        ),
        agent=editor
    )
    
    return research_task, write_task, edit_task

def main():
    """Main execution function"""
    
    print("="*80)
    print("IEEE SCIENTIFIC PAPER WRITER")
    print("Powered by Google Gemini and CrewAI")
    print("="*80)
    print()
    
    # Get topic from user
    topic = input("Enter the research topic for your paper: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty!")
        return
    
    print(f"\n📚 Generating IEEE-style scientific paper on: {topic}")
    print("This may take several minutes...\n")
    
    try:
        # Initialize Gemini LLM
        print("🔧 Initializing Gemini model...")
        llm = get_gemini_llm()
        
        # Create agents
        print("👥 Creating AI agents (Researcher, Writer, Editor)...")
        researcher, writer, editor = create_agents(llm)
        
        # Create tasks
        print("📋 Setting up research, writing, and editing tasks...")
        research_task, write_task, edit_task = create_tasks(researcher, writer, editor)
        
        # Create crew
        print("🚀 Assembling the crew and starting work...\n")
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, write_task, edit_task],
            verbose=2
        )
        
        # Execute
        result = crew.kickoff(inputs={"topic": topic})
        
        # Save output
        output_filename = f"ieee_paper_{topic.replace(' ', '_').lower()}.md"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n" + "="*80)
        print("✅ PAPER GENERATION COMPLETE!")
        print("="*80)
        print(f"\n📄 Paper saved to: {output_filename}")
        print("\nPreview of the paper:")
        print("-"*80)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("-"*80)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
