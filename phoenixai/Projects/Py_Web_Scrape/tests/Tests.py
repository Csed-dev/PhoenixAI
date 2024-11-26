import unittest
from unittest.mock import patch

import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from main import fetch_url_content, SHOTGUN, get_user_input

class Tests(unittest.TestCase):
    @patch('main.requests.get')
    def test_fetch_url_content(self, mock_get):
        print('Now running test_fetch_url_content')
        mock_get.return_value.content = b"<html></html>"
        content = fetch_url_content("https://example.com")
        self.assertEqual(content, b"<html></html>")

    def test_fetch_url_invalid(self):
        print('Now running test_fetch_url_invalid')
        with patch('main.requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Invalid URL")
            content = fetch_url_content("invalid-url")
            assert content is None

    @patch('main.input', return_value="https://example.com")  # Mock user input
    @patch('main.requests.get')  # Mock requests.get
    def test_mock_input(self, mock_get, mock_input):
        print('Now running test_mock_input')
        # Simulate a response from requests.get
        mock_get.return_value.content = b"<html></html>"

        # Call the function that invokes both input and requests.get
        url = get_user_input()
        content = fetch_url_content(url)  # This ensures requests.get is invoked

        # Assert the mocked input was called and returned correctly
        self.assertEqual(url, "https://example.com")
        mock_input.assert_called_once()

        # Assert requests.get was called with the mocked URL
        mock_get.assert_called_once_with("https://example.com")
        self.assertEqual(content, b"<html></html>")

    def test_shotgun_output(self):
        print('Now running test_shotgun_output')
        # Ensure SHOTGUN just prints the ASCII without user input
        SHOTGUN()  # This shouldn't require mocking, as it doesn't use input.


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
