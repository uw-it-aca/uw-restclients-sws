# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from uw_sws import DAO

logger = logging.getLogger(__name__)


class Worker(ABC):

    @abstractmethod
    def get_task_ids(self):
        """
        Return a list of strings
        """
        raise NotImplementedError("Subclasses must implement get_task_ids")

    @abstractmethod
    def task(self, tid):
        raise NotImplementedError("Subclasses must implement task")

    @property
    def concurrency(self):
        return DAO.get_service_setting("THREAD_POOL_SIZE", 10)

    def run_tasks(self):
        """
        Return a dictionary of task-ids to results
        """
        results = {}
        task_ids = self.get_task_ids() or []
        total_tasks = len(task_ids)
        if total_tasks == 0:
            return results

        max_workers = min(self.concurrency, total_tasks)
        batch_size = min(max_workers * 4, total_tasks)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, total_tasks, batch_size):
                chunk = task_ids[i:i + batch_size]
                futures = {
                    executor.submit(self.task, tid): tid
                    for tid in chunk
                }

                # Handle tasks in their completion order
                for future in as_completed(futures):
                    # As soon as any finishes, store its result immediately
                    tid = futures[future]
                    try:
                        results[tid] = future.result()
                    except Exception as ex:
                        logger.error(f"Task failed for {tid}: {ex}")
        # Upon block exits, Python automatically shutdown the executor
        return results


class PersonGetter(Worker):
    """
    The base-class for PWS or SWS Person object getters for a list of regids
    """

    def __init__(self, regid_set):
        self.regid_list = list(regid_set or [])

    def get_task_ids(self):
        return self.regid_list

    @abstractmethod
    def task(self, tid):
        raise NotImplementedError("Subclasses must implement task")
