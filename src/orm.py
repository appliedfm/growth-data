from dataclasses import dataclass
from datalite import datalite
from datetime import datetime, timedelta, timezone
import git

@datalite(db_path="growth-data.db")
@dataclass
class Run:
    ds: str
    ts: str
    run_commit_hash: str
    run_mode: str
    run_status: str

    def new_run(run_mode):
        ts = datetime.now(tz=timezone.utc)
        repo = git.Repo(search_parent_directories=True)

        return Run(
            ds = str(datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")),
            ts = str(ts),
            run_commit_hash = str(repo.head.object.hexsha),
            run_mode = run_mode,
            run_status = "STARTED"
        )


@datalite(db_path="growth-data.db")
@dataclass
class Task:
    ds: str
    ts: str
    run_obj_id: int
    task_kind: str
    task_args: str
    task_tags: str
    task_status: str

    def new_task(run: Run, task_kind, task_args, task_tags):
        ts = datetime.now(tz=timezone.utc)

        return Task(
            ds = run.ds,
            ts = str(ts),
            run_obj_id = run.obj_id,
            task_kind = task_kind,
            task_args = task_args,
            task_tags = str(task_tags),
            task_status = "STARTED"
        )