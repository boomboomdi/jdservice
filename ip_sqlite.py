import sqlite3
from tools import LOG_D, LOG_E


db = 'ip.db'

class ip_sql:

    def __init__(self) -> None:
        self.conn = sqlite3.connect(db, check_same_thread=False) 

    def __del__(self):
        self.conn.close()

    def insert_ip(self, account, ip):
        LOG_D(account + ' ' + ip)
        try:
            cursor = self.conn.cursor()
            cursor.execute('insert into ips (ip, account) values (\'' + ip + '\', \'' + account + '\')')
        except Exception as e:
            LOG_E(e)
        finally:
            self.conn.commit()
            cursor.close()

    def delete_ip(self, account):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM ips WHERE account=' + account)
        except Exception as e:
            LOG_E(e)
        finally:
            self.conn.commit()
            cursor.close()

    def search_ip(self, account):
        try:
            cursor = self.conn.cursor()
            cursor.execute('select ip from ips where account=' + '\'' + account + '\'')
            values = cursor.fetchall()
            return values[0][0]
        except Exception as e:
            LOG_E(e)
            return None
        finally:
            self.conn.commit()
            cursor.close()

    def update_ip(self, account, ip):
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE ips SET ip=\'' + ip + '\' WHERE account=' + '\'' + account + '\'')
        except Exception as e:
            LOG_E(e)
        finally:
            self.conn.commit()
            cursor.close()

if __name__ == '__main__':
    sql = ip_sql()
    # sql.insert_ip('13456523', '127.0.0.2')
    # sql.delete_ip('13456523')
    # sql.update_ip('13456523', '1222.33.22.33')
    print(sql.search_ip('13456523'))
    pass