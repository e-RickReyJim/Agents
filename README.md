# Advanced Scientific Paper Writer

An AI-powered tool that generates professional scientific papers in multiple citation formats using Google Gemini and CrewAI framework.

---

## 🌟 Key Features

- **📚 Multiple Citation Formats** - IEEE, APA 7th, Vancouver
- **🔍 Real Web Search** - Finds actual academic papers using CrossRef API
- **�️ RAG (Local PDF Search)** - Search your own PDF library (NEW!)
- **�📄 PDF Export** - Professional PDF generation (Windows-compatible)
- **🤖 Three AI Agents** - Researcher, Writer, and Editor working together
- **🎯 Publication-Ready Output** - Properly structured papers with real references
- **💰 100% Free RAG** - Local embeddings, no additional API costs

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))
- Virtual environment (already set up if you completed setup)

### 2. Installation

```powershell
# Navigate to project directory
cd c:\GIT\Agents

# Install dependencies
pip install -r requirements.txt

# Verify setup
python test_setup.py
```

### 3. Configure API Key

Create a `.env` file with your Google Gemini API key:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

**To get your API key:**
1. Visit https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file

### 4. (Optional) Setup RAG for Local PDF Search

**NEW FEATURE!** Search your own PDF library:

```powershell
# Install RAG dependencies
pip install pypdf sentence-transformers faiss-cpu numpy

# Create folder and add your PDFs
mkdir pdf_library
# Copy your PDF files to ./pdf_library/

# Index your PDFs (one-time setup)
python rag_setup.py
```

**See [RAG_GUIDE.md](RAG_GUIDE.md) for complete instructions.**

### 5. Run the Script

```powershell
python scientific_paper_writer.py
```

**You'll be prompted for:**
1. **Citation format** - Type `1` (IEEE), `2` (APA), or `3` (Vancouver)
2. **Research topic** - e.g., "Machine Learning in Healthcare"
3. **Use local PDFs?** - Type `y` to include your PDF library (if RAG setup)
4. **PDF export** - Type `y` or `n` when asked

**Output:**
- Markdown file: `paper_<format>_<topic>.md`
- PDF file: `paper_<format>_<topic>.pdf` (if you chose yes)

---

## 📋 Citation Formats Explained

### IEEE (Institute of Electrical and Electronics Engineers)
- **In-text citations:** `[1]`, `[2]`, `[3]`
- **Reference format:** `[1] A. Author and B. Coauthor, "Article Title," Journal Name, vol. 10, no. 2, pp. 123-456, 2023.`
- **Best for:** Engineering, Computer Science, Electronics

### APA 7th (American Psychological Association)
- **In-text citations:** `(Smith, 2023)`, `(Smith & Doe, 2023)`
- **Reference format:** `Smith, J., & Doe, A. (2023). Article title. Journal Name, 10(2), 123-456.`
- **Best for:** Psychology, Social Sciences, Education

### Vancouver (International Committee of Medical Journal Editors)
- **In-text citations:** `(1)`, `(2)`, `(3)`
- **Reference format:** `1. Smith J, Doe A. Article title. Journal Name. 2023;10(2):123-456.`
- **Best for:** Medicine, Health Sciences, Biomedical Research

---

## 📖 Paper Structure

Generated papers include all required sections:

1. **Title** - Clear and descriptive
2. **Abstract** - 150-200 word summary
3. **Introduction** - Context, motivation, and contributions
4. **Literature Review** - Survey of existing research with citations
5. **Methodology** - Technical approach and methods
6. **Results and Discussion** - Findings and their implications
7. **Conclusion** - Summary and future work
8. **References** - Properly formatted citation list (5-7 real sources)

---

## 🔧 How It Works

### Three AI Agents Work Together

1. **🔬 Researcher Agent**
   - Searches CrossRef API for real academic papers
   - (Optional) Searches your local PDF library with RAG
   - Extracts: authors, titles, journals, years, DOIs
   - Formats references in selected citation style
   - Provides research brief to Writer

2. **✍️ Writer Agent**
   - Receives research findings
   - Writes complete paper with proper structure
   - Includes in-text citations
   - Creates comprehensive content

