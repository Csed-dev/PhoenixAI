from bs4 import BeautifulSoup
from main import get_tag_content, fetch_url_content
import pytest
from unittest.mock import patch

#def test_get_tag_content():
#    html = "<html><body><p>Test</p></body></html>"
#    soup = BeautifulSoup(html, 'html.parser')
#    result = get_tag_content(soup, 'p')
#    assert len(result) == 1
#    assert result[0].text == "Test"

#def test_integration_web_scraping():
#    url = "https://example.com"
#    html = "<html><body><a href='/test'>Link</a></body></html>"
#    with patch('main.requests.get') as mock_get:
#        mock_get.return_value.content = html.encode()
#        content = fetch_url_content(url)
#        soup = BeautifulSoup(content, 'html.parser')
#        links = get_tag_content(soup, 'a')
#        assert len(links) == 1
#        assert links[0]['href'] == "/test"