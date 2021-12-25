from dataclasses import dataclass
from datalite import datalite
from datetime import datetime, timedelta, timezone
import git
import json
import requests
import time
import urllib.parse

now = datetime.now(tz=timezone.utc)
now_ds = now.strftime("%Y-%m-%d")

@datalite(db_path="github.db")
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


@datalite(db_path="github.db")
@dataclass
class Task:
    ds: str
    ts: str
    run_obj_id: int
    task_kind: str
    task_args: str
    task_tags: str

    def new_task(run: Run, task_kind, task_args, task_tags):
        ts = datetime.now(tz=timezone.utc)

        return Task(
            ds = str(now_ds),
            ts = str(ts),
            run_obj_id = run.obj_id,
            task_kind = task_kind,
            task_args = task_args,
            task_tags = str(task_tags),
        )

@datalite(db_path="github.db")
@dataclass
class GitHub_Rest_Request:
    ds: str
    ts: str
    task_obj_id: int
    github_rest_request_url: str
    github_rest_request_status: int
    github_rest_request_data: str

@datalite(db_path="github.db")
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

@datalite(db_path="github.db")
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

@datalite(db_path="github.db")
@dataclass
class GitHub_Search_User:
    ds: str
    task_obj_id: int
    github_search_obj_id: int
    github_user_login: str
    github_user_id: int
    github_user_type: str

    def of_json(task: Task, github_search: GitHub_Search, user):
        return GitHub_Search_User(
            ds = str(now_ds),
            task_obj_id = task.obj_id,
            github_search_obj_id = int(github_search.obj_id),
            github_user_login = str(user["login"]),
            github_user_id = int(user["id"]),
            github_user_type = str(user["type"])
        )

@datalite(db_path="github.db")
@dataclass
class GitHub_Search_Topic:
    ds: str
    task_obj_id: int
    github_search_obj_id: int
    github_topic_name: str
    github_topic_display_name: str
    github_topic_short_description: str
    github_topic_description: str
    github_topic_created_by: str
    github_topic_released: str
    github_topic_created_at: str
    github_topic_updated_at: str
    github_topic_featured: int
    github_topic_curated: int
    github_topic_score: int

    def of_json(task: Task, github_search: GitHub_Search, user):
        return GitHub_Search_Topic(
            ds = str(now_ds),
            task_obj_id = task.obj_id,
            github_search_obj_id = int(github_search.obj_id),
            github_topic_name = str(user["name"]),
            github_topic_display_name = str(user["display_name"]),
            github_topic_short_description = str(user["short_description"]),
            github_topic_description = str(user["description"]),
            github_topic_created_by = str(user["created_by"]),
            github_topic_released = str(user["released"]),
            github_topic_created_at = str(user["created_at"]),
            github_topic_updated_at = str(user["updated_at"]),
            github_topic_featured = int(user["featured"]),
            github_topic_curated = int(user["curated"]),
            github_topic_score = int(user["score"])
        )


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
                time.sleep(sleep_for)

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
                self.do_search(
                    task,
                    target,
                    item_of_json,
                    q,
                    page = page + 1,
                    per_page = per_page,
                    fetch_all = fetch_all
                )

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

        self.do_search(
            task,
            "repositories",
            GitHub_Search_Repo.of_json,
            q + (f" and pushed:>{pushed_since}" if pushed_since is not None else ""),
            page = page,
            per_page = per_page,
            fetch_all = fetch_all
        )

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
        
        self.do_search(
            task,
            "users",
            GitHub_Search_User.of_json,
            q + (f" and created:>{created_after}" if created_after is not None else ""),
            page = page,
            per_page = per_page,
            fetch_all = fetch_all
        )

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
        
        self.do_search(
            task,
            "topics",
            GitHub_Search_Topic.of_json,
            q + (f" and created:>{created_after}" if created_after is not None else ""),
            page = page,
            per_page = per_page,
            fetch_all = fetch_all
        )


CUTOFFS = {
    "alltime": None,
    "001_1week": (now - timedelta(weeks=1)).strftime("%Y-%m-%d"),
    "004_1month": (now - timedelta(weeks=1*4)).strftime("%Y-%m-%d"),
    "012_3month": (now - timedelta(weeks=3*4)).strftime("%Y-%m-%d"),
    "024_6month": (now - timedelta(weeks=6*4)).strftime("%Y-%m-%d"),
    "052_1year": (now - timedelta(weeks=52)).strftime("%Y-%m-%d"),
    "156_3year": (now - timedelta(weeks=3*52)).strftime("%Y-%m-%d"),
    "260_5year": (now - timedelta(weeks=5*52)).strftime("%Y-%m-%d"),
    "520_10year": (now - timedelta(weeks=10*52)).strftime("%Y-%m-%d"),
}

FULL_LANGUAGES = [
    "coq",
    "isabelle",
    "agda",
    "lean",
    "ada",
    "idris",
    "tla"
]

PARTIAL_LANGUAGES = [
    "ocaml",
    "haskell",
    "prolog",
    "go",
    "rust",
    "erlang",
    "java",
    "scala",
    "assembly",
    "c",
    "c++",
    "python",
    "fortran",
    "r",
    "terraform",
    "verilog"
]

FETCH_ALL = [
    (language, cutoff)
    for language in FULL_LANGUAGES
    for cutoff in [
        "alltime",
        "004_1month",
        "024_6month",
        "052_1year",
        "156_3year",
    ]
]

USER_CUTOFFS = [
    "alltime",
    "004_1month",
    "052_1year",
    "260_5year",
]

TOPIC_CUTOFFS = [
    "alltime",
]


gh = GitHub()
time_start = time.time()
run = Run.new_run()
run.create_entry()

for cutoff in CUTOFFS:
    for language in (FULL_LANGUAGES + PARTIAL_LANGUAGES):
        print(f"q={language}, cutoff={cutoff} ...")
        gh.repositories_search(
            run,
            {
                "language": language,
                "cutoff": cutoff,
            },
            f"language:{language} and fork:false",
            pushed_since=CUTOFFS[cutoff],
            fetch_all=(language, cutoff) in FETCH_ALL,
        )
        if cutoff in USER_CUTOFFS:
            gh.users_search(
                run,
                {
                    "language": language,
                    "cutoff": cutoff,
                },
                f"language:{language}",
                created_after=CUTOFFS[cutoff],
            )
        if cutoff in TOPIC_CUTOFFS:
            gh.topics_search(
                run,
                {
                    "language": language,
                    "cutoff": cutoff,
                },
                f"{language}",
                created_after=CUTOFFS[cutoff],
            )
        print("")

time_end = time.time()
print(f"Completed in {timedelta(seconds=time_end - time_start)}")
