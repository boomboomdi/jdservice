# -*- coding: utf-8 -*-#
import json
import base64
from urllib.parse import quote
from flask import Flask, make_response
import flask
import requests
from callback_jdsb import callback_task
from jd_yk import create_order

SUCCESS = 1
WEB_CK_UNVALUE = 2
CK_UNVALUE = 3
CK_PAY_FAIL = 4
NETWOTK_ERROR = 5
RET_CODE_ERROR = 6
CK_NO_ADDRESS = 7

def sdk2_android(ali_param):
    param = {
        'external_info': ali_param,
        'sourcePid': '1',
        'session': '',
        'pkgName': 'com.ss.android.ugc.aweme'
    }
    pay_url = 'alipays://platformapi/startapp?appId=20000125&mqpSchemePay=' +   \
        quote(str(base64.b64encode(bytes(json.dumps(param), 'utf-8')), 'utf-8'))
    print(pay_url)
    return pay_url

def sdk2_ios(ali_param):
    param = {
        'requestType': 'SafePay',
        'fromAppUrlScheme': 'alipays',
        'dataString': ali_param
    }
    return "alipaymatrixbwf0cml3://alipayclient/?" + quote(json.dumps(param))

GOOD_IDS = {
    '1': {
        '5000':'3'
    },
    '2':{
        '1000':'7'
    },
    '3':{
        '1000':'13'
    }
}

def get_proxy():
    url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=&username=chukou01&spec=1'
    return requests.get(url).text.strip()

def check_proxy(ip):
    proxy = {
        'http': ip,
        'https': ip
    }
    try:
        res = requests.get('http://www.baidu.com', proxies=proxy, timeout=3)
        if res.status_code == 200:
            return True
        return False
    except Exception:
        return False

def test_proxy(ip):
    url = 'http://2021.ip138.com'
    proxy = {
        'http': ip,
        'https': ip
    }
    head = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
        'Referer':'https://www.ip138.com/'
    }
    res = requests.get(url, headers=head, proxies=proxy)
    print(res.text)

def update_proxy(ck, proxy):
    pass

def update_ck_status(account, code):
    print('======== update_ck_status =========')
    url = 'http://175.178.150.157:9666/api/get/updateAccountState?account=' + str(account) + '&state=' + str(code)
    head = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    print(url)
    res = requests.get(url, headers=head)
    print(res.text)


    pass


app = Flask(__name__)
# 
@app.route('/test', methods=['GET'])
def index():
    a = flask.request.args.get('a')
    b = flask.request.args.get('b')
    return a + b

