import re
import threading
from time import sleep, time
import requests
import json
import random
import base64
from urllib.parse import urlencode
# import threading
from concurrent.futures import TimeoutError
from time import *    
import os
# import psutil
import datetime
from pebble import ProcessPool


token = "23f6ecdb93e24f2445395169d53e11c5"
expirat_ts = 1698725942
ua_iphonex = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
base_url = "http://api.vmlogin.com/v1"
local_base_url = "http://127.0.0.1:23947/api/v1"


def get_ip():
    url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=&username=chukou01&spec=1'
    # url = 'http://tiqu.pyhttp.taolop.com/getip?count=1&neek=14769&type=1&yys=0&port=1&sb=&mr=1&sep=1&username=chukou01&spec=1'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
        ip = response.text.split(':')[0]
        port = response.text.split(':')[1]
        port = port.replace('\n', '')
        port = port.replace('\r', '')
        return ip, port
        # return '218.86.18.17', '12345'

def test_proxy(ip, port, times=2):
    proxy = {
          'http': 'http://' + ip + ':' + port,
        }
    for i in range(times):
        try:
            re = requests.get('http://www.baidu.com', proxies=proxy, timeout=5)
            # print(re.text)
            print('代理:' + ip + '可用')
            return True
        except:
            pass
        i += 1
    print('代理:' + ip + '不可用')
    return False

def create_order_result(pay_data):
    url = 'http://1.12.255.177:9555/api/pay/createOrderResult'
    head = {"Content-Type": "application/json"}
    resopnse = requests.post(url=url, headers=head, data=pay_data)
    if resopnse.status_code == 200:
        print(resopnse.text)
    return False

def query_order_result(order_no, card_id, card_key):
    url = 'http://1.12.255.177:9555/api/pay/queryOrderResult'
    param = {
        'jdOrderId': order_no,
        'kmiId': card_id,
        'kmiKey': card_key
    }
    print(param)
    head = {"Content-Type": "application/json"}
    resopnse = requests.post(url=url, headers=head, data=json.dumps(param))
    if resopnse.status_code == 200:
        print(resopnse.text)
        if 'success' in resopnse.text:
            return True        
    return False

def quert_order(profile_id, order_no):
    print('查单', profile_id, order_no)
    try:
        pass
        query_common_order(profile_id, order_no)
    except Exception as error:
        print('查单错误', profile_id, " %s" % error)


def create_task(pool):
    print('启动创建订单线程')
    url = 'http://123.1.194.131:9555/api/pay/createdRequestTask'
    head = {"Content-Type": "application/json"}
    # with ProcessPool(max_workers=30, max_tasks=20) as create_pool:
    pool.__enter__()
    while True:
        response = requests.get(url, headers=head)
        if response.status_code == 200:
            print(response.text)
            task_json = json.loads(response.text)
            print(task_json)
            # s = '''{"createOrderTask":[{"amount":10,"goodUrl":"https://item.m.jd.com/product/10022039398507.html","profileId":"1241F6FB-839F-44C1-BBC5-70B7FB48E93D","phoneNum":"pin=%E5%B5%87%E5%AF%92%E5%AE%81svU71"}],"queryOrderTask":[]}'''
            # task_json = json.loads(s)
            # 服务器返回错误数据
            if 'flag' in task_json:
                sleep(10)
                continue
            for create_task in task_json['createOrderTask']:
                phone = create_task['phoneNum']
                good_url = create_task['goodUrl']
                profile_id = create_task['profileId']
                amount = create_task['amount']
                future = pool.schedule(creaet_order_test, args=[phone, profile_id, amount, good_url, 'appstore'], timeout=out_time)
                sleep(0.5)
        sleep(10)

def query_task():
    print('启动查询订单线程')
    url = 'http://123.1.194.131:9555/api/pay/selectRequestTask'
    head = {"Content-Type": "application/json"}
    with ProcessPool(max_workers=30, max_tasks=20) as query_pool:
        while True:
            response = requests.get(url, headers=head)
            if response.status_code == 200:
                task_json = json.loads(response.text)
                print(task_json)
                # s = '''{"createOrderTask":[{"amount":10,"goodUrl":"https://item.m.jd.com/product/10022039398507.html","profileId":"1241F6FB-839F-44C1-BBC5-70B7FB48E93D","phoneNum":"pin=%E5%B5%87%E5%AF%92%E5%AE%81svU71"}],"queryOrderTask":[]}'''
                # task_json = json.loads(s)
                # 服务器返回错误数据
                if 'flag' in task_json:
                    sleep(10)
                for query_task in task_json['queryOrderTask']:
                    profile_id = query_task['profileId']
                    order_no = query_task['jdOrderId']
                    # future = pool.schedule(query_common_order, args=[profile_id, order_no], timeout=20)
                    future = query_pool.schedule(query_appstore_order, args=[profile_id, order_no], timeout=out_time)
                    sleep(0.5)
            sleep(5)

out_time = 60
if __name__ == '__main__':
    create_url = 'http://123.1.194.131:9555/api/pay/createdRequestTask'
    query_url = 'http://123.1.194.131:9555/api/pay/selectRequestTask'
    head = {"Content-Type": "application/json"}
    # 创建线程监控浏览器进程超时情况
    threading.Thread(target=kill_process_timeout, args=(name_list, out_time)).start()
    with ProcessPool(max_workers=30, max_tasks=20) as pool:
        while True:
            # 查单任务
            query_response = requests.get(query_url, headers=head)
            if query_response.status_code == 200:
                querytask_json = json.loads(query_response.text)
                # 服务器返回错误数据
                if 'flag' in querytask_json:
                    sleep(3)
                    continue
                for query_task in querytask_json['queryOrderTask']:
                    profile_id = query_task['profileId']
                    order_no = query_task['jdOrderId']
                    future = pool.schedule(query_appstore_order, args=[profile_id, order_no], timeout=out_time)
                    sleep(0.5)
            # 下单任务
            create_response = requests.get(create_url, headers=head)
            if create_response.status_code == 200:
                createtask_json = json.loads(create_response.text)
                # 服务器返回错误数据
                if 'flag' in createtask_json:
                    sleep(3)
                    continue
                for create_task in createtask_json['createOrderTask']:
                    phone = create_task['phoneNum']
                    good_url = create_task['goodUrl']
                    profile_id = create_task['profileId']
                    amount = create_task['amount']
                    future = pool.schedule(creaet_order_test, args=[phone, profile_id, amount, good_url, 'appstore'], timeout=out_time)
                    sleep(0.5)
            sleep(30)


# 
    # profile_id = '372438B2-8910-44A5-A2CD-4B04871346D2'
    # goodUrl = 'https://item.m.jd.com/product/10022039398507.html'
    # # creaet_order_test('13333333333', profile_id, '10', goodUrl, 'appstore')
    # query_appstore_order(profile_id, '232909165251')

# create_pool = ProcessPool(max_workers=30, max_tasks=20)


# if __name__ == '__main__':
# 
    # threading.Thread(target=kill_process_timeout, args=(name_list, out_time)).start()
    # with ProcessPool(max_workers=30, max_tasks=20) as pool:
    # 创建线程监控浏览器进程超时情况
        # 创建线程处理下单任务
        # threading.Thread(target=create_task, args=(pool,)).start()
    # 创建线程处理查单任务
    # threading.Thread(target=query_task).start()
