# growth-data

**This tool is under development.**

Tools and data for measuring the popularity & growth of various programming languages.


## Getting the data

Data can be found in the [`data`](https://github.com/appliedfm/growth-data/tree/data/data) branch of this repo.


## Rendering the plots

```console
$ python3 src/plot.py
```


## Building the report

```console
$ make -C docs html
$ xdg-open docs/build/html/index.html
```


## Tool usage

### Install the dependencies

```console
$ pip install -r requirements.txt
```

### Collect the data

```console
$ python3 src/github/main.py -o data all
```
