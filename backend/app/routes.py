# backend/app/routes.py
import jwt
import datetime

from functools import wraps
from flask import current_app as app, request, jsonify, make_response, session, Response

# Database
from . import db
from .models import Admin, Account
from .exchange.exchange_bingx import ExchangeBingx

# Secret key for JWT
SECRET_KEY = "XbBtyL3Z9NzYUgzK8e6A"


# ANCHOR GET sample
@app.route("/")
def index():
    return "Bot API Server"


# ANCHOR GET sample
@app.route("/api")
def api_index():
    return "OK"


# ------------------------------


# JWT 인증 데코레이터
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("x-access-token")
        if not token:
            return make_response(
                jsonify({"message": "토큰이 없습니다.", "data": None}), 401
            )

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = Admin.query.filter_by(id=data["id"]).first()
        except Exception as e:
            return make_response(
                jsonify({"message": "토큰이 유효하지 않습니다.", "data": str(e)}), 401
            )

        return f(current_user, *args, **kwargs)

    return decorated


# ANCHOR 로그인
@app.route("/api/signIn", methods=["POST"])
def signIn():
    try:
        # params
        account = request.form.get("account")
        password = request.form.get("password")

        # 계정 확인
        admin = Admin.query.filter_by(account=account).first()
        if not admin:
            return make_response(
                jsonify({"message": "계정을 찾을 수 없습니다.", "data": None}),
                400,
            )

        # 비밀번호 확인
        if admin.password != password:
            return make_response(
                jsonify({"message": "비밀번호가 올바르지 않습니다.", "data": None}),
                400,
            )

        # JWT 생성
        token = jwt.encode(
            {
                "id": admin.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        return make_response(
            jsonify({"message": "로그인 되었습니다.", "data": {"token": token}}),
            200,
        )

    except Exception as e:
        # 에러 처리
        db.session.rollback()
        return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)


# ANCHOR 사용자 인증 및 정보 가져오기
@app.route("/api/getUser", methods=["GET"])
@token_required
def getUser(current_user):
    try:
        user_data = {
            "id": current_user.id,
            "account": current_user.account,
            "username": current_user.username,
        }

        return make_response(
            jsonify({"message": "사용자 정보 조회 성공", "data": user_data}),
            200,
        )

    except Exception as e:
        return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)


# ANCHOR 계정 목록 가져오기
@app.route("/api/getAccountList", methods=["GET"])
@token_required
def getAccountList(current_user):
    try:
        # Retrieve all accounts from the database
        accounts = Account.query.all()

        # Format the data as a list of dictionaries
        account_list = [
            {
                "id": account.id,
                "account": account.account,
                "token": account.token,
                "secret": account.secret,
            }
            for account in accounts
        ]

        return make_response(
            jsonify({"message": "계정 목록 조회 성공", "data": account_list}),
            200,
        )

    except Exception as e:
        return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)


# ANCHOR Buy
@app.route("/api/buy", methods=["POST"])
@token_required
def buy(current_user):
    try:
        # params
        account = request.form.get("account")
        symbol = request.form.get("symbol")
        qty = request.form.get("qty")

        # 계정 확인
        account = Account.query.filter_by(account=account).first()
        if not account:
            return make_response(
                jsonify({"message": "계정을 찾을 수 없습니다.", "data": None}),
                400,
            )

        token = account.token
        secret = account.secret

        print("token => ", token)
        print("secret => ", secret)

        # 빙엑스 인스턴스 생성
        exchange = ExchangeBingx(
            symbol=symbol,
            api_key=token,
            api_secret=secret,
        )

        # 레버리지 설정
        exchange.set_leverage(30)

        # 포지션 모드 설정 (One-way mode)
        exchange.set_position_mode()

        # 마진 모드 설정 (Cross mode)
        exchange.set_margin_type()

        result = exchange.order("BUY", qty)
        if result.get("result") == True:
            return make_response(
                jsonify(
                    {
                        "message": f"[{symbol}] 숏에 대해 수량({qty}) 주문 되었습니다.",
                        "data": None,
                    }
                ),
                200,
            )
        else:
            return make_response(
                jsonify({"message": f"주문 실패 ({result.get('msg')})", "data": None}),
                400,
            )

    except Exception as e:
        # 에러 처리
        db.session.rollback()
        return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)


# ANCHOR Sell
@app.route("/api/sell", methods=["POST"])
@token_required
def sell(current_user):
    try:
        # params
        account = request.form.get("account")
        symbol = request.form.get("symbol")
        qty = request.form.get("qty")

        # 계정 확인
        account = Account.query.filter_by(account=account).first()
        if not account:
            return make_response(
                jsonify({"message": "계정을 찾을 수 없습니다.", "data": None}),
                400,
            )

        token = account.token
        secret = account.secret

        print("token => ", token)
        print("secret => ", secret)

        # 빙엑스 인스턴스 생성
        exchange = ExchangeBingx(
            symbol=symbol,
            api_key=token,
            api_secret=secret,
        )

        # 레버리지 설정
        exchange.set_leverage(30)

        # 포지션 모드 설정 (One-way mode)
        exchange.set_position_mode()

        # 마진 모드 설정 (Cross mode)
        exchange.set_margin_type()

        result = exchange.order("SELL", qty)
        if result.get("result") == True:
            return make_response(
                jsonify(
                    {
                        "message": f"[{symbol}] 숏에 대해 수량({qty}) 주문 되었습니다.",
                        "data": None,
                    }
                ),
                200,
            )
        else:
            return make_response(
                jsonify({"message": f"주문 실패 ({result.get('msg')})", "data": None}),
                400,
            )

    except Exception as e:
        # 에러 처리
        db.session.rollback()
        return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)


# ANCHOR 포지션
@app.route("/api/getPosition", methods=["GET"])
@token_required
def getPosition(current_user):
    try:
        # params
        account = request.args.get("account")

        # 계정 확인
        account = Account.query.filter_by(account=account).first()
        if not account:
            return make_response(
                jsonify({"message": "계정을 찾을 수 없습니다.", "data": None}),
                400,
            )

        token = account.token
        secret = account.secret

        print("token => ", token)
        print("secret => ", secret)

        # 빙엑스 인스턴스 생성
        exchangeBTC = ExchangeBingx(
            symbol="BTC-USDT",
            api_key=token,
            api_secret=secret,
        )
        exchangeETH = ExchangeBingx(
            symbol="ETH-USDT",
            api_key=token,
            api_secret=secret,
        )

        btc = exchangeBTC.get_position_list()
        eth = exchangeETH.get_position_list()

        print("btc => ", btc)
        print("eth => ", eth)

        return make_response(
            jsonify(
                {
                    "message": "포지션 목록 조회 성공",
                    "data": {
                        "btc": btc,
                        "eth": eth,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)
