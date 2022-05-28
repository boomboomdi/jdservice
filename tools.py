import random
import requests
import base64
import json
from PIL import Image,ImageEnhance
import pyzbar
from io import BytesIO
import time
import inspect


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
    url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=0&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=&username=chukou01&spec=1'
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

if __name__ == '__main__':
    # parse_qrcode('https://qr.m.jd.com/show?appid=133&size=147&t=')
    pass