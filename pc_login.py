#-*- coding = utf-8 -*-
#Time : 2021/2/9 
#Author : 小柠檬
#File : 京东扫码登录.py
import requests
from PIL import Image
import time
import re

def timer():
    #输出时间
    t = time.strftime('%H:%M:%S')
    return t

def loginQrCode():
    #获取登录二维码
    url = 'https://qr.m.jd.com/show?appid=133&size=147'

    try:
        qrCode = requests.get(url)
        cookies = qrCode.headers.get('Set-cookie')
        return qrCode.content,cookies

    except Exception as e:
        print(e)

def monitor(cookies,token):
    #判断二维码状态
    url = 'https://qr.m.jd.com/check?callback=jQuery1058594&appid=133&token={}'.format(token)
    headers = {'Referer':'https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F%3Fcu%3Dtrue%26utm_source%3Dsogou-pinzhuan%26utm_medium%3Dcpc%26utm_campaign%3Dt_288551095_sogoupinzhuan%26utm_term%3D72c3e74a359c48598c6fabe6c1169112_0_8ac09db8ee5c42d19c8bd8e15bd92ac5',
               'Cookie':cookies}

    while True:
        try:
            r = requests.get(url, headers=headers)

            if 'ticket' in r.text:
                regex = re.compile(r'"ticket" : "(.*?)"')
                ticket = re.findall(regex,r.text)[0]
                return ticket

            elif '二维码未扫描，请扫描二维码' in r.text:
                print('[{}]'.format(timer()),'二维码未扫描，请扫描二维码')

            elif '二维码过期，请重新扫描' in r.text:
                print('[{}]'.format(timer()),'二维码过期，请重新扫描')

            elif '请手机客户端确认登录' in r.text:
                print('[{}]'.format(timer()),'请手机客户端确认登录')

            else:
                print('[{}]'.format(timer()),r.text)

            time.sleep(3)

        except Exception as e:
            print(e)

def getCookie(ticket,wlfstk):
    #获取cookies
    url = 'https://passport.jd.com/uc/qrCodeTicketValidation?t={}'.format(ticket)
    headers = {'Referer':'https://passport.jd.com/uc/login?ltype=logout'}
    cookies = {'Cookie':wlfstk}

    try:
        r = requests.get(url, headers=headers, cookies=cookies)
        cookies = requests.utils.dict_from_cookiejar(r.cookies)

        if cookies:
            print('[{}]'.format(timer()), '登录成功')
            return cookies

        else:
            print('[{}]'.format(timer()), '登录失败')

    except Exception as e:
        print(e)

def main():
    #主函数
    qrCode,cookies = loginQrCode()

    with open(r'C:\Users\Administrator\Desktop\JD.png','wb') as f:
        f.write(qrCode)

    image = Image.open(r'C:\Users\Administrator\Desktop\JD.png')
    image = image.resize((300,300))
    image.show()

    token = cookies.split(';')[1].split(',')[1].split('=')[1]
    QRCodeKey = cookies.split(';')[0]
    wlfstk = cookies.split(';')[1].split(',')[1]
    cookies = QRCodeKey + ';' + wlfstk
    ticket = monitor(cookies,token)
    cookies = getCookie(ticket,wlfstk)  #获取到的cookies

    #将要实现的功能
    test(cookies)

def test(cookies):
    url = 'https://api.m.jd.com/client.action?functionId=lotteryForTurntableFarm&body=%7B%22type%22%3A1%2C%22version%22%3A4%2C%22channel%22%3A1%7D&appid=wh5'
    r = requests.get(url,cookies=cookies)
    print(r.text)

if __name__ == '__main__':
    main()
