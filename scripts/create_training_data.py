"""
Create Training Data from PubMed Central
Fetches papers about CKD, AI/ML, and prediction models for fine-tuning
"""

import json
import requests
import time
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import List, Dict, Optional


class PubMedDataCollector:
    """Fetch and process papers from PubMed Central"""
    
    # Q1 High-Impact Journals in Medicine/AI (JCR Quartile 1)
    Q1_JOURNALS = [
        "Nature", "Science", "The Lancet", "New England Journal of Medicine",
        "JAMA", "BMJ", "Nature Medicine", "Nature Biotechnology",
        "Kidney International", "Journal of the American Society of Nephrology",
        "American Journal of Kidney Diseases", "Clinical Journal of the American Society of Nephrology",
        "Nature Machine Intelligence", "Nature Methods", "Cell",
        "The Lancet Digital Health", "npj Digital Medicine",
        "Journal of Medical Internet Research", "PLOS Medicine",
        "Artificial Intelligence in Medicine", "IEEE Journal of Biomedical and Health Informatics",
        "Journal of Biomedical Informatics", "Bioinformatics"
    ]
    
    def __init__(self, min_year: int = 2020, filter_q1: bool = True):
        """
        Initialize collector with quality filters.
        
        Args:
            min_year: Minimum publication year (default: 2020)
            filter_q1: Only include Q1 journals (default: True)
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = "reicardoreyji@unisabana.edu.co"
        self.tool = "scientific_paper_trainer"
        self.min_year = min_year
        self.filter_q1 = filter_q1
    
    def search_papers(
        self,
        query: str,
        max_results: int = 500,
        retstart: int = 0
    ) -> List[str]:
        """
        Search PubMed for papers matching query with year filter.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to fetch
            retstart: Starting index for pagination
            
        Returns:
            List of PubMed IDs
        """
        # Add year filter to query
        year_filter = f"({self.min_year}[PDAT] : 3000[PDAT])"
        full_query = f"{query} AND {year_filter}"
        
        print(f"🔍 Searching PubMed: '{query}' (>={self.min_year})...")
        
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": full_query,
            "retmax": max_results,
            "retstart": retstart,
            "retmode": "json",
            "tool": self.tool,
            "email": self.email
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            pmids = data.get("esearchresult", {}).get("idlist", [])
            count = data.get("esearchresult", {}).get("count", 0)
            
            print(f"✅ Found {count} papers, fetching {len(pmids)} IDs")
            return pmids
            
        except Exception as e:
            print(f"❌ Error searching PubMed: {e}")
            return []
    
    def fetch_paper_details(self, pmid: str) -> Optional[Dict]:
        """
        Fetch full paper details including abstract.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with paper details or None if error
        """
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "tool": self.tool,
            "email": self.email
        }
        
        try:
            response = requests.get(fetch_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            article = root.find(".//PubmedArticle")
            
            if article is None:
                return None
            
            # Extract title
            title_elem = article.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""
            
            # Extract abstract
            abstract_elem = article.find(".//Abstract/AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            # Extract authors
            authors = []
            for author in article.findall(".//Author"):
                lastname = author.find("LastName")
                forename = author.find("ForeName")
                if lastname is not None and forename is not None:
                    authors.append(f"{forename.text} {lastname.text}")
            
            # Extract year
            year_elem = article.find(".//PubDate/Year")
            year = year_elem.text if year_elem is not None else ""
            
            # Extract journal
            journal_elem = article.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else ""
            
            # Extract keywords
            keywords = []
            for keyword in article.findall(".//Keyword"):
                if keyword.text:
                    keywords.append(keyword.text)
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "year": year,
                "journal": journal,
                "keywords": keywords
            }
            
        except Exception as e:
            print(f"⚠️  Error fetching PMID {pmid}: {e}")
            return None
    
    def is_q1_journal(self, journal_name: str) -> bool:
        """
        Check if journal is in Q1 list (case-insensitive partial match).
        
        Args:
            journal_name: Name of the journal
            
        Returns:
            True if Q1 journal, False otherwise
        """
        if not journal_name:
            return False
        
        journal_lower = journal_name.lower()
        return any(q1.lower() in journal_lower for q1 in self.Q1_JOURNALS)
    
    def fetch_batch(
        self,
        pmids: List[str],
        batch_size: int = 10,
        delay: float = 0.5
    ) -> List[Dict]:
        """
        Fetch multiple papers with rate limiting and quality filters.
        
        Args:
            pmids: List of PubMed IDs
            batch_size: Number of papers to fetch per batch
            delay: Delay between requests (seconds)
            
        Returns:
            List of paper dictionaries
        """
        papers = []
        filtered_count = {"no_abstract": 0, "old_year": 0, "not_q1": 0}
        total = len(pmids)
        
        print(f"\n📥 Fetching {total} papers in batches of {batch_size}...")
        if self.filter_q1:
            print(f"   🎯 Filtering: Q1 journals only, Year >= {self.min_year}")
        else:
            print(f"   🎯 Filtering: Year >= {self.min_year}")
        
        for i, pmid in enumerate(pmids, 1):
            paper = self.fetch_paper_details(pmid)
            
            if not paper or not paper.get("abstract"):
                filtered_count["no_abstract"] += 1
                print(f"  [{i}/{total}] ⏭️  Skipped (no abstract)")
                continue
            
            # Check year filter
            try:
                year = int(paper.get("year", "0"))
                if year < self.min_year:
                    filtered_count["old_year"] += 1
                    print(f"  [{i}/{total}] ⏭️  Skipped (year {year} < {self.min_year})")
                    continue
            except ValueError:
                pass  # If year parsing fails, include it
            
            # Check Q1 filter
            if self.filter_q1 and not self.is_q1_journal(paper.get("journal", "")):
                filtered_count["not_q1"] += 1
                print(f"  [{i}/{total}] ⏭️  Skipped (not Q1: {paper['journal'][:40]}...)")
                continue
            
            # Paper passed all filters
            papers.append(paper)
            journal_display = paper['journal'][:40] if len(paper['journal']) > 40 else paper['journal']
            print(f"  [{i}/{total}] ✅ [{paper['year']}] {journal_display}")
            
            # Rate limiting
            if i % batch_size == 0:
                time.sleep(delay)
        
        print(f"\n✅ Successfully fetched {len(papers)} high-quality papers")
        print(f"📊 Filtered out:")
        print(f"   • No abstract: {filtered_count['no_abstract']}")
        print(f"   • Year < {self.min_year}: {filtered_count['old_year']}")
        if self.filter_q1:
            print(f"   • Not Q1 journal: {filtered_count['not_q1']}")
        
        return papers


class TrainingDataFormatter:
    """Format papers into instruction fine-tuning datasets"""
    
    @staticmethod
    def create_abstract_examples(papers: List[Dict]) -> List[Dict]:
        """Create training examples for writing abstracts"""
        examples = []
        
        for paper in papers:
            # Extract key topics from keywords/title
            topics = ", ".join(paper.get("keywords", [])[:3])
            if not topics:
                topics = "chronic kidney disease, machine learning"
            
            examples.append({
                "instruction": "Write an abstract for a scientific paper on the given topic.",
                "input": f"Topic: {topics}",
                "output": paper["abstract"][:1000]  # Limit length
            })
        
        return examples
    
    @staticmethod
    def create_introduction_examples(papers: List[Dict]) -> List[Dict]:
        """Create training examples for writing introductions"""
        examples = []
        
        for paper in papers:
            # Use first 2 sentences of abstract as "introduction style"
            sentences = paper["abstract"].split(". ")[:2]
            intro_style = ". ".join(sentences) + "."
            
            if len(intro_style) > 50:
                examples.append({
                    "instruction": "Write an introduction paragraph for a scientific paper.",
                    "input": f"Topic: {paper['title']}",
                    "output": intro_style
                })
        
        return examples
    
    @staticmethod
    def create_citation_examples(papers: List[Dict]) -> List[Dict]:
        """Create training examples for formatting citations"""
        examples = []
        
        for paper in papers:
            if not paper.get("authors") or not paper.get("year"):
                continue
            
            # IEEE format
            authors_str = ", ".join(paper["authors"][:3])
            if len(paper["authors"]) > 3:
                authors_str += " et al."
            
            ieee_citation = (
                f'[1] {authors_str}, "{paper["title"]}", '
                f'{paper["journal"]}, {paper["year"]}.'
            )
            
            examples.append({
                "instruction": "Format this reference in IEEE citation style.",
                "input": (
                    f"Authors: {', '.join(paper['authors'][:3])}. "
                    f"Title: {paper['title']}. "
                    f"Journal: {paper['journal']}. "
                    f"Year: {paper['year']}."
                ),
                "output": ieee_citation
            })
        
        return examples
    
    @staticmethod
    def create_methodology_examples(papers: List[Dict]) -> List[Dict]:
        """Create examples for methodology sections"""
        examples = []
        
        for paper in papers:
            # Look for methodology keywords in abstract
            abstract = paper["abstract"].lower()
            if any(word in abstract for word in ["method", "approach", "model", "algorithm", "dataset"]):
                examples.append({
                    "instruction": "Describe the methodology for this research study.",
                    "input": f"Research topic: {paper['title']}",
                    "output": paper["abstract"][:800]
                })
        
        return examples
    
    @staticmethod
    def create_results_examples(papers: List[Dict]) -> List[Dict]:
        """Create examples for results sections"""
        examples = []
        
        for paper in papers:
            # Look for results keywords
            abstract = paper["abstract"].lower()
            if any(word in abstract for word in ["results", "findings", "accuracy", "performance", "significant"]):
                examples.append({
                    "instruction": "Summarize the key findings and results of this study.",
                    "input": f"Study: {paper['title']}",
                    "output": paper["abstract"][:800]
                })
        
        return examples


def main():
    """Main execution function"""
    
    print("="*80)
    print("PUBMED TRAINING DATA CREATOR")
    print("Topic: CKD, AI/ML, Prediction Models")
    print("="*80)
    print()
    
    # Configuration options
    print("📋 Configuration Options:")
    print()
    
    # Year filter
    print("Minimum publication year?")
    print("  (Recommended: 2020 or later for recent AI/ML methods)")
    try:
        min_year = int(input("Enter year (default: 2020): ") or "2020")
    except ValueError:
        min_year = 2020
    
    # Q1 filter
    print("\nFilter for Q1 (high-impact) journals only?")
    print("  Q1 journals include: Nature, Lancet, JAMA, Kidney International, etc.")
    print("  Yes = Higher quality but fewer papers")
    print("  No = More papers but variable quality")
    filter_q1_input = input("Filter Q1 only? (y/n, default: y): ").strip().lower()
    filter_q1 = filter_q1_input != 'n'
    
    print()
    print("="*80)
    print(f"✅ Configuration:")
    print(f"   • Minimum Year: {min_year}")
    print(f"   • Q1 Filter: {'Enabled' if filter_q1 else 'Disabled'}")
    print("="*80)
    print()
    
    # Initialize collector with filters
    collector = PubMedDataCollector(min_year=min_year, filter_q1=filter_q1)
    
    # Define search queries for CKD + AI/ML
    queries = [
        "chronic kidney disease machine learning prediction",
        "CKD artificial intelligence diagnosis",
        "kidney disease deep learning model",
        "renal failure neural network prediction",
        "chronic kidney disease AI classification",
    ]
    
    # Collect papers
    all_pmids = []
    for query in queries:
        pmids = collector.search_papers(query, max_results=100)
        all_pmids.extend(pmids)
        time.sleep(1)  # Rate limiting between searches
    
    # Remove duplicates
    unique_pmids = list(set(all_pmids))
    print(f"\n📊 Total unique papers found: {len(unique_pmids)}")
    
    # Ask user how many to fetch
    print("\nHow many papers to fetch?")
    print("  Recommendation: 100-500 for good quality")
    print("  More papers = longer training time but better results")
    
    try:
        max_papers = int(input("\nEnter number (default: 200): ") or "200")
    except ValueError:
        max_papers = 200
    
    # Limit to requested amount
    pmids_to_fetch = unique_pmids[:max_papers]
    
    # Fetch paper details
    papers = collector.fetch_batch(pmids_to_fetch)
    
    if not papers:
        print("\n❌ No papers fetched. Please check your internet connection.")
        return
    
    print(f"\n✅ Successfully collected {len(papers)} papers")
    
    # Create training examples
    print("\n🔄 Generating training examples...")
    formatter = TrainingDataFormatter()
    
    training_data = []
    
    # Generate different types of examples
    training_data.extend(formatter.create_abstract_examples(papers))
    training_data.extend(formatter.create_introduction_examples(papers))
    training_data.extend(formatter.create_citation_examples(papers))
    training_data.extend(formatter.create_methodology_examples(papers))
    training_data.extend(formatter.create_results_examples(papers))
    
    print(f"✅ Generated {len(training_data)} training examples")
    
    # Save to file
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "training_data.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"📊 Total examples: {len(training_data)}")
    
    # Show sample
    print("\n" + "="*80)
    print("SAMPLE TRAINING EXAMPLE:")
    print("="*80)
    sample = training_data[0]
    print(f"\nInstruction: {sample['instruction']}")
    print(f"\nInput: {sample['input']}")
    print(f"\nOutput: {sample['output'][:200]}...")
    
    # Statistics
    print("\n" + "="*80)
    print("DATASET STATISTICS:")
    print("="*80)
    print(f"Total papers fetched: {len(papers)}")
    print(f"Total training examples: {len(training_data)}")
    print(f"Average examples per paper: {len(training_data)/len(papers):.1f}")
    
    # Count by instruction type
    instruction_types = {}
    for example in training_data:
        instr = example['instruction']
        instruction_types[instr] = instruction_types.get(instr, 0) + 1
    
    print("\nExamples by type:")
    for instr, count in instruction_types.items():
        print(f"  • {instr[:50]}... : {count}")
    
    print("\n" + "="*80)
    print("✅ TRAINING DATA CREATION COMPLETE!")
    print("="*80)
    print(f"\nNext steps:")
    print(f"1. Review the data in: {output_file}")
    print(f"2. Upload to Google Drive: Phi3_FineTuning/")
    print(f"3. Continue with Phase 4 of the fine-tuning guide")
    print()


if __name__ == "__main__":
    main()
