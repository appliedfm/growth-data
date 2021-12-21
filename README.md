# growth-data

Tools and data for measuring the popularity & growth of various programming languages.

## Install the dependencies

```console
$ pip install -r requirements.txt
```

# Example queries

```sql
sqlite> .mode column
sqlite> SELECT
    ds,
    q,
    MAX(total_count) AS num_repos
  FROM github_search
  GROUP BY ds, q
  ORDER BY 3;
ds            q                                    num_repos
------------  -----------------------------------  ---------
"2021-12-21"  "language:tla and fork:false"        64       
"2021-12-21"  "language:lean and fork:false"       75       
"2021-12-21"  "language:idris and fork:false"      140      
"2021-12-21"  "language:agda and fork:false"       192      
"2021-12-21"  "language:ada and fork:false"        438      
"2021-12-21"  "language:coq and fork:false"        509      
"2021-12-21"  "language:erlang and fork:false"     2260     
"2021-12-21"  "language:ocaml and fork:false"      2278     
"2021-12-21"  "language:fortran and fork:false"    3196     
"2021-12-21"  "language:verilog and fork:false"    3880     
"2021-12-21"  "language:assembly and fork:false"   8652     
"2021-12-21"  "language:haskell and fork:false"    10053    
"2021-12-21"  "language:terraform and fork:false"  10251    
"2021-12-21"  "language:rust and fork:false"       21904    
"2021-12-21"  "language:go and fork:false"         67585    
"2021-12-21"  "language:r and fork:false"          114930   
"2021-12-21"  "language:c and fork:false"          174429   
"2021-12-21"  "language:c++ and fork:false"        270318   
"2021-12-21"  "language:python and fork:false"     773425   
"2021-12-21"  "language:java and fork:false"       943294   
sqlite> 
```