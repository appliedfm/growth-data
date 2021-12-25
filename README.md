# growth-data

Tools and data for measuring the popularity & growth of various programming languages.

## Install the dependencies

```console
$ pip install -r requirements.txt
```

## Fetch the data

```console
$ python3 src/fetch_github.py
```


# Example queries

## Queries about repositories

### Number of (non-fork) repositories

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds,
    task.task_tags,
    github_search_q AS q,
    MAX(github_search_total_count) AS num_repos
  FROM task INNER JOIN github_search
    ON task.obj_id = github_search.task_obj_id
  WHERE
    task.task_kind = 'github_repositories_search'
  GROUP BY 1, 2
  ORDER BY 3;
.exit
EOF
```

```
ds          q                                  num_repos
----------  ---------------------------------  ---------
2021-12-25  language:tla and fork:false        63       
2021-12-25  language:lean and fork:false       75       
2021-12-25  language:isabelle and fork:false   97       
2021-12-25  language:idris and fork:false      140      
2021-12-25  language:agda and fork:false       192      
2021-12-25  language:ada and fork:false        439      
2021-12-25  language:coq and fork:false        508      
2021-12-25  language:prolog and fork:false     1640     
2021-12-25  language:erlang and fork:false     2261     
2021-12-25  language:ocaml and fork:false      2280     
2021-12-25  language:fortran and fork:false    3199     
2021-12-25  language:verilog and fork:false    3888     
2021-12-25  language:assembly and fork:false   8658     
2021-12-25  language:haskell and fork:false    10052    
2021-12-25  language:terraform and fork:false  10266    
2021-12-25  language:scala and fork:false      17797    
2021-12-25  language:rust and fork:false       21950    
2021-12-25  language:go and fork:false         67714    
2021-12-25  language:r and fork:false          115000   
2021-12-25  language:c and fork:false          174594   
2021-12-25  language:c++ and fork:false        270676   
2021-12-25  language:python and fork:false     776308   
2021-12-25  language:java and fork:false       944077   
```

### Stats about the average (non-fork) repository

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds AS ds,
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
  FROM task INNER JOIN github_search INNER JOIN github_search_repo
    ON github_search.obj_id = github_search_obj_id
    AND task.obj_id = github_search.task_obj_id
  WHERE
    task.task_kind = 'github_repositories_search'
  GROUP BY 1, 2
  ORDER BY 3;
.exit
EOF
```

```
ds          q                                 repos  repos_with_issues  repos_with_wiki  repos_with_pages  repos_with_license  sum_repo_size  sum_stars  avg_stars         avg_forks          avg_size          avg_open_issues  
----------  --------------------------------  -----  -----------------  ---------------  ----------------  ------------------  -------------  ---------  ----------------  -----------------  ----------------  -----------------
2021-12-25  language:tla and fork:false       63     62                 60               1                 23                  1327108        1936       30.7301587301587  2.38095238095238   21065.2063492063  0.365079365079365
2021-12-25  language:lean and fork:false      75     73                 72               5                 22                  1121189        1480       19.7333333333333  1.86666666666667   14949.1866666667  1.69333333333333 
2021-12-25  language:isabelle and fork:false  97     92                 92               3                 30                  2442396        697        7.18556701030928  1.63917525773196   25179.3402061856  1.76288659793814 
2021-12-25  language:idris and fork:false     140    139                136              4                 63                  108914         1243       8.87857142857143  0.85               777.957142857143  0.714285714285714
2021-12-25  language:agda and fork:false      192    188                187              9                 51                  394783         1726       8.98958333333333  0.911458333333333  2056.16145833333  0.291666666666667
2021-12-25  language:ada and fork:false       439    422                407              12                156                 2389109        2212       5.03872437357631  1.13895216400911   5442.16173120729  1.08883826879271 
2021-12-25  language:coq and fork:false       508    501                492              41                203                 2914178        4306       8.47637795275591  1.50984251968504   5736.57086614173  0.852362204724409
```

### Stats about the average recently-updated (non-fork) repository

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds AS ds,
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
  FROM task INNER JOIN github_search INNER JOIN github_search_repo
    ON task.obj_id = github_search.task_obj_id
    AND github_search.obj_id = github_search_obj_id
  WHERE
    task.task_kind = 'github_repositories_search'
    AND github_repo_updated_at >= '2021-01-01T00:00:00Z'
  GROUP BY 1, 2
  ORDER BY 3;
