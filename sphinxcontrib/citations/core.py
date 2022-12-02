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

"""Fetch list of citing papers from ADS and produce a bibtex file.
"""

import json
import re
from typing import Iterable, Set, Union
from urllib.parse import urlencode

import requests


def get_citing_bibcodes(
    token: str, bibcodes: Union[str, Iterable[str]]
) -> Set[str]:
    """Return a set of all the bibcodes that cite the given ones.

    This function performs one API call per bibcode. It requires an active
    internet connection.

    :param token: ADSABS API key.
    :param bibcodes: Bibcode(s) for which the citing papers have to be found.

    :returns: Bibcodes of papers that cite the given bibcode(s)

    """
    _API_URL = "https://api.adsabs.harvard.edu/v1/"

    # We have to ask for a maximum number of results for any given query. We
    # set this to a reasonably high value. If more results are needed, we
    # should implement pagination, but we will worry about this only if needed.
    MAX_ROWS = 2000

    # Ensure that we are working with an iterable
    bibcodes = (bibcodes,) if isinstance(bibcodes, str) else bibcodes

    # We will collect all the results in the ret_bibcodes set
    ret_bibcodes = set()

    for bibcode in bibcodes:
        query = f"citations(bibcode:{bibcode})"
        encoded_query = urlencode({"q": query, "fl": "bibcode"})
        full_query = f"{_API_URL}search/query?{encoded_query}&rows={MAX_ROWS}"
        req = requests.get(
            full_query,
            headers={
                "Authorization": "Bearer " + token,
                "Content-type": "application/json",
            },
        )
        if not req.ok:
            raise RuntimeError(f"Request failed ({req.reason})")

        req_json = req.json()

        if req_json["response"]["numFound"] > MAX_ROWS:
            # See https://github.com/adsabs/adsabs-dev-api/blob/master/examples/search_and_export.ipynb
            raise NotImplementedError()

        docs = req_json["response"]["docs"]

        ret_bibcodes.update([doc["bibcode"] for doc in docs])

    return ret_bibcodes


def get_bibtex(token: str, bibcodes: Union[str, Iterable[str]]) -> str:
    """Return a bibtex associated to the given bibcode(s).

    This function performs a API call. It requires an active internet
    connection.

    :param token: ADSABS API key.
    :param bibcodes: Bibcode(s) for the desired resource(s).

    :returns: Bibtex(s) retrieved for given bibcode(s) and list

    """

    # Ensure that we are working with a tuple
    bibcodes = (bibcodes,) if isinstance(bibcodes, str) else tuple(bibcodes)

    payload = {"bibcode": bibcodes}

    req = requests.post(
        "https://api.adsabs.harvard.edu/v1/export/bibtex",
        headers={
            "Authorization": "Bearer " + token,
            "Content-type": "application/json",
        },
        data=json.dumps(payload),
    )
    if not req.ok:
        raise RuntimeError("Request failed ({req.reason})")

    return req.json()["export"]


def get_citing_bibtex(token: str, bibcodes: Union[str, Iterable[str]]) -> str:
    """Return a bibtex for all the papers citing the given bibcodes.

    :param token: ADSABS API key.
    :param bibcodes: Bibcode(s) for which the citing papers have to be found.

    :returns: Bibtex(s) retrieved for papers citing the given bibcode(s).

    """
    bibcodes = get_citing_bibcodes(token, bibcodes)

    return get_bibtex(token, bibcodes)


