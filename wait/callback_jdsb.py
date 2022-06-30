# -*- coding: utf-8 -*-#

from base64 import encode
import json
import threading
from time import sleep, time
import requests
from jingdong import jd
from jingdong import get_ip

COMPLETED = 'completed'
COMPLETED_SORT_NAME = 'desc'

WAItOUT = 'waitOut'
WAItOUT_SORT_NAME = 'asc'

HADOUT = 'hadOut'
HADOUT_SORT_NAME = 'desc'

PAGE_SIZE = '30'

CALLBACK_IP = 'http://175.178.241.238:9999'

def LOG(text):
    print(text)
    pass

ck = 'shshshfpa=50181531-34cb-04cd-985f-51404241ba85-1646122231; shshshfpb=yCoeZPY7j8NPw5Hv1OIONXg; __jdu=1646122196094400153357; cid=9; webp=1; visitkey=20166911958496727; mba_muid=1646122196094400153357; sc_width=1920; __jdv=56585130|direct|-|none|-|1649397477224; pinId=u5hAPfor5Y1dd8wZH1Comw;  _vender_=TNK3O6PALVQGHEV76KASNL3M66TWEINRNPAN24NGLWKGQRXY2CORG35NAMDRMK3MTAIL5QLKA5WCEZDGQCRFT3MHQBRFOESRI2IQJTKP7QBLUREHV5UVZEMMX2TPO4NKRTC4UEHLLLQOA5ZILUPQBCOX7VHCBQGNVDFBBO6JSJOVBIM4FSHBOTIRNYITE5BBUEZCZETTRPRG7WPLH7RDGQTMKBAU6WKRKJQDLC6PHE66VC6MGF7FBFJH67T53YHR3MGRB5OZSQZPUXK7OTV5QTIP7NLKLLY3WYJPC4XXU6XVCP7N5QIKTWTEHPHQGKVREAXD3KNXDN5RI6TR6XAHU7ZH7NGHJNC24ZWEJW3TBR4STR3FX3WDJKATQGW6ZT5VZYD6MZOT7I46XBLKRWCRQWNBMQKR4MJHRULBANWF6UTHMNOVQBBLSSGJDY44LGNC23V2JMFUZMOJCWZIS6YK4NPFDV2YMBQG7EPFVAOEWNELCU55YP5A; areaId=52993; wq_logid=1649397609.1493934512; retina=1; __wga=1649397614031.1649397614031.1647247723728.1647247723728.1.2; share_cpin=; share_open_id=; share_gpin=; shareChannel=; source_module=; erp=; PPRD_P=UUID.1646122196094400153357-LOGID.1649397614042.1822441886; equipmentId=J7KXXLRCQODL6VMSKO2SRA55DRIFQL5VIEKFK2QGL2GZ2DLXF5PPWCLRCAUF2E42PJOL7DRCBTVILVRXKHVFWO6BBA; fingerprint=f4ce8f0e7b7e7492bdbcc8124810c0d0; deviceVersion=604.1; deviceOS=ios; deviceOSVersion=13.2.3; deviceName=Safari; sk_history=10047077591909,10046491419580,10046491008754,; language=zh_CN; csrf_token=6d90daff-0a72-49c0-9826-f1499fddc300; shshshfp=6847c45f6fed4cee468055de9c3d8e4a; ip_cityCode=52994; ipLoc-djd=1-72-55653-0; TrackID=1uFBMUYqwZ4PGdPCPMc-QGdAbkvvV188xRy1-1eDUBNwiQ8QQcWcnk1zOuu_eRLwvYhgE9me6OfpKSdwaLD9Wr62E88wIpHchGNY20minQtXc-zBE433igfWZdKtQuXSm; ceshi3.com=000; _tp=KQHfZxxtPCZ/+Pz7nAaqbBNAIYf6uWG6zXtblKyAPJk=; __jdc=191429163; _base_=YKH2KDFHMOZBLCUV7NSRBWQUJPBI7JIMU5R3EFJ5UDHJ5LCU7R2NILKK5UJ6GLA2RGYT464UKXAI5KK7PNC5B5UHJ2HVQ4ENFP57OC2H7JNOEO5EI3HE6QLN2CVY2O2BTCNE6YVKRXISUX7BSPDSWBJWYCS2GMV77CV7EE2SG4SOQWCP5WPWO6EFS7HEHMRWVKBRVHB33TFD5V6UX2VNVKPHEU3BO2FEED3OL6YZ2VDEFMFIYD337MUONOJRFN6ANJ5LBF4T2WJU5WOUCTSLMD2KWX4CZWCGAMZVNFDDJKXDEVH7G4OZZZJYSJEAJFZVHTFVCP6YNWCUGPQL2QSGWZIXBFWPDNGQFDQNK5GFZC3THSF2MNRTZ3IZ6HDDQN3X; _vender_new_=GI63BGTJFDBQ54O53F7UGHK57IBT4PTSPTSMPSO47UUQAWZSK3E7HCLN2IECNRQA4CQGIPYIHLEMA6STCVESYJAJ37GRIEZ7WHPCJALP6K6N6KGJSJM3I7L63P23HGHHB66YFQDZDTXE3UMO7BQPHQGYZVN7LSU6NF4KRDAR47BL5F7X5AQYWZW2Q63252ERSIADFYBBNFL3XPL7GNTNIFTAWESSNMCBFFJOHYQAKWST3KULLTB7D7C2K4AJQLTG7UDEFF3SY3HM3YOQ5P23IUHH2JIJ3BB7VVPVJUP6GU6OQL64PB4RDYOYD22B6AFMCOJO4I24I5TSQPLAS56USJOWDQRQEQHE3YYKV3NEZQPVUACOBUWKZRUGZ7YN6A2PEMBEBZG6GCVO3JGMD5NAATQNFQGGLHI4L4QJMRXFGZM3OQYLZJRS7JJS6XGTP34JOGOLFDALWLYLTOVZ6ZWBXWNSPJ5IFKIA4A4KJWEAOG5YGYQV7XXYEJEOUNWXHUVE66HHWNPJ3JJA5V6UX2VNVKPHEXQRSD4GNMQ76XABOSCQ7DMZAURHWUK2Z5E6D4KMJO3UTTGM3YK2DF2S7464SYZDFHH3ZRU7WA5GKJJKBZUGIX7NEO4HTOSAKGBGMJHTQHIAPXGTVLLZQPZNR5RPMWFGBQMIBSZ62YYYYNWWWZP7G4OPUADA; __jda=191429163.1646122196094400153357.1646122196.1649490485.1649499650.7; thor=57D0B19917EF65EA6DC7870DA155D0C583202A3CF3159819DD6A6E5E9A1B2ACAFD4E40808E452BAE9CE0197D3FEA50CD344F8F72CE872B2BFFA9ADD195DD2234750E54829746D70622437C2D26E8ED194C462774B87AC27C1CAFBBD9488125A4D8829BA5F9B2A7D6BD76EACF455A145D2BCE19A639054310E232AC377538B3C6; 3AB9D23F7A4B3C9B=J7KXXLRCQODL6VMSKO2SRA55DRIFQL5VIEKFK2QGL2GZ2DLXF5PPWCLRCAUF2E42PJOL7DRCBTVILVRXKHVFWO6BBA; _BELONG_CLIENT_=WPSC4XJXWK5USS4JNZY2X7VRLR5MCBKRSVHEXABGTHDGISIQK5YOLZUXYE7IOIM7MOKO74H6CRN6WHAAR4TMDV3XZWMXZRCRT5XRNE3V356BTOB2Y7LPK66VWQK6HPTGWVXIDXDCPVE3W5WMHAIO6AT2LX2XXVNUCXR34ZWFK6HY45CORGIKOSYDYZBF27WOKTUX6BS4FZMIJWNUX6CB4JAA25ZLF7ZEKYOO4QV5HTSBXGNRM3E242MBI6V5D4C5VJDQ3EOYCOW5BMTUJZACIBHXQFAVLRF76VQY5PNJGGJNBEZHSFYYJA3YORRT7FB5AHCOIFQKF3W5RWNUX6CB4JAA26JNMO7AYWNUPZF5HTSBXGNRM3E242MBI6V5D4C5VJDQ3EOYCOW5BWZDKMOJ5BS6II53ERY6ALV3ZWPF42L4CPUHEGPYIII35KDC4FCNVCORCXFD6IVNLBEDPB2GGP4UHWNRUDOQBDIW7RZJXBA2WV5ANZOTEGUCDWYRVQS2YUTIZNZ276PRYG4N56V6YTII7MBKBC7LYHO7C555HTSBXGNRM3E466AYN67DHWVM5HQFJ4NFDO5BSDWMVLLHJUD5NST6B6M3HZQONUI; b-sec=C654Y6DBMMGCISUJWRY5JEKI2HHXNG73HV6CVFBRIW7MT5PM3WFPS4EJBDGN7TC5PII47TRTMLEDS; __jdb=191429163.5.1646122196094400153357|7.1649499650'

