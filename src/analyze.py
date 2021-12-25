from tabulate import tabulate
import pandas as pd
import sqlite3

def most_recent_ds(con):
    query = """
        SELECT
          MAX(ds) AS ds
        FROM run;
    """
    return pd.read_sql_query(query, con)['ds'][0]

def repositories_count(con, ds):
    query = f"""
        SELECT
          task.ds,
          JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
          JSON_EXTRACT(task.task_tags, '$.language') AS language,
          MAX(github_search_total_count) AS num_repos
        FROM task INNER JOIN github_search
          ON task.obj_id = github_search.task_obj_id
        WHERE
          task.ds = '{ds}'
          AND task.task_kind = 'github_repositories_search'
        GROUP BY 1, 2, 3
        ORDER BY 2, 4;
    """
    return pd.read_sql_query(query, con)

def users_count(con, ds):
    query = f"""
        SELECT
          task.ds,
          JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
          JSON_EXTRACT(task.task_tags, '$.language') AS language,
          MAX(github_search_total_count) AS num_users
        FROM task INNER JOIN github_search
          ON task.obj_id = github_search.task_obj_id
        WHERE
          task.ds = '{ds}'
          AND task.task_kind = 'github_users_search'
        GROUP BY 1, 2, 3
        ORDER BY 2, 4;
    """
    return pd.read_sql_query(query, con)

def topics_count(con, ds):
    query = f"""
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
    """
    return pd.read_sql_query(query, con)

def average_repository(con, ds):
    query = f"""
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
          task.ds = '{ds}'
          AND task.task_kind = 'github_repositories_search'
        GROUP BY 1, 2, 3
        ORDER BY 2, 4;
    """
    return pd.read_sql_query(query, con)


con = sqlite3.connect("growth-data.db")
ds = most_recent_ds(con)


print(f"""
# Results for {ds}
""")


print("""
## Statistics about non-fork repositories

`Window` refers to the number of weeks since the repository was last pushed.
""")

print(tabulate(average_repository(con, ds), headers='keys', tablefmt='github'))


print("""
## Users

`Window` refers to the number of weeks since the account was created.
""")

print(tabulate(users_count(con, ds), headers='keys', tablefmt='github'))


print("""
## Topics

`Window` refers to the number of weeks since the topic was created.
""")

print(tabulate(topics_count(con, ds), headers='keys', tablefmt='github'))



print("""
## Global repository counts

`Window` refers to the number of weeks since the repository was last pushed.
""")

print(tabulate(repositories_count(con, ds), headers='keys', tablefmt='github'))

con.close()
