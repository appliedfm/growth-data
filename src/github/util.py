from tabulate import tabulate
import os

def write_df(context, task_outdir, name, df):
    df.to_csv(os.path.join(task_outdir, f"{context['now']['ds']}-{name}.csv"), index=False)
    with open(os.path.join(task_outdir, f"{context['now']['ds']}-{name}.md"), 'w') as f:
        f.write(tabulate(df, headers='keys', showindex=False, tablefmt='github'))
        f.write("\n")
