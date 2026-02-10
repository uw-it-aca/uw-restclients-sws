

from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Iterable
from uw_pws import PWS

MAX_WORKERS = 50
logger = logging.getLogger(__name__)
UWPWS = PWS()

class Worker(ABC):

    @abstractmethod
    def get_task_ids(self) -> Iterable[str]:
        """
        Return an iterable of strings to process
        """
        raise NotImplementedError("Subclasses must implement get_task_ids")

    @abstractmethod
    def task(self, tid: str):
        """
        The function to be excuted for each regid
        """
        raise NotImplementedError("Subclasses must implement task")

    def run_tasks(self, concurrency=MAX_WORKERS):
        """
        Run tasks concurrently and return a dictionary of results
        """
        results: Dict[str, Any] = {}

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            # Map futures to task_identifiers
            futures = {
                executor.submit(self.task, tid): tid 
                for tid in self.get_task_ids()}

            for future in as_completed(futures):
                tid = futures[future]
                try:
                    results[tid] = future.result()
                except Exception as exc:
                    logger.error(f"Task for {tid} failed: {exc}")

        return results


class PWSPerson(Worker):
    """
    Get PWS.Person object for a list of regids
    """
    def __init__(self, regid_set: Iterable[str]):
        self.regid_set = regid_set

    def get_task_ids(self) -> Iterable[str]:
        return self.regid_set

    def task(self, tid: str):
        return UWPWS.get_person_by_regid(tid)
