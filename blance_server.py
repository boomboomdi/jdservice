# -*- coding: utf-8 -*-#
import json
import base64
from random import randint
from time import sleep
from urllib.parse import quote
from flask import Flask, session
import flask
import requests
from blance import query_blance, query_blance_first
from query_blance_task import query_result
import phone_sqlite
import threading
from tools import LOG_D
from query_blance_task import query_task
from phone_sqlite import phone_sqlite

SUCCESS = 0
CK_UNABLE = 1
NET_ERROR = 2
CODE_ERROR = 3

PHONE = 0
ORDER_NO = 1

app = Flask('app')

@app.route('/test', methods=['GET'])
def index():
    a = flask.request.args.get('a')
    b = flask.request.args.get('b')
    return a + b

@app.route('/queryBlance', methods=['POST'])
def queryResult():
    param = flask.request.get_json()
    phone = str(param.get('phone'))
    order_no = str(param.get('order_no'))
    action =  param.get('action')
    if action == 'first':
        return query_blance_first(phone)
        # sleep(3)
        # return '{"code": 0, "msg": "SUCCESS", "data": {"phone": "' + phone + '", "amount": 469.19}, "sign": "488864C0AB51AEA0AF551074446FBCEC"}'
    else:
        # sql = phone_sqlite()
        # sql.insert_phone(phone, order_no)
        # phone_mysql.insert_task(phone, order_no)
        threading.Thread(target=query_result, args=(phone, order_no)).start()
    return 'success'
    # return '{"code": 0, "msg": "SUCCESS", "data": {"phone": "' + phone + '", "amount": 469.19}, "sign": "488864C0AB51AEA0AF551074446FBCEC"}'

@app.route('/callBack', methods=['POST'])
def callBack():
    param = flask.request.get_json()
    order_no = param.get('order_no')
    account = param.get('account')
    pay_status = param.get('pay_status')
    print('callback:', order_no, account, pay_status)
    return "success"

@app.route('/callBackDv', methods=['POST'])
def callBackDv():
    param = flask.request.get_json()
    print('callback dv:', param)
    return "success"

@app.route('/getQrcode', methods=['POST'])
def getQrcode():
    param = flask.request.get_json()
    print(param)
    phone = param['phone']
    print(phone)
    url = 'http://119.188.210.40:10086/index/Payurl/wx?tel=' + phone + '&key=26fc99ec0a0432e66228b0113649ea40'
    res = requests.get(url).json()
    if res['code'] == 1:
        result = {}
        result['code'] = 1
        result['qrcode'] = res['url']
        return json.dumps(result)
    else:
        result = {}
        result['code'] = -1
        return json.dumps(result)
    return ''


if __name__ == '__main__':
    # threading.Thread(target=query_task).start()
    app.debug = False
    app.run(port=23943, threaded=True)
    # app.run(host='0.0.0.0', port=23943)