# get one order status, for query order
def order_result(order_id):
    url = 'https://porder.shop.jd.com/order/orderlist'
    status = {}
    head = {
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': 'wxa_level=1; jxsid=16461221931604287111; webp=1; __jdv=122270672|direct|-|none|-|1646122196095; mba_muid=1646122196094400153357; visitkey=67233590100519535; sc_width=1920; shshshfpa=50181531-34cb-04cd-985f-51404241ba85-1646122231; equipmentId=LISWMCPVK2WW3QANZ3PB3YH4SXMKDVEON7I7DJ2LK255B3ZPCL5G5JOMEREKEICN7TOSKYK6F57423HCR7XAZGSOFQ; fingerprint=54564af864f11d78e7ae63e2ff116edd; deviceVersion=97.0.4692.71; deviceOS=; deviceOSVersion=; deviceName=Chrome; shshshfpb=yCoeZPY7j8NPw5Hv1OIONXg; wq_logid=1646122239.1677026648; share_cpin=; share_open_id=; share_gpin=; shareChannel=; source_module=; erp=; sk_history=10045398811484,100020207748,; retina=1; cid=3; __wga=1646125822115.1646125812501.1646122231217.1646122231217.2.2; PPRD_P=UUID.1646122196094400153357-LOGID.1646122240414.1135001550-CT.138054.1.1; jxsid_s_u=https://wqs.jd.com/order/n_detail_v2.shtml; jxsid_s_t=1646125822200; rurl=https://wqs.jd.com/order/n_detail_v2.shtml?deal_id=237024870847&new=1&ptag=138054.1.1&orderfrom=paysuc&jxsid=16461221931604287111&source=paysuc; shshshfp=21638afac46d22cb8137e27ec590360d; __jd_ref_cls=MLoginRegister_SMSVerificationAppear; areaId=6; ipLoc-djd=6-303-0-0; __jdu=1646122196094400153357; wlfstk_smdl=ka6fplfsojbzo3h45xbnmsve6wrjdk1y; TrackID=1J0dSWf1wLoC8CLc-4MfC_5PDtk9CeMez0HnPxoyahEXlUKZuelk2Xvkxa16zBPicYzl9TfekhG-LFZVTu9WwJjLFKUwxTC_3tfP9O_7Yt_kiVunTRjFaqqo7si78YA7V; pinId=Yk7HzQK3bbxFOgPHvFjotw; pin=anyouzizhanghao; unick=anyouzizhanghao; ceshi3.com=000; _tp=6K9lMB5ZmB9fvOaJUTlFyQ==; _pst=anyouzizhanghao; language=zh_CN; _vender_=TNK3O6PALVQGGGJTPU4CVADIXEBTNNTXDSY6BLNTTGYTK3SQPFKA2JKDVRZVIET6GS2IN7AUMR4SDDV3ZF5XQSJCY5QC4BOI4HHNOST4LPXA4Q7DMEVTCPO4RBSWAIEN6WK5LLOVNMCZYUYDWLYXCKNVXA7UWJVUAUO3RW653TLN7CAXV4WGN26H3G7KKNDLSDTMSWGJQP3ZT4RF7ZWBF64PXPUNPE4HX7RVGN5HIOCHIDOMTRHAHM6OB3MI7NAFZW4SGOILVSKSJ5TT36ENGPI4SVT6GTISHBALGS4KWI4C2Q6JLCSMJK5EW4MDSF26RTK2HKG2TO7YNVFVW3AKNPW2LTLXDXG437VMTXF2SUTVQYNJ6AET4W36A4YP3NOOETSAI2B5EYHEUERQZWDV23MRQ6AFZJWYC7UCGWRP4T4XRB77D6WDCMKD6B3SO7WSNQVVAWFRIXYQKR653JCT6O2OYIIYW7LTTKIRM4LRSSSVOVUFIQPCMOEILTFRQNS2I37WSSK225CJE; universityLanguage=zh_CN; xue_userTypeCookieName4585b6ca7e6e962bedb8bada182c5d7d="{\"1\":\"POP\"}"; xue_userTypePageCookieName4585b6ca7e6e962bedb8bada182c5d7d=1; is_sz_old_version=false; __jda=191429163.1646122196094400153357.1646122196.1646125812.1646138589.3; __jdc=191429163; thor=E7BF9ED92E0310AFB8A7A0477F2A4396B8B25AD901A36802870AC4A6785E49888314F613BF2C65EE342EEE889A886A57F9FB98FBBA62B503D75A7F1143CCE38447848DCD36706195853502E7B6D96D4ECCA783FCE5602404DB42306B98C3308DBB62B9E669206113EC88A4AB47295BB5D79E2CC7A3C93E990E6E841229E67D8F34AF626B4F2CE04C467D1FD6CC7F5F81CFE675A6E27B4F1450647FE4705CD936; __jdb=191429163.15.1646122196094400153357|3.1646138589; 3AB9D23F7A4B3C9B=J7KXXLRCQODL6VMSKO2SRA55DRIFQL5VIEKFK2QGL2GZ2DLXF5PPWCLRCAUF2E42PJOL7DRCBTVILVRXKHVFWO6BBA; _BELONG_CLIENT_=WPSC4XJXWK5USS4JNZY2X7VRLR5MCBKRSVHEXABGTHDGISIQK5YOLZUXYE7IOIM7MOKO74H6CRN6WHAAR4TMDV3XZWMXZRCRT5XRNE3V356BTOB2Y7LPK66VWQK6HPTGWVXIDXDCPVE3W5WMHAIO6AT2LX2XXVNUCXR34ZWFK6HY45CORGIKOSYDYZBF27WOKTUX6BS4FZMIJWNUX6CB4JAA25ZLF7ZEKYOO4QV5HTSBXGNRM3E242MBI6V5D4C5VJDQ3EOYCOW5BMTUJZACIBHXQFAVLRF76VQY5PNJGGJNBEZHSFYYJA3YORRT7FB5AHCOIFQKF3W5RWNUX6CB4JAA26JNMO7AYWNUPZF5HTSBXGNRM3E242MBI6V5D4C5VJDQ3EOYCOW5BWZDKMOJ5BS6II53ERY6ALV3ZWPF42L4CPUHEGPYIII35KDC4FCNVCORCXFD6IVNLBEDPB2GGP4UHWNRUDOQBDIW7RZJXBA2WV5ANZOTEGUCDWYRVQS2YUTIZNZ276PRYG4N56V6YTII7MBKBC7LYHO7C555HTSBXGNRM3E466AYN67DHWVM5HQFJ4NFDO5BSIQZEJZFSPDXM5CBBFQRKDS75MQ; _base_=YKH2KDFHMOZBLCUV7NSRBWQUJPBI7JIMU5R3EFJ5UDHJ5LCU7R2NILKK5UJ6GLA2RGYT464UKXAI5KK7PNC5B5UHJ2HVQ4ENFP57OC76OJ3QRHKHZLBOBFIHQESBJDEVTCNE6YVKRXISUEFRLMM3A5GN3GUVH46IGQS4XX2SG4SOQWCP5WPWO6EFS7HEHMRWVKBRVHB33TFD5CG6S5TI4LAIAEU2WY74DWFDQ6BE3G6RXFLELSGCNOZTRATM2NB2UWGDXYAFY35T3VHDP3Y4KLYB2YFHVCALOLV5NX7QO4R3BGIJOKGV4ZFOTNBBYBIZRXZYERXXIG6ATVPUY5SGOFWEGUHBVUS26JCPWV6DI5MCTVQUE7RYZYHTHIXOTJHD7EH2RD2AHHNOW; b-sec=BVGQKA5GVM7GKGFDBXIOKHFXJOZJNOS4RFWLWVH6P5RGFTMZNUXAXRTIKVMSYAZLT2IQEJDWS5QSU; _vender_new_=GI63BGTJFDBQ4P7O2PX6AXDABNZCUTHAIHEDTAHISEVBM4JS4TRSDZQZONZ4MBDHT63R4KOSA64MW6FJFSU6UJ7NKNUFHCXGGYIHCDZGFSJR4DW66KLBDAAXVDD4Y3SEHQR5IJCQIJMF2OFCK7TTAESTITC7YECADJUCKC6WWMFWVMEE6L7ZSD7O62NYJFAAE6CR7C5SW443GXNQCAXJOYKQSHX3OC7V64PBWNPTLANN3BMVYXRBNW64HXDOYD4SG5MLIPLVK4YWFDFJKEWT6VWURWXPNP22JJH6Q43QTABUNKJIOUMOWBO5USH5IR6F25ZGKWZ6H5SK2FPRRTVQWT2PKX4OYBKVM63DJBL7LBZGTQVLUNJNXFLILXNJFLASV2JWVIG7FORUJ6G42VFKKGSFG3NZK2C53KJKYEVOSNVKBXZLUNCHQEEL2P5CPSEE2GA6T3MGTLRVOPMH7LK2QFLH67GUZEDNXWXWCDEBHL53OBON7VTXATZ2ZOB4Q7VPD72JCBF33JL3NN43242BTRDPKK36ACTKXITPCTXWR3X26TWKTGW2Y36XOX54Y4MIFPZO5HZDA27IG7Q33CIHUZ6QLSEYTJJERPAWOJ7J3NURNXQPDLWAQDBKZVGRGP33FF7YNDQR3KSAVYMP5UF3ACEWDB6O53WHVNKD6JSQ4TGSEFZJJNBJDGO4VR4GOVPQ4FNIT374F4VDI'
    }
    data = '{"current":1,"pageSize":10,"sortName":"desc","orderId":"' + order_id + '","skuName":"","orderCreateDateRange":[],' + \
        '"orderCompleteDateRange":[],"receiverName":"","receiverTel":"","userPin":"","skuId":"","logiNo":"","paymentType":"",' + \
        '"orderType":"","orderSource":"","deliveryType":"","storeId":"","huoHao":"","orderStatusArray":[],"o2oStoreIds":null,"selectedTabName":"allOrders"}'
    res = requests.post(url, headers=head, data=data)
    print(res.text)
    if res.status_code == 200:
        ret_json = json.loads(res.text)
        for order in ret_json['orderList']:
            status['orderStatus'] = order['orderStatus']
            status['orderStatusStrCN'] = order['orderStatusStrCN']
            return status

