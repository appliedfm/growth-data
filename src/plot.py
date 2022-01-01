from corpus import Corpus
import pandas as pd
import plotly.express as px
import os

class Plot:
    def __init__(self, outdir, corpus):
        self.outdir = outdir
        self.corpus = corpus

    def repo_stats_metric(self, dataset, table, metric, agg, logscale=False, export=False):
        dfs = self.corpus.read_dfs()
        df = dfs[dataset][table].drop(['sortby'], axis=1)
        title = f"{agg} of {metric}"
        if logscale:
            title = title + " (log scale)"
        fig = px.line(
            df,
            x='ds',
            y=[
                f"{metric}_{agg}",
            ],
            log_y=logscale,
            facet_col='pushed',
            color='language',
            symbol='language',
            markers=True,
            labels={
                'ds': 'Date',
                'value': metric,
                f"{metric}_{agg}": agg,
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
            outpath = os.path.join(tablepath, f"{metric}-{agg}{'-logscale' if logscale else ''}.html")
            fig.write_html(outpath)
        return fig
