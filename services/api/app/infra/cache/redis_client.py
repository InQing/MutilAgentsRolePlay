from redis.asyncio import Redis


class RedisClientFactory:
    def __init__(self, url: str) -> None:
        self.url = url

    def create(self) -> Redis:
        return Redis.from_url(self.url, decode_responses=True)

