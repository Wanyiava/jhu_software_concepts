"""Bounded survey scraping with injectable HTTP transport and pure parsing."""
import json
import re
from pathlib import Path
from urllib.parse import urlencode, urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.thegradcafe.com/survey/index.php"


def _build_urls(pages):
    """Return the first 1-10 survey page URLs; avoid an unbounded pull."""
    if isinstance(pages, bool) or not isinstance(pages, int) or not 1 <= pages <= 10:
        raise ValueError("pages must be an integer between 1 and 10")
    return [f"{BASE_URL}?{urlencode({'p': page})}" for page in range(1, pages + 1)]


def _match(pattern, value):
    """Return the first captured metadata value or None."""
    match = re.search(pattern, value, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _parse_html(html_text):
    """Parse supplied five-column survey HTML and optional detail rows.

    Header/detail rows are ignored. Details cannot leak from the next result.
    Missing identity fields are reported by the cleaner before persistence.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    for row in soup.select("tr"):
        columns = row.find_all("td", recursive=False)
        if len(columns) < 5:
            continue
        details = row.find_next_sibling("tr")
        comments = ""
        if details is not None and len(details.find_all("td", recursive=False)) < 5:
            comments = details.get_text(" ", strip=True)
        combined = row.get_text(" ", strip=True) + " " + comments
        link = columns[4].find("a", href=True)
        results.append({
            "university": columns[0].get_text(" ", strip=True),
            "program": columns[1].get_text(" ", strip=True),
            "date_added": columns[2].get_text(" ", strip=True),
            "status": columns[3].get_text(" ", strip=True),
            "url": urljoin(BASE_URL, link["href"]) if link else "",
            "comments": comments,
            "degree": _match(r"\b(PhD|Ph\.?D\.?|Doctorate|Masters?|MFA|MS|MA)\b", combined),
            "us_or_international": _match(r"\b(International|American)\b", combined),
            "term": _match(r"\b((?:Fall|Spring|Summer|Winter)\s+20\d{2})\b", combined),
            "gpa": _match(r"\bGPA\s*:?\s*(\d+(?:\.\d+)?)", combined),
            "gre": _match(r"\bGRE\s*:?\s*(\d{3})\b", combined),
        })
    return results


def scrape_data(pages=1, *, http_get=None):
    """Fetch bounded pages with TLS verification and a 15 s timeout.

    Pass an HTTP double in tests. HTTP failures propagate before any database
    write so the web layer can report failure without committing a partial batch.
    """
    get = http_get or requests.get
    results = []
    for url in _build_urls(pages):
        response = get(url, timeout=15, headers={"User-Agent": "GradCafeCourseProject/1.0"})
        response.raise_for_status()
        rows = _parse_html(response.text)
        if not rows:
            break
        results.extend(rows)
    return results


def save_data(data, filename):
    """Save raw scraper records as UTF-8 JSON (legacy helper)."""
    Path(filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_data(filename):
    """Read a previously saved raw scraper JSON file (legacy helper)."""
    return json.loads(Path(filename).read_text(encoding="utf-8"))
