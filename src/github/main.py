from config import *
from datetime import datetime, timedelta, timezone
from github import GitHub
from tabulate import tabulate
from time import sleep, time
import argparse
import json
import pandas as pd
import os
import sys


def write_df(context, task_outdir, name, df):
    df.to_csv(os.path.join(task_outdir, f"{context['now']['ds']}-{name}.csv"), index=False)
    with open(os.path.join(task_outdir, f"{context['now']['ds']}-{name}.md"), 'w') as f:
        f.write(tabulate(df, headers='keys', showindex=False, tablefmt='github'))
        f.write("\n")


def repo_stats(context, task_outdir, repos_df):
    def q10(x):
        return x.quantile(0.1)

    def q25(x):
        return x.quantile(0.25)

    def q50(x):
        return x.quantile(0.5)

    def q75(x):
        return x.quantile(0.75)

    def q90(x):
        return x.quantile(0.9)

    grouped_df = repos_df.groupby(['ds', 'sortby', 'pushed', 'language'], as_index=False).agg(
        repos=('full_name', 'count'),

        repos_with_license=('has_license', 'sum'),
        repos_with_issues=('has_issues', 'sum'),
        repos_with_downloads=('has_downloads', 'sum'),
        repos_with_wiki=('has_wiki', 'sum'),
        repos_with_projects=('has_projects', 'sum'),
        repos_with_pages=('has_pages', 'sum'),

        size_min=('size', 'min'),
        size_max=('size', 'max'),
        size_sum=('size', 'sum'),
        size_avg=('size', 'mean'),
        size_std=('size', 'std'),
        size_q10=('size', q10),
        size_q25=('size', q25),
        size_q50=('size', q50),
        size_q75=('size', q75),
        size_q90=('size', q90),

        stargazers_count_min=('stargazers_count', 'min'),
        stargazers_count_max=('stargazers_count', 'max'),
        stargazers_count_sum=('stargazers_count', 'sum'),
        stargazers_count_avg=('stargazers_count', 'mean'),
        stargazers_count_std=('stargazers_count', 'std'),
        stargazers_count_q10=('stargazers_count', q10),
        stargazers_count_q25=('stargazers_count', q25),
        stargazers_count_q50=('stargazers_count', q50),
        stargazers_count_q75=('stargazers_count', q75),
        stargazers_count_q90=('stargazers_count', q90),

        forks_count_min=('forks_count', 'min'),
        forks_count_max=('forks_count', 'max'),
        forks_count_sum=('forks_count', 'sum'),
        forks_count_avg=('forks_count', 'mean'),
        forks_count_std=('forks_count', 'std'),
        forks_count_q10=('forks_count', q10),
        forks_count_q25=('forks_count', q25),
        forks_count_q50=('forks_count', q50),
        forks_count_q75=('forks_count', q75),
        forks_count_q90=('forks_count', q90),

        open_issues_count_min=('open_issues_count', 'min'),
        open_issues_count_max=('open_issues_count', 'max'),
        open_issues_count_sum=('open_issues_count', 'sum'),
        open_issues_count_avg=('open_issues_count', 'mean'),
        open_issues_count_std=('open_issues_count', 'std'),
        open_issues_count_q10=('open_issues_count', q10),
        open_issues_count_q25=('open_issues_count', q25),
        open_issues_count_q50=('open_issues_count', q50),
        open_issues_count_q75=('open_issues_count', q75),
        open_issues_count_q90=('open_issues_count', q90),

        topics_count_min=('topics_count', 'min'),
        topics_count_max=('topics_count', 'max'),
        topics_count_sum=('topics_count', 'sum'),
        topics_count_avg=('topics_count', 'mean'),
        topics_count_std=('topics_count', 'std'),
        topics_count_q10=('topics_count', q10),
        topics_count_q25=('topics_count', q25),
        topics_count_q50=('topics_count', q50),
        topics_count_q75=('topics_count', q75),
        topics_count_q90=('topics_count', q90),
    )
    return grouped_df

def repo_query_string(context, query):
    language = query['args']['language']
    pushed = context['windows'][query['args']['pushed']]
    q = f"language:{language} and fork:false"
    if pushed is not None:
        q = q + f" and pushed:>{pushed}"
    return q

