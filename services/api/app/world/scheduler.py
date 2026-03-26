from app.world.clock import WorldClock
from app.world.events import RuntimeTask


class WorldScheduler:
    def __init__(self) -> None:
        self._tasks: dict[str, RuntimeTask] = {}

    def schedule(self, task: RuntimeTask) -> None:
        self._tasks[task.id] = task

    def pop_due_tasks(self, *, clock: WorldClock) -> list[RuntimeTask]:
        now = clock.snapshot().now
        due_ids = [
            task_id
            for task_id, task in self._tasks.items()
            if task.run_at <= now
        ]
        due_tasks = [self._tasks.pop(task_id) for task_id in due_ids]
        return sorted(due_tasks, key=lambda task: (task.run_at, task.priority))

    def snapshot(self) -> list[RuntimeTask]:
        return sorted(self._tasks.values(), key=lambda task: (task.run_at, task.priority))

    def replace(self, tasks: list[RuntimeTask]) -> None:
        self._tasks = {task.id: task for task in tasks}
