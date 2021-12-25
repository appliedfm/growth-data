from dataclasses import dataclass
from datalite import datalite
from orm import Task

@datalite(db_path="growth-data.db")
@dataclass
class GitHub_Rest_Request:
    ds: str
    ts: str
    task_obj_id: int
    github_rest_request_url: str
    github_rest_request_status: int
    github_rest_request_data: str

@datalite(db_path="growth-data.db")
@dataclass
class GitHub_Search:
    ds: str
    task_obj_id: int
    github_search_type: str
    github_rest_request_obj_id: int
    github_search_q: str
    github_search_page: int
    github_search_per_page: int
    github_search_total_count: int
    github_search_incomplete_results: int
    github_search_len_items: int

    def of_json(task: Task, github_search_type, github_rest_request: GitHub_Rest_Request, q, page, per_page, search_results):
        return GitHub_Search(
            ds = task.ds,
            task_obj_id = task.obj_id,
            github_search_type = github_search_type,
            github_rest_request_obj_id = github_rest_request.obj_id,
            github_search_q = q,
            github_search_page = page,
            github_search_per_page = per_page,
            github_search_total_count = int(search_results["total_count"]),
            github_search_incomplete_results = int(search_results["incomplete_results"]),
            github_search_len_items = int(len(search_results["items"]))
        ) 

@datalite(db_path="growth-data.db")
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
            ds = task.ds,
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

@datalite(db_path="growth-data.db")
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
            ds = task.ds,
            task_obj_id = task.obj_id,
            github_search_obj_id = int(github_search.obj_id),
            github_user_login = str(user["login"]),
            github_user_id = int(user["id"]),
            github_user_type = str(user["type"])
        )

@datalite(db_path="growth-data.db")
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
            ds = task.ds,
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

@datalite(db_path="growth-data.db")
@dataclass
class GitHub_Discovered_Repo:
    ds: str
    run_obj_id: int
    github_repo_id: int
    github_repo_full_name: str
    languages: str

@datalite(db_path="growth-data.db")
@dataclass
class GitHub_Seen_Repo:
    ds: str
    run_obj_id: int
    github_repo_id: int
    github_repo_full_name: str
    first_seen_ds: str
    last_seen_ds: str
    languages: str
