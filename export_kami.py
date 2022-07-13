from re import I
from time import sleep
from flask import send_file
import json
import requests

# f_yifasong = open('/home/police/project/pay_data/appstore/0702')

token = 'r99ch0qas1h2mv60gvviga6eng'


def get_send():
    f_kami = open('/home/police/project/pay_data/appstore/0702/total_28_72')
    kami_list = []
    for line in f_kami.readlines():
        line = line.replace('\n', '')
        # print(line)
        if ':' not in line:
            continue
        kami = {}
        kami['amount'] = line.split(' ')[0]
        kami['card_name'] = line.split(' ')[1]
        kami['card_password'] = line.split(' ')[2]
        kami['add_time'] = line.split(' ')[3] + ' ' +line.split(' ')[4] 
        kami_list.append(json.dumps(kami))       
    return kami_list

def get_kami(size):
    kami_list = []
    url = 'http://175.178.195.147:9191/admin/cammy/index?page=1&limit=' + str(size)
    head = {
        'Cookie': 'PHPSESSID=' + token,
        'Referer':'http://175.178.195.147:9191/admin/cammy/index?mpi=m-p-i-1',
        'X-Requested-With':'XMLHttpRequest'
    }
    res = requests.get(url, headers=head)
    print(res.text)
    total = 0
    for i in res.json()['data']:
        try:
            # if True:
            if not (i['id'] >= 12061 and i['id'] <= 12075):
                kami = {}
                kami['amount'] = str(i['amount']) 
                kami['card_name'] = i['card_name']
                kami['card_password'] = i['card_password']
                kami['add_time'] = i['add_time']
                kami['id'] = i['id']
                kami_list.append(json.dumps(kami))
            total += int(i['amount'])
        except:
            print(i)   
    return total, kami_list


def compare(send_list, total_list):
    f = open('kami100.txt', 'w')
    total = 0
    num = 0
    for i in total_list:
        is_send = False
        for n in send_list:
            if i == n:
                is_send = True
                break
        if is_send == False:
            kami = json.loads(i)
            if 'QB_'in kami['card_name']:
                continue
            print(kami)
            if int(kami['amount']) == 200:
            # if True:
                f.write(kami['amount'] + ' ' + kami['card_name'] + ' ' + kami['card_password'] + ' ' + kami['add_time'] + '\n')
                total += int(kami['amount'])
                num += 1
                # print(kami)
                # print(total)
    print(total)
    print(num)
    sleep(1)

if __name__ == '__main__':
    total, kami_list = get_kami(2000)
    send_list = get_send()
    print(len(send_list))
    compare(send_list, kami_list)