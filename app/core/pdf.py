# Creates a function to generate invoice in PDF format
# The generate_invoice_pdf() builds a PDF document in memory, and returns the raw bytes - no file written to disk
# the bytes go directly into the HTTP response
# Reportlab has two APIs, here we use the high level one - Platypus, it contains:
# SimpleDocTemplate — the document container, controls page size and margins
# Paragraph — a block of text with a style applied
# Spacer — empty vertical space between elements
# Table — grid layout for line items
# getSampleStyleSheet — built-in text styles you can customize

# The pattern is always the same - build a list called 'story', append elements to it, then call doc.build(story),
# which rebders everything into bytes

# The invoice contains:

# Header -> company nema from tenant_settings, brand color as background
# Invoice metadata -> invoice ID, created date, due date
# Customer info -> name and email
# Line items table -> description , quantity, amount per line
# Total -> sum of all items in dollars

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import logging


# Get a logger instance
logger = logging.getLogger("app.core.pdf")



def generate_invoice_pdf(invoice, customer, tenant_settings) -> bytes:
    logger.info(f"Creating PDF with invoice ID {invoice.id}.")

    # Create a bytes buffer
    # in memory buffer -> a container that behavies like a file in RAM 
    # When reportlab creates the PDF it writes bytes into this container
    # At the end, when buffer.getvalue() is called it extracts those bytes 
    # so that it can be returned from the function 
    buffer = BytesIO() 

    # Create the document
    doc = SimpleDocTemplate(buffer, pagesize = letter)
    styles = getSampleStyleSheet()

    # Build the story list with these elements in order:
    story = []

    # Header table with company name and brand color from tenant_settings
    brand_color = HexColor(tenant_settings.brand_color) if tenant_settings.brand_color else HexColor("#4f46e5")
    header = Table([[Paragraph(tenant_settings.company_name, styles["Title"])]])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), brand_color) 
    ]))
    story.append(header)
    # Spacer
    story.append(Spacer(1, 20))
    
    # Invoice metedata -ID, created date, due date
    story.append(Paragraph(f"ID #{invoice.id}", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Create Date : {invoice.created_at.strftime('%B %d, %Y')}", styles["Normal"]))
    story.append(Paragraph(f"Due Date : {invoice.due_date.strftime('%B %d, %Y')}", styles["Normal"]))
    story.append(Spacer(1, 20))

    
    # Customer name and email
    story.append(Paragraph(f"Customer Name : {customer.name}", styles["Normal"]))
    story.append(Paragraph(f"Customer Email : {customer.email}", styles["Normal"]))
    story.append(Spacer(1, 20))
    
    # Line items table - one row per invoice.line_items, columns: Description, quantity, unit price and amount
    # rows is a list of lists containing the header
    # loop over the invoice.line_items and add values corresponding to each row in the header
    rows = [["Description", "Qty","Unit Price",  "Amount"]]
    total_cents = 0

    for item in invoice.line_items: 
        
        total_cents += item.amount_cents * item.quantity
        rows.append([
            item.description, 
            str(item.quantity), 
            f"${item.amount_cents /100:.2f}", 
            f"${item.amount_cents * item.quantity / 100:.2f}"
        ])

    # Append the values to rows
    rows.append(["", "", "Total", f"${total_cents / 100:.2f}"])
  

    # Create a table
    table = Table(rows, colWidths=[250, 60, 90, 90])

    # Apply styles
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), brand_color),\
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#ffffff")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, brand_color),
        ])

    table.setStyle(style)

    # Add table to the story
    story.append(table)

    # Build and return bytes
    doc.build(story)

    logger.info(f"PDF with invoice ID {invoice.id} successfully created.")

    # Return the raw byte string
    return buffer.getvalue()
    

