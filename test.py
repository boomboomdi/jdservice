import requests
import json
import base64,requests
from rsa import decrypt
from tools import yanzhengma
import requests
import time
import sys
import time
import hashlib
import base64
import sqlite3
import binascii
from pyDes import des, CBC, PAD_PKCS5, ECB

# 流量订单使用

STATUS_TRUE = '1'
STATUS_FALSE = '0'

class Base64(object):
    stopwatch = [
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'U', 'V',
        'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'e', 'f', 'g', 'h',
        'i', 'j', 'k', 'l', 'm', 'n', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '/'
    ]
    @staticmethod
    def encode(text):
        b_arr = [x for x in bytearray(text, 'utf-8')]
        sb = ''
        for i in range(0, len(b_arr), 3):
            b_arr2 = [0] * 4
            b = 0
            for i2 in range(0, 3):
                i3 = i + i2
                if i3 <= len(b_arr) - 1:
                    b_arr2[i2] = (b | ((b_arr[i3] & 255) >> ((i2 * 2) + 2)))
                    b = ((((b_arr[i3] & 255) << (((2 - i2) * 2) + 2)) & 255) >> 2)
                else:
                    b_arr2[i2] = b
                    b = 64
            b_arr2[3] = b
            for i4 in range(0, 4):
                if b_arr2[i4] <= 63:
                    sb += Base64.stopwatch[b_arr2[i4]]
                else:
                    sb += '='
        return sb

    @staticmethod
    def deocde(text):
        pass

user = 'jd_4d9b500034155'
# print(Base64.encode(user))
# def update_ck(ck):
    # url = 'http://175.178.150.157:9666/api/get/getPhone'
def callback(order_id):
    # LOG('callback:' + str(order_id))
    # url = 'http://175.178.150.157:9666/api/pay/callBack?offOrderNo=' + str(order_id)
    url = 'http://1270.0.0.1:9666/api/pay/callBack?offOrderNo=' + str(order_id)
    head = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    print(url)
    res = requests.get(url, headers=head)

def login(user='18332556879', passwd='18332556879'):
    base_url = 'https://jdcardsys.whkv.net'
    first_page = requests.get(base_url + '/user/login/index.html').text
    img_code_url = None
    for line in first_page.split('\n'):
        if 'new_captcha.html' in line:
            for i in line.split('\"'):
                if 'new_captcha' in i:
                    img_code_url = i.replace('this.src=\'', '').replace('&time=\'+Math.random();', '')
    if img_code_url == None:
        return None
    code = yanzhengma(base_url + img_code_url)
    print(code)
    if code == None:
        return None
    login_url = 'https://jdcardsys.whkv.net/user/login/doLogin.html'
    login_header = {
        'referer': 'https://jdcardsys.whkv.net/user/login/index.html',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest'
    }
    login_param = 'username=' + user + '&password=' + passwd + '&captcha=' + code + '&_captcha_id='
    login_res = requests.post(login_url, headers=login_header, data=login_param)
    print(login_res.text)

def get_liuguan_proxy(pid, cid):
    orderId = "O22030913492661582939"
    secret = "10b80d0144644c049da1bd912077cdd5"
    pwd = 'testLiuguan1'
    ts = str(int(time.time()))
    txt = "orderId=" + orderId + "&" + "secret=" + secret + "&" + "time=" + ts
    sign = hashlib.md5(txt.encode()).hexdigest()                 # 计算sign   user = "proxy"
    url = 'http://api.hailiangip.com:8422/api/getIp?type=1&num=1&pid=' + pid + '&unbindTime=60&cid=' + cid + '&orderId=' + \
        orderId + '&time=' + ts + '&sign=' + sign + '&noDuplicate=1&dataType=1&lineSeparator=0&singleIp='
# 
    # password = password + "pwd=" + passwd + "&pid=" + pid + "&cid=" + cid + "&uid=" + ts  
# 
    res = requests.get(url)
    if res.status_code == 200:
        print(res.text)
        if '无可用IP' in res.text:
            return None
        return res.text

    # username = orderId
    # password = password + "pwd=" + pwd + "&pid=" + pid + "&cid=" + cid + "&uid=" + ts + "&sip=" + '0'
    # proxyUrl = "http://" + username + ":" + password + "@" + host + ":" + httpPort
    # proxy = {"http": proxyUrl, "https": proxyUrl}
    # r = requests.get('https://www.ip138.com', proxies = proxy)
    # print("status Code : " + str(r.status_code))

