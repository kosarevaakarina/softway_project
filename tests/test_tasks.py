import pytest

from src.application.task_service import TaskService
from src.domain.entities import TaskStatus
from src.domain.exceptions import TaskNotFoundError
from tests.conftest import make_task, run_async


class TestCreateTask:

    def test_create_returns_task(self, mock_repo, mock_queue):
        task = make_task(id=1, title="Report")
        mock_repo.create.return_value = task
        service = TaskService(repo=mock_repo, queue=mock_queue)

        result = run_async(service.create_task("Report"))

        assert result.id == 1
        assert result.title == "Report"
        assert result.status == TaskStatus.new

    def test_create_enqueues_job(self, mock_repo, mock_queue):
        task = make_task(id=5, title="Job")
        mock_repo.create.return_value = task
        service = TaskService(repo=mock_repo, queue=mock_queue)

        run_async(service.create_task("Job"))

        mock_queue.enqueue.assert_awaited_once_with(5)

    def test_create_calls_repo(self, mock_repo, mock_queue):
        task = make_task(id=1, title="T")
        mock_repo.create.return_value = task
        service = TaskService(repo=mock_repo, queue=mock_queue)

        run_async(service.create_task("T"))

        mock_repo.create.assert_awaited_once_with("T")


class TestGetTask:

    def test_get_existing_task(self, mock_repo, mock_queue):
        task = make_task(id=1, title="Found")
        mock_repo.get_by_id.return_value = task
        service = TaskService(repo=mock_repo, queue=mock_queue)

        result = run_async(service.get_task(1))

        assert result.id == 1
        assert result.title == "Found"

    def test_get_nonexistent_raises(self, mock_repo, mock_queue):
        mock_repo.get_by_id.return_value = None
        service = TaskService(repo=mock_repo, queue=mock_queue)

        with pytest.raises(TaskNotFoundError):
            run_async(service.get_task(999))


class TestListTasks:

    def test_list_returns_tasks(self, mock_repo, mock_queue):
        tasks = [make_task(id=1, title="A"), make_task(id=2, title="B")]
        mock_repo.list_by_status.return_value = tasks
        mock_repo.count_by_status.return_value = 2
        service = TaskService(repo=mock_repo, queue=mock_queue)

        tasks_result, total = run_async(service.list_tasks(TaskStatus.new, offset=0, limit=10))

        assert total == 2
        assert len(tasks_result) == 2

    def test_list_empty(self, mock_repo, mock_queue):
        mock_repo.list_by_status.return_value = []
        mock_repo.count_by_status.return_value = 0
        service = TaskService(repo=mock_repo, queue=mock_queue)

        tasks_result, total = run_async(service.list_tasks(TaskStatus.done))

        assert total == 0
        assert tasks_result == []

    def test_pagination_forwarded(self, mock_repo, mock_queue):
        mock_repo.list_by_status.return_value = [make_task()]
        mock_repo.count_by_status.return_value = 10
        service = TaskService(repo=mock_repo, queue=mock_queue)

        run_async(service.list_tasks(TaskStatus.new, offset=5, limit=3))

        mock_repo.list_by_status.assert_awaited_once_with(TaskStatus.new, 5, 3)


class TestProcessTask:

    def test_even_title_done(self, mock_repo, mock_queue):
        task = make_task(id=1, title="ab")
        mock_repo.get_by_id_for_update.return_value = task
        service = TaskService(repo=mock_repo, queue=mock_queue)

        run_async(service.process_task(1))

        assert task.status == TaskStatus.done
        assert task.result == "success"
        assert mock_repo.save.await_count == 2

    def test_odd_title_failed(self, mock_repo, mock_queue):
        task = make_task(id=2, title="abc")
        mock_repo.get_by_id_for_update.return_value = task
        service = TaskService(repo=mock_repo, queue=mock_queue)

        run_async(service.process_task(2))

        assert task.status == TaskStatus.failed
        assert task.result == "error"

    def test_not_found_skips(self, mock_repo, mock_queue):
        mock_repo.get_by_id_for_update.return_value = None
        service = TaskService(repo=mock_repo, queue=mock_queue)

        run_async(service.process_task(999))

        mock_repo.save.assert_not_awaited()

    def test_non_new_status_skips(self, mock_repo, mock_queue):
        task = make_task(id=1, title="ab", status=TaskStatus.processing)
        mock_repo.get_by_id_for_update.return_value = task
        service = TaskService(repo=mock_repo, queue=mock_queue)

        run_async(service.process_task(1))

        mock_repo.save.assert_not_awaited()
