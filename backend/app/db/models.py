from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "_user"

    id = Column(Integer, primary_key=True)
    account = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=True)
    tg_account = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)
    api_secret = Column(String(255), nullable=True)
    tg_token = Column(String(255), nullable=True)
    tg_chat_id = Column(String(255), nullable=True)
    bot_status = Column(Boolean, default=False)
    expired_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class Trading(Base):
    __tablename__ = "_trading"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    bot_status = Column(Boolean, default=False)
    symbol = Column(String(255), nullable=False)
    leverage = Column(Integer, nullable=False)
    tp = Column(Integer, nullable=True)
    sl = Column(Integer, nullable=True)
    add_order = Column(Integer, nullable=True)
    qty = Column(Float, nullable=False)
    dynamic = Column(JSON, nullable=True)

    # 신규추가
    current_add_order = Column(Integer, nullable=True)
    max_add_order = Column(Integer, nullable=True)
    listen_signal = Column(Integer, default=1, comment="시그널 리스닝 유무")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)


class History(Base):
    __tablename__ = "_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    bot_onoff = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    symbol = Column(String(255), nullable=True)
    leverage = Column(Integer, nullable=True)
    tp = Column(Integer, nullable=True)
    sl = Column(Integer, nullable=True)
    add_order = Column(Integer, nullable=True)
    qty = Column(Float, nullable=True)
    dynamic = Column(JSON, nullable=True)

    # 신규추가
    current_add_order = Column(Integer, nullable=True)
    max_add_order = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
