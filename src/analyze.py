from tabulate import tabulate
import pandas as pd
import sqlite3
import sys

def most_recent(con):
    query = """
        SELECT
          obj_id,
          ds,
          run_status
        FROM run
        ORDER BY 1 DESC
        LIMIT 1;
    """
    df = pd.read_sql_query(query, con)
    run_obj_id = df['obj_id'][0]
    ds = df['ds'][0]
    run_status = df['run_status'][0]
    if run_status != "SUCCESS":
      print(f"Error: most recent run (run_obj_id={run_obj_id}, ds={ds}) has status={run_status}", file = sys.stderr)
      exit(-1)

    return run_obj_id, ds

def repositories_count(con, run_obj_id):
    query = f"""
        SELECT
          task.ds,
          JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
          JSON_EXTRACT(task.task_tags, '$.language') AS language,
          MAX(github_search_total_count) AS num_repos
        FROM task INNER JOIN github_search
          ON task.obj_id = github_search.task_obj_id
        WHERE
          task.run_obj_id = {run_obj_id}
          AND task.task_kind = 'github_repositories_search'
        GROUP BY 1, 2, 3
        ORDER BY 2, 4;
    """
    return pd.read_sql_query(query, con)

def users_count(con, run_obj_id):
    query = f"""
        SELECT
          task.ds,
          JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
          JSON_EXTRACT(task.task_tags, '$.language') AS language,
          MAX(github_search_total_count) AS num_users
        FROM task INNER JOIN github_search
          ON task.obj_id = github_search.task_obj_id
        WHERE
          task.run_obj_id = {run_obj_id}
          AND task.task_kind = 'github_users_search'
        GROUP BY 1, 2, 3
        ORDER BY 2, 4;
    """
    return pd.read_sql_query(query, con)

def topics_count(con, run_obj_id):
    query = f"""
        SELECT
          task.ds,
          JSON_EXTRACT(task.task_tags, '$.cutoff') AS window,
          JSON_EXTRACT(task.task_tags, '$.language') AS language,
          MAX(github_search_total_count) AS num_topics
        FROM task INNER JOIN github_search
          ON task.obj_id = github_search.task_obj_id
        WHERE
          task.run_obj_id = {run_obj_id}
          AND task.task_kind = 'github_topics_search'
        GROUP BY 1, 2, 3
        ORDER BY 2, 4;
    """
    return pd.read_sql_query(query, con)

def average_repository(con, run_obj_id):
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
          task.run_obj_id = {run_obj_id}
          AND task.task_kind = 'github_repositories_search'
        GROUP BY 1, 2, 3
        ORDER BY 2, 4;
    """
    return pd.read_sql_query(query, con)


def print_windowed_results(df):
  for window in sorted(set(df['window'])):
    print(f"""
### {window}
    """)
    print(tabulate(df.loc[df['window'] == window], headers='keys', tablefmt='github'))


con = sqlite3.connect("growth-data.db")
run_obj_id, ds = most_recent(con)


print(f"""
# Results for {ds}
""")


print("""
## Topics

`Window` refers to the number of weeks since the topic was created.
""")

print_windowed_results(topics_count(con, run_obj_id))


print("""
## Statistics about non-fork repositories

`Window` refers to the number of weeks since the repository was last pushed.
""")

print_windowed_results(average_repository(con, run_obj_id))


print("""
## Repository counts

`Window` refers to the number of weeks since the repository was last pushed.
""")

print_windowed_results(repositories_count(con, run_obj_id))


print("""
## Users

`Window` refers to the number of weeks since the account was created.
""")

print_windowed_results(users_count(con, run_obj_id))


con.close()