# get orders status, for callback
def order_list(selectedTabName, pageSize, sortName):
    print('==== order_list ====')
    url = 'https://porder.shop.jd.com/order/orderlist'
    data = '{"current":1,"pageSize":' + pageSize + ',"selectedTabName":"' + selectedTabName + '","sortName":"' + sortName + '"}'
    head = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': ck,
        'Referer': 'https://porder.shop.jd.com/order/orderlist/completed'
    }
    res = requests.post(url, headers=head, data=data)
    print(res.text)
    if res.status_code == 200:
        return json.loads(res.text)['orderList']

def callback(order_id):
    url = CALLBACK_IP + '/api/pay/callBack?offOrderNo=' + str(order_id)
    head = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    print(url)
    res = requests.get(url, headers=head)
    LOG('callback:' + str(order_id) + res.text)
    if 'not exist' in res.text:
        return False
    return True

def out(sku_id, order_id):
    url = 'https://porder.shop.jd.com/order/stockOut/sopSingle/'
    data = '{"skuIds":[' + sku_id + '],"orderId":' + order_id + ',"venderTaskAddressId":20443705,"isEpsOut":0,' + \
        '"deliveryNumbers":[{"deliveryId":332098,"deliveryNums":[]}]}'
    head = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': ck
    }
    res = requests.post(url, headers=head, data=data)
    if res.status_code == 200:
        print(res.text)

