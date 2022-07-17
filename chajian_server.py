# -*- coding: utf-8 -*-#
import json
from pydoc import cli
from random import randint
from time import sleep
from urllib.parse import quote
from flask import Flask, session
import flask
from pkg_resources import resource_listdir
import requests
import threading
from jingdong import jd
from jingxi import jx
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
        'title': u'您未安装京东旗下的京喜app，仅安装无需打开登录，充值百分百成功，大额无忧！安装可返回继续支付'
    },
    '1':{
        'pgkName': 'com.jingdong.app.mall',
        'appName': u'京东app',
        'downloadUrl': 'https://wqs.jd.com/downloadApp/download.html?channel=jdbdad-pinzhuan',
        'title': u'您未安装京东app，仅安装无需打开登录，充值百分百成功，大额无忧！安装可返回继续支付'
    },
    '2':{
        'pgkName': 'web_app',
        'appName': u'web',
        'downloadUrl': 'https://wqs.jd.com/downloadApp/download.html?channel=jdbdad-pinzhuan',
        'title': u'您未安装京东app，仅安装无需打开登录，充值百分百成功，大额无忧！安装可返回继续支付'
    }
}

@app.route('/getPkgs', methods=['POST'])
def getPkgs():
    param = flask.request.get_json()
    ts = str(param.get('ts'))
    return json.dumps(pkgs)

@app.route('/callBackDv', methods=['POST'])
def callBackDv():
    param = flask.request.get_json()
    print('callback dv:', param)
    return "success"

@app.route('/start', methods=['POST'])
def start():
    param_json = flask.request.get_json()
    pkg = param_json['pkgName']
    order_id = param_json['orderId']
    amount = param_json['amount']
    ck = param_json['ck']
    if pkg == 'com.jingdong.app.mall':
        client = jd(ck)
        url, head, body, allow_red = client.get_gen_payid_param(order_id, '22', amount, 'android')
        result = {}
        request_data = {}
        result['next'] = 'jdSecond'
        request_data['type'] = 'POST'
        request_data['url'] = url
        request_data['header'] = head
        request_data['param'] = body
        request_data['media'] = 'application/x-www-form-urlencoded; charset=UTF-8' 
        request_data['allowRed'] = allow_red
        result['requestData'] = request_data
        return json.dumps(result)
    elif pkg == 'com.jd.pingou':
        client = jx(ck)
        url, head, body, allow_red = client.get_wx_apppay_param(order_id)
        result = {}
        request_data = {}
        result['next'] = 'jxFinish'
        request_data['type'] = 'POST'
        request_data['url'] = url
        request_data['header'] = head
        request_data['param'] = body
        request_data['media'] = 'application/x-www-form-urlencoded; charset=UTF-8' 
        request_data['allowRed'] = allow_red
        result['requestData'] = request_data
        return json.dumps(result)
    elif pkg == 'web_app':
        client = jd(ck)
        jmp_url = 'https://wqs.jd.com/order/n_detail_jdm.shtml?deal_id=' + order_id + '&sceneval=2&referer=http://wq.jd.com/wxapp//order/orderlist_jdm.shtml?stamp=1'
        url, head, body, allow_red = client.get_gen_token_param(jmp_url)
        result = {}
        request_data = {}
        result['next'] = 'webFinish'
        request_data['type'] = 'POST'
        request_data['url'] = url
        request_data['header'] = head
        request_data['param'] = body
        request_data['media'] = 'application/x-www-form-urlencoded; charset=UTF-8' 
        request_data['allowRed'] = allow_red
        result['requestData'] = request_data
        return json.dumps(result)

@app.route('/jdSecond', methods=['POST'])
def jdsecond():
    param_json = flask.request.get_json()
    ck = param_json['ck']
    client_res = json.loads(param_json['clientRes'])
    pay_id = client_res['payId']
    client = jd(ck)
    url, head, body, allow_red = client.get_pay_index_param(pay_id, 'android')
    result = {}
    request_data = {}
    result['next'] = 'jdThired'
    request_data['type'] = 'POST'
    request_data['url'] = url
    request_data['header'] = head
    request_data['param'] = body
    request_data['media'] = 'application/x-www-form-urlencoded; charset=UTF-8' 
    request_data['allowRed'] = allow_red
    result['requestData'] = request_data
    return json.dumps(result)

