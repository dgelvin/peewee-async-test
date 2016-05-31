from asynctest import TestCase

from peewee import Model, Proxy, CharField
from peewee_async import Manager, PostgresqlDatabase

PG_USER_ENV_VAR = 'PG_USER'
PG_HOST_ENV_VAR = 'PG_HOST'
PG_PASSWORD_ENV_VAR = 'PG_PASSWORD'
PG_DATABASE_ENV_VAR = 'PG_DATABASE'


class Database:
    aio_manager = None
    database = Proxy()

    @classmethod
    def init_db(cls, database_name, **kwargs):
        database = PostgresqlDatabase(database_name, **kwargs)
        cls.database.initialize(database)
        User.create_table(fail_silently=True)
        cls.aio_manager = Manager(cls.database)
        database.allow_sync = False

    @classmethod
    def close_db(cls):
        cls.database.close()

    @classmethod
    def drop_tables(cls):
        with cls.aio_manager.allow_sync():
            User.drop_table(fail_silently=True)


class BaseModel(Model):
    class Meta:
        database = Database.database

    @classmethod
    async def get(cls, **kwargs):
        return await Database.aio_manager.get(cls, **kwargs)

    @classmethod
    async def create(cls, **kwargs):
        return await Database.aio_manager.create(cls, **kwargs)


class User(BaseModel):
    name = CharField()


class UnitTests(TestCase):
    def setUp(self):
        Database.init_db(database_name='pwt', host='172.17.0.2', user='postgres', password='abc123')

    def tearDown(self):
        Database.drop_tables()
        Database.database.close()

    async def test_one(self):
        user = User.create(username='bob')

