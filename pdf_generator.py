"""
PDF Report Generator for Sales Coach Analysis
Generates professional PDF reports containing analysis results and annotated transcripts.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import re
import io

class SalesCoachPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Set up custom paragraph styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb'),
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#1e40af'),
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8,
            backColor=colors.HexColor('#f8fafc')
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#374151')
        ))
        
        # Analysis content style
        self.styles.add(ParagraphStyle(
            name='AnalysisContent',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leftIndent=12
        ))
        
        # Annotation style
        self.styles.add(ParagraphStyle(
            name='AnnotationText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            fontName='Helvetica'
        ))
        
        # Coach comment style
        self.styles.add(ParagraphStyle(
            name='CoachComment',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leftIndent=20,
            textColor=colors.HexColor('#059669'),
            backColor=colors.HexColor('#f0fdf4'),
            borderWidth=1,
            borderColor=colors.HexColor('#bbf7d0'),
            borderPadding=6
        ))
    
    def clean_text_for_pdf(self, text):
        """Clean and format text for PDF generation"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Handle common markdown-style formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)      # Italic
        
        # Handle line breaks
        text = text.replace('\n\n', '<br/><br/>')
        text = text.replace('\n', '<br/>')
        
        return text
    
    def parse_analysis_content(self, analysis_text):
        """Parse analysis content into structured sections"""
        sections = []
        
        # More comprehensive section patterns to catch various formats
        section_patterns = [
            r'^##\s*(.*?)$',           # ## Section Header
            r'^###\s*(.*?)$',          # ### Subsection Header  
            r'^\*\*(.*?):\*\*',        # **Section:**
            r'^(\d+\.)\s*(.*?)$',      # 1. Numbered sections
            r'^[A-Z][A-Z\s]+:$',       # ALL CAPS HEADERS:
            r'^[A-Z].*?:$'             # Title Case Headers:
        ]
        
        current_section = None
        current_content = []
        
        lines = analysis_text.split('\n')
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Keep empty lines for spacing
            if not line:
                if current_content or current_section:
                    current_content.append('')
                continue
                
            # Check if this is a section header
            is_header = False
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous section if it exists
                    if current_section and (current_content or not sections):
                        sections.append({
                            'title': current_section,
                            'content': '\n'.join(current_content).strip()
                        })
                    
                    # Extract section title
                    if len(match.groups()) >= 1 and match.group(1):
                        current_section = match.group(1).strip()
                    else:
                        current_section = line.strip()
                    
                    # Clean up section title
                    current_section = re.sub(r'\*\*', '', current_section)  # Remove markdown bold
                    current_section = re.sub(r':$', '', current_section)    # Remove trailing colon
                    
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(original_line)
        
        # Add the last section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        # If no sections found or sections are empty, treat entire text as one section
        if not sections or all(not section['content'].strip() for section in sections):
            sections = [{
                'title': 'Complete Analysis Results',
                'content': analysis_text.strip()
            }]
        
        # Filter out empty sections
        sections = [section for section in sections if section['content'].strip()]
        
        return sections
    
    def parse_annotated_transcript(self, annotated_text):
        """Parse annotated transcript to separate dialogue and coaching comments"""
        parsed_content = []
        
        # Split by coaching comments (typically in brackets or marked)
        lines = annotated_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect coaching comments (various patterns)
            if (line.startswith('[COACH:') or line.startswith('**[COACH') or 
                line.startswith('COACHING NOTE:') or line.startswith('**COACHING') or
                'COACH INSIGHT:' in line or 'FEEDBACK:' in line):
                
                # This is a coaching comment
                clean_comment = re.sub(r'\[COACH:?\s*', '', line)
                clean_comment = re.sub(r'\*\*\[?COACH.*?:\s*', '', clean_comment)
                clean_comment = re.sub(r'COACHING NOTE:\s*', '', clean_comment)
                clean_comment = re.sub(r'\]$', '', clean_comment)
                clean_comment = re.sub(r'\*\*$', '', clean_comment)
                
                parsed_content.append({
                    'type': 'coaching',
                    'content': clean_comment.strip()
                })
            else:
                # This is regular transcript content
                parsed_content.append({
                    'type': 'dialogue',
                    'content': line
                })
        
        return parsed_content
    
    def generate_pdf_report(self, analysis_content, annotated_transcript, transcript_original=""):
        """Generate a complete PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title page
        story.append(Paragraph("Sales Call Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Report info
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        info_data = [
            ['Report Generated:', report_date],
            ['Analysis Type:', 'Sales Call Coaching'],
            ['Tool:', 'Sales Coach AI']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Executive Summary section
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Paragraph(
            "This report provides comprehensive analysis and coaching feedback for a sales call transcript. "
            "The analysis includes performance insights, improvement recommendations, and annotated feedback "
            "throughout the conversation.",
            self.styles['AnalysisContent']
        ))
        story.append(Spacer(1, 20))
        
        # Analysis Results section
        story.append(Paragraph("Detailed Analysis Results", self.styles['SectionHeader']))
        
        # Parse and format analysis content
        print(f"📄 Raw analysis content length: {len(analysis_content)}")
        print(f"📄 First 200 chars: {analysis_content[:200]}")
        
        analysis_sections = self.parse_analysis_content(analysis_content)
        print(f"📄 Parsed into {len(analysis_sections)} sections")
        
        for i, section in enumerate(analysis_sections):
            print(f"📄 Section {i+1}: '{section['title']}' - Content length: {len(section['content'])}")
            
            if section['title'] and section['title'] != 'Analysis Results':
                story.append(Paragraph(section['title'], self.styles['SubSection']))
            
            clean_content = self.clean_text_for_pdf(section['content'])
            
            # If content is very long, split it into multiple paragraphs for better PDF handling
            if len(clean_content) > 3000:
                content_parts = clean_content.split('<br/><br/>')
                for part in content_parts:
                    if part.strip():
                        story.append(Paragraph(part.strip(), self.styles['AnalysisContent']))
                        story.append(Spacer(1, 6))
            else:
                story.append(Paragraph(clean_content, self.styles['AnalysisContent']))
            
            story.append(Spacer(1, 12))
        
        # Page break before annotated transcript
        story.append(PageBreak())
        
        # Annotated Transcript section
        story.append(Paragraph("Annotated Transcript with Coaching Feedback", self.styles['SectionHeader']))
        story.append(Paragraph(
            "The following section contains the original transcript with inline coaching comments and feedback.",
            self.styles['AnalysisContent']
        ))
        story.append(Spacer(1, 15))
        
        # Parse and format annotated transcript
        parsed_transcript = self.parse_annotated_transcript(annotated_transcript)
        
        for item in parsed_transcript:
            if item['type'] == 'coaching':
                # Coaching comment
                clean_content = self.clean_text_for_pdf(item['content'])
                story.append(Paragraph(f"💡 Coach: {clean_content}", self.styles['CoachComment']))
            else:
                # Regular dialogue
                clean_content = self.clean_text_for_pdf(item['content'])
                story.append(Paragraph(clean_content, self.styles['AnnotationText']))
            
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data