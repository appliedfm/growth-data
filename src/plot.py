from corpus import Corpus
import argparse
import pandas as pd
import plotly.express as px
import os

class Plot:
    def __init__(self, outdir, corpus):
        self.outdir = outdir
        self.corpus = corpus

    def export(self, dataset, table, fname, fig):
        tablepath = os.path.join(
            self.outdir,
            dataset,
            table,
            )
        os.makedirs(tablepath, exist_ok=True)
        outpath = os.path.join(tablepath, f"{fname}.html")
        fig.write_html(
            outpath,
            include_plotlyjs='cdn',
            full_html=False,
        )

    def write_index(self):
        datasets = sorted([f for f in os.listdir(self.outdir) if 'index.html' not in f])
        datasets_f = open(os.path.join(self.outdir, 'index.html'), 'w')
        datasets_f.write(f"<ul>\n")
        for dataset in datasets:
            datasets_f.write(f"<li><a href='{dataset}/index.html'>{dataset}</a></li>\n")

            tables = sorted([f for f in os.listdir(os.path.join(self.outdir, dataset)) if 'index.html' not in f])
            tables_f = open(os.path.join(self.outdir, dataset, 'index.html'), 'w')
            tables_f.write(f"<ul>\n")
            for table in tables:
                tables_f.write(f"<li><a href='{table}/index.html'>{table}</a></li>\n")

                plots = sorted([f for f in os.listdir(os.path.join(self.outdir, dataset, table)) if 'index.html' not in f])
                plots_f = open(os.path.join(self.outdir, dataset, table, 'index.html'), 'w')
                plots_f.write(f"<ul>\n")
                for plot in plots:
                    plots_f.write(f"<li><a href='{plot}'>{os.path.splitext(plot)[0]}</a></li>\n")
                plots_f.write(f"</ul>\n")
                plots_f.close()
            tables_f.write(f"</ul>\n")
            tables_f.close()
        datasets_f.write(f"</ul>\n")
        datasets_f.close()

    def plot_counts(self, dataset, table, metric, facet, logscale=False, export=False):
        df = self.corpus.read_dfs()[dataset][table]

        title = f"{metric}"
        if logscale:
            title = title + " (log scale)"

        fig = px.line(
            df,
            x='ds',
            y=[metric],
            log_y=logscale,
            facet_col=facet,
            height=550,
            color='language',
            symbol='language',
            markers=True,
            labels={
                'ds': '',
                'value': '',
            },
            title = title,
        )
        if export:
            self.export(dataset, table, f"{metric}{'-logscale' if logscale else ''}", fig)
        return fig

    def repo_stats_license_metric_latest(self, dataset, table, path, metric, pushed, export=False):
        df = self.corpus.read_dfs()[dataset][table]
        df = df[df['sortby'] == 'stars']
        df = df[df['pushed'] == pushed]
        df = df.drop(['sortby'], axis=1)
        latest_ds = df['ds'].max()
        df = df[df['ds'] == latest_ds]

        df['license_key'] = df['license_key'].fillna("(Unknown)")

        title = f"{metric} by {', '.join(path)}"
        title = title + " ("
        title = title + f"ds={latest_ds}"
        title = title + f", pushed={pushed}"
        title = title + ")"

        fig = px.sunburst(
            df,
            path=path,
            values=metric,
            height=550,
            title = title,
        )
        if export:
            self.export(dataset, table, f"latest--{metric}--{'-'.join(path)}", fig)
        return fig

    def repo_stats_license_metric(self, dataset, table, metric, pushed, logscale=False, export=False):
        df = self.corpus.read_dfs()[dataset][table]
        df = df[df['sortby'] == 'stars']
        df = df[df['pushed'] == pushed]
        df = df.drop(['sortby'], axis=1)

        df['license_key'] = df['license_key'].fillna("(Unknown)")

        title = metric
        title = title + " ("
        title = title + f"pushed={pushed}"
        if logscale:
            title = title + ", log scale"
        title = title + ")"

        fig = px.area(
            df,
            x='ds',
            y=metric,
            log_y=logscale,
            facet_col='license_key',
            facet_col_wrap=6,
            height=550,
            color='language',
            line_group='language',
            labels={
                'ds': '',
                'value': '',
            },
            title = title,
        )
        if export:
            self.export(dataset, table, f"{metric}{'-logscale' if logscale else ''}", fig)
        return fig

    def repo_stats_metric_latest(self, dataset, table, metric, logscale=False, export=False):
        df = self.corpus.read_dfs()[dataset][table]
        df = df[df['sortby'] == 'stars']
        df = df.drop(['sortby'], axis=1)
        latest_ds = df['ds'].max()
        df = df[df['ds'] == latest_ds]

        title = metric
        title = title + " ("
        title = title + f"ds={latest_ds}"
        if logscale:
            title = title + ", log scale"
        title = title + ")"

        fig = px.bar(
            df,
            x='language',
            y=metric,
            log_y=logscale,
            facet_col='pushed',
            height=550,
            color='language',
            labels={
                'language': '',
                'value': '',
            },
            title = title,
        )
        if export:
            self.export(dataset, table, f"latest--{metric}{'-logscale' if logscale else ''}", fig)
        return fig

    def repo_stats_metric_area(self, dataset, table, metric, logscale=False, export=False):
        df = self.corpus.read_dfs()[dataset][table]
        df = df[df['sortby'] == 'stars']
        df = df.drop(['sortby'], axis=1)

        title = metric
        if logscale:
            title = title + " (log scale)"

        fig = px.area(
            df,
            x='ds',
            y=metric,
            log_y=logscale,
            facet_col='pushed',
            height=550,
            color='language',
            line_group='language',
            labels={
                'ds': '',
                'value': '',
            },
            title = title,
        )
        if export:
            self.export(dataset, table, f"{metric}-{'-logscale' if logscale else ''}", fig)
        return fig

    def repo_stats_metric(self, dataset, table, metric, aggs, logscale=False, export=False):
        df = self.corpus.read_dfs()[dataset][table]
        df = df[df['sortby'] == 'stars']
        df = df.drop(['sortby'], axis=1)

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
            height=550,
            color='language',
            symbol='language',
            markers=True,
            labels={
                'ds': '',
                'value': '',
            },
            title = title,
        )
        if export:
            self.export(dataset, table, f"{metric}-{'_'.join(aggs)}{'-logscale' if logscale else ''}", fig)
        return fig


