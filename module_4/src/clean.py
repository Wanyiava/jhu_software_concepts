"""Normalize original scraped/enriched records without requiring a live LLM."""
import math
import re
from datetime import date, datetime
from urllib.parse import urlsplit, urlunsplit

TEXT_FIELDS = ("program", "university", "comments", "status", "term",
               "us_or_international", "degree", "llm_generated_program",
               "llm_generated_university")
ALIASES = {"us_or_international": "US/International", "degree": "Degree",
           "gpa": "GPA", "gre": "GRE", "llm_generated_program": "llm-generated-program",
           "llm_generated_university": "llm-generated-university"}


def parse_str(value):
    """Strip scalar text; missing, structured, and textual nulls become None."""
    if value is None or isinstance(value, (dict, list)):
        return None
    value = str(value).strip()
    return None if value.lower() in {"", "null", "none", "nan"} else value


def parse_float(value):
    """Read a finite number, also accepting legacy values such as 'GPA 3.8'."""
    text = parse_str(value)
    if text is None:
        return None
    match = re.search(r"[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?", text)
    if not match:
        return None
    number = float(match.group())
    return number if math.isfinite(number) else None


def parse_date(value):
    """Accept Python dates and the original ISO/abbreviated/full month formats."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    for pattern in ("%Y-%m-%d", "%b %d, %Y", "%b %d %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value.strip(), pattern).date()
        except ValueError:
            continue
    return None


def canonical_url(value):
    """Normalize a stable result URL while retaining ID-bearing query strings."""
    parts = urlsplit(str(value or "").strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        raise ValueError("Each applicant requires an absolute HTTP(S) result URL")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                       parts.path.rstrip("/"), parts.query, ""))


def clean_record(record):
    """Map legacy keys to Module 3 columns and validate required fields.

    Existing LLM-generated fields are retained; missing enrichment stays NULL.
    IDs are allocated by PostgreSQL. Source URLs deduplicate repeated pulls.
    """
    values = dict(record)
    for key, alias in ALIASES.items():
        if key not in values:
            values[key] = values.get(alias)
    result = {key: parse_str(values.get(key)) for key in TEXT_FIELDS}
    result["date_added"] = parse_date(values.get("date_added"))
    result["url"] = canonical_url(values.get("url"))
    for key in ("gpa", "gre", "gre_v", "gre_aw"):
        result[key] = parse_float(values.get(key))
    for key, label in (("gre_v", "V"), ("gre_aw", "AW")):
        if result[key] is None:
            match = re.search(rf"GRE\s*{label}\s*:?\s*(\d+(?:\.\d+)?)",
                              result["comments"] or "", re.IGNORECASE)
            if match:
                result[key] = float(match.group(1))
    for key in ("program", "university", "date_added", "status"):
        if result[key] is None:
            raise ValueError(f"Applicant is missing required field: {key}")
    return result


def clean_data(records, *, enrich=None):
    """Validate records; optionally call an injected enrichment adapter.

    The adapter takes and returns a dictionary. The default path needs no model
    download or external LLM service; tests can supply a deterministic double.
    """
    result = []
    for record in records:
        prepared = dict(record)
        if enrich is not None:
            prepared.update(enrich(dict(prepared)))
        result.append(clean_record(prepared))
    return result
