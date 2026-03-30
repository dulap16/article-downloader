"""Tests for the crawler module."""

import pytest
from app.crawler import _clean_html, _is_article_link, _safe_filename, _url_hash


class TestUrlHash:
    def test_returns_string(self):
        result = _url_hash("https://example.com")
        assert isinstance(result, str)
        assert len(result) == 12

    def test_deterministic(self):
        assert _url_hash("https://example.com") == _url_hash("https://example.com")

    def test_different_urls_differ(self):
        assert _url_hash("https://a.com") != _url_hash("https://b.com")


class TestSafeFilename:
    def test_basic_url(self):
        result = _safe_filename("https://example.com/article/hello-world")
        assert result.startswith("example.com_")
        assert result.endswith(".html")

    def test_root_url(self):
        result = _safe_filename("https://example.com/")
        assert "index" in result


class TestIsArticleLink:
    def test_valid_link(self):
        assert _is_article_link("https://example.com/article") is True

    def test_empty(self):
        assert _is_article_link("") is False

    def test_anchor(self):
        assert _is_article_link("#section") is False

    def test_mailto(self):
        assert _is_article_link("mailto:test@example.com") is False

    def test_image(self):
        assert _is_article_link("https://example.com/photo.jpg") is False

    def test_javascript(self):
        assert _is_article_link("javascript:void(0)") is False


class TestCleanHtml:
    def test_extracts_title_and_content(self):
        html = """
        <html>
        <head><title>Test Article</title></head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>This is a test article with enough content to be detected
                   by readability. We need several paragraphs of meaningful text
                   for the extraction to work properly.</p>
                <p>Here is another paragraph with more content that makes this
                   look like a real article rather than just a short snippet.</p>
                <p>And a third paragraph for good measure, with a link to
                   <a href="/other-article">another article</a> that we want
                   to follow.</p>
            </article>
        </body>
        </html>
        """
        cleaned, title, links = _clean_html(html, "https://example.com")
        assert "Test Article" in title
        assert "test article" in cleaned.lower()
        assert isinstance(links, list)

    def test_resolves_relative_links(self):
        html = """
        <html>
        <head><title>Links</title></head>
        <body>
            <article>
                <p>Long enough content to pass readability filters with important
                   information and context about the article topic at hand.</p>
                <p>More content with a link to <a href="/page2">page two</a>
                   which should be resolved to an absolute URL.</p>
                <p>Yet another paragraph to ensure readability picks this up
                   as the main content of the article.</p>
            </article>
        </body>
        </html>
        """
        _, _, links = _clean_html(html, "https://example.com")
        for link in links:
            assert link.startswith("http")
