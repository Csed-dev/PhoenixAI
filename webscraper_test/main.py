
"""Main script."""

import sys
from webscraper_test.tag_list import get_all_tags

def shotgun(url):
    """Fetch all tags from a given URL."""
    tags = get_all_tags(url)
    return tags

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main