def repo_task(context, gh, dataset_name, task_outdir, args, queries):
    print(f"repo_task({dataset_name}, {task_outdir}, {json.dumps(args)}, {len(queries)} queries)", flush=True)
    repos_df = pd.DataFrame(dtype=float, columns=(
        'ds',
        'sortby',
        'pushed',
        'language',
        'full_name',
        'owner_type',
        'size',
        'stargazers_count',
        'forks_count',
        'open_issues_count',
        'topics_count',
        'license_key',
        'license_spdx_id',
        'has_license',
        'has_issues',
        'has_downloads',
        'has_wiki',
        'has_projects',
        'has_pages',
        'created_at',
        'updated_at',
        'pushed_at',
        'topics',
        ))
    counts_df = pd.DataFrame(columns=('ds', 'sortby', 'pushed', 'language', 'repo_count', 'repo_data_count'))
    for query in queries:
        status, total, repos = gh.do_search(
            search_type="repositories",
            fetch_all=args['stats'],
            q=repo_query_string(context, query),
            sortby=query['args']['sort-by'],
        )
        if 200 != status:
            print(f"  ... error: status={status}", file=sys.stderr, flush=True)
            return
        counts_df = counts_df.append(
            {
                'ds': context['now']['ds'],
                'sortby': query['args']['sort-by'],
                'pushed': query['args']['pushed'],
                'language': query['args']['language'],
                'repo_count': total,
                'repo_data_count': len(repos),
            },
            ignore_index=True
        )
        for repo in repos:
            repos_df = repos_df.append(
                {
                    'ds': context['now']['ds'],
                    'sortby': query['args']['sort-by'],
                    'pushed': query['args']['pushed'],
                    'language': query['args']['language'],
                    'full_name': str(repo["full_name"]),
                    'owner_type': str(repo["owner"]["type"]) if repo["owner"] is not None else "",
                    'size': int(repo["size"]),
                    'stargazers_count': int(repo["stargazers_count"]),
                    'forks_count': int(repo["forks_count"]),
                    'open_issues_count': int(repo["open_issues_count"]),
                    'topics_count': int(len(repo["topics"])),
                    'license_key': str(repo["license"]["key"]) if repo["license"] is not None else "",
                    'license_spdx_id': str(repo["license"]["spdx_id"]) if repo["license"] is not None else "",
                    'has_license': 1 if repo["license"] is not None and "" != repo["license"]["key"] else 0,
                    'has_issues': int(repo["has_issues"]),
                    'has_downloads': int(repo["has_downloads"]),
                    'has_wiki': int(repo["has_wiki"]),
                    'has_projects': int(repo["has_projects"]),
                    'has_pages': int(repo["has_pages"]),
                    'created_at': str(repo["created_at"]),
                    'updated_at': str(repo["updated_at"]),
                    'pushed_at': str(repo["pushed_at"]),
                    'topics': str(repo["topics"]),
                },
                ignore_index=True
            )
    if context['saveraw']:
        write_df(context, task_outdir, 'repos', repos_df)
    write_df(context, task_outdir, 'repo_counts', counts_df)
    if args['stats']:
        grouped_df = repo_stats(context, task_outdir, repos_df)
        write_df(context, task_outdir, 'repo_stats_overall', grouped_df)
        joined_df = pd.merge(repos_df, grouped_df, on=['ds', 'sortby', 'pushed', 'language'])
        COLUMNS = ['size', 'stargazers_count', 'forks_count', 'open_issues_count', 'topics_count']
        QUANTS = [
            ('< q10', None, 'q10'),
            ('q10 - q25', 'q10', 'q25'),
            ('q25 - q50', 'q25', 'q50'),
            ('q50 - q75', 'q50', 'q75'),
            ('q75 - q90', 'q75', 'q90'),
            ('q90 <', 'q90', None)
        ]
        for column in COLUMNS:
            quant_dfs = []
            for q_name, q_lo, q_hi in QUANTS:
                q_df = joined_df
                q_df = q_df[q_df[f"{column}_{q_lo}"] <= q_df[column]] if q_lo is not None else q_df
                q_df = q_df[q_df[column] < q_df[f"{column}_{q_hi}"]] if q_hi is not None else q_df
                quant_df = repo_stats(context, task_outdir, q_df)
                quant_df.insert(4, 'quantile', q_name)
                quant_dfs.append(quant_df)
            quant_df = pd.concat(quant_dfs).sort_values(by=['ds', 'sortby', 'pushed', 'language', 'quantile'])
            write_df(context, task_outdir, f"repo_stats_quantile_by_{column}", quant_df)


def user_query_string(context, query):
    language = query['args']['language']
    created = context['windows'][query['args']['created']]
    q = f"language:{language}"
    if created is not None:
        q = q + f" and created:>{created}"
    return q

def user_task(context, gh, dataset_name, task_outdir, args, queries):
    print(f"user_task({dataset_name}, {task_outdir}, {json.dumps(args)}, {len(queries)} queries)", flush=True)
    counts_df = pd.DataFrame(columns=('ds', 'created', 'language', 'user_count'))
    for query in queries:
        status, total, _ = gh.do_search(
            search_type="users",
            q=user_query_string(context, query),
        )
        if 200 != status:
            print(f"  ... error: status={status}", file=sys.stderr, flush=True)
            return
        counts_df = counts_df.append(
            {
                'ds': context['now']['ds'],
                'created': query['args']['created'],
                'language': query['args']['language'],
                'user_count': total,
            },
            ignore_index=True
        )
    write_df(context, task_outdir, 'user_counts', counts_df)

