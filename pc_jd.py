import base64
from email import header
import json
import requests
from time import time
from urllib.parse import quote
import tools
from jingdong import LOG, jd

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


    def get_order_status(self, order_no):
        query_list = '[{"orderType":34,"erpOrderId":"' + order_no + '"}]'
        url = 'https://ordergw.jd.com/orderCenter/app/1.0/?callback=jQuery7859047&queryList=' + quote(query_list) + '&_=' + str(int(time())) + '049'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
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
    pc_client = pc_jd(ck)
    app_client = jd(ck)
    retry_time = 0
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
    # for i in range(3):
        # if code == NETWOTK_ERROR:
            # proxy = None
            # code, order_no, img_url = create_order_appstore(ck, order_me, amount, proxy)
        # elif code == CK_UNVALUE:
            # ck_status = '0'
        # elif code == SUCCESS:
            # break
        # i += 1
    # tools.LOG_D(img_url)
    # upload_order_result(order_me, order_no, img_url, amount, ck_status)
    upload_order_result(order_me, '', '', amount, ck_status)

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


def get_real_url(ck, weixin_page_url):
    pc_client = pc_jd(ck)
    app_client = jd(ck)
    for i in weixin_page_url.split('?')[1].split('&'):
        if 'orderId' in i:
            order_no = i.split('=')[1]
        if 'paySign' in i:
            pay_sign = i.split('=')[1]
    code, image_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        pass
    code, token = app_client.gen_token(quote(image_url, safe=''))
    if code != SUCCESS:
        pass
    pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token
    print(pay_url)

def upload_callback_result(result):
    # url = '/api/ordernotify/notifyOrderStatus0069'
    print(result)
    return True

def upload_order_result(order_me, order_no, img_url, amount, ck_status):
    # result = {
        # 'prepare_status': '0',
        # 'ck_status': ck_status,
        # 'order_me': order_me,
        # 'order_pay': order_no,
        # 'amount': amount,
        # 'qr_url': img_url
    # }
    # if img_url != None and order_no != None:
        # result['prepare_status'] = '1'
    url = 'http://175.178.195.147:9191/api/preparenotify/notifyjdurl0069'
    head = {
        'content-type': 'application/json'
    }
    # print(json.dumps(result))
    data = '{"prepare_status": "1", "ck_status": "1", "order_me": "' + order_me + '", "order_pay": "247775877802", "amount": "100", "qr_url": "https://pcashier.jd.com/image/virtualH5Pay?sign=d6e2869be73c243c560393c09a7182ca89a1ed515bb088cc3ca08658daa14a0a6d4f8399eb23e3c53f93c113731f840e7fbd03300ab7e2ace58ab06ead2a3128ca6ce6e5705410517c18220000f4be1334af41273e8fe32548929db9a7001d32"}'
    # res = requests.post(url, headers=head, data=json.dumps(result))
    res = requests.post(url, headers=head, data=data)
    print(res.text)

    
def handle_fail(code):
    pass


def test(ck):
    pc_client = pc_jd(ck)
    pc_client.get_order_url('247682795586')

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
    pc_client = pc_jd(ck)
    code, order_status, status_name = pc_client.get_order_status(order_no)
    if code != SUCCESS:
        pass
    if order_status == True and status_name == '已完成':
        code, card_id, card_key, pay_time = pc_client.get_kami(order_no)
        print(card_id, card_key, pay_time)
        result['check_status'] = '1'
        result['pay_status'] = '1'
        result['ck_status'] = '1'
        result['time'] = pay_time
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
    upload_callback_result(result)

def clear_order(ck, order_no):
    pc_client = pc_jd(ck)
    passkey = pc_client.get_passkey(order_no)
    tools.LOG_D(passkey)
    code, status = pc_client.recycle_order(order_no, passkey)
    if code != SUCCESS:
        pass
    if status == True:
        code, passkey = pc_client.get_recycle_passkey(order_no)
        if code != SUCCESS:
            pass
        pc_client.delete_order(order_no, passkey)


