import os
import time
import sys
import socketio
import pandas as pd
import requests

from datetime import datetime
from typing import List, Dict, Optional, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from exchange.exchange_bitunix import ExchangeBitunix
from config import DB_URL
from db.models import User, Trading

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NOTE 전역변수
# 텔레그램
TELEGRAM_BOT_TOKEN = "7632298781:AAGYnannsjQFniinCUcPAAuN5IpL7b9S1Hk"  # 봇 토큰
TELEGRAM_CHAT_ID = "-4511964608"

# 웹소켓
WS_URL = "wss://socket.chihiro.company/"

# 거래소 인스턴스
EXCHANGE = None

# 사용자
USER_ID = None
USER_NAME = None
ACCOUNT = None

# 봇 설정
SYMBOL = None
LEVERAGE = None
TP_PERCENT = None
SL_PERCENT = None
ADD_ORDER = None
QTY = None
DYNAMIC = None

# 신규
CURRENT_ADD_ORDER = 0
MAX_ADD_ORDER = 0

# 데이터베이스 엔진 생성
ENGINE = create_engine(DB_URL)

# 세션 팩토리 생성
SESSION_LOCAL = sessionmaker(bind=ENGINE)

# Socket.IO 클라이언트 설정
SIO = socketio.Client(
    reconnection=True,
    reconnection_delay=5,  # 재연결 시도 간격 (초)
    reconnection_delay_max=10,  # 최대 대기 시간 (초)
)


# SECTION 신호 처리
# ANCHOR 연결
@SIO.event
def connect() -> None:
    print("[INFO#] Socket.IO 서버에 연결되었습니다.")


# ANCHOR 연결 끊김
@SIO.event
def disconnect() -> None:
    global WS_URL
    print("[INFO#] Socket.IO 서버 연결이 끊어졌습니다. 재연결을 시도합니다.")
    try:
        SIO.connect(WS_URL)
    except Exception as e:
        print(f"[ERROR] 재연결 시도 중 오류 발생: {e}")


# ANCHOR 알림 수신
@SIO.on("alert")
def handle_alert(data: dict) -> None:
    process_signal(data)


