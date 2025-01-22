import requests
import time
import hashlib
import json
import random
import string
import re
from datetime import datetime


class ExchangeBitunix:
    def __init__(self, symbol: str, api_key: str, api_secret: str):
        self.symbol = symbol
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://fapi.bitunix.com/"

    def __repr__(self):
        return f"<ExchangeBitunix(symbol={self.symbol}, api_key={self.api_key}, api_secret={self.api_secret})>"

    def sha256_hex(self, input_string):
        return hashlib.sha256(input_string.encode("utf-8")).hexdigest()

    def generate_timestamp(self):
        return str(int(time.time()))

    def generate_nonce(self):
        return "".join(random.choices(string.ascii_letters + string.digits, k=32))

    def generate_sign_api(self, method, data):
        nonce = self.generate_nonce()
        timestamp = self.generate_timestamp()
        api_key = self.api_key
        secret_key = self.api_secret

        query_params = ""
        body = ""

        # print("data => ", data)

        if data:
            if method == "get":
                data = {k: v for k, v in data.items() if v is not None}
                query_params = "&".join([f"{k}={v}" for k, v in sorted(data.items())])
                query_params = re.sub(r"[^a-zA-Z0-9]", "", query_params)
            if method == "post":
                body = str(data)

        # print("query_params => ", query_params)

        digest_input = nonce + timestamp + api_key + query_params + body
        digest = self.sha256_hex(digest_input)
        sign_input = digest + secret_key
        sign = self.sha256_hex(sign_input)

        return sign, nonce, timestamp

    def change_leverage(self, leverage: int, margin_coin: str = "USDT") -> dict:
        endpoint = "api/v1/futures/account/change_leverage"
        url = f"{self.base_url}{endpoint}"
        method = "post"
        data = json.dumps(
            {"marginCoin": "USDT", "symbol": self.symbol, "leverage": leverage}
        )
        sign, nonce, timestamp = self.generate_sign_api(method, data)
        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "language": "en-US",
            "Content-Type": "application/json",
        }
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        res = response.json()
        if res.get("code") == 0:
            return True
        else:
            return False

    def change_margin_mode(self, marginMode, margin_coin: str = "USDT"):
        endpoint = "api/v1/futures/account/change_margin_mode"
        url = f"{self.base_url}{endpoint}"
        method = "post"
        data = json.dumps(
            {"marginCoin": "USDT", "symbol": self.symbol, "marginMode": marginMode}
        )
        sign, nonce, timestamp = self.generate_sign_api(method, data)
        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "language": "en-US",
            "Content-Type": "application/json",
        }
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        print(response.json())

    def change_position_mode(self, positionMode):
        endpoint = "api/v1/futures/account/change_position_mode"
        url = f"{self.base_url}{endpoint}"
        method = "post"
        data = json.dumps({"positionMode": positionMode})
        sign, nonce, timestamp = self.generate_sign_api(method, data)
        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "language": "en-US",
            "Content-Type": "application/json",
        }
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        print(response.json())

    def place_order(self, qty, side):
        endpoint = "api/v1/futures/trade/place_order"
        url = f"{self.base_url}{endpoint}"
        method = "post"
        data = json.dumps(
            {
                "symbol": self.symbol,
                "qty": qty,
                "side": side,
                "orderType": "MARKET",
                "effect": "GTC",
            }
        )
        sign, nonce, timestamp = self.generate_sign_api(method, data)
        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "language": "en-US",
            "Content-Type": "application/json",
        }
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        print(response.json())

    def get_pending_positions(self):
        endpoint = "api/v1/futures/position/get_pending_positions"
        url = f"{self.base_url}{endpoint}"
        method = "get"
        data = {}
        sign, nonce, timestamp = self.generate_sign_api(method, data)
        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "language": "en-US",
            "Content-Type": "application/json",
        }
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        # print(response.json())

        return response.json().get("data", [])

    def get_position(self, position_list):
        for position in position_list:
            if position.get("symbol") == self.symbol:  # self.symbol과 일치하는지 확인
                return position
        return None  # 일치하는 값이 없으면 None 반환

    def set_tp(self, positionId, tpPrice):
        endpoint = "api/v1/futures/tpsl/position/place_order"
        url = f"{self.base_url}{endpoint}"
        method = "post"
        data = json.dumps(
            {
                "symbol": self.symbol,
                "positionId": positionId,
                "tpPrice": tpPrice,
                "tpStopType": "LAST_PRICE",
            }
        )
        sign, nonce, timestamp = self.generate_sign_api(method, data)
        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "language": "en-US",
            "Content-Type": "application/json",
        }
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        print(response.json())

    def getHistoryOrder(self):
        endpoint = "api/v1/futures/trade/get_history_orders"
        url = f"{self.base_url}{endpoint}"
        method = "get"
        data = {}
        sign, nonce, timestamp = self.generate_sign_api(method, data)
        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "language": "en-US",
            "Content-Type": "application/json",
        }
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        return response.json()
