# playground/exchange_bybit.py
import os
import time
import sys
import requests
import hmac
import json
from hashlib import sha256

from pybit.unified_trading import HTTP

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ExchangeBingx:
    def __init__(self, symbol: str, api_key: str, api_secret: str):
        self.symbol = symbol
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://open-api.bingx.com/"

    def __repr__(self):
        return f"<ExchangeBingx(symbol={self.symbol}, api_key={self.api_key}, api_secret={self.api_secret})>"

    def get_sign(self, api_secret, payload):
        signature = hmac.new(
            api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256
        ).hexdigest()
        # print("sign=" + signature)
        return signature

    def send_request(self, method, path, urlpa, payload):
        url = "%s%s?%s&signature=%s" % (
            self.base_url,
            path,
            urlpa,
            self.get_sign(self.api_secret, urlpa),
        )
        # print(url)
        headers = {
            "X-BX-APIKEY": self.api_key,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        return response.text

    def parseParam(self, paramsMap, timestmp):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        if paramsStr != "":
            return paramsStr + "&timestamp=" + timestmp
        else:
            return paramsStr + "timestamp=" + timestmp

    def set_margin_type(self):
        payload = {}
        path = "/openApi/swap/v2/trade/marginType"
        method = "POST"
        timestmp = str(int(time.time() * 1000))
        paramsMap = {
            "symbol": self.symbol,
            "marginType": "CROSSED",
            "recvWindow": "60000",
            "timestamp": timestmp,
        }
        paramsStr = self.parseParam(paramsMap, timestmp)
        result = self.send_request(method, path, paramsStr, payload)
        result = json.loads(result)
        print("set_margin_type result => ", result)
        if result.get("code") == 0:
            return True
        else:
            return False

    def set_position_mode(self):
        payload = {}
        path = "/openApi/swap/v1/positionSide/dual"
        method = "POST"
        timestmp = str(int(time.time() * 1000))
        paramsMap = {"dualSidePosition": "false", "timestamp": timestmp}
        paramsStr = self.parseParam(paramsMap, timestmp)
        result = self.send_request(method, path, paramsStr, payload)
        result = json.loads(result)
        print("set_position_mode result => ", result)
        if result.get("code") == 0:
            return True
        else:
            return False

    def set_leverage(self, leverage):
        payload = {}
        path = "/openApi/swap/v2/trade/leverage"
        method = "POST"
        timestmp = str(int(time.time() * 1000))
        paramsMap = {
            "leverage": str(leverage),
            "side": "BOTH",
            "symbol": self.symbol,
            "timestamp": timestmp,
        }
        paramsStr = self.parseParam(paramsMap, timestmp)
        result = self.send_request(method, path, paramsStr, payload)
        result = json.loads(result)
        print("set_leverage result => ", result)
        if result.get("code") == 0:
            return True
        else:
            return False

    def order(self, side, qty):
        payload = {}
        path = "/openApi/swap/v2/trade/order"
        method = "POST"
        timestmp = str(int(time.time() * 1000))
        paramsMap = {
            "symbol": self.symbol,
            "type": "MARKET",
            "side": side,  # SELL or BUY
            "positionSide": "BOTH",
            "timestmp": timestmp,
            "quantity": qty,
        }
        paramsStr = self.parseParam(paramsMap, timestmp)
        result = self.send_request(method, path, paramsStr, payload)
        result = json.loads(result)
        print("order result => ", result)
        if result.get("code") == 0:
            return {"result": True, "msg": ""}
        else:
            return {"result": False, "msg": result.get("msg")}

    def set_tp(self, side, price, qty):
        payload = {}
        path = "/openApi/swap/v2/trade/order"
        method = "POST"
        timestmp = str(int(time.time() * 1000))
        paramsMap = {
            "symbol": self.symbol,
            "type": "TAKE_PROFIT_MARKET",
            "side": side,  # SELL or BUY
            "positionSide": "BOTH",
            "timestmp": timestmp,
            "stopPrice": price,
            "price": price,
            "workingType": "MARK_PRICE",
            "quantity": qty,
        }
        paramsStr = self.parseParam(paramsMap, timestmp)
        result = self.send_request(method, path, paramsStr, payload)
        result = json.loads(result)
        print("set_tp result => ", result)
        if result.get("code") == 0:
            return True
        else:
            return False

    def get_position_list(self):
        payload = {}
        path = "/openApi/swap/v2/user/positions"
        method = "GET"
        timestmp = str(int(time.time() * 1000))
        paramsMap = {
            "symbol": self.symbol,
            "timestamp": timestmp,
        }
        paramsStr = self.parseParam(paramsMap, timestmp)
        result = self.send_request(method, path, paramsStr, payload)
        result = json.loads(result)
        if result.get("code") == 0:
            return result.get("data")
        else:
            return []

    def get_position(self, position_list):
        for position in position_list:
            if position.get("symbol") == self.symbol:
                return position
        return None

    def cancel_all_open_orders(self):
        payload = {}
        path = "/openApi/swap/v2/trade/allOpenOrders"
        method = "DELETE"
        timestmp = str(int(time.time() * 1000))
        paramsMap = {
            "recvWindow": "0",
            "symbol": self.symbol,
            "type": "TAKE_PROFIT_MARKET",
            "timestamp": timestmp,
        }
        paramsStr = self.parseParam(paramsMap, timestmp)
        result = self.send_request(method, path, paramsStr, payload)
        result = json.loads(result)
        print("cancel_all_open_orders result => ", result)
        if result.get("code") == 0:
            return True
        else:
            return False
