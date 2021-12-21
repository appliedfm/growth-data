from dataclasses import dataclass
from datalite import datalite
from datetime import datetime, timedelta, timezone
import base64
import requests
import time
import zlib

now_ds = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

@datalite(db_path="data.db")
@dataclass
class GitHub_Request:
    ds: str
    ts: str
    url: str
    status: int
    data: str

@datalite(db_path="data.db")
@dataclass
class GitHub_Repos_Search:
    ds: str
    request_id: int
    q: str
    page: int
    per_page: int
    total_count: int
    incomplete_results: int
    len_items: int

@datalite(db_path="data.db")
@dataclass
class GitHub_Repos_Search_Repo:
    ds: str
    repos_search_id: int
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


class GitHub:
    def __init__(self, query_delay):
        self.last_query = None
        self.query_delay = query_delay

    def do_request(self, api_url):
        ts = datetime.now(tz=timezone.utc)
        if self.last_query is not None:
            second_since_last_query = (ts - self.last_query).total_seconds()
            print(f"Seconds since last query: {second_since_last_query}")
            if self.query_delay > second_since_last_query:
                delay = self.query_delay - second_since_last_query
                print(f"Sleeping for {delay} seconds ...")
                time.sleep(delay)
        self.last_query = ts
        response = requests.get(api_url)
        status = response.status_code
        data = response.json()
        req = GitHub_Request(
            ds = str(now_ds),
            ts = str(ts),
            url = str(api_url),
            status = int(status),
            data = str(data)
        )
        req.create_entry()
        return req, data

    def repositories_search(self, q, page=1, per_page=75, fetch_all=False):
        req, data = self.do_request(f"https://api.github.com/search/repositories?q={q}&page={page}&per_page={per_page}")
        if 200 != req.status:
            print(f"Error: status {req.status}")
            return

        total_count = int(data["total_count"])
        total_so_far = (page - 1) * per_page + int(len(data["items"]))
        print(f"repositories_search(q=\"{q}\", fetch_all={fetch_all}): {total_so_far} of {total_count}")

        # Log the top-line results
        res = GitHub_Repos_Search(
            ds = str(now_ds),
            request_id = int(req.obj_id),
            q = str(q),
            page = int(page),
            per_page = int(per_page),
            total_count = total_count,
            incomplete_results = int(data["incomplete_results"]),
            len_items = int(len(data["items"]))
        )
        res.create_entry()

        # Log each of the repos
        for repo in data["items"]:
            rep = GitHub_Repos_Search_Repo(
                ds = str(now_ds),
                repos_search_id = int(res.obj_id),
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
            rep.create_entry()

        # Continue on to the next page of results
        if fetch_all and total_so_far < total_count:
            self.repositories_search(q, page = page + 1, per_page = per_page, fetch_all = fetch_all)



gh = GitHub(query_delay=10)
time_start = time.time()


FULL_LANGUAGES = ["coq", "agda", "lean"]

for language in FULL_LANGUAGES:
    gh.repositories_search(f"language:{language} and fork:false", fetch_all=True)


PARTIAL_LANGUAGES = ["ocaml", "haskell", "go", "rust", "erlang", "java", "python3", "python2", "c",]

for language in PARTIAL_LANGUAGES:
    gh.repositories_search(f"language:{language} and fork:false")


time_end = time.time()
print(f"Completed in {timedelta(seconds=time_end - time_start)}")
