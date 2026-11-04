#管理数据库连接和建表
from pathlib import Path
from sqlalchemy import create_engine,event

from e03_models import Base

db_path = Path(__file__).resolve().parent / "runs.db"   
engine = create_engine(f"sqlite:///{db_path}",echo = True)#创建管理数据库连接的对象

@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection,connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print(f"数据库位置：{db_path}")    
