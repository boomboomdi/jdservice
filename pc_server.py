# -*- coding: utf-8 -*-#
from random import randint
from time import sleep
from urllib.parse import quote
from flask import Flask, session
import flask
import requests
import threading
from tools import LOG_D
from pc_jd import order_appstore


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

@app.route('/createOrderAppstore', methods=['POST'])
def queryResult():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    order_me = str(param.get('order_me'))
    amount = str(param.get('amount'))
    threading.Thread(target=order_appstore, args=(ck, order_me, amount)).start()
    return 'success'
    # return '{"code": 0, "msg": "SUCCESS", "data": {"phone": "' + phone + '", "amount": 469.19}, "sign": "488864C0AB51AEA0AF551074446FBCEC"}'

@app.route('/queryOrder', methods=['POST'])
def callBack():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    order_me = str(param.get('order_me'))
    order_pay = str(param.get('order_pay'))
    amount = str(param.get('amount'))
    print('callback:', order_no, account, pay_status)
    return "success"

@app.route('/callBackDv', methods=['POST'])
def callBackDv():
    param = flask.request.get_json()
    print('callback dv:', param)
    return "success"


if __name__ == '__main__':
    # threading.Thread(target=query_task).start()
    app.debug = False
    app.run(port=23942)