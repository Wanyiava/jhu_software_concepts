"""Sphinx configuration; imports require neither PostgreSQL nor network access."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
project = "Grad Café Analytics"
author = "Wanyi Liu"
copyright = "2026, Wanyi Liu"
release = "4.0"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode"]
autodoc_member_order = "bysource"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {"description": "Module 4 · Tested, documented admissions analytics",
                      "fixed_sidebar": True, "page_width": "1120px", "sidebar_width": "250px"}
html_title = "Grad Café Analytics — Module 4"
nitpicky = True
