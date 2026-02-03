import os

class Settings:
    PROJECT_NAME = 'PowerLine Defects'
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

settings = Settings()
