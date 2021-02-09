import threading
import time
import traceback#处理异常

from .controller1 import *
from .functionlist import functionlist


class SpiderPool:
    '''
    自制爬虫框架
    
    方法:start,put

    参数:threadnum_max,checkinterval,trytimes

    自带锁:gLock
    '''
    def __init__(self):
        self.readypool=[]
        self.failedpool=[]

        self.threadnum_max=500
        self.checkinterval=2#秒
        self.trytimes=3#默认一共试3次
        
        self.gLock=threading.Lock()

        self.showlist={}

        self.threadnum_now=0
        self.finishedtimes=0
        self.failedtimes=0
        self.spiderruntime=0

    def start(self):
        '''打开check，打开Controller，运行run'''
        # 打开check
        threading.Thread(target=self.check).start()

        while 1:
            # time.sleep(0.0001)
            # 如果check让showlist有元素
            if self.showlist:
                break

        # TODO启动controller
        self.controller=Controller(self.showlist,functionlist,self)
        self.controller.start()

        self.run()

    def run(self):
        '''运行至readypool没有元素'''
        while 1:
            if self.threadnum_now<=self.threadnum_max and len(self.readypool)>0:
                self.gLock.acquire()
                threading.Thread(target=self.release_spider,args=(self.readypool.pop(),)).start()
                self.threadnum_now+=1
                self.gLock.release()
                continue
            elif self.threadnum_now==0 and len(self.readypool)==0:
                time.sleep(0.1)
                if self.threadnum_now==0 and len(self.readypool)==0:
                    return

    def check(self):
        starttime=time.time()
        pretime=time.time()
        prechecktime=time.time()
        prefinishedtimes=self.finishedtimes
        prefailedtimes=self.failedtimes
        speed=0
        failedrate=0
        averageSpideRunTime=0

        while 1:
            self.gLock.acquire()

            if time.time()-pretime==0:
                speed=0
            else:
                speed=(self.finishedtimes-prefinishedtimes)/(time.time()-pretime)

            if speed==0:
                failedrate=0
                averageSpideRunTime=0
            else:
                failedrate=round(((self.failedtimes-prefailedtimes)/(self.finishedtimes-prefinishedtimes))*100,2)
                averageSpideRunTime=round(((self.spiderruntime)/(self.finishedtimes-prefinishedtimes)),3)
                self.spiderruntime=0
            
            self.showlist['运行时间（秒）'] = round(time.time()-starttime, 2)
            self.showlist['设定的最大线程数'] = self.threadnum_max
            self.showlist['爬虫尝试运行次数'] = self.trytimes
            self.showlist['当前线程数'] = self.threadnum_now
            self.showlist['爬虫列表内爬虫数'] = len(self.readypool)
            self.showlist['失败爬虫列表内爬虫数'] = len(self.failedpool)
            self.showlist['该检查时间内完成数'] = self.finishedtimes-prefinishedtimes
            self.showlist['该检查时间内失败数'] = self.failedtimes-prefailedtimes
            self.showlist['爬取速度(次/秒)'] = round(speed, 1)
            self.showlist['爬虫失败率(%)'] = failedrate
            self.showlist['爬虫平均用时(秒)'] = averageSpideRunTime
            if speed!=0:
                self.showlist['完成所有爬虫需时间(秒)'] = round((len(self.readypool)+self.threadnum_now)/speed,0)
            else:
                self.showlist['完成所有爬虫需时间(秒)']=0

            pretime=time.time()
            prefinishedtimes=self.finishedtimes
            prefailedtimes=self.failedtimes

            self.gLock.release()

            # TODO自动调整threadnum_max
            # if failedrate>0:
            #     self.threadnum_max-=50
            # elif self.threadnum_max < len(self.readypool):
            #     self.threadnum_max+=10
        
            # TODO打印showlist
            # print(self.showlist)

            # 大约等价于time.sleep(self.checkinterval)
            while 1:
                if time.time()-prechecktime>=self.checkinterval:
                    break
                else:
                    time.sleep(0.01)
            prechecktime=time.time()

    def put(self,spider,description='无名爬虫'):
        '''
        传入一个toSpider修饰过的函数
        '''
        spider.description=description
        self.gLock.acquire()
        self.readypool.append(spider)
        self.gLock.release()
    
    def release_spider(self,spider):
        trytimes=self.trytimes
        # thread_now增加已在run中完成

        for i in range(trytimes): 
            try:
                starttime=time.time()
                spider.run()
                # 到这里，成功了
                self.gLock.acquire()

                self.spiderruntime+=time.time()-starttime
                self.threadnum_now-=1
                self.finishedtimes+=1

                self.gLock.release()
                return
            except Exception as e:
                if i==trytimes-1:
                    # 失败了
                    info = traceback.format_exc()
                    spider.exception=info
                    # spider.exception=info[282:]

                    self.gLock.acquire()

                    self.finishedtimes+=1
                    self.failedtimes+=1
                    self.failedpool.append(spider)

                    self.threadnum_now-=1
                    self.spiderruntime+=time.time()-starttime

                    self.gLock.release()    
                    return        

    def retry_failedspiders(self):
        '''把失败爬虫列表并入爬虫列表中'''
        self.gLock.acquire()

        self.readypool.extend(self.failedpool)
        self.failedpool.clear()

        self.gLock.release()

    def output_failedspiders_log(self):
        self.gLock.acquire()

        with open('failedspiders_log','w',encoding='utf-8') as f:
            for spider in self.failedpool:
                f.write('爬虫类型：'+spider.type+'\n')
                f.write('爬虫描述：\n'+spider.description+'\n')
                f.write('错误信息：\n'+spider.exception+'\n'*2)

        self.gLock.release()



def toSpider(func):
    '''
    输入一个函数，返回一个自身方法run是该函数的对象。
    但是函数使用时所有参数都要是关键字参数！！！
    貌似运行效率会降低！！
    '''
    class Spider:
        def __init__(self,func,**kwargs):
            self.kwargs=kwargs
            self.func=func
            self.type=func.__name__

        def run(self):
            args=''
            for item in self.kwargs.items():
                exec('%s=item[1]'%(item[0]))
                args=args+item[0]+','
            args=args[:-1]
            exec('self.func(%s)'%(args))
    
    def inner(**kwargs):
        return Spider(func,**kwargs)
    return inner