def get_ck(account):
    url = CALLBACK_IP + '/api/get/getCk?account=' + account
    print('================', url)
    head = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    # print(url)
    res = requests.get(url, headers=head)
    if res.status_code == 200:
        print('getck: ============', res.text)
        ret_json = json.loads(res.text)
        if ret_json['message'] == 'success':
            return ret_json['data']
        return None
    return None
    # ck = 'guid=f243fbdb7be66583bad34c1a1dc0a94dfa62409992e1d2ec8ec7c5b50e1e7b40; pwdt_id=jd_uPvFzRIHqogg; sid=b87fe50f82219ae1c377ad90fd88f4bw; pin=jd_uPvFzRIHqogg; wskey=AAJhVb2zAEBeaqcrEXYNwJ_lIJvO_GSMhSu5KLcj2FJnP1NW6L3UGHJQijkuuIeGpHdYrYPKfVrkOREw7ZI7Nwb6Zv6O0jTz; pt_pin=jd_uPvFzRIHqogg;pt_key=app_openAAJiHg-fADDFXZDmJf2RAX-xHrlgfkkw5C3qRombYHVqD-tWVUX9bhG2TzGu8cjcuMuU2jtFTII;'
    # return ck

def waitout():
    print('===== waitout =====')
    try:
        waitout_l = order_list(WAItOUT, PAGE_SIZE, WAItOUT_SORT_NAME)
        for order in waitout_l:
            if order['orderStatusStrCN'] == '等待出库' and order['orderStatus'] == 8:
                order_id = str(order['orderId'])
                for i in order['orderItems']:
                    sku_id = str(i['skuId'])
                    out(sku_id, order_id)
    except:
        print('waitout error')


