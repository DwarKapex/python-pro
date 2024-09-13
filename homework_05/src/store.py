from dataclasses import dataclass

import redis  # type: ignore[import-untyped]


@dataclass
class RedisConfig:
    ADDRESS = "127.0.0.1"
    REDIS_PORT = 6379
    TIMEOUT = 20
    RETRY_COUNT = 4


class RedisClient:
    def __init__(self, ip_address, port, timeout):
        self.port = port or RedisConfig.REDIS_PORT
        self.ip_address = ip_address
        self.timeout = timeout
        self.connection = self.get_connection()

    def get_connection(self):
        try:
            return redis.StrictRedis(
                host=self.ip_address, port=self.port, db=0, socket_timeout=self.timeout
            )
        except redis.ConnectionError:
            return None

    def get(self, key):
        try:
            return self.connection.get(key)
        except redis.ConnectionError:
            return None

    def set(self, key, value, time):
        try:
            return self.connection.set(key, value, ex=time)
        except redis.ConnectionError:
            return 0


class Store:
    def __init__(
        self,
        address=RedisConfig.ADDRESS,
        port=RedisConfig.REDIS_PORT,
        retry=RedisConfig.RETRY_COUNT,
        timeout=RedisConfig.TIMEOUT,
    ):
        self.client = RedisClient(address, port, timeout)
        self.retry_count = retry

    def _get_helper(self, key):
        value = self.client.get(key)
        if value is None:
            for _ in range(self.retry_count):
                value = self.client.get(key)
                if value is not None:
                    break
        return value

    def get(self, key):
        value = self._get_helper(key)
        if value is None:
            raise OSError("Error due cache reading")
        return value

    def cache_get(self, key):
        return self._get_helper(key)

    # pylint: disable = no-value-for-parameter
    def cache_set(self, key, value, time):
        result = self.client.set(key, value, time)
        if result == 0:
            for _ in range(self.retry_count):
                value: int = self.client.get(key)
                if value:
                    return True
                else:
                    return 0
        return True
