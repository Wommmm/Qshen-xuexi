from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
from datetime import datetime 
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4

# run(...)	创建携带数据的模型实例
# session.add(record)	把对象交给Session跟踪
# session.flush()	执行待处理写入，但不提交事务
# session.commit()	通常先flush，再提交事务
# session.rollback()	回滚当前未提交事务
# session.get(run, 编号)	按主键查询，返回模型实例或None

db_path = Path(__file__).resolve().parent / "runs.db"
engine = create_engine(f"sqlite:///{db_path.as_posix()}",echo = True)

class Base(DeclarativeBase):
    #DeclarativeBase	提供定义数据库模型的基础能力
    pass

class run(Base):
    __tablename__ = "run_records"
    # Mapped[str]	声明这个属性映射到数据库，Python值为字符串
    # mappend_column()配置对应的数据库列，例如是否为主键
    run_id:Mapped[str] = mapped_column(primary_key = True)
    status:Mapped[str] = mapped_column()
    latency_ms:Mapped[int] = mapped_column()
    create_at : Mapped[datetime] = mapped_column()

#保存表结构描述
Base.metadata.create_all(engine)

#进入上下文，将 Session 对象绑定给 session；退出时关闭 Session。
with Session(engine) as session:
#创建实例
    record = run(
        run_id = uuid4().hex,status = "success",
        latency_ms = 120,create_at = datetime.now(),
    )
    #跟踪这条待保存的记录
    saved_run_id = record.run_id
    session.add(record)
    try:
        #将带写入的数据发送给数据库
        session.commit()
        #捕获这类库报告的操作错误
    except SQLAlchemyError:
        session.rollback()
        print("发生故障，本次写入已回滚")
        raise
    

with Session(engine) as session:
    saved_record = session.get(run,saved_run_id)
    if saved_record is not None:
        print(saved_record.run_id,saved_record.status)
        print(saved_record.latency_ms,saved_record.create_at)
    else:
        print("未找到该记录")        