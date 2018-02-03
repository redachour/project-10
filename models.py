import datetime

from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *


DATABASE = SqliteDatabase('todos.sqlite')
HASHER = PasswordHasher()
SECRET_KEY = 'GWK~M$F2"|[|i|,KEJWxvA5~JQN!}fUz>|&h`>g.K2/p)%t3%4P:tuR6G6A'


class User(Model):
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, password):
        try:
            cls.select().where(cls.username ** username).get()
        except cls.DoesNotExist:
            user = cls(username=username)
            user.password = user.hash_password(password)
            user.save()
            return user
        else:
            raise Exception('User with that username already exists')

    @staticmethod
    def hash_password(password):
        return HASHER.hash(password)

    def verify_password(self, password):
        return HASHER.verify(self.password, password)

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(SECRET_KEY)
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            user = User.get(User.id == data['id'])
            return user

    def generate_auth_token(self, expires=3600):
        serializer = Serializer(SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id': self.id})


class Todo(Model):
    name = CharField()
    created_at = DateField(default=datetime.date.today)

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Todo], safe=True)
    DATABASE.close()
