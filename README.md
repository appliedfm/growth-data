# growth-data

![Website](https://img.shields.io/website?url=https%3A%2F%2Fgrowth.applied.fm)
![Documentation Status](https://readthedocs.org/projects/fm-growth/badge/?version=latest)

![GitHub](https://img.shields.io/github/license/appliedfm/growth-data)

Tools and data for measuring the popularity & growth of various programming languages.

The latest report can be viewed at [https://growth.applied.fm](https://growth.applied.fm).

Published by [applied.fm](https://applied.fm). Hosted by [readthedocs.org](https://readthedocs.org/projects/fm-growth/)

## Repo organization & flow

1. Code & doc changes are made to the [`main` branch](https://github.com/appliedfm/growth-data).
2. Data is added to the [`data` branch](https://github.com/appliedfm/growth-data/tree/data).
3. Docs are rendered in the [`docs` branch](https://github.com/appliedfm/growth-data/tree/docs).

This flow has the benefit of automatically tracking data lineage: for any given datum, it is easy to determine which version of the tool generated it. It also ensures that each data-fetch operation uses the latest version of the tool.

[Check the network](https://github.com/appliedfm/growth-data/network) to see the current relationship between these branches.

## Getting the data

Data can be found in the [`data` directory in the `data` branch](https://github.com/appliedfm/growth-data/tree/data/data).

Alternatively, you can fetch new data by running

```console
$ python3 src/github/main.py -o data all
```


## Rendering the plots

```console
$ python3 src/plot.py
```


## Building the report

```console
$ make -C docs html
$ xdg-open docs/build/html/index.html
```

#

[![pandas](https://img.shields.io/badge/-pandas-firebrick)](https://pandas.pydata.org)
[![plotly](https://img.shields.io/badge/-plotly-mediumblue)](https://plotly.com)
[![Sphinx](https://img.shields.io/badge/-Sphinx-navy)](https://www.sphinx-doc.org)
[![readthedocs](https://img.shields.io/badge/-readthedocs-slateblue)](https://readthedocs.org)

[![applied.fm](https://img.shields.io/badge/-applied.fm-orchid)](https://applied.fm)
