# -*- coding: utf-8 -*-#
from random import randint
from time import sleep
from urllib.parse import quote
from flask import Flask, session
import flask
import requests
import threading
from tools import LOG_D
from pc_jd import order_appstore, order_knowkedge, order_qb, query_order_appstore, get_real_url, query_order_qb


SUCCESS = 0
CK_UNABLE = 1
NET_ERROR = 2
CODE_ERROR = 3

PHONE = 0
ORDER_NO = 1

qqs = [947705958, 947743456, 952458479, 947570644, 2605711095, 1994816316, 1208559244, 1208620725, 1207350251, 1125689908, 1206655847, 2235241725, 1020353698, 1060648356, 1019166513, 1060697875, 1127855236, 1207295299, 1016856692, 1204321547, 1059805332, 1014971894, 1014663878, 1014700394, 1016757488, 1016923555, 1017906219, 1019504222, 1019572118, 1020276438, 1131496551, 1020350745, 1059922045, 1060034285, 1060041759, 1060875383, 1060517237, 1060566552, 1060612899, 1014517277, 1060747539, 1060755845, 1018560611, 1125294666, 1125380405, 1125424555, 1125457784, 1125874180, 1015069805, 1127054482, 1127245846, 1127443830, 1016011723, 1127609000, 1060039843, 1127659529, 1127794777, 1204248772, 1127875111, 1131010444, 1131384627, 1060068426, 1131547253, 1021072333, 1060875092, 1204168988, 1204285035, 1205306795, 1207342573, 1208705617, 1207618757, 1060271681, 1207403513, 1060189289, 1363151385, 1749425086, 1748362369, 2238862031, 1020134241, 1127376555, 1207631772, 2205561709, 1208927421, 1293871194, 1293879945, 1284073013, 1284072849, 1284072851, 1284072767, 1292913861, 1284073065, 1284073060, 1284073018, 1284072954, 1284073067, 1293685062, 1292778396, 1209399014, 1284072833, 1293522869, 1291948564, 1291806458, 1291516612, 1284072938, 1284073078, 1284072932, 1284073066, 1284072947, 1284072830, 1284072928, 1127440684, 1206636065, 1210749101, 1391552476, 1294497297, 1295244985, 1394330367, 1394843689, 1394493540, 1395339265, 1400508380, 1400553280, 1397582570, 1400366722, 1295281714, 1293889695, 1060247523, 1295407806, 1393402391, 1444345509, 1284072802, 1284072823, 1059863225, 1284072831, 1294429779, 1391565464, 1295438669, 1295576193, 1295805895, 1391098774, 1391994472, 1394323123, 1391212174, 1391935490, 1392059406, 1482502080, 1482542150, 1492589607, 1493345164, 1493691294, 1473645771, 1749949814, 1750078515, 1750263110, 1750326903, 1750506893, 1750582431, 1750962734, 1750987193, 1751325637, 1751361695, 1751688539, 1753226005, 1756107324, 1756636392, 1761709874, 1768331289, 2267147506, 2281798362, 2316693149, 2328978624, 2375199817, 239227256, 2394512197, 994904960, 997279711, 755685909, 2322630974, 2353901021, 1727560100, 761842512, 2359852270, 1295829327, 2283120754, 1502478914, 1494600634, 2275034125, 1296930517, 1410222384, 1285894044, 1105477009, 1151699805, 1405363135, 1023481175, 1021669630, 1021738629, 1063757504, 1064125872, 1064090266, 1063986423]

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
    ck = ck.encode("utf-8").decode("latin1")
    order_me = str(param.get('order_me'))
    amount = str(param.get('amount'))
    threading.Thread(target=order_appstore, args=(ck, order_me, amount)).start()
    return 'success'
    # return '{"code": 0, "msg": "SUCCESS", "data": {"phone": "' + phone + '", "amount": 469.19}, "sign": "488864C0AB51AEA0AF551074446FBCEC"}'

# @app.route('/createOrderAppstore', methods=['POST'])
# def createOrderAppstore():
    # param = flask.request.get_json()
    # ck = str(param.get('cookie'))
    # ck = ck.encode("utf-8").decode("latin1")
    # order_me = str(param.get('order_me'))
    # amount = str(param.get('amount'))
    # print(param)
    # qq = str(qqs[randint(0, 180)])
    # qq = ''
    # threading.Thread(target=order_qb, args=(ck, order_me, amount, qq)).start()
    # return 'success'
    
@app.route('/queryAppstore', methods=['POST'])
def queryAppstore():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    ck = ck.encode("utf-8").decode("latin1")
    order_me = str(param.get('order_me'))
    order_pay = str(param.get('order_pay'))
    amount = str(param.get('amount'))
    print(param)
    print('========')
    threading.Thread(target=query_order_appstore, args=(ck, order_me, order_pay, amount)).start()
    return "success"

# @app.route('/queryAppstore', methods=['POST'])
# def queryAppstore():
    # param = flask.request.get_json()
    # ck = str(param.get('cookie'))
    # ck = ck.encode("utf-8").decode("latin1")
    # order_me = str(param.get('order_me'))
    # order_pay = str(param.get('order_pay'))
    # amount = str(param.get('amount'))
    # print(param)
    # print('========')
    # threading.Thread(target=query_order_qb, args=(ck, order_me, order_pay, amount)).start()
    # return "success"



@app.route('/queryAppstoreImmediate', methods=['POST'])
def queryAppstoreImmediate():
    param = flask.request.get_json()
    ck = str(param.get('cookie'))
    ck = ck.encode("utf-8").decode("latin1")
    order_me = str(param.get('order_me'))
    order_pay = str(param.get('order_pay'))
    amount = str(param.get('amount'))
    print(param)
    print('========')
    return query_order_appstore(ck, order_me, order_pay, amount)
# 
@app.route('/getRealurl', methods=['POST'])
def getRealurl():
    param = flask.request.get_json()
    print('========')
    print(param)
    ck = str(param.get('cookie'))
    ck = ck.encode("utf-8").decode("latin1")
    url = str(param.get('qr_url'))
    os = str(param.get('os'))
    if os == 'android':
        return get_real_url(ck, url, os)
    elif os == 'ios':
        return get_real_url(ck, url, os)

@app.route('/callBackDv', methods=['POST'])
def callBackDv():
    param = flask.request.get_json()
    print('callback dv:', param)
    return "success"


if __name__ == '__main__':
    # threading.Thread(target=query_task).start()
    # app.debug = False
    app.debug = True
    app.run(port=23942)
