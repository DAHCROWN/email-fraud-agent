import sys
from pathlib import Path
# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


from tools.webcrawling_tool import parse_html_beautiful_soup


def test_beautiful_soup_crawling():
    print("Testing Beautiful soup crawling")
    try:
        soup = parse_html_beautiful_soup("https://leetcode.com")
        print("---Website Content---")
        print(soup)
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_beautiful_soup_crawling()
    sys.exit(0 if success else 1)