def waitout_callback():
    try:
        waitout_l = order_list(WAItOUT, PAGE_SIZE, WAItOUT_SORT_NAME)
        for order in waitout_l:
            if order['orderStatusStrCN'] == '等待出库' and order['orderStatus'] == 8:
                order_id = str(order['orderId'])
                callback(order_id)
    except:
        print('waitout error')

def completed():
    try:
        threads = []
        ids = []
        completed_l = order_list(COMPLETED, '15', COMPLETED_SORT_NAME)
        for order in completed_l:
            # print(order)
            if order['orderStatusStrCN'] == '完成' and order['orderStatus'] == 19:
                try:
                    ids.append(order['orderId'])
                except:
                    LOG('callback error:' + str(order['orderId']))
        print(ids)
        for id in ids:
            t = threading.Thread(target=callback, args=(id, ))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except:
        print('completed error')
    print('=========================================================')


def completed_callback():
    try:
        threads = []
        ids = []
        completed_l = order_list(COMPLETED, PAGE_SIZE, COMPLETED_SORT_NAME)
        for order in completed_l:
            # print(order)
            if order['orderStatusStrCN'] == '完成' and order['orderStatus'] == 19:
                try:
                    ids.append(order['orderId'])
                except:
                    LOG('callback error:' + str(order['orderId']))
        print(ids)
        for id in ids:
            callback(id)
            sleep(1)
            # t = threading.Thread(target=callback, args=(id, ))
            # threads.append(t)
        # for t in threads:
            # t.start()
        # for t in threads:
            # t.join()
    except Exception as e:
        print(e.with_traceback())
        print('completed error')
    print('=========================================================')


