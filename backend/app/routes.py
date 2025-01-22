# backend/app/routes.py
import os
import jwt
import asyncio
import subprocess
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app as app, request, jsonify, make_response, session, Response

from . import db


# ANCHOR GET sample
@app.route("/")
def index():
    return "Bot API Server"


# ANCHOR GET sample
@app.route("/api")
def api_index():
    return "OK"


# ------------------------------


# # ANCHOR 회원가입
# @app.route("/api/signUp", methods=["POST"])
# def signUp():
#     try:
#         # params
#         account = request.form.get("account")
#         password = request.form.get("password")
#         username = request.form.get("username")
#         uid = request.form.get("uid")

#         # 입력값 검증
#         if not account or not password or not username:
#             return make_response(
#                 jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#             )

#         # 중복 계정 체크
#         existing_user = User.query.filter_by(account=account).first()
#         if existing_user:
#             return make_response(
#                 jsonify({"message": "아이디가 이미 존재합니다.", "data": None}), 400
#             )

#         # 새로운 사용자 생성
#         new_user = User(
#             account=account,
#             password=password,
#             username=username,
#             tg_account=uid,
#         )

#         # 데이터베이스에 저장
#         db.session.add(new_user)
#         db.session.commit()

#         user_id = new_user.id

#         BTCUSDT = Trading.query.filter_by(user_id=user_id, symbol="BTCUSDT").first()
#         ETHUSDT = Trading.query.filter_by(user_id=user_id, symbol="ETHUSDT").first()
#         XRPUSDT = Trading.query.filter_by(user_id=user_id, symbol="XRPUSDT").first()
#         DOGEUSDT = Trading.query.filter_by(user_id=user_id, symbol="DOGEUSDT").first()

#         if BTCUSDT is None:
#             BTCUSDT = Trading(
#                 user_id=user_id,
#                 symbol="BTCUSDT",
#                 leverage=30,
#                 tp=10,
#                 sl=0,
#                 qty=0.001,
#                 add_order=0,
#             )
#             db.session.add(BTCUSDT)
#             db.session.commit()

#         if ETHUSDT is None:
#             ETHUSDT = Trading(
#                 user_id=user_id,
#                 symbol="ETHUSDT",
#                 leverage=30,
#                 tp=10,
#                 sl=0,
#                 qty=0.01,
#                 add_order=0,
#             )
#             db.session.add(ETHUSDT)
#             db.session.commit()

#         if XRPUSDT is None:
#             XRPUSDT = Trading(
#                 user_id=user_id,
#                 symbol="XRPUSDT",
#                 leverage=30,
#                 tp=10,
#                 sl=0,
#                 qty=5,
#                 add_order=0,
#             )
#             db.session.add(XRPUSDT)
#             db.session.commit()

#         if DOGEUSDT is None:
#             DOGEUSDT = Trading(
#                 user_id=user_id,
#                 symbol="DOGEUSDT",
#                 leverage=30,
#                 tp=10,
#                 sl=0,
#                 qty=30,
#                 add_order=0,
#             )
#             db.session.add(DOGEUSDT)
#             db.session.commit()

#         return make_response(
#             jsonify(
#                 {
#                     "message": "아이디가 생성되었습니다.",
#                     "data": {
#                         "userId": new_user.id,
#                     },
#                 }
#             ),
#             200,
#         )

#     except Exception as e:
#         # 에러 처리
#         db.session.rollback()
#         return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)


# # ANCHOR 키수정
# @app.route("/api/updateAuth", methods=["POST"])
# def updateAuth():
#     try:
#         # params
#         userId = request.form.get("userId")
#         api_key = request.form.get("apiKey")
#         api_secret = request.form.get("apiSecret")

#         # 입력값 검증
#         if not userId or not api_key or not api_secret:
#             return make_response(
#                 jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#             )

