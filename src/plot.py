from corpus import Corpus
import argparse
import pandas as pd
import plotly.express as px
import os

class Plot:
    def __init__(self, outdir, corpus):
        self.outdir = outdir
        self.corpus = corpus

    def repo_stats_metric(self, dataset, table, metric, aggs, logscale=False, export=False):
        dfs = self.corpus.read_dfs()
        df = dfs[dataset][table].drop(['sortby'], axis=1)
        title = f"{', '.join(aggs)} of {metric}" if len(aggs) > 0 else metric
        if logscale:
            title = title + " (log scale)"
        fig = px.line(
            df,
            x='ds',
            y=[
                f"{metric}_{agg}"
                for agg in aggs
            ] if len(aggs) > 0 else [metric],
            log_y=logscale,
            facet_col='pushed',
            color='language',
            symbol='language',
            markers=True,
            labels={
                'ds': 'Date',
                'value': metric,
            },
            title = title,
        )
        if export:
            tablepath = os.path.join(
                self.outdir,
                dataset,
                table,
                )
            os.makedirs(tablepath, exist_ok=True)
            outpath = os.path.join(tablepath, f"{metric}-{'_'.join(aggs)}{'-logscale' if logscale else ''}.html")
            fig.write_html(outpath)
        return fig


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to corpus")
    parser.add_argument("-o", "--outdir", help="Output directory")
    parser.set_defaults(input='data')
    parser.set_defaults(output='docs/source/plots')
    args = parser.parse_args()

    M = Corpus(args.input)
    P = Plot(args.output, M)

    dataset='repo-alltime-stats'
    table='repo_stats_overall'
    for metric in ['repo_count', 'repos_with_license', 'repos_with_issues', 'repos_with_downloads', 'repos_with_wiki', 'repos_with_projects', 'repos_with_pages']:
        for logscale in [False, True]:
            print(f"rendering {dataset} {table} {metric} (logscale={logscale})")
            fig = P.repo_stats_metric(
                dataset,
                table,
                metric,
                [],
                logscale=logscale,
                export=True
            )

    for metric in ['days_since_create']:
        for logscale in [False, True]:
            for aggs in [['avg'], ['q10', 'q90'], ['q25', 'q75'], ['q50'], ['max']]:
                print(f"rendering {dataset} {table} {metric} {aggs} (logscale={logscale})")
                fig = P.repo_stats_metric(
                    dataset,
                    table,
                    metric,
                    aggs,
                    logscale=logscale,
                    export=True
                )

    for metric in ['stargazers_count', 'forks_count', 'size', 'open_issues_count']:
        for logscale in [False, True]:
            for aggs in [['sum'], ['avg'], ['q10', 'q90'], ['q25', 'q75'], ['q50'], ['max']]:
                print(f"rendering {dataset} {table} {metric} {aggs} (logscale={logscale})")
                fig = P.repo_stats_metric(
                    dataset,
                    table,
                    metric,
                    aggs,
                    logscale=logscale,
                    export=True
                )