@app.route('/createYkOrder', methods=['POST'])
def createOrder():
    param = flask.request.get_json()
    ck = param.get('ck')
    amount = param.get('amount')
    account = param.get('account')
    skuid = param.get('skuid')
    card_id = param.get('cardId')
    phone_type = param.get('phoneType')
    print(ck)
    print(amount)
    print(account)
    print(skuid)
    print(card_id)
    code, pay_url, order_id = create_order(account, ck, skuid, card_id, amount, phone_type)
    if code == SUCCESS:
        order_info = {
            'payUrl': pay_url,
            'orderNo': order_id,
            'amount': amount
        }
        return json.dumps(order_info)
    elif code != NETWOTK_ERROR and code != RET_CODE_ERROR:
        update_ck_status(account, code)
        order_info = {
            'payUrl': 'error',
            'orderNo': '',
            'amount': ''
        }
        return json.dumps(order_info)
    elif code == NETWOTK_ERROR:
        print('!!!!!!!!!!! ip proxy error !!!!!!!!')

    # order_info = {
    #     'pay_url': '',
    #     'dy_order_no': '',
    #     'phone_type': phone_type,
    #     'amount': amount
    # }
    # order_info['pay_url'] = 'alipays://platformapi/startapp?appId=20000125&mqpSchemePay=eyJleHRlcm5hbF9pbmZvIjogImFsaXBheV9zZGs9YWxpcGF5LWVhc3lzZGstamF2YSZhcHBfaWQ9MjAyMTAwMjExODY5MTAyNiZiaXpfY29udGVudD0lN0IlMjJib2R5JTIyJTNBJTIyJUU4JUFGJTlEJUU4JUI0JUI5JUU1JTg1JTg1JUU1JTgwJUJDKzUwJUU1JTg1JTgzJTIyJTJDJTIyYnVzaW5lc3NfcGFyYW1zJTIyJTNBJTIyJTdCJTVDJTIybWNDcmVhdGVUcmFkZUlwJTVDJTIyJTNBJTVDJTIyMS42OC4xNjMuMTU5JTVDJTIyJTJDJTVDJTIyb3V0VHJhZGVSaXNrSW5mbyU1QyUyMiUzQSU1QyUyMiU3QiU1QyU1QyU1QyUyMm1jQ3JlYXRlVHJhZGVUaW1lJTVDJTVDJTVDJTIyJTNBJTVDJTVDJTVDJTIyMjAyMi0wMS0xOCsyMiUzQTI5JTNBMjUlNUMlNUMlNUMlMjIlN0QlNUMlMjIlN0QlMjIlMkMlMjJleHRlbmRfcGFyYW1zJTIyJTNBJTdCJTIyc3BlY2lmaWVkX3NlbGxlcl9uYW1lJTIyJTNBJTIyJTIyJTdEJTJDJTIyb3V0X3RyYWRlX25vJTIyJTNBJTIyMTIyMDExODAzMzg1NjMxMDM4MjQlMjIlMkMlMjJwcm9kdWN0X2NvZGUlMjIlM0ElMjJRVUlDS19NU0VDVVJJVFlfUEFZJTIyJTJDJTIyc2VsbGVyX2lkJTIyJTNBJTIyMjA4ODA0MTMxNzk3MDY2MiUyMiUyQyUyMnN1YmplY3QlMjIlM0ElMjIlRTglQUYlOUQlRTglQjQlQjklRTUlODUlODUlRTUlODAlQkMrNTAlRTUlODUlODMlMjIlMkMlMjJ0aW1lX2V4cGlyZSUyMiUzQSUyMjIwMjItMDEtMTgrMjIlM0E1OSUzQTI0JTIyJTJDJTIydG90YWxfYW1vdW50JTIyJTNBJTIyNTAuMDAlMjIlN0QmY2hhcnNldD11dGYtOCZmb3JtYXQ9anNvbiZtZXRob2Q9YWxpcGF5LnRyYWRlLmFwcC5wYXkmbm90aWZ5X3VybD1odHRwcyUzQSUyRiUyRmFwaS1jcGMuc25zc2RrLmNvbSUyRmdhdGV3YXklMkZwYXltZW50JTJGY2FsbGJhY2slMkZhbGlwYXklMkZub3RpZnklMkZwYXkmc2lnbj1ZMnRFNktZM2VsTE8zMjdSak1ZNHhqVkUzemJjTkQyV3ZDZno4eEJHMnEzd1BEN3p6dnhMeTJSUXVIbDJIYVJ6WHBrbmVHMDhxNVVPMHNhdHlTWVZxYU5VUTBjRThudmlBYjBQVGs0dHJxbHVkRGZqU3IyUHVLTjI0c3pIZ215Y2w2T1ZXQ3c5eERldG5nbnpWNTkycVhNazA3ZVN0MXBraTRDeXpYJTJCclVrR05rVXdoMkQ4bHRhZEY2cWFFQkNSJTJCaVFIZEtyMjVEM3J0b2JPUjlhWUV0WXNSTHclMkY0WFZvc1pRbTJNc1kydzJTT1VPVE9HcjhzMiUyQllTRiUyQnpTS1BEOFZLM0VPMGVxZUhRTHZNSHJrcmpwWklmZ1klMkZJV1M1cHVhcXJYOTR5MU1qaEN1UFhIbFJqWHd4MmlpeXpSYmFvQ3dlbGdsTGlxcG9oc0pkJTJCJTJCSGcwazB3JTNEJTNEJnNpZ25fdHlwZT1SU0EyJnRpbWVzdGFtcD0yMDIyLTAxLTE4KzIyJTNBMjklM0EyNSZ2ZXJzaW9uPTEuMCIsICJzb3VyY2VQaWQiOiAiMSIsICJzZXNzaW9uIjogIiIsICJwa2dOYW1lIjogImNvbS5zcy5hbmRyb2lkLnVnYy5hd2VtZSJ9'
    # order_info['dy_order_no'] = 'SP2022011822324539616394314226'
    # return json.dumps(order_info)

    # proxy_ip = get_proxy()
    # if not check_proxy(proxy_ip):
    #     print('================== proxy_ip error', proxy_ip)
    #     return False, None
    # print('================== use ip', proxy_ip)
    # good_id = GOOD_IDS[channel][amount]
    # huafei = dy_huafei(ck, proxy_ip)
    # status = huafei.mobile_plan(phone_num)
    # if status != SUCCESS:
    #     return handle_failed(status)
    # status, param = huafei.mobile_order_create(phone_num, amount, good_id)
    # if status != SUCCESS:
    #     return handle_failed(status)
    # status, app_id, tp_log_id, trade_no, process, promotion_process, risk_info = huafei.trade_create(param)
    # if status != SUCCESS:
    #     return handle_failed(status)
    # status, ali_param = huafei.trade_confirm(app_id, tp_log_id, trade_no, process, promotion_process, risk_info)
    # if status != SUCCESS:
    #     return handle_failed(status)
    # if phone_type == OS_ANDROID:
    #     order_info['pay_url'] = sdk2_android(ali_param)
    # elif phone_type == OS_IOS:
    #     order_info['pay_url'] = sdk2_ios(ali_param)
    # order_info['dy_order_no'] = trade_no
    # return json.dumps(order_info)


# @app.route('/query', methods=['POST'])
# def query_order():
#     print('==== create_order ====')
#     param = flask.request.get_json()
#     print(param)
#     ck = param.get('ck')
#     dy_order_no = param.get('dy_order_no')
#     proxy_ip = get_proxy()
#     if not check_proxy(proxy_ip):
#         return False, None
#     print('use ip', proxy_ip)
#     huafei = dy_huafei(ck, proxy_ip)
#     return huafei.query_order()


if __name__ == '__main__':
    app.debug = True
    app.run(port=23946)
    # update_ck_status('jd_uPvFzRIHqogg', SUCCESS)

