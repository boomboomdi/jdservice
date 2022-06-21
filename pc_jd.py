# -*- coding: utf-8 -*-
import base64
import json
import requests
from time import time, sleep
from urllib.parse import quote
import tools
from jingdong import LOG, jd
from ip_sqlite import ip_sql
from jingdong import get_ios_wx
from order_sqlite import order_sql

SUCCESS = 1
WEB_CK_UNVALUE = 2
CK_UNVALUE = 3
CK_PAY_FAIL = 4
NETWOTK_ERROR = 5
RET_CODE_ERROR = 6
CK_NO_ADDRESS = 7
UNLOGIN=8
UNKNOW = 9


class pc_jd():

    def __init__(self, ck, proxy_ip=None) -> None:
        self.ck = ck
        if proxy_ip == None:
            self.proxy = None
        else:
            self.proxy = {
                'http': proxy_ip,
                'https':proxy_ip 
            }

    def get_order_url(self, order_no):
        query_list = '[{"orderType":34,"erpOrderId":"' + order_no + '"}]'
        url = 'https://ordergw.jd.com/orderCenter/app/1.0/?callback=jQuery9550751&queryList=' + quote(query_list) + '&_=' + str(int(time())) + '575'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
        tools.LOG_D(res.text)
        if res.status_code == 200:
            ret = res.text.split('(')[1][0:-1]
            ret_json = json.loads(ret)
            operations = ret_json['appOrderInfoList'][0]['operations']
            for operation in operations:
                if operation['name'] == '付款':
                    return SUCCESS ,'https:' + operation['url']
            return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None


    def get_jmiurl(self, url):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

    def cashier_index(self, cashier_url):
        tools.LOG_D('enter')
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url=cashier_url, headers=head, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

    def get_pay_channel(self, jmi_url):
        params = jmi_url.split('?')[1]
        for param in params.split('&'):
            if 'orderId' in param[0:7]:
                order_id = param.replace('orderId=', '')
            if 'reqInfo' in param[0:7]:
                req_info = param.replace('reqInfo=', '')
            if 'sign' in param[0:4]:
                sign = param.replace('sign=', '')
        url = 'https://pay.jd.com/api-d-cashier/jdpay/getPayChannel?cashierId=1&appId=pcashier'
        data = '{"orderId":"' + order_id + '","reqInfo":"' + req_info + '","sign":"' + sign + '","aksType":"sm","riskReqVo":{"deviceId":"","fingerprint":""}}'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': jmi_url,
            'Origin': 'https://pay.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None, None
        if res.status_code == 200:
            ret = res.text
            if '微信支付' not in ret:
                return CK_UNVALUE, None, None, None
            ret_json = json.loads(ret)
            channel_list = ret_json['platPayInfo']['platPayChannelList']
            for channel in channel_list:
                if channel['channelName'] == '微信支付':
                    channelSign = channel['channelSign']
            return SUCCESS, ret_json['paySign'], ret_json['pageId'], channelSign
        else:
            return RET_CODE_ERROR, None, None, None

    def get_pay_channel_qq(self, jmi_url):
        tools.LOG_D('enter')
        params = jmi_url.split('?')[1]
        for param in params.split('&'):
            if 'orderId' in param[0:7]:
                order_id = param.replace('orderId=', '')
            if 'reqInfo' in param[0:7]:
                req_info = param.replace('reqInfo=', '')
            if 'sign' in param[0:4]:
                sign = param.replace('sign=', '')
        url = 'https://pay.jd.com/api-d-cashier/jdpay/getPayChannel?cashierId=1&appId=pcashier'
        data = '{"orderId":"' + order_id + '","reqInfo":"' + req_info + '","sign":"' + sign + '","aksType":"sm","riskReqVo":{"deviceId":"","fingerprint":""}}'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Origin': 'https://pay.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None, None
        if res.status_code == 200:
            ret = res.text
            if '微信支付' not in ret:
                return CK_UNVALUE, None, None, None
            ret_json = json.loads(ret)
            channel_list = ret_json['platPayInfo']['platPayChannelList']
            for channel in channel_list:
                if channel['channelName'] == '微信支付':
                    channelSign = channel['channelSign']
            return SUCCESS, ret_json['paySign'], ret_json['pageId'], channelSign
        else:
            return RET_CODE_ERROR, None, None, None



    def weixin_confirm(self, order_id, pay_sign, amount, page_id, channel_sign):
        tools.LOG_D('enter')
        url = 'https://pcashier.jd.com/weixin/weixinConfirm?cashierId=1&appId=pcashier'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://pay.jd.com',
            'Origin': 'https://pay.jd.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.ck
        }
        data = '{"orderId":"' + order_id + '","pageId":"' + page_id + '","paySign":"' + pay_sign + '","riskReqVo":{"deviceId":"","fingerprint":""},' + \
            '"payingChannel":{"bankCode":"weixin","channelSign":"' + channel_sign + '","payAmount":"' + amount + '","agencyCode":"617"}}'
        data = 'bankPayRequestStr=' + quote(data)
        try:
            res = requests.post(url, headers=head, data=data, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']


    def get_weixin_img(self, weixin_page_url, order_id, pay_sign):
        tools.LOG_D('enter')
        url = 'https://pcashier.jd.com/weixin/getWeixinImageUrl?cashierId=1&appId=pcashier'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': weixin_page_url,
            'Origin': 'https://pcashier.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        data = '{"orderId":"' + order_id + '","paySign":"' + pay_sign + '","riskReqVo":{"deviceId":"","fingerprint":""}}'
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            if 'weixinImageUrl' in res.text:
                ret_json = json.loads(res.text)
                return SUCCESS, 'https:' + ret_json['weixinImageUrl'].replace('virtualH5CashierImage?qrCodeSign', 'virtualH5Pay?sign')
            else:
                return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None


    def get_payurl(self, weixin_img_url):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://pcashier.jd.com/',
            'Origin': 'https://pcashier.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        img = requests.get(weixin_img_url, headers=head, proxies=self.proxy).content
        pay_url = tools.parse_qrcode_local(img)
        print(pay_url)

    def order_place(self, skuid):
        url = 'https://card.jd.com/order/order_place.action?skuId=' + skuid
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=5)
            # print(res.text)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            # print(res.text)
            for line in res.text.split('\n'):
                if 'orderParam.winId' in line:
                    line = line.replace(' ', '')
                    win_id = line.replace('<inputtype="hidden"id="winId_"name="orderParam.winId"value="', '')   \
                                .replace('"attr="exclu"sync="true"/>', '')
                    return SUCCESS, win_id
            return CK_UNVALUE, None
        return RET_CODE_ERROR, None

    def submit_order(self, skuid, amount, win_id):
        # url = 'https://card.jd.com/json/order_syncSubmitOrder.action'
        url = 'https://card.jd.com/json/order_syncSubmitOrder.action?now=0.7249590835586648'
        print(url)
        data = 'webFeOrderInfo.buyNum=1&webFeOrderInfo.payRuleInfo=&webFeOrderInfo.cardNewVersion=1' + \
            '&webFeOrderInfo.payMode=0&webFeOrderInfo.moneyBasic=0&webFeOrderInfo.integralBasic=0&' + \
            'webFeOrderInfo.payPwd=&webFeOrderInfo.couponIds=&webFeOrderInfo.dongCouponIds=&webFeOrderInfo.amountPayable=' + amount + '.00' + \
            '&webFeOrderInfo.couponsAmount=&webFeOrderInfo.jbeanAmount=&orderParam.useBean=&orderParam.gameAreaSrv=2&webFeOrderInfo.skuId=' + \
            skuid + '&webFeOrderInfo.categoryId=13759&orderParam.winId=' + win_id + '&orderParam.secondSource=0&webFeOrderInfo.eid='
        head = {
            'Host': 'card.jd.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Origin': 'https://card.jd.com',
            'Referer': 'https://card.jd.com/order/order_place.action?skuId=' + skuid,
            'Cookie': self.ck,
            'Content-Length': str(len(data) + 2)
        }
        print(head)

            # skuid + '&webFeOrderInfo.categoryId=13759&orderParam.winId=' + win_id + '&orderParam.secondSource=0'
        # data = 'webFeOrderInfo.buyNum=1&webFeOrderInfo.payRuleInfo=&webFeOrderInfo.cardNewVersion=1&webFeOrderInfo.payMode=0&webFeOrderInfo.moneyBasic=0&webFeOrderInfo.integralBasic=0&webFeOrderInfo.payPwd=&webFeOrderInfo.couponIds=&webFeOrderInfo.dongCouponIds=&webFeOrderInfo.amountPayable=200.00&webFeOrderInfo.couponsAmount=&webFeOrderInfo.jbeanAmount=&orderParam.useBean=&orderParam.gameAreaSrv=2&webFeOrderInfo.skuId=11183368356&webFeOrderInfo.categoryId=13759&orderParam.winId=card_7567142298329571078&orderParam.secondSource=0&webFeOrderInfo.eid='
        print(data)
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            ret_json = res.json()
            tools.LOG_D(res.text)
            if ret_json['code'] == 200:
                url = ret_json['url']
                items = url.split('?')[1].split('&')
                for i in items:
                    if 'orderId' in i:
                        order_no = i.split('=')[1]
                        return SUCCESS, order_no
            elif ret_json['code'] == 31 or '销售火爆' in ret_json['msg']:
                tools.LOG_D(ret_json)
                return CK_UNVALUE, None
            else:
                tools.LOG_D(ret_json)
                return UNKNOW, None
        else:
            return RET_CODE_ERROR, None

    
    def get_order_list(self):
        tools.LOG_D('get_order_list')
        url = 'https://order.jd.com/center/list.action'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None


    def get_order_status(self, order_no):
        query_list = '[{"orderType":34,"erpOrderId":"' + order_no + '"}]'
        url = 'https://ordergw.jd.com/orderCenter/app/1.0/?callback=jQuery7859047&queryList=' + quote(query_list) + '&_=' + str(int(time())) + '049'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None
        ret = res.text.split('(')[1][0:-1]
        ret_json = json.loads(ret)
        print(ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name'])
        if ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name'] == '已完成':
            return SUCCESS, True, ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name']
        else:
            return SUCCESS, False, ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name']


    def get_order_status_qb(self, order_no):
        url = 'https://kami.jd.com/order/detail/' + order_no + '/39'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            html = res.text.replace(' ', '').replace('\n', '').replace('\t', '')
            if '充值成功' in html.split('state-txt')[1][0:20]:
                return SUCCESS, True, '充值成功'
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None
        return SUCCESS, False, '等待付款'

    def get_kami(self, order_no):
        url = 'https://card.jd.com/order/order_detail.action?orderId=' + order_no
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        res = requests.get(url, headers=head, proxies=self.proxy)
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if 'onclick="copyToClipboard(' in line:
                    if '</div>' in line:
                        card_id = line.replace(' ', '').replace('onclick="copyToClipboard(\'', '').replace('\');"></div>', '').replace('\r', '')
                        # print('id', card_id)
                    else:
                        card_key = line.replace(' ', '').replace('onclick="copyToClipboard(\'', '').replace('\');">', '').replace('\r', '')
                        # print('key', card_key)
                if '卡密提取时间' in line:
                    pay_time = line.replace('\r', '').split('时间:')[1]
            if card_id != None and card_key != None:
                return SUCCESS, card_id, card_key, pay_time

    def get_passkey(self, order_no):
        url = 'https://order.jd.com/center/list.action?r=' + str(int(time())) + '784'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }          
        res = requests.get(url, headers=head, proxies=self.proxy)
        print(res.text)
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if '_orderid' in line:
                    if order_no in line:
                        passkey = line.split('_passkey="')[1].replace('"></a>', '')
                        return passkey

    def get_recycle_passkey(self, order_no):
        url = 'https://order.jd.com/center/recycle.action?d=1'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }          
        res = requests.get(url, headers=head, proxies=self.proxy)
        if res.status_code == 200:
            if '忘记密码' in res.text:
                return UNLOGIN, None
            for line in res.text.split('\n'):
                if '_orderid' in line:
                    if order_no in line:
                        passkey = line.split('_passkey="')[1].replace('"></a>', '')
                        return SUCCESS, passkey
        else:
            return RET_CODE_ERROR, None



    def recycle_order(self, order_no, passkey):
        url = 'https://order.jd.com/lazy/recycleOrder.action?orderId=' + order_no + '&PassKey=' + passkey + '&callback=jQuery1715934&_=' + str(int(time())) + '685'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        res = requests.get(url, headers=head, proxies=self.proxy)
        if res.status_code == 200:
            tools.LOG_D(res.text)
            if 'success' in res.text:
                return SUCCESS, True
            else:
                return SUCCESS, False


    def delete_order(self, order_no, passkey):
        url = 'https://order.jd.com/lazy/deleteOrder.action?orderId=' + order_no + '&PassKey=' + passkey + '&callback=jQuery3342349&_=' + str(int(time())) + '149'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        res = requests.get(url, headers=head, proxies=self.proxy)
        if res.status_code == 200:
            tools.LOG_D(res.text)
            if 'success' in res.text:
                return SUCCESS, True
               
    # ==================== qb =====================
    def qb_get_repeatkey(self, skuid):
        url = 'https://kami.jd.com/order/confirm?skuId=' + skuid + '&quantity=1&source=6&appId=22123-6-001&categoryId=22123'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=5)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if 'repeatKey' in line:
                    repeakey = line.replace(' ', '').replace('<inputtype="hidden"name="repeatKey"value="', '').replace('">', '').replace('\r', '')
                    return SUCCESS, repeakey
            return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None

    def qb_get_jmiurl(self, order_no):
        url = 'https://kami.jd.com/order/getJmiUrl/' + order_no + '/39'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
            print(res.headers)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

   
    def qb_submit_order(self, amount, repeatkey, qq):
        url = 'https://kami.jd.com/order/submitOrder?businessType=19&source=6&appCode=109&salePrice=' + amount + \
            '.00&skuPrice=' + amount + '.00&payType=0&orderAmount=' + amount + '.00&onlineAmount=' + amount + \
            '.00&balanceAmount=0&jingdouAmount=0&jingquanAmount=0&dongquanAmount=0&couponIds=&password=&repeatKey=' \
            + repeatkey + '&skuParam.brand=64&skuParam.quantity=1&skuParam.skuId=' + QB_SKUIDS[amount] + \
            '&skuParam.categoryId=22123&features=&rechargeNum=' + qq + '&isCouponBiz=false&stockAvailable=true&eid='
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://kami.jd.com/order/confirm?skuId=' + QB_SKUIDS[amount] + '&quantity=1&source=6&appId=22123-6-001&categoryId=22123',
            'Cookie': self.ck
        }              
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
            print(res.headers)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

    def clear_order(self, order_no):
        tools.LOG_D(order_no)
        passkey = self.get_passkey(order_no)
        code, status = self.recycle_order(order_no, passkey)
        if code != SUCCESS:
            pass
        if status == True:
            code, passkey = self.get_recycle_passkey(order_no)
            if code != SUCCESS:
                pass
            self.delete_order(order_no, passkey)

    def weixin_page(self, url):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, proxies=self.proxy)
            print(res.text)
            print(res.headers)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, False
        if res.status_code == 302:
            # if 'fail' in res.headers['Location']:
                # tools.LOG_D('wxpay can not use')
                # return CK_UNVALUE, False
                return SUCCESS, True
            # else:
                return SUCCESS, True

    def weixin_page_qb(self, url):
        tools.LOG_D('enter')
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://pay.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 302:
                if '/success/fail' in res.headers['Location']:
                    tools.LOG_D(res.headers['Location'])
                    return SUCCESS, False
                else:
                    return SUCCESS, True
            return SUCCESS, True
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, False

    def get_unpay(self):
        url = 'https://order.jd.com/center/list.action?s=1'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/center/list.action?s=1',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
            orders = []
            order = {}
            for line in res.text.split('\n'):
                if 'pay-button-order' in line:
                    print(line)
                    if len(line) < 64:
                        return SUCCESS, orders
                    tmps = line.replace("$ORDER_CONFIG['pay-button-order']='[", '').replace("]';", '').split('},{')
                    for tmp in tmps:
                        for s in tmp.split(','):
                            if 'orderId' in s:
                                order['order_id'] = s.split(':')[1]
                            if 'amount' in s:
                                order['amount'] = s.split(':')[1].replace('.00', '')
                        orders.append(json.dumps(order))
            return SUCCESS, orders
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None


    def get_unpay_appstore(self):
        url = 'https://order.jd.com/center/list.action'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/center/list.action?s=1',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
            orders = []
            order = {}
            for line in res.text.split('\n'):
                if 'pay-button-order' in line:
                    print(line)
                    if len(line) < 64:
                        return SUCCESS, orders
                    tmps = line.replace("$ORDER_CONFIG['pay-button-order']='[", '').replace("]';", '').split('},{')
                    for tmp in tmps:
                        for s in tmp.split(','):
                            if 'orderId' in s:
                                order['order_id'] = s.split(':')[1]
                            if 'amount' in s:
                                order['amount'] = s.split(':')[1].replace('.00', '')

                        for line in res.text.split('\n'):
                            # if ('https://card.jd.com/order/order_detail.action?orderId=' + order['order_id']) in line:
                            if 'order_pay' in line:
                                print(line)
                                # line = line.replace(' ', '')
                                # order_url = line.split('href=\'')[1].split('\'clstag')[0]
                                # order['passkey'] = order_url.split('PassKey=')[1]
                        orders.append(json.dumps(order))
            return SUCCESS, orders
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None


    # def order_center

    def locdetails_order(self, order_id):
        # order_id = '248615578437'
        url = 'https://locdetails.jd.com/pc/locdetail?orderId=' + order_id + '&modelId=2'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/center/list.action?s=1',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy)
            for line in res.text.split('\n'):
                if 'https://pcashier.jd.com/cashier/index.action' in line:
                    return SUCCESS, line.split('"')[1]
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None

    def jump_url(self, order_id):
        url = 'https://kami.jd.com/order/getJmiUrl/' + order_id + '/39'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 302:
                return SUCCESS, res.headers['Location']
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None

    def jump_url_appstore(self, order_id, passkey):
        url = 'https://card.jd.com/order/order_pay.action?orderId=' + order_id + '&PassKey=' + passkey
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            print(res.text)
            if res.status_code == 302:
                return SUCCESS, res.headers['Location']
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None


    def jump_url_knowledge(self, order_id):
        url = 'https://kami.jd.com/order/getJmiUrl/' + order_id + '/39'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 302:
                return SUCCESS, res.headers['Location']
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None

    def test(self):
        tools.LOG_D('enter')

    
    def knowledge_get_repetkey(self, skuid):
        tools.LOG_D('enter')
        url = 'https://v-knowledge.jd.com/order/confirm?skuId=' + skuid + '&quantity=1&source=6'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://cartv.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=5)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if 'repeatKey' in line:
                    repeakey = line.replace(' ', '').replace('<inputtype="hidden"id="repeatKey"name="repeatKey"value="', '').replace('">', '').replace('\r', '')
                    repeakey = repeakey.encode("utf-8").decode("latin1")
                    # repeakey = repeakey.encode("UTF-8").decode("UTF-8")
                    print(repeakey)
                    return SUCCESS, repeakey
            return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None



    def knowledge_submit(self, skuid, repeatKey, price, qq):
        tools.LOG_D('enter')
        url = 'https://v-knowledge.jd.com/order/submitOrder'
        data = 'skuParam.quantity=1&skuParam.skuId=' + skuid + '&businessType=6&source=6&repeatKey=' + repeatKey + \
            '&salePrice=' + price + '.00&payType=0&orderAmount=' + price + '.00&onlineAmount=' + price + '.00&balanceAmount=0' + \
            '&jingdouAmount=0&jingquanAmount=0&dongquanAmount=0&couponIds=&rechargeNum=' + qq + '&password=d41d8cd98f00b204e9800998ecf8427e' + \
            '&features=&skuParam.activityId='
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://v-knowledge.jd.com/order/confirm?skuId=' + skuid + '&quantity=1&source=6',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.ck
        }              
        try:
            res = requests.post(url, headers=head, data=data, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            if 'redirectUrl' in res.text:
                if '销售火爆' in res.text:
                    return CK_UNVALUE, None
                return SUCCESS, res.json()['redirectUrl']
        if res.status_code == 302:
            if 'orderId' in res.headers['Location']:
                return SUCCESS, res.headers['Location']
        return CK_UNVALUE, None


    # def 



amount = '200.00'

APPSTORE_SKUIDS = {
    '10': '10022039398507',
    '50': '11170365589',
    '100': '11183343342',
    '200': '11183368356',
    '500': '11183445154' 
}

QB_SKUIDS = {
    '11': '200145364712',
    '105': '200145365539',
    '210': '200145348880',
    '586': '10048511037815',
    '68': '200153870251',
    '305': '200153773388'
}

DNF_SKUIDS = {
    '50': '200153770492',
    '80': '200153769485',
    # '100': '200153773388'
    '100': '200145201414'
}


def create_order_appstore(ck, order_me, amount, proxy):
    tools.LOG_D('create_order_appstore')
    # ========test=========
    pc_client = pc_jd(ck, proxy)

    # code, order_id, cashier_url = get_useful_unpay_appstore(ck, amount, proxy)
    # if code != SUCCESS:
        # return code, None, None
    # return

    code, win_id = pc_client.order_place(APPSTORE_SKUIDS[amount])
    tools.LOG_D(win_id)
    if code != SUCCESS:
        return code, None, None
    sleep(3)

    code, order_no = pc_client.submit_order(APPSTORE_SKUIDS[amount], amount, win_id)
    tools.LOG_D(order_no)
    if code != SUCCESS:
        return code, None, None
    code, order_url = pc_client.get_order_url(order_no)
    if code != SUCCESS:
        return code, None, None
    code, jmi_url = pc_client.get_jmiurl(order_url)
    if code != SUCCESS:
        return code, None, None
    code, cashier_url = pc_client.cashier_index(jmi_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel(cashier_url)


    for i in range(5):
        code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
        if code != SUCCESS:
            return code, None, None
        tools.LOG_D(weixin_page_url)
        code, status = pc_client.weixin_page_qb(weixin_page_url)
        if code != SUCCESS:
            return code, None, None
        if status == True:
            break
        code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
        sleep(1)
        i += 1

    # if code != SUCCESS:
        # return code, None, None
    # code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    # if code != SUCCESS:
        # return code, None, None
    # tools.LOG_D(weixin_page_url)
    # code, status = pc_client.weixin_page(weixin_page_url)
    # if code != SUCCESS:
        # return code, None, None
    # if status == False:
        # return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url


def order_appstore(ck, order_me, amount):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('account: ' + account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(3):
        code, order_no, img_url = create_order_appstore(ck, order_me, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            if proxy == None:
                return NETWOTK_ERROR
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            order_sql().insert_order(order_no, amount)
            order_sql().update_order_time(order_no)
            break
        elif code == RET_CODE_ERROR:
            return None
        i += 1
    tools.LOG_D(img_url)
    upload_order_result(order_me, order_no, img_url, amount, ck_status)


def get_useful_unpay(ck, amount, proxy):
    tools.LOG_D('enter')
    pc_client = pc_jd(ck, proxy)
    code, orders =  pc_client.get_unpay()
    if code != SUCCESS:
        return code, None, None
    if orders == None:
        return SUCCESS, None, None
    for order in orders:
        order = json.loads(order)
        if amount == str(order['amount']):
            order_id = str(order['order_id'])
            last_time = order_sql().search_order(order_id)
            now_time = str(int(time()))
            if last_time != None:
                # if int(now_time) - int(last_time) > 600:
                if int(now_time) - int(last_time) > 60:
                    code, cashier_url = pc_client.jump_url(order_id)
                    # code, cashier_url = pc_client.locdetails_order(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    return SUCCESS, order_id, cashier_url
    return SUCCESS, None, None

def get_useful_unpay_appstore(ck, amount, proxy):
    tools.LOG_D('enter')
    pc_client = pc_jd(ck, proxy)
    code, orders =  pc_client.get_unpay_appstore()
    if code != SUCCESS:
        return code, None, None
    if orders == None:
        return SUCCESS, None, None
    for order in orders:
        order = json.loads(order)
        if amount == str(order['amount']):
            order_id = str(order['order_id'])
            passkey = str(order['passkey'])
            last_time = order_sql().search_order(order_id)
            now_time = str(int(time()))
            if last_time != None:
                # if int(now_time) - int(last_time) > 600:
                if int(now_time) - int(last_time) > 60:
                    code, cashier_url = pc_client.jump_url_appstore(order_id, passkey)
                    # code, cashier_url = pc_client.locdetails_order(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    return SUCCESS, order_id, cashier_url
    return SUCCESS, None, None



def get_useful_unpay_knowledge(ck, amount, proxy):
    pc_client = pc_jd(ck, proxy)
    code, orders =  pc_client.get_unpay()
    if code != SUCCESS:
        return code, None, None
    if orders == None:
        return SUCCESS, None, None
    for order in orders:
        order = json.loads(order)
        if amount == str(order['amount']):
            order_id = str(order['order_id'])
            last_time = order_sql().search_order(order_id)
            now_time = str(int(time()))
            if last_time != None:
                # if int(now_time) - int(last_time) > 600:
                if int(now_time) - int(last_time) > 100:
                    code, cashier_url = pc_client.jump_url(order_id)
                    # code, cashier_url = pc_client.locdetails_order(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    return SUCCESS, order_id, cashier_url
    return SUCCESS, None, None




def order_qb(ck, order_me, amount, qq):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('account: ' + account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(3):
        code, order_no, img_url = create_order_qb(ck, order_me, amount, qq, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            order_sql().insert_order(order_no, amount)
            order_sql().update_order_time(order_no)
            break
        elif code == RET_CODE_ERROR:
            return None
        i += 1
    tools.LOG_D(img_url)
    order_no = '1234567891'
    img_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=91cdd3c81ca4eb0e567ae1aa974c0edc26ca3884223ba250dbcfa8810261853e2328b54465304f257d4cf742590d02052b86033b07b653b048611091e50a63b4c1b0c4ab88b7e0928f8872365c7dde35'
    upload_order_result(order_me, order_no, img_url, amount, ck_status)


def create_order_dnf(ck, order_me, amoung):

    pass




def test_order_appstore(ck, order_me, amount):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    proxy = tools.getip_uncheck()
    for i in range(3):
        code, order_no, img_url = create_order_appstore(ck, order_me, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            break
        elif code == RET_CODE_ERROR:
            return None
        i += 1
    tools.LOG_D(img_url)
    upload_order_result(order_me, order_no, img_url, amount, ck_status)
    # upload_order_result(order_me, '', '', amount, ck_status)



def create_order_qb(ck, order_me, amount, qq, proxy):
    pc_client = pc_jd(ck, proxy)
    code, order_no, cashier_url = get_useful_unpay(ck, amount, proxy)
    if code != SUCCESS:
        return code, None, None
    if cashier_url == None:
        code, repeatkey = pc_client.qb_get_repeatkey(QB_SKUIDS[amount])
        print(repeatkey)
        if code != SUCCESS:
            return code, None, None
        code, cashier_url = pc_client.qb_submit_order(amount, repeatkey, qq)
        for i in cashier_url.split('?')[1].split('&'):
            if 'orderId' in i:
                order_no = i.split('=')[1]
    # return SUCCESS, order_no, order_no
    # print(order_no)
    # print(cashier_url)
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    tools.LOG_D(weixin_page_url)
    # weixin_page_url = 'https://pcashier.jd.com/weixin/weixinPage?cashierId=1&orderId=248572526985&sign=a2dbea7cfcbc9d5ba448d6b0ade9bb6b&appId=pcashier'
    # weixin_page_url = 'https://pcashier.jd.com/weixin/weixinPage?cashierId=1&orderId=248609542688&sign=bdcfdb8be07588b1e1cc8e6a6d688c49&appId=pcashier'
    code, status = pc_client.weixin_page_qb(weixin_page_url)
    if code != SUCCESS:
        return code, None, None
    if status == False:
        return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url


def create_order_knowkedge(ck, amount, skuid, qq, proxy):
    pc_client = pc_jd(ck, proxy)
    code, order_no, cashier_url = get_useful_unpay(ck, amount, proxy)
    if code != SUCCESS:
        return code, None, None
    if cashier_url == None:
        code, repeatkey = pc_client.knowledge_get_repetkey(skuid)
        print(repeatkey)
        pc_client.test()
        if code != SUCCESS:
            return code, None, None
    # return None
        code, cashier_url = pc_client.knowledge_submit(skuid, repeatkey, amount, qq)
        if code != SUCCESS:
            return code, None, None
        for i in cashier_url.split('?')[1].split('&'):
            if 'orderId' in i:
                order_no = i.split('=')[1]
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None

    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None

    for i in range(5):
        code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
        if code != SUCCESS:
            return code, None, None
        tools.LOG_D(weixin_page_url)

        code, status = pc_client.weixin_page_qb(weixin_page_url)
        if code != SUCCESS:
            return code, None, None
        if status == True:
            break
        code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
        sleep(1)
        i += 1

    if status == False:
        return CK_UNVALUE, None, None


    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        return code, None, None
    print('success', img_url)
    return code, order_no, img_url


def order_knowkedge(ck, order_me, amount, qq):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('account: ' + account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(3):
        code, order_no, img_url = create_order_knowkedge(ck, amount, DNF_SKUIDS[amount], qq, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            if proxy == None:
                return None
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            order_sql().insert_order(order_no, amount)
            order_sql().update_order_time(order_no)
            break
        elif code == RET_CODE_ERROR:
            return None
        i += 1
    tools.LOG_D(img_url)
    upload_order_result(order_me, order_no, img_url, amount, ck_status)



def create_order_qb_unpay(ck, order_me, amount, qq, proxy):
    pc_client = pc_jd(ck, proxy)
    code, repeatkey = pc_client.qb_get_repeatkey(QB_SKUIDS[amount])
    print(repeatkey)
    if code != SUCCESS:
        return code, None, None
    code, cashier_url = pc_client.qb_submit_order(amount, repeatkey, qq)
    for i in cashier_url.split('?')[1].split('&'):
        if 'orderId' in i:
            order_no = i.split('=')[1]
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    tools.LOG_D(weixin_page_url)
    # weixin_page_url = 'https://pcashier.jd.com/weixin/weixinPage?cashierId=1&orderId=248572526985&sign=a2dbea7cfcbc9d5ba448d6b0ade9bb6b&appId=pcashier'
    code, status = pc_client.weixin_page_qb(weixin_page_url)
    if code != SUCCESS:
        return code, None, None
    if status == False:
        return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url



    # app_client.gen_token()
    # img_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=a78134e5944ce6619b7a54d2649898586b4776d24acc654320214577da92c7cbcd92cf045f5eab8bd50492fd2bf6035d45eb0db7d81e99916b6e43eeab562ba13b9487beaf0dcae568f49411ab2e64b3'
    # code, token  = app_client.gen_token(img_url)
    # pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
    # print(pay_url)

def get_real_qb(ck, order_info):
    order_no = order_info.split('=')[0]
    amount = order_info.split('=')[1]
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    account = tools.get_jd_account(ck)
    proxy = None
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        code, pay_url = get_ios_wx(ck, order_no, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['msg'] = 'ck unvalue'
            break
        elif code == SUCCESS:
        # pay_url = 'weixin://app/wxe75a2e68877315fb/pay/?nonceStr=7c250678f61f49092fa0d4040e5e54e9&package=Sign%253DWXPay&partnerId=1238342201&prepayId=wx1321152505977680ae181c2f694ddd0000&timeStamp=1655126125&sign=872D48225CD35C74783548967B23710D&signType=MD5'
            result['code'] = '0'
            result['data'] = pay_url
            result['msg'] = 'success'
            return json.dumps(result)
        i += 1
    return json.dumps(result)



def get_real_url(ck, img_url, os):
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    account = tools.get_jd_account(ck)
    proxy = None
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        app_client = jd(ck, proxy)
        tools.LOG_D(img_url)
        code, token = app_client.gen_token(img_url)
        tools.LOG_D(token)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            if proxy == None:
                return None
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['msg'] = 'ck unvalue'
            break
        elif code == SUCCESS:
            pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token
            result['code'] = '0'
            result['data'] = pay_url
            result['msg'] = 'success'
            return json.dumps(result)
        i += 1
    return json.dumps(result)

def upload_callback_result(result):
    url = 'http://127.0.0.1:9191/api/ordernotify/notifyorderstatus0069'
    head = {
        'content-type': 'application/json'
    }
    tools.LOG_D(result)
    res = requests.post(url, headers=head, data=result).json()
    tools.LOG_D(str(result) + '\nret:' + json.dumps(res))
    if res['code'] == 0:
        return True
    else:
        return False

def upload_order_result(order_me, order_no, img_url, amount, ck_status):
    url = 'http://127.0.0.1:9191/api/preparenotify/notifyjdurl0069'
    head = {
        'content-type': 'application/json'
    }
    data = '{"prepare_status": "1", "ck_status": "1", "order_me": "' + order_me + '", "order_pay": "247775877802", "amount": "' + amount + '", "qr_url": "https://pcashier.jd.com/image/virtualH5Pay?sign=d6e2869be73c243c560393c09a7182ca89a1ed515bb088cc3ca08658daa14a0a6d4f8399eb23e3c53f93c113731f840e7fbd03300ab7e2ace58ab06ead2a3128ca6ce6e5705410517c18220000f4be1334af41273e8fe32548929db9a7001d32"}'
    data = {
        'prepare_status': '1',
        'ck_status': ck_status,
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'qr_url': img_url
    }
    if img_url == None:
        data['prepare_status'] = '0'
    data = json.dumps(data)
    tools.LOG_D(data)
    res = requests.post(url, headers=head, data=data)
    print(res.text)

    
def handle_fail(code):
    pass


def test(ck):
    pc_client = pc_jd(ck)
    pc_client.get_order_url('247682795586')


def query_order_appstore(ck, order_me, order_no, amount):
    result = {
        'check_status': '1',
        'pay_status': '0',
        'ck_status': '1',
        'time': str(int(time())),
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'card_name': '',
        'card_password': ''
    }
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        proxy = tools.getip_uncheck()
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        pc_client = pc_jd(ck, proxy)
        code, order_status, status_name = pc_client.get_order_status(order_no)
        if code == SUCCESS:
            if order_status == True and status_name == '已完成':
                code, card_id, card_key, pay_time = pc_client.get_kami(order_no)
                result['card_name'] = card_id
                result['card_password'] = card_key
                result['pay_status'] = '1'
                tools.LOG_D(card_id, card_key, pay_time)
                result = json.dumps(result)
                if upload_callback_result(result):
                    if order_status == True and status_name == '已完成':
                        pc_client.clear_order(order_no)
            else:
                result = json.dumps(result)
                upload_callback_result(result)
            return
        elif code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1


def query_order_qb(ck, order_me, order_no, amount):
    result = {
        'check_status': '1',
        'pay_status': '0',
        'ck_status': '1',
        'time': str(int(time())),
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'card_name': '',
        'card_password': ''
    }
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        proxy = tools.getip_uncheck()
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        pc_client = pc_jd(ck, proxy)
        code, order_status, status_name = pc_client.get_order_status_qb(order_no)
        if code == SUCCESS:
            if order_status == True and status_name == '充值成功':
                result['pay_status'] = '1'
                result['card_name'] = 'QB' + str(time()).replace('.', '')
                result['card_password'] = 'QB' + str(time()).replace('.', '')
                result = json.dumps(result)
                upload_callback_result(result)
                order_sql().delete_order(order_no)
            else:
                result = json.dumps(result)
                upload_callback_result(result)
            return
        elif code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1

    result = json.dumps(result)
    upload_callback_result(result)





def query_order_appstore_immediate(ck, order_me, order_no, amount):
    result = {
        'check_status': '1',
        'pay_status': '0',
        'ck_status': '1',
        'time': str(int(time())),
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'card_name': '',
        'card_password': ''
    }
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        proxy = tools.getip_uncheck()
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        pc_client = pc_jd(ck, proxy)
        code, order_status, status_name = pc_client.get_order_status(order_no)
        if code == SUCCESS:
            if order_status == True and status_name == '已完成':
                code, card_id, card_key, pay_time = pc_client.get_kami(order_no)
                result['card_name'] = card_id
                result['card_password'] = card_key
                result['pay_status'] = '1'
                tools.LOG_D(card_id, card_key, pay_time)
                result = json.dumps(result)
                if upload_callback_result(result):
                    if order_status == True and status_name == '已完成':
                        pc_client.clear_order(order_no)
            else:
                result = json.dumps(result)
                upload_callback_result(result)
            return
        elif code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1



def callback(ck, order_no, order_me, amount):
    result = {
        'check_status': '',
        'pay_status': '',
        'ck_status': '',
        'time': '',
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'card_name': '',
        'card_password': ''
    }
    proxy = None
    pc_client = pc_jd(ck)
    code, order_status, status_name = pc_client.get_order_status(order_no)
    if code != SUCCESS:
        pass
    if order_status == True and status_name == '已完成':
        code, card_id, card_key, pay_time = pc_client.get_kami(order_no)
        tools.LOG_D(card_id, card_key, pay_time)
        result['check_status'] = '1'
        result['pay_status'] = '1'
        result['ck_status'] = '1'
        result['order_me'] = order_me
        result['order_pay'] = order_no
        result['card_name'] = card_id
        result['card_password'] = card_key
    else:
        result['check_status'] = '1'
        result['pay_status'] = '0'
        result['ck_status'] = '1'
        result['order_me'] = order_me
        result['order_pay'] = order_no
        pass
    result = json.dumps(result)
    if upload_callback_result(result):
        if order_status == True and status_name == '已完成':
            pc_client.clear_order(order_no)



if __name__=='__main__':
    # ck = 'pin=bb17108392702; wskey=AAJijhQVAEAUuK5yxaGAiLVqJz3vy2eDcw4Mbk13xp2KJWAMbw8Ni2ihRP8D9e-mIYOsLhbPWOLy8edS4GfgUOx6trKMts4f; __jdv=76161171|direct|-|none|-|1653475472625; __jdu=1653475472623645022175; areaId=5; ipLoc-djd=5-142-0-0; shshshfp=c8154d5c31b835b717a87e7197043139; shshshfpa=c4e699b6-78cd-5d72-fc82-0464edc0b499-1653475476; shshshfpb=dNdB1ULltKqRZUn3U3kSZ1g; TrackID=18oAEvWCESKwvCuZTMo9UEpieA7cIkc8fA4W6voDJHt2LMMaQXjGq49NKPbG3KRXgURDbZgVGIy_FOFTvSVYIe3X40H_Y0WRKQs-YGdTGUVCjIwSt8oIhXhw1fczaSzGr; pinId=hZVnPybRNrtIM016vp53LQ; pin=bb17108392702; unick=bb17108392702; ceshi3.com=000; _tp=LSfrzCZhIkpYM+Vd6iAGJQ==; _pst=bb17108392702; bjd.advert.popup=d34dd1b9cb1caaaad0c408ab72e7615d; qd_ad=-|-|-|-|0; qd_uid=L3LM5W8G-C09N0FN6RODT8GLSSTCG; qd_fs=1653484809324; qd_ts=1653484809324; qd_ls=1653484809324; qd_sq=2; qd_sid=L3LM5W8G-C09N0FN6RODT8GLSSTCG-2; _distM=247703057827; __jda=122270672.1653475472623645022175.1653475473.1653484717.1653498288.3; __jdb=122270672.7.1653475472623645022175|3.1653498288; __jdc=122270672; thor=5B960A72EDEABC412FA1D4E520C1BAE311222104FDB0B15D2E58892276E8C63CE4DE693C0C75A7449351710A7E23605E28CCA52B810D9167E8BB81CFB5CF89007E75EBEAE6737E0075B1486A656A9500BC332BAC42624A3C71E0491288E810BF86CBDF2DCC52F4BBAD1E2CCA2A689AC89183E2DE66E04A87897CFAF22615DECA421E391A0010E64D0DE1E67EAD55CA4C; 3AB9D23F7A4B3C9B=RI6THBNZSP72TJ56KEHDNOJWYNEOHHKWSYJDG2HCFCH5LHJBYSLIHQFOTUMOEGVVCPKBWM56QOYAETL5O3BOYIYDQ4'
    ck = '__jdv=76161171|direct|-|none|-|1653749346999; cud=0730de7257939d3fd7461cbff9dfe95d; cvt=1; jdu=1653749346999445038783; areaId=5; ipLoc-djd=5-148-0-0; shshshfp=cd34b24a1665fd7b12e97eb7ed71868f; shshshfpa=fcf1641c-08b8-866f-a460-4c84b762dc99-1653749348; TrackID=1wUCxHob9ggkJeJtHkzZCVa5Tb1NX0-hCQ-1ysQLskFMEjV5gKFsoBSahhiTfQuPXxISuZmxqqUWI-1lRlHyuHq0RFd5-mJwD9FD8AB7Zkj1kY_BJUOPPz3eJdw63rGbK; thor=ACE0952A8F2157F5D040EB4A1880B15BC8004900DB7A874465C5D9C17160CD20C5AE1A38E33D7DBDDC4BDDF96EB0A30C4C707A20D3C43EC76F9011D8E01A47CDA7F6111C88FCCF746EC7FCE63BD5000B832BE0FA74842A0D765D07CD46669EFA3996448D5DAF61DFA8DCBB223CD8076E12201EB3229ED32855A5F837A0C423FC7A5C96C094D6AC77CD07638C4FF4773E; pinId=m4W1ON9HdhXhf853BbXirUuw8eocEJZIzcca-DjZFyE; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; unick=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDu8L8+kWidpUZSpfurkvvAJtAZmNbi6aX/ToTXRDPWc+j+x9HoMC4pmpejYnscNPcGjD82Uzx9T468WX88Z0AMSZBVWcJ6+CQGSWn+zoaSpDH; _pst=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; shshshsID=a78231a1c715154152ba173030d5cde1_2_1653749372588; bjd.advert.popup=e51b5713dba58eb0dee78e993c9288bf; jda=122270672.1653749346999445038783.1653749347.1653749347.1653749347.1; jdc=122270672; 3AB9D23F7A4B3C9B=YC3I4KBDT6NTFRCJAIDMNOQ5ORYTPPVEMQQFYHEL3KNEGSPHNWF3RYM4D5SZK7UM6Y5H3HP6D3XUUMFVXOAKIPLJYA; __jdb=122270672.7.1653749346999445038783|1.1653749347; csn=6'
    ck = 'pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%B8%BF%E5%85%89%E7%83%AD%E5%8A%9B%E6%9C%89;wskey=AAJikkyeAFDY6a4fMRVCTVaFKsoHTAhCY1ufcASTPbKbz6MOYnJ3jDL44hfLhXuFW5gbns6Pb49g9uk-Je-S3wo7hJn11O9s0lBnReZx4z_cvN4mV1is_Q; __jdv=76161171|direct|-|none|-|1653755135844; cud=2e4b2206c61d1ff684de25a2d4346e93; cvt=1; __jdu=16537551358431249497367; ipLoc-djd=5-148-0-0; areaId=5; shshshfp=cd34b24a1665fd7b12e97eb7ed71868f; shshshfpa=92273255-0271-31c0-9cda-5b2fbcdb76a1-1653755137; shshshsID=35bbe3f9a95d42cc15ef87578365011d_1_1653755137483; shshshfpb=oekB9r83jqDqVTo_iagsJ1A; TrackID=1fH7umkqe9_kd00dmJdmQv8Ky_EWijKDD2CZN8qMQrcI_5stLnabGdcUDA1DoruaC1YnoBEjSoDQwohyBP3cQ_YYVj39ICom0LKIbzxsNmZxqUllQ0yGYcNhu93_0LUtH; thor=D730C4ACC232FCD9CB3472289B11675F1580AD76F2BE08203D251817F15522D27335CCE1A656E5D16BBC20A7F31D423BCBA6C0F5B6B7C2C5FF65DB978CAFB0435893103A89903FD2450C18DA949459BA7088F972C2E8D8CE92DCD59FE8443B9F5411E55CFE47A420C93818519EC24971CBC62161C34B7AD26B981243DF8C1841B73F8043CBA5F4749F14F1214041B5E6; pinId=m4W1ON9HdhVYm_4VNF1VJAppH81LKH3KtX37H5_fCPs; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%B8%BF%E5%85%89%E7%83%AD%E5%8A%9B%E6%9C%89; unick=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%B8%BF%E5%85%89%E7%83%AD%E5%8A%9B%E6%9C%89; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDuwh71rGCdI5K4oWwhwuxEICJYuuhYFKiMmZMbb4IoCVqW9yfthyxBQSD9g2itHmugNPuL/KW4kx1Yk5kqBGWuqI=; _pst=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%B8%BF%E5%85%89%E7%83%AD%E5%8A%9B%E6%9C%89; bjd.advert.popup=bb8e8cb52856ea93484956af23c41a89; __jda=122270672.16537551358431249497367.1653755136.1653755136.1653755136.1; __jdc=122270672; 3AB9D23F7A4B3C9B=YC3I4KBDT6NTFRCJAIDMNOQ5ORYTPPVEMQQFYHEL3KNEGSPHNWF3RYM4D5SZK7UM6Y5H3HP6D3XUUMFVXOAKIPLJYA; __jdb=122270672.7.16537551358431249497367|1.1653755136; csn=6'
    ck = '__jdv=76161171|direct|-|none|-|1653749346999; cud=0730de7257939d3fd7461cbff9dfe95d; cvt=1; jdu=1653749346999445038783; areaId=5; ipLoc-djd=5-148-0-0; shshshfp=cd34b24a1665fd7b12e97eb7ed71868f; shshshfpa=fcf1641c-08b8-866f-a460-4c84b762dc99-1653749348; TrackID=1wUCxHob9ggkJeJtHkzZCVa5Tb1NX0-hCQ-1ysQLskFMEjV5gKFsoBSahhiTfQuPXxISuZmxqqUWI-1lRlHyuHq0RFd5-mJwD9FD8AB7Zkj1kY_BJUOPPz3eJdw63rGbK; thor=ACE0952A8F2157F5D040EB4A1880B15BC8004900DB7A874465C5D9C17160CD20C5AE1A38E33D7DBDDC4BDDF96EB0A30C4C707A20D3C43EC76F9011D8E01A47CDA7F6111C88FCCF746EC7FCE63BD5000B832BE0FA74842A0D765D07CD46669EFA3996448D5DAF61DFA8DCBB223CD8076E12201EB3229ED32855A5F837A0C423FC7A5C96C094D6AC77CD07638C4FF4773E; pinId=m4W1ON9HdhXhf853BbXirUuw8eocEJZIzcca-DjZFyE; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; unick=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDu8L8+kWidpUZSpfurkvvAJtAZmNbi6aX/ToTXRDPWc+j+x9HoMC4pmpejYnscNPcGjD82Uzx9T468WX88Z0AMSZBVWcJ6+CQGSWn+zoaSpDH; _pst=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; shshshsID=a78231a1c715154152ba173030d5cde1_2_1653749372588; bjd.advert.popup=e51b5713dba58eb0dee78e993c9288bf; jda=122270672.1653749346999445038783.1653749347.1653749347.1653749347.1; jdc=122270672; 3AB9D23F7A4B3C9B=YC3I4KBDT6NTFRCJAIDMNOQ5ORYTPPVEMQQFYHEL3KNEGSPHNWF3RYM4D5SZK7UM6Y5H3HP6D3XUUMFVXOAKIPLJYA; __jdb=122270672.7.1653749346999445038783|1.1653749347; csn=6; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89;wskey=AAJikkYfAFAgXEakpQ3A5vKOv_XopdQHyNXwOgIyWzinpb4vJ4pEa5Ys-xdfUsiLo_eBT29DW0ZnrPoBmOlokxBZij94z8zPMvFLrI6HibdzBRaF5zv_UQ;'
    ck = '__jdv=76161171|direct|-|none|-|1653749346999; cud=0730de7257939d3fd7461cbff9dfe95d; cvt=1; jdu=1653749346999445038783; areaId=5; ipLoc-djd=5-148-0-0; shshshfp=cd34b24a1665fd7b12e97eb7ed71868f; shshshfpa=fcf1641c-08b8-866f-a460-4c84b762dc99-1653749348; TrackID=1wUCxHob9ggkJeJtHkzZCVa5Tb1NX0-hCQ-1ysQLskFMEjV5gKFsoBSahhiTfQuPXxISuZmxqqUWI-1lRlHyuHq0RFd5-mJwD9FD8AB7Zkj1kY_BJUOPPz3eJdw63rGbK; thor=ACE0952A8F2157F5D040EB4A1880B15BC8004900DB7A874465C5D9C17160CD20C5AE1A38E33D7DBDDC4BDDF96EB0A30C4C707A20D3C43EC76F9011D8E01A47CDA7F6111C88FCCF746EC7FCE63BD5000B832BE0FA74842A0D765D07CD46669EFA3996448D5DAF61DFA8DCBB223CD8076E12201EB3229ED32855A5F837A0C423FC7A5C96C094D6AC77CD07638C4FF4773E; pinId=m4W1ON9HdhXhf853BbXirUuw8eocEJZIzcca-DjZFyE; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; unick=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDu8L8+kWidpUZSpfurkvvAJtAZmNbi6aX/ToTXRDPWc+j+x9HoMC4pmpejYnscNPcGjD82Uzx9T468WX88Z0AMSZBVWcJ6+CQGSWn+zoaSpDH; _pst=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89; shshshsID=a78231a1c715154152ba173030d5cde1_2_1653749372588; bjd.advert.popup=e51b5713dba58eb0dee78e993c9288bf; jda=122270672.1653749346999445038783.1653749347.1653749347.1653749347.1; jdc=122270672; 3AB9D23F7A4B3C9B=YC3I4KBDT6NTFRCJAIDMNOQ5ORYTPPVEMQQFYHEL3KNEGSPHNWF3RYM4D5SZK7UM6Y5H3HP6D3XUUMFVXOAKIPLJYA; __jdb=122270672.7.1653749346999445038783|1.1653749347; csn=6;'
    ck = 'pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%87%91%E4%B8%B0%E5%86%9C%E4%B8%9A%E6%9C%8D%E5%8A%A1%E6%9C%89;wskey=AAJiklV3AFACDQDKoHGlXGNYsMz1HF3E6OFUuP0AWxLVcI71Z5pepeqC0QJYbh34mSatv22vzoR8QXPdahkhtJWwGK_3250JJoLal92gcECHI0ozrPwIKg;whwswswws=JD012145b9D6405wwb5D165375727943804L_dxdNLi1gf1c0EXawekreaQiLzuMGCCjmXHZrRqdrqvAq2wV6JaJHWARSpwRxOloRjxA_1bMLgE_0IsjNSGe5cdwkjLkKFFVt_d1c2k6i40o43acv~w-H8Ca39GZRldpTyl2iE3XTDzHslz3sf_64_MlKd72L5zWA9DFU48NkCDwJRbVN0wDZ-_d0Dwigt7Rh9xL7arbEVJ7r8rijheqq_suexqsqBUwvCv4PLiZU7f4naDSFHzaPOTS-WVA5Q9U3XVdBBWxaeG0mi9PWTGchze5UAQceA;unionwsws={"devicefinger":"eidAf2d481228as1+bPJmhKvSSCLXDzBu+XwU\/mzyxseTMqyHgBKzK+7z8H4n6Pw3xVOKVV6fKviEm7QGA+ispC6p18J6Mfziuie15rHVioGtemItl1K","jmafinger":"JD012145b9D6405wwb5D165375727943804L_dxdNLi1gf1c0EXawekreaQiLzuMGCCjmXHZrRqdrqvAq2wV6JaJHWARSpwRxOloRjxA_1bMLgE_0IsjNSGe5cdwkjLkKFFVt_d1c2k6i40o43acv~w-H8Ca39GZRldpTyl2iE3XTDzHslz3sf_64_MlKd72L5zWA9DFU48NkCDwJRbVN0wDZ-_d0Dwigt7Rh9xL7arbEVJ7r8rijheqq_suexqsqBUwvCv4PLiZU7f4naDSFHzaPOTS-WVA5Q9U3XVdBBWxaeG0mi9PWTGchze5UAQceA"};'
    ck = '__jdv=76161171|direct|-|none|-|1653757067629; cud=df370b238dc610c48b487239c8e97965; cvt=1; __jdu=16537570676271452648685; areaId=5; ipLoc-djd=5-148-0-0; shshshfp=cd34b24a1665fd7b12e97eb7ed71868f; shshshfpa=6fd5b59b-0ee9-7239-01ea-d834dc5d1437-1653757069; shshshfpb=sPNK5IKrELODHb4ZDrJpzxw; TrackID=16wUomAJUp2uXk1obbpv1mV8Kt67Iv9hGOvyd9qOo7RuyWgnerB0UlMpCfA8ZTP2DBTIFoIrTIGTwVQxyl2wmR8kEhIwkwKIZxF-XBxUInc4kMGyIw9qRXlfiJ0mRuZrH; thor=D24CBEE8BD33E68999AB333ED46A9720BBCCB982964DC0573E274E9CFCD65A2C8486274C4F4FC894212D15F06FAA743D16F5321484BC09626C059729568FD95A66EBBAECB36F5EF0DD0081E37535B7E861522C9434BA72718465FA7FE06012F7CDE335226E48F13C277473F247B587633771F3069847785B69EDC79A8F92DDA105E852364B820ACD9299493E2E23522D; pinId=m4W1ON9HdhU_7qj20VML0sAKFP8AIzG7RpfSlmi5DgA; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%87%91%E4%B8%B0%E5%86%9C%E4%B8%9A%E6%9C%8D%E5%8A%A1%E6%9C%89; unick=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%87%91%E4%B8%B0%E5%86%9C%E4%B8%9A%E6%9C%8D%E5%8A%A1%E6%9C%89; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDuyl1wM+bm+YIZklrYw3LDCDio6k+hvYaf2mdbZz9slb28/qD0nWWOb37AmlzqOoa2KdhiOkfJxfUVRF3hdm1CHkbwwbIAImGeAsxGpSlPEDQ; _pst=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%87%91%E4%B8%B0%E5%86%9C%E4%B8%9A%E6%9C%8D%E5%8A%A1%E6%9C%89; shshshsID=1da6c1fca4ccd25e0a3ec6baa1b82b4d_2_1653757080650; bjd.advert.popup=eb02984fd2e992e3cfa25fb567692015; __jda=122270672.16537570676271452648685.1653757068.1653757068.1653757068.1; __jdc=122270672; 3AB9D23F7A4B3C9B=YC3I4KBDT6NTFRCJAIDMNOQ5ORYTPPVEMQQFYHEL3KNEGSPHNWF3RYM4D5SZK7UM6Y5H3HP6D3XUUMFVXOAKIPLJYA; __jdb=122270672.7.16537570676271452648685|1.1653757068; csn=6'
    ck = '__jdv=76161171|direct|-|none|-|1653755677608; cud=d17b3b906bf0d2f4347129c33a10fac0; cvt=1; __jdu=1653755677607992066371; areaId=5; ipLoc-djd=5-148-0-0; bjd.advert.popup=de527453264e572003bb611b3ef9be26; smb_track=61D8F62D5CF04FE8960AFDB2DA62C591; wlfstk_smdl=3lwh0z6x2qrapo7rz4bj31cwrwr3wje0; TrackID=184Nbu3YxjEIjKxVL1XB3ZN_uNfoxSiXtPrNtoOR-66o1tw53fuKfZ-ufXfS8U7HHlwv15IDruPAosI6S_VVCc9VKNDF_ly_coe4iMoHOWEtlsS5HLi1GYWhzvJKPWSXn; thor=02C1781462EFE1CC60B66675B06E311B606552193010D0A9201307A4B6530973E738C9B241629E1FDC14DE0F356453FA44E383DBAFC39817ABFB83800A5E2D9BC1A26DC4E96E428FEE29D3382EA54A55287C47B7898AA102B2423340DFE7F7C833C2CE2CA61D142A5F30A8804BFE9C383532CB7320E419FF9D6E0E56EEBC232B35719AD7EECD860445D12625A8DDBCB3; pinId=m4W1ON9HdhW5rXPPWmWWh8g2_WjdTMYK0jQafeKeB28; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E5%92%8C%E5%85%B4%E6%88%BF%E5%9C%B0%E4%BA%A7%E5%BC%80; wskey=AAJiklAWAFCIwesYPDXCq7Npy__op37Lyx-qYO3etqH0qUDPWOogSSn2N3i1Mk4c4yPE0K9lO39-hmY4OxUGEW0QzCPcIJ7j8YYmcwaV1kEpbkPtxxH4ZA; unick=%E8%AE%B7%E6%B2%B3%E5%B8%82%E5%92%8C%E5%85%B4%E6%88%BF%E5%9C%B0%E4%BA%A7%E5%BC%80; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDu1KOJFpGQofXcE9Fl2GUqZnacRmlaXTq8Z6AsgiH3WVZv0ZxnzjVhguB4ZUq5A/ZxybDJ7EICNnUKxOvc7iQnywaN1mDzwdtVAho+z6SQpfo; _pst=%E8%AE%B7%E6%B2%B3%E5%B8%82%E5%92%8C%E5%85%B4%E6%88%BF%E5%9C%B0%E4%BA%A7%E5%BC%80; __jda=122270672.1653755677607992066371.1653755678.1653755678.1653755678.1; __jdc=122270672; 3AB9D23F7A4B3C9B=YC3I4KBDT6NTFRCJAIDMNOQ5ORYTPPVEMQQFYHEL3KNEGSPHNWF3RYM4D5SZK7UM6Y5H3HP6D3XUUMFVXOAKIPLJYA; __jdb=122270672.8.1653755677607992066371|1.1653755678; csn=7'
    ck = '__jdv=76161171|direct|-|none|-|1653755677608; cud=d17b3b906bf0d2f4347129c33a10fac0; cvt=1; __jdu=1653755677607992066371; areaId=5; ipLoc-djd=5-148-0-0; bjd.advert.popup=de527453264e572003bb611b3ef9be26; smb_track=61D8F62D5CF04FE8960AFDB2DA62C591; wlfstk_smdl=3lwh0z6x2qrapo7rz4bj31cwrwr3wje0; TrackID=184Nbu3YxjEIjKxVL1XB3ZN_uNfoxSiXtPrNtoOR-66o1tw53fuKfZ-ufXfS8U7HHlwv15IDruPAosI6S_VVCc9VKNDF_ly_coe4iMoHOWEtlsS5HLi1GYWhzvJKPWSXn; thor=02C1781462EFE1CC60B66675B06E311B606552193010D0A9201307A4B6530973E738C9B241629E1FDC14DE0F356453FA44E383DBAFC39817ABFB83800A5E2D9BC1A26DC4E96E428FEE29D3382EA54A55287C47B7898AA102B2423340DFE7F7C833C2CE2CA61D142A5F30A8804BFE9C383532CB7320E419FF9D6E0E56EEBC232B35719AD7EECD860445D12625A8DDBCB3; pinId=m4W1ON9HdhW5rXPPWmWWh8g2_WjdTMYK0jQafeKeB28; pin=讷河市和兴房地产开; unick=讷河市和兴房地产开; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDu1KOJFpGQofXcE9Fl2GUqZnacRmlaXTq8Z6AsgiH3WVZv0ZxnzjVhguB4ZUq5A/ZxybDJ7EICNnUKxOvc7iQnywaN1mDzwdtVAho+z6SQpfo; _pst=讷河市和兴房地产开; __jda=122270672.1653755677607992066371.1653755678.1653755678.1653755678.1; __jdc=122270672; 3AB9D23F7A4B3C9B=YC3I4KBDT6NTFRCJAIDMNOQ5ORYTPPVEMQQFYHEL3KNEGSPHNWF3RYM4D5SZK7UM6Y5H3HP6D3XUUMFVXOAKIPLJYA; __jdb=122270672.8.1653755677607992066371|1.1653755678; csn=7'
    ck = 'pin=jd_0btkY4xXEvn2; wskey=AAJil55OAEDRGhlmgcd5wZ-26OLbYPD8JeE5z5lRUgRcnqOqTgHUDyxTZ9HnrPgllE7jHn-PMgjdCPesP1b9Ptsyvw_kGXod; pt_pin=jd_0btkY4xXEvn2; pt_key=AAJil55PADDhxksEVKxABY41fnwnkJZ_LJ0nVsqoAzgvjmNLiPytwLxTka7sPt9ooPU2n5Xdfe4; unionwsws={"devicefinger":"eidAba3f81218fs4opL0W5l2Q0SLoy4WlABUa6KS9dy5uKgk/C3yZnglm8YEGHTx+x3xuU0waGO32Qh8FmJGH6Nzvvf5UfuIQmmsVXc12odnaDA54m9D","jmafinger":"tGmwgi8u-kzCPDKUaPv_jr5PfD95nmvhVfhnj7Fpj3XeMs52rJnPF-cthkaF7x6qD"}; DeviceSeq=e332823f14164fe9b1ff30e9fc2b01b4; TrackID=1fR0B7seG_AbFWGexHpiuS01mR8d-YPwK4UWoHm10O7JO2896jw3lDTe8M05vUJM6lR1tY5dpCr-O00tncwl1D25taT8pOae1OB65nxTwN6s; thor=A7291C31B7F8C9461E8415DC878574BE8DBE7684212AE1141F590F2417A280D5D5C9592F6B332857DFB5C7484F85E67531C10B8D40DB871F5DB2D246F1AE92CB3C5833349028DF2E9589A48BC8D9350187C26A8AA90E56BC08EC8A2CA5207CE0218A766BBB90E0C986B0ACB247291979A52239665BBFD06F67EA35BCC216565FDF1E976FA1E3A0BC3984E4E7BC7A3B1B9DEA9EA340ED1EF12C725514F569EC59; pinId=en1A3u1HhlodlweZxhSjBw; unick=jd_0btkY4xXEvn2; ceshi3.com=000; _tp=jJvXPi8ZMnkz9%2F%2BA1g7hYw%3D%3D; logining=1; _pst=jd_0btkY4xXEvn2'
    ck = 'pin=jd_qFMUSreiBN7P; wskey=AAJil54wAECtn8kdVe9yt5z_6BKky9246L75rvLi40dv9HkcvPAEs9NnM6UYE590ucTsaLp59gr_rS0Ttb0R1vW-JcQH4Ax1; pt_pin=jd_qFMUSreiBN7P; pt_key=AAJil54xADBZSnpHIXvIGbh_nKTbt5-2t1Ix3FbxLh7SwZYaZltFx4SPNwnguqxa4Nj21-ad2ME; unionwsws={"devicefinger":"eidA0ad58122cbsdio1XPiq6TqSPXvEztdZQqoqNWL9K/D34Chyqu6CLxhAMpTD49eAnWnEx/AEB1Pz48ktXYqdr5VnJgMRks6ifA9+nOsUsTcVdwA4w","jmafinger":"wKjxYi5j9m73nEgueCv41Wa69RJiy7aqhfJryBBR19meSSHLnX755jBvZfCimOdR5"}; DeviceSeq=7da0a15524cc4a86a699ee16f249422d; TrackID=1frtMo4yVKlLTIThqqrHzA6TXWMeUBJ7ROZ7FZc-dj-iZ0PwhUAPmuE-3dCCvRrYRrKBcU5Y1G38LP4qRprMmK_oHaAMGb9bJmHf3e7Jv9_g; thor=E6C68BF6BC349B8DB31B1491C39E68DC47A5B3478B2BE69014457C94A2CF1232D8000C4CCDA86ADAB6C4556C3D910FCB7F4CA1C5BE308111A3A76112E56493675397DDF63DE38E72EDBCC0D02344B40677ED682A1EB0D7A3C30158FEA4EF7A4F1E94E47A89907907455F6E8233F8474B214935186D2ACFF731A3FFD8E4C0F637A6CF33216D5CF70DD8B234CC59A4239B9BC71668489459EDD468A5357786911A; pinId=NdMJUQt2pkG8f9LJo4DOQg; unick=jd_qFMUSreiBN7P; ceshi3.com=000; _tp=vEn6l4EAlgnEZT1tHooiJw%3D%3D; logining=1; _pst=jd_qFMUSreiBN7P'
    ck = 'pin=relunwenis; wskey=AAJil6byAEBl3gAWrW3KXuH7XX7XqmDtuN3hNhgFEeb3gk5fvGs7CrUCuI5yuVLoD-y0IuLFOM4zojlbBxqk5MQ1gUH1TVPM; pt_pin=relunwenis; pt_key=AAJil6bzADDKz-mTsALRK_owSzHpi1mCPbhzRDda24aRLeJBTnJV0yNiWTlBXZrJeHfZryl6DHE; unionwsws={"devicefinger":"eidA0f7b812298scUUxrvY3iQTakW/ZuRVCtp1FMbT6uRmdnFVR5MiSB/lZq71j4qEEUw2w1lGdmh4SuQdQJLEgGGkybHMkuaTMOljP97pRafwK/AFFU","jmafinger":"l9y8Y8IQq2pv3aTndHvTj5JhZP7PWi-0wRiNKKH4P7nM6-jmKArVoOJs2U3TQt2dp"}; DeviceSeq=ec0dc634655647a48dee217e0225fed1; TrackID=1kNIszPGQg-RTNHkWlPmM4ZJraqDf8rCbyIOpShhX95nMZ9Tp7H9W9A5YvVZW3U2VCy-eRDTh3XaZuTI8p_rIqpnnBUU4Ymy9syhn0p0G_Zo; thor=8C72F90B0E412F225470B026D24C6C0F2D8948744611A5206ED19A4E78E8CBEFCDAF409F05039BE20F9DA93A7EC621F46D0265C4DC26303FC1D721FED228DF0742B0AF3D4EF6DC2DC924F570433084D540D239F232DA1C131E8AFFCF052336D1B3E311F4DA1678880E93FCB6E71E262DC768A344BEBE13FA5E567F89BCAB4B6632419A7C165870749DD501813DDA47D1; pinId=yngNG8RhiHo_2yh9wv2pQQ; unick=relunwenis; ceshi3.com=000; _tp=vtkkv%2FiY0b2wPAXDCi7PeQ%3D%3D; logining=1; _pst=relunwenis'
    ck = 'pin=jd_620c23157abbe; wskey=AAJig64uAEAYUa7maQKPDrzVG6Tj00UL4RjCGLpkZBX1l-Edw2a0BdLtX_toWCRkPG3oiJX2hQU9uktxUb_8l1A__-yPr-g-; pt_pin=jd_620c23157abbe; pt_key=app_openAAJig64vADB9NoxEhkBwbCdBVgEvXhn82yXyZ79pJuCso3tlbn6pxFj3CO8m-vaZlxRvwePwxa4; unionwsws={"devicefinger":"eidAdc9f812208sfy5SUVHmJQpWb2UUkKIWHocuUldVL6Z2G4b6LqDV0clhrLQf0JDlWeFRsvD6M2/1VAOaWSoTLgyv4dj3UVYxYINZH/kQu9mAPuhx4","jmafinger":"yqCE_oqMMelaT63IkJ2MKrFEfupvpLcDp9PiAaWhzVibSCk0vQUHQ13yvlXCG_nR5"}; guid=4fff79991a8fae02a2d348ea7c6baee5da76275478f0da6de7580ff7cb9fdc91; pwdt_id=jd_620c23157abbe; sid=492237c958888556c50d876b17ef7948; USER_FLAG_CHECK=56048e907bf9c55d8517a41d777e5873; abtest=20220517221615488_52; mobilev=html5'
    ck = 'thor=1852CACA53C0E003E8BFECF10C55FBB5EEF436326E5FEB6CF31116A5446563BDB1631F881D824EA480A3CDC23B8DEBFA127FDA40019358AD926789D773FCDB00F03C27E8E9A9DB06EFD17898482FDBF502918026B319988F42613D2362FA8348CE42B4C46A62036EE0ECFD70D34B9DFA3CC0035F4FC040917C1DCCCC85760077B7364509BEA088D6946539252F0C7187; pinId=qbxInVe92VYBNB2Km3viKQ; unick=1zlFBWmyr; ceshi3.com=000; _tp=VwtT4LsE4IPokJjfln7G2Q%3D%3D; logining=1; _pst=1zlFBWmyr;'
    # ck = '__jda=187205033.16539204314931141715129.1653920431.1653920431.1653920431.1; __jdb=187205033.11.16539204314931141715129|1.1653920431; __jdc=187205033; __jdv=76161171|direct|-|none|-|1653920431493; __jdu=16539204314931141715129; areaId=5; ipLoc-djd=5-142-0-0; shshshfp=ce4ef42540f107788900abe5857d0831; shshshfpa=51cd8f7b-be86-dc0f-0327-607912dd751d-1653920432; shshshsID=f47a3bcd9f07375311f5d215bc0c9e6b_1_1653920432804; shshshfpb=bFfYFmNBEv3Ww_d-BJfrmsw; wlfstk_smdl=cpn7v5gdfgceqcrw66v27md6fgk9npmz; TrackID=12FCCdfvLPVUBG3A-ZlYYjRtf3ouXrSVDksS09rNtx3WYSL5SZIIM9IxHnvo8vW7mICFy6l6gJuV7y8ZCV4Dr2wZ_eG0015ensZlVPMwgCcWPv0cN44Y7zgx_gcFhKKPf; thor=6ACFE398FD99B21E5CD5BF8CE2DCE4EB0788031068B306653D0F1C237B844DCD303C1875DD576F5678D216184B82C8AA2AEC83016BF97CC31575362BC50DA4F8A1588B5360D25BBA5A7519987B45A6E389F731AB8A6ADEDC99811518EAB88E7E6A1A46FB6490B10AE828B1DA8ABF9BBA56F3616FC818D3764FA00D3C38AB2E33FDC29927FDDBDC2CC16DCBC00FD30913; pinId=aJBn56UcHbr6nJp9AcA2-A; pin=yNzZeCwSs; unick=yNzZeCwSs; ceshi3.com=000; _tp=DDU27STeItY6zX1100OSKg%3D%3D; _pst=yNzZeCwSs; bjd.advert.popup=77fff5c730715d8fbe88f442cc156069; 3AB9D23F7A4B3C9B=UKTIOLLP753IGSUPUQHSSQBHBY2Y5KIO6RHGFCUW3VJUYI3XCRDBBKM6TBNO5HXP5IKJTEXZ6P6HOYG3LUVWVOOMF4; _distM=247958383015'
    # ck = '__jdv=122270672|direct|-|none|-|1653684678322; shshshfpa=54b03d9b-9e14-a6f8-a6a4-74bc09ff1d79-1653684688; shshshfpb=kaxjITozukJzQKR2yTHvVkQ; __jdu=1653684678321815288407; areaId=5; ipLoc-djd=5-142-0-0; shshshfp=c8154d5c31b835b717a87e7197043139; TrackID=1LuiQoeX1l2uYaXGl4pWdvnKv07C5Ze_pbxbupAQe_P4b2oWYyGf9RImyGbJawpljoeJ_BaNMQoNSDIsmyDAWvhyHnwkVSj1zS6ynjxYMOGqHxNs5YeSHYWKGTYCyLdFB; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d+SKBX0iW+Qy5xFBy0C7MU1+oxmN9c=; _pst=jd_4d9b500034155; user-key=74aab15f-c2ad-432d-a388-6fe482a10e4a; cn=1; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A745F29F8513D02C2A15A9CCD823FCD255B1DC17C702797DE4A2B40A5749B0F9620A489FDFC834F465233DE7A1551BB66003DDFC7F1F3A45DEAA234DE753409D1F9C65C28D6027A43D1F6D4ED3F5BC13A7932654F616D6B971141147D75CB794FBE48D35E812D23B52180180F7DC923A237C9348AD1CE3B6A6C9CA9F983D6CE670F1; shshshsID=f7275fa22194787a412431d3e88b314b_1_1653763565833; __jda=122270672.1653684678321815288407.1653684678.1653752556.1653763559.4; __jdb=122270672.2.1653684678321815288407|4.1653763559; __jdc=122270672; 3AB9D23F7A4B3C9B=RI6THBNZSP72TJ56KEHDNOJWYNEOHHKWSYJDG2HCFCH5LHJBYSLIHQFOTUMOEGVVCPKBWM56QOYAETL5O3BOYIYDQ4'


    # ck = ck.encode("utf-8").decode("latin1")
    # pc_client = pc_jd(ck, None)
    # qr_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=8b2aad72668890803d70ddfce9341c399254da213289d54ee189d9646867fd9212c0ad4b2ec950030cadfbec772745c74270384c890ea00f51a93f8f8e125670aef277307a0ff5ecf6b214ab52cebebe34af41273e8fe32548929db9a7001d32'
    # get_real_url(ck, qr_url)
    # pc_client.get_order_list()
    # pc_client.get_order_status('247875909217')
    # pc_client.get_order_status('247775877802')

    # ck = 'mp=jd_uPlHcIlPnyzTnW2;  TrackID=1nEErzInNtLpop2-Lo1SCTBEHzZfLbcwaEhg9InjX8viFEs4oBELN7wl2XWv-Ynu0E6Xx1as1G7GVYcd57RhqARVtqnQ9N2Sxwz6nOtyTMgSXTm_EZEPnL2WAQ-sGV5La3T6khWUoE05Ea6rEOLfc3g;  thor=9279C802BF1DF49A97744F1921F198CB35FDB7596CF9ED63DDEF17A073E42D6052D8F0779D1847455959BDDAC1BCE6915F08D8068623B479C448E6AD5E8679F81527EB910A3DDE307F7113418E4352E12DC6EA2B44930E67AF701BC0255D763778D1D547A002BF19A798BC4BB8A58452ECFDF0AA794C2A91586F1AF640AA685E401582DC104864B83F40648B385E8BF6E580ECD469949E2D80DE98EA6A793562;  pinId=GvW4MUF8D7jTNNzpYb3xdYJeWJ6eghPZ;  pin=jd_uPlHcIlPnyzTnW2;  unick=jd_uPlHcIlPnyzTnW2;  _tp=8kAwDtLgQf8%2BeZRSG2H21tsaMsZ32Qi9XZL5o1GUAvA%3D;  _pst=jd_uPlHcIlPnyzTnW2; pin=jd_uPlHcIlPnyzTnW2; wskey=AAJiogKlAFDDFXsvInK4Vh5L5B1EKEY_RsSjHVwE3Ox_1bLTtzDQdDjhO9rxb1NqyvBdLGhmf47vXkMbtNw-YZfYbJMLyDAPDJAk0mg7XwI4YkoyNr24Mg..; TARGET_UNIT=bjcenter; guid=8fa1461f478d5af8254e49a01ecb187f3ec3886e1ac7789854e88beeb84aa4a5; pt_key=app_openAAJiogKnAEAaBZ7TxPGIcAB0-2djLTUYlAiOf-DhlxTTWNDqCrD5cqiuO4C-0yJ2GT-0YR5hv50kVEAwkVFMEnEGO9UjwbdY; pt_pin=jd_uPlHcIlPnyzTnW2; pwdt_id=jd_uPlHcIlPnyzTnW2; sid=5eea73329c535a9f29cb72e2e181015w'
    # ck = 'pin=%E6%80%BB%E5%BC%8F%E8%AE%BE%E6%95%AC; wskey=AAJiNaoDAEC84C05A0aq2fdMT7rORaZbJrEcy-pQaL_pfAeECQIthwaO1BgdAZfgo48gNCq_769yk1TBIbaRqlymW-uUte48; mp=%E6%80%BB%E5%BC%8F%E8%AE%BE%E6%95%AC;  TrackID=10YIH6fAWKU36HeGY4xw8PdL1RvqvQFguc85OIb6ZHptMbUGKCQO2TIaHqJhCh66B_HBmv5QRTSAnQ-1hxACkITq689T4gmxq7cRS0yrw6iBv8TVRZbXShWuxodzQl6C1;  thor=B77F9665654784C1771FF34283830D55034429B1D84EC85623AF01FFA10CB38BC685500F5228CE33A528980956E284AB47CC1180F22BE5DD82D8041EF9960D5D4E00A0948AE8A341D12D4505800EA33AE4A1A8C1E071BCB13957D4A1066CC907FB9CB08BF7B3E727D6E3D3101416EC32DD0CA124FBD36D52F6CF49B744EAC333;  pinId=p56bE4Z5HbIZOtIJLJ2ZQA;  pin=%E6%80%BB%E5%BC%8F%E8%AE%BE%E6%95%AC;  unick=jd_EazqYwjzisSo;  _tp=f%2B8wvpCxBbWs3EcBG34USmDYUUc4sPNUGJYzg%2BfgZQgJufct26rxXJlFJnyiHs90;  _pst=%E6%80%BB%E5%BC%8F%E8%AE%BE%E6%95%AC;'
    # ck = 'pin=%E6%80%BB%E5%BC%8F%E8%AE%BE%E6%95%AC; wskey=AAJiNaoDAEC84C05A0aq2fdMT7rORaZbJrEcy-pQaL_pfAeECQIthwaO1BgdAZfgo48gNCq_769yk1TBIbaRqlymW-uUte48;'
    # ck = '__jdv=76161171|direct|-|none|-|1655053931746; __jdu=16550539317441626176942; ipLoc-djd=21-1827-0-0; areaId=21; TrackID=1VTH9kmooHoaIy_Pit27jf9lDp8aq7uNw9nfcKT_nU-cjzSjN0WKMEEs-4mofNfLSd73-RvwzHHz7d1HMGNqLe7yxfmYnLwVbMav-SIEuR2g; pinId=GvW4MUF8D7jTNNzpYb3xdYJeWJ6eghPZ; pin=jd_uPlHcIlPnyzTnW2; unick=jd_uPlHcIlPnyzTnW2; ceshi3.com=000; _tp=8kAwDtLgQf8+eZRSG2H21tsaMsZ32Qi9XZL5o1GUAvA=; _pst=jd_uPlHcIlPnyzTnW2; shshshfpa=a579c10c-4a6e-033a-3858-2ca83d40a487-1655054022; shshshfpb=u2W5o6HCHzcxv-UxwlLO3kw; token=58d235d270602fdb72eca3cf959b2faa,3,919474; __tk=2UfC1APuqwNuruS42ursrY1AKUrsqUG41YxDqY2t2zMAqz141YtXrG,3,919474; shshshfp=164424c1b2403ec63fe41c91d1aa8982; shshshsID=3059d538b1416dd6b183a5ebaec10955_4_1655054071694; _distM=248495288589; qd_ad=-|-|-|-|0; qd_uid=L4BKHRFT-IWL4QZM9N7AKIDYPDXXM; qd_fs=1655054124324; qd_ls=1655054124324; qd_ts=1655054124324; qd_sq=1; qd_sid=L4BKHRFT-IWL4QZM9N7AKIDYPDXXM-1; thor=9279C802BF1DF49A97744F1921F198CB35FDB7596CF9ED63DDEF17A073E42D604C0111B94F3F82EB77D5D512AEFFF40FA1A53773DE6B1BB914A915F5D0A0CA233251884E25EACCD697805F39507821EC0277C64AAB2899BA96780E3C6B976F7C643CAA1C1DED25B1DCE35FCA263E672B0C34D076FA4FBBC9ACD3C9A820643DEAE0EB966A1BD18C1D283B4F8227D327EAAFDC5EE7F1EB6A4EAF21F5BEF4340553; 3AB9D23F7A4B3C9B=YBP4YEIUENYLTXH4V4Y6ZTZYOSGVVYCYTT3JHNHGSLRLQRATFYLUBPG653IHKFSNXMWTCSIWJGYZIBISUUSGQEOWWY; __jda=24961467.16550539317441626176942.1655053932.1655053932.1655053932.1; __jdb=24961467.16.16550539317441626176942|1.1655053932; __jdc=24961467'
    # ck = '__jdv=76161171|direct|-|none|-|1655101961436; __jdu=16551019614341375759345; areaId=21; ipLoc-djd=21-1827-0-0; TrackID=1cFkqkAtFJBSfgBuCVD49uXw-7f6uQVqQkX_A2bElOkX8mVHRn1ajhC3qMNMqDEfLM-ZiVYo2i0wmT93aXch6s7eHgwute8gFjg54dJM8lGEvgf-iWtWGT2bizKAyI_Tm3P-xJOB92dlOynXic4BJwg; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d%2BSKBX0iW%2BQy5xFBy0C7MU1%2BoxmN9c%3D; _pst=jd_4d9b500034155; shshshfpa=dd8f32ba-0b0e-fdd2-4e20-b88b239c45ac-1655101991; shshshfpb=eqZZ17sBAB9OERB_YX4U_FQ; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A745E350399D0BCAD2D796623BE2BEE5CF7891083712D4A082EB4C23BC7192C4B5496191760D1C31EAAEE709D7285CD07D1A7D95BAC4ACC2F3907F52B9D1F2954D8FE0F47C5E978ED4687830C4B223EB97B3F18241C06C79A2F470EA4CA71E75CA863612FDD8AECDA9D42016E6530668854308FA613D3D92268F22AD5A11AE433DCF; shshshfp=3ec2e38aeaef87232e6d74b5de7d50b5; shshshsID=c5e77eecad4445425e803109fe1bcb49_6_1655104454246; 3AB9D23F7A4B3C9B=QNCWC64QP4P2LVZKSMOYVQ5UVCXBVUAFAP3XXO4Q2JGY5MVLJ5CNJO5XE3NHQHT2XMBDWWZ24L3C6T75QSANI6DL6E; __jda=187205033.16551019614341375759345.1655101961.1655101961.1655101961.1; __jdb=187205033.18.16551019614341375759345|1.1655101961; __jdc=187205033; _distM=244726662902'
    # ck = 'wskey=AAJioezoAECwBP5u00yWw4Wmm1VoGgB6DKaGtp_iF-nnh3LMty5vhN6xuU0oVyMTQ9ENxG8Wyb2utzOCDrs5gulgXGCajild; pin=jd_4d9b500034155;'

    # ck = 'mp=jd_5fb9ae7b01e08;  TrackID=19FYOprl5sBgnEkuYUE3KDb0zG3SHGp7jCaunlHGMncLmYqqew8jn40NgY5cCPCy_zhmF9HVLD02jJvY1z7ST2Wv5VYEJFzAnPbiwzhO83MQ_os-3Nj2Bj1-AKegtZHs6zzhWeSjDTuKGOM3bVwrfvQ;  thor=B30DD83C6079DAA5CFBDA36F593B368D801DAF94F2BF40779727F6F9CFFB1DDF7F1362598B695E92B2B49895D18236005E7CC26ED03DD85FB14B5442A229BCAD8CD6523034E6BF3429F43F008CE9C268404161CAA7DE10BEDD056F1A055A989DE5B584F5C56A75E9A2DCCCF7161FB8BA3171EB701479C231A3D14AE4554966F4AC9A0420A167E462A952431A6B8FDDDBA0E7092A8C7BBBFBED8D0704D48A0EEB;  pinId=BGKvA2_UfjvhWAZmjwVu8rV9-x-f3wj7;  pin=jd_5fb9ae7b01e08;  unick=jd_153795jwr;  _tp=SQ7R3CmB8JuGRypP2WMBzKKIvWOeJwI9QrI7oK2WBz0%3D;  _pst=jd_5fb9ae7b01e08;pin=jd_5fb9ae7b01e08; wskey=AAJiik9hAEDDjxoqzjfQ1XpC-HYi3V5BN3ueuBk88kG2ysV-KnENPtnbpNcP0NoYBlPJUI9Q3eI-y8XoH-VrWtcbjUjZhAgj; pt_pin=jd_5fb9ae7b01e08; pt_key=AAJiik9jADAiGcrzRHH56ZpNTozHWShxk3d-Q7id3SuwdIToxU4F0DQx5BAWQN-wYVooN0HFiG0; unionwsws={"devicefinger":"eidAf2d9812223s47XKUfq+fStSVW1VOujudXO1ylf+b5WB4rKwtO5AJpcZmhzjIgcv1YEdiioqGHb6DI9CnyX8HD2Hf5du2E4Hfz/Jhi2AVzMn6qE1y","jmafinger":"qlcWImUm4XkA3PPAuUrp941LEp0xhgZz4dXXX0VwR1hxTlqfinMj0YNSC4qL7zV7P"}'
    # ck = 'mp=jd_474e7a709bc7f;  TrackID=1NeUHbdp5ia7p0GkIbx9nXYkW529m0CXNb6BRO-fk016FhieXIWqzO8LPVNXWTsg8lD59ZMP8v3HTa0dmUZpYx8SP1o0r8Emr-aSS1nw3IXYPcx6ipbA6anTD7KLYG8w6fUjxlKeNligZHtfNNWg9og;  thor=FC898F8A1BE881FEAB9205429175D2D0C6BFFECABA3D280010FBB740A3E8EDC48CDBD4C020B51E6BE9CBBAAB036D451CAE436CBF803C8B4E4A44A6A9A43C38EBA8C33B5485B11CC68324FB1A67F311E61C67C4E137523C411589A54052B55D20A5371A7B97F13FEBB727347394A705DF79382B72D2D9F3B89FAB413A040ADB5E3D0B8861896B7B1118DB17C75980A6C19FBEBA05574B5CDC60929D07F6D4E169;  pinId=46fYYuNy2Bc0K_U0pjz0pLV9-x-f3wj7;  pin=jd_474e7a709bc7f;  unick=jd_474e7a709bc7f;  _tp=i1rP4aZdhiuqeNPqeJ8oZ4PjW8W4Xjt8GoIpoJCZyAc%3D;  _pst=jd_474e7a709bc7f; pin=jd_474e7a709bc7f; wskey=AAJiik9uAEDW2ik5WNAvtRFhrtWh1I_DS4HhoUPqfkF-f5AiPy_A7XUK-yuF7CI01PBWkiifu7pNLfvxz17XmbnZMPdMppWZ; pt_pin=jd_474e7a709bc7f; pt_key=AAJiik9vADB2k1GpfJ_bvE8E68CKK320ZSUlJ12dy7gnOd3gzLtS7f7Lq5I4Gt3_xCWzl4odRQ8; unionwsws={"devicefinger":"eidAbe5d8120a3sdLJdV3OEVQqi3LkJJfWRvHCyXV13NW4zcvqX8nd70TwQYWpcZ4vS4NURZKMJdPcQQ2CXM/C51K3uKzCvMNfXDYm60FnS1M+344bZm","jmafinger":"dfI5WktNC1KLuBldBZ67Ry7ZENuX3cnt8_kkUdvhsbAa3dP3rHzXy-T_bK_t0eVIZ"}'
    # ck = 'mp=jd_6b9d96fd0d837;  TrackID=1xSTbkSRdGeyBYdpDR2fPKLhUi4XvabGBTnWOinJpsPoo66-cYsLUQX35wHGkT1yQySaNXUUQViN0vXd8M3I7_Sl6SI8Aaa40HxSqyolT2oR7Ux3kyS95XBruIGsP8UyK85AlwRbesYtoEMLG2i1IJw;  thor=7FE9F5D6D6C9A6C796BBEEA3189D28E8338722E18F03548C5AEF2D01B3C409B22FD0DA40D6BD10ED5421183F70CF1051E5F7811B0F7D5388AF851A0F7A1424D2201D68348F6B4E16345050FD7CE9C29CD5D12F9D11932095404C6E5912AE5F2F05E5D384E13A08E2FADC4E8B747F061902CA555A6DB030730DA715654145659FD2D23E10ECCCA637269E4B27A9E121D2303E8B98317DB9764D77931595CA363E;  pinId=N5_vYWcwCx2wbLEFt7aFIrV9-x-f3wj7;  pin=jd_6b9d96fd0d837;  unick=jd_153804kwdt;  _tp=%2BK5iEN2qxsfunAsu881z42iB5YIRoDUN6Hsup%2BOe1a4%3D;  _pst=jd_6b9d96fd0d837; pin=jd_6b9d96fd0d837; wskey=AAJiik9wAECj_LcQ2TY_8otK55ml-69lGcAanZ7kYn85xOg9alpSsLXowQD0fmtaiMou7VahI0ra4sFvMHPZZKXfNfirarR5; pt_pin=jd_6b9d96fd0d837; pt_key=AAJiik9xADDmPHrTFVbtmZtLhP9y9zdcq_rfvCj_pWMj7siS-epPtL9Os2ayf8gdWZu3saRMq7I; unionwsws={"devicefinger":"eidAc6588120ccs4Cok4yA2mTI6WDdRbQ66CnwqJOkj57JyhQWgx2Jp3BogfeZj9y/WRtHR1Goit9pa4O38whl97ijvo4Y05OU3WP1291ZNkTFYAm004","jmafinger":"kVxK-p1gOjV9M-lt-qrQhj_doUOOijFcrFcjhZNsisGDsa6Zjuh6i_gGtEzbdsLTv"}'
    # ck = 'mp=jd_vMd4ndXc5Sv6NPj;  TrackID=18RTfWm-UgNZzJo3dc1KnQC8jgwFTjq0JqGkkMTYZvJlQBphvz5s9v6QD5jxRep-bNPKeN0Fjv25ghc-aq_mSNT1caijJRJGZB0Tp3JOpdtVS_Mn8UMIQJkgqjp-5hCHucyGJjkifmocplcBpa-gvKw;  thor=7248A84612E5ACCA551476A6EF51F0E57CA7D5CEFE439BD712DA409C4F00EF3C56EAF246C5FCB20287E67389B4FB61F97644715E630258788BFE3845ABDD8420298FDE67E9ABC62B070D3FAE8402AD885144D0EF334194512E3BAE85A9E3373AD7812779FA3CA39549E72A743363ADD6F1BDF6CEA46AD02B87D0B73046C21E227809B37799F8C8FA20018F98B7B247FFDC796F3D32EF1C86C95BF000666D2874;  pinId=X6jIrSJAIN0Dz1-uddPyL_AK-8CHeFO6;  pin=jd_vMd4ndXc5Sv6NPj;  unick=jd_vMd4ndXc5Sv6NPj;  _tp=9Tw3GEGzFXC%2BWdHjP74noDLH64xRkfRnpK6ZuFJqWjc%3D;  _pst=jd_vMd4ndXc5Sv6NPj; pin=jd_vMd4ndXc5Sv6NPj; wskey=AAJiogLrAFAVIVwKfgWui1FtfIpTtEFq9NaDKy3bOqNK4mDiidYZM-bMQOwzdR5K5y1gLTiDXOzCBRhvCd-xApVNPRuEBOH06m1yLdiALQ2l3tZ6xxmiQg..; TARGET_UNIT=squnit; guid=2ece958887d0755afad6af5389b04441cf4fdbdb2562b83db8959eb64cfb9ab4; pt_key=app_openAAJiogLsAEBVzvlQQSAg4NeWEEliW_hsGwH6BI5BSAtY1Bbal1IsgQg5LSUlKx-ceeaOidV447OQgqWbDZ_f22qvCa4PHdtN; pt_pin=jd_vMd4ndXc5Sv6NPj; pwdt_id=jd_vMd4ndXc5Sv6NPj; sid=3866ebbd6cd1c9ca93f4cbaf039be3aw'
    # ck = '__jdv=76161171|direct|-|none|-|1655119788712; __jdu=1655119788709304160315; areaId=24; ipLoc-djd=24-2155-0-0; TrackID=1QwxwvVuB0MNeMux5D22UXS8_1NyzanFJCLEaYmBlxmWwcDK2vNjgW045R5iUaO0EEsIH9HH5e1mAZmpQG_Jrx_72AVRVnHseFnH292UQEvE; thor=EB7FE7B4B9421540CD01AF0A5C6078519C039791EC2AA1F3C564EBF831AD1F99D4F6A7809468BEC3A9B9033A3935E8F20D155344D7222C87FCDF9DE0B82E7B789FE132E4417C227AA40AC6D4BC6668E505AD885BC9C79FDAE742C723CF0090DE8D0B6AB8BFABF2B1B96D43E7DF02FFD214FA54DE17835A9CA62093D5B2D42CA8B5304D79E08085C90D3B2B0E4B6604E1D5F869935D4955D090B71EE52C5589EA; pinId=XbaKKym0jS5zi-kUilP_irV9-x-f3wj7; pin=jd_5a256a9e9558b; unick=jd_5a256a9e9558b; ceshi3.com=000; _tp=wcR6+Q0yRPrU4122bZ5VKhfyeLyoi6jiaX+JwcCX2Fk=; _pst=jd_5a256a9e9558b; __jdc=76161171; __jda=76161171.1655119788709304160315.1655119789.1655119789.1655119789.1; __jdb=76161171.4.1655119788709304160315|1.1655119789; shshshfp=d65adcf8131fbb129c4917e40b9c431f; shshshfpa=92c08747-6a6c-c18c-845a-2718da668fa5-1655119811; shshshsID=f1127af74498f66b1e815a929ea5ce76_1_1655119811914; 3AB9D23F7A4B3C9B=KR22YY5JONUFP2V5SPMYPVSIWJOIWGQTSQZOVV4QZZUYZVAWSK7JDUR6EHERP6MUSU46OHFT2CZWJM7TCMG4OTHUCA; shshshfpb=xphTdPvLos5qApv29mJ8clw; cn=0; user-key=842f5936-7717-44a3-b985-65a832a69d2c; cart-main=xx'
    # test_order_appstore(ck, '123', '100')
    # proxy = getip_uncheck()
    # print(create_order_appstore(ck, '123', '100', proxy))
    # query_order(ck, '247775877802')
    # ck = 'mp=jd_7b6b4d6d0b4bc;  TrackID=1DjmxNpT0-fhXrbiDae866h10Dw_YR_ndeHFrLYklqIYEAlKEe1qDXEiNK4e8qi6nQu0tQdXDR5xm7XSyfmpjG_BDY6SR21zzRVdthYV3hOwNF5Ey3Oec0wDybn0JQYfWd1jz0ABzT2-NYHoz8ugHGw;  thor=E7E196E8A12A5CE173405235B9239BDA4C5EFE63D32FC15163BC2AE71D121CC7119E66CC99578FFD3EF0F449F1F9567B222BBA817A78DE0C67F14BDB1BF28A01649351AF29E6F3A150599EA68B0820506FB0DE4E544E88310A9CAFF820246C781F29D88F29258C793EA262646B75FFE765E15EE1AD6F3A4EE95C74C304A69658C404DA5744C7F66D7291967F19C647C896EE8DC248118B1DE2550E99C1549568;  pinId=SBr-25ouTZE_8n6hcfrbebV9-x-f3wj7;  pin=jd_7b6b4d6d0b4bc;  unick=jd_7b6b4d6d0b4bc;  _tp=iNluJKUSrG9Estty85fNU%2B70gQrhhPR47VpXn6whI9Y%3D;  _pst=jd_7b6b4d6d0b4bc; pin=jd_7b6b4d6d0b4bc; wskey=AAJiik9kAEBdr2TwInWTnN3Jipm_5cfQmeC9WGnkbrVkScACgyTBgrwkXbooQBbKpIR1UjE4gEwR8ltRD-Pu4c9nFQHpIDAC; pt_pin=jd_7b6b4d6d0b4bc; pt_key=AAJiik9lADCZ4B4g_7nme68g60_4QSEX-9yBJJk2cXW0aGAA8MhC4sCnKyVsKW50XApcjrIlMJ4; unionwsws={"devicefinger":"eidAbcb4812178sbg2crCUSyRlSY7J3VMNsceINnLIow+GfKPl8Q/s4aF200XmwBM9SLz0lNiTCG6Q5SjOWe2wAfRNFNh1+EObxi1jKrfb/sVkNoz1Ra","jmafinger":"lhd7wQWZNVefTprrDLTR3toDMe10RpaIFbIkscMU7CgR7PyQrRbHHeUDhiatJeqQf"}'
    ck = '__jdu=16509706855941893098380; __jdv=76161171|direct|-|none|-|1654941522932; areaId=21; shshshfpa=24b6bb36-e2eb-935b-8da5-4244c2284385-1654941526; shshshfpb=zgH442FN956xyfHqjr4f9ag; TrackID=1m6fmJ08yeZiFC_4GezQ9QMoQQ_QLI2PQkVg0KK_NngpOSm72nMGIO0uGbmdBJeVuX1QYELzBb5jlo-aKY0HTOIqoN8ARK3s3DN5iHRU4b0NehczkKZwLAWwN39rfmbSFGKouBmDGu34FYBind1B_5w; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d%2BSKBX0iW%2BQy5xFBy0C7MU1%2BoxmN9c%3D; _pst=jd_4d9b500034155; user-key=b713e0dc-ea97-4f4b-8edb-4e1a16076df9; token=2415f697843ce67270befb8623ea479e,3,919548; __tk=qUGDrLvgriS4qUa3OLKisIrdriTfqI2AqLS3sLSANIu,3,919548; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A745D6D68C5F25C91A097657B5245B48C0998007BE001C8E944803D9D0670878FD5D306D8B2CA5BB7D8EE05CEEEE5D622E9798178E7D592609FC07835F93A2E04490477306F40973B88DF7E5848C7CAE43F96A32434E7C798C2CB9DE33180D16CE678A7F1F19AA946DDCB641F01BE81FBB193F91205641FF365333030BF8AFFB5D10; shshshfp=3ec2e38aeaef87232e6d74b5de7d50b5; ip_cityCode=1827; ipLoc-djd=5-142-157-42800.8254666397; ipLocation=%u6cb3%u5317; shshshsID=d072f2ec16c36f28368943ba2c97b84b_5_1655186733936; cn=0; _distM=248541400941; __jda=122270672.16509706855941893098380.1650970686.1655183467.1655185920.6; __jdb=122270672.17.16509706855941893098380|6.1655185920; __jdc=122270672; 3AB9D23F7A4B3C9B=L4VA3H3XRQXTHOSQML6VS3B7QYYN7GVIBS2KPYED4PB7WAMMO52MPHRJZLNNWXPSPTBNDJOKGTPD7SIYJTCJZFPFE4'
    ck = 'mp=jd_7b6b4d6d0b4bc;  TrackID=1vN4FH6zMhiQVuVxhYz58lTYTVkHiZyPRqTAHY3Ea-fwGWri0FYVTGv10VUCvXaX0dA5S39PcbF113un8NPeOHzXHwIvT88-Uax4bKeFSJdbHgwoD6Gzu0sFGqmFqjofRshWfS-RJ5eLjnVfPme152g;  thor=E7E196E8A12A5CE173405235B9239BDA4C5EFE63D32FC15163BC2AE71D121CC7C871D4390F7718332F9F1DC201A5FE3F548D608FE276529CC728805AAD8EAEA47B2D574F8F039D4895E039000EAA74623413FC1A8EB76DB38E54522D89BADA03CA56F04E9E594102539DAE1D551FE808B5DA6CD70591125E04F086DE519E56C5079850FFBB336446C5520082080A509945CDD9341BF0B6CCA47E55A9C4CDF95A;  pinId=SBr-25ouTZE_8n6hcfrbebV9-x-f3wj7;  pin=jd_7b6b4d6d0b4bc;  unick=jd_7b6b4d6d0b4bc;  _tp=iNluJKUSrG9Estty85fNU%2B70gQrhhPR47VpXn6whI9Y%3D;  _pst=jd_7b6b4d6d0b4bc; pin=jd_7b6b4d6d0b4bc; wskey=AAJiik9kAEBdr2TwInWTnN3Jipm_5cfQmeC9WGnkbrVkScACgyTBgrwkXbooQBbKpIR1UjE4gEwR8ltRD-Pu4c9nFQHpIDAC; pt_pin=jd_7b6b4d6d0b4bc; pt_key=AAJiik9lADCZ4B4g_7nme68g60_4QSEX-9yBJJk2cXW0aGAA8MhC4sCnKyVsKW50XApcjrIlMJ4; unionwsws={"devicefinger":"eidAbcb4812178sbg2crCUSyRlSY7J3VMNsceINnLIow+GfKPl8Q/s4aF200XmwBM9SLz0lNiTCG6Q5SjOWe2wAfRNFNh1+EObxi1jKrfb/sVkNoz1Ra","jmafinger":"lhd7wQWZNVefTprrDLTR3toDMe10RpaIFbIkscMU7CgR7PyQrRbHHeUDhiatJeqQf"}'
    ck = 'mp=jd_7b6b4d6d0b4bc;  TrackID=1vN4FH6zMhiQVuVxhYz58lTYTVkHiZyPRqTAHY3Ea-fwGWri0FYVTGv10VUCvXaX0dA5S39PcbF113un8NPeOHzXHwIvT88-Uax4bKeFSJdbHgwoD6Gzu0sFGqmFqjofRshWfS-RJ5eLjnVfPme152g;  thor=E7E196E8A12A5CE173405235B9239BDA4C5EFE63D32FC15163BC2AE71D121CC7C871D4390F7718332F9F1DC201A5FE3F548D608FE276529CC728805AAD8EAEA47B2D574F8F039D4895E039000EAA74623413FC1A8EB76DB38E54522D89BADA03CA56F04E9E594102539DAE1D551FE808B5DA6CD70591125E04F086DE519E56C5079850FFBB336446C5520082080A509945CDD9341BF0B6CCA47E55A9C4CDF95A;  pinId=SBr-25ouTZE_8n6hcfrbebV9-x-f3wj7;  pin=jd_7b6b4d6d0b4bc;  unick=jd_7b6b4d6d0b4bc;  _tp=iNluJKUSrG9Estty85fNU%2B70gQrhhPR47VpXn6whI9Y%3D;  _pst=jd_7b6b4d6d0b4bc; '
    ck = 'mp=%E5%B9%B4%E7%82%B9%E6%96%AF%E8%B1%AA;  TrackID=17gjbbJ8vIl4p7EwuQDBWOOCP6OINSHzETHKZgvKs_VFXPFuTdkEzLgAt3yJUcdD4K1cUb41MQuoXmzv6mCyvx7OczOVU2tfSKsjdcENyOmL92kqDvI9FotWwdWuW3ifl;  thor=1399188F58298572C9D38E1B6F69C9476099357670C553A028CD05BBD7CE1723751316886B43B3B5A44E454A21C8A1D5B7AB1717FF77A668B2F535CC3DF0F55B445F30DB1B62EC251F42F6FEC1BBE0B6664BAF8E0E921759D0C084FD5082464AE74B24F9306532460959DDB39ACDFD4104E062045C04EAC3872005CF9753D933;  pinId=HmAV0Gvao7XabKKrewWsaw;  pin=%E5%B9%B4%E7%82%B9%E6%96%AF%E8%B1%AA;  unick=%E5%B9%B4%E7%82%B9%E6%96%AF%E8%B1%AA;  _tp=IfrgA2pjrV2k4Mr7l5Jr1qfRO%2BoKGdHtlxmAm7pWGP1BncOmJsCxlS5ke4Dk1W%2Bm;  _pst=%E5%B9%B4%E7%82%B9%E6%96%AF%E8%B1%AA; pin=%E5%B9%B4%E7%82%B9%E6%96%AF%E8%B1%AA; wskey=AAJiNgAUAEDtcEv5CtGkS3vuoMnJhuUTlKizeQnOqMfTLz_yJHDwVnQkmf60S-moPK-4aw-4yUFOwG9HFrx-PiCSKiKdM_ul;'
    ck = 'mp=%E5%93%B2%E4%BA%AE%E8%B0%A6%E8%89%B3;  TrackID=1MgshfXxaqylqZ-Hys7oVs2S38IBSKnh15au72uqd8tO7dIOys67iSLqUXogz3vpJ2fa9lwqf2PreWHY0GpRhlCse7JIe8vKKUjEyyVWaN4_DJeH-O6wPwpzye2K6qkbx;  thor=F3D526CDD9A796FEF7A07B711EF9F54F0ECEFA6D749C306FC779EE39DBD3BB0A3F7485F103A488EFEB57A00ED18230EBA69C74241D7BD67BA200426F5CA18BF254BB3757B109DC5E417E6B4D9F2C2E39040FA879D557ECB085D7BB17BF5D2BC8B7C69BDABDC767DC426C0EA7A2C1BE33FDC4305C8FEE5D1677AFE1DC1B2AAFDB;  pinId=9Mmx2To6b3U1ekxGPHZQpw;  pin=%E5%93%B2%E4%BA%AE%E8%B0%A6%E8%89%B3;  unick=jd_dkPcherrdmyM;  _tp=pPAYftXvf8oEeOUYyxCPKWyfW9vnwj%2F7lbrnMv9Yd7vKQM65Zy4KUs8roYIxs6gt;  _pst=%E5%93%B2%E4%BA%AE%E8%B0%A6%E8%89%B3; pin=%E5%93%B2%E4%BA%AE%E8%B0%A6%E8%89%B3; wskey=AAJiNgAvAEClEOCgplhUiLwQqUvYiFvBQ0aXD_zGSMNFCwyWRvrNBFH059Z1E7N9E8NOU0yOwJNGQdEa7PfKVVcL5ZyTuBpb;'
    ck = 'mp=%E8%BF%90%E7%8E%89%E7%A7%80%E5%A8%9F;  TrackID=1ki0BMvkLXAMDkc2YlHD6FJfGIqx8nOOeU6s4NNiaPsOqU_2gzG0MaAu64e9cNbHwGFAiZXLrEZmlFB_G-rFocHNeG3iYVEMyNpe4vq3mXg6P5edKf6SqkMCcvXTWXuqG;  thor=CFF6635A5B25F28359797681B34C4ABFB3CF7C40972D63771EF7A06CA6DF77AA696535227EFC6295CD77E6B7ADEC33774E14DE23BB1F89E73CCF82D0D793B0152998E88DBA3E0A68CA684A3F0C92A3DEC09702928F09A88C75742CC1A077DB42B5ED12E55EF1B825D7FB578A200EB1B2F3FFC3DDD186117DC90AB24000166777;  pinId=KJzsK3Homa3DYPghib9SOA;  pin=%E8%BF%90%E7%8E%89%E7%A7%80%E5%A8%9F;  unick=%E8%BF%90%E7%8E%89%E7%A7%80%E5%A8%9F;  _tp=kmp3mT3%2FC54jZ17fuFE%2Bqp9mnjG%2BJ2Jm60SY6OhXl5ZnYlQoaIglugRX3J%2FmTjAj;  _pst=%E8%BF%90%E7%8E%89%E7%A7%80%E5%A8%9F; pin=%E8%BF%90%E7%8E%89%E7%A7%80%E5%A8%9F; wskey=AAJiNgApAEAdH_4HEI5FJoxj3CIZcWsiH8jKienGQiNEsfWWlzAITbFWPK1zD3FkVhgZ2NyQgai8pOtbJy1BZ_8OC-K2q9pb;'
    ck = 'mp=jd_m3nGd7xgKCzs;  TrackID=1Os1rJsJzGwM2STUb3qSxVETUC5O4AlPgo4_Tsh8Fn7GOmzYxY8L6p9VnZa8opuynnhBV2ovQqGOaY3LFp-zErkOuyfBNJsHqJ5QfWNsY6HN1ReJdvub2Le-wWNoABi8s;  thor=6E8DEC652A4676163A1B523A4B7B7B7EF30085ABA63000AA27FD0F23AC14BE103B52EC0AA08280DF5294CE4B9BFAA3C4FE75A096660716985F3C8FB5BC69C21B495941E81398F3C0F6F4A4C541EF7A3D7E0C7A726ECDC7BBF0E7C4E1AFF571A58995EEAAB5CAFC808BAD755890BF9F512BAA34946C2D3EC6E081D7C66782A93F6DC6CBC1C5349058BFBA6509FC4DD9559F49B8469E4328F24303B6AA7F22F5B8;  pinId=6HXteTwr9Qb1LYurdjJNng;  pin=jd_m3nGd7xgKCzs;  unick=jd_m3nGd7xgKCzs;  _tp=NsJnOpzBAeJ3d%2BXmRqHjkw%3D%3D;  _pst=jd_m3nGd7xgKCzs; guid=47de2fb25294f66142674a6a29785e98daa924467b3f9e1d5349df39d4bbcf35; pt_key=app_openAAJiqtmqADAjTH2ShkBeaq1qCjaVdcv4U7ngsnVuzz71w3-Q_XuHNRV9r3PHEoaf3bxFTxiJv6o; pt_pin=jd_m3nGd7xgKCzs; pwdt_id=jd_m3nGd7xgKCzs; sid=e03a86472146848d71be27a4eabe79aw; pin=jd_m3nGd7xgKCzs; wskey=AAJiaOSmAECT_6zUtAs0lauy9irIqLgbIZfF85X6Sow1jOgLUrbPyaJUqc2F7dU-nnC3kKWZz1uWHTQz0ZSjigQeigjzkDj0;'
    ck = 'mp=hyNKLtrfOSvJZlvT;  TrackID=1b0OeOd131fF1DgQlaoHWHdEyg_ETS1pIFj-4iH0SpEPWS7oN3vJ1AqwWdLAwtCOpGDo3IGd3my1RPsrakAD0IARW2pBNfD4T_o8ClH2jFCa474tPtqxdh453rHuIkVfuxOgSRnSVopg7r6rFcpFDcA;  thor=3D5D80D9E1771340289901AC9ED2ACB39A937652306726C6CBE237370A1C7D6F760045F310089522D4B64E9A6FD75A2A83D65B53AC41F70D7D96C0640D53702B3F49F402CA65997832EC276BA42F01E57CD41357423AE57C479E5BB557470BFC3F101FBF5CBCCBC4D459A1AA6C463FD85B48C4322A33D2D0FE52FBAB2E676EDA8149070B40B7D49603364BEC013405EEF1899FD8D7E46F5447CFF353EB3FDE68;  pinId=-Pm6Exjw9d_952BeeNBtTrV9-x-f3wj7;  pin=hyNKLtrfOSvJZlvT;  unick=hyNKLtrfOSvJZlvT;  _tp=JSk2JfzZKZHjpGtWnyPZC%2BP8CQNJpLc4eMYzZ5c2P5k%3D;  _pst=hyNKLtrfOSvJZlvT; pin=hyNKLtrfOSvJZlvT; wskey=AAJiquBEAEBLM0U9tBsVwT4wkQVlLAdG288wSxTS9-7yx0vgvtBoQbiFF_8n1vBGGTaTVZdW8HMAblYZf2oW90NybiJfltuo; pt_pin=hyNKLtrfOSvJZlvT; pt_key=AAJiquBFADBdM_UIAyZ5NpCxG555h5WqSGHgCSVE0JlTUjJd9VvgwKKH60I3byzy8SL0O7r9CJk; unionwsws={"devicefinger":"eidAfbe081222fs1TauHdCJySK2MdUY7hB1ViU2riPWN7lgyWPsl5tqMMJYvrgPrDNQiZzdp8ge8kbu0P0Qta1LGMbl3dGdu5CsHiN16QE6qTGkJQt41","jmafinger":"u78g6vCOD_Ee44JWI_MWDJahLrZrDSWeWvDqcmOgZFP_E8MOx42-MdjNxxf5bwet4"}'
    ck = 'mp=5Y19QlPSdXZ0nIu;  TrackID=1QL70vtTuDzaff0BPWGd0OpZVyWDNrXcgfz31IGHXKSXWRczi8t7adk1tmEFF_XfkKnj-ctkN-l7WNIV_mP0WJ9xIjDwyRu7b02SkXzRzzppHd6BKR-DyI68m2y4av_8A;  thor=BCAC54CC1B2315EF1495D93A1A6B2AF16A64EE5056763C14D6A4E2C349C648648508F87F1F1385AD10642ED278CA4FD97350BAAC03C91E4C33E58DF5E577B76B5DBB0EF8E2F873F3A0F6BB31A0AAD2E730E9B83730946DD65A610F62637F4278640E199A418F8CB958057B50265975602FD575824E5BBC5904DBF9C11C31F57AC31CBB04022D18F17C8F8B20EDD50D8012DB02A5F07A91A84C33FDF94B24A13A;  pinId=NZ3IDQW-M5PMvYCv7PWLSg;  pin=5Y19QlPSdXZ0nIu;  unick=5Y19QlPSdXZ0nIu;  _tp=yhaAyCLYMqnbTcc7MKbWXg%3D%3D;  _pst=5Y19QlPSdXZ0nIu; pin=5Y19QlPSdXZ0nIu; wskey=AAJiqueFAED66ZZIzs23Uaeetyp1HmjkuVbcdh4o-AhCiRsobhQeq3-ILeE_q1XqnLRAfFmNXms4BgNv6mPF0L7NTEqQpRPb; pt_pin=5Y19QlPSdXZ0nIu; pt_key=AAJiqueGADDmv8gPRlz6fbvijF9fC_1vKU5wGyApUV4e_DM3tdXMV8_NjpDIlF6uDw1nHlQf0t4; unionwsws={"devicefinger":"eidAb6118120e8s2y+T2+gulRo2IXV6QVO1Xdsvk+Ht3PaoVXKrIKqZHRoUIDZ1SnE1492NmwThRnGlyP4aU97un2an/rxyNNlL77HR/NFgt0J4P0s54","jmafinger":"uFBrLn2iUVIoFlm5uzlBTlra9OJOOQ7g6mPvCJ5f-9LMEbPrXpAxVQuW4w1tlSFU-"}'
    ck = 'mp=6Cnt0GbbD6wk5Rhs;  TrackID=1cgWdCphf4L3jycWmvvre9-HxVPpMnkERbeAjjEZxIvUD6YpQ57rAxAi5OeBGzAPTghQf5BI0px2fAj5fKU0rXELPVmj1Y--gfI20pCZVEZs6AXOlu_Fc22QlTSgs_chfVlj0AAW76CySWB8cS7P98g;  thor=F77F2697EEA9013258569999A09E88568860EEF1E44F13AFFDF20E17CF3E1BC7142252C20C713CF0A90E9FBB1458D6D45815FC8981257AB84D0CA187C59D9FE9DE9BC7B05D2B12416B994B9E05721D048A926F98DF9C2C44FE2D135500326F31771615DB5E45F61D919DA1E1A27AD43E67B3C4ADFE81C7B2F62194145BDA841180A1F346013ACD0963CAA44FB1F1AAB1DD8ABB3A620780CCAFE792C6A7E8BB04;  pinId=UixK-Pp5gDAjFXDxmCUQlbV9-x-f3wj7;  pin=6Cnt0GbbD6wk5Rhs;  unick=6Cnt0GbbD6wk5Rhs;  _tp=oDXBNisvkejUWmKrVYdC%2B973VGtFXqn%2FHJ1evp5ztAY%3D;  _pst=6Cnt0GbbD6wk5Rhs; pin=6Cnt0GbbD6wk5Rhs; wskey=AAJiqueHAEDccOwphedKIwEqVpWqwJOgIEzbV-Cy_TQJHtiQEb4xAGBimt6M8q-ATfQYahLkknEjmXVgPyrwgtbkp4TEVyCJ; pt_pin=6Cnt0GbbD6wk5Rhs; pt_key=AAJiqueIADC7D-Sb9T2FV49J6jMqQuICmxh4bbZzUR3j2eotJrRKImRQUtl_Xt01c9R--TFkGg0; unionwsws={"devicefinger":"eidAdaad81221es5r6aIG/fmQCWNl6U8zFCuBa+miZ1jfqoahB/yLPrkz8WVa/++yVrwIE5yTMCBzcRMy7vtR3S6qZUY3mEjb1UjdQnrzKE50DyOL7Rm","jmafinger":"txvFM4Atjgrxdp1_9gi2EXVy_FbfbBja7ciSg_J7gqqrfa8tiOzL9TsxBYADKlalv"}'
    ck = 'mp=v7oa6k6IbP6oMqtl;  TrackID=1TRcTGEtn2ugSMS-qE_5L7dm8C0pSeMYeyIF6r57OWlOQ8NPwW41BIAs9rXQ1nnjHbjP3ZinwS0uA4FaT0K4vkcmd9SAlhoSaqtpzme4JPO5QKxkWV0GNx3GAdaCKb7irD4OgdNe0g4kc2CynE4a-qQ;  thor=F07063810DA4A567758850DC728CDF9A7139506B3E3051584654336D8B5BAE4AF637C53D7CEA87267A0501E14EC93860723582F4BB6D4959F56EC84A852DDC59B87B0455905DBA1699F7BE0EB3497B4F4FD8CA4CD4E10B65D72EEB7984BDF32E4D445E21634DB606DF736FDF25DC7C6575D92B4384A51D7DDC754BBF1E29DB7ACA18B218C2229173CF91BD73C02F3B8272FDAE34DBA11A09A5A1B16FB7582EB5;  pinId=wKJIH4y-2pSDr_INFU3cKLV9-x-f3wj7;  pin=v7oa6k6IbP6oMqtl;  unick=v7oa6k6IbP6oMqtl;  _tp=ARbkT1Y1lxaRdrqEk%2BLDe%2B9eLT3Fga6w%2F4uheJ4f98Y%3D;  _pst=v7oa6k6IbP6oMqtl;'

    ck = 'mp=0iF0ltaFDhB2UEy;  TrackID=1ifVwgFuEHKDm7GPQsANXXIHPWmu6omszt2CMHIWHFoGnuckeoG9RK_L-vObTs1qUoYLYDlcWfbKUVwPYnXegaG5EVd0CzJlpAxnJXI_rxcIS3n6KHvAfwjc0hvcU9VGW;  thor=0235A054F38AF2CFEB29F02C16F451469A1A2242E708EB4FAC6E20C55A73DA48CD4DDFA602B9A5586E1B39C12E0F60D35F85ADC9D7A680F96E765DC930017A74CFEFAC929091D64BD8B256C032E01597A1CFD3DC10BBC120D65751A01AD885C85EC091902B2711F8C9D2A35D35B597354473DBCFE62264725B509A306CBA26EB86C982598833474FE32BC13A97CE244A1CD1B12991FC992B5BA9DA28A72D839A;  pinId=PY0BkauJudJ5KMWm-cttcw;  pin=0iF0ltaFDhB2UEy;  unick=0iF0ltaFDhB2UEy;  _tp=vjgGkqF7zfTtaNereOCDzA%3D%3D;  _pst=0iF0ltaFDhB2UEy; '
    ck = 'mp=v7oa6k6IbP6oMqtl;  TrackID=1TRcTGEtn2ugSMS-qE_5L7dm8C0pSeMYeyIF6r57OWlOQ8NPwW41BIAs9rXQ1nnjHbjP3ZinwS0uA4FaT0K4vkcmd9SAlhoSaqtpzme4JPO5QKxkWV0GNx3GAdaCKb7irD4OgdNe0g4kc2CynE4a-qQ;  thor=F07063810DA4A567758850DC728CDF9A7139506B3E3051584654336D8B5BAE4AF637C53D7CEA87267A0501E14EC93860723582F4BB6D4959F56EC84A852DDC59B87B0455905DBA1699F7BE0EB3497B4F4FD8CA4CD4E10B65D72EEB7984BDF32E4D445E21634DB606DF736FDF25DC7C6575D92B4384A51D7DDC754BBF1E29DB7ACA18B218C2229173CF91BD73C02F3B8272FDAE34DBA11A09A5A1B16FB7582EB5;  pinId=wKJIH4y-2pSDr_INFU3cKLV9-x-f3wj7;  pin=v7oa6k6IbP6oMqtl;  unick=v7oa6k6IbP6oMqtl;  _tp=ARbkT1Y1lxaRdrqEk%2BLDe%2B9eLT3Fga6w%2F4uheJ4f98Y%3D;  _pst=v7oa6k6IbP6oMqtl;'
    ck = 'mp=N04CaREvkvIouigH;  TrackID=1Ku8OfpeMkIyPpHeRwhuRUtty57ITAwa0p2geQ_t3M09h3tA714b621PgUEXy1F8HZ84K9KcZ-ZLMY7P2btBBzlDrMKHrPhHG3Q04X-woF6hAKS-1PiDQqfZXGRh3dXF0ZV0RV71kTxdMH3zy7djULA;  thor=8752EC62841B81BD3B209D5467F80E7FEBF8DB24ABDFC07E1CE3259306EF595D6F1FDAC911EFD99F0932D4B18EAC2129D29063CE4DEAF071B8F864DE2232E7919F4123924BCF8B6FC6DE8CE8D1FD8363803D3805BBBA0C33FA27EB96DB507FEEFFF071B9644A780C84586C1C2718CD54EA0FB8627BA679F6E2CCA07EE4E30ADA3768AF7A90F45FB6DC5D6F1848071F81312AE732A8A5AB4CF3E66C2F7F4F6F2F;  pinId=n2ypXyomKYgKsMh4bvsnOLV9-x-f3wj7;  pin=N04CaREvkvIouigH;  unick=N04CaREvkvIouigH;  _tp=3%2B7Zkl0uuYPwyBdGCq7zqtGNwuLEeIyM4LBEhZ41fx4%3D;  _pst=N04CaREvkvIouigH; pin=N04CaREvkvIouigH; wskey=AAJiquO8AEDXY-_ko3_HKk3KXSpbhrrTcSZRqE03jwi0yF0a9S5_1kQ2Kp8tyO07oQzctv2tMHzg0KemrcFRF_LL1MhKEo09; pt_pin=N04CaREvkvIouigH; pt_key=AAJiquO9ADDZmV2iAjtd3dpZYeByZIGDe7NP-12TKsIuyuTEokcydwml49Bo-GdD2IXsdrRrP4A; unionwsws={"devicefinger":"eidA295f8122cbsehvPnI9rhQgSi5Q7x1NusRobz6KVGatxk+3tTnxJ6e4r1IBhpayxNBEVVYodNd7BaYR7e0r6vu5cbbpEj9gz6F5E51HvpCGUfJcNX","jmafinger":"tqFkWgV8jCsnGO8IcKdXqk7M4uiAYxs3PS-MZvdBDLwYB_i-IiVNK0wVIw30IxTWa"}'
    ck = 'pin=8hIdWHSGZjAqMhJ; wskey=AAJiqz44AEDYdkVFAEEu-G6-2QFqkkEfrIypeRXjP2AdR3KEnbaaMy0ug-ACGq-78Liy_HGdkBdtB5Zn6pNpUNP7t9FWa8t4; pt_pin=8hIdWHSGZjAqMhJ; pt_key=app_openAAJiqz46ADBgzpX4v8U2q3tFI0CIV4yh8bEsayvpjTgkfRH6ZFbcue9LYdnLJLF5w47t6TUYFS0; unionwsws={"devicefinger":"eidAd96e8121eas6XzWuye4VTvC0RUyK08xv2181sEtbAF3EnytPeXK70rsSYUqIwCvsa09wWasG+LOEKJWQ2DFM6e9NXlvS4bDd+wgPwsZ2uA1yoad2","jmafinger":"oNZezb8HrGmzeuGCEpR4LdTFsm3UXWlzOkQnKoI_4ZJr2ip8yAM2SOtCQHjK5S9c6"}; DeviceSeq=dfd1825fadeb4a889e9f8a272d2b3191; TrackID=18T_2HMW2l5SqQiRbN5M0aZ2jYqCu0XKowQcpU3v78ChGoQEXLnhrQwx0MOcTU0OREiDh4dct0IFZ9oBnqd4VtjjZloVjBZBWylYnnnVfBHY; thor=04BAC086CD93D5FD47B392CB12574E16E9AD2959EDB47C64E1282479F61986D5C05B619EC73D40FB1627B0E649C27D696F50ADB69587E586BCD721A57A90B619C67A6D28A6B6AAE576145AA44C84F8357FC796C4684033D929EB1A84D3FA59D3E2012FF1E492FD81EBA72DF9636147D5D95BCD409AEBF051693CE490B0B3A251F8400B8D50CD38077C8129F2A8D9918791A7F6F25D400ED95A35A485BAB48EFD; pinId=1hI1uxT3jeOkBbbjZjDJRw; unick=8hIdWHSGZjAqMhJ; ceshi3.com=000; _tp=mFP36iYd%2BpcELZ2E02A32g%3D%3D; logining=1; _pst=8hIdWHSGZjAqMhJ; guid=1497d3eec1d6e2f4b3dfdd485b0abdbc5c9c30ef8401106ad366e67e1e6e5714; pwdt_id=8hIdWHSGZjAqMhJ; sid=38d97be301f9cf078954d79c973c1d9w'
    # true
    ck = 'mp=jd_74fb50fd9b6b2;  TrackID=1Z7mcUIQjoG9wJkP5rDYvPSosmWE8yprnbQRPLqbbxzWrBWzlHMAQeUVcsGI6-4NnAY6LlNPcNxQhgsNH4HHtHh4Q7ntB97pb2NViTbqlN1TwVbu3cEh06M0aT45W-IyeC1lYaulBmJ1TjOE1DyRCKg;  thor=50F30A27D539B5D32A91FCBA5AED4EDB685624C8FE6B951C74A3E01042C0CB9ECDE7C7051A72A3E82DB3B37550279BF0B8CA07A73AEE190AFC7F051FBCB93CC97A41FCCBA7D0776486A223ABF852FC34A3F29F430B5253CDE24FBF4D111D0F3D0BEF9F9429505B513A8962C21AD4CA9F682F2E1CD372E59F622D14DBC55E7901F2347E45FA8951C9F2593251CA3CCFF57DABA27E7492D926DB9B730E10192DD5;  pinId=cwxM7dEAJq8O8obCeoreELV9-x-f3wj7;  pin=jd_74fb50fd9b6b2;  unick=jd_171936xzt;  _tp=7sX82QmJsUZpfU%2BHkXGhyNlrONuu6qAyaaRlmUai2js%3D;  _pst=jd_74fb50fd9b6b2; '
    ck = 'mp=jd_7d1c1d0d7c8c6;  TrackID=1AGmN_CLM039p7vDsL3kFhIUZ7Uom_-GLHLQXlCQyq8I6LqpI5o7dhCinK_0du8UPVq6q9Qjt2kRrYVjZqexOVr3o_XNiRGh88oaToEO7xNCU3r49zHqdfxUUNZs15AQgfiwTdqCGWtZTA60AmViXmw;  thor=C040A6072512C96C41CDAD4EEADE30C75753322AE1EAD2D97DB28C7F1B0B21525D0181A432CA2DE801182E48C205E20CA5950973236F1FA6E658DA82B105BBF3B7AC6ABE558AAA8651A357F8435D3E064F1D176A7E092F366378683E33BD8DEA78E6FF6335E5B9838BF8E6573F92278529A5DCCFE18F7F71A7B88AA53379706DCE39481AFA4E19BD45CAE68EE8F8815568D4715927F996A33FB537934D245AFD;  pinId=JItSfozO-dmoVpKnpZjJj7V9-x-f3wj7;  pin=jd_7d1c1d0d7c8c6;  unick=jd_7d1c1d0d7c8c6;  _tp=VAH00k1KlTDwOG56Me8R0oQqV9WRC9xJoiZ9wCU1G4Q%3D;  _pst=jd_7d1c1d0d7c8c6;'
    ck = 'pin=sgsr77; wskey=AAJiq4NsAEClXI1qecynmmJHOasKwnlkEHPbbOrK3DIEfVuVREUqo4WHauIGmPRLj5iS76kbeNypoUN9P4l2Sang8dvxqiDA; pt_pin=sgsr77; pt_key=app_openAAJiq4NuADCbLOeJKRYeyIKwaD4Np9WHJ35_aMOFLUtNu2_l9ZWvGfCH6WkDch4T8ByPBlmBW_s; unionwsws={"devicefinger":"eidAd43b812112seTuotYW0cTB+s4mPJet/Cl07qLuLbFa9teCCgQP7tmDgCywF2aWDHr3lw8lE9adb4X2pAnCYK5C8d96OO2DJNCR2bHP8AOvjR0uJv","jmafinger":"sNFZ0WE6Jn2xQG50dhNuhlNqBgGFZ1ZeqsjjzncS8DbVfmTJjyaXPIxa-qXKWpYhv"}; DeviceSeq=580d2efb669546449f27934b652b412d; TrackID=1MYYG76jAvHqxYJwAK6_nxCaXzh28SiWRA1Ut3wykSdB3K8GvUpqwGdos7h5aLBcGh1aVPyLa7seV_FfcY999bQ; thor=3619E1CA1EB15C2CE50479B18EE952195639AEAA4182409635C84597D1DB662E25F2BA8403997921C6C5101501BF0B49F366F1535E91F478E088C3A5AA0930CF5161EF5B9BD5832629CC009E1A567A68B365B6533CA95FC236BC8BBA1BE08355BB9C22A00E44635837BD26ECB30C3AC8DB253DDEE738BE3D36ADD840E76C9CBF; pinId=nxSaUzC0P2A; unick=sgsr77; ceshi3.com=000; _tp=I6I0dMyoYzoyZIG7ifjO%2Bw%3D%3D; logining=1; _pst=sgsr77; guid=72f94d4c8971e044dc821596f0a1827218b33b4445d8e5ff96b1fa582f1aab81; pwdt_id=sgsr77; sid=9d8d56ed0980b532e5df3dd9faa716cw'
    ck = 'pin=jd_tFdNtEmFsSxV; wskey=AAJirCWGAEBnQXf3-i1SFpstQeRvosIxUYYM_Chhfy14whZcOJOoQ21GylAN646mRVf32-9NpYQ--UYBrgDxoffscGkGdGow; pt_pin=jd_tFdNtEmFsSxV; pt_key=app_openAAJirCWJADAs5WF2HTysuNSFO-ZMTbldUSl2ZcKtiCTCQrKEf_e3IoH_xfghzUD0DHB5EOsPKZ8; unionwsws={"devicefinger":"eidAfe4b8122b1sf1ltNfMWFSayRq49k/1djsdZbTv419+M9LKApxVr8wwqYmaY1eAB6HkFQzxq+WRWstb8CwplZoDFOp2gdNLrdcFSCSlgM9fGb4NlB","jmafinger":"vBbKf0Bf5Z2dmPVhaJ__N35e3M2wWLjdS6vwXV5jAUcoSnnbjGK9-yf_LSp-n-FYV"}; DeviceSeq=c366cd66a12c42a28d7add40151b51f9; TrackID=1Kw4XMPOy4Q9MaRmSGs4mhBKfNbDgbqJ1Xkv4QGztnL6fmzkvrgcOySN46hK9UEmsJ6GOd8CqJtpfj5h2fC6NOWHXfKWxxwmOwhO4jkeCwYE; thor=89EF236FCB771CB2826B8CB2C3D1FE163FF6C658CB2D15CECBA39182275F349AEC9A4EABA6D6E11B0E44EF28EA0189542918B86C29FE1A42DE738237F718EA8C77E001A5E6ACC04AA0A02F54CC9C78ED855547ADA214800E64E80E8264E98F22DB0A4D4218503C281922789B4F139ABADD686CFC71E86EE5407F0625DD9097AC8B3F73015000A7199C37C993A92B22EBCBA3C11E09A5F3612519948B0A27BDED; pinId=VbOMHzNrjHLypslR2V8nLQ; unick'
    ck = 'mba_muid=16553973626421230428730.1.1655397526163; mba_sid=1.14; __jda=122270672.16553974852471650173590.1655397485.1655397485.1655397485.1; __jdb=122270672.3.16553974852471650173590|1.1655397485; __jdv=122270672%7Cappstore%7Ct_2018512525_appstore%7Ctuiguang%7C50965_0_apple_0_0%7C1655397323000; pt_key=app_openAAJiq1yUADCUwyZaB3l8xqEU3dy631KZyzMFayQvpjtS_mGhWsr1QkR4l-ovvKIW54j_dwMpq9A; pt_pin=jd_rBZhqJJPercu; pwdt_id=jd_rBZhqJJPercu; sid=bcae5bd55d77a02d027adc8a7393245w; abtest=20220617003844648_17; jcap_dvzw_fp=5OWHjTmnC5FqcRvnWwkYuG0lCd3RgH39UZ5G2jl2tmlkYL2565CSbkDpe_JmES_VnHgiqQ=='
    ck = 'pin=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU; wskey=AAJirKsBAFDqkoJnxGdwAnNoctk5_ILxI_8WiDLFGDhkRnpKFFiorpY90yx-HREZuJtamaumlWhjxh1qDG9oiD6zwHH9GnOQrRnI-3iGx8OULGhXXrN53w; pt_pin=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU; unionwsws={"devicefinger":"eidA078c8121e9saZqgb/wsaTNis19ilB0yp3GaoHYB9lk6iMgXaGU6ESMZNcr0zWOpGf1FsqMojL7Ncs5Dtg2ZhfIsluFNc233CH8HPXM9S/n9v5h9T","jmafinger":"dPleoI64xxP-GEaXFTgGAJMnYTByqKwdelf4Pwb0byK3zTu0tC-PeKds3hyhiSrOV"}; guid=08f88e94a2af8728a9fd7884c48340933701ce799d5df14eacaa5c7aa2ff315c; pt_key=app_openAAJirKsEAEBj-aGKN6K0M0o_vxPodqdQ82k8PRUvRiKyaNKK87MIQf2rr7k3gEWmU6M6KyaMX6Ah3ei_DhNihzgpMqPXwzx8; pwdt_id=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU; sid=0386822957a3b67eb07c70c017e9ab4w'
    ck = '__jdv=76161171|direct|-|none|-|1655484084422; __jdu=16554840844201950595880; areaId=18; ipLoc-djd=18-1592-0-0; shshshfpa=2dfcdc4c-0135-654a-93ce-9c3e2194269f-1655484089; shshshfpb=eRm-o5csstbphWGx8mqAnQQ; pinId=LHFLNe7qURaikoLCdEMd1glwgcBe_fXw; pin=埋泉下泥销骨ergJU; unick=埋泉下泥销骨ergJU; _tp=npDmO1ZrnqujVYknCP7+z8ZUtyctNmvNs40En3N4l9CtHjDdaScGXMSlyrcY6NYj7fy6ptxyu+Du6ZznpFyrkw==; _pst=埋泉下泥销骨ergJU; bjd.advert.popup=141c7536c8a06d071364e9423c93baff; shshshfp=9b19408b0719b5707dd639162ad47d0e; shshshsID=0b46e0e95c873d3262d1bcc750319556_2_1655484147317; 3AB9D23F7A4B3C9B=VDJH2HTJ5ATH4X5ZQS5XUDANBC7QAO4VFXYPPUCADBAIUJQQO6NOJ5J5OKK3ZRRIITFWY6V4YBOPZ66FYWNV23LB6Q; wlfstk_smdl=zy5kazz3ac3z6g73dwasxrjxofcs9rr9; TrackID=1TZYJfyfvdCXbB0JYfEtkp8cAhaXK2rv8poah3zS_MJQ8pzgwQIi73wf9vozdsq_AhiiredaYTykABbbgdMZm7Yz0mCAqSBzZjrZrx-cGwUg; thor=AB2F1E8F70BDA565CEC8A17D6360A6C25A9EE43E33F6CA52569155C9451D96F05ED18EA7746C031FC129CE9BC40665BC33D0121C60E9077F201EC1715E4D4A0C5C8F7682E2F517C6BE16FFFF81D8562756A35864A233F85B193967C3DBFBD0E3E0D278914E5820A82C26B22D183F3B76AA55F87DC2D909D9FF3AEED752CDC4EF7A15CBA5B7389345B1487F9F98BA1330; ceshi3.com=000; _distM=248814279744; __jda=24961467.16554840844201950595880.1655484084.1655484084.1655484084.1; __jdc=24961467; qd_ad=-|-|-|-|0; qd_uid=L4IPF8SV-VSA0KV00ENOCX8ZPLOXK; qd_fs=1655485668172; qd_sid=L4IPF8SV-VSA0KV00ENOCX8ZPLOXK-1; qd_sq=1; qd_ls=1655485668172; qd_ts=1655485668172; __jdb=24961467.46.16554840844201950595880|1.1655484084'
    ck = 'mp=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU;  TrackID=1uFmNK39F3ZVIL21i0wYLO9vbEuipwChIdDg-1NoagJGk1uWxCQbisPI8LO2mQB4MdqsVfeGypzWHNza8Te74gtYbvn1dGLhNZAX0kMUf_ADTLTIXLBqLEwyUuB4do9KmBWhDgpzkRtPXkJRBEAi_ag;  thor=AB2F1E8F70BDA565CEC8A17D6360A6C25A9EE43E33F6CA52569155C9451D96F07CCA36D6B51E111F21D5841EB58E0287E6FC5C9AAB66182A36E15FE3DD50A3CA632BAFF0D16D928313DB1146735B6F306616BDA40C34EFCC08E17D0C8F10A15F02DE0DE26114329BC5E62BA4E37F7453D7817285DF8682D72E2CE72E63C230F164343EFF44F9341DB42ADE8803A8B835;  pinId=LHFLNe7qURaikoLCdEMd1glwgcBe_fXw;  pin=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU;  unick=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU;  _tp=npDmO1ZrnqujVYknCP7%2Bz8ZUtyctNmvNs40En3N4l9CtHjDdaScGXMSlyrcY6NYj7fy6ptxyu%2BDu6ZznpFyrkw%3D%3D;  _pst=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU;'
    # ck = 'mp=%E5%93%B2%E4%BA%AC%E8%A7%92%E5%B1%9E;  TrackID=16GTdjcucdt5Y9YnwBvuAtnsYaFtAPpAFmiHqGIRw8Wpc3y7xNoNcwde7yKVWWLkgLePPy4KoWMVVj2AT6Y_LDQ8Mb2iiPlCQzoYcsdBD5daqBhVeXy8ZC63CO9P6H15W;  thor=37A59C924A2C08E74970459B691716ACBFC8955F7B86DCCA512BB903318B539AB1463EBE6F4EE8C0563B4FA84D20B3C637EB4EEAD48580241BE6671E51F5D24ED86E50E7CF5CE43E34D451C4A9FE211331751D30AAFA2EF4280140A6E7E12F4183085074A0B26CFBC42441FCA06A494F68B143EE79AF7DE7F57237A4DF68FB73;  pinId=-y5F8554uzJM_zlVBykaCA;  pin=%E5%93%B2%E4%BA%AC%E8%A7%92%E5%B1%9E;  unick=jd_AXsGdWdYEzYN;  _tp=pPAYftXvf8oEeOUYyxCPKd6lzLP6c5q8fzCUn6O6oEf4K4Vmzdj6dXTX%2BPEkjTC2;  _pst=%E5%93%B2%E4%BA%AC%E8%A7%92%E5%B1%9E; pin=%E5%93%B2%E4%BA%AC%E8%A7%92%E5%B1%9E; wskey=AAJiNgBTAEAW04VNIs2HN1JWQX56ri8BYkyxjOwuDrNfMHI5L5wgEXCqs7YYyqvqUuA3ZYo7D0G7eBd-t6g-tqKXGCpwuJZ-;'
    # ck = 'mp=jd_2JP1idb8rENy;  TrackID=1O1EJN77mbT6D0iBtNTJSz8cTCLPT4OOwMBs9Siswq58P6Wrx5KDwpAbIrgyeDHQqC_5cFhVhsrcZtZTBu8ZQplQ-RiwkidJTEZ-29S6GMFyCsrH29eqZft0ZEA2e2mBv;  thor=C0F263D91A4D1E19A9804DF4F2E60F997812EA92939593B1E2C7BC04EB755BC29612889301B089CDB0E678098A0B202AC47F397E2847748220F74BE94E8740D44857E8A28FECBDCA778AF97B132A689F52653E4A0A6CD39C736AD9DA6723DFBEE44F9CE252040D4145F39EA184D1D236D94FF8796531DD20FBF31F9A7C2F9C6B2B0E1FA9A76B3331E885B4584318244375EE70822DFA52FE3C4C8E4C175C7471;  pinId=lYnqkXDi8DFZie5dNhjmBQ;  pin=jd_2JP1idb8rENy;  unick=jd_2JP1idb8rENy;  _tp=xPPggkJUm5LLLOESRKBm4Q%3D%3D;  _pst=jd_2JP1idb8rENy;  _pst=jd_2JP1idb8rENy; pin=jd_2JP1idb8rENy; wskey=AAJiCFQrAEBsNbLhVc7D5TrXRTlCLfTMMACzyMMIOCjknXYhqsmEmXAxVn1wTIjlFXtZ6fPgUJXP1Wx5b6CsiCydtblLKqSX;'
    # ck = 'mp=hyNKLtrfOSvJZlvT;  TrackID=1Zr6IASL_ZVq6vQ8F4a_u6msuKOTGU9dwY_amlD7SHOdDHLAPyC4UwgGchpoR1Mcbdy8z91q2XuWDdyEvmZ_nh2jY8Mhh9UOU6oi4aIkHhKIcRX7-AzLfRuK8pmjV572ss02vgPAmPrkwK2ysKsutnw;  thor=3D5D80D9E1771340289901AC9ED2ACB39A937652306726C6CBE237370A1C7D6FA41B61E10B20E485B2958C7B2251EE0BD9D3217B233B323FDA48372373F6357390E760896FF040C8B8173DCB918840EA041F0B12C4FBF3CD0C6663BFF92D237193A51A19E4E2C8B1B98A3F28B17525E243717BF45CFC2A51B7B1665B213E12A8F04C4E95BA4C7B5CCD745044C881AA2095A3D848F2B3C3BC1CA9B4859C280C17;  pinId=-Pm6Exjw9d_952BeeNBtTrV9-x-f3wj7;  pin=hyNKLtrfOSvJZlvT;  unick=hyNKLtrfOSvJZlvT;  _tp=JSk2JfzZKZHjpGtWnyPZC%2BP8CQNJpLc4eMYzZ5c2P5k%3D;  _pst=hyNKLtrfOSvJZlvT;'
    # ck = 'mp=jd_2Joor5swMRYn;  TrackID=1iq1VXQXiSAowlh_rLNh7_oh6tdcF15e8JSwcZZPDLSPGtR9JyASisvZnR-2LiAn2RWDN6y1kForpWAWM66gMa46uZ9ZUpwoTCRlvLqD2hcT6NtfIseuaAfr6QCDCYEH4;  thor=69304ABF054FB0B1BFBEDECF4291EA968D5A66608BA7FA8E424C5232587C709BB5347FA5B042E3F2B0D3B2EC2EEF6350C5BCFB3F19B760D86AE52F225366D769C05D4154CC4C449B4FFD1F5619F8A3A3F4D08979D91940B96F9BEC2DE7ACC5C017482C2E6E25FD9A51A489FFD597C7DF561320409A8F614F083BB7ABB59B8042EBDDF22A7C91179A537D6281666FB9520584E1197C44D25464FF8A9E496B8FE9;  pinId=cawvLTW7pPeNiML_J_udSQ;  pin=jd_2Joor5swMRYn;  unick=jd_2Joor5swMRYn;  _tp=GiJrkj%2FLlUjZKFE3QMQyhQ%3D%3D;  _pst=jd_2Joor5swMRYn; pin=jd_2Joor5swMRYn; wskey=AAJiCFQrAEBkfROIoXWOiImtMfnSibP401ulzP-DbPdmq1H9H8jogVAPVRDJUFLI8r-gySbfHIuBCWr15cBPYq8AQEULTUZ6;'
    # ck = 'mp=jd_2Joor5swMRYn;  TrackID=171Bu1zVrDN6jtJ7ybIXi9Yxj8WuJuXCOm5ymqFBjaAUwAwnoleGYbF-037gESQecHSGABQXleGr3sqLf8dnd7x_VxaUBXgIKmWucJNqLEJzC2OkbRDT2rd5WhxItMFoa;  thor=69304ABF054FB0B1BFBEDECF4291EA968D5A66608BA7FA8E424C5232587C709B3D4DC70328DE510210B8245262745A7CFDD22F2FB1ED89C72DD9E83BEFFCCE511FB9BEDCD992165915733C180578ED1BD87159FB30B484A4CAA97E7BA0C9B94EC91C2F8CBB8985F7DC43544AB390A889C94091FEB595B941FFE2883F6C58393616E44293ABD14509E05F201A70F0857F7CF2DA2EAC113D65D2BBFFE87A7C7CD2;  pinId=cawvLTW7pPeNiML_J_udSQ;  pin=jd_2Joor5swMRYn;  unick=jd_2Joor5swMRYn;  _tp=GiJrkj%2FLlUjZKFE3QMQyhQ%3D%3D;  _pst=jd_2Joor5swMRYn; pin=jd_2Joor5swMRYn; wskey=AAJiCFQrAEBkfROIoXWOiImtMfnSibP401ulzP-DbPdmq1H9H8jogVAPVRDJUFLI8r-gySbfHIuBCWr15cBPYq8AQEULTUZ6;'
    # ck = 'mp=jd_2IU8CuUAdQDl;  TrackID=1VYB2zCyFVXLBGOnW0JR7JX69bcjGVyPcg-YOlYzCPdHg_2cq2x7Jlg4KrpMkTK0AjWQDiUIFSBVcnCgZyrcgm_ZoPFShQxMc4tF6tw7KEpYtEaak_wECBtXCJ0FgJirf;  thor=089AD313F58DDAC701B41EEA5A0D2CBD08B96AD6709FA5C6162FDBB2860D909780AABD2E602E7F62D32E708C0936C5956362C1E55397A0ECADDC7B93DC81887BEC91AEE64A96461ED5287794A52948E384C0C2C6F99C68C4328C9828589A6D129AE02CD214376C6B54C4AE193770702EFD4874C451559F5EAAC8C02A8525853C7EE64197C951955404B642902EACAB6E8832CB8B2C388CB3FE623CF4AAD4ADF4;  pinId=VTx2BGFqgAMdwzRWCysLUA;  pin=jd_2IU8CuUAdQDl;  unick=jd_2IU8CuUAdQDl;  _tp=RDSrkxDoANK4TUuU0cYohw%3D%3D;  _pst=jd_2IU8CuUAdQDl;'
    ck = 'pin=jd_5zWGTfk9FBCc; wskey=AAJirYGwAEDK69KOB0q8shMA6l1ww2e4f_Qgexe5Pb_Xr3epNGLR-0kRfZg72seFOaW5fmbWhm7q-PeJlMH7lAegvx4cHgTV; pt_pin=jd_5zWGTfk9FBCc; pt_key=app_openAAJirYGzADCdPGLsEI4CS0Im23KyBHHjOl1hetmWlNGccjrrKknRwULHyuZ7NQtUdCsbj1pb3ns; unionwsws={"devicefinger":"eidAe61281232bs47e2jHFk8QGui5gDp9P/sTu3tpJ3O/t1gzzQvRS7NqwuD6njc5k6CZm41kXjrOqnRNZrHQa6YcVBbvolh9CpVy5swn/nroJKDpXRu","jmafinger":"dCPwmgwNggMPWytdI4G4CuWChPK1TmDzI61D9Zx0Jnlh5MMlWT9_J-1DsrMtDnaAc"}; DeviceSeq=28014f837ddf4bbb9d8b5076a301847c; TrackID=1uZ8cL96sx1KNvR-5PIUh1cZWXXdNh33-f810TXHoF9w7P_ha0tQyEyAKQ4vEB9SH2jpid10wYjIqyRS1zkxYXFh4emD_tspF43edhcQyjhE; thor=7B44E30A66A4704049D7142F04C775EEA3F0B9095E95C63464742A5DB55ABE9F35AA87911334AAE9054916560FC562C727DD7457B7C6B43C4034CB837680339FD97D8E6EDCC1CB14706F6729E43B4F05D2862C40F84D894EBAD5A74E6E024906739DBBBE289AE6217BAEEFB2F4F8B0A616B5856ACFC233C82627EC153FAD1B3D50025D0E2F8E7BF0EADD6C0346A87E6DAC61F0E5C060E83A12BE0E492651DB8C; pinId=-u1pxiis-ggqnnWyaLZQQw; unick=jd_5zWGTfk9FBCc; ceshi3.com=000; _tp=x7eMJ5mIHGzFe4g8oUW3Vg%3D%3D; logining=1; _pst=jd_5zWGTfk9FBCc; guid=e6aa9f1129f450953e87990b6f55a678b93b35242c49e912265185d60e55b341; pwdt_id=jd_5zWGTfk9FBCc; sid=ada718fe488c49beb4df16af962959dw'
    ck = 'pin=jd_gxuavMFG6lnf; wskey=AAJirtxzAECZuivvU52gUf3hH2UcDlLbxXxNzAOrvYt97xwSTZqxWuLk34DzdkJ9MVsgxFuLZEyctqItHyjHg8Y5ktp8gWkg; pt_pin=jd_gxuavMFG6lnf; pt_key=app_openAAJirtx1ADD3JFhz38CIcxhYrUMxg6pRoJ2YeN583-ObVI3mS8TicPxDndELcK2s7PjTlbzptsU; unionwsws={"devicefinger":"eidAef76812289sb9e0ISDlMTHepovZ/DD71zvXtCcm0WXIAamsWKNMqV402nmqnen4zsHRJwhnKAwUy0Q/fMAUe4/oiaGi9Egd66m7jnSz8om1rf1Jz","jmafinger":"xsTlY_ykyPaf0Ubt6Awx9q2aT9gds2Nq5v9N1-o_p-HShge--5aEinRTQl7zuztW_"}; DeviceSeq=c46ab50e695d441098787c42a75ec9a9; TrackID=1aZfxrZX8ajcQ0OM42a8s5xlMRVRuq-VVZsPuaPrWw5ueaecCTMjOQ9TqjO36YqjOexqgE9tY-l-nZgGlCmAC-F8O4K-cKeX3C_jiW9p6lRM; thor=C457C37BB07B7E2755F4F038E7347C04453B6B93B2199969B0A8F90DCB8108C5F5F3B697037717FED961B86EDD34CE18E03E7969273D0CBD86F6F535151A3F65886F09237FA115BCB39369D2C0B17DE0EADDE2CC4C01C75041EBCBB757928FF906C61BD5E98717B334036AE1AD9FED1457903679D08592105AA31A997BE31FAB09B51FE3B5089529DCCD00EDAE92545A0BCDE540AF16729804E8DEEDA2CB2C6A; pinId=PmbKSyN98rJEWC4ccGAQXQ; unick=jd_gxuavMFG6lnf; ceshi3.com=000; _tp=C4aXsxccB1sXwPFRO0HutQ%3D%3D; logining=1; _pst=jd_gxuavMFG6lnf; guid=553b913a9ca56e1029b563c6bc21a613e0b25010c802f466bacd628824f4377c; pwdt_id=jd_gxuavMFG6lnf; sid=41b3e03ececd580b0589c4cbf88d19cw'
    ck = 'pin=%E8%8A%B1%E9%9D%9E%E8%8A%B1%E8%BF%87%E7%A8%8B; wskey=AAJiruzyAEDmlAcvUebF7aw3eDa9AGMdj50g7xmFbE-sHGIYBkG5V6mLOrgjhkAhCeUqZNTzskKhVjt1PJFS7BR7JR7agqkT; pt_pin=%E8%8A%B1%E9%9D%9E%E8%8A%B1%E8%BF%87%E7%A8%8B; pt_key=app_openAAJiruz1ADDNbpatAiKS9QKcemm-nKPWYRImPPOwH9wlnPfVlevkQqtYNeDsXqS4n8JtrMATco4; unionwsws={"devicefinger":"eidAbf53812164s7OrNCTxMgTQa2F1pBYZ582zqzQ9CObeKVmh1BfTAdmx/dfb0pLxGdJk1FLJoADs31fUa1hVHeVQYhTS6M6l6/RyMkfZEwNTS+JOFy","jmafinger":"yjpSFlZtSf1DRD1Awt4G4-9IR9lyxzQbEZ85fICMH6IgwGdmA5L-NPdIn3F2udqtM"}; guid=646d2e7b674afec5ad7369d2b91ecbc3971dc8d71f3cdf329535f64e85ddaaa0; pwdt_id=%E8%8A%B1%E9%9D%9E%E8%8A%B1%E8%BF%87%E7%A8%8B; sid=947e14091e7f659839e150cf3d8c2b9w'
    ck = 'mp=%E5%BE%88%E5%A4%9A%E4%BA%8B%E9%9D%9E%E9%9D%9E;  TrackID=1T2cuQqi_Ba61sQSgJHEBNIw7drlhRD9JquUIYqiWbzkhuxYM37EGaDA6j0t8oYQz-opDACmnpmKKogXvI6XHwu5wl494QAuTEQbCCjBH-grAXLnh98pnm7REERiH6mSX;  thor=32EEA0965596BC8F5FA10EC97326850800B6D2036D4F8E659252B1C90B148D5A4765DC260536A869E02C5A57D23D429DEB602ABF9E2FA682808C34B80252709C2CDC6FFBA771ABA9AF0479B1F5C3587F510C6B21A89BC8E94FB13835A199F7E0407BE8118D568649BBDA94A2D19CDE1F987DE1412A6FB9D95153917EE35CFF4A;  pinId=Z5dF3fwhWT3KnmxA4uZHbw;  pin=%E5%BE%88%E5%A4%9A%E4%BA%8B%E9%9D%9E%E9%9D%9E;  unick=%E5%BE%88%E5%A4%9A%E4%BA%8B%E9%9D%9E%E9%9D%9E;  _tp=Dcub4161wmaLRVtXWwCg4HkYSFCYHrc4nPLffhtaj7TI3rUwMfy4PQuXm7c%2FGLOv;  _pst=%E5%BE%88%E5%A4%9A%E4%BA%8B%E9%9D%9E%E9%9D%9E;'
    ck = 'pin=%E5%85%AC%E5%AD%99%E7%AD%96%E5%BD%B1%E8%A7%86; wskey=AAJiruztAEA8IJy9VbHTgPte1ykenbHAZNhSOxRXXW0D99vxThm2weHOU2SWDaUGoFxuJob2TAnpvjN7osdgf4AXDlub2ULx; pt_pin=%E5%85%AC%E5%AD%99%E7%AD%96%E5%BD%B1%E8%A7%86; pt_key=app_openAAJiruzvADAeKBFy1M9Q2mZzOZNpJPg97D9JGwBTXRyP5RwY852E4AabEYZGhETsDE6VkC13Tjo; unionwsws={"devicefinger":"eidAcc5f812269s1VnRTmNE4Qly0GDu2VIF+YlZ0VRpMhcJBenO0jjuSKFlgyiLY20syK29F4UDtBM6nOxLWod67TvUruDDbWMyhpbIxYBsaTqVh9R5x","jmafinger":"umqG-gLPetbA_5JKcvjBviDIf4aJgfOP99w95hGUlhul_OKYYJkK5ScGrSdWZmKE7"}; guid=ecb2167ca8740aa9538843d75818ea517d8815e48065605ceda9deb4eabd93d6; pwdt_id=%E5%85%AC%E5%AD%99%E7%AD%96%E5%BD%B1%E8%A7%86; sid=62484951fdf09a7d825562a1d479d66w'
    ck = 'mp=%E5%85%AC%E5%AD%99%E7%AD%96%E5%BD%B1%E8%A7%86;  TrackID=1dkPsx3Ux5dqKNUPXVApJH2-uK2EIfN06U7wJrazsVXcrDxUACCEOgk2V4vG0LsaH5D8b-3UGnlgkESWdYxfMEe6r3rQtqni6WWzRDd5Gh9OmdWL_xdB3X7RUP3pArHGS;  thor=D8BE675CD8A305F37E8CEC71E9028E8D93D4BF53B8BD75A65CA4F5F6878B8CF0838C1AF1DDAA40BBE01F8C00CB38A83E899B82C1A198D134819E8ED3001D3D04A44474C04C8AE26A6CC5161101ED6E49DB9C44114F5A39A24A37BCC5707CCB83AB06CC95ADFCEE72EAED141448385A4EA2778C9EF7BF99B55C334DE15EBD306F;  pinId=vAaNifwjdaya1YdPbZ5FFQ;  pin=%E5%85%AC%E5%AD%99%E7%AD%96%E5%BD%B1%E8%A7%86;  unick=%E5%85%AC%E5%AD%99%E7%AD%96%E5%BD%B1%E8%A7%86;  _tp=QCs57yHCt29WO8v2a7XbJ0d%2Be51pL9gJJdv2HwGs3JqPAB8Bjiv%2FGQ86M1ApADx3;  _pst=%E5%85%AC%E5%AD%99%E7%AD%96%E5%BD%B1%E8%A7%86;'
    ck = 'pin=jd_9yd99eSUQtTX; wskey=AAJirvxZAECMqz2O53yuGn1Nzdamo2AZu9S1n8m5oBh3P_rhLdRdmHFoHQwCIDfXXvQbkHDZDmx9cT7mf6PxO-c8rId3TktB; pt_pin=jd_9yd99eSUQtTX; pt_key=app_openAAJirvxcADAncIJzkWVwbi8HCMG0VVWHCncYAgUkunQJpEy0auAyV9EhBkx3rCTEBGs8gCl3Xw8; unionwsws={"devicefinger":"eidA0b9e8122d0s8+qXxHELxS/igJTugEsSjjPql8p2+ew1H7Otrfupc7fXrRs472KSyDTRyx40jxhLQuJicUbYF1JC72aQgdAu4fotjsHtANPBG58wx","jmafinger":"bbhn9MJfRxk4LxQ1Yl8Umo2Bvf1pLMwLkNWFqHzNVg9cEsokzfWJqK8sJsEyl5oit"}; DeviceSeq=a69a2e09a0e94d68b21e207c232e720b; TrackID=1OWigegHsKMth8JuEsi5ReJ65tJ2WwaUXTfK8pBDYJX0jBG_edWkO5pVuB0S1E0ywZtNsBX3HTSQraNyMEtP2q4ieM42Ed5shj_vdid9BLZA; thor=6571CC2E3B9133467DC464AEEEE43D33A64AD39C09CEB4DE000B3B818CDAAEF2C7E3B067BC1B215BE9C0AA53FB119D1599C43CC1F773767DD6E06D8992188434CB716FA86BC97F6792DC22105DF68B86816B30D737E996F528C576F359D382695746F9132A9C2C9643FE60D15E08E48C8A646AA0D0DB18C86334ACEF431BE22AC40BDBE213445AA1CC849B6FA927176FA8C975607B295DB0858C7F7A1A32F8AE; pinId=LzqJhjCGO6_O56uFioIRgg; unick=jd_9yd99eSUQtTX; ceshi3.com=000; _tp=vO6bBtH5vWgEzVXRcOcROQ%3D%3D; logining=1; _pst=jd_9yd99eSUQtTX; guid=3b1ee4d949585fb318d8ad9845622eee7fbba575d0bf8b15dd30e6e08353e08f; pwdt_id=jd_9yd99eSUQtTX; sid=2ef5f3bf6f0bb62f45e40083f82daa0w'
    ck = 'pin=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D; wskey=AAJirxlJAFAxh9EyD3dvVSxseGMy3ymEFokeROlblOuZPzm-KoqENyzbzQ5BUj55Wh39FUfeEWk8Hgw4CCOvlTPAHj91k5U1T2irDIsJ68uQVbiApFeyuA; pt_pin=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D; unionwsws={"devicefinger":"eidA9e9e8120c3s9p7f/qUOGRDmUgtLZ57t4Yae4ASq/gQ82oNnHoc5Ok7o7J8Ok8jKYJUhHBJhaZPAUOEWa8N76t5edEvZrDQ4PsY7FJ00E4fxqVgx0","jmafinger":"uQd9ICI4nOPAZ843nF9qcYhb0dFOV01dwtepasuaN_xHWG_eQUjmvquVt20U_3fRJ"}; guid=92a54b115cfa1f295d2927b0c9951c67645e2ec5f79733e6a723d7c9b558dce0; pt_key=app_openAAJirxlMAED7KBvvZ2ULO6j4AbqGyAwqGAwCVPq0FH65XSORJpGcEhYnTmPn0LqhaF8GmqzZh6tMOgZiBVFHUNe6gqthq-ai; pwdt_id=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D; sid=33b4cb0b0328e0316db0b5ce94339e4w'
    ck = 'mp=NKTYr%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D;  TrackID=1iuwIH0vORgwjXJMc39iEhZ073lrmF1IKONVRLAQ8ipDW3JIhRGJVwpyF-a3tNHpn6aGl8-jcRcHlXRafH94SLozSsCy4Gyn8-sfMAbhlF7-0XkAdhQ_p9kIjykG19jaNMMRRGDXznbFOPwLD0qrWSw;  thor=D088EF3DC6FE558295F881E188C90EA43F9EB45D23E3D933DFB3EC2931EDB801125A8FB88F83BBB21FDF519212D971A2443811E8F061CEC1EA7FD425F1569BA7ED758BF6AF1B15B0D6C7AFA4E948B7813C10A8DC1CC2EA87BB3719C16AD053305F222057DC3A828FFF3D18766C9B1AC7624FD3051F85E5CB0760E91E9542DDFD764C98899A460590FEEC9D82F33A3457;  pinId=_vLNmt-NGz5sUrMCKuqSGLA_n_aofsP7;  pin=NKTYr%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D;  unick=NKTYr%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D;  _tp=PlG8N%2F9laJf%2BwYdf5Tv8oU2q3gaK8ArBNXV5s0gwwb6whwtT4o09yr9tvmkQIh72OMmgRxrOAZBdv95g6Z7b0w%3D%3D;  _pst=NKTYr%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D; '
    ck = '__jdv=122270672|direct|-|none|-|1655674156609; __jdu=1655674156605580935857; pinId=nGtUW9EFSAHh4DAIQ2YmPxNmbjgR5rvE; pin=常德鑫惠商贸有; unick=常德鑫惠商贸有; _tp=S9ltnMsm4uGTQz2N9PhfaC3RfnBFdLQvtS8fb7z4GdhAShf80frD4jQJGjsfy/vad1TbdL3IskTjXdDf06zgBw==; _pst=常德鑫惠商贸有; areaId=5; ipLoc-djd=5-142-0-0; shshshfpa=fd32a51e-3b83-c6d5-d554-96a52c794f8e-1655675526; shshshfpb=y77saU9E7DP1bdE7TMWPPZg; shshshfp=dc60dcdec8a01786bfe8b6dc61e022eb; bjd.advert.popup=b758bb041ea34c24ae55e299fa1968ce; smb_track=8B705CF26E4A4545BBD815F6C12CA4DE; wlfstk_smdl=vbrsw1o0exmal26gxdt059szxkvngv3c; TrackID=1T0GAqekQI-EPRxQ7_AfXDweGRw3_3K-Wv9qfbzXwDR3vURsZhL9nijcmCz7wviaiOPRbTMOQknN1x-qYaK2jlolTev0jyWI0Itmjs87TWK4; thor=0944E0DC62EB44D00ADB370E1A55B5C41E4B698D6B58022C911918E90C96FA2775B4428E1AB0BF629604E54558CC669959195766DDFD61ED28047663F9D0676A95C31D7BD84B891CB12C9688E91ADB826F58ED62947B1495F43E8668A63A46CA143CD8B98CDCAAEA34B87C0A8B105953FF5984F63B6F3DD4CB1B4601D10FDB850F22FBA67B8564B1E4B3EC01C14C7A6E; ceshi3.com=000; __jda=122270672.1655674156605580935857.1655674157.1655674157.1655732435.2; __jdc=122270672; user-key=430367bb-b5ae-4d2c-a873-ca74f4443db6; cn=0; __jdb=122270672.12.1655674156605580935857|2.1655732435; 3AB9D23F7A4B3C9B=TTAY52VM5QHK3WLEFBHJ75CRQ2PGLP4NKIYD7VGAP6JQBS7QDA3RVEARCELFFRWA3TSTTYW3UTDJNGWRN55UG5QSOY'
    # ck = 'mp=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D;  TrackID=1h3nAK9Z4O5Egw6gbRziSvvorz2u19jzj58uC9GZbmcV82G3lzTFWz5tcgzJlh6g2Cw_Yh17Ejj93JlSswu9MNw4H07g4iGMtR8qai6tlRsNVK5kuAcrcKq-1KoJB9NqczryqC0cbHFuRwSzyYFLn-g;  thor=4D813F6EC493AF102B5493D2DD3AC8A354D4C0D8B851429680E4CC5C392A432D153A4C512638EED6D32280D39347CED98C85D77E582F46FD073C3FD37C799C16624B8E3491B2DA929B29361B0E301482153B21E5119DA8D9EC048FB7C85D27E02C1683957128C31D42D1512DE79C0DAFCA588714921FE2C51B1D8FAAB08EE98B202908D2740E5F2D9F60E34BE7BF3048;  pinId=isAdWnA1919sUrMCKuqSGLA_n_aofsP7;  pin=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D;  unick=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D;  _tp=%2BxpGwSyxyaFVvjHbV1RcmMApXSn18PQVV%2FVlXlo7iFER%2BlKOxJK0BcbGN1mc9LpXot8SYJaE8EB0z46UAFexww%3D%3D;  _pst=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D; '
    ck = 'mp=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89;  TrackID=1jP64P3PBB9u5gHA40PRmn_hq5OdOiu3iq8sAraDddMv32lDfHSra9rKZ-A298klHNleFn73cOEzZsPMaaKzxlG5qY4_MDZ8UqwjQABTQ95r45aWVlY8WkObg9vZhJZ9CxaaAJTDi3WwB-5D8Uzt9wQ;  thor=0944E0DC62EB44D00ADB370E1A55B5C4DDC751D1BE312F5CA44F1AE64F9DF8905B9B55EE73BB88A68E1FDFA49855C4064DCEE05AF1D9DD0670CF3812DC901CD8AC362D75F0B41B4795E9DCB7741F0D5E8DC4A3F3CFDE62036B714C9BB310DC34F40074B6E751C1C24BBD5191FB19FF8D7ABAB76617691AF10124C37B2FA6CA5F16478CB83263F37DD90F78680FE0269C;  pinId=nGtUW9EFSAHh4DAIQ2YmPxNmbjgR5rvE;  pin=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89;  unick=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89;  _tp=S9ltnMsm4uGTQz2N9PhfaC3RfnBFdLQvtS8fb7z4GdhAShf80frD4jQJGjsfy%2Fvad1TbdL3IskTjXdDf06zgBw%3D%3D;  _pst=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89; '
    ck = 'mp=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8;  TrackID=1LOR5xqLW7SZJ6qM-veEfopS28U6kfrKgVB3V4WaESQRBj1JuS11_VE4c16fKxbmskdZDYkM5enBdZumT9Up-dY6-3TJ5SKtddCbcMWwnlEAL8b8_xmsXTgHqmt-AaqOHIjsuAXHZrDqv-rrWcKtwtw;  thor=11F350161A639A8FFDEB2D927D14E00FC0622EE9CBA5E49B923CC3528284B3854967B22AEE62BE9FD9C85B4BF79A6F9860CEC0E09D80F8E641775CB7CA19804F020C7F8493C267A9EF896804F54902315CFC7ACCCB3BDBD832A71938D965F4163CC7665ECAF3C6FA9B03DEC3A7E6FE898FCEE2E9181701B095157369E243BCAA81A7B0850E2811E677CAE1C8D84E341D;  pinId=Ww8ssFBYyPLlN2KL7Ev_q3wnzN6coHcK;  pin=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8;  unick=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8;  _tp=rR3s0tEXqirKHl5VPSrdF35ngTQtCrdqeKVE7me0muzxckj7aH2XmVNGjjOxN0rmVOIDmyRP8YVQ4JeTQsWVoQ%3D%3D;  _pst=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; '
    ck = 'mp=%E6%B2%AA%E5%8F%A0%E7%BB%BF%E5%8C%96%E5%B7%A5%E7%A8%8B;  TrackID=1O57tmqvpbdcjNTV6tDh-rSLJ-fDRkj2gBJTuaZ_-o5sugsNvwjMRovj7qU7dZQtX2yk2CDHmNKaWL_9bhWYgw2tQVp1-NVxAYaEZ8QK_iLfqKaJq-RrMdHBLgB5DnFMKSZrt9oK3l5EdjbZT-UU9BQ;  thor=B4B6BD9F4407322D86D3E3614D678EC349408302FE3C0DD0EE38A56C81E821105DF228DFB189E1E32E3EC91AF24CD93A30390CEBC4EADC2F4EB22B7CAC9F445817426BF525A68EC6D0BD0017A1206104B9C376F10F9475679B5C9B55D3DD7DD028EF82C14D26462BC6D966A361BDD15E9BBA713C0D6BE5F5EE03A40F494B37A2;  pinId=ZYNHD_IQelH-PDA135BQG9QaOhQ7vEQA;  pin=%E6%B2%AA%E5%8F%A0%E7%BB%BF%E5%8C%96%E5%B7%A5%E7%A8%8B;  unick=%E6%B2%AA%E5%8F%A0%E7%BB%BF%E5%8C%96%E5%B7%A5%E7%A8%8B;  _tp=cuRvxWSpKD%2F4T21xxNtPdOJJGJcweKqoQbzkOeaKuqFeMCaCl7keX3KLJmHsnL7cxhAHRpToYaeakPRq6gng7g%3D%3D;  _pst=%E6%B2%AA%E5%8F%A0%E7%BB%BF%E5%8C%96%E5%B7%A5%E7%A8%8B; pin=%E6%B2%AA%E5%8F%A0%E7%BB%BF%E5%8C%96%E5%B7%A5%E7%A8%8B; wskey=AAJisH5xAFBh2_VV3yZXapZ_mEoY8OMMvQ6qK4Bef-qx3DH2iXmWH40SiQgcxnTQFVAmEx0wHGWKSNL4UrAjXGwbtdCsz9Ck_G2SJsDqSRC_oiI6B5rfXA; pt_pin=%E6%B2%AA%E5%8F%A0%E7%BB%BF%E5%8C%96%E5%B7%A5%E7%A8%8B; unionwsws={"devicefinger":"eidA7aa8812105s9AcNZ/OwOT56weCzTDJE7+gHDW35tfEKkylkRZX4CFpF1bA655c0fXVE2e5FVKigQaoKknX8H2cG+v6MCkrt19I+Zp5OoxRtxarhy","jmafinger":"d-zjZvjS5wBYgFHmxk6QkUuSTdKDKIJf0GjYHxCZn0oHDidR-E1M-_G3YWnLdDuOc"}'
    ck = '__jdv=76161171|direct|-|none|-|1655733376517; __jdu=1655733376515139287949; areaId=8; pinId=Ww8ssFBYyPLlN2KL7Ev_q3wnzN6coHcK; pin=郴州市惠飞商贸; unick=郴州市惠飞商贸; _tp=rR3s0tEXqirKHl5VPSrdF35ngTQtCrdqeKVE7me0muzxckj7aH2XmVNGjjOxN0rmVOIDmyRP8YVQ4JeTQsWVoQ==; _pst=郴州市惠飞商贸; bjd.advert.popup=77aa169e44add2a516f2d398e97c17b6; shshshfpa=5624b3b6-4849-3bef-2fbf-084a662b99cf-1655733458; shshshfpb=jbBGQN-DRbE-GoLW-1MeUeg; ipLoc-djd=8-598-601-40134; qid_uid=cbd4440d-c2a9-4a2c-8669-a5c2723c8c84; qid_fs=1655733551267; qid_ls=1655733551267; qid_ts=1655733551285; qid_sq=1; qid_sid=cbd4440d-c2a9-4a2c-8669-a5c2723c8c84-1; qid_ad=pay.jd.com||jd||0; ip_cityCode=598; wlfstk_smdl=v7ql6n0qh88fmwwigd55r71que1jn91j; TrackID=1SA3Lrg7-de9Xsc9FK9m0hTwLpS-cJH-9tBJnp9pscwiLiBHXo1cA464E-HcbJgtC7uFETFvO4o6x-xvzxRVgBqqbQKWjRinblR29uYQ7dxA; ceshi3.com=000; thor=11F350161A639A8FFDEB2D927D14E00F9A391681FA34EB1E7334D235C907088A96C522B4660EFCAD98F697E106C39474DEAB2592D805D3F3AF7ECE67D3F01FB78ADEBBFD3CE6B5C8FF70AD5C364BD55AAFDB8A3F86C7F6C597273C748C5AD83FFFBD5ABFC8A3CCB27106A52F4EE0528040F213457DE0DA6E08F1364DC27AAA55834E9679DB06C0C298CC4D4EE4456F03; token=7e2249a0edc0d2971bfac9d3422522f4,3,919852; __tk=rzxE2YPtrAVA2cyX1APXrDM4rUSBrwVn1waFqcaEqu152wxCKwaEKM,3,919852; shshshfp=83c9994bf8e732dacd731ca741d0e5de; shshshsID=95f3471fcf66127638375cc3a20f2b21_7_1655735297940; 3AB9D23F7A4B3C9B=KM2HAP5O35YI7CYZN3UZWG4NKAFJ5BXQRAUNCPNFEUKSFUODDU42KR5ZNKJARVIWTM62OVDTOPSRCFARJ3VNFYWDZI; idtUserSession=11079fa4-7ab6-494f-a1c6-4b00e3840463; __jda=187205033.1655733376515139287949.1655733377.1655733377.1655733377.1; __jdb=187205033.34.1655733376515139287949|1.1655733377; __jdc=187205033; _distM=248981093248'
    ck = '__jdv=76161171|direct|-|none|-|1655741652859; __jdu=1655741652857284734440; areaId=5; PCSYCityID=CN_130000_130100_0; shshshfpa=f16da761-3a44-b368-575c-0ec234e8be30-1655741656; shshshfpb=vodOdfkrFAbs-0NYe_wreXA; TrackID=1pCUdUcxTzK8iAorC5m01IPZm6_4aGYSZX72zBgdi8SvKMiure1eBZdkb8QciSQEkXaAtoxhrk2YFEugp268M39_tr8wDIXPdGU2rTBUCxZx4MM8VZHiwyJstdSlB6K8Z9RNJj9G0Nd0-xwJsfYPlSw; thor=2963001E8CBC27360A0C164705512C7B724CAD41C30869929058E55129B78FC4D51BB5BE57B97DFA665F90C818263B7D6EDCDB4C0B909D7AFE572A2268647E574DFC4BFEF74049A163CA2CADBE19239C0B84C89860EA021BC42B55D1BB6A3EF08592912CE64F725554C5F76CF6B3EDC469B1200D67488AEEFF1A6E85F0D9034A; pinId=HGuW9anrYWCj6LBX_g6HKV2dlD6NMZPH; pin=浩田园林绿化; unick=浩田园林绿化; ceshi3.com=000; _tp=F1Z6Lbq8yjI3Jz/wG0f8w5bYPOnvO7tcq+dlNJfOufMWoNbRIRa2wPntkG6fZvuejc7KjgK53Allaj4LwP37LQ==; _pst=浩田园林绿化; bjd.advert.popup=ac5f7aa78683afd6a60e824a614794f2; shshshfp=f9e5fb552de10bec2545bcafa3a2d0f4; token=69289eb29e71f6b61d92170abb40a1b3,3,919856; __tk=OiTdsU2FrDTerDvdqfbfsLSBqcSBqfNnscKdNA2AqLvfscJDqDOiqu,3,919856; shshshsID=7874bc96f50198637bf3b68c59c8e7be_3_1655742289203; ip_cityCode=142; ipLoc-djd=5-142-42547-54561; 3AB9D23F7A4B3C9B=QNCWC64QP4P2LVZKSMOYVQ5UVCXBVUAFAP3XXO4Q2JGY5MVLJ5CNJO5XE3NHQHT2XMBDWWZ24L3C6T75QSANI6DL6E; __jda=187205033.1655741652857284734440.1655741653.1655741653.1655741653.1; __jdb=187205033.15.1655741652857284734440|1.1655741653; __jdc=187205033; _distM=248993922057'
    ck = '__jdv=76161171|direct|-|none|-|1655742458037; __jdu=1655742458034492679635; areaId=5; ipLoc-djd=5-142-0-0; PCSYCityID=CN_130000_130100_0; shshshfp=75eab5f243e0e0369fab1aa388e3811f; shshshfpa=637c5e74-580b-9649-3b82-284064f78995-1655742461; shshshsID=28739638ba3ac225daad943992ae41fc_1_1655742462467; shshshfpb=b9L-s6XK5l6yZL8AOmxxutw; TrackID=1gPfnXL4bkzUbXbzXn8WGK2ydkvEu89MLxFnj9VvM9FtTVPP34vGwf_KZNpFlJET_fqojPHZPBsMmmCXOGut10S1fYNHBSwEEkb3ikkWMAkpojz5ITSdlUBM5655VarQL6uedM5tUeOZj5EDOvz_g0w; thor=11F350161A639A8FFDEB2D927D14E00FD77F76958AFE38476DAC270A51DDA9AD0978E7B9E65A2511243B7535FD207AF341FF01B72393F39DF7315E83F798A8A4E38D2A4DCA509E2E1F65065E28A4D5CAD487BBA4A151D02ABD4FA04CBD15FA5A88BB730CF76D165A2F150B87C6FD1D62A1C9E0CF365A4D4986A7E934653AD45A5108C810DF2303E48DED65288C2653B7; pinId=Ww8ssFBYyPLlN2KL7Ev_q3wnzN6coHcK; pin=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; unick=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; ceshi3.com=000; _tp=rR3s0tEXqirKHl5VPSrdF35ngTQtCrdqeKVE7me0muzxckj7aH2XmVNGjjOxN0rmVOIDmyRP8YVQ4JeTQsWVoQ%3D%3D; _pst=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; bjd.advert.popup=4fa91c0e04f159ddb42cfa2e2856b375; __jda=122270672.1655742458034492679635.1655742458.1655742458.1655742458.1; __jdc=122270672; __jdb=122270672.12.1655742458034492679635|1.1655742458; 3AB9D23F7A4B3C9B=QNCWC64QP4P2LVZKSMOYVQ5UVCXBVUAFAP3XXO4Q2JGY5MVLJ5CNJO5XE3NHQHT2XMBDWWZ24L3C6T75QSANI6DL6E'
    ck = '__jdv=76161171|direct|-|none|-|1655742458037; __jdu=1655742458034492679635; areaId=5; ipLoc-djd=5-142-0-0; PCSYCityID=CN_130000_130100_0; shshshfp=75eab5f243e0e0369fab1aa388e3811f; shshshfpa=637c5e74-580b-9649-3b82-284064f78995-1655742461; shshshsID=28739638ba3ac225daad943992ae41fc_1_1655742462467; shshshfpb=b9L-s6XK5l6yZL8AOmxxutw; TrackID=1gPfnXL4bkzUbXbzXn8WGK2ydkvEu89MLxFnj9VvM9FtTVPP34vGwf_KZNpFlJET_fqojPHZPBsMmmCXOGut10S1fYNHBSwEEkb3ikkWMAkpojz5ITSdlUBM5655VarQL6uedM5tUeOZj5EDOvz_g0w; thor=11F350161A639A8FFDEB2D927D14E00FD77F76958AFE38476DAC270A51DDA9AD0978E7B9E65A2511243B7535FD207AF341FF01B72393F39DF7315E83F798A8A4E38D2A4DCA509E2E1F65065E28A4D5CAD487BBA4A151D02ABD4FA04CBD15FA5A88BB730CF76D165A2F150B87C6FD1D62A1C9E0CF365A4D4986A7E934653AD45A5108C810DF2303E48DED65288C2653B7; pinId=Ww8ssFBYyPLlN2KL7Ev_q3wnzN6coHcK; pin=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; unick=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; ceshi3.com=000; _tp=rR3s0tEXqirKHl5VPSrdF35ngTQtCrdqeKVE7me0muzxckj7aH2XmVNGjjOxN0rmVOIDmyRP8YVQ4JeTQsWVoQ%3D%3D; _pst=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; bjd.advert.popup=4fa91c0e04f159ddb42cfa2e2856b375; __jda=122270672.1655742458034492679635.1655742458.1655742458.1655742458.1; __jdc=122270672; __jdb=122270672.12.1655742458034492679635|1.1655742458; 3AB9D23F7A4B3C9B=QNCWC64QP4P2LVZKSMOYVQ5UVCXBVUAFAP3XXO4Q2JGY5MVLJ5CNJO5XE3NHQHT2XMBDWWZ24L3C6T75QSANI6DL6E'
    ck = 'mp=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8;  TrackID=17LKG441mUw5lDLoxFsgoodl5_RdURKBl2sS0p5i-k_8txH8Z0JTeM2fmY_nVVu226AXOpd304E1RjY4t4RHbnDPQ8DFJDb0PSMfA7qVpsrXmyfh8tTSREsz89jPfFNZUUqAMVof2FtGF5SMVXvaqVw;  thor=11F350161A639A8FFDEB2D927D14E00F41F1C3EDE8F8C482DE82F0612DE1828BEE240BD5E7718E12F0F9B0F624EA82E5F5AADE2661216B03799D52F3F526EC64D929AD7713F19AE3A9238452366F6CE3BC16133D612159FC85D57775F19F2E1E4FCDC5743016F1D29D72EB6A469ACC515869B996046DD9736F0AB8A9638A967DFC26C188D13E2F894E58A71DF7D2C8AD;  pinId=Ww8ssFBYyPLlN2KL7Ev_q3wnzN6coHcK;  pin=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8;  unick=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8;  _tp=rR3s0tEXqirKHl5VPSrdF35ngTQtCrdqeKVE7me0muzxckj7aH2XmVNGjjOxN0rmVOIDmyRP8YVQ4JeTQsWVoQ%3D%3D;  _pst=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8;'
    ck = 'mp=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89;  TrackID=1aOsz38LSQgwMbOHbccjt_Si3LXARhK5HPRzBtPGr5QSJ4YsbzTJM5tUGERem4eIMyfto-Ov_5iyCTcyf3YMlUiJNZHbWIehG5pgAUgD5GOGAqtWvD6_3HqHiY1HT_B214RYHLrZi4jNWprgKJd0hOQ;  thor=0944E0DC62EB44D00ADB370E1A55B5C489F4718BCC2A5B1658F0A9DBB543C3F2264F0B832FB0E0C6B4D6E2CF7E12B41F515477BBAE42E9381152B0A3AD20B28E3B13FBA1B173F366508D4E3473D329E616B097C4BCDFB5579A48DC8B909804893D580741FF12A7908A6DC633089111897566F1E6579DC74285AFB1986285C6A2128CF05D589BAEDAC23FA98382177BF6;  pinId=nGtUW9EFSAHh4DAIQ2YmPxNmbjgR5rvE;  pin=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89;  unick=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89;  _tp=S9ltnMsm4uGTQz2N9PhfaC3RfnBFdLQvtS8fb7z4GdhAShf80frD4jQJGjsfy%2Fvad1TbdL3IskTjXdDf06zgBw%3D%3D;  _pst=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89; pin=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89; wskey=AAJisV_SAFCkXgoWvHkkWOw81sWXTb6cbldM-6E8ksVUeoGtEDzsCDGAqUDWEsLf5m3lH2gXiJ-SYurdBEl9UbyGh3Tppg7WZ7mzVgI9OhGD4vVh830fEw; pt_pin=%E5%B8%B8%E5%BE%B7%E9%91%AB%E6%83%A0%E5%95%86%E8%B4%B8%E6%9C%89; unionwsws={"devicefinger":"eidAacf98120e3s6/AVdYbJhR9ih+YP9biegFfwFXuM3P5fAWZ7PJIH3km/EKCbUBkSgiHptwoEIHgrXY8TLXzyF0eT+M10T4HP7Jq8/TYm2x9y8C/ps","jmafinger":"mp6gtBiHYP0O0ZUhI2zeJzSLtjzuZya_oYUL7JMiURv2HWVMdzuOqlVsLn_EgpJH8"}'
    # pc_client = pc_jd(ck, None)
    # print(get_useful_unpay(ck, '586', None))

    # print(order_qb(ck, '', '305', '13562365463'))
    # dnf80 = '200153769485'
    # amount = '80'
    # ck = ck.encode('utf-8').decode('latin-1')

    # print(create_order_knowkedge(ck, amount, DNF_SKUIDS[amount], '52313461', getip_uncheck()))
    # print(create_order_knowkedge(ck, amount, DNF_SKUIDS[amount], '52353462', None))
    # print(order_knowkedge(ck, '', '100', '2325463432'))
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=1c268751b4d3f5ec8ab255c01537372beaba8a259a056385a9bd95fcd26aa269940ec59282a6f63c01bd8878f9ecb403cb6b510cd1fa1d15aeca8ceb7551ed069dad0fe81d042f848ab3f603f57cf109'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=a8992807ee08692fed8c70bab00cf1bbb09d4f2da4444431ac45a211c20a4b5826cef82354c2cf661474df9c82776427122f64c16e897369932856dd0260db749dad0fe81d042f848ab3f603f57cf109'
    # print(get_real_url(ck, url))
    # print(get_real_qb(ck, '248592464389=105'))

    order_appstore(ck, '', '200')

    # print(query_order_qb(ck, '', DNF_SKUIDS['50'], '50'))
    # test(ck)
    # callback(ck, '247486125452', '123', '100')
    # clear_order(ck, '247761070918')
    # 06:50
    # 07:18
    # weixin_page_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=699d3620bdddb2cd1d9471b07eca4efedef02545e1061f0cc3119c5588f40c8c5893c0c857e10c555aecefb46ea62f518caa1476b7d3513d6242fad999a962a0c1b0c4ab88b7e0928f8872365c7dde35'
    # print(get_real_url(ck, weixin_page_url))
    # order_no = '247574887620'
    # callback(ck, order_no)
    # upload_order_result('124', '123','http://www.baidu.com', '100')