# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 인스턴스 생성
db = SQLAlchemy()


def to_kst(dt):
    """Convert UTC datetime to KST."""
    if dt is None:
        return None
    kst = timezone("Asia/Seoul")
    return dt.astimezone(kst)


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config")  # config 파일을 불러옵니다.

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # SQLAlchemy 초기화
    db.init_app(app)

    # SQLAlchemy 이벤트로 UTC → KST 처리
    @db.event.listens_for(db.session, "before_flush")
    def handle_utc_to_kst(session, flush_context, instances):
        for instance in session.new:
            if hasattr(instance, "created_at"):
                instance.created_at = to_kst(instance.created_at)
            if hasattr(instance, "updated_at"):
                instance.updated_at = to_kst(instance.updated_at)

    with app.app_context():
        # 라우트와 블루프린트를 등록합니다.
        from . import routes

        return app