def hadout():
    try:
        hadout_l = order_list(HADOUT, PAGE_SIZE, HADOUT_SORT_NAME)
        print(hadout_l)
        for order in hadout_l:   
            # recomform
            if order['orderStatusStrCN'] == '等待确认收货' and order['orderStatus'] == 16:
                account = order['userPin']
                print('============', account)
                confirm_recv(account, str(order['orderId']))
    except:
        print('hadout error')
    # ck = get_ck('')
    # order_id = '237057117434'
    # confirm_recv(ck, order_id)

def callback_task():
    while(True):
        try:
            threads = []
            # threads.append(threading.Thread(target=waitout_callback()))
            # threads.append(threading.Thread(target=hadout))
            # threads.append(threading.Thread(target=completed))
            threads.append(threading.Thread(target=completed_callback))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            sleep(30)
        except:
            pass

def confirm_recv(account, order_id):
    ck = get_ck(account)
    print(ck)
    if ck == None:
        return None
    ip = get_ip()
    print('confirm_recv')
    jd_client = jd(ck, ip)
    jd_client.confirm_recv(order_id)

   

def query_order(order_id):
    status = order_result(order_id)
    if status['orderStatus'] == '完成' and status['orderStatus'] == 19:
        # callback
        pass

id = '239888608519'

# order_list(s, '30')

if __name__ == '__main__':
    callback_task()
    # order_list(COMPLETED, '15', COMPLETED_SORT_NAME)