3. **📝 Editor Agent**
   - Reviews paper for format compliance
   - Checks grammar and clarity
   - Verifies citation consistency
   - Ensures publication standards

### Web Search Integration

- **API Used:** CrossRef REST API (free, no key needed)
- **Search Process:** Finds 5-7 recent academic papers on your topic
- **Data Extracted:** Full publication details
- **Auto-Formatting:** Citations formatted per selected style

### RAG (Local PDF Search) Integration

- **Technology:** Sentence-transformers + FAISS (100% local, free)
- **Setup:** One-time indexing of your PDF library
- **Search:** Semantic search across your documents
- **Results:** Top 5 relevant excerpts with page numbers
- **Citations:** Mixed with web sources in selected format
- **Cost:** FREE - no API calls for local search
- **Guide:** See [RAG_GUIDE.md](RAG_GUIDE.md) for setup

---

## 🎯 Project Structure

```
c:\GIT\Agents\
├── scientific_paper_writer.py  # Main script ⭐ (use this)
├── rag_setup.py               # RAG one-time indexing script (NEW!)
├── rag_utils.py               # RAG helper functions (NEW!)
├── ieee_paper_writer.py        # Original IEEE-only version
├── test_setup.py              # Setup validator
├── requirements.txt           # All dependencies
├── .env                       # Your API key (keep private)
├── .env.example              # Template
├── README.md                 # This file
├── RAG_GUIDE.md              # Complete RAG setup guide (NEW!)
├── pdf_library/              # Your PDF files (create manually)
└── rag_db/                   # RAG index (auto-created)
```

### Scripts Comparison

| Feature | scientific_paper_writer.py ⭐ | ieee_paper_writer.py |
|---------|------------------------------|---------------------|
| Citation formats | IEEE, APA, Vancouver | IEEE only |
| Web search | ✅ CrossRef API | ❌ General knowledge |
| PDF export | ✅ ReportLab | ❌ Markdown only |
| References | Real academic papers | Simulated |
| Speed | 5-10 minutes | 3-5 minutes |
| Best for | Production use | Quick testing |

---

## 📦 Dependencies

```
crewai==0.28.8              # AI agent framework
crewai_tools==0.1.6         # Agent tools
langchain-core==0.1.53      # LangChain core
langchain-google-genai==0.0.11  # Gemini integration
python-dotenv>=1.0.0        # Environment variables
markdown>=3.5               # Markdown processing
requests>=2.31.0            # Web API calls
reportlab>=4.0.0            # PDF generation (Windows-compatible)
```

---

## 🚦 Understanding Rate Limits

### What You'll See

```
WARNING: Retrying in 2.0 seconds as it raised ResourceExhausted...
```

**This is NORMAL!** The free tier has limits, and the script handles them automatically.

### Free Tier Limits

| Metric | Free Tier | Your Usage |
|--------|-----------|------------|
| Requests per minute | 15 | ~17 (3 agents) |
| Tokens per minute | 1,000,000 | ~100,000 |
| Requests per day | 1,500 | ~20 per paper |

### How Rate Limiting Works

1. Script makes API calls
2. Hits 15 req/min limit → `429 Error`
3. **Automatically waits** 2-5 seconds
4. **Retries** up to 3 times
5. Continues until completion

**Expected time:** 5-10 minutes per paper

### Your Script Has Built-in Handling

✅ Automatic retry logic (max 3 attempts)  
✅ Extended timeout (120 seconds)  
✅ User notifications when retrying  
✅ Smart waiting between calls

**Just be patient and let it complete!** ☕

### Upgrade Options (Optional)

**Google AI Studio Pro** (Pay-as-you-go):
- **60 requests/minute** (4x more)
- **4M tokens/minute**
- **Cost:** ~$0.02 per paper
- **Link:** https://console.cloud.google.com/

### Best Practices

- ✅ Run during off-peak hours
- ✅ Use simpler topics for faster generation
- ✅ IEEE format = fastest (simplest citations)
- ✅ Let the script retry automatically
- ❌ Don't restart if you see retry messages

---

## 📄 PDF Export (Windows)

### How It Works

Your script uses **ReportLab** for PDF generation - a pure Python library that works perfectly on Windows without external dependencies.