# SECTION 함수
# LINK 텔레그램 메시지 보내기
def send_telegram_message(message: str) -> None:
    """
    텔레그램 메시지를 전송하는 함수

    Args:
        message (str): 전송할 메시지 내용

    Returns:
        None
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            pass
        else:
            print(f"[ERROR] 텔레그램 메시지 전송 실패: {response.text}")
    except Exception as e:
        print(f"[ERROR] 텔레그램 메시지 전송 중 오류 발생: {e}")


# LINK pm2 프로세스 정지
def stop_pm2_process() -> None:
    """
    pm2 프로세스를 정지하는 함수.

    Returns:
        None
    """
    global USER_ID
    global ACCOUNT
    global SYMBOL
    try:
        process_name = f"bot_{USER_ID}_{ACCOUNT}_{SYMBOL}"
        command = f"pm2 delete {process_name}"

        print(f"[DEBUG] 실행되는 커맨드 = {command}")

        # 봇 종료
        trading = Trading.query.filter_by(user_id=USER_ID, symbol=SYMBOL).first()
        trading.bot_status = False
        trading.save()

        print(f"[INFO] 봇이 종료되었습니다.")

        os.system(command)
        exit()
    except Exception as e:
        print(f"[ERROR] pm2 프로세스 정지 중 오류 발생: {e}")


# LINK 신호 처리
def process_signal(data: dict) -> None:
    """
    트레이딩뷰에서 발생한 신호를 처리하는 함수
    실질적으로 자체 웹소켓 서버에서 포워딩 해줍니다.

    Args:
        data (object): 발생한 신호 데이터

        신호의 패턴은 다음과 같습니다.

        Long 신호
        { "symbol": "BTCUSDT", "signal": "buy" }

        Short 신호
        { "symbol": "BTCUSDT", "signal": "sell" }

    Returns:
        None
    """

    # 글로벌 변수 사용
    global EXCHANGE
    global USER_ID
    global USER_NAME
    global SYMBOL
    global QTY

    # NOTE 유효성 - 신호 거부
    if data.get("symbol") != SYMBOL:
        return False

    # 포지션 조회
    position_list = EXCHANGE.get_pending_positions()

    # 포지션
    position = EXCHANGE.get_position(position_list)

    # 시그널 | "buy" or "sell"
    signal = data.get("signal")
    valid_signal_condition = signal in ["buy", "sell"]

    if valid_signal_condition and position is None:
        # 시그널이 정상적이고 포지션을 소유하고 있지 않은 경우
        position_side = "Long" if signal == "buy" else "Short"
        message = f"✈️ [Bitunix] {USER_NAME}님이 신호({signal})에 의해 포지션({position_side})을 진입합니다."

        # 출력
        print(message)

        # 텔레그램 발송
        send_telegram_message(message)

        # 주문 생성
        EXCHANGE.place_order(QTY, signal.upper())

        # 5초 대기
        time.sleep(5)

        # TP 설정
        position_list = EXCHANGE.get_pending_positions()
        position = EXCHANGE.get_position(position_list)
        TP_price = get_take_profit_price(position["avgOpenPrice"], signal)
        if TP_price is not None:
            EXCHANGE.set_tp(position["positionId"], TP_price)

    elif valid_signal_condition and position is not None:
        # 시그널이 정상적이고 BTC 포지션을 소유하고 있는 경우
        position_side = "Long" if position["side"] == "BUY" else "Short"
        message = f"⛱ [Bitunix] 신호({signal})가 들어왔지만 포지션({position_side})을 이미 보유 중이므로 스킵합니다. (사용자명: {USER_NAME})"

        # 출력
        print(message)

        # 텔래그램 발송
        send_telegram_message(message)


# LINK TP 가격 조회
def get_take_profit_price(entry_price: float, signal: str) -> float:
    """
    Take Profit(TP) 가격을 계산합니다.

    Args:
        entry_price (float): 진입 가격.
        signal (str): 신호 유형 ("buy" 또는 "sell").

    Returns:
        float: 계산된 TP 가격. TP_PERCENT가 None일 경우 None을 반환합니다.

    Global Variables:
        LEVERAGE (float): 레버리지 배율.
        TP_PERCENT (float): Take Profit 비율(퍼센트).

    Raises:
        None
    """
    global LEVERAGE
    global TP_PERCENT

    # 파라미터 방어
    entry_price = float(entry_price)

    if TP_PERCENT is None or TP_PERCENT == 0:
        return None

    # Take Profit 가격 계산
    if signal == "buy":
        TP_price = entry_price + ((entry_price / 100) / LEVERAGE) * TP_PERCENT
    elif signal == "sell":
        TP_price = entry_price - ((entry_price / 100) / LEVERAGE) * TP_PERCENT

    return TP_price


# LINK SL 가격 조회
def get_stop_loss_price(entry_price: float, signal: str) -> float:
    """
    Stop Loss(SL) 가격을 계산합니다.

    Args:
        entry_price (float): 진입 가격.
        signal (str): 신호 유형 ("buy" 또는 "sell").

    Returns:
        float: 계산된 SL 가격. SL_PERCENT가 None일 경우 None을 반환합니다.

    Global Variables:
        LEVERAGE (float): 레버리지 배율.
        SL_PERCENT (float): Stop Loss 비율(퍼센트).

    Raises:
        None
    """
    global LEVERAGE
    global SL_PERCENT

    # 파라미터 방어
    entry_price = float(entry_price)

    if SL_PERCENT is None or SL_PERCENT == 0:
        return None

    # Stop Loss 가격 계산
    if signal == "buy":
        # 매수 신호일 경우: 손절가는 진입 가격에서 SL_PERCENT만큼 하락
        SL_price = entry_price - ((entry_price / 100) / LEVERAGE) * SL_PERCENT
    elif signal == "sell":
        # 매도 신호일 경우: 손절가는 진입 가격에서 SL_PERCENT만큼 상승
        SL_price = entry_price + ((entry_price / 100) / LEVERAGE) * SL_PERCENT

    return SL_price


# LINK Unrealized P&L(ROI) % 계산 함수
def calculate_roi(position: Dict[str, any]) -> Optional[float]:
    try:
        # 미실현 손익과 초기 증거금 조회
        unrealized_pnl = float(position.get("unrealizedPNL", 0))
        margin = float(position.get("margin", 0))

        # 증거금이 0이면 ROI 계산 불가능
        if margin == 0:
            return None

        # ROI % 계산
        roi_percent = (unrealized_pnl / margin) * 100
        return round(roi_percent, 2)  # 소수점 2자리로 반환
    except Exception as e:
        # 예외 처리 및 로그 출력
        print(f"[ERROR] ROI 계산 중 오류 발생: {e}")
        return None


# LINK 바이비트 토큰 및 시크릿 조회
def get_bybit_info(user_id: int) -> Tuple[Optional[str], Optional[str]]:
    """
    데이터베이스에서 바이비트 API 키와 시크릿 키를 조회하는 함수.

    Args:
        user_id (int): 조회할 사용자의 고유 ID.

    Returns:
        Tuple[Optional[str], Optional[str]]:
            - api_key (Optional[str]): 사용자의 바이비트 API 키. 존재하지 않으면 None.
            - api_secret (Optional[str]): 사용자의 바이비트 API 시크릿 키. 존재하지 않으면 None.
    """
    session = SESSION_LOCAL()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return user.api_key, user.api_secret
        else:
            return None, None
    except Exception as e:
        print(f"[ERROR] 데이터 조회 중 오류 발생: {e}")
        return None, None
    finally:
        session.close()


# LINK 사용자 조회
def get_user(user_id: int) -> Optional[User]:
    """
    데이터베이스에서 사용자 정보를 조회하는 함수.

    Args:
        user_id (int): 조회할 사용자의 고유 ID.

    Returns:
        Optional[User]: 조회된 사용자 객체. 사용자가 없거나 오류가 발생하면 None을 반환.
    """
    session = SESSION_LOCAL()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return user
        else:
            return None
    except Exception as e:
        print(f"[ERROR] 데이터 조회 중 오류 발생: {e}")
        return None
    finally:
        session.close()


# LINK 트레이딩 조회
def get_trading(user_id: int, symbol: str) -> Optional[User]:
    """
    데이터베이스에서 트레이딩 정보를 조회하는 함수.

    Args:
        user_id (int): 조회할 사용자의 고유 ID.
        symbol (str): 조회할 심볼

    Returns:
        Optional[User]: 조회된 트레이딩 객체. 트레이딩이 없거나 오류가 발생하면 None을 반환.
    """
    session = SESSION_LOCAL()
    try:
        trading = (
            session.query(Trading).filter_by(user_id=user_id, symbol=symbol).first()
        )
        if trading:
            return trading
        else:
            return None
    except Exception as e:
        print(f"[ERROR] 데이터 조회 중 오류 발생: {e}")
        return None
    finally:
        session.close()


# LINK 현재 추가 주문 회수 업데이트
def update_current_add_order(current_add_order: int) -> None:
    """
    Trading 테이블의 current_add_order 값을 업데이트합니다.

    Args:
        current_add_order (int): 현재 추가 주문 카운트.

    Returns:
        None
    """
    session = SESSION_LOCAL()
    try:
        trading = (
            session.query(Trading).filter_by(user_id=USER_ID, symbol=SYMBOL).first()
        )
        if trading:
            trading.current_add_order = current_add_order
            session.commit()
            # print(
            #     f"[DEBUG] {USER_NAME}의 current_add_order: {current_add_order} 업데이트 완료."
            # )
    except Exception as e:
        print(f"[ERROR] current_add_order 업데이트 중 오류 발생: {e}")
    finally:
        session.close()


# LINK 현재 최고 주문 회수 업데이트
def update_max_add_order(max_add_order: int) -> None:
    """
    Trading 테이블의 max_add_order 값을 업데이트합니다.

    Args:
        max_add_order (int): 최대 추가 주문 카운트.

    Returns:
        None
    """
    session = SESSION_LOCAL()
    try:
        trading = (
            session.query(Trading).filter_by(user_id=USER_ID, symbol=SYMBOL).first()
        )
        if trading:
            trading.max_add_order = max_add_order
            session.commit()
            # print(
            #     f"[DEBUG] {USER_NAME}의 max_add_order: {max_add_order} 업데이트 완료."
            # )
    except Exception as e:
        print(f"[ERROR] max_add_order 업데이트 중 오류 발생: {e}")
    finally:
        session.close()


# ANCHOR 전략
def strategy():
    try:
        global WS_URL
        global EXCHANGE
        global USER_ID
        global USER_NAME
        global SYMBOL
        global ADD_ORDER

        global CURRENT_ADD_ORDER
        global MAX_ADD_ORDER

        # 추가 주문 카운터
        additional_order_count = CURRENT_ADD_ORDER

        # Socket.IO 서버에 연결
        SIO.connect(WS_URL)

        # 무한 루프
        while True:
            # 10초 대기
            time.sleep(10)

            # 시간 포맷팅 (예: 2024-11-17 15:42:05)
            fm_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 출력
            # print(f"[{fm_time}] {USER_NAME}님이 봇 기동중입니다.")

            # 포지션 리스트
            position_list = EXCHANGE.get_pending_positions()

            # 포지션
            position = EXCHANGE.get_position(position_list)

            # 포지션이 없는 경우
            if position is None:
                # 추가 주문 카운트 초기화
                additional_order_count = 0
                update_current_add_order(0)

                continue

            # 포지션 방향
            position_side = "Long" if position["side"] == "BUY" else "Short"

            # ROI
            roi = calculate_roi(position)

            # 로깅
            print(
                f"[{fm_time}] {USER_NAME}님의 {SYMBOL} 포지션({position_side})의 ROI는 {roi}% 입니다."
            )

            # null 방어 로직
            if additional_order_count == ADD_ORDER:
                continue

            # 다이나믹 추출
            qty_amount = DYNAMIC[additional_order_count]["qty"]
            roi_percent = DYNAMIC[additional_order_count]["roi"]

            print(
                f"[DEBUG] 대기중인 물타기 -{roi_percent}% 인 경우 {qty_amount} 수량이 추가됩니다."
            )

            # ROI 조건
            roi_condition = -1 * float(roi_percent)

            # ROI가 -n% 이하이고 추가 주문 카운트가 n 미만인 경우
            if float(roi) < roi_condition and additional_order_count < ADD_ORDER:
                # 추가 주문 카운트 증가
                additional_order_count += 1
                update_current_add_order(additional_order_count)

                # 최고 주문 카운트 갱신
                trading = get_trading(USER_ID, SYMBOL)
                if int(additional_order_count) > int(trading.max_add_order):
                    update_max_add_order(additional_order_count)

                message = f"🤢 [Bitunix] [{SYMBOL}] {USER_NAME}님의 ROI가 {roi_condition}% 이하입니다. 추가 주문을 생성합니다. (추가 주문 {additional_order_count}/{ADD_ORDER})"
                print(message)
                send_telegram_message(message)

                if position["side"] == "BUY":
                    EXCHANGE.place_order(qty=qty_amount, side="BUY")

                    # 5초 대기
                    time.sleep(5)

                    # TP 설정
                    position_list = EXCHANGE.get_pending_positions()
                    position = EXCHANGE.get_position(position_list)
                    TP_price = get_take_profit_price(position["avgOpenPrice"], "buy")
                    if TP_price is not None:
                        EXCHANGE.set_tp(position["positionId"], TP_price)
                elif position["side"] == "SELL":
                    EXCHANGE.place_order(qty=qty_amount, side="SELL")

                    # 5초 대기
                    time.sleep(5)

                    # TP 설정
                    position_list = EXCHANGE.get_pending_positions()
                    position = EXCHANGE.get_position(position_list)
                    TP_price = get_take_profit_price(position["avgOpenPrice"], "sell")
                    if TP_price is not None:
                        EXCHANGE.set_tp(position["positionId"], TP_price)

                if additional_order_count == ADD_ORDER:
                    if SL_PERCENT == 0:
                        message = f"👿 [Bitunix] {USER_NAME}님 마지막 물타기가 끝났습니다. 손절이 없으니 모니터링해서 대응 하세요!"
                    else:
                        message = f"👿 [Bitunix] {USER_NAME}님 마지막 물타기가 끝났습니다. 손절될 수도 있습니다! (ROI: {roi}, SL: {SL_PERCENT})"
                    print(message)
                    send_telegram_message(message)

    except KeyboardInterrupt as e:
        print(f"[INFO] 사용자에 의해 프로그램이 종료되었습니다.")
    finally:
        SIO.disconnect()
        print(f"[INFO] socket.io 연결이 종료되었습니다.")


if __name__ == "__main__":
    # 파라미터 확인
    if len(sys.argv) < 1 + 2:
        print("[WARN] 파라미터로 제대로 전달되지 않았습니다.")
        exit()

    # 파라미터
    user_id = int(sys.argv[1])  # 사용자번호
    symbol = sys.argv[2]  # 거래심볼

    user = get_user(user_id)

    # 전역변수 설정
    USER_ID = user.id  # 사용자번호
    USER_NAME = user.username  # 사용자명
    ACCOUNT = user.account  # 사용자아이디

    trading = get_trading(user_id, symbol)

    # 전역변수 설정
    SYMBOL = symbol
    LEVERAGE = trading.leverage
    TP_PERCENT = trading.tp
    SL_PERCENT = trading.sl
    ADD_ORDER = trading.add_order
    QTY = trading.qty
    DYNAMIC = trading.dynamic

    # 신규
    CURRENT_ADD_ORDER = trading.current_add_order
    MAX_ADD_ORDER = trading.max_add_order

    # 로깅
    print(
        f"""
<파라미터 정보>
사용자번호: {user_id}
사용자명: {USER_NAME}
심볼: {SYMBOL}
레버리지: {LEVERAGE}
TP: {TP_PERCENT}
SL: {SL_PERCENT}
물타기: {ADD_ORDER}
첫주문수량: {QTY}
현재 물타기 카운트: {CURRENT_ADD_ORDER}
최고 물타기 카운트: {MAX_ADD_ORDER}
        """
    )

    # 바이비트 토큰 및 시크릿 조회
    api_key, api_secret = get_bybit_info(user_id)

    # 비트유닉스 인스턴스 생성
    EXCHANGE = ExchangeBitunix(
        symbol=SYMBOL,
        api_key=api_key,
        api_secret=api_secret,
    )

    # 레버리지 설정
    EXCHANGE.change_leverage(leverage=LEVERAGE)

    # 마진모드 설정
    EXCHANGE.change_margin_mode(marginMode="CROSS")

    # 포지션모드 설정
    EXCHANGE.change_position_mode(positionMode="ONE_WAY")

    # 주문
    # EXCHANGE.place_order(qty="0.001", side="BUY")
    # EXCHANGE.place_order(qty="0.001", side="SELL")

    # ANCHOR 전략 실행
    strategy()
