from config import *
from datetime import datetime, timedelta, timezone
from orm import Run, Task
from orm_github import GitHub_Rest_Request, GitHub_Search, GitHub_Search_Repo, GitHub_Search_User, GitHub_Search_Topic
from time import sleep, time
import argparse
import json
import requests
import sqlite3
import sys
import urllib.parse

now = datetime.now(tz=timezone.utc)
now_ds = now.strftime("%Y-%m-%d")


class GitHub:
    def __init__(self, query_delay=3, search_delay=7, search_results_max=1000):
        self.search_results_max = search_results_max

        self.last_query = None
        self.query_delay = query_delay

        self.last_search = None
        self.search_delay = search_delay

    def ratelimit(self, is_search):
        ts = datetime.now(tz=timezone.utc)

        last = self.last_search if is_search else self.last_query

        if last is not None:
            delay = self.search_delay if is_search else self.query_delay
            second_since_last = (ts - last).total_seconds()
            sleep_for = delay - second_since_last
            if sleep_for > 0:
                print(f"  ... rate limit: sleeping for {sleep_for} seconds ...")
                sleep(sleep_for)

        ts = datetime.now(tz=timezone.utc)
        if is_search:
            self.last_search = ts
        else:
            self.last_query = ts
        return ts

    def do_request(self, task, api_url, is_search=False, retries=1):
        print(f"  ... do_request(\"{api_url}\")")
        ts = self.ratelimit(is_search)

        response = requests.get(api_url)
        status = response.status_code
        github_rest_request_data = response.json()
        github_rest_request = GitHub_Rest_Request(
            ds = str(now_ds),
            ts = str(ts),
            task_obj_id = task.obj_id,
            github_rest_request_url = str(api_url),
            github_rest_request_status = int(status),
            github_rest_request_data = str(github_rest_request_data)
        )
        github_rest_request.create_entry()

        if 200 != status and 0 < retries:
            return do_request(
                task = task,
                api_url = api_url,
                is_search = is_search,
                retries = retries - 1
            )

        return github_rest_request, github_rest_request_data

    def do_search(self, task, target, item_of_json, q, page, per_page, fetch_all):
        print(f"{target}_search(q={q}, page={page}, per_page={per_page}, fetch_all={fetch_all})")

        github_rest_request, github_rest_request_data = self.do_request(
            task,
            f"https://api.github.com/search/{target}?q={urllib.parse.quote(q)}&page={page}&per_page={per_page}",
            is_search=True
        )

        if 200 != github_rest_request.github_rest_request_status:
            print(f" ... error: status {github_rest_request.github_rest_request_status}")
            return False

        total_count = int(github_rest_request_data["total_count"])
        total_so_far = (page - 1) * per_page + int(len(github_rest_request_data["items"]))
        print(f"  ... success: {total_so_far} of {total_count}")

        # Log the top-line results
        github_search = GitHub_Search.of_json(
            task = task,
            github_search_type = target,
            github_rest_request = github_rest_request,
            q = q,
            page = page,
            per_page = per_page,
            search_results = github_rest_request_data,
        )
        github_search.create_entry()

        if fetch_all:
            # Log each of the results
            for github_search_item_data in github_rest_request_data["items"]:
                github_search_item = item_of_json(
                    task,
                    github_search,
                    github_search_item_data
                )
                github_search_item.create_entry()

            # Continue to the next page
            if total_so_far < total_count and total_so_far < self.search_results_max:
                return self.do_search(
                    task,
                    target,
                    item_of_json,
                    q,
                    page = page + 1,
                    per_page = per_page,
                    fetch_all = fetch_all
                )
        return True

    def repositories_search(self, run: Run, tags, q, pushed_since=None, page=1, per_page=75, fetch_all=False):
        if not fetch_all:
            per_page=1

        task = Task.new_task(
            run,
            task_kind = "github_repositories_search",
            task_args = json.dumps({
                "q": q,
                "pushed_since": pushed_since,
                "page": page,
                "per_page": per_page,
                "fetch_all": fetch_all
            }),
            task_tags = json.dumps(tags),
        )
        task.create_entry()

        success = self.do_search(
            task,
            "repositories",
            GitHub_Search_Repo.of_json,
            q + (f" and pushed:>{pushed_since}" if pushed_since is not None else ""),
            page = page,
            per_page = per_page,
            fetch_all = fetch_all
        )
        task.task_status = "SUCCESS" if success else "HAS_ERRORS"
        task.update_entry()
        return success

    def users_search(self, run: Run, tags, q, created_after=None, page=1, per_page=75, fetch_all=False):
        if not fetch_all:
            per_page=1

        task = Task.new_task(
            run,
            task_kind = "github_users_search",
            task_args = json.dumps({
                "q": q,
                "created_after": created_after,
                "page": page,
                "per_page": per_page,
                "fetch_all": fetch_all
            }),
            task_tags = json.dumps(tags),
        )
        task.create_entry()
        
        success = self.do_search(
            task,
            "users",
            GitHub_Search_User.of_json,
            q + (f" and created:>{created_after}" if created_after is not None else ""),
            page = page,
            per_page = per_page,
            fetch_all = fetch_all
        )
        task.task_status = "SUCCESS" if success else "HAS_ERRORS"
        task.update_entry()
        return success

    def topics_search(self, run: Run, tags, q, created_after=None, page=1, per_page=75, fetch_all=False):
        if not fetch_all:
            per_page=1

        task = Task.new_task(
            run,
            task_kind = "github_topics_search",
            task_args = json.dumps({
                "q": q,
                "created_after": created_after,
                "page": page,
                "per_page": per_page,
                "fetch_all": fetch_all
            }),
            task_tags = json.dumps(tags),
        )
        task.create_entry()
        
        success = self.do_search(
            task,
            "topics",
            GitHub_Search_Topic.of_json,
            q + (f" and created:>{created_after}" if created_after is not None else ""),
            page = page,
            per_page = per_page,
            fetch_all = fetch_all
        )
        task.task_status = "SUCCESS" if success else "HAS_ERRORS"
        task.update_entry()
        return success