#         # API 키 중복 확인
#         existing_keys = User.query.filter(
#             (User.api_key == api_key) | (User.api_secret == api_secret)
#         ).first()
#         if existing_keys:
#             return make_response(
#                 jsonify(
#                     {
#                         "message": "중복된 API 키 또는 시크릿 키가 존재합니다.",
#                         "data": None,
#                     }
#                 ),
#                 400,
#             )

#         # 사용자 확인
#         user = User.query.filter_by(id=userId).first()
#         if not user:
#             return make_response(
#                 jsonify({"message": "사용자를 찾을 수 없습니다.", "data": None}), 404
#             )

#         # API 키 업데이트
#         user.api_key = api_key
#         user.api_secret = api_secret

#         # 데이터베이스 저장
#         db.session.commit()

#         return make_response(
#             jsonify(
#                 {
#                     "message": "API 키가 성공적으로 업데이트되었습니다.",
#                     "data": None,
#                 }
#             ),
#             200,
#         )

#     except Exception as e:
#         # 에러 처리
#         db.session.rollback()
#         return make_response(jsonify({"message": "시스템 오류", "data": str(e)}), 500)


# # ANCHOR 봇시작
# @app.route("/api/startBot", methods=["POST"])
# def startBot():
#     # params
#     user_id = request.form.get("userId")
#     symbol = request.form.get("symbol")

#     # 입력값 검증
#     if not user_id or not symbol:
#         return make_response(
#             jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#         )

#     # 데이터베이스 조회
#     user = User.query.filter_by(id=user_id).first()

#     # 데이터베이스 조회
#     trading = Trading.query.filter_by(user_id=user_id, symbol=symbol).first()

#     # 입력값 검증
#     if trading is None:
#         return make_response(
#             jsonify({"message": "봇 설정을 찾을 수 없습니다.", "data": None}), 400
#         )

#     script_name = f"bot_{user.id}_{symbol}"
#     script_path = os.path.abspath(__file__)
#     script_path = script_path.replace("routes.py", f"script.py")

#     print("script_name => ", script_name)
#     print("script_path => ", script_path)

#     out, err = start_script(script_name, script_path, user.id, symbol)
#     print("out => ", out)
#     print("err => ", err)

#     trading.bot_status = 1

#     # 데이터베이스 저장
#     db.session.commit()

#     return make_response(
#         jsonify(
#             {
#                 "message": "OK",
#                 "data": {
#                     "stdout": out,
#                     "stderr": err,
#                 },
#             }
#         ),
#         200,
#     )


# # ANCHOR 봇종료
# @app.route("/api/stopBot", methods=["POST"])
# def stopBot():
#     # params
#     user_id = request.form.get("userId")
#     symbol = request.form.get("symbol")

#     # 입력값 검증
#     if not user_id or not symbol:
#         return make_response(
#             jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#         )

#     # 데이터베이스 조회
#     user = User.query.filter_by(id=user_id).first()

#     # 데이터베이스 조회
#     trading = Trading.query.filter_by(user_id=user_id, symbol=symbol).first()

#     # 입력값 검증
#     if trading is None:
#         return make_response(
#             jsonify({"message": "봇 설정을 찾을 수 없습니다.", "data": None}), 400
#         )

#     # 봇 종료
#     out, err = stop_script(f"bot_{user.id}_{user.account}_{symbol}")
#     print("out => ", out)
#     print("err => ", err)

#     trading.bot_status = 0

#     # 데이터베이스 저장
#     db.session.commit()

#     return make_response(
#         jsonify(
#             {
#                 "message": "OK",
#                 "data": {
#                     "stdout": out,
#                     "stderr": err,
#                 },
#             }
#         ),
#         200,
#     )


# # ANCHOR 봇 설정 수정
# @app.route("/api/updateBotSetting", methods=["POST"])
# def updateBotSetting():
#     # params
#     user_id = request.form.get("userId")
#     symbol = request.form.get("symbol")

#     # 입력값 검증
#     if not user_id or not symbol:
#         return make_response(
#             jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#         )

