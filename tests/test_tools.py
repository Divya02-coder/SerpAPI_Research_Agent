import unittest
from unittest.mock import patch

from src.tools import web_search, news_search


class TestSearchTools(unittest.TestCase):

    @patch("src.tools._search_serpapi")
    def test_web_search(self, mock_search):

        mock_search.return_value = {
            "organic_results": [
                {
                    "title": "Test Result",
                    "link": "https://example.com/test",
                    "snippet": "This is a test."
                }
            ]
        }

        result = web_search("test query")

        self.assertEqual(
            result["search_type"],
            "web"
        )

        self.assertEqual(
            result["source_count"],
            1
        )

        self.assertEqual(
            result["sources"][0]["domain"],
            "example.com"
        )

    @patch("src.tools._search_serpapi")
    def test_news_search(self, mock_search):

        mock_search.return_value = {
            "news_results": [
                {
                    "title": "Test News",
                    "link": "https://news.example.com/test",
                    "snippet": "Test news article.",
                    "source": {
                        "name": "Example News"
                    },
                    "date": "2026-10-06"
                }
            ]
        }

        result = news_search("test news")

        self.assertEqual(
            result["search_type"],
            "news"
        )

        self.assertEqual(
            result["source_count"],
            1
        )

    @patch("src.tools._search_serpapi")
    def test_serpapi_error(self, mock_search):

        mock_search.return_value = {
            "error": "API failed"
        }

        result = web_search("test")

        self.assertEqual(
            result["source_count"],
            0
        )

        self.assertIn(
            "error",
            result
        )


if __name__ == "__main__":
    unittest.main()