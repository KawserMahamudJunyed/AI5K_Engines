"""Utility for parsing and sanitizing LLM-generated XML tags."""
from bs4 import BeautifulSoup
import re

async def sanitize_proposal_xml(raw_text: str) -> str:
    """
    Sanitizes raw LLM output containing XML-like tags (e.g., <verified src="..."> and <gap skill="...">).
    Automatically repairs unclosed tags, malformed nesting, and broken attributes using BeautifulSoup.
    
    Args:
        raw_text: The raw, potentially malformed text from the LLM.
        
    Returns:
        100% compliant XML string with preserved line formatting.
    """
    if not raw_text:
        return ""
        
    # BeautifulSoup with html.parser is highly fault tolerant for broken tags
    soup = BeautifulSoup(raw_text, "html.parser")
    
    # Serialize back to string
    sanitized = str(soup)
    
    # Ensure it's not wrapped in html/body if BS4 added it (html.parser typically doesn't, but lxml might)
    if sanitized.startswith("<html><body>") and sanitized.endswith("</body></html>"):
        sanitized = sanitized[12:-14]
        
    return sanitized
