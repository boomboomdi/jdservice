import base64
from ctypes.wintypes import LONG
import json
import requests
from time import time
from urllib.parse import quote
import tools
from jingdong import LOG, jd
from ip_sqlite import ip_sql

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
            res = requests.get(url, headers=head, proxies=self.proxy)
            # print(res.text)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if 'orderParam.winId' in line:
                    line = line.replace(' ', '')
                    win_id = line.replace('<inputtype="hidden"id="winId_"name="orderParam.winId"value="', '')   \
                                .replace('"attr="exclu"sync="true"/>', '')
                    return SUCCESS, win_id
            return CK_UNVALUE, None
        return RET_CODE_ERROR, None

    def submit_order(self, skuid, win_id):
        url = 'https://card.jd.com/json/order_syncSubmitOrder.action'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.ck
        }
        data = 'webFeOrderInfo.buyNum=1&webFeOrderInfo.payRuleInfo=&webFeOrderInfo.cardNewVersion=1' + \
            '&webFeOrderInfo.payMode=0&webFeOrderInfo.moneyBasic=0&webFeOrderInfo.integralBasic=0&' + \
            'webFeOrderInfo.payPwd=&webFeOrderInfo.couponIds=&webFeOrderInfo.dongCouponIds=&webFeOrderInfo.amountPayable=' + amount + '.00' + \
            '&webFeOrderInfo.couponsAmount=&webFeOrderInfo.jbeanAmount=&orderParam.useBean=&orderParam.gameAreaSrv=2&webFeOrderInfo.skuId=' + \
            skuid + '&webFeOrderInfo.categoryId=13759&orderParam.winId=' + win_id + '&orderParam.secondSource=0&webFeOrderInfo.eid='
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            ret_json = res.json()
            tools.LOG_D(ret_json)
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
            res = requests.get(url, headers=head, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if 'repeatKey' in line:
                    repeakey = line.replace(' ', '').replace('<inputtype="hidden"name="repeatKey"value="', '').replace('">', '').replace('\r', '')
                    return SUCCESS, repeakey
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



amount = '200.00'

APPSTORE_SKUIDS = {
    '100': '11183343342',
    '200': '',
    '300': '',
    '500': '' 
}

QB_SKUIDS = {
    '105': '200145365539'
}


def create_order_appstore(ck, order_me, amount, proxy):
    tools.LOG_D('create_order_appstore')
    pc_client = pc_jd(ck, proxy)
    code, win_id = pc_client.order_place(APPSTORE_SKUIDS[amount])
    if code != SUCCESS:
        return code, None, None
    code, order_no = pc_client.submit_order(APPSTORE_SKUIDS[amount], win_id)
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
    if code != SUCCESS:
        return code, None, None
    code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
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



def create_order_qb(ck, order_me, amount, qq):
    pc_client = pc_jd(ck)
    app_client = jd(ck)
    code, repeatkey = pc_client.qb_get_repeatkey(QB_SKUIDS[amount])
    print(repeatkey)
    if code != SUCCESS:
        pass   
    code, cashier_url = pc_client.qb_submit_order(amount, repeatkey, qq)
    for i in cashier_url.split('?')[1].split('&'):
        if 'orderId' in i:
            order_no = i.split('=')[1]
    print(order_no)
    print(cashier_url)
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        pass
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        pass
    code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    if code != SUCCESS:
        pass
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    print(img_url)
    # app_client.gen_token()
    # img_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=a78134e5944ce6619b7a54d2649898586b4776d24acc654320214577da92c7cbcd92cf045f5eab8bd50492fd2bf6035d45eb0db7d81e99916b6e43eeab562ba13b9487beaf0dcae568f49411ab2e64b3'
    # code, token  = app_client.gen_token(img_url)
    # pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
    # print(pay_url)


def get_real_url(ck, img_url):
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    account = tools.get_jd_account(ck)
    proxy = ip_sql().search_ip(account)
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
    # ck = '__jdv=122270672|direct|-|none|-|1653684678322; shshshfpa=54b03d9b-9e14-a6f8-a6a4-74bc09ff1d79-1653684688; shshshfpb=kaxjITozukJzQKR2yTHvVkQ; __jdu=1653684678321815288407; areaId=5; ipLoc-djd=5-142-0-0; shshshfp=c8154d5c31b835b717a87e7197043139; TrackID=1LuiQoeX1l2uYaXGl4pWdvnKv07C5Ze_pbxbupAQe_P4b2oWYyGf9RImyGbJawpljoeJ_BaNMQoNSDIsmyDAWvhyHnwkVSj1zS6ynjxYMOGqHxNs5YeSHYWKGTYCyLdFB; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d+SKBX0iW+Qy5xFBy0C7MU1+oxmN9c=; _pst=jd_4d9b500034155; user-key=74aab15f-c2ad-432d-a388-6fe482a10e4a; cn=1; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A745F29F8513D02C2A15A9CCD823FCD255B1DC17C702797DE4A2B40A5749B0F9620A489FDFC834F465233DE7A1551BB66003DDFC7F1F3A45DEAA234DE753409D1F9C65C28D6027A43D1F6D4ED3F5BC13A7932654F616D6B971141147D75CB794FBE48D35E812D23B52180180F7DC923A237C9348AD1CE3B6A6C9CA9F983D6CE670F1; shshshsID=f7275fa22194787a412431d3e88b314b_1_1653763565833; __jda=122270672.1653684678321815288407.1653684678.1653752556.1653763559.4; __jdb=122270672.2.1653684678321815288407|4.1653763559; __jdc=122270672; 3AB9D23F7A4B3C9B=RI6THBNZSP72TJ56KEHDNOJWYNEOHHKWSYJDG2HCFCH5LHJBYSLIHQFOTUMOEGVVCPKBWM56QOYAETL5O3BOYIYDQ4'
    # ck = ck.encode('utf-8')
    pc_client = pc_jd(ck, None)
    qr_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=8b2aad72668890803d70ddfce9341c399254da213289d54ee189d9646867fd9212c0ad4b2ec950030cadfbec772745c74270384c890ea00f51a93f8f8e125670aef277307a0ff5ecf6b214ab52cebebe34af41273e8fe32548929db9a7001d32'
    get_real_url(ck, qr_url)
    # pc_client.get_order_list()
    # pc_client.get_order_status('247875909217')
    # pc_client.get_order_status('247775877802')

    # ck = '__jdv=122270672|direct|-|none|-|1653684678322; shshshfpa=54b03d9b-9e14-a6f8-a6a4-74bc09ff1d79-1653684688; shshshfpb=kaxjITozukJzQKR2yTHvVkQ; __jdu=1653684678321815288407; areaId=5; ipLoc-djd=5-142-0-0; shshshfp=c8154d5c31b835b717a87e7197043139; TrackID=1LuiQoeX1l2uYaXGl4pWdvnKv07C5Ze_pbxbupAQe_P4b2oWYyGf9RImyGbJawpljoeJ_BaNMQoNSDIsmyDAWvhyHnwkVSj1zS6ynjxYMOGqHxNs5YeSHYWKGTYCyLdFB; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A745F29F8513D02C2A15A9CCD823FCD255B11986E25C463239E99B7788EBDC564FD4C47115D458A2FC05AC7987D3EAAADB85ACC5A099C3500AF2A2973224784AE4781CAC2ADEA905C12B9FAE4E5BED4453097A2EF8126FCD6BAA865E00E5B6A3B206768F89D9EE140929D54137ACB5919123555CC657DA472D929DF0D0F26C96B0B0; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d+SKBX0iW+Qy5xFBy0C7MU1+oxmN9c=; _pst=jd_4d9b500034155; shshshsID=9c7467be5e15b1258194cdadfc730cfa_2_1653750129706; user-key=74aab15f-c2ad-432d-a388-6fe482a10e4a; cn=1; __jda=122270672.1653684678321815288407.1653684678.1653684678.1653749827.2; __jdb=122270672.6.1653684678321815288407|2.1653749827; __jdc=122270672; 3AB9D23F7A4B3C9B=RI6THBNZSP72TJ56KEHDNOJWYNEOHHKWSYJDG2HCFCH5LHJBYSLIHQFOTUMOEGVVCPKBWM56QOYAETL5O3BOYIYDQ4'
    # test_order_appstore(ck, '123', '100')
    # create_order_appstore(ck, '123', '100', None)
    # query_order(ck, '247775877802')
    # create_order_qb(ck, '', '105', '123542321')
    # test(ck)
    # callback(ck, '247486125452', '123', '100')
    # clear_order(ck, '247761070918')
    # 06:50
    # 07:18
    # weixin_page_url = 'https://pcashier.jd.com/weixin/weixinPage?cashierId=1&orderId=247716765350&sign=6f990a7f03bf3a3c55d4eb6eb49e63bb&appId=pcashier&orderId=247716765350&paySign=a739f0bee0d3894c9471eb0010d483c8148a9d1151bec320a35c1c1541a5fcf63b024afc97cf06a83dc1d8d04191e8e1ed46edc520ef9d2df3ed474aa7305a271aa6febd443a78c9591e5ea55ba8dd7c7c18e47c3a1ef8d7dcdb64fc18bfb8a79f65b4df56ce0d3800232607d5d57865182a9dcd5baabfea59f1a0338ad910e842e573337e4591a327c211d7c5183316ed39e1b834268cdd122219b557856de7fa3850777bd32a3ede1eb2727929646709a2afffc9647da3e1bb1d827665c22c32f4961caff000ce107bfcbef577006d3cc9901ea30739f8e2fcac9eb7d8d567'
    # get_real_url(ck, weixin_page_url)
    # order_no = '247574887620'
    # callback(ck, order_no)
    # upload_order_result('124', '123','http://www.baidu.com', '100')