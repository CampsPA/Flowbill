# This file has one function: send_invoice_email(customer, invoice, pdf_bytes). It
# sends a transactional email with the PDF attached using the Resend SDK.


import logging
import resend
import base64
from app.config import settings



# Get a logger instance
logger = logging.getLogger("app.core.email")


def send_invoice_email(customer, invoice, pdf_bytes):
    resend.api_key = settings.resend_api_key
    encoded_bytes = base64.b64encode(pdf_bytes).decode('utf-8')

    params = {
        "from": "user@mail.com" ,
        "to": [customer.email], 
        "subject": f"Invoice #{invoice.id}",
        "text": "Please find your invoice attached.",
        "attachments" : [
            {"filename": f"invoice_{invoice.id}.pdf",
             "content" : encoded_bytes}
        ]
    }

    result = resend.Emails.send(params)
    return result
    



    
    
    
    