### PDF Features

- ✅ Professional formatting
- ✅ 1-inch margins on all sides
- ✅ Times Roman font (12pt)
- ✅ Bold section headings (14pt)
- ✅ Justified text alignment
- ✅ Page metadata (date, citation format)

### What Was Fixed

**Problem:** WeasyPrint needs GTK3 libraries (Linux/Mac) that are difficult on Windows

**Solution:** Script now uses ReportLab as primary PDF generator (Windows-compatible)

**Result:** PDF export works out of the box! 🎉

### Alternative PDF Tools (Optional)

If you want advanced formatting, you can also:

1. **Pandoc** (more features):
   ```powershell
   pandoc paper.md -o paper.pdf
   ```

2. **VS Code Extension**:
   - Install "Markdown PDF" extension
   - Right-click .md file → "Markdown PDF: Export (pdf)"

3. **WeasyPrint** (if you install GTK3):
   - Download: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
   - Install GTK3, then: `pip install weasyprint`

---

## ⚙️ Customization

### Change Gemini Model

Edit `scientific_paper_writer.py` (around line 102):

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # Options: "gemini-2.0-flash-exp", "gemini-1.5-flash"
    temperature=0.7,
    google_api_key=api_key
)
```

**Model Options:**
- `gemini-2.0-flash-exp` - Fastest, latest (default)
- `gemini-1.5-flash` - Balanced speed/quality
- `gemini-1.5-pro` - Highest quality, slower

### Adjust Creativity

```python
temperature=0.7,  # Range: 0.0 (deterministic) to 1.0 (creative)
```

- **0.0-0.3** - Focused, factual (good for technical papers)
- **0.5-0.7** - Balanced (default, recommended)
- **0.8-1.0** - Creative, varied (experimental)

### Add Custom Citation Format

Edit the `CITATION_FORMATS` dictionary in `scientific_paper_writer.py`:

```python
CITATION_FORMATS = {
    'IEEE': { ... },
    'APA': { ... },
    'Vancouver': { ... },
    'YOUR_FORMAT': {
        'name': 'Your Format Name',
        'description': 'Brief description',
        'in_text': '(N)',  # How citations appear in text
        'reference_format': 'Reference pattern',
        'example': 'Full example citation'
    }
}
```

---

## 🛠️ Troubleshooting

### Import Errors

```powershell
# Reinstall all packages with correct versions
pip install -r requirements.txt --upgrade
```

### API Key Not Found

```
❌ GOOGLE_API_KEY not found in environment variables
```

**Fix:**
1. Check `.env` file exists
2. Verify it contains: `GOOGLE_API_KEY=your_actual_key`
3. Key should start with `AIza`
4. No quotes around the value
5. No spaces around `=`

**Test it:**
```powershell
python test_setup.py
```

### PDF Generation Fails

If you see PDF errors:

```powershell
# Reinstall reportlab
pip uninstall reportlab
pip install reportlab>=4.0.0
```

### Rate Limit Errors (429)

```
429 Resource exhausted. Please try again later.
```

**This is expected!** The script will automatically retry. Just wait 5-10 minutes.

**To check your quota:**
- Visit https://aistudio.google.com/app/apikey
- View usage dashboard

### Web Search Not Working

If CrossRef is unavailable:
- Script falls back to general knowledge
- Consider using a paid API (Serper, SerpAPI) for better results
- Check internet connection

### Script Hangs or Stops

1. Check terminal for error messages
2. Verify API key is valid
3. Ensure you have internet connection
4. Try with a simpler topic first
5. Restart and try again

---

## 💡 Tips for Best Results

### Choose Clear, Specific Topics

✅ **Good:**
- "Machine Learning for Diabetes Diagnosis"
- "Quantum Computing in Cryptography"
- "IoT Security in Smart Homes"

❌ **Too Broad:**
- "Artificial Intelligence"
- "Healthcare Technology"
- "Computer Science"

### Optimal Topic Length

- **Ideal:** 3-7 words
- **Too short:** May lack context
- **Too long:** May hit rate limits faster

### Citation Format Selection

- **IEEE** - Fastest generation (simplest format)
- **Vancouver** - Medium speed
- **APA** - Slowest (most complex formatting)

### When to Use Each Script

**Use `scientific_paper_writer.py` when:**
- You need specific citation formats
- You want real academic references
- You need PDF output
- Quality > Speed

**Use `ieee_paper_writer.py` when:**
- You only need IEEE format
- Quick testing/prototyping
- Speed > References
- Learning how the system works

---

## 📚 Example Topics by Field

### Computer Science / AI
- Neural Networks for Image Recognition
- Blockchain Consensus Mechanisms
- Natural Language Processing in Chatbots
- Reinforcement Learning Applications

### Healthcare / Medicine
- Machine Learning in Cancer Detection
- Telemedicine During Pandemics
- AI-Assisted Surgical Robotics
- Personalized Medicine Using Genomics

### Engineering
- 5G Network Optimization
- IoT Security Protocols
- Renewable Energy Grid Integration
- Autonomous Vehicle Navigation Systems

### Environmental Science
- Climate Change Modeling with AI
- Satellite Imaging for Deforestation
- Ocean Acidification Monitoring
- Carbon Capture Technologies

---

## 📝 Usage Example

```powershell
# 1. Run the script
python scientific_paper_writer.py

