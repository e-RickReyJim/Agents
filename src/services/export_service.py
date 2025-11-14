"""Export Service for converting and saving papers"""

import os
from datetime import datetime
from pathlib import Path
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

from ..config.settings import Settings


class ExportService:
    """Service for exporting papers to markdown and PDF formats"""
    
    def __init__(self):
        """Initialize export service with settings"""
        self.settings = Settings
    
    def save_markdown(
        self,
        content: str,
        filename: str,
        citation_format: str
    ) -> str:
        """
        Save paper content to markdown file.
        
        Args:
            content: Paper content in markdown format
            filename: Output filename (without extension)
            citation_format: Citation format name (for metadata)
        
        Returns:
            Path to saved markdown file
        """
        # Ensure output directory exists
        output_dir = Path(self.settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean filename
        filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
        if not filename.endswith('.md'):
            filename += '.md'
        
        md_path = output_dir / filename
        
        # Add metadata header
        metadata = f"""<!-- 
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Format: {citation_format}
-->

"""
        
        # Write file
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(metadata + content)
        
        return str(md_path)
    
    def markdown_to_pdf(
        self,
        markdown_content: str,
        output_path: str,
        citation_format: str
    ) -> bool:
        """
        Convert markdown to PDF with proper formatting (Windows-compatible).
        
        Args:
            markdown_content: Paper content in markdown format
            output_path: Output PDF file path
            citation_format: Citation format name (for footer)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # Define styles
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name='Justify',
                alignment=TA_JUSTIFY,
                fontSize=12,
                fontName='Times-Roman',
                leading=14
            ))
            styles.add(ParagraphStyle(
                name='PaperTitle',
                alignment=TA_CENTER,
                fontSize=18,
                fontName='Times-Bold',
                spaceAfter=30
            ))
            styles.add(ParagraphStyle(
                name='PaperHeading',
                fontSize=14,
                fontName='Times-Bold',
                spaceAfter=12,
                spaceBefore=12
            ))
            
            story = []
            
            # Parse markdown content line by line
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
                    text = (line
                           .replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;'))
                    story.append(Paragraph(text, styles['Justify']))
            
            # Add footer
            footer_style = ParagraphStyle(
                name='Footer',
                fontSize=10,
                alignment=TA_CENTER,
                textColor='gray'
            )
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y')} | Format: {citation_format}",
                footer_style
            ))
            
            # Build PDF
            doc.build(story)
            return True
        
        except Exception as e:
            print(f"⚠️  PDF generation failed: {e}")
            print("   Markdown file saved successfully.")
            return False
    
    def export_paper(
        self,
        content: str,
        filename: str,
        citation_format: str,
        export_pdf: bool = True
    ) -> dict:
        """
        Export paper to markdown and optionally PDF.
        
        Args:
            content: Paper content in markdown format
            filename: Output filename (without extension)
            citation_format: Citation format name
            export_pdf: Whether to also export PDF
        
        Returns:
            Dictionary with paths: {'markdown': path, 'pdf': path or None}
        """
        # Save markdown
        md_path = self.save_markdown(content, filename, citation_format)
        print(f"\n✅ Markdown saved: {md_path}")
        
        result = {'markdown': md_path, 'pdf': None}
        
        # Export PDF if requested
        if export_pdf:
            pdf_filename = filename.replace('.md', '') + '.pdf'
            pdf_path = Path(self.settings.OUTPUT_DIR) / pdf_filename
            
            print(f"\n📄 Generating PDF: {pdf_path}")
            success = self.markdown_to_pdf(content, str(pdf_path), citation_format)
            
            if success:
                print(f"✅ PDF saved: {pdf_path}")
                result['pdf'] = str(pdf_path)
            else:
                print("❌ PDF generation failed")
        
        return result
