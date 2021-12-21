# growthdata

## Install the dependencies

```console
$ pip install -r requirements.txt
```

# Example queries

```sql
sqlite> SELECT ds, q, MAX(total_count) AS num_repos FROM github_repos_search GROUP BY q ORDER BY 3;
"2021-12-21"|"language:lean and fork:false"|74
"2021-12-21"|"language:agda and fork:false"|192
"2021-12-21"|"language:coq and fork:false"|509
"2021-12-21"|"language:erlang and fork:false"|2260
"2021-12-21"|"language:ocaml and fork:false"|2278
"2021-12-21"|"language:haskell and fork:false"|10051
"2021-12-21"|"language:rust and fork:false"|21890
"2021-12-21"|"language:go and fork:false"|67572
"2021-12-21"|"language:c and fork:false"|174374
"2021-12-21"|"language:python3 and fork:false"|780169
"2021-12-21"|"language:java and fork:false"|943134
"2021-12-21"|"language:python2 and fork:false"|6959161
sqlite>
```