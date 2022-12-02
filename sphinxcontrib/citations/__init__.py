#!/usr/bin/env python3

# Copyright (C) 2022 Gabriele Bozzola
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <https://www.gnu.org/licenses/>.

from typing import Any, Dict

from sphinx.application import Sphinx
from sphinx.config import Config

from sphinxcontrib.citations.core import write_citing_bibtex


def add_bibfile_to_sphinxcontrib_bibtex(_, config: Config):
    """Ensure that sphinxcontrib.bibtex knowns of our bibtex file."""

    if "sphinxcontrib.bibtex" not in config["extensions"]:
        # This should not happen, but it is better to catch the error instead
        # of relying on everything being properly packaged and installed
        raise RuntimeError(
            "sphinxcontrib-citations requires sphinxcontrib.bibtex"
        )

    # config["bibtex_bibfiles"] is a parameter defined by
    # "sphinxcontrib.bibtex". It is the list of bibtex files that should be
    # taken into consideration during compilation. If the parameter is empty,
    # we write is as our [citations_bibtex_file], otherwise we append the same
    # value to the pre-existing list.

    if config["bibtex_bibfiles"] is not None:
        config["bibtex_bibfiles"].append(config["citations_bibtex_file"])
    else:
        config["bibtex_bibfiles"] = [config["citations_bibtex_file"]]


def produce_bibtex(_, config: Config):
    """Fetch the citations and write the bibtex file."""

    if config["citations_ads_token"] is None:
        raise RuntimeError("citations_ads_token not set")

    if config["citations_bibtex_file"] is not None:
        # We act only if we have a destination bibtex file where to write

        write_citing_bibtex(
            config["citations_ads_token"],
            config["citations_bibcode_list"],
            config["citations_bibtex_file"],
        )


def setup(app: Sphinx) -> Dict[str, Any]:

    # Syntax: <name of the option>, <default value>, "html"
    # "html" means "a change in the parameter requires a complete html rebuild"
    app.add_config_value("citations_bibcode_list", None, "html")
    app.add_config_value("citations_ads_token", None, "html")
    app.add_config_value(
        "citations_bibtex_file", "sphinxcontrib_citations.bib", "html"
    )

    # We produce the bibtex files very early on (in the "config-initiated"
    # phase), so that we can assume that they are ready for the compilation
    app.connect("config-inited", add_bibfile_to_sphinxcontrib_bibtex)
    app.connect("config-inited", produce_bibtex)

    return {
        "version": "0.2.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
