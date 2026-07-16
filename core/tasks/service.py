import time
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class Task(BaseModel):
    task_id: str
    description: str
    status: str = "pending"
    priority: int = 1
    progress: int = 0
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    assigned_agent: Optional[str] = None
    results: Optional[Any] = None

class TaskManager:
    def __init__(self):
        self._tasks = {}

    def create_task(self, task_id, description, priority=1) -> Task:
        task = Task(task_id=task_id, description=description, priority=priority)
        self._tasks[task_id] = task
        return task

    def update_task_status(self, task_id, status, progress=None, results=None):
        if task_id in self._tasks:
            t = self._tasks[task_id]
            t.status = status
            if progress is not None: t.progress = progress
            if results is not None: t.results = results
            t.updated_at = time.time()
            return t
        return None

    def list_tasks(self) -> List[Task]:
        return sorted(list(self._tasks.values()), key=lambda x: x.priority, reverse=True)

global_task_manager = TaskManager()
