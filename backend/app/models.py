from . import db
from datetime import datetime, timedelta


# Helper function to add 9 hours
def utc_plus_9():
    return datetime.utcnow() + timedelta(hours=9)


class User(db.Model):
    __tablename__ = "_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="번호")
    account = db.Column(db.String(255), unique=True, nullable=False, comment="아이디")
    password = db.Column(db.String(255), nullable=False, comment="비밀번호")
    username = db.Column(db.String(255), nullable=False, comment="사용자명")
    phone = db.Column(
        db.String(255), nullable=True, comment="핸드폰번호"
    )  # NOT NULL 제거
    tg_account = db.Column(
        db.String(255), nullable=True, comment="텔레그램아이디"
    )  # NOT NULL 제거

    # Bybit
    api_key = db.Column(db.String(255), comment="API KEY")
    api_secret = db.Column(db.String(255), comment="API SECRET")

    # Telegram
    tg_token = db.Column(db.String(255), comment="텔레그램 봇 토큰")
    tg_chat_id = db.Column(db.String(255), comment="텔레그램 채팅 아이디")

    # Bot Status
    bot_status = db.Column(db.Boolean, default=False, comment="봇 상태")

    expired_at = db.Column(db.DateTime, default=None, comment="만료일시")
    created_at = db.Column(
        db.DateTime, default=utc_plus_9, nullable=False, comment="생성일시"
    )
    updated_at = db.Column(
        db.DateTime,
        default=None,
        onupdate=utc_plus_9,
        nullable=True,
        comment="수정일시",
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True, comment="삭제일시")

    def __repr__(self):
        return f"<User id={self.id} account={self.account}>"


class Trading(db.Model):
    __tablename__ = "_trading"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="번호")
    user_id = db.Column(
        db.Integer, db.ForeignKey("_user.id"), nullable=False, comment="사용자번호"
    )
    bot_status = db.Column(db.Boolean, default=False, comment="봇 상태")

    # Info
    symbol = db.Column(db.String(255), nullable=False, comment="심볼")
    leverage = db.Column(db.Integer, nullable=False, comment="레버리지")
    tp = db.Column(db.Integer, comment="Take Profit")
    sl = db.Column(db.Integer, comment="Stop Loss")
    add_order = db.Column(db.Integer, comment="물타기 회수")
    qty = db.Column(db.Float, nullable=False, comment="주문수량")

    # Dynamic input field
    dynamic = db.Column(db.JSON, default=None, comment="동적 입력 데이터")
    current_add_order = db.Column(
        db.Integer, default=0, comment="현재 물타기 회수"
    )  # 추가된 컬럼
    max_add_order = db.Column(
        db.Integer, default=0, comment="최대 물타기 회수"
    )  # 추가된 컬럼
    listen_signal = db.Column(
        db.Integer, default=1, comment="시그널 리스닝 유무"
    )  # 신규 컬럼

    created_at = db.Column(
        db.DateTime, default=utc_plus_9, nullable=False, comment="생성일시"
    )
    updated_at = db.Column(
        db.DateTime,
        default=None,
        onupdate=utc_plus_9,
        nullable=True,
        comment="수정일시",
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True, comment="삭제일시")

    def __repr__(self):
        return f"<Trading id={self.id} user_id={self.user_id} symbol={self.symbol}>"


class History(db.Model):
    __tablename__ = "_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="번호")
    user_id = db.Column(
        db.Integer, db.ForeignKey("_user.id"), nullable=False, comment="사용자번호"
    )

    # Info
    bot_onoff = db.Column(db.String(255), comment="봇 시작종료")
    position = db.Column(db.String(255), comment="포지션")
    symbol = db.Column(db.String(255), comment="심볼")
    leverage = db.Column(db.Integer, comment="레버리지")
    tp = db.Column(db.Integer, comment="Take Profit")
    sl = db.Column(db.Integer, comment="Stop Loss")
    add_order = db.Column(db.Integer, comment="물타기 회수")
    qty = db.Column(db.Float, nullable=False, comment="주문수량")

    # Dynamic input field
    dynamic = db.Column(db.JSON, default=None, comment="동적 입력 데이터")
    current_add_order = db.Column(
        db.Integer, default=0, comment="현재 물타기 회수"
    )  # 추가된 컬럼
    max_add_order = db.Column(
        db.Integer, default=0, comment="최대 물타기 회수"
    )  # 추가된 컬럼

    created_at = db.Column(
        db.DateTime, default=utc_plus_9, nullable=False, comment="생성일시"
    )
    updated_at = db.Column(
        db.DateTime,
        default=None,
        onupdate=utc_plus_9,
        nullable=True,
        comment="수정일시",
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True, comment="삭제일시")

    def __repr__(self):
        return f"<History id={self.id} user_id={self.user_id} symbol={self.symbol}>"