# 2. You'll see:
================================================================================
ADVANCED SCIENTIFIC PAPER WRITER
Powered by Google Gemini and CrewAI
Features: Multiple citation formats, Web search, PDF export
================================================================================

Available citation formats:
  1. IEEE: IEEE - Institute of Electrical and Electronics Engineers
  2. APA: APA 7th - American Psychological Association (7th edition)
  3. Vancouver: Vancouver - International Committee of Medical Journal Editors

Select citation format (1-3 or IEEE/APA/Vancouver): 1

✅ Using IEEE format
   In-text: [N]

Enter the research topic: Machine Learning in Healthcare

📚 Generating IEEE-style scientific paper on: Machine Learning in Healthcare
🔍 Will search the web for real academic references...
⏳ This may take several minutes...

# 3. Wait 5-10 minutes while agents work...

# 4. When complete:
================================================================================
✅ PAPER GENERATION COMPLETE!
================================================================================

📄 Markdown saved to: paper_ieee_machine_learning_in_healthcare.md

📥 Export to PDF? (y/n): y

🔄 Converting to PDF...
✅ PDF saved to: paper_ieee_machine_learning_in_healthcare.pdf
```

---

## 🎓 Educational Use

This tool is designed for:
- ✅ Learning about AI agents and automation
- ✅ Understanding scientific paper structure
- ✅ Exploring different citation formats
- ✅ Generating initial drafts for research
- ✅ Educational and research purposes

**Note:** Always review and verify generated content before submission. AI-generated papers should be edited and fact-checked by humans.

---

## 🤝 Contributing & Support

### Report Issues

If you encounter problems:
1. Check this README's troubleshooting section
2. Run `python test_setup.py` to verify configuration
3. Check error messages carefully
4. Ensure dependencies are up to date

### Improve the Code

Feel free to modify and enhance:
- Add new citation formats
- Improve web search functionality
- Enhance PDF formatting
- Add more agent capabilities

---

## 📄 License

This project is for educational and research purposes. Generated papers should be reviewed and edited before any formal submission or publication.

---

## 🙏 Credits

- **Powered by:** [Google Gemini](https://ai.google.dev/)
- **Framework:** [CrewAI](https://www.crewai.com/)
- **LLM Integration:** [LangChain](https://www.langchain.com/)
- **References API:** [CrossRef](https://www.crossref.org/)
- **PDF Generation:** [ReportLab](https://www.reportlab.com/)

---

## 🎯 Summary

You now have a complete scientific paper writing system with:

✅ Multiple citation formats (IEEE, APA, Vancouver)  
✅ Real academic references from web search  
✅ Professional PDF export  
✅ AI-powered research, writing, and editing  
✅ Publication-ready output  
✅ Windows-compatible  
✅ Free tier friendly with automatic rate limit handling

**Everything is set up and ready to generate professional scientific papers!** 🚀📚

---

**Happy paper writing! If you have questions, refer to the troubleshooting section above.**
