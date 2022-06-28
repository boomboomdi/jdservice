import json
import threading
from gevent import sleep
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
from urllib.parse import quote
from jingdong import jd

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




def upload_callback_result(result):
    url = 'http://175.178.195.147:9191/api/ordernotify/notifyorderstatus0069'
    print(url)
    head = {
        'content-type': 'application/json'
    }
    print(result)
    res = requests.post(url, headers=head, data=result).json()
    print(res)
    if res['code'] == 0:
        return True
    else:
        return False

from pc_jd import just_del

def test():
    url = 'http://175.178.241.238/pay/#/wxsrc?order_id=P202206230035577530755&amount=100.00&apiUrl=http%3A%2F%2F175.178.195.147%3A9191%2Fapi%2Forderinfo%2Fgetorderinfo%5C'
    head = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36'
    }
    res = requests.get(url, headers=head)
    print(res.text)

def test_img():
    url = 'http://175.178.241.238/pay/img/wxtitle.9820b9b8.png'
    head = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36'
    }
    res = requests.get(url, headers=head)
    print(res.text)



def test_order():
    url = 'http://175.178.195.147:9191/api/orderinfo/getorderinfo/'
    head = {
        'Content-Type': 'application/json;charset=UTF-8'
    }
    data = '{"order_no":"P202206230035577530755","os":"android"}'
    res = requests.post(url, headers=head, data=data)
    print(res.text)

# conn = sqlite3.connect('/home/police/project/python/jd/jd.db') 
from tools import getip_uncheck
if __name__ == '__main__':
    a = {
        'modile': '13283544122'
    }
    # s = Base64.encode(json.dumps(a))
    # print(s)
    # s = base64.b64decode('yXHAF5mz3YNu7tCyIBXSWQ==')
    # data = 'BsBfLCzOTlBGoq5gIBRaumf56aJxrurFoDkYKoywLcgJIyRuRlJdmTwqqJ14MAkuJBVWoUctCi8Fq+4pXGi34VxQ2VF287irFgf1hfDcjLBlqx3jlqZ+ppGA/LSZ8fD89OtWnpDhel352bQn77KOQk2ysxtQjCRPIfYA0F9SCU943Vf5H9StfleUMylDQ6Fe'
    # key = '2E1ZMAF8'
    # card = des_descrypt(base64.b64decode(data), key)
    # print(str(int(time.time())))
    # result = {
        # 'check_status': '1',
        # 'pay_status': '1',
        # 'ck_status': '1',
        # 'time': str(int(time.time())),
        # 'order_me': '439bca0a80710784f2d2a6ebaae29811',
        # 'order_pay': '248981043887',
        # 'amount': '10.00',
        # 'card_name': '',
        # 'card_password': ''
    # }
    # upload_callback_result(json.dumps(result))

    # test()
    # test_order()
    # for i in range(100):
        # threading.Thread(target=test_img)
        # sleep(0.5)
        

# 
    # f = open('/home/police/project/pay_data/t')
    # for line in f.readlines():
        # line = line.replace('\n', '')
        # t = line.split('&')[0] + '&' + quote(line.split('&')[1])
        # print(t)
        # try:
            # just_del(line)
        # except Exception as e:
            # print(e)
            # continue
    # url = 'http://175.178.195.147:9191/admin/cammy/index?page=1&limit=446'
    # head = {
    #     'Cookie': 'PHPSESSID=3h079gujknvr3iql69np5tjqu1',
    #     'Referer':'http://175.178.195.147:9191/admin/cammy/index?mpi=m-p-i-1',
    #     'X-Requested-With':'XMLHttpRequest'
    # }
    # res = requests.get(url, headers=head)
    # total = 0
    # for i in res.json()['data']:
    #     if i['amount'] == 200:
    #         print(i['amount'], i['card_name'], i['card_password'])
    #     total += int(i['amount'])
    # print(total)

    ck = 'pin=jd_CltrcYCAUeQM; wskey=AAJits-hAECnLlYa49U8uDyLjSmx9_00AE7hMR-xkIhN3MS6qLJNXjB3bAfJvLNZHEb18vZVCHx5bqPIMJNBsSPuCZCmc3km;'
    ck = 'pin=jd_NzjJNSQfaUdD;wskey=AAJhnw5-AEDNcqCp8obD7wUBWKanbgUaJXjqiw9TfItKN5yFtfjipa0py5m9sc8JtsVgXNDJdQfm6TR8eES5GuNBGqkWp4nD'
    ck = 'pin=jd_AzNriYibHqye; wskey=AAJiOFfrAEBpHas-0yK7UHkFqcmFk2WzlWgGZUrmJhrsrIdLBXcYlvc-J035mwa8VwuXC6An7lmFReCHvtVmmcSj0_12VxQV;'
    ck = 'pin=jd_qf9WGE9cGKXR; wskey=AAJiOFgSAECC8IvhpEHdlOW5rmGG879M2HE69X50fhZlxFDZDam67zCmJOnRemZ3lxZPiLflWrFrb5solZxnNy5sDHUTY2uI;'
    ck = 'pin=jd_n1R056zplaIPySs;wskey=AAJiuQCtAFAnrRLuQfVqWFH-oRdYdSjmym-yo4Le2g-hfhibR1ZZJx2D28NwCrNb0eQS1OrU7UxmkBymvf-PlwF9ldmTurmNy-o_eeZvsscbF_1sfTG2CA;'
    ck = 'pin=jd_zzKhEoX7BghTC3O;wskey=AAJiuQEgAFCk2MkyFzHngZ_NxOux4NRyaOjcu4iJGpMZXX7bUmhzZNQiANhgDohO0TlraCF8wxG4_Oly-ycNQw7wOvEHBBmpS8KP0xFhaK5vwjGLZYZjXg;'
    ck = 'pin=jd_4VQCTwcjvi3M5CC;wskey=AAJiuQGIAFAIvY617XZem0YoCYO2ORWaWP54HPLRxEYd9s8pgQrNIuuWp_qu6MoreVYzHkl6spj5t2N-KCSWK0p9Oqm8JGYkyn3qV-wGhUi60LqCDw9nRg;'
    ck = 'TrackID=1tewj3MOVwdCFuslu5WQ2wQ0FBwtdGoMpk5A_41sOu5UqYhG-BHlH39YObd6poV2rI4h3qdelR_EHLFWNe_P9zUHwNq91OUrOLLMxECxg8Uw; thor=D046550577BB0131576C22649B502BE2EFE3D6EFE27FFF58806C6D506EDA349D10041F11326E2CFC7931894EC6D8413B1E748F104F809C8BA789801D6BA296AC246FC3062A56FFE3707859D1A496A5FFD53F029549929385231269D4E5D4E846BEA7C4B1296CFAE30E550E276DB293D619088ADF254A0ED66740D1BAB1EB1A84CE2832D553D44F13CB0FF76D98335965AB269F0D220262698353B9D79E9F3EE6; pinId=zPa3uRlxethAvhgsmmAGUOjur-jFCHph; pin=jd_9cfB1U73ElvRFmp; unick=jd_9cfB1U73ElvRFmp; _tp=V1iADZHLxTprAJT%2F6rf3KlGr%2BQqb%2Beug941iNkagld8%3D; _pst=jd_9cfB1U73ElvRFmp; upn=4cFy4Mhb44xC4sVN4X3Y4chB; pin=jd_9cfB1U73ElvRFmp; wskey=AAJiC797AFDmNazEksmnI5Nq7NtPdSGGW0Qska3yOhUoydJt_osmDJhE6LeTYJhCF_SRNf5Reexy-7Q1MKWcKEVH02SmqiJVdDZ83vwQ0hu9G81eExLU_g;'
    ck = 'pin=jd_b2KhIVxuopzpFQU;wskey=AAJiuqjrAFD8ag6Q18qSyV99ytBRpSAQxChDK9pfIpVHZI6DOX_rC2UEuUmTjHbud5rsGTaSzYnM2VY-0wIEStbIwZauGXWIToCIJgiw7OBz3uiUj-sRIg;whwswswws=yfOZIuT2O2beMto6O9H3XUmq7oqIqEUWRcQo8jf4X_CH5U9YNUXgk58r6QvJ6gx67xsHUHWLiVXU1be6d4eVKM75LaMTdkLCygstgmW8v2JY65q5p2JZpw-8E8SqNnze5;unionwsws={"devicefinger":"eidA1659812345sdKW+MRDYhSeKLnyCcdr2mgSlvjcXYx68sL9Y6ROqrlHY2Y2IljGBDXmZnzArcL\/4Wzx2xqUfMT4bZaKNDbudZ9uuPyV9wkcUd50hU","jmafinger":"yfOZIuT2O2beMto6O9H3XUmq7oqIqEUWRcQo8jf4X_CH5U9YNUXgk58r6QvJ6gx67xsHUHWLiVXU1be6d4eVKM75LaMTdkLCygstgmW8v2JY65q5p2JZpw-8E8SqNnze5"};'

    url = 'https://m.jd.com'
    print(url)
    # url = 'https://pay.m.jd.com/pay/weixin-pay.html?appId=jd_m_pay&payId=cc00f1c3cab14dc8b399aac2d7036c9e&code=091trr0w3xDoKY2JvXZv3NYfVO2trr0m&state=123'
    # url = 'https://pay.jd.com/d/cashier/?orderId=249072861996&reqInfo=eyJjYXRlZ29yeSI6IjEiLCJvcmRlckFtb3VudCI6IjEwMC4wMCIsIm9yZGVyRXJwUGxhdCI6IkpEIiwidmVyc2lvbiI6IjMuMCIsIm9yZGVySWQiOiIyNDkwNzI4NjE5OTYiLCJwYXlBbW91bnQiOiIxMDAuMDAiLCJjb21wYW55SWQiOiI2Iiwib3JkZXJUeXBlIjoiMzciLCJ0b1R5cGUiOiIxMCJ9&sign=285efbe203f1df8f164d48b968ff9c43&appId=pcashier&cashierId=1'
    ip = getip_uncheck('山东省济南市')
    # url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx32e4d3446c02b4b5&redirect_uri=https%3A%2F%2Fpay.m.jd.com%2Fpay%2Fweixin-pay.html%3FappId%3Djd_pc_pay%26payId%3D07656299260746a79060d40fcef7b07c&response_type=code&scope=snsapi_base&state=123#wechat_redirect'
    client = jd(ck, ip)
    status, token = client.gen_token(url)
    pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
    print(pay_url)

