from concurrent.futures import thread
from random import randint
import sqlite3
import threading
from time import sleep, time
from tools import LOG_D, LOG_E
import uuid

db = 'ip.db'

class order_sql:

    def __init__(self) -> None:
        self.conn = sqlite3.connect(db, check_same_thread=False) 

    def __del__(self):
        self.conn.close()

    def insert_order(self, order, amount):
        LOG_D(order + ' ' + amount)
        try:
            cursor = self.conn.cursor()
            s = 'insert into orders (order_id, amount, time) values (\'' + order + '\', \'' + amount + '\', \'' + str(int(time())) + '\')'
            print(s)
            cursor.execute(s)
        except Exception as e:
            LOG_E(e)
        finally:
            self.conn.commit()
            cursor.close()

    def delete_order(self, order_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM orders WHERE order_id=' + order_id)
        except Exception as e:
            LOG_E(e)
        finally:
            self.conn.commit()
            cursor.close()

    def search_order(self, order_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('select time from orders where order_id=' + '\'' + order_id + '\'')
            values = cursor.fetchall()
            return values[0][0]
        except Exception as e:
            LOG_E(e)
            return None
        finally:
            self.conn.commit()
            cursor.close()

    def update_order_time(self, order_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE orders SET time=\'' + str(int(time())) + '\' WHERE order_id=' + '\'' + order_id + '\'')
        except Exception as e:
            LOG_E(e)
        finally:
            self.conn.commit()
            cursor.close()

def test():
    order_sql().insert_order(str(randint(0, 99999999)) + str(uuid.uuid4()), '586')

if __name__ == '__main__':
    # for i in range(500):
        # sleep(0.01)
        # threading.Thread(target=test).start()
    # sleep(1)
    # sql.delete_order('13456523')
    # sql.update_order_time('13456523')
    t = order_sql().search_order('248615578436')
    print(t)
    # print(sql.search_ip('13456523'))