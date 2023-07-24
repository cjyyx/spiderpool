import random
import time

import requests

from spiderpool import *
import threading


@toSpider
def spider(generation_num):
    # time.sleep(1)
    # if random.random()<0.1:
    #     1/0

    requests.get(
        "https://www.52bqg.net/book_127071/51314634.html", headers=ranheaders()
    )

    sp.put(spider(generation_num=generation_num + 1), "第%d代爬虫" % (generation_num + 1))


def adjust():
    while 1:
        sp.threadnum_max += 50
        time.sleep(5)


if __name__ == "__main__":
    sp = SpiderPool()
    sp.checkinterval = 1
    sp.trytimes = 1
    sp.threadnum_max = 50

    for i in range(10000):
        sp.put(spider(generation_num=0), "第0代爬虫")

    threading.Thread(target=adjust).start()

    sp.start()
