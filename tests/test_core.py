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

import os

from citations import core


def test_expand_journal_abbreviations():
    # Valid
    assert core.expand_journal_abbreviations("{\\prd}") == "{Phys.~Rev.~D}"

    # Escaped character
    assert core.expand_journal_abbreviations("{\\na}") == "{New A}"

    # Missing abbreviation
    assert core.expand_journal_abbreviations("{\\lol}") == "{lol}"


def test_write_citing_bibtex(tmp_path):
    token = os.environ["ADS_API"]

    path = tmp_path / "bibtex.bib"

    core.write_citing_bibtex(token, ["2021JOSS....6.3099B"], path)

    with open(path, "r") as file_:
        content = file_.read()

    expected = """
@ARTICLE{2022PhRvL.128g1101B,
       author = {{Bozzola}, Gabriele},
        title = "{Does Charge Matter in High-Energy Collisions of Black Holes?}",
      journal = {Phys.~Rev.~Lett.},
     keywords = {General Relativity and Quantum Cosmology},
         year = 2022,
        month = feb,
       volume = {128},
       number = {7},
          eid = {071101},
        pages = {071101},
          doi = {10.1103/PhysRevLett.128.071101},
archivePrefix = {arXiv},
       eprint = {2202.05310},
 primaryClass = {gr-qc},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2022PhRvL.128g1101B},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}"""

    assert expected in content
