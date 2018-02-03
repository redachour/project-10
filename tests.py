import datetime
import json
import unittest
from base64 import b64encode

from playhouse.test_utils import test_database
from peewee import *

import app
from models import Todo, User

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, Todo], safe=True)

headers = {'Authorization': 'Basic ' +
           b64encode(b"username:password").decode("ascii")}


class ModelsTestCase(unittest.TestCase):
    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            user = User.create_user('username', 'password')
            self.assertEqual(User.select().count(), 1)
            self.assertEqual(user.username, 'username')
            self.assertNotEqual(user.password, 'password')
            with self.assertRaises(Exception):
                User.create_user('username', 'password')

    def test_todo(self):
        with test_database(TEST_DB, (Todo,)):
            todo = Todo.create(name='sport')
            self.assertEqual(Todo.select().count(), 1)
            self.assertEqual(Todo.select().get().created_at,
                             datetime.date.today())
            self.assertEqual(todo.name, 'sport')


class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def test_todolist_get(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name='sport')
            response = self.app.get('/api/v1/todos')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"sport", response.data)

            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(len(data), 1)
            for item in data:
                self.assertIn('id', item)
                self.assertIn('name', item)

    def test_todolist_post(self):
        response = self.app.post('/api/v1/todos', data={'name': 'sport'})
        self.assertEqual(response.status_code, 401)

        with test_database(TEST_DB, (User, Todo)):
            User.create_user('username', 'password')
            response = self.app.post('/api/v1/todos', headers=headers,
                                     data={'name': 'sport'})
            self.assertEqual(response.status_code, 201)

            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['id'], 1)
            self.assertEqual(data['name'], 'sport')

    def test_todo_put(self):
        with test_database(TEST_DB, (User, Todo)):
            Todo.create(name='sport')
            User.create_user('username', 'password')
            response = self.app.put('/api/v1/todos/1', data={'name': 'word'})
            self.assertEqual(response.status_code, 200)

            response = self.app.put('/api/v1/todos/1', headers=headers,
                                    data={'name': 'work'})
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['id'], 1)
            self.assertEqual(data['name'], 'work')

    def test_todo_delete(self):
        with test_database(TEST_DB, (User, Todo)):
            Todo.create(name='sport')
            User.create_user('username', 'password')
            response = self.app.delete('/api/v1/todos/1')
            self.assertEqual(response.status_code, 401)

            response = self.app.delete('/api/v1/todos/1', headers=headers)
            self.assertEqual(response.status_code, 204)
            self.assertEqual(Todo.select().count(), 0)


if __name__ == '__main__':
    unittest.main()
