import time
import pytest
from kernel.scheduler import KernelScheduler

def test_scheduler_jobs():
    scheduler = KernelScheduler()
    called_count = 0

    def job_func():
        nonlocal called_count
        called_count += 1

    scheduler.add_interval_job("test_job", 0.05, job_func)
    assert len(scheduler._jobs) == 1
    assert scheduler._jobs[0]["name"] == "test_job"

    scheduler.start()
    time.sleep(0.15)
    scheduler.stop()

    assert called_count > 0