@app.route('/jdThired', methods=['POST'])
def jdthired():
    param_json = flask.request.get_json()
    ck = param_json['ck']
    client_res = json.loads(param_json['clientRes'])
    pay_id = client_res['payId']
    client = jd(ck)
    url, head, body, allow_red = client.get_weixin_pay_param(pay_id, 'android')
    result = {}
    request_data = {}
    result['next'] = 'jdFinish'
    request_data['type'] = 'POST'
    request_data['url'] = url
    request_data['header'] = head
    request_data['param'] = body
    request_data['media'] = 'application/x-www-form-urlencoded; charset=UTF-8' 
    request_data['allowRed'] = allow_red
    result['requestData'] = request_data
    return json.dumps(result)

@app.route('/jdFinish', methods=['POST'])
def jdfinish():
    param_json = flask.request.get_json()
    ck = param_json['ck']
    client_res = json.loads(param_json['clientRes'])
    result = {}
    if client_res['code'] == '0':
        payinfo = {}
        for i in client_res['payInfo']:
            payinfo[str(i).lower()] = client_res['payInfo'][i]
        result['next'] = 'wxsdk'
        result['payInfo'] = payinfo
        result['pkgName'] = 'com.jingdong.app.mall'
        result['appId'] = 'wxe75a2e68877315fb'
        return json.dumps(result)
    else:
        result['next'] = 'error'
        return json.dumps(result)


@app.route('/jxFinish', methods=['POST'])
def jxFinish():
    param_json = flask.request.get_json()
    ck = param_json['ck']
    client_res = json.loads(param_json['clientRes'])
    result = {}
    if client_res['errno'] == 0:
        payinfo = {}
        for i in client_res['data']:
            payinfo[str(i).lower()] = client_res['data'][i]
        result['next'] = 'wxsdk'
        result['payInfo'] = payinfo
        result['pkgName'] = 'com.jd.pingou'
        result['appId'] = 'wx2c49e82e87e57ff0'
        return json.dumps(result)
    else:
        result['next'] = 'error'
        return json.dumps(result)

@app.route('/getOrderInfo', methods=['POST'])
def getOrderInfo():
    param_json = flask.request.get_json()
    pkg = param_json['pkgName']
    # ck = param_json['']
    # request orderinfo
    ck = '{"com.jd.pingou": "pin=jd_4d9b500034155;wskey=AAJi09vPAEBpBvdBVKV6dcOtBbeYH_UibdSKX1xd8Y5Mer0xmCiGb6VN1G5y6NuJ7xS-3zXR7czyZ6OxvQJhz0EklZKDPiBU;", "com.jingdong.app.mall": "pin=jd_4d9b500034155;wskey=AAJiussbAEC7VxcofMvhtWrHU-Bu8OBYzUVl2RKHGCfuq3ShtZiK9OLp7N3AobVN3owJNOr0oDkUuLl8-pPBf1PdcmTytHjY;", "web_app": "pin=jd_4d9b500034155;wskey=AAJiussbAEC7VxcofMvhtWrHU-Bu8OBYzUVl2RKHGCfuq3ShtZiK9OLp7N3AobVN3owJNOr0oDkUuLl8-pPBf1PdcmTytHjY;"}'
    result = {}
    result['orderId'] = '249751389965'
    result['amount'] = '1000'
    ck_json = json.loads(ck)
    result['ck'] = ck_json[pkg]
    print(json.dumps(result))
    return json.dumps(result)

@app.route('/webFinish', methods=['POST'])
def webFinish():
    param_json = flask.request.get_json()
    ck = param_json['ck']
    client_res = json.loads(param_json['clientRes'])
    result = {}
    if 'tokenKey' in param_json['clientRes']:
        payinfo = {}
        token = client_res['tokenKey']
        result['next'] = 'redict'
        pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
        # pay_url = 'weixin://wap/pay?prepayid%3Dwx171809138880790eb76109616265570000&package=3517728757&noncestr=1658052554&sign=457af7bdd02c00c27c091822c06892bd'
        result['url'] = pay_url
        result['pkgName'] = 'web_app'
        return json.dumps(result)
    else:
        result['next'] = 'error'
        return json.dumps(result)



if __name__ == '__main__':
    # threading.Thread(target=query_task).start()
    # app.debug = False
    app.debug = True
    app.run(host='0.0.0.0', port=23938)

