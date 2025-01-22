from . import db
from datetime import datetime, timedelta


# Helper function to add 9 hours
def utc_plus_9():
    return datetime.utcnow() + timedelta(hours=9)


class Admin(db.Model):
    __tablename__ = "_admin"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="id")
    account = db.Column(db.String(255), unique=True, nullable=False, comment="account")
    password = db.Column(db.String(255), nullable=False, comment="password")
    username = db.Column(db.String(255), nullable=False, comment="username")

    created_at = db.Column(
        db.DateTime, default=utc_plus_9, nullable=False, comment="create time"
    )
    updated_at = db.Column(
        db.DateTime,
        default=None,
        onupdate=utc_plus_9,
        nullable=True,
        comment="update time",
    )
    deleted_at = db.Column(
        db.DateTime, default=None, nullable=True, comment="delete time"
    )

    def __repr__(self):
        return f"<Admin id={self.id} account={self.account}>"


class Account(db.Model):
    __tablename__ = "_account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="id")
    account = db.Column(db.String(255), unique=True, nullable=False, comment="account")
    token = db.Column(db.String(255), nullable=False, comment="token")
    secret = db.Column(db.String(255), nullable=False, comment="secret")

    created_at = db.Column(
        db.DateTime, default=utc_plus_9, nullable=False, comment="create time"
    )
    updated_at = db.Column(
        db.DateTime,
        default=None,
        onupdate=utc_plus_9,
        nullable=True,
        comment="update time",
    )
    deleted_at = db.Column(
        db.DateTime, default=None, nullable=True, comment="delete time"
    )

    def __repr__(self):
        return f"<Account id={self.id} account={self.account}>"
