from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    text = """The Document Management System

This document provides an overview of our document management system capabilities.

Key Features:
1. Document Upload: Users can upload PDF documents to the system
2. Text Extraction: The system automatically extracts text content from uploaded PDFs
3. Question Answering: Users can ask questions about the document content
4. Smart Search: The system uses AI to understand and answer questions accurately

Benefits:
- Improved document accessibility
- Quick information retrieval
- Automated content analysis
- Secure document storage

This test document is designed to verify the system's ability to:
1. Process PDF uploads
2. Extract text content
3. Handle user questions
4. Provide relevant answers

The system should be able to answer questions about the content of this document, including its features, benefits, and capabilities."""

    y = 750  # Starting y position
    for line in text.split('\n'):
        if line.strip():  # Only draw non-empty lines
            c.drawString(50, y, line)
        y -= 15  # Move down 15 points
        if y < 50:  # If near bottom of page
            c.showPage()  # Start a new page
            y = 750  # Reset y position
    
    c.save()

if __name__ == '__main__':
    create_test_pdf('test_document.pdf') 