import os
import pytest
from src.models import Base, engine

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # 测试开始前，在 Postgres 数据库中自动创建所有数据表（包括 applicants）
    Base.metadata.create_all(bind=engine)
    yield