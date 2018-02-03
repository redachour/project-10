from flask import Blueprint, url_for
from flask_restful import (Resource, reqparse, Api, fields, marshal,
                           marshal_with)

import models
from auth import auth

todo_fields = {
    'id': fields.Integer,
    'name': fields.String}


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            location=['form', 'json'],
            help='No name provided'
        )

    def get(self):
        return [marshal(todo, todo_fields) for todo in models.Todo.select()]

    @auth.login_required
    @marshal_with(todo_fields)
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
        return todo, 201, {'Location': url_for('resources.todos.todo',
                                               id=todo.id)}


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            location=['form', 'json'],
            help='No name provided'
        )

    @marshal_with(todo_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Todo.update(**args).where(models.Todo.id == id)
        query.execute()
        return models.Todo.get(models.Todo.id == id), 200

    @auth.login_required
    def delete(self, id):
        query = models.Todo.delete().where(models.Todo.id == id)
        query.execute()
        return '', 204, {'Location': url_for('resources.todos.todos')}


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/todos/<int:id>',
    endpoint='todo'
)
