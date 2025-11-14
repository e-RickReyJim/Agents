# Migration Guide - Refactored Architecture

## Overview

The project has been refactored from a single 698-line monolithic file into a modular architecture with ~15 specialized modules. This document explains the changes and how to use the new structure.

## What Changed

### Before (Monolithic)
```
scientific_paper_writer.py (698 lines)
├── All configuration
├── All agents
├── All tasks
├── All tools
├── All services
└── Main execution
```

### After (Modular)
```
src/
├── config/          # Configuration (citation formats, settings)
├── agents/          # Agent definitions (researcher, writer, editor, rag)
├── tasks/           # Task definitions (research, writing)
├── tools/           # CrewAI tools (web search, RAG search)
├── services/        # Business logic (LLM, crew, export)
├── rag/             # RAG system (FAISS indexing)
└── utils/           # Utilities (input handling)

scripts/
├── paper_writer.py  # Main entry point (NEW!)
└── rag_setup.py     # RAG indexing (moved from root)
```

## Breaking Changes

### 1. Main Entry Point Changed

❌ **Old Way**:
```powershell
python scientific_paper_writer.py
```

✅ **New Way**:
```powershell
python scripts/paper_writer.py
```

### 2. RAG Setup Moved

❌ **Old Way**:
```powershell
python rag_setup.py
```

✅ **New Way**:
```powershell
python scripts/rag_setup.py
```

### 3. Import Paths Changed (for developers extending the code)

❌ **Old Way**:
```python
from scientific_paper_writer import create_agents, create_tasks
from rag_utils import RAGSystem
```

✅ **New Way**:
```python
from src.agents.researcher import WebResearcherAgent
from src.agents.writer import WriterAgent
from src.rag.rag_system import RAGSystem
from src.services.crew_service import CrewService
```

## New File Locations

| Old Location | New Location | Purpose |
|-------------|--------------|---------|
| `scientific_paper_writer.py` (lines 28-50) | `src/config/citation_formats.py` | Citation format templates |
| `scientific_paper_writer.py` (lines 134-151) | `src/services/llm_service.py` | LLM initialization |
| `scientific_paper_writer.py` (lines 155-248) | `src/agents/*.py` | Agent definitions |
| `scientific_paper_writer.py` (lines 250-393) | `src/tasks/*.py` | Task definitions |
| `scientific_paper_writer.py` (lines 53-131) | `src/tools/*.py` | CrewAI tools |
| `scientific_paper_writer.py` (lines 396-536) | `src/services/export_service.py` | Export service |
| `rag_utils.py` | `src/rag/rag_system.py` | RAG system |
| `rag_setup.py` | `scripts/rag_setup.py` | RAG setup script |

## Benefits of New Structure

### 1. Maintainability
- Each file is 50-100 lines (vs 698)
- Easy to find specific functionality
- Clear separation of concerns

### 2. Testability
```powershell
# Run tests for specific components
pytest tests/test_tools.py
pytest tests/test_agents.py
pytest tests/test_services.py
```

### 3. Reusability
```python
# Import only what you need
from src.agents.researcher import WebResearcherAgent
from src.config.citation_formats import CITATION_FORMATS

# Use in your own project
llm = get_llm()
researcher = WebResearcherAgent.create(llm, CITATION_FORMATS['IEEE'])
```

### 4. Extensibility
Add new features without touching existing code:

**Add New Citation Format**:
```python
# Edit src/config/citation_formats.py only
CITATION_FORMATS['MLA'] = {
    'name': 'MLA 9th',
    # ...
}
```

**Add New Agent**:
```python
# Create src/agents/proofreader.py
class ProofreaderAgent:
    @staticmethod
    def create(llm, citation_format):
        # ...
```

## Configuration Changes

### Settings Centralized

All settings now in `src/config/settings.py`:

```python
class Settings:
    # API Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash'
    TEMPERATURE = 0.7
    MAX_RETRIES = 5
    REQUEST_TIMEOUT = 180
    
    # RAG Configuration
    PDF_LIBRARY_PATH = './pdf_library'
    RAG_DB_PATH = './rag_db'
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 5
    
    # Output Configuration
    OUTPUT_DIR = './outputs/papers'
    LOG_DIR = './outputs/logs'
```

### Environment Variables

No changes to `.env` file:
```env
GOOGLE_API_KEY=your_key_here
```

## Testing the Refactored Code

### 1. Verify Imports
```powershell
python -c "from src.config.settings import Settings; print('✅ Imports OK')"
```

### 2. Generate Test Paper
```powershell
python scripts/paper_writer.py
```

Follow prompts:
- Format: IEEE
- Topic: "Machine learning"
- Filename: "test_paper"
- RAG: No
- PDF: Yes

### 3. Run Unit Tests
```powershell
pytest tests/ -v
```

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Ensure you're in the project root directory:
```powershell
cd c:\GIT\Agents
python scripts/paper_writer.py
```

### Old Files Still Present

Backup files created:
- `scientific_paper_writer_OLD.py` - Original monolithic file
- `rag_utils.py` - Original RAG utilities
- `README_OLD.md` - Original README

You can safely delete these after verifying the new system works.

### Path Issues

The new structure uses relative imports. Always run from project root:
```powershell
# ✅ Correct (from project root)
cd c:\GIT\Agents
python scripts/paper_writer.py

# ❌ Incorrect (from scripts folder)
cd c:\GIT\Agents\scripts
python paper_writer.py  # Will fail with import errors
```

## Rollback Procedure

If you need to revert to the old monolithic version:

```powershell
# Restore old file
Copy-Item scientific_paper_writer_OLD.py scientific_paper_writer.py

# Run old way
python scientific_paper_writer.py
```

## Migration Checklist

- [ ] Virtual environment activated
- [ ] Dependencies up to date: `pip install -r requirements.txt`
- [ ] `.env` file with `GOOGLE_API_KEY` exists
- [ ] Test imports: `python -c "from src.config.settings import Settings"`
- [ ] Generate test paper: `python scripts/paper_writer.py`
- [ ] Verify outputs in `outputs/papers/`
- [ ] Run unit tests: `pytest tests/`
- [ ] Update any custom scripts using old imports
- [ ] Delete backup files (optional): `*_OLD.py`, `rag_utils.py`

## Questions?

If you encounter issues:
1. Check this migration guide
2. Review error messages carefully
3. Ensure virtual environment is activated
4. Verify working directory is project root
5. Check that all imports use new `src/` structure

## Next Steps

With the refactored architecture, you can:
- **Add Features**: Create new agents/services without touching existing code
- **Run Tests**: Ensure quality with unit tests
- **Extend Citation Formats**: Easy to add MLA, Chicago, etc.
- **Improve Components**: Refactor individual modules independently
- **Build on Top**: Import specific components in your own projects

---

**Refactoring Complete!** 🎉

Original: 698-line monolithic file  
New: ~15 modular files, fully tested, production-ready
