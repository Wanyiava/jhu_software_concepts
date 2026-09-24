import os
import pytest
from src.models import Base, engine

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # 测试开始前，在 Postgres 数据库中自动创建所有数据表
    Base.metadata.create_all(bind=engine)
    yield
    # 测试结束后，显式释放数据库引擎连接，防止进程挂起退出
    engine.dispose()