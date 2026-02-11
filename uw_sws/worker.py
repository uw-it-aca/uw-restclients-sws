# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from uw_pws import PWS

logger = logging.getLogger(__name__)
MAX_POOL_SIZE = 30
UWPWS = PWS()


class Worker(ABC):

    @abstractmethod
    def get_task_ids(self):
        """
        Return an iterable of strings to process
        """
        raise NotImplementedError("Subclasses must implement get_task_ids")

    @abstractmethod
    def task(self, tid):
        """
        The function to be excuted for each regid
        """
        raise NotImplementedError("Subclasses must implement task")

    def run_tasks(self):
        """
        Scalably run concurrent tasks
        Return a dictionary of task-ids to results
        """
        results = {}
        task_ids = self.get_task_ids()
        concurrency = min(MAX_POOL_SIZE, len(task_ids))

        task_iter = iter(self.get_task_ids())
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {}
            for _ in range(concurrency):
                try:
                    tid = next(task_iter)
                except StopIteration:
                    break
                futures[executor.submit(self.task, tid)] = tid

            while futures:
                for future in as_completed(futures):
                    tid = futures.pop(future)

                    try:
                        results[tid] = future.result()
                    except Exception:
                        logger.exception(f"Task failed for {tid}")
                        results[tid] = None

                    # Submit next task
                    try:
                        ntid = next(task_iter)
                        futures[executor.submit(self.task, ntid)] = ntid
                    except StopIteration:
                        pass

                    break
        return results


class PWSPerson(Worker):
    """
    Get PWS.Person object for a list of regids
    """
    def __init__(self, regid_set):
        self.regid_set = regid_set

    def get_task_ids(self):
        return list(self.regid_set)

    def task(self, tid):
        return UWPWS.get_person_by_regid(tid)