#     # 데이터베이스 조회
#     trading = Trading.query.filter_by(user_id=user_id, symbol=symbol).first()

#     # 입력값 검증
#     if trading is None:
#         return make_response(
#             jsonify({"message": "봇 설정을 찾을 수 없습니다.", "data": None}), 400
#         )

#     leverage = request.form.get("leverage")
#     tp = request.form.get("tp")
#     sl = request.form.get("sl")
#     add_order = request.form.get("add_order")
#     qty = request.form.get("qty")
#     roi = request.form.get("roi")

#     # 동적 데이터 생성
#     dynamic_data = [
#         {"qty": qty, "roi": roi} for _ in range(int(add_order) if add_order else 0)
#     ]

#     # 봇 설정 업데이트
#     trading.leverage = leverage
#     trading.tp = tp
#     trading.sl = sl
#     trading.add_order = add_order
#     trading.qty = qty
#     trading.dynamic = dynamic_data

#     # 데이터베이스 저장
#     db.session.commit()

#     return make_response(
#         jsonify(
#             {
#                 "message": "봇 설정이 수정되었습니다.",
#                 "data": None,
#             }
#         ),
#         200,
#     )


# # ANCHOR 시그널시작
# @app.route("/api/startSignal", methods=["POST"])
# def startSignal():
#     # params
#     user_id = request.form.get("userId")
#     symbol = request.form.get("symbol")

#     # 입력값 검증
#     if not user_id or not symbol:
#         return make_response(
#             jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#         )

#     # 데이터베이스 조회
#     trading = Trading.query.filter_by(user_id=user_id, symbol=symbol).first()

#     # 입력값 검증
#     if trading is None:
#         return make_response(
#             jsonify({"message": "봇 설정을 찾을 수 없습니다.", "data": None}), 400
#         )

#     # 봇 설정 업데이트
#     trading.listen_signal = 1

#     # 데이터베이스 저장
#     db.session.commit()

#     return make_response(
#         jsonify(
#             {
#                 "message": "시그널 리스닝이 시작되었습니다.",
#                 "data": None,
#             }
#         ),
#         200,
#     )


# # ANCHOR 시그널종료
# @app.route("/api/stopSignal", methods=["POST"])
# def stopSignal():
#     # params
#     user_id = request.form.get("userId")
#     symbol = request.form.get("symbol")

#     # 입력값 검증
#     if not user_id or not symbol:
#         return make_response(
#             jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#         )

#     # 데이터베이스 조회
#     trading = Trading.query.filter_by(user_id=user_id, symbol=symbol).first()

#     # 입력값 검증
#     if trading is None:
#         return make_response(
#             jsonify({"message": "봇 설정을 찾을 수 없습니다.", "data": None}), 400
#         )

#     # 봇 설정 업데이트
#     trading.listen_signal = 0

#     # 데이터베이스 저장
#     db.session.commit()

#     return make_response(
#         jsonify(
#             {
#                 "message": "시그널 리스닝이 중지되었습니다.",
#                 "data": None,
#             }
#         ),
#         200,
#     )


# # ANCHOR 오더히스토리
# @app.route("/api/orderHistory", methods=["POST"])
# def orderHistory():
#     # params
#     user_id = request.form.get("userId")

#     # 입력값 검증
#     if not user_id:
#         return make_response(
#             jsonify({"message": "파라미터가 유효하지 않습니다.", "data": None}), 400
#         )

#     # 데이터베이스 조회
#     user = User.query.filter_by(id=user_id).first()
#     if not user:
#         return make_response(
#             jsonify({"message": "사용자를 찾을 수 없습니다.", "data": None}), 404
#         )

#     exchange = ExchangeBitunix(
#         symbol="BTCUSDT", api_key=user.api_key, api_secret=user.api_secret
#     )

#     data = exchange.getHistoryOrder()

#     return make_response(
#         jsonify(data),
#         200,
#     )
