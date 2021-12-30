from util import *
import pandas as pd
import json
import sys

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
            context['task_log'][dataset_name]['error'] = {
                'msg': "status {status} received (expected 200)"
            }
            print(f"  ... error: {dataset_name} encountered status={status}", file=sys.stderr, flush=True)
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
    counts_df = counts_df.sort_values(by=['ds', 'created', 'user_count'], ascending=[True, True, False])
    write_df(context, task_outdir, 'user_counts', counts_df)
