from time import sleep
import requests


def query(id):
    url = 'http://175.178.195.147:9191/admin/order/check.html?id=' + str(id)
    print(url)
    head = {
        'Cookie': 'PHPSESSID=r99ch0qas1h2mv60gvviga6eng',
        'X-Requested-With': 'XMLHttpRequest'
    }
    res = requests.get(url, headers=head)
    print(res.text)


id = 68713
for i in range(1000):
    query(id - i)
    sleep(0.05)