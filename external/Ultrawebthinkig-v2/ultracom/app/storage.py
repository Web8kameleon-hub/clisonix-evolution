import os
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, select, desc

DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///./ultracom.db")

engine = create_async_engine(DB_URL, future=True, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room: Mapped[str] = mapped_column(String(128), index=True)
    role: Mapped[str] = mapped_column(String(16))
    sender: Mapped[str] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(String(8000))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_message(room:str, role:str, sender:str, text:str) -> Message:
    async with Session() as s:
        m = Message(room=room, role=role, sender=sender, text=text, ts=datetime.utcnow())
        s.add(m)
        await s.commit()
        await s.refresh(m)
        return m

async def get_history(room:str, limit:int=50, offset:int=0) -> List[Message]:
    async with Session() as s:
        q = select(Message).where(Message.room==room).order_by(desc(Message.ts)).limit(limit).offset(offset)
        res = (await s.execute(q)).scalars().all()
        return list(reversed(res))  # kthim në rend rritës kohor
