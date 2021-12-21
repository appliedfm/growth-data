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
    commit_hash: str

    def new_run():
        ts = datetime.now(tz=timezone.utc)
        repo = git.Repo(search_parent_directories=True)

        return Run(
            ds = str(now_ds),
            ts = str(ts),
            commit_hash = str(repo.head.object.hexsha),
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
    url: str
    status: int
    data: str

@datalite(db_path="data.db")
@dataclass
class GitHub_Search:
    ds: str
    task_obj_id: int
    github_rest_request_obj_id: int
    q: str
    page: int
    per_page: int
    total_count: int
    incomplete_results: int
    len_items: int

    def of_json(task: Task, github_rest_request: GitHub_Rest_Request, q, page, per_page, search_results):
        return GitHub_Search(
            ds = str(now_ds),
            task_obj_id = task.obj_id,
            github_rest_request_obj_id = github_rest_request.obj_id,
            q = q,
            page = page,
            per_page = per_page,
            total_count = int(search_results["total_count"]),
            incomplete_results = int(search_results["incomplete_results"]),
            len_items = int(len(search_results["items"]))
        ) 

@datalite(db_path="data.db")
@dataclass
class GitHub_Search_Repo:
    ds: str
    task_obj_id: int
    github_search_obj_id: int
    repo_id: int
    repo_name: str
    repo_full_name: str
    owner_login: str
    owner_id: int
    owner_type: str
    repo_fork: int
    repo_created_at: str
    repo_updated_at: str
    repo_pushed_at: str
    repo_git_url: str
    repo_ssh_url: str
    repo_clone_url: str
    repo_homepage: str
    repo_size: int
    repo_stargazers_count: int
    repo_watchers_count: int
    repo_language: str
    repo_has_issues: int
    repo_has_projects: int
    repo_has_downloads: int
    repo_has_wiki: int
    repo_has_pages: int
    repo_forks_count: int
    repo_archived: int
    repo_open_issues_count: int
    repo_license_key: str
    repo_license_name: str
    repo_license_spdx_id: str
    repo_license_url: str
    repo_allow_forking: int
    repo_is_template: int
    repo_topics: str
    repo_default_branch: str
    repo_score: int

    def of_json(task: Task, github_search: GitHub_Search, repo):
        return GitHub_Search_Repo(
            ds = str(now_ds),
            task_obj_id = task.obj_id,
            github_search_obj_id = int(github_search.obj_id),
            repo_id = int(repo["id"]),
            repo_name = str(repo["name"]),
            repo_full_name = str(repo["full_name"]),
            owner_login = str(repo["owner"]["login"]) if repo["owner"] is not None else "",
            owner_id = int(repo["owner"]["id"]) if repo["owner"] is not None else "",
            owner_type = str(repo["owner"]["type"]) if repo["owner"] is not None else "",
            repo_fork = int(repo["fork"]),
            repo_created_at = str(repo["created_at"]),
            repo_updated_at = str(repo["updated_at"]),
            repo_pushed_at = str(repo["pushed_at"]),
            repo_git_url = str(repo["git_url"]),
            repo_ssh_url = str(repo["ssh_url"]),
            repo_clone_url = str(repo["clone_url"]),
            repo_homepage = str(repo["homepage"]),
            repo_size = int(repo["size"]),
            repo_stargazers_count = int(repo["stargazers_count"]),
            repo_watchers_count = int(repo["watchers_count"]),
            repo_language = str(repo["language"]),
            repo_has_issues = int(repo["has_issues"]),
            repo_has_projects = int(repo["has_projects"]),
            repo_has_downloads = int(repo["has_downloads"]),
            repo_has_wiki = int(repo["has_wiki"]),
            repo_has_pages = int(repo["has_pages"]),
            repo_forks_count = int(repo["forks_count"]),
            repo_archived = int(repo["archived"]),
            repo_open_issues_count = int(repo["open_issues_count"]),
            repo_license_key = str(repo["license"]["key"]) if repo["license"] is not None else "",
            repo_license_name = str(repo["license"]["name"]) if repo["license"] is not None else "",
            repo_license_spdx_id = str(repo["license"]["spdx_id"]) if repo["license"] is not None else "",
            repo_license_url = str(repo["license"]["url"]) if repo["license"] is not None else "",
            repo_allow_forking = int(repo["allow_forking"]),
            repo_is_template = int(repo["is_template"]),
            repo_topics = str(repo["topics"]),
            repo_default_branch = str(repo["default_branch"]),
            repo_score = int(repo["score"]),
        )

class GitHub:
    def __init__(self, query_delay):
        self.last_query = None
        self.query_delay = query_delay

    def do_request(self, task, api_url):
        print(f"  ... do_request(\"{api_url}\")")
        ts = datetime.now(tz=timezone.utc)
        if self.last_query is not None:
            second_since_last_query = (ts - self.last_query).total_seconds()
            if self.query_delay > second_since_last_query:
                delay = self.query_delay - second_since_last_query
                print(f"  ... rate limit: sleeping for {delay} seconds ...")
                time.sleep(delay)
        ts = datetime.now(tz=timezone.utc)
        self.last_query = ts
        response = requests.get(api_url)
        status = response.status_code
        github_rest_request_data = response.json()
        github_rest_request = GitHub_Rest_Request(
            ds = str(now_ds),
            ts = str(ts),
            task_obj_id = task.obj_id,
            url = str(api_url),
            status = int(status),
            data = str(github_rest_request_data)
        )
        github_rest_request.create_entry()
        return github_rest_request, github_rest_request_data

    def do_repositories_search(self, task, q, page, per_page, fetch_all):
        print(f"repositories_search(q=\"{q}\", page={page}, per_page={per_page}, fetch_all={fetch_all})")

        github_rest_request, github_rest_request_data = self.do_request(
            task,
            f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&page={page}&per_page={per_page}"
        )

        if 200 != github_rest_request.status:
            print(f" ... error: status {github_rest_request.status}")
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
                github_search_repo = GitHub_Search_Repo.of_json(task, github_search, github_search_repo_data)
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



gh = GitHub(query_delay=10)
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
