import redis
from enum import IntEnum
from decouple import config
from datetime import timedelta

EXPIRATION = config("MINUTES", cast=int) * 2


class RedisCache:
    class Database(IntEnum):
        OPENING = 0
        CLOSING = 1

    @classmethod
    def get_client(cls, database: Database):
        client = redis.Redis(
            host=config("REDIS_HOST"),
            port=config("REDIS_PORT"),
            db=int(database),
            charset="utf-8",
            decode_responses=True,
        )

        assert client.ping()
        return client

    @classmethod
    def add_opening(cls, exchange_name):
        db = cls.Database.OPENING
        client = cls.get_client(db)
        expiration = timedelta(minutes=EXPIRATION)
        client.setex(exchange_name, expiration, "sent")

    @classmethod
    def check_opening_message_sent(cls, exchange_name):
        db = cls.Database.OPENING
        client = cls.get_client(db)
        return True if client.get(exchange_name) is not None else False

    @classmethod
    def add_closing(cls, exchange_name):
        db = cls.Database.CLOSING
        client = cls.get_client(db)
        expiration = timedelta(minutes=EXPIRATION)
        client.setex(exchange_name, expiration, "sent")

    @classmethod
    def check_closing_message_sent(cls, exchange_name):
        db = cls.Database.CLOSING
        client = cls.get_client(db)
        return True if client.get(exchange_name) is not None else False
