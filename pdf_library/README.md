# PDF Library

Place your PDF files here to use with RAG (Retrieval-Augmented Generation).

## Instructions

1. Copy PDF files to this folder
2. Run: `python rag_setup.py`
3. Run: `python scientific_paper_writer.py`
4. Answer `y` when prompted to use local PDF library

## Supported Files

- Any PDF with extractable text (not scanned images)
- Academic papers, reports, theses, books, etc.
- No password-protected PDFs

## Examples

```
pdf_library/
├── Smith_ML_2023.pdf
├── Doe_AI_Review_2024.pdf
├── Johnson_DataScience_2022.pdf
└── ...
```

## See Also

- [RAG_GUIDE.md](../RAG_GUIDE.md) - Complete guide
- `rag_setup.py` - Indexing script
- `rag_utils.py` - Helper functions