.exit
EOF
```

```
ds          q                                 repos  repos_with_issues  repos_with_wiki  repos_with_pages  repos_with_license  sum_repo_size  sum_stars  avg_stars         avg_forks         avg_size          avg_open_issues  
----------  --------------------------------  -----  -----------------  ---------------  ----------------  ------------------  -------------  ---------  ----------------  ----------------  ----------------  -----------------
2021-12-25  language:tla and fork:false       32     31                 29               1                 18                  1255691        1920       60.0              4.53125           39240.34375       0.65625          
2021-12-25  language:isabelle and fork:false  43     42                 39               2                 19                  2183578        688        16.0              3.48837209302326  50780.8837209302  3.93023255813953 
2021-12-25  language:idris and fork:false     44     44                 43               3                 23                  33672          1053       23.9318181818182  2.22727272727273  765.272727272727  1.56818181818182 
2021-12-25  language:lean and fork:false      46     44                 43               3                 14                  1117939        1447       31.4565217391304  2.95652173913043  24303.0217391304  2.71739130434783 
2021-12-25  language:agda and fork:false      77     74                 75               8                 24                  310665         1521       19.7532467532468  1.94805194805195  4034.61038961039  0.376623376623377
2021-12-25  language:ada and fork:false       169    166                149              10                83                  1616822        2067       12.2307692307692  2.66272189349112  9566.99408284024  2.7810650887574  
2021-12-25  language:coq and fork:false       212    207                201              31                113                 1962204        4049       19.0990566037736  3.2688679245283   9255.67924528302  1.91509433962264 
```


## Queries about users

### Number of users per language

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds,
    task.task_tags,
    github_search_q AS q,
    MAX(github_search_total_count) AS num_users
  FROM task INNER JOIN github_search
    ON task.obj_id = github_search.task_obj_id
  WHERE
    task.task_kind = 'github_users_search'
  GROUP BY 1, 2
  ORDER BY 3;
.exit
EOF
```

```
ds          q                   num_users
----------  ------------------  ---------
2021-12-25  language:tla        66       
2021-12-25  language:idris      96       
2021-12-25  language:isabelle   137      
2021-12-25  language:agda       213      
2021-12-25  language:lean       281      
2021-12-25  language:ada        821      
2021-12-25  language:coq        1009     
2021-12-25  language:prolog     3764     
2021-12-25  language:ocaml      4770     
2021-12-25  language:erlang     7247     
2021-12-25  language:verilog    11928    
2021-12-25  language:fortran    12499    
2021-12-25  language:haskell    15265    
2021-12-25  language:assembly   22227    
2021-12-25  language:terraform  28924    
2021-12-25  language:rust       32639    
2021-12-25  language:scala      50258    
2021-12-25  language:go         218182   
2021-12-25  language:r          284599   
2021-12-25  language:c          769291   
2021-12-25  language:c++        1085261  
2021-12-25  language:python     2858174  
2021-12-25  language:java       3401670  
```


## Queries about topics

### Number of language-related topics

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds,
    github_search_q AS q,
    MAX(github_search_total_count) AS num_topics
  FROM task INNER JOIN github_search
    ON task.obj_id = github_search.task_obj_id
  WHERE
    task.task_kind = 'github_topics_search'
  GROUP BY 1, 2
  ORDER BY 3;
.exit
EOF
```

```
ds          q          num_topics
----------  ---------  ----------
2021-12-25  isabelle   3         
2021-12-25  r          3         
2021-12-25  idris      10        
2021-12-25  agda       12        
2021-12-25  tla        21        
2021-12-25  c          30        
2021-12-25  c++        30        
2021-12-25  coq        37        
2021-12-25  ocaml      57        
2021-12-25  verilog    68        
2021-12-25  fortran    85        
2021-12-25  prolog     96        
2021-12-25  lean       121       
2021-12-25  erlang     165       
2021-12-25  haskell    205       
2021-12-25  assembly   328       
2021-12-25  terraform  339       
2021-12-25  scala      512       
2021-12-25  rust       659       
2021-12-25  ada        1072      
2021-12-25  python     4825      
2021-12-25  java       5547      
2021-12-25  go         7742      
```
