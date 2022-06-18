
if __name__ == '__main__':
    oldck_f = open('oldck', encoding='utf-8')
    newck_f = open('newck', 'w', encoding='utf-8')
    # print(address_f.readlines())
    for line in oldck_f.readlines():
        ck = line.replace('\n', '')
        newck = ''
        for i in ck.split(';'):
            if 'pin=' in i or 'wskey=' in i:
                newck = newck + i.replace(' ', '') + '; '
        newck_f.write(newck + '\n')
    print('finish')