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
ds          q                                  num_repos
----------  ---------------------------------  ---------
2021-12-22  language:tla and fork:false        64       
2021-12-22  language:lean and fork:false       75       
2021-12-22  language:idris and fork:false      140      
2021-12-22  language:agda and fork:false       192      
2021-12-22  language:ada and fork:false        438      
2021-12-22  language:coq and fork:false        509      
2021-12-22  language:erlang and fork:false     2260     
2021-12-22  language:ocaml and fork:false      2278     
2021-12-22  language:fortran and fork:false    3196     
2021-12-22  language:verilog and fork:false    3882     
2021-12-22  language:assembly and fork:false   8654     
2021-12-22  language:haskell and fork:false    10052    
2021-12-22  language:terraform and fork:false  10254    
2021-12-22  language:rust and fork:false       21906    
2021-12-22  language:go and fork:false         67601    
2021-12-22  language:r and fork:false          114942   
2021-12-22  language:c and fork:false          174439   
2021-12-22  language:c++ and fork:false        270351   
2021-12-22  language:python and fork:false     762729   
2021-12-22  language:java and fork:false       943381   
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
    SUM(github_repo_license_name != '') AS repos_with_license,
    SUM(github_repo_size) AS sum_repo_size,
    SUM(github_repo_stargazers_count) AS sum_stars,
    AVG(github_repo_stargazers_count) AS avg_stars,
    AVG(github_repo_forks_count) AS avg_forks,
    AVG(github_repo_size) AS avg_size,
    AVG(github_repo_open_issues_count) AS avg_open_issues
  FROM github_search INNER JOIN github_search_repo
  ON github_search.obj_id = github_search_obj_id
  GROUP BY 1, 2
  ORDER BY 3;
ds          q                              repos  repos_with_issues  repos_with_wiki  repos_with_pages  repos_with_license  sum_repo_size  sum_stars  avg_stars         avg_forks         avg_size          avg_open_issues  
----------  -----------------------------  -----  -----------------  ---------------  ----------------  ------------------  -------------  ---------  ----------------  ----------------  ----------------  -----------------
2021-12-22  language:tla and fork:false    64     63                 61               1                 23                  1393879        1937       30.265625         2.34375           21779.359375      0.359375         
2021-12-22  language:lean and fork:false   75     73                 72               5                 22                  1119783        1475       19.6666666666667  1.85333333333333  14930.44          1.61333333333333 
2021-12-22  language:idris and fork:false  140    139                136              4                 63                  108818         1242       8.87142857142857  0.85              777.271428571429  0.728571428571429
2021-12-22  language:agda and fork:false   192    188                187              9                 51                  394233         1725       8.984375          0.90625           2053.296875       0.291666666666667
2021-12-22  language:ada and fork:false    438    421                406              12                155                 2387761        2210       5.04566210045662  1.13926940639269  5451.50913242009  1.09360730593607 
2021-12-22  language:coq and fork:false    509    502                493              42                204                 2894476        4304       8.45579567779961  1.50098231827112  5686.59332023576  0.846758349705305
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
    SUM(github_repo_license_name != '') AS repos_with_license,
    SUM(github_repo_size) AS sum_repo_size,
    SUM(github_repo_stargazers_count) AS sum_stars,
    AVG(github_repo_stargazers_count) AS avg_stars,
    AVG(github_repo_forks_count) AS avg_forks,
    AVG(github_repo_size) AS avg_size,
    AVG(github_repo_open_issues_count) AS avg_open_issues
  FROM github_search INNER JOIN github_search_repo
  ON github_search.obj_id = github_search_obj_id
  WHERE github_repo_updated_at >= '2021-01-01T00:00:00Z'
  GROUP BY 1, 2
  ORDER BY 3;
ds          q                              repos  repos_with_issues  repos_with_wiki  repos_with_pages  repos_with_license  sum_repo_size  sum_stars  avg_stars         avg_forks         avg_size          avg_open_issues  
----------  -----------------------------  -----  -----------------  ---------------  ----------------  ------------------  -------------  ---------  ----------------  ----------------  ----------------  -----------------
2021-12-22  language:tla and fork:false    33     32                 30               1                 18                  1322462        1921       58.2121212121212  4.39393939393939  40074.6060606061  0.636363636363636
2021-12-22  language:idris and fork:false  44     44                 43               3                 23                  33576          1052       23.9090909090909  2.22727272727273  763.090909090909  1.61363636363636 
2021-12-22  language:lean and fork:false   46     44                 43               3                 14                  1116533        1442       31.3478260869565  2.93478260869565  24272.4565217391  2.58695652173913 
2021-12-22  language:agda and fork:false   77     74                 75               8                 24                  310115         1520       19.7402597402597  1.93506493506494  4027.46753246753  0.376623376623377
2021-12-22  language:ada and fork:false    168    165                148              10                82                  1615474        2065       12.2916666666667  2.67261904761905  9615.91666666667  2.80357142857143 
2021-12-22  language:coq and fork:false    211    206                201              32                113                 1962100        4018       19.042654028436   3.22748815165877  9299.05213270142  1.89099526066351 
sqlite> 
```
