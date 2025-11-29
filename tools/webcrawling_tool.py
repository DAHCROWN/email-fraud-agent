import requests
from bs4 import BeautifulSoup


def parse_html_beautiful_soup(domain_url: str) -> str:
    """Retrieves the webpage from the url and returns a searchable object. Some websites have protection against bot scrapping
    
    Keyword arguments:
    Args:
        domain_url: The webpage url to be crawled and indexed
    Returns:
        The parse webpage
    """
    response = requests.get(domain_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()
