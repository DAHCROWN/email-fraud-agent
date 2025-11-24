"""Test WHOIS lookup functionality."""
import sys
import os
from pathlib import Path
from unittest.mock import patch, Mock
import json

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.whois_lookup_tool import search_whois_api_ninja, WhoisResponse


def test_whois_lookup_success_with_single_dates():
    """Test successful WHOIS lookup with single date values."""
    print("Testing WHOIS lookup with single date values...")
    print("-" * 60)
    
    mock_response_data = {
        "domain_name": "google.com",
        "registrar": "reserved-internet assigned numbers authority",
        "whois_server": "whois.iana.org",
        "updated_date": 1628924504,
        "creation_date": 808372800,
        "expiration_date": 1660363200,
        "name_servers": [
            "a.iana-servers.net",
            "b.iana-servers.net"
        ],
        "dnssec": "signeddelegation"
    }
    
    with patch.dict(os.environ, {"API_NINJA_KEY": "test_api_key"}):
        with patch('tools.whois_lookup_tool.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = search_whois_api_ninja("example.com")
            
            assert result is not None, "Result should not be None"
            assert result["domain_name"] == "example.com"
            assert result["registrar"] == "reserved-internet assigned numbers authority"
            assert isinstance(result["updated_date"], int)
            assert isinstance(result["creation_date"], int)
            assert isinstance(result["expiration_date"], int)
            assert len(result["name_servers"]) == 2
            
            print("✓ Test passed: Single date values handled correctly")
            return True


def test_whois_lookup_success_with_list_dates():
    """Test successful WHOIS lookup with list date values."""
    print("\nTesting WHOIS lookup with list date values...")
    print("-" * 60)
    
    mock_response_data = {
        "domain_name": "google.com",
        "registrar": "markmonitor, inc.",
        "registrar_url": "http://www.markmonitor.com",
        "whois_server": "whois.markmonitor.com",
        "updated_date": [1722565053, 1568043544],
        "creation_date": [874306800, 874296000],
        "expiration_date": [1852516800, 1852441200],
        "name_servers": [
            "ns4.google.com",
            "ns1.google.com",
            "ns2.google.com",
            "ns3.google.com"
        ],
        "emails": [
            "abusecomplaints@markmonitor.com",
            "whoisrequest@markmonitor.com"
        ],
        "dnssec": "unsigned",
        "org": "google llc",
        "country": "us"
    }
    
    with patch.dict(os.environ, {"API_NINJA_KEY": "test_api_key"}):
        with patch('tools.whois_lookup_tool.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = search_whois_api_ninja("google.com")
            
            assert result is not None, "Result should not be None"
            assert result["domain_name"] == "google.com"
            assert result["registrar"] == "markmonitor, inc."
            assert result["registrar_url"] == "http://www.markmonitor.com"
            assert isinstance(result["updated_date"], list)
            assert len(result["updated_date"]) == 2
            assert isinstance(result["creation_date"], list)
            assert isinstance(result["expiration_date"], list)
            assert len(result["name_servers"]) == 4
            assert len(result["emails"]) == 2
            assert result["dnssec"] == "unsigned"
            assert result["org"] == "google llc"
            assert result["country"] == "us"
            
            print("✓ Test passed: List date values handled correctly")
            print(f"  Domain: {result['domain_name']}")
            print(f"  Registrar: {result['registrar']}")
            print(f"  Name servers: {len(result['name_servers'])}")
            print(f"  Emails: {len(result['emails'])}")
            return True


def test_whois_lookup_missing_api_key():
    """Test that function raises error when API key is missing."""
    print("\nTesting WHOIS lookup with missing API key...")
    print("-" * 60)
    
    with patch.dict(os.environ, {}, clear=True):
        try:
            result = search_whois_api_ninja("example.com")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "API_NINJA_KEY" in str(e)
            print("✓ Test passed: Correctly raises ValueError for missing API key")
            return True


def test_whois_lookup_api_error():
    """Test handling of API request errors."""
    print("\nTesting WHOIS lookup with API error...")
    print("-" * 60)
    
    with patch.dict(os.environ, {"API_NINJA_KEY": "test_api_key"}):
        with patch('tools.whois_lookup_tool.requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
            
            result = search_whois_api_ninja("example.com")
            
            assert result is None, "Should return None on error"
            print("✓ Test passed: Correctly handles API errors")
            return True


def test_whois_lookup_http_error():
    """Test handling of HTTP errors."""
    print("\nTesting WHOIS lookup with HTTP error...")
    print("-" * 60)
    
    with patch.dict(os.environ, {"API_NINJA_KEY": "test_api_key"}):
        with patch('tools.whois_lookup_tool.requests.get') as mock_get:
            import requests
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            result = search_whois_api_ninja("example.com")
            
            assert result is None, "Should return None on HTTP error"
            print("✓ Test passed: Correctly handles HTTP errors")
            return True


def test_whois_lookup_api_request_params():
    """Test that API request is made with correct parameters."""
    print("\nTesting WHOIS lookup API request parameters...")
    print("-" * 60)
    
    with patch.dict(os.environ, {"API_NINJA_KEY": "test_api_key"}):
        with patch('tools.whois_lookup_tool.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"domain_name": "test.com"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            search_whois_api_ninja("test.com")
            
            # Verify the request was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            
            assert call_args[0][0] == "https://api.api-ninjas.com/v1/whois"
            assert call_args[1]["headers"]["X-Api-Key"] == "test_api_key"
            assert call_args[1]["params"]["domain"] == "test.com"
            assert call_args[1]["timeout"] == 10
            
            print("✓ Test passed: API request made with correct parameters")
            return True


def run_all_tests():
    """Run all WHOIS lookup tests."""
    print("=" * 60)
    print("Running WHOIS Lookup Tests")
    print("=" * 60)
    
    tests = [
        test_whois_lookup_success_with_single_dates,
        test_whois_lookup_success_with_list_dates,
        test_whois_lookup_missing_api_key,
        test_whois_lookup_api_error,
        test_whois_lookup_http_error,
        test_whois_lookup_api_request_params,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test {test.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
