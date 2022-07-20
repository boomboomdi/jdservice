import sqlite3
from weakref import proxy
# from tools import LOG_D, LOG_E


db = 'ip.db'

class proxy_sql:

    def __init__(self) -> None:
        self.conn = sqlite3.connect(db, check_same_thread=False) 

    def __del__(self):
        self.conn.close()

    def insert_area(self, id, pname, pcode, cname, ccode):
        try:
            cursor = self.conn.cursor()
            cursor.execute('insert into proxy (id, provice, provice_code, city, city_code) values (\'' + id + '\', \'' + pname + '\', \'' + pcode + '\', \'' + cname + '\', \'' + ccode +'\')')
        except Exception as e:
            # LOG_E(e)
            pass
        finally:
            self.conn.commit()
            cursor.close()

    def search_area(self):
        try:
            cursor = self.conn.cursor()
            # cursor.execute('select * from ips where account=' + '\'' + account + '\'')
            cursor.execute('select * from proxy')
            values = cursor.fetchall()
            return values
        except Exception as e:
            # LOG_E(e)
            pass
            return None
        finally:
            self.conn.commit()
            cursor.close()

    def update_ip(self, account, ip):
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE ips SET ip=\'' + ip + '\' WHERE account=' + '\'' + account + '\'')
        except Exception as e:
            # LOG_E(e)
            pass
        finally:
            self.conn.commit()
            cursor.close()

if __name__ == '__main__':
    # sql = proxy_sql()
    # sql.insert_ip('13456523', '127.0.0.2')
    # sql.delete_ip('13456523')
    # sql.update_ip('13456523', '1222.33.22.33')
    # print(sql.search_ip('13456523'))
    # sql.insert_area('zhima', '1', '2', '3', '4')
    # areas = sql.search_area()
    # print(areas)
    pass