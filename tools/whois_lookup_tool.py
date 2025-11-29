import os
import requests
from typing import TypedDict, List, Optional, Union


class WhoisResponse(TypedDict, total=False):
    domain_name: str
    registrar: str
    registrar_url: Optional[str]
    whois_server: str
    updated_date: Union[int, List[int]]
    creation_date: Union[int, List[int]]
    expiration_date: Union[int, List[int]]
    name_servers: List[str]
    emails: Optional[List[str]]
    dnssec: str
    org: Optional[str]
    country: Optional[str]


def search_whois_api_ninja(domain: str) -> Optional[WhoisResponse]:
    """
    Perform a WHOIS lookup for a domain using API Ninja. Hidden registrar information 
    
    Args:
        domain: The domain name to look up (e.g., "example.com"), API key currently only suppports .com domains
        
    Returns:
        WhoisResponse dictionary containing domain information, or None if lookup fails
    """
    api_key = os.getenv("API_NINJA_KEY")
    
    if not api_key:
        raise ValueError("API_NINJA_KEY environment variable is not set")
    
    url = "https://api.api-ninjas.com/v1/whois"
    headers = {"X-Api-Key": api_key}
    params = {"domain": domain}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching WHOIS data: {e}")
        return None