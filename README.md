# growth-data

Tools and data for measuring the popularity & growth of various programming languages.

## Install the dependencies

```console
$ pip install -r requirements.txt
```

# Example queries

## Number of (non-fork) repositories

```sql
sqlite> .mode column
sqlite> SELECT
    ds,
    github_search_q AS q,
    MAX(github_search_total_count) AS num_repos
  FROM github_search
  GROUP BY 1, 2
  ORDER BY 3;
ds            q                                    num_repos
------------  -----------------------------------  ---------
"2021-12-22"  "language:tla and fork:false"        64       
"2021-12-22"  "language:lean and fork:false"       75       
"2021-12-22"  "language:idris and fork:false"      140      
"2021-12-22"  "language:agda and fork:false"       192      
"2021-12-22"  "language:ada and fork:false"        438      
"2021-12-22"  "language:coq and fork:false"        509      
"2021-12-22"  "language:erlang and fork:false"     2260     
"2021-12-22"  "language:ocaml and fork:false"      2278     
"2021-12-22"  "language:fortran and fork:false"    3196     
"2021-12-22"  "language:verilog and fork:false"    3880     
"2021-12-22"  "language:assembly and fork:false"   8653     
"2021-12-22"  "language:haskell and fork:false"    10053    
"2021-12-22"  "language:terraform and fork:false"  10253    
"2021-12-22"  "language:rust and fork:false"       21904    
"2021-12-22"  "language:go and fork:false"         67588    
"2021-12-22"  "language:r and fork:false"          114932   
"2021-12-22"  "language:c and fork:false"          174431   
"2021-12-22"  "language:c++ and fork:false"        270321   
"2021-12-22"  "language:python and fork:false"     785129   
"2021-12-22"  "language:java and fork:false"       943300   
sqlite> 
```

## Stats about the average (non-fork) repository

```sql
sqlite> .mode column
sqlite> SELECT
    github_search.ds AS ds,
    github_search_q AS q,
    COUNT(*) AS repos,
    SUM(github_repo_has_issues) AS repos_with_issues,
    SUM(github_repo_has_wiki) AS repos_with_wiki,
    SUM(github_repo_has_pages) AS repos_with_pages,
    SUM(length(github_repo_license_name) > 2) AS repos_with_license,
    AVG(github_repo_stargazers_count) AS avg_stars,
    AVG(github_repo_watchers_count) AS avg_watchers,
    AVG(github_repo_forks_count) AS avg_forks,
    AVG(github_repo_size) AS avg_size,
    AVG(github_repo_open_issues_count) AS avg_open_issues
  FROM github_search INNER JOIN github_search_repo
  ON github_search.obj_id = github_search_obj_id
  GROUP BY 1, 2
  ORDER BY 3;
ds            q                                repos  repos_with_issues  repos_with_wiki  repos_with_pages  repos_with_license  avg_stars         avg_watchers      avg_forks         avg_size          avg_open_issues  
------------  -------------------------------  -----  -----------------  ---------------  ----------------  ------------------  ----------------  ----------------  ----------------  ----------------  -----------------
"2021-12-22"  "language:tla and fork:false"    64     63                 61               1                 23                  30.265625         30.265625         2.34375           21779.3125        0.359375         
"2021-12-22"  "language:lean and fork:false"   75     73                 72               5                 22                  19.6533333333333  19.6533333333333  1.86666666666667  14930.3066666667  1.61333333333333 
"2021-12-22"  "language:idris and fork:false"  140    139                136              4                 63                  8.87142857142857  8.87142857142857  0.85              777.142857142857  0.728571428571429
"2021-12-22"  "language:agda and fork:false"   192    188                187              9                 51                  8.984375          8.984375          0.90625           2053.296875       0.291666666666667
"2021-12-22"  "language:ada and fork:false"    438    421                406              12                156                 5.04566210045662  5.04566210045662  1.14155251141553  5451.41095890411  1.09360730593607 
"2021-12-22"  "language:coq and fork:false"    509    502                493              40                202                 8.45186640471513  8.45186640471513  1.5049115913556   5763.44400785855  0.846758349705305
sqlite> 
```

## Stats about the average recently-updated (non-fork) repository

```sql
sqlite> .mode column
sqlite> SELECT
    github_search.ds AS ds,
    github_search_q AS q,
    COUNT(*) AS repos,
    SUM(github_repo_has_issues) AS repos_with_issues,
    SUM(github_repo_has_wiki) AS repos_with_wiki,
    SUM(github_repo_has_pages) AS repos_with_pages,
    SUM(length(github_repo_license_name) > 2) AS repos_with_license,
    AVG(github_repo_stargazers_count) AS avg_stars,
    AVG(github_repo_watchers_count) AS avg_watchers,
    AVG(github_repo_forks_count) AS avg_forks,
    AVG(github_repo_size) AS avg_size,
    AVG(github_repo_open_issues_count) AS avg_open_issues
  FROM github_search INNER JOIN github_search_repo
  ON github_search.obj_id = github_search_obj_id
  WHERE github_repo_updated_at >= '"2021-01-01T00:00:00Z"'
  GROUP BY 1, 2
  ORDER BY 3;
ds            q                                repos  repos_with_issues  repos_with_wiki  repos_with_pages  repos_with_license  avg_stars         avg_watchers      avg_forks         avg_size          avg_open_issues  
------------  -------------------------------  -----  -----------------  ---------------  ----------------  ------------------  ----------------  ----------------  ----------------  ----------------  -----------------
"2021-12-22"  "language:tla and fork:false"    33     32                 30               1                 18                  58.2121212121212  58.2121212121212  4.39393939393939  40074.5151515152  0.636363636363636
"2021-12-22"  "language:idris and fork:false"  44     44                 43               3                 23                  23.9090909090909  23.9090909090909  2.22727272727273  762.681818181818  1.61363636363636 
"2021-12-22"  "language:lean and fork:false"   46     44                 43               3                 14                  31.3260869565217  31.3260869565217  2.95652173913043  24272.2391304348  2.58695652173913 
"2021-12-22"  "language:agda and fork:false"   77     74                 75               8                 24                  19.7402597402597  19.7402597402597  1.93506493506494  4027.46753246753  0.376623376623377
"2021-12-22"  "language:ada and fork:false"    168    165                148              10                82                  12.2857142857143  12.2857142857143  2.67261904761905  9615.82142857143  2.80357142857143 
"2021-12-22"  "language:coq and fork:false"    209    204                199              30                111                 19.2153110047847  19.2153110047847  3.25837320574163  9385.28708133971  1.90909090909091 
sqlite> 
```

