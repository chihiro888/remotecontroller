from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from config import DB_URL

# SQLAlchemy Engine 생성
engine = create_engine(DB_URL, echo=True)

# 세션 팩토리 생성
Session = sessionmaker(bind=engine)


@contextmanager
def get_session():
    """
    세션 생성 및 종료를 관리하는 함수.
    """
    session = Session()  # 새 세션 생성
    try:
        yield session  # 세션 반환
    finally:
        session.close()  # 세션 종료
