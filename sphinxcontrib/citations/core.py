#!/usr/bin/env python3

import json
import re
from typing import Iterable, Set, Tuple, Union
from urllib.parse import urlencode

import requests


def get_citing_bibcodes(token: str, bibcodes: Union[str, Iterable[str]]) -> Set[str]:
    """Return a set of all the bibcodes that cite the given ones.

    This function performs one API call per bibcode. It requires an active internet
    connection.

    :param token: ADSABS API key.
    :param bibcodes: Bibcode(s) for which the citing papers have to be found.

    :returns: Bibcodes of papers that cite the given bibcodes()

    """
    MAX_ROWS = 2000

    if isinstance(bibcodes, str):
        bibcodes = (bibcodes,)

    ret_bibcodes = set()

    for bibcode in bibcodes:
        query = f"citations(bibcode:{bibcode})"
        encoded_query = urlencode({"q": query, "fl": "bibcode"})
        req = requests.get(
            f"https://api.adsabs.harvard.edu/v1/search/query?{encoded_query}&rows={MAX_ROWS}",
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

    This function performs a API call. It requires an active internet connection.

    :param token: ADSABS API key.
    :param bibcodes: Bibcode(s) for the desired resource(s).

    :returns: Bibtex(s) retrieved for given bibcode(s) and list

    """

    if isinstance(bibcodes, str):
        bibcodes = (bibcodes,)

    payload = {"bibcode": tuple(bibcodes)}

    req = requests.post(
        "https://api.adsabs.harvard.edu/v1/export/bibtex",
        headers={"Authorization": "Bearer " + token, "Content-type": "application/json"},
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


def write_citing_bibtex(
    token: str, bibcodes: Union[str, Iterable[str]], path: str
) -> None:
    """Write a bibtex for all the papers citing the given bibcodes.

    Pre-existing files will be overwritten.

    The macros defined by ADS will be added to the bibtex.

    :param token: ADSABS API key.
    :param bibcodes: Bibcode(s) for which the citing papers have to be found.
    :param path: File where the file should be written.

    """
    bibtex = get_citing_bibtex(token, bibcodes)

    subs = {
        "\aj": "AJ",
        "\actaa": "Acta Astron.",
        "\araa": "ARA\&A",
        "\apj": "ApJ",
        "\apjl": "ApJ",
        "\apjlett": "ApJ",
        "\apjs": "ApJS",
        "\apjsupp": "ApJS",
        "\ao": "Appl.~Opt.",
        "\applopt": "Appl.~Opt.",
        "\apss": "Ap\&SS",
        "\aap": "A\&A",
        "\astap": "A\&A",
        "\aapr": "A\&A~Rev.",
        "\aaps": "A\&AS",
        "\azh": "AZh",
        "\baas": "BAAS",
        "\bac": "Bull. astr. Inst. Czechosl.",
        "\caa": "Chinese Astron. Astrophys.",
        "\cjaa": "Chinese J. Astron. Astrophys",
        "\icarus": "Icarus",
        "\jcap": "J. Cosmology Astropart. Phys.",
        "\jrasc": "JRASC",
        "\memras": "MmRAS",
        "\mnras": "MNRAS",
        "\na": "New A",
        "\nar": "New A Rev.",
        "\pra": "Phys.~Rev.~A",
        "\prb": "Phys.~Rev.~B",
        "\prc": "Phys.~Rev.~C",
        "\prd": "Phys.~Rev.~D",
        "\pre": "Phys.~Rev.~E",
        "\prl": "Phys.~Rev.~Lett.",
        "\pasa": "PASA",
        "\pasp": "PASP",
        "\pasj": "PASJ",
        "\rmxaa": "Rev. Mexicana Astron. Astrofis.",
        "\qjras": "QJRAS",
        "\skytel": "S\&T",
        "\solphys": "Sol.~Phys.",
        "\sovast": "Soviet~Ast.",
        "\ssr": "Space~Sci.~Rev.",
        "\zap": "ZAp",
        "\nat": "Nature",
        "\iaucirc": "IAU~Circ.",
        "\aplett": "Astrophys.~Lett.",
        "\apspr": "Astrophys.~Space~Phys.~Res.",
        "\bain": "Bull.~Astron.~Inst.~Netherlands",
        "\fcp": "Fund.~Cosmic~Phys.",
        "\gca": "Geochim.~Cosmochim.~Acta",
        "\grl": "Geophys.~Res.~Lett.",
        "\jcp": "J.~Chem.~Phys.",
        "\jgr": "J.~Geophys.~Res.",
        "\jqsrt": "J.~Quant.~Spec.~Radiat.~Transf.",
        "\memsai": "Mem.~Soc.~Astron.~Italiana",
        "\nphysa": "Nucl.~Phys.~A",
        "\physrep": "Phys.~Rep.",
        "\physscr": "Phys.~Scr",
        "\planss": "Planet.~Space~Sci.",
        "\procspie": "Proc.~SPIE",
    }

    # Using a lookaround regex here to avoid removing the { }
    bibtex = re.sub(r"(?<={)\\(\w+)(?=})", lambda m: subs.get(m.group()), bibtex)

    with open(path, "w") as file_:
        file_.write(bibtex)
