import logging
import re
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)


class PDFExporter:
    """
    Exports markdown reports to PDF format using ReportLab.
    Pure Python solution with no external system dependencies.
    """
    
    # Custom styles for better formatting
    STYLES = getSampleStyleSheet()
    
    @staticmethod
    def _create_custom_styles():
        """Create custom paragraph styles for the report."""
        styles = getSampleStyleSheet()
        
        # Main title
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#3498db'),
            borderWidth=2,
            borderPadding=8
        ))
        
        # Subsection heading
        styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#5d6d7b'),
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Normal paragraph with better spacing
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Bullet list
        styles.add(ParagraphStyle(
            name='BulletStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            leftIndent=20,
            spaceAfter=4,
            bulletIndent=10
        ))
        
        return styles
    
    @staticmethod
    def _markdown_to_reportlab_elements(markdown_content: str, styles) -> List:
        """
        Convert markdown content to ReportLab elements.
        
        Args:
            markdown_content: Markdown text
            styles: ReportLab styles
            
        Returns:
            List of ReportLab elements
        """
        logger.debug(f"Converting markdown to ReportLab elements")
        
        elements = []
        lines = markdown_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines (but add spacer for visual separation)
            if not line.strip():
                elements.append(Spacer(1, 0.1*inch))
                i += 1
                continue
            
            # H1 heading (# )
            if line.startswith('# '):
                heading_text = line[2:].strip()
                elements.append(Paragraph(heading_text, styles['CustomTitle']))
                elements.append(Spacer(1, 0.15*inch))
                i += 1
                
            # H2 heading (## )
            elif line.startswith('## '):
                heading_text = line[3:].strip()
                elements.append(Paragraph(heading_text, styles['CustomHeading2']))
                elements.append(Spacer(1, 0.1*inch))
                i += 1
                
            # H3 heading (### )
            elif line.startswith('### '):
                heading_text = line[4:].strip()
                elements.append(Paragraph(heading_text, styles['CustomHeading3']))
                elements.append(Spacer(1, 0.08*inch))
                i += 1
                
            # Horizontal rule (---)
            elif line.strip() == '---':
                elements.append(Spacer(1, 0.2*inch))
                i += 1
                
            # Bullet points (- or *)
            elif line.strip().startswith(('- ', '* ')):
                bullet_text = line.strip()[2:].strip()
                # Clean up any markdown formatting
                bullet_text = bullet_text.replace('**', '').replace('__', '')
                # Use a table for proper bullet formatting
                elements.append(Paragraph(f"• {bullet_text}", styles['BulletStyle']))
                i += 1
                
            # Numbered lists
            elif re.match(r'^\d+\.', line.strip()):
                list_item = re.sub(r'^\d+\.\s', '', line.strip())
                list_item = list_item.replace('**', '').replace('__', '')
                elements.append(Paragraph(f"{line.strip()[0]}. {list_item}", styles['BulletStyle']))
                i += 1
                
            # Code block (triple backticks)
            elif line.strip().startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # Skip closing ```
                
                code_text = '\n'.join(code_lines)
                # Create code block with background
                from reportlab.platypus import Table, TableStyle
                code_table = Table(
                    [[Paragraph(f"<font face='Courier' size='9'>{code_text}</font>", styles['Normal'])]],
                    colWidths=[7.5*inch]
                )
                code_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f4f4f4')),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
                ]))
                elements.append(code_table)
                elements.append(Spacer(1, 0.1*inch))
                continue
                
            # Bold and italic cleanup, then add as regular paragraph
            else:
                # Clean markdown formatting
                text = line.strip()
                text = text.replace('**', '<b>').replace('__', '<b>')
                text = text.replace('*', '<i>').replace('_', '<i>')
                
                if text:
                    try:
                        elements.append(Paragraph(text, styles['CustomBody']))
                    except Exception as e:
                        logger.warning(f"Could not parse line: {text}, error: {e}")
                        elements.append(Paragraph(line.strip(), styles['Normal']))
                
                i += 1
        
        return elements
    
    @staticmethod
    def export(
        markdown_content: str,
        output_path: Path,
        title: str = "Assessment Report"
    ) -> bool:
        """
        Export markdown to PDF using ReportLab.
        
        Args:
            markdown_content: Markdown text to export
            output_path: Path where PDF should be saved
            title: Document title
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Exporting to PDF: {output_path}")
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title=title
            )
            
            # Create custom styles
            styles = PDFExporter._create_custom_styles()
            
            # Convert markdown to reportlab elements
            elements = PDFExporter._markdown_to_reportlab_elements(markdown_content, styles)
            
            # Add timestamp footer
            elements.append(Spacer(1, 0.3*inch))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elements.append(Paragraph(
                f"<font size='8' color='gray'>Generated: {timestamp}</font>",
                styles['Normal']
            ))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"PDF export successful: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}", exc_info=True)
            return False
    
    @staticmethod
    def export_markdown(
        markdown_content: str,
        output_path: Path
    ) -> bool:
        """
        Export markdown to file.
        
        Args:
            markdown_content: Markdown text to export
            output_path: Path where markdown should be saved
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Exporting markdown: {output_path}")
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown export successful: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting markdown: {e}", exc_info=True)
            return False