def get_zhima_proxy(pro='', city='0'):
    url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=' + pro + '&city=' + city + '&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='    
    res = requests.get(url)
    return res.text.strip()

def ip2address(ip):
    token = '71d3346f13ec3cc6d6ff468e77055ce0'
    url = 'https://api.ip138.com/ip/?ip=' + ip + '&datatype=jsonp&token=' + token
    res = requests.get(url)
    if res.status_code == 200:
        ret_json = json.loads(res.text)
        if ret_json['ret'] == 'ok':
            return ret_json['data'][1], ret_json['data'][2]
    print(res.text)

def query_near_city(city_name):
    if '自治州' in city_name or '区' in city_name or '自治县' in city_name:
        # get pro ip
        pass
    sample_name = city_name.split('市')[0]
    conn = sqlite3.connect('/home/police/project/python/jd/jd.db') 
    c = conn.cursor()
    cursor = c.execute('SELECT * FROM "bsa_citys" WHERE city_name LIKE \'' + city_name + '\'')
    for row in cursor:
        print(row)

def update_zhima_by_city(city_name, status):
    if '市' not in city_name:
        city_name = city_name + '市'
    conn = sqlite3.connect('/home/police/project/python/jd/jd.db') 
    try:
        sql = 'UPDATE "bsa_zhima" SET status = ' + status + ' WHERE city = \'' + city_name + '\''
        print(sql)
        conn.execute(sql)
    except:
        print('=== update_zhima_status error ===')
    finally:
        conn.commit()
        conn.close()


def check_citys():
    try:
        c = conn.cursor()
        cursor = c.execute('SELECT id FROM "bsa_zhima"')
        for row in cursor:
            print(row[0])
            update_zhima__by_id(row[0], STATUS_TRUE)
    except:
        print('=== check_citys error ===')

def check_zhima(city_code):
    url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=' + city_code + '&yys=0&port=1&time=1' + \
        '&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=&username=chukou01&spec=1'
    res = requests.get(url)
    if res.status_code == 200:
        if 'msg' in res.text:
            pass


def update_zhima__by_id(id, status):
    try:
        sql = 'UPDATE "bsa_zhima" SET status = ' + status + ' WHERE id = \'' + id + '\''
        conn.execute(sql)
    except:
        print('=== update_zhima_status error ===')
    finally:
        conn.commit()
    pass

CALLBACK_IP = 'http://175.178.241.238:9999'
def update_ck_status(account, code):
    print('======== update_ck_status =========')
    url = CALLBACK_IP + '/api/get/updateAccountState?account=' + str(account) + '&state=' + str(code)
    head = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    print(url)
    res = requests.get(url, headers=head)
    print(res.text)


def des_descrypt(s, key):
    """
    DES 解密
    :param s: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    secret_key = key 
    iv = secret_key
    des_obj = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    # decrypt_str = des_obj.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    decrypt_str = des_obj.decrypt(s, padmode=PAD_PKCS5)
    return decrypt_str

def des_decrypt(data,secretkey):
    des_obj = des(secretkey, ECB, secretkey, padmode=PAD_PKCS5)
    decodebs64data = base64.b64decode(data)
    return des_obj.decrypt(decodebs64data).decode('utf-8')


# conn = sqlite3.connect('/home/police/project/python/jd/jd.db') 
if __name__ == '__main__':
    a = {
        'modile': '13283544122'
    }
    # s = Base64.encode(json.dumps(a))
    # print(s)
    # s = base64.b64decode('yXHAF5mz3YNu7tCyIBXSWQ==')
    data = 'BsBfLCzOTlBGoq5gIBRaumf56aJxrurFoDkYKoywLcgJIyRuRlJdmTwqqJ14MAkuJBVWoUctCi8Fq+4pXGi34VxQ2VF287irFgf1hfDcjLBlqx3jlqZ+ppGA/LSZ8fD89OtWnpDhel352bQn77KOQk2ysxtQjCRPIfYA0F9SCU943Vf5H9StfleUMylDQ6Fe'
    key = '2E1ZMAF8'
    # card = des_descrypt(base64.b64decode(data), key)
    print()