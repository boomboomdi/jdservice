from asyncio import sleep
import random
from socket import timeout
import time

for i in range(3000):
    card_id = '100011110' + str(random.randint(12345, 99999)) + str(random.randint(12345, 99999))
    print(card_id)