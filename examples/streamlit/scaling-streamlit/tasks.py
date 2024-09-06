import time
from enum import Enum


from redis import Redis
from rq import Queue

from db import TaskResultManager


redis_conn = Redis(host="localhost", port=6379)
q = Queue(connection=redis_conn)

manager = TaskResultManager("task_results.db")


class JobStatus(Enum):
    PENDING = "pending"
    FINISHED = "finished"
    FAILED = "failed"
    INVALID = "invalid"


def _on_success(job, connection, result, *args, **kwargs):
    TaskResultManager("task_results.db").store_result(
        job.id, result, JobStatus.FINISHED
    )


def _on_failure(job, connection, result, *args, **kwargs):
    TaskResultManager("task_results.db").store_result(job.id, None, JobStatus.FAILED)


def enqueue_task(fn, fn_kwargs=None, user_id=None):

    if user_id:
        enqueue_kwargs = {"on_success": _on_success, "on_failure": _on_failure}
    else:
        enqueue_kwargs = {}

    job = q.enqueue(fn, kwargs=fn_kwargs, **enqueue_kwargs)
    id_ = job.id

    if user_id:
        manager.store_pending_task(id_, user_id)

    return id_


def run_until_complete(fn, fn_kwargs=None, user_id=None):
    job_id = enqueue_task(fn, fn_kwargs, user_id)
    status, result = check_job_status(job_id)

    if status == JobStatus.INVALID:
        raise ValueError("Invalid job ID")

    while status != JobStatus.FINISHED:
        if status == JobStatus.FAILED:
            raise ValueError("Job failed")

        time.sleep(1)
        status, result = check_job_status(job_id)

    return result


def check_job_status(job_id):
    job = q.fetch_job(job_id)

    if job is None:
        return JobStatus.INVALID, None
    if job.is_finished:
        return JobStatus.FINISHED, job.result
    elif job.is_failed:
        return JobStatus.FAILED, None
    else:
        return JobStatus.PENDING, None
