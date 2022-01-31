"""Pipeline orchestrator with dependency management and scheduling."""
import time, logging, threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import heapq

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

@dataclass
class PipelineTask:
    """A single task in the pipeline."""
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    max_retries: int = 3
    timeout: int = 3600
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0

    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __lt__(self, other):
        return self.priority < other.priority


class PipelineOrchestrator:
    """Orchestrates pipeline execution with dependency resolution."""

    def __init__(self, max_workers: int = 4):
        self.tasks: Dict[str, PipelineTask] = {}
        self.max_workers = max_workers
        self._running = False
        self._completed_order: List[str] = []
        self._lock = threading.Lock()

    def add_task(self, name: str, func: Callable, dependencies: List[str] = None,
                 priority: int = 0, max_retries: int = 3, timeout: int = 3600,
                 args: tuple = (), kwargs: dict = None):
        """Add a task to the pipeline."""
        task = PipelineTask(
            name=name, func=func, dependencies=dependencies or [],
            priority=priority, max_retries=max_retries, timeout=timeout,
            args=args, kwargs=kwargs or {},
        )
        self.tasks[name] = task
        logger.debug("Added task: %s (deps=%s)", name, dependencies)
        return self

    def _resolve_dependencies(self) -> List[str]:
        """Topological sort of tasks based on dependencies."""
        in_degree = {name: 0 for name in self.tasks}
        graph = {name: [] for name in self.tasks}
        for name, task in self.tasks.items():
            for dep in task.dependencies:
                if dep in graph:
                    graph[dep].append(name)
                    in_degree[name] += 1
        queue = [name for name, deg in in_degree.items() if deg == 0]
        order = []
        while queue:
            queue.sort(key=lambda n: self.tasks[n].priority)
            node = queue.pop(0)
            order.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if len(order) != len(self.tasks):
            raise ValueError("Circular dependency detected in pipeline")
        return order

    def _run_task(self, task: PipelineTask) -> bool:
        """Execute a single task with retry logic."""
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        logger.info("Running task: %s", task.name)
        for attempt in range(task.max_retries):
            try:
                result = task.func(*task.args, **task.kwargs)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.end_time = datetime.now()
                with self._lock:
                    self._completed_order.append(task.name)
                logger.info("Task completed: %s (%.2fs)", task.name, task.duration)
                return True
            except Exception as e:
                task.retry_count += 1
                task.error = str(e)
                if attempt < task.max_retries - 1:
                    task.status = TaskStatus.RETRYING
                    wait = 2 ** attempt
                    logger.warning("Task %s failed (attempt %d/%d), retrying in %ds: %s",
                                   task.name, attempt + 1, task.max_retries, wait, e)
                    time.sleep(wait)
                else:
                    task.status = TaskStatus.FAILED
                    task.end_time = datetime.now()
                    logger.error("Task failed: %s after %d attempts: %s",
                                 task.name, task.max_retries, e)
        return False

    def run(self) -> Dict[str, Any]:
        """Execute the full pipeline."""
        order = self._resolve_dependencies()
        logger.info("Pipeline execution order: %s", order)
        self._running = True
        results = {}
        for name in order:
            task = self.tasks[name]
            deps_ok = all(
                self.tasks[d].status == TaskStatus.COMPLETED
                for d in task.dependencies if d in self.tasks
            )
            if not deps_ok:
                task.status = TaskStatus.SKIPPED
                logger.warning("Skipping task %s due to failed dependencies", name)
                continue
            success = self._run_task(task)
            results[name] = {
                "status": task.status.value,
                "duration": task.duration,
                "result": task.result,
            }
        self._running = False
        summary = {
            "total": len(self.tasks),
            "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            "skipped": sum(1 for t in self.tasks.values() if t.status == TaskStatus.SKIPPED),
            "execution_order": self._completed_order,
            "results": results,
        }
        logger.info("Pipeline complete: %s", summary)
        return summary

    def get_task_status(self) -> Dict[str, Dict]:
        """Get status of all tasks."""
        return {
            name: {
                "status": task.status.value,
                "retries": task.retry_count,
                "duration": task.duration,
                "error": task.error,
            }
            for name, task in self.tasks.items()
        }
