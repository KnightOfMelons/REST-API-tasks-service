import unittest
from unittest.mock import patch
from main import app, db, Task


class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # SQLite для тестов также
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()  # Создаем таблицы в тестовой БД

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Удаляем все таблицы после теста

    @patch('main.send_task_to_queue')
    def test_create_task(self, mock_send_task_to_queue):
        response = self.client.post('/tasks', json={'description': 'Test task'})
        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertIn('id', data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'new')

        mock_send_task_to_queue.assert_called_once()
        mock_send_task_to_queue.assert_called_with(data['id'], 'Test task')

    def test_get_task(self):
        # Создаем задачу в БД через API
        response = self.client.post('/tasks', json={'description': 'Test task'})
        self.assertEqual(response.status_code, 201)

        task_id = response.get_json()['id']

        response = self.client.get(f'/tasks/{task_id}')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data['id'], task_id)
        self.assertEqual(data['description'], 'Test task')
        self.assertEqual(data['status'], 'new')

    def test_list_tasks_with_status_filter(self):
        task1 = Task(description='Test task 1', status='completed')
        task2 = Task(description='Test task 2', status='error')
        with self.app.app_context():
            db.session.add(task1)
            db.session.add(task2)
            db.session.commit()

        # Запрашиваем задачи с фильтром по статусу 'completed'
        response = self.client.get('/tasks?status=completed')
        self.assertEqual(response.status_code, 200)

        # Проверяем, что вернулась только одна задача со статусом 'completed'
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], 'completed')

    def test_list_tasks_without_filter(self):
        task1 = Task(description='Test task 1', status='completed')
        task2 = Task(description='Test task 2', status='error')
        with self.app.app_context():
            db.session.add(task1)
            db.session.add(task2)
            db.session.commit()

        # Запрашиваем все задачи без фильтров
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)

        # Проверяем, что вернулись обе задачи
        data = response.get_json()
        self.assertEqual(len(data), 2)


if __name__ == '__main__':
    unittest.main()
