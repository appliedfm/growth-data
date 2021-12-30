from config import *
from github import GitHub
from repo import *
from user import *

from datetime import datetime, timedelta, timezone
from time import time
import argparse
import json
import os
import sys

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
    parser.add_argument("--savemd", help="save results as GitHub markdown (in addition to csv)", action='store_true')
    parser.add_argument("--saveraw", help="save all raw search results", action='store_true')
    parser.add_argument("--disable_ratelimit", help="disable ratelimiting", action='store_true')
    parser.set_defaults(noexec=False)
    parser.set_defaults(savemd=False)
    parser.set_defaults(saveraw=False)
    parser.set_defaults(disable_ratelimit=False)
    args = parser.parse_args()

    ts = datetime.now(tz=timezone.utc)
    context = {
        'now': {
            'ts': str(ts),
            'ds': ts.strftime("%Y-%m-%d"),
            'month': ts.strftime("%m"),
            'year': ts.strftime("%Y"),
        },
        'outdir': args.outdir,
        'savemd': args.savemd,
        'saveraw': args.saveraw,
        'windows': {},
    }
    for window in GITHUB_WINDOWS:
        context['windows'][window] = (ts - GITHUB_WINDOWS[window]).strftime("%Y-%m-%d") if GITHUB_WINDOWS[window] is not None else None
    print(f"{json.dumps(context, indent=4, sort_keys=True)}\n", flush=True)

    total_time_start = time()

    dataset_names = GITHUB_DATASETS.keys() if "all" in args.dataset_names else args.dataset_names
    tasks = {}
    context['task_log'] = {}

    print("Planning tasks ...", flush=True)

    for dataset_name in dataset_names:
        tasks[dataset_name] = plan_tasks(dataset_name)

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
        context['task_log'][dataset_name] = {
            'query_count': query_count,
            'est_time_lo': str(est_time_lo),
            'est_time_hi': str(est_time_hi),
        }
        print(f"{dataset_name}: {query_count} queries planned; estimated time: {est_time_lo} - {est_time_hi}", flush=True)

    total_est_time_lo = timedelta(seconds=total_est_time_lo)
    total_est_time_hi = timedelta(seconds=total_est_time_hi)
    context['task_log']['_total'] = {
        'query_count': total_query_count,
        'est_time_lo': str(total_est_time_lo),
        'est_time_hi': str(total_est_time_hi),
    }
    print(f"{len(tasks)} tasks ({context['task_log']['_total']['query_count']} queries) planned; estimated total time: {context['task_log']['_total']['est_time_lo']} - {context['task_log']['_total']['est_time_hi']}\n", flush=True)

    print("Running tasks ...", flush=True)

    if args.noexec:
        print("exiting (noexec)", flush=True)
    else:
        gh = GitHub(disable_ratelimit=args.disable_ratelimit)
        for dataset_name in tasks:
            print(f"... {dataset_name} ...", flush=True)
            time_start = time()
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
            context['task_log'][dataset_name]['time'] = str(timedelta(seconds=time_end - time_start))
            print(f"... completed {dataset_name} ({context['task_log'][dataset_name]['query_count']} queries) in {context['task_log'][dataset_name]['time']} (estimated total time was {context['task_log'][dataset_name]['est_time_lo']} - {context['task_log'][dataset_name]['est_time_hi']})", flush=True)

    total_time_end = time()
    context['task_log']['_total']['time'] = str(timedelta(seconds=total_time_end - total_time_start))
    print(f"\nCompleted {context['task_log']['_total']['query_count']} queries in {context['task_log']['_total']['time']} (estimated total time was {context['task_log']['_total']['est_time_lo']} - {context['task_log']['_total']['est_time_hi']})", flush=True)

    runlog_outdir = os.path.join(
        context['outdir'],
        '_runlog',
        context['now']['year'],
        context['now']['month']
    )
    os.makedirs(runlog_outdir, exist_ok=True)
    with open(os.path.join(runlog_outdir, f"{context['now']['ds']}.json"), 'w') as f:
        f.write(json.dumps(context, indent=4, sort_keys=True))
