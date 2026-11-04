#定义两张表以及字段
from sqlalchemy import JSON,ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class RunRecord(Base):
    __tablename__ = "runs"
    request_id: Mapped[str] = mapped_column(primary_key=True)
    payload_hash: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    result: Mapped[dict] = mapped_column(JSON)

class RunItem(Base):
    __tablename__ = "run_items"
    request_id: Mapped[str] = mapped_column(ForeignKey("runs.request_id"),primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    error_code: Mapped[str | None] = mapped_column(nullable=True)