def expand_journal_abbreviations(bibtex: str) -> str:
    r"""Expand the journal macros.

    We use the official ADS list.

    Note, this function assumes that the only line in a bib entry with
    structure {\XXXXXXX} is the line with the journal (which is the case as the
    time of writing). Unknown journal abbreviations will be expanded with their
    value.

    :param bibtex: Raw string of the bibtex file

    :returns: Same as input, but with abbreviations expanded.

    """

    # The bibtex now will contain macros for journal names that need to be
    # defined to be able to compile the file. For example, we will have lines
    # that look like: `journal = {\prd},`
    # What we want to do here is substitute \prd with whatever ADS deems the
    # correct name. The substitution list is:
    subs = {
        r"\aj": "AJ",
        r"\actaa": "Acta Astron.",
        r"\araa": r"ARA\&A",
        r"\apj": "ApJ",
        r"\apjl": "ApJ",
        r"\apjlett": "ApJ",
        r"\apjs": "ApJS",
        r"\apjsupp": "ApJS",
        r"\ao": "Appl.~Opt.",
        r"\applopt": "Appl.~Opt.",
        r"\apss": r"Ap\&SS",
        r"\aap": r"A\&A",
        r"\astap": r"A\&A",
        r"\aapr": r"A\&A~Rev.",
        r"\aaps": r"A\&AS",
        r"\azh": "AZh",
        r"\baas": "BAAS",
        r"\bac": "Bull. astr. Inst. Czechosl.",
        r"\caa": "Chinese Astron. Astrophys.",
        r"\cjaa": "Chinese J. Astron. Astrophys",
        r"\icarus": "Icarus",
        r"\jcap": "J. Cosmology Astropart. Phys.",
        r"\jrasc": "JRASC",
        r"\memras": "MmRAS",
        r"\mnras": "MNRAS",
        r"\na": "New A",
        r"\nar": "New A Rev.",
        r"\pra": "Phys.~Rev.~A",
        r"\prb": "Phys.~Rev.~B",
        r"\prc": "Phys.~Rev.~C",
        r"\prd": "Phys.~Rev.~D",
        r"\pre": "Phys.~Rev.~E",
        r"\prl": "Phys.~Rev.~Lett.",
        r"\pasa": "PASA",
        r"\pasp": "PASP",
        r"\pasj": "PASJ",
        r"\rmxaa": "Rev. Mexicana Astron. Astrofis.",
        r"\qjras": "QJRAS",
        r"\skytel": r"S\&T",
        r"\solphys": "Sol.~Phys.",
        r"\sovast": "Soviet~Ast.",
        r"\ssr": "Space~Sci.~Rev.",
        r"\zap": "ZAp",
        r"\nat": "Nature",
        r"\iaucirc": "IAU~Circ.",
        r"\aplett": "Astrophys.~Lett.",
        r"\apspr": "Astrophys.~Space~Phys.~Res.",
        r"\bain": "Bull.~Astron.~Inst.~Netherlands",
        r"\fcp": "Fund.~Cosmic~Phys.",
        r"\gca": "Geochim.~Cosmochim.~Acta",
        r"\grl": "Geophys.~Res.~Lett.",
        r"\jcp": "J.~Chem.~Phys.",
        r"\jgr": "J.~Geophys.~Res.",
        r"\jqsrt": "J.~Quant.~Spec.~Radiat.~Transf.",
        r"\memsai": "Mem.~Soc.~Astron.~Italiana",
        r"\nphysa": "Nucl.~Phys.~A",
        r"\physrep": "Phys.~Rep.",
        r"\physscr": "Phys.~Scr",
        r"\planss": "Planet.~Space~Sci.",
        r"\procspie": "Proc.~SPIE",
    }

    # Now we match anything that looks like `{\XXXXXXX}`, and substitute the
    # content. In this, we a lookaround regex here to avoid removing the { }
    #
    # Let's unpack (?<={)\\(\w+)(?=}): https://stackoverflow.com/a/2973495
    # 1. (?<={) and (?=}) are the bounding lookaround groups
    # 2. Inside, we match \\(\w+), which matches the literal \\ and a word
    #
    # re.sub matches the pattern in the first argument and applies the
    # substitution defined in the second argument to the string in the last
    # argument
    def _expand(abbr: str) -> str:
        # If we don't have the abbreviation in the dictionary, just return what
        # we had with removing the \
        return subs.get(abbr, abbr.replace("\\", ""))

    return re.sub(r"(?<={)\\(\w+)(?=})", lambda m: _expand(m.group(0)), bibtex)


def write_citing_bibtex(
    token: str, bibcodes: Union[str, Iterable[str]], path: str
) -> None:
    """Write a bibtex for all the papers citing the given bibcodes.

    Pre-existing files will be overwritten.

    :param token: ADSABS API key.
    :param bibcodes: Bibcode(s) for which the citing papers have to be found.
    :param path: File where the file should be written.

    """

    bibtex = expand_journal_abbreviations(get_citing_bibtex(token, bibcodes))

    with open(path, "w") as file_:
        file_.write(bibtex)
