# -*- coding: utf-8 -*-#
from random import randint
from time import sleep
from urllib.parse import quote
from flask import Flask, session
import flask
import requests
import threading
from tools import LOG_D
from pc_jd import order_appstore, query_order_appstore, get_real_url


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
def createOrderAppstore():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    order_me = str(param.get('order_me'))
    amount = str(param.get('amount'))
    threading.Thread(target=order_appstore, args=(ck, order_me, amount)).start()
    return 'success'
    # return '{"code": 0, "msg": "SUCCESS", "data": {"phone": "' + phone + '", "amount": 469.19}, "sign": "488864C0AB51AEA0AF551074446FBCEC"}'

@app.route('/queryAppstore', methods=['POST'])
def queryAppstore():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    order_me = str(param.get('order_me'))
    order_pay = str(param.get('order_pay'))
    amount = str(param.get('amount'))
    print(param)
    print('========')
    threading.Thread(target=query_order_appstore, args=(ck, order_me, order_pay, amount)).start()
    return "success"

@app.route('/queryAppstoreImmediate', methods=['POST'])
def queryAppstore():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    order_me = str(param.get('order_me'))
    order_pay = str(param.get('order_pay'))
    amount = str(param.get('amount'))
    print(param)
    print('========')
    threading.Thread(target=query_order_appstore, args=(ck, order_me, order_pay, amount)).start()
    return "success"

@app.route('/getRealurl', methods=['POST'])
def getRealurl():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    url = str(param.get('url'))
    print(param)
    print('========')
    return get_real_url(ck, url)

@app.route('/callBackDv', methods=['POST'])
def callBackDv():
    param = flask.request.get_json()
    print('callback dv:', param)
    return "success"


if __name__ == '__main__':
    # threading.Thread(target=query_task).start()
    app.debug = False
    app.run(port=23942)
