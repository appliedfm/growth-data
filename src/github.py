from dataclasses import dataclass
from datalite import datalite
from datetime import datetime, timedelta, timezone
import git
import json
import requests
import time
import urllib.parse

now_ds = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

@datalite(db_path="data.db")
@dataclass
class Run:
    ds: str
    ts: str
    run_commit_hash: str

    def new_run():
        ts = datetime.now(tz=timezone.utc)
        repo = git.Repo(search_parent_directories=True)

        return Run(
            ds = str(now_ds),
            ts = str(ts),
            run_commit_hash = str(repo.head.object.hexsha),
        )


@datalite(db_path="data.db")
@dataclass
class Task:
    ds: str
    ts: str
    run_obj_id: int
    task_kind: str
    task_args: str

    def new_task(run: Run, task_kind, task_args):
        ts = datetime.now(tz=timezone.utc)

        return Task(
            ds = str(now_ds),
            ts = str(ts),
            run_obj_id = run.obj_id,
            task_kind = task_kind,
            task_args = task_args
        )

@datalite(db_path="data.db")
@dataclass
class GitHub_Rest_Request:
    ds: str
    ts: str
    task_obj_id: int
    github_rest_request_url: str
    github_rest_request_status: int
    github_rest_request_data: str

@datalite(db_path="data.db")
@dataclass
class GitHub_Search:
    ds: str
    task_obj_id: int
    github_rest_request_obj_id: int
    github_search_q: str
    github_search_page: int
    github_search_per_page: int
    github_search_total_count: int
    github_search_incomplete_results: int
    github_search_len_items: int

    def of_json(task: Task, github_rest_request: GitHub_Rest_Request, q, page, per_page, search_results):
        return GitHub_Search(
            ds = str(now_ds),
            task_obj_id = task.obj_id,
            github_rest_request_obj_id = github_rest_request.obj_id,
            github_search_q = q,
            github_search_page = page,
            github_search_per_page = per_page,
            github_search_total_count = int(search_results["total_count"]),
            github_search_incomplete_results = int(search_results["incomplete_results"]),
            github_search_len_items = int(len(search_results["items"]))
        ) 

@datalite(db_path="data.db")
@dataclass
class GitHub_Search_Repo:
    ds: str
    task_obj_id: int
    github_search_obj_id: int
    github_repo_id: int
    github_repo_name: str
    github_repo_full_name: str
    github_repo_owner_login: str
    github_repo_owner_id: int
    github_repo_owner_type: str
    github_repo_fork: int
    github_repo_created_at: str
    github_repo_updated_at: str
    github_repo_pushed_at: str
    github_repo_git_url: str
    github_repo_ssh_url: str
    github_repo_clone_url: str
    github_repo_homepage: str
    github_repo_size: int
    github_repo_stargazers_count: int
    github_repo_watchers_count: int
    github_repo_language: str
    github_repo_has_issues: int
    github_repo_has_projects: int
    github_repo_has_downloads: int
    github_repo_has_wiki: int
    github_repo_has_pages: int
    github_repo_forks_count: int
    github_repo_archived: int
    github_repo_open_issues_count: int
    github_repo_license_key: str
    github_repo_license_name: str
    github_repo_license_spdx_id: str
    github_repo_license_url: str
    github_repo_allow_forking: int
    github_repo_is_template: int
    github_repo_topics: str
    github_repo_default_branch: str
    github_repo_score: int

    def of_json(task: Task, github_search: GitHub_Search, repo):
        return GitHub_Search_Repo(
            ds = str(now_ds),
            task_obj_id = task.obj_id,
            github_search_obj_id = int(github_search.obj_id),
            github_repo_id = int(repo["id"]),
            github_repo_name = str(repo["name"]),
            github_repo_full_name = str(repo["full_name"]),
            github_repo_owner_login = str(repo["owner"]["login"]) if repo["owner"] is not None else "",
            github_repo_owner_id = int(repo["owner"]["id"]) if repo["owner"] is not None else "",
            github_repo_owner_type = str(repo["owner"]["type"]) if repo["owner"] is not None else "",
            github_repo_fork = int(repo["fork"]),
            github_repo_created_at = str(repo["created_at"]),
            github_repo_updated_at = str(repo["updated_at"]),
            github_repo_pushed_at = str(repo["pushed_at"]),
            github_repo_git_url = str(repo["git_url"]),
            github_repo_ssh_url = str(repo["ssh_url"]),
            github_repo_clone_url = str(repo["clone_url"]),
            github_repo_homepage = str(repo["homepage"]),
            github_repo_size = int(repo["size"]),
            github_repo_stargazers_count = int(repo["stargazers_count"]),
            github_repo_watchers_count = int(repo["watchers_count"]),
            github_repo_language = str(repo["language"]),
            github_repo_has_issues = int(repo["has_issues"]),
            github_repo_has_projects = int(repo["has_projects"]),
            github_repo_has_downloads = int(repo["has_downloads"]),
            github_repo_has_wiki = int(repo["has_wiki"]),
            github_repo_has_pages = int(repo["has_pages"]),
            github_repo_forks_count = int(repo["forks_count"]),
            github_repo_archived = int(repo["archived"]),
            github_repo_open_issues_count = int(repo["open_issues_count"]),
            github_repo_license_key = str(repo["license"]["key"]) if repo["license"] is not None else "",
            github_repo_license_name = str(repo["license"]["name"]) if repo["license"] is not None else "",
            github_repo_license_spdx_id = str(repo["license"]["spdx_id"]) if repo["license"] is not None else "",
            github_repo_license_url = str(repo["license"]["url"]) if repo["license"] is not None else "",
            github_repo_allow_forking = int(repo["allow_forking"]),
            github_repo_is_template = int(repo["is_template"]),
            github_repo_topics = str(repo["topics"]),
            github_repo_default_branch = str(repo["default_branch"]),
            github_repo_score = int(repo["score"]),
        )

