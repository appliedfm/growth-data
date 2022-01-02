import glob
import json
import os
import pandas as pd

class Corpus:
    def __init__(self, root):
        self.root = root
        self.dfs = None

    def manifest(self, dataset='*', table='*', ext='*', year='*', month='*', day='*'):
        ret = {
            'root': self.root,
            'datasets': {}
        }
        for f in glob.iglob(f"{ret['root']}/{dataset}/{year}/{month}/{year}-{month}-{day}-{table}.{ext}"):
            rel_f = os.path.relpath(f, ret['root'])
            parts = rel_f.split(os.sep)
            dataset = parts[0]
#             year = parts[1]
#             month = parts[2]
            file = parts[3]
            ds = file[:10]
            table, ext = os.path.splitext(file[11:])
            if dataset not in ret['datasets']:
                ret['datasets'][dataset] = {
                    'tables': {}
                }
            if table not in ret['datasets'][dataset]['tables']:
                ret['datasets'][dataset]['tables'][table] = {
                    'files': []
                }
            ret['datasets'][dataset]['tables'][table]['files'].append(
                {
                    'ds': ds,
                    'type': ext[1:],
                    'path': f,
                }
            )
        return ret

    def datasets(self, dataset='*', table='*', ext='*', year='*', month='*', day='*'):
        m = self.manifest(
            dataset=dataset,
            table=table,
            ext=ext,
            year=year,
            month=month,
            day=day
        )
        return sorted(m['datasets'].keys())

    def tables(self, dataset, table='*', ext='*', year='*', month='*', day='*'):
        m = self.manifest(
            dataset=dataset,
            table=table,
            ext=ext,
            year=year,
            month=month,
            day=day
        )
        return sorted(m['datasets'][dataset]['tables'].keys())

    def table_files(self, dataset, table, ext='*', year='*', month='*', day='*'):
        m = self.manifest(
            dataset=dataset,
            table=table,
            ext=ext,
            year=year,
            month=month,
            day=day
        )
        return sorted(m['datasets'][dataset]['tables'][table]['files'], key = lambda f: (f['type'], f['ds']))

    def read_table_df(self, dataset, table):
        df = None
        for f in self.table_files(dataset, table, ext='csv'):
            f_df = pd.read_csv(f['path'])
            if df is None:
                df = f_df
            else:
                df = df.append(f_df)
        return df

    def read_dfs(self):
        if self.dfs is None:
            self.dfs = {}
            for d in self.datasets(ext='csv'):
                self.dfs[d] = {}
                for t in self.tables(d, ext='csv'):
                    print(f"reading {d}/{t} ...")
                    self.dfs[d][t] = self.read_table_df(d, t)
                print("")
        return self.dfs