def plan_tasks(dataset_name):
    if dataset_name not in GITHUB_DATASETS:
        print(f"unknown task: {dataset_name}", file=sys.stderr, flush=True)
        exit(-1)
    task = GITHUB_DATASETS[dataset_name]
    if "repo" == task["type"]:
        task_plan = {
            "fn": repo_task,
            "args": {
                "stats": task['stats'],
            },
            "queries": [],
        }
        for sortby in task['args']["sort-by"]:
            for pushed in task['args']['pushed']:
                for language in task['args']['language']:
                    task_plan["queries"].append({
                        "est_time_lo": GITHUB_SEARCH_DELAY,
                        "est_time_hi": GITHUB_SEARCH_DELAY * (10 if task_plan['args']['stats'] else 1),
                        "args": {
                            "sort-by": sortby,
                            "pushed": pushed,
                            "language": language,
                        },
                    })
        return task_plan
    elif "user" == task["type"]:
        task_plan = {
            "fn": user_task,
            "args": {},
            "queries": []
        }
        for created in task['args']["created"]:
            for language in task['args']['language']:
                task_plan["queries"].append({
                    "fn": user_task,
                    "est_time_lo": GITHUB_SEARCH_DELAY,
                    "est_time_hi": GITHUB_SEARCH_DELAY,
                    "args": {
                        "created": created,
                        "language": language,
                    },
                })
        return task_plan
    else:
        print(f"unknown task type: {task['type']}", file=sys.stderr, flush=True)
        exit(-1)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_names", help="one or more datasets from the configuration file", nargs='+')
    parser.add_argument("-o", "--outdir", help="output directory", required=True)
    parser.add_argument("--noexec", help="print information about the plan but do not run the plan", action='store_true')
    parser.add_argument("--saveraw", help="save all raw search results", action='store_true')
    parser.add_argument("--disable_ratelimit", help="disable ratelimiting", action='store_true')
    parser.set_defaults(noexec=False)
    parser.set_defaults(saveraw=False)
    parser.set_defaults(disable_ratelimit=False)
    args = parser.parse_args()

    ts = datetime.now(tz=timezone.utc)
    context = {
        "now": {
            "ts": str(ts),
            "ds": ts.strftime("%Y-%m-%d"),
            "month": ts.strftime("%m"),
            "year": ts.strftime("%Y"),
        },
        "outdir": args.outdir,
        "saveraw": args.saveraw,
        "windows": {},
    }
    for window in GITHUB_WINDOWS:
        context['windows'][window] = (ts - GITHUB_WINDOWS[window]).strftime("%Y-%m-%d") if GITHUB_WINDOWS[window] is not None else None
    print(f"{json.dumps(context, indent=4, sort_keys=True)}\n", flush=True)

    time_start = time()

    dataset_names = GITHUB_DATASETS.keys() if "all" in args.dataset_names else args.dataset_names
    tasks = {}
    for dataset_name in dataset_names:
        tasks[dataset_name] = plan_tasks(dataset_name)

    print("Planning tasks ...", flush=True)
    total_est_time_lo = 0
    total_est_time_hi = 0
    total_query_count = 0
    for dataset_name in tasks:
        est_time_lo = 0
        est_time_hi = 0
        query_count = len(tasks[dataset_name]["queries"])
        for task in tasks[dataset_name]["queries"]:
            est_time_lo = est_time_lo + task["est_time_lo"]
            est_time_hi = est_time_hi + task["est_time_hi"]
        total_est_time_lo = total_est_time_lo + est_time_lo
        total_est_time_hi = total_est_time_hi + est_time_hi
        total_query_count = total_query_count + query_count
        est_time_lo = timedelta(seconds=est_time_lo)
        est_time_hi = timedelta(seconds=est_time_hi)
        print(f"{dataset_name}: {query_count} queries planned; estimated time: {est_time_lo} - {est_time_hi}", flush=True)

    total_est_time_lo = timedelta(seconds=total_est_time_lo)
    total_est_time_hi = timedelta(seconds=total_est_time_hi)
    print(f"{len(tasks)} tasks ({total_query_count} queries) planned; estimated total time: {total_est_time_lo} - {total_est_time_hi}\n", flush=True)

    if args.noexec:
        print("exiting (noexec)", flush=True)
    else:
        gh = GitHub(disable_ratelimit=args.disable_ratelimit)
        for dataset_name in tasks:
            task_outdir = os.path.join(
                context['outdir'],
                dataset_name,
                context['now']['year'],
                context['now']['month']
            )
            os.makedirs(task_outdir, exist_ok=True)
            tasks[dataset_name]["fn"](
                context = context,
                gh = gh,
                dataset_name = dataset_name,
                task_outdir = task_outdir,
                args = tasks[dataset_name]['args'],
                queries = tasks[dataset_name]["queries"]
            )

    time_end = time()
    print(f"\nCompleted in {timedelta(seconds=time_end - time_start)} (estimated total time was {total_est_time_lo} - {total_est_time_hi})", flush=True)
