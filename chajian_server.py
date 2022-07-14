# -*- coding: utf-8 -*-#
import json
from random import randint
from time import sleep
from urllib.parse import quote
from flask import Flask, session
import flask
import requests
import threading
from tools import LOG_D


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

pkgs = {
    '0': {
        'pgkName': 'com.jd.pingou',
        'appName': u'京东旗下的京喜app',
        'downloadUrl': 'https://wqs.jd.com/wxsq_item_search/download/downloadPgApp/index.html?channel=pingou_jdpay1',
        'title': '您未安装京东旗下的京喜app，仅安装无需打开登录，充值百分百成功，大额无忧！安装可返回继续支付'
    },
    '1':{
        'pgkName': 'com.jingdong.app.mall',
        'appName': u'京东app',
        'downloadUrl': 'https://wqs.jd.com/downloadApp/download.html?channel=jdbdad-pinzhuan',
        'title': '您未安装京东app，仅安装无需打开登录，充值百分百成功，大额无忧！安装可返回继续支付'
    }
}

@app.route('/getPkgs', methods=['POST'])
def queryAppstore():
    param = flask.request.get_json()
    ts = str(param.get('ts'))
    return json.dumps(pkgs)


@app.route('/callBackDv', methods=['POST'])
def callBackDv():
    param = flask.request.get_json()
    print('callback dv:', param)
    return "success"


if __name__ == '__main__':
    # threading.Thread(target=query_task).start()
    # app.debug = False
    app.debug = True
    app.run(host='0.0.0.0', port=23938)

