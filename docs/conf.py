"""Sphinx configuration."""
project = "Langchain Token Usage"
author = "Janos Tolgyesi"
copyright = "2023, Janos Tolgyesi"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
