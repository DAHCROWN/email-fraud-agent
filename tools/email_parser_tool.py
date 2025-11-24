from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
import re
from typing import List
from models.email import EmailContent


def parse_email(content: str) -> str:
    """Parse email content string (legacy function)."""
    return content


def extract_links(text: str) -> List[str]:
    """Extract URLs from text."""
    # Regex pattern to find URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
    urls = re.findall(url_pattern, text)
    # Also check for URLs in angle brackets or parentheses
    urls.extend(re.findall(r'<(https?://[^>]+)>', text))
    return list(set(urls))  # Remove duplicates


def parse_eml_file(eml_file_path: str) -> EmailContent:
    """
    Parse an .eml file and extract structured email data.
    
    Args:
        eml_file_path: Path to the .eml file
        
    Returns:
        EmailContent object with parsed email data
    """
    with open(eml_file_path, 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)
    
    # Extract email address from 'From' header
    from_header = msg.get('from', '')
    email_address = parseaddr(from_header)[1] if from_header else ''
    
    # Extract host domain from email address
    host_domain = ''
    if email_address and '@' in email_address:
        host_domain = email_address.split('@')[1]
    
    # Extract subject
    subject = msg.get('subject', '') or ''
    
    # Extract body content
    body = ''
    links = []
    
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition', ''))
            
            # Skip attachments
            if 'attachment' in cdispo:
                continue
            
            # Extract plain text or HTML body
            if ctype == 'text/plain':
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_text = payload.decode('utf-8', errors='ignore')
                        body += body_text + '\n'
                        links.extend(extract_links(body_text))
                except (UnicodeDecodeError, AttributeError):
                    pass
            elif ctype == 'text/html':
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_text = payload.decode('utf-8', errors='ignore')
                        # Extract text from HTML (simple approach)
                        # Remove HTML tags for body text
                        text_content = re.sub(r'<[^>]+>', ' ', html_text)
                        body += text_content + '\n'
                        links.extend(extract_links(html_text))
                except (UnicodeDecodeError, AttributeError):
                    pass
    else:
        # Single part message
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
                links = extract_links(body)
        except (UnicodeDecodeError, AttributeError):
            pass
    
    # Extract all headers
    headers = []
    for key, value in msg.items():
        if value:
            headers.append(f"{key}: {value}")
    
    # Clean up body
    body = body.strip()
    
    return EmailContent(
        email_address=email_address,
        host_domain=host_domain,
        subject=subject,
        body=body,
        links=links,
        headers=headers
    )


def parse_eml_builtin(eml_file_path):
    """Legacy function for debugging - prints email content."""
    with open(eml_file_path, 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)

    # Accessing headers
    print(f"From: {msg['from']}")
    print(f"To: {msg['to']}")
    print(f"Subject: {msg['subject']}")

    # Accessing body content
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # Extracting plain text or HTML body
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                print(f"\nPlain Text Body:\n{part.get_payload(decode=True).decode()}")
            elif ctype == 'text/html' and 'attachment' not in cdispo:
                print(f"\nHTML Body:\n{part.get_payload(decode=True).decode()}")
            # Extracting attachments
            elif 'attachment' in cdispo:
                filename = part.get_filename()
                if filename:
                    print(f"\nAttachment: {filename}")
    else:
        print(f"\nBody:\n{msg.get_payload(decode=True).decode()}")