def weekly_stats(run):
    success = True

    for window in GITHUB_WINDOWS:
        for language in (GITHUB_LANGUAGES):
            print(f"q={language}, window={window} ...")
            success = success and gh.repositories_search(
                run,
                {
                    "language": language,
                    "window": window,
                },
                f"language:{language} and fork:false",
                pushed_since=(now - GITHUB_WINDOWS[window]).strftime("%Y-%m-%d") if GITHUB_WINDOWS[window] is not None else None,
                fetch_all=(language, window) in GITHUB_FETCH_ALL,
            )
            if window in GITHUB_USER_WINDOWS:
                success = success and gh.users_search(
                    run,
                    {
                        "language": language,
                        "window": window,
                    },
                    f"language:{language}",
                    created_after=(now - GITHUB_WINDOWS[window]).strftime("%Y-%m-%d") if GITHUB_WINDOWS[window] is not None else None,
                )
            if window in GITHUB_TOPIC_WINDOWS:
                success = success and gh.topics_search(
                    run,
                    {
                        "language": language,
                        "window": window,
                    },
                    f"{language}",
                    created_after=(now - GITHUB_WINDOWS[window]).strftime("%Y-%m-%d") if GITHUB_WINDOWS[window] is not None else None,
                )
            print("")
    return success


def discover_repos(run):
    query = f"""
        INSERT INTO github_discovered_repo (ds, run_obj_id, github_repo_id, github_repo_full_name, languages)
        SELECT
            task.ds as ds,
            task.run_obj_id as run_obj_id,
            github_repo_id,
            github_repo_full_name,
            JSON_GROUP_ARRAY(JSON_EXTRACT(task.task_tags, '$.language')) AS languages
        FROM task INNER JOIN github_search_repo
            ON task.obj_id = github_search_repo.task_obj_id
        WHERE
            task.run_obj_id = {run.obj_id}
            AND task.task_kind = 'github_repositories_search'
        GROUP BY 1, 2, 3, 4
        ORDER BY 1, 5;
    """
    con = sqlite3.connect('growth-data.db')
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

def see_repos(run):
    query = f"""
        INSERT INTO github_seen_repo (ds, github_repo_id, github_repo_full_name, first_seen_ds, last_seen_ds, languages)
        SELECT
            '{run.ds}' AS ds,
            github_repo_id,
            github_repo_full_name,
            MIN(first_seen_ds) AS first_seen_ds,
            MAX(last_seen_ds) AS last_seen_ds,
            JSON_GROUP_ARRAY(language) AS languages
        FROM (
            SELECT DISTINCT
                github_repo_id,
                github_repo_full_name,
                ds AS first_seen_ds,
                ds AS last_seen_ds,
                json_each.value as language
            FROM
                github_discovered_repo, JSON_EACH(github_discovered_repo.languages)
            WHERE
                run_obj_id = {run.ds}

            UNION

            SELECT DISTINCT
                github_repo_id,
                github_repo_full_name,
                first_seen_ds,
                last_seen_ds,
                json_each.value as language
            FROM
                github_seen_repo, JSON_EACH(github_seen_repo.languages)
        )
        GROUP BY 1, 2
        ORDER BY 5;
    """
    con = sqlite3.connect('growth-data.db')
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="either 'daily' or 'weekly'")
    args = parser.parse_args()

    time_start = time()
    gh = GitHub()
    run = Run.new_run(args.mode)
    run.create_entry()

    success = True
    if args.mode == 'weekly':
        success = success and weekly_stats(run)
        success = success and discover_repos(run)
        success = success and see_repos(run)
    else:
        success = False
        print(f"unknown mode: {args.mode}", file=sys.stderr)

    run.run_status = "SUCCESS" if success else "HAS_ERRORS"
    run.update_entry()

    time_end = time()
    print(f"Completed in {timedelta(seconds=time_end - time_start)}")