class GitHub:
    def __init__(self, query_delay=3, search_delay=10):
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
                time.sleep(sleep_for)

        ts = datetime.now(tz=timezone.utc)
        if is_search:
            self.last_search = ts
        else:
            self.last_query = ts
        return ts

    def do_request(self, task, api_url, is_search=False):
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
        return github_rest_request, github_rest_request_data

    def do_repositories_search(self, task, q, page, per_page, fetch_all):
        print(f"repositories_search(q={q}, page={page}, per_page={per_page}, fetch_all={fetch_all})")

        github_rest_request, github_rest_request_data = self.do_request(
            task,
            f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&page={page}&per_page={per_page}",
            is_search=True
        )

        if 200 != github_rest_request.github_rest_request_status:
            print(f" ... error: status {github_rest_request.github_rest_request_status}")
            return

        total_count = int(github_rest_request_data["total_count"])
        total_so_far = (page - 1) * per_page + int(len(github_rest_request_data["items"]))
        print(f"  ... success: {total_so_far} of {total_count}")

        # Log the top-line results
        github_search = GitHub_Search.of_json(
            task,
            github_rest_request,
            q,
            page,
            per_page,
            github_rest_request_data
        )
        github_search.create_entry()

        if fetch_all:
            # Log each of the repos
            for github_search_repo_data in github_rest_request_data["items"]:
                github_search_repo = GitHub_Search_Repo.of_json(
                    task,
                    github_search,
                    github_search_repo_data
                )
                github_search_repo.create_entry()

            # Continue to the next page
            if total_so_far < total_count:
                self.do_repositories_search(
                    task,
                    q,
                    page = page + 1,
                    per_page = per_page,
                    fetch_all = fetch_all
                )

    def repositories_search(self, run: Run, q, page=1, per_page=75, fetch_all=False):
        if not fetch_all:
            per_page=1

        task = Task.new_task(
            run,
            task_kind = "github_repositories_search",
            task_args = json.dumps({
                "q": q,
                "page": page,
                "per_page": per_page,
                "fetch_all": fetch_all
            })
        )
        task.create_entry()
        
        self.do_repositories_search(
            task,
            q,
            page = page,
            per_page = per_page,
            fetch_all = fetch_all
        )



gh = GitHub()
time_start = time.time()
run = Run.new_run()
run.create_entry()

FULL_LANGUAGES = [
    "coq",
    "agda",
    "lean",
    "ada",
    "idris",
    "tla"
]

for language in FULL_LANGUAGES:
    gh.repositories_search(run, f"language:{language} and fork:false", fetch_all=True)

PARTIAL_LANGUAGES = [
    "ocaml",
    "haskell",
    "go",
    "rust",
    "erlang",
    "java",
    "assembly",
    "c",
    "c++",
    "python",
    "fortran",
    "r",
    "terraform",
    "verilog"
]

for language in PARTIAL_LANGUAGES:
    gh.repositories_search(run, f"language:{language} and fork:false")


time_end = time.time()
print(f"Completed in {timedelta(seconds=time_end - time_start)}")
