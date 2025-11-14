"""Web search tool for finding academic papers"""

import requests
from crewai_tools import tool


@tool("Web Search Tool")
def web_search_tool(query: str) -> str:
    """
    Search the web for recent academic papers and credible sources.
    Returns formatted results with titles, authors, and publication info.
    Uses CrossRef API for academic paper search.
    """
    try:
        # Using CrossRef API for academic paper search
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
