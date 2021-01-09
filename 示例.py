import random
import time

import requests

from spiderpool import SpiderPool,toSpider

# 一种写法
class Spider:
    def _init_(self):
        pass
    def run(self):
        # print('运行中')
        # bookId=10
        # response=requests.get('https://www.52bqg.com/book_'+str(bookId)+'/',timeout=5)

        time.sleep(1)
        if random.random()<0.5:
            raise NameError

        # sp.gLock.acquire()
        # sp.gLock.release()
        # print('完成')

class Producer:
    def _init_(self):
        pass
    def run(self):
        # print('开始了')
        while 1:
            if len(sp.readypool)<5000:
                # print('放了')
                sp.put(Spider())

# 另一种写法，更简洁
@toSpider
def spider():
    time.sleep(1)
    if random.random()<0.5:
        raise NameError
    
@toSpider
def producer():
    while 1:
        if len(sp.readypool)<5000:
            sp.put(spider())

if __name__ == "__main__":
    sp=SpiderPool()
    sp.checkinterval=1
    sp.trytimes=1
    sp.threadnum_max=250
    
    sp.put(producer(),'生产者')
    sp.start()
    print('爬虫结束')
