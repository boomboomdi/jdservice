from re import I


import requests

f_kami = open('kami_100.txt', 'w')

if __name__ == '__main__':
    url = 'http://175.178.195.147:9191/admin/cammy/index?page=1&limit=1500'
    head = {
        'Cookie': 'PHPSESSID=3h079gujknvr3iql69np5tjqu1',
        'Referer':'http://175.178.195.147:9191/admin/cammy/index?mpi=m-p-i-1',
        'X-Requested-With':'XMLHttpRequest'
    }
    res = requests.get(url, headers=head)
    print(len(res.text))
    total = 0
    for i in res.json()['data']:
        try:
            print(i)
            if i['amount'] == 100:
                f_kami.write(str(i['amount']) + ' ' + i['card_name'] + ' ' + i['card_password'] + ' ' + i['add_time'] + '\n')
            total += int(i['amount'])
        except:
            print(i)
    print(total)