#!/usr/bin/env python3

from typing import Any, Dict

from sphinx.application import Sphinx
from sphinx.config import Config

from sphinxcontrib.citations.core import write_citing_bibtex

def add_bibfile_to_sphinxcontrib_bibtex(app: Sphinx, config: Config):
    if not "sphinxcontrib.bibtex" in config["extensions"]:
        raise RuntimeError("sphinxcontrib-citations requires sphinxcontrib.bibtex")

    if config["bibtex_bibfiles"] is not None:
        config["bibtex_bibfiles"].append(config["citations_bibtex_file"])
    else:
        config["bibtex_bibfiles"] = [config["citations_bibtex_file"]]


def produce_bibtex(app: Sphinx, config: Config):

    if config["citations_ads_token"] is None:
        raise RuntimeError("citations_ads_token not set")

    if config["citations_bibtex_file"] is not None:
        write_citing_bibtex(
            config["citations_ads_token"],
            config["citations_bibcode_list"],
            config["citations_bibtex_file"],
        )

    print(config["bibtex_bibfiles"])


def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_config_value("citations_bibcode_list", None, "html")
    app.add_config_value("citations_ads_token", None, "html")
    app.add_config_value("citations_bibtex_file", "sphinxcontrib_citations.bib", "html")

    app.connect("config-inited", add_bibfile_to_sphinxcontrib_bibtex)
    app.connect("config-inited", produce_bibtex)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