if __name__=='__main__':
    # ck = 'pin=bb17108392702; wskey=AAJijhQVAEAUuK5yxaGAiLVqJz3vy2eDcw4Mbk13xp2KJWAMbw8Ni2ihRP8D9e-mIYOsLhbPWOLy8edS4GfgUOx6trKMts4f; __jdv=76161171|direct|-|none|-|1653475472625; __jdu=1653475472623645022175; areaId=5; ipLoc-djd=5-142-0-0; shshshfp=c8154d5c31b835b717a87e7197043139; shshshfpa=c4e699b6-78cd-5d72-fc82-0464edc0b499-1653475476; shshshfpb=dNdB1ULltKqRZUn3U3kSZ1g; TrackID=18oAEvWCESKwvCuZTMo9UEpieA7cIkc8fA4W6voDJHt2LMMaQXjGq49NKPbG3KRXgURDbZgVGIy_FOFTvSVYIe3X40H_Y0WRKQs-YGdTGUVCjIwSt8oIhXhw1fczaSzGr; pinId=hZVnPybRNrtIM016vp53LQ; pin=bb17108392702; unick=bb17108392702; ceshi3.com=000; _tp=LSfrzCZhIkpYM+Vd6iAGJQ==; _pst=bb17108392702; bjd.advert.popup=d34dd1b9cb1caaaad0c408ab72e7615d; qd_ad=-|-|-|-|0; qd_uid=L3LM5W8G-C09N0FN6RODT8GLSSTCG; qd_fs=1653484809324; qd_ts=1653484809324; qd_ls=1653484809324; qd_sq=2; qd_sid=L3LM5W8G-C09N0FN6RODT8GLSSTCG-2; _distM=247703057827; __jda=122270672.1653475472623645022175.1653475473.1653484717.1653498288.3; __jdb=122270672.7.1653475472623645022175|3.1653498288; __jdc=122270672; thor=5B960A72EDEABC412FA1D4E520C1BAE311222104FDB0B15D2E58892276E8C63CE4DE693C0C75A7449351710A7E23605E28CCA52B810D9167E8BB81CFB5CF89007E75EBEAE6737E0075B1486A656A9500BC332BAC42624A3C71E0491288E810BF86CBDF2DCC52F4BBAD1E2CCA2A689AC89183E2DE66E04A87897CFAF22615DECA421E391A0010E64D0DE1E67EAD55CA4C; 3AB9D23F7A4B3C9B=RI6THBNZSP72TJ56KEHDNOJWYNEOHHKWSYJDG2HCFCH5LHJBYSLIHQFOTUMOEGVVCPKBWM56QOYAETL5O3BOYIYDQ4'
    ck = '__jda=24961467.1653564699911433506861.1653564700.1653564700.1653564700.1; __jdc=24961467; __jdv=76161171|direct|-|none|-|1653564699911; __jdu=1653564699911433506861; areaId=5; ipLoc-djd=5-142-42547-54561; shshshfp=ce4ef42540f107788900abe5857d0831; shshshfpa=9b48a7ff-a5fe-ebd3-ae89-5ddc92ab7a40-1653564700; shshshfpb=uJucIkGjIbRrTIaRGiKbuoA; wlfstk_smdl=ael4j53f8927i4os0fym9dnt9x96mqwx; TrackID=1u1ZKFeg4WAejJoSajMtnrdM0yuJbawO4WLKgQQwbuqSvNatjC1q4wcABqdfTNp99FvLOzU5GAkKTOnWOXdj9SpEeKQt20gYJMBWYDxPkKunqhC49vf8nfpiV8Utc3-yakbc4mJo1xEdtBGtoL0v6Nw; thor=5BC3BA255AE4A8428C911AF1E3476BE39C8881EEC0396A93799EF09D029CF387D538361D559919B696CD28205C35E585CC1B4B0A03F09A6969DBE4536CA3E0D572D28F381202266CA06DD238921FA7223A7AC29E42653FE76397F6401E49E6F61726ED9DF1BEB4CC561BC4622BE873D0D937A621F9769BA00A3760D30D2C1EF0F7E1D1CAEDD0C3DF2B7132BBF587C7B4; pinId=m4W1ON9HdhVnOt3b2SjWeAVIxgkk_fOxHYBiJEn8G34; pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E8%8A%B1%E4%B9%8B%E9%9F%B5%E5%9B%AD%E8%89%BA%E6%9C%89; unick=%E8%AE%B7%E6%B2%B3%E5%B8%82%E8%8A%B1%E4%B9%8B%E9%9F%B5%E5%9B%AD%E8%89%BA%E6%9C%89; ceshi3.com=000; _tp=3QbDybAYBdiCsmqHk4hDu%2Fi5MtvWn3JmxO0ZYRfDzOmbwWBhYg%2Bsib2rqCduBPz%2FrwOqYY2RlIHypwBX5oMq2o608aHs6UeSJt3KOtaix8d0bYQ34i1KM2bDW%2FSC0JvC; _pst=%E8%AE%B7%E6%B2%B3%E5%B8%82%E8%8A%B1%E4%B9%8B%E9%9F%B5%E5%9B%AD%E8%89%BA%E6%9C%89; bjd.advert.popup=8f3d58ac337c2ee479ab1507fb67fd6a; ip_cityCode=142; _distM=247761187688; 3AB9D23F7A4B3C9B=UKTIOLLP753IGSUPUQHSSQBHBY2Y5KIO6RHGFCUW3VJUYI3XCRDBBKM6TBNO5HXP5IKJTEXZ6P6HOYG3LUVWVOOMF4;'
    order_appstore(ck, '123', '100')
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