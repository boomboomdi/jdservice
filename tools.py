from imaplib import Time2Internaldate
from os import times
import random
import requests
import base64
import json
# from PIL import Image,ImageEnhance
# import pyzbar
from io import BytesIO
import time
import inspect
from pyDes import des, CBC, PAD_PKCS5, ECB


def random_phone():
    list=['134','135','136','137','138','139','150','151','130','131','132','155','156','185','186','133','153','180','189']
    shou=random.choice(list)
    haoma="0123456789"
    haom=''
    haom1=[]
    for i in range (8):
        haom1.append(random.choice(haoma))
        haom = ''.join(haom1)
    return (shou+haom)


# 1003
def yanzhengma(img_url, code=1003):
    url = "http://www.bingtop.com/ocr/upload/"
    code_img = requests.get(img_url).content
    base64_img = base64.b64encode(bytes(code_img))
    params = {
        "username": 'testYanzhengma',
        "password": 'C8J44EhRKg3sQJr',
        "captchaData": base64_img,
        "captchaType": code 
    }
    res = requests.post(url, data=params)
    if res.status_code == 200:
        # print(res.text)
        ret_json = json.loads(res.text)
        if ret_json['message'] == '':
            return ret_json['data']['recognition']
    return None


def parse_qrcode_online(image_url):
    rq_img = requests.get(image_url).content
    img = Image.open(BytesIO(rq_img))
    txt_list = pyzbar.decode(img)
    for txt in txt_list:
        barcodeData = txt.data.decode("utf-8")
        print(barcodeData)

def parse_qrcode_local(content):
    img = Image.open(BytesIO(content))
    txt_list = pyzbar.decode(img)
    for txt in txt_list:
        barcodeData = txt.data.decode("utf-8")
        print(barcodeData)

def LOG_D(log):
    t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
    print('[+++]' + t, 'function', '[' + inspect.stack()[1][3] + ']' + ':', log)

def LOG_E(log):
    t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
    print('[---]' + t, 'function', '[' + inspect.stack()[1][3] + ']' + ':', log)

def getip_uncheck():
    # url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=0&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=&username=chukou01&spec=1'
    # shanghai
    url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=310000&city=310200&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=&username=chukou01&spec=1'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
        if '请添加白名单' in response.text:
            return None
        ip = response.text
        ip = ip.replace('\n', '')
        ip = ip.replace('\r', '')
        return ip

def get_jd_account(ck):
    for item in ck.split(';'):
        if 'pin=' in item:
            return item.split('=')[1]
    return None

def des_decrypt(data,secretkey):
    des_obj = des(secretkey, ECB, secretkey, padmode=PAD_PKCS5)
    decodebs64data = base64.b64decode(data)
    return des_obj.decrypt(decodebs64data).decode('utf-8')

DES_KEY = '2E1ZMAF8'
def parse_card_info(en_info):
    de_info = des_decrypt(en_info, DES_KEY)
    info_json = json.loads(de_info.replace('[', '').replace(']', ''))
    return info_json['cardNo'], info_json['cardPass']

def time_2_ts(time_str):
    # 先转换为时间数组
    timeArray = time.strptime(time_str, "%Y-%m-%d%H:%M:%S")
    # 转换为时间戳
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def get_ipinfo(ip):
    url = 'https://ip.taobao.com/outGetIpInfo'
    head = {
        'content-type': 'application/x-www-form-urlencoded',
        'referer': 'https://ip.taobao.com/ipSearch',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'
    }
    data = 'ip=' + ip + '&accessKey=alibaba-inc'
    res = requests.post(url=url, headers=head, data=data)
    if res.status_code == 200:
        if 'query success' in res.text:
            return res.json()['data']['region'], res.json()['data']['city']
        return None, None
    return None, None

if __name__ == '__main__':
    # parse_qrcode('https://qr.m.jd.com/show?appid=133&size=147&t=')
    data = 'BsBfLCzOTlBGoq5gIBRaumf56aJxrurFoDkYKoywLcgJIyRuRlJdmTwqqJ14MAkuJBVWoUctCi8Fq+4pXGi34VxQ2VF287irFgf1hfDcjLBlqx3jlqZ+ppGA/LSZ8fD89OtWnpDhel352bQn77KOQk2ysxtQjCRPIfYA0F9SCU943Vf5H9StfleUMylDQ6Fe'
    # print(parse_card_info(data))
    a1 = "2022-05-1023:40:00"
    # print(time_2_ts(a1))
    # pass
    print(get_ipinfo('223.83.132.229'))