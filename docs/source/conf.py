import sys
from pathlib import Path

# sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path("/home/alex/oakestra-cli")))

# sys.path.insert(0, str(Path(__file__).parent.parent / "oak_cli/main.py"))
# sys.path.insert(0, str(Path(__file__).parent.parent / "examples/example.py"))
# sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))
# sys.path.insert(0, str(Path(__file__).parent / "examples" / "example.py"))
# from examples.example import app

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OAK-CLI"
copyright = "2024, Alexander Malyuk"
author = "Alexander Malyuk"
release = "v0.4.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx_click", "sphinxcontrib.typer"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]


# def setup(app):
#     import shutil
#     from pathlib import Path

#     if Path(app.doctreedir).exists():
#         shutil.rmtree(app.doctreedir)
