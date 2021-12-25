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
    JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
    JSON_EXTRACT(task.task_tags, '$.language') AS language,
    MAX(github_search_total_count) AS num_repos
  FROM task INNER JOIN github_search
    ON task.obj_id = github_search.task_obj_id
  WHERE
    task.task_kind = 'github_repositories_search'
  GROUP BY 1, 2, 3
  ORDER BY 2, 4;
.exit
EOF
```

```

```


### Stats about the average (non-fork) repository

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds AS ds,
    JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
    JSON_EXTRACT(task.task_tags, '$.language') AS language,
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
  GROUP BY 1, 2, 3
  ORDER BY 2, 4;
.exit
EOF
```

```

```


## Queries about users

### Number of users per language

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds,
    JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
    JSON_EXTRACT(task.task_tags, '$.language') AS language,
    MAX(github_search_total_count) AS num_users
  FROM task INNER JOIN github_search
    ON task.obj_id = github_search.task_obj_id
  WHERE
    task.task_kind = 'github_users_search'
  GROUP BY 1, 2, 3
  ORDER BY 2, 4;
.exit
EOF
```

```

```


## Queries about topics

### Number of language-related topics

```sql
sqlite3 github.db <<EOF
.mode column
SELECT
    task.ds,
    JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
    JSON_EXTRACT(task.task_tags, '$.language') AS language,
    MAX(github_search_total_count) AS num_topics
  FROM task INNER JOIN github_search
    ON task.obj_id = github_search.task_obj_id
  WHERE
    task.task_kind = 'github_topics_search'
  GROUP BY 1, 2, 3
  ORDER BY 2, 4;
.exit
EOF
```

```

```
