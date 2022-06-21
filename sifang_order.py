from random import randint
import threading
import time
from time import sleep
import hashlib
import requests
import json

def md5(pw):
    md = hashlib.md5()  # 生成md5对像
    md.update(pw.encode('utf-8'))  # 加密，加密密码的时候，必须对密码进行编码，否则会报错
    return md.hexdigest()  # 返回16进制密文

token = '032ebcd09e23b885fd4e568d8095dee2'
token = '14e1b600b1fd579f47433b88e8d85291'
def create_order(amount):
    merchant_sign = 'dv'
    order_no = 'dv' + str(randint(1000000, 99999999))
    payment = 'onlyalipay'
    # payment = 'weixin'
    ts = str(int(time.time()))
    notify_url = 'http://127.0.0.1:23943/callBackDv'
    sign = md5(merchant_sign+ order_no+amount+ ts+token)
    order = {
        'merchant_sign': merchant_sign,
        'order_no': order_no,
        'payment': payment,
        'amount': amount,
        'time': ts,
        'notify_url': notify_url,
        'sign': sign
    }
    head = {
        'session': order_no
    }
    # url = 'http://175.178.195.147:9191/api/orderinfo/order?t=' + str(randint(100000,9999999))
    url = 'http://27.152.28.201:9393/api/orderinfo/order?t=' + str(randint(100000,9999999))
    data = json.dumps(order)
    print(data)
    res = requests.post(url, headers=head, data=data)
    if 'code' in res.text[0:20]:
        print(res.json())
    else:
        print(res.text)


def test():
    for i in range(10000):
        n = randint(1, 3)
        amount = str(n*50)
        t = threading.Thread(target=create_order, args=(amount,))
        t.start()
        i += 1
        sleep(0.08)


if __name__ == '__main__':
    # test()
    create_order('100')