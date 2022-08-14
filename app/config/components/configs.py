from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    class Config:
        env_file = '../../../.env'


class RedisSettings(Settings):
    host: str = Field(..., env='REDIS_HOST')
    port: int = Field(..., env='REDIS_PORT')

REDIS_CONFIG = RedisSettings()


class CelerySettings(Settings):
    name = 'Bettingtools'
    broker = f'redis://{REDIS_CONFIG.host}:{REDIS_CONFIG.port}/0'
    backend = f'redis://{REDIS_CONFIG.host}:{REDIS_CONFIG.port}/0'

CELERY_CONFIG = CelerySettings()
