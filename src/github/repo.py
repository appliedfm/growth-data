from util import *
from datetime import datetime, timedelta, timezone
import dateutil
import pandas as pd
import json
import sys

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

        days_since_create_min=('days_since_create', 'min'),
        days_since_create_max=('days_since_create', 'max'),
        days_since_create_avg=('days_since_create', 'mean'),
        days_since_create_std=('days_since_create', 'std'),
        days_since_create_q10=('days_since_create', q10),
        days_since_create_q25=('days_since_create', q25),
        days_since_create_q50=('days_since_create', q50),
        days_since_create_q75=('days_since_create', q75),
        days_since_create_q90=('days_since_create', q90),

        days_since_push_min=('days_since_push', 'min'),
        days_since_push_max=('days_since_push', 'max'),
        days_since_push_avg=('days_since_push', 'mean'),
        days_since_push_std=('days_since_push', 'std'),
        days_since_push_q10=('days_since_push', q10),
        days_since_push_q25=('days_since_push', q25),
        days_since_push_q50=('days_since_push', q50),
        days_since_push_q75=('days_since_push', q75),
        days_since_push_q90=('days_since_push', q90),

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
        'days_since_create',
        'days_since_push',
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
    topics_df = pd.DataFrame(columns=('ds', 'sortby', 'pushed', 'language', 'topic'))
    counts_df = pd.DataFrame(columns=('ds', 'sortby', 'pushed', 'language', 'repo_count', 'repo_data_count'))
    for query in queries:
        status, total, repos = gh.do_search(
            search_type="repositories",
            fetch_all=args['stats'],
            q=repo_query_string(context, query),
            sortby=query['args']['sort-by'],
        )
        if 200 != status:
            context['task_log'][dataset_name]['error'] = {
                'msg': "status {status} received (expected 200)"
            }
            print(f"  ... error: {dataset_name} encountered status={status}", file=sys.stderr, flush=True)
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
            for topic in repo["topics"]:
                topics_df = topics_df.append(
                    {
                        'ds': context['now']['ds'],
                        'sortby': query['args']['sort-by'],
                        'pushed': query['args']['pushed'],
                        'language': query['args']['language'],
                        'topic': topic,
                    },
                    ignore_index=True
                )
            repos_df = repos_df.append(
                {
                    'ds': context['now']['ds'],
                    'sortby': query['args']['sort-by'],
                    'pushed': query['args']['pushed'],
                    'language': query['args']['language'],
                    'full_name': str(repo["full_name"]),
                    'owner_type': str(repo["owner"]["type"]) if repo["owner"] is not None else "",
                    'size': int(repo["size"]),
                    'days_since_create': (datetime.strptime(context['now']['ds'], '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1) - dateutil.parser.isoparse(str(repo["created_at"]))).days,
                    'days_since_push': (datetime.strptime(context['now']['ds'], '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1) - dateutil.parser.isoparse(str(repo["pushed_at"]))).days,
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
    write_df(context, task_outdir, 'repo_counts', counts_df)
    if args['stats']:
        if context['saveraw']:
            write_df(context, task_outdir, 'repos', repos_df)
        if context['saveraw']:
            write_df(context, task_outdir, 'topics', topics_df)

        # Topic stats
        grouped_topics_df = topics_df.groupby(['ds', 'language', 'topic'], as_index=False).agg(
            repos=('language', 'count'),
        ).sort_values(by=['ds', 'language', 'repos'], ascending=[True, True, True, True, False])
        write_df(context, task_outdir, 'topics', grouped_topics_df)

        # Top-line repo stats
        grouped_df = repo_stats(context, task_outdir, repos_df)
        write_df(context, task_outdir, 'repo_stats_overall', grouped_df)
        joined_df = pd.merge(repos_df, grouped_df, on=['ds', 'sortby', 'pushed', 'language'])
        COLUMNS = [
            'size',
            'days_since_create',
            'days_since_push',
            'stargazers_count',
            'forks_count',
            'open_issues_count',
            'topics_count'
        ]
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
