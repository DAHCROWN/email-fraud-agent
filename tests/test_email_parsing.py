"""Test email parsing functionality."""
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.email_parser_tool import parse_eml_file
from models.email import EmailContent


def test_parse_sample_email():
    """Test parsing the sample_email.eml file."""
    sample_email_path = Path(__file__).parent / "files" / "sample_email.eml"
    
    print(f"Testing email parsing with: {sample_email_path}")
    print("-" * 60)
    
    try:
        result = parse_eml_file(str(sample_email_path))
        
        # Verify it returns EmailContent
        assert isinstance(result, EmailContent), "Result should be EmailContent instance"
        
        # Print results
        print("✓ Email parsed successfully!")
        print(f"\nEmail Address: {result.email_address}")
        print(f"Host Domain: {result.host_domain}")
        print(f"Subject: {result.subject}")
        print(f"\nBody (first 200 chars): {result.body[:200]}...")
        print(f"\nLinks found: {len(result.links)}")
        for i, link in enumerate(result.links[:5], 1):  # Show first 5 links
            print(f"  {i}. {link}")
        if len(result.links) > 5:
            print(f"  ... and {len(result.links) - 5} more")
        print(f"\nHeaders found: {len(result.headers)}")
        print(f"First few headers:")
        for header in result.headers[:3]:
            print(f"  - {header[:80]}...")
        
        # Basic assertions
        assert result.email_address, "Email address should not be empty"
        assert result.host_domain, "Host domain should not be empty"
        assert result.subject, "Subject should not be empty"
        assert result.body, "Body should not be empty"
        assert isinstance(result.links, list), "Links should be a list"
        assert isinstance(result.headers, list), "Headers should be a list"
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_parse_sample_email()
    sys.exit(0 if success else 1)

