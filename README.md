# sphinxcontrib-citations
[![PyPI version](https://badge.fury.io/py/sphinxcontrib-citations.svg)](https://badge.fury.io/py/sphinxcontrib-citations)
[![Test](https://github.com/Sbozzolo/sphinxcontrib-citations/actions/workflows/test.yml/badge.svg)](https://github.com/Sbozzolo/sphinxcontrib-citations/actions/workflows/test.yml)

It is often the case that open-source software enables new scientific
developments. When this happens, it is desirable to highlight which new results
were obtained with a given piece of software. If your project has one or more
associated published resources (for example, in the Journal of Open-Source
Software, or in Zenodo), you can use `sphinxcontrib-citations` to generate a
page in your documentations that lists the papers that cite your code.

`sphinxcontrib-citations` is an Sphinx extension that uses NASA's ADS to look up
which papers cite a given list of references. `sphinxcontrib-citations` is
currently in a state of minimum-viable-product: the basic features are
available, but not much else. Pull request are welcome.

To use `sphinxcontrib-citations`, first install it and add it to the
`extensions` variable in your `conf.py` as `sphinxcontrib.citations`.
`sphinxcontrib-citations` has only three options:

- `citations_ads_token`: this is the ADS API token, and it required for the
  correct functioning of the extension. You need a freely obtainable API token
  to use this package. [Read more about NASA ADS
  API](https://ui.adsabs.harvard.edu/help/api/).
- `citations_bibcode_list`: this is the list of bibcodes for which citations
  have to be found. You can find the bibcode for a given paper on ADS.
- `citations_bibtex_file`: this is the name of the `.bib` file that will be
  generated. If not specified, it will be `sphinxcontrib_citations.bib`. If a
  file with the given path already exists, it will be silently overwritten.

When you compile your documentation, `sphinxcontrib-citations` will find all the
references and create a `bib` file. Then, `sphinxcontrib-citations` interfaces
with `sphinxcontrib-bibtex` to produce the page. You can use all the options
provided by that package. A simple page might look like:

``` restructuredtext
Papers citing this software
=============================================

.. bibliography:: sphinxcontrib_citations.bib
   :list: enumerated
   :all:
```

Make sure that the name of the file matches your choice for
`citations_bibtex_file`.

### ADS API Token in GitHub actions

Clearly, committing the API token directly to GitHub is not a good idea. GitHub
actions support [encrypted
secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
that can be used to safely store the token.

Assuming you create a repository secret named `ADS_API` (that contains the
token), you can pass it to `Sphinx` through an environment variable. For
instance, the action step might look like:
``` yaml
- name: Produce documentation
  env:
      ADS_API: ${{ secrets.ADS_API }}
  run: |
    make html
```
with `citations_ads_token = os.environ["ADS_API"]` in the `conf.py`.

### Example

For an example, see
[kuibit](https://sbozzolo.github.io/kuibit/dev/citations.html).

The relevant Sphinx configuration settings that generated this example are:
``` python
citations_ads_token = os.environ["ADS_API"]
citations_bibcode_list = ["2021JOSS....6.3099B"]
```

