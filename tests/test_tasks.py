from unittest.mock import AsyncMock, patch

import pytest

from src.exceptions import TaskNotFoundException
from src.models.task import TaskStatus
from src.schemas.task_schema import TaskCreate
from src.services.task_service import TaskService
from src.workers.task_worker import process_task
from tests.conftest import make_task, run_async


class TestCreateTask:
    """Тест создания задачи."""

    @patch("src.services.task_service.TaskCrud")
    def test_create_returns_task_with_new_status(self, mock_crud, mock_session, mock_redis):
        task = make_task(id=1, title="Report")
        mock_crud.create_task = AsyncMock(return_value=task)

        result = run_async(TaskService.create_task(
            TaskCreate(title="Report"), mock_session, mock_redis,
        ))

        assert result.id == 1
        assert result.title == "Report"
        assert result.status == TaskStatus.new

    @patch("src.services.task_service.TaskCrud")
    def test_create_enqueues_job_to_redis(self, mock_crud, mock_session, mock_redis):
        task = make_task(id=5, title="Job")
        mock_crud.create_task = AsyncMock(return_value=task)

        run_async(TaskService.create_task(
            TaskCreate(title="Job"), mock_session, mock_redis,
        ))

        mock_redis.enqueue_job.assert_awaited_once_with("process_task", 5)

    @patch("src.services.task_service.TaskCrud")
    def test_create_calls_crud(self, mock_crud, mock_session, mock_redis):
        task = make_task(id=1, title="T")
        mock_crud.create_task = AsyncMock(return_value=task)

        run_async(TaskService.create_task(
            TaskCreate(title="T"), mock_session, mock_redis,
        ))

        mock_crud.create_task.assert_awaited_once()


class TestGetTask:
    """Тест получения одной задачи."""

    @patch("src.services.task_service.TaskCrud")
    def test_get_existing_task(self, mock_crud, mock_session):
        task = make_task(id=1, title="Found")
        mock_crud.get_task = AsyncMock(return_value=task)

        result = run_async(TaskService.get_task(1, mock_session))

        assert result.id == 1
        assert result.title == "Found"
        mock_crud.get_task.assert_awaited_once_with(1, mock_session)

    @patch("src.services.task_service.TaskCrud")
    def test_get_nonexistent_task_raises_404(self, mock_crud, mock_session):
        mock_crud.get_task = AsyncMock(return_value=None)

        with pytest.raises(TaskNotFoundException):
            run_async(TaskService.get_task(999, mock_session))


class TestFilterTasks:
    """Тест фильтрации по статусу с пагинацией."""

    @patch("src.services.task_service.TaskCrud")
    def test_filter_returns_matching_tasks(self, mock_crud, mock_session):
        tasks = [make_task(id=1, title="A"), make_task(id=2, title="B")]
        mock_crud.get_tasks = AsyncMock(return_value=tasks)
        mock_crud.count_tasks = AsyncMock(return_value=2)

        result_tasks, total = run_async(TaskService.list_tasks(
            TaskStatus.new, mock_session, offset=0, limit=10,
        ))

        assert total == 2
        assert len(result_tasks) == 2

    @patch("src.services.task_service.TaskCrud")
    def test_filter_empty_result(self, mock_crud, mock_session):
        mock_crud.get_tasks = AsyncMock(return_value=[])
        mock_crud.count_tasks = AsyncMock(return_value=0)

        result_tasks, total = run_async(TaskService.list_tasks(
            TaskStatus.done, mock_session,
        ))

        assert total == 0
        assert result_tasks == []

    @patch("src.services.task_service.TaskCrud")
    def test_pagination_params_forwarded(self, mock_crud, mock_session):
        mock_crud.get_tasks = AsyncMock(return_value=[make_task()])
        mock_crud.count_tasks = AsyncMock(return_value=10)

        run_async(TaskService.list_tasks(
            TaskStatus.new, mock_session, offset=5, limit=3,
        ))

        mock_crud.get_tasks.assert_awaited_once_with(
            mock_session, TaskStatus.new, 5, 3,
        )


class TestProcessTask:
    """Тест смены статуса воркером."""

    @patch("src.workers.task_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch("src.workers.task_worker.new_session")
    @patch("src.workers.task_worker.TaskCrud")
    def test_even_title_becomes_done(self, mock_crud, mock_new_session, mock_sleep):
        task = make_task(id=1, title="ab")
        mock_crud.get_task = AsyncMock(return_value=task)

        mock_session = AsyncMock()
        mock_new_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_new_session.return_value.__aexit__ = AsyncMock(return_value=False)

        run_async(process_task({}, 1))

        assert task.status == TaskStatus.done
        assert task.result == "success"
        assert mock_session.commit.await_count == 2

    @patch("src.workers.task_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch("src.workers.task_worker.new_session")
    @patch("src.workers.task_worker.TaskCrud")
    def test_odd_title_becomes_failed(self, mock_crud, mock_new_session, mock_sleep):
        task = make_task(id=2, title="abc")
        mock_crud.get_task = AsyncMock(return_value=task)

        mock_session = AsyncMock()
        mock_new_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_new_session.return_value.__aexit__ = AsyncMock(return_value=False)

        run_async(process_task({}, 2))

        assert task.status == TaskStatus.failed
        assert task.result == "error"

    @patch("src.workers.task_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch("src.workers.task_worker.new_session")
    @patch("src.workers.task_worker.TaskCrud")
    def test_nonexistent_task_skips(self, mock_crud, mock_new_session, mock_sleep):
        mock_crud.get_task = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_new_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_new_session.return_value.__aexit__ = AsyncMock(return_value=False)

        run_async(process_task({}, 999))

        mock_session.commit.assert_not_awaited()
