# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.worker import Worker


class TestWorker(Worker):

    def __init__(self, task_ids):
        self._task_ids = task_ids

    def get_task_ids(self):
        return self._task_ids

    def task(self, tid):
        return tid.replace("regid", "person")


class WorkerTest(TestCase):
    def test_run_tasks(self):
        task_ids = []
        for i in range(0, 2000):
            task_ids.append(f"regid-{i}")

        results = TestWorker(task_ids).run_tasks()
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 2000)
        for i in range(0, 2000):
            id = f"regid-{i}"
            self.assertIsNotNone(results[id])
            self.assertEqual(results[id], f"person-{i}")

        results = TestWorker().run_tasks()
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 0)

        results = TestWorker([]).run_tasks()
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 0)