def render_plots(M, P):
    COUNTS = [
        (
            'repo-alltime-counts',
            'pushed',
            [
                ('repo_counts', 'repo_count')
            ]
        ),
        (
            'repo-alltime-stats',
            'pushed',
            [
                ('repo_counts', 'repo_count')
            ]
        ),
        (
            'repo-weekly-stats',
            'pushed',
            [
                ('repo_counts', 'repo_count')
            ]
        ),
        (
            'user-alltime-counts',
            'created',
            [
                ('user_counts', 'user_count')
            ]
        ),
    ]

    for dataset, facet, metrics in COUNTS:
        for table, metric in metrics:
            for logscale in [True, False]:
                print(f"rendering {dataset} {table} {metric} (logscale={logscale})")
                P.plot_counts(
                    dataset,
                    table,
                    metric,
                    facet,
                    logscale=logscale,
                    export=True
                )
        print("")

    LICENSE_METRICS = [
        'repo_count',
        'stargazers_count_sum',
        'forks_count_sum',
        'size_sum',
        'open_issues_count_sum',
    ]

    for dataset in ['repo-alltime-stats']:
        for table in ['repo_stats_license']:
            for metric in LICENSE_METRICS:
                for logscale in [False, True]:
                    print(f"rendering {dataset} {table} {metric} (logscale={logscale})")
                    fig = P.repo_stats_license_metric(
                        dataset,
                        table,
                        metric,
                        pushed='156_3year',
                        logscale=logscale,
                        export=True
                    )
                    for path in [['language', 'license_key'], ['license_key', 'language']]:
                        fig = P.repo_stats_license_metric_latest(
                            dataset,
                            table,
                            path,
                            metric,
                            pushed='156_3year',
                            export=True
                        )
        print("")

        for table in ['repo_stats_overall']:
            for metric in ['repo_count', 'stargazers_count_sum', 'forks_count_sum', 'size_sum', 'open_issues_count_sum']:
                for logscale in [False, True]:
                    print(f"rendering latest {dataset} {table} {metric} (logscale={logscale})")
                    fig = P.repo_stats_metric_latest(
                        dataset,
                        table,
                        metric,
                        logscale=logscale,
                        export=True
                    )
            print("")

            for metric in ['repo_count', 'repos_with_license', 'repos_with_issues', 'repos_with_downloads', 'repos_with_wiki', 'repos_with_projects', 'repos_with_pages']:
                for logscale in [False, True]:
                    print(f"rendering {dataset} {table} {metric} (logscale={logscale})")
                    fig = P.repo_stats_metric_area(
                        dataset,
                        table,
                        metric,
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
            for metric in ['stargazers_count_sum', 'forks_count_sum', 'size_sum', 'open_issues_count_sum']:
                for logscale in [False, True]:
                    print(f"rendering {dataset} {table} {metric} (logscale={logscale})")
                    fig = P.repo_stats_metric_area(
                        dataset,
                        table,
                        metric,
                        logscale=logscale,
                        export=True
                    )
            for metric in ['stargazers_count', 'forks_count', 'size', 'open_issues_count']:
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
        print("")


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to corpus")
    parser.add_argument("-o", "--outdir", help="Output directory")
    parser.add_argument("--index_only", help="Generate indexes but don't generate any plots", action='store_true')
    parser.set_defaults(input='data')
    parser.set_defaults(output='docs/source/_static/plots')
    parser.set_defaults(index_only=False)
    args = parser.parse_args()

    M = Corpus(args.input)
    P = Plot(args.output, M)

    if not args.index_only:
        render_plots(M, P)

    P.write_index()
