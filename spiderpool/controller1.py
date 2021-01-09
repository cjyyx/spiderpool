'''
测试版
2021年1月8日14:42:23
Bug:
1、functionlist操作有问题
'''

#region controller

from tkinter import *
from threading import Thread,Lock
from multiprocessing import Process, Queue
import time
import openpyxl

class TrueController(Process):

    def __init__(self,showlist,functionlist,toCon,fromCon):
        Process.__init__(self)

        self.toCon=toCon
        self.fromCon=fromCon

        self.showlist=showlist
        self.functionlist=functionlist

        self.showlist_datas=[self.showlist.copy()]


    def run(self):
        
        self.root=Tk()
        self.root.title('controller')
        self.root.geometry('80x30')

        #XXXfunctionlist
        self.functionFrame=Frame(self.root)
        self.functionFrame.place(x=20,y=20)

        # 函数列表
        self.functionListbox=Listbox(self.functionFrame,setgrid=True,width=30,height=10)
        self.functionListbox.grid(row=0)

        for each in self.functionlist:
            self.functionListbox.insert(END,each)

        Button(self.functionFrame,text='执行',command=self.functionListbox_act).grid(row=1)
        self.functionListbox.bind("<Double-Button-1>",self.function_text_show)

        # 函数文本
        self.functionText=Text(self.functionFrame, width=35,height=20)
        self.functionText.grid(row=2)
        
        Button(self.functionFrame,text='执行',command=self.functionText_act).grid(row=3)



        #XXXshowlist
        self.showFrame=Frame(self.root)
        self.showFrame.place(x=300,y=20)

        self.showListbox=Listbox(self.showFrame,setgrid=True,width=30,height=13)
        self.showListbox.grid(row=0)

        keys=list(self.showlist.keys())
        values=list(self.showlist.values())
        for i in range(len(keys)):
            self.showListbox.insert(END,keys[i]+':  '+str(values[i]))

        # self.showtree=Treeview(self.showFrame)
        # self.showtree['columns']=('键','值')
        self.showListbox.bind("<Double-Button-1>",self.showCanvas_show_change)

        Button(self.showFrame,text='保存为Excel',command=self.save_showlist_datas).grid(row=1,column=0)
    
        self.showCanvas=Canvas(self.showFrame,bg='white',width=210,height=210)
        self.showCanvas.grid(row=2)
        self.showCanvas_show=None

        #XXXmain

        Thread(target=self.update_showListbox).start()

        self.root.mainloop()

    def functionText_act(self):
        Thread(target=self.run_function,args=(self.functionText.get("0.0", "end"),)).start()

    def update_showListbox(self):
        pre_showlist=self.showlist.copy()
        while 1:
            self.showlist=self.toCon.get()
            # 更新listbox
            self.showListbox.delete(0,END)
            keys=list(self.showlist.keys())
            values=list(self.showlist.values())
            for i in range(len(keys)):
                self.showListbox.insert(END,keys[i]+':  '+str(values[i]))

            self.showlist_datas.append(self.showlist.copy())
            pre_showlist=self.showlist.copy()

            self.showCanvas_draw()

    def run_function(self,function_text):
        # exec(function_text)
        self.fromCon.put(function_text)
        self.functionListbox.insert(END,self.functionText.get("0.0", "end"))
        self.functionText.delete("0.0", "end")

    def functionListbox_act(self):
        Thread(target=self.run_function,args=(self.functionListbox.get(self.functionListbox.curselection()),)).start()

    def save_showlist_datas(self):
        datas=self.showlist_datas.copy()
        wb=openpyxl.Workbook()
        ws=wb.active
        ws.append(list(datas[0].keys()))
        for data in datas:
            ws.append(list(data.values()))
        wb.save('showlist_datas.xlsx')

        print('save_showlist_datas保存完成')

    def function_text_show(self,event):
        # print(self.functionListbox.curselection())
        # print(self.functionListbox.get(self.functionListbox.curselection()))
        self.functionText.delete("0.0", "end")
        self.functionText.insert('end',self.functionListbox.get(self.functionListbox.curselection()))

    def showCanvas_show_change(self,event):
        # print(self.showListbox.curselection())
        self.showCanvas_show=self.showListbox.curselection()
        self.showCanvas_draw()

    def showCanvas_draw(self):
        try:
            can=self.showCanvas
            datas=self.showlist_datas.copy()
            can.delete('all')

            show=self.showListbox.get(self.showCanvas_show)
            show=show[:show.find(':')]
            # print(datas[0][show])
            datas=list(map(lambda data: data[show],datas))
            # print(datas)

            # 画
            if len(datas)>10:
                datas=datas[-10:]
            m=max(datas)
            datas=list(map(lambda data: data/m,datas))

            for i in range(len(datas)-1):
                can.create_line(i*20+5,205-200*datas[i],i*20+25,205-200*datas[i+1])
        except:
            pass


class Controller():
    '''
    掌控器

    Controller().start()
    '''

    def __init__(self,showlist={},functionlist=[],share={}):

        self.gLock=Lock()
        self.showlist=showlist
        self.functionlist=functionlist
        self.share=share

        # to，from相对于TrueController进程而言，去TrueController：to
        self.toCon=Queue()#showlist
        self.fromCon=Queue()#文本

        self.con=TrueController(showlist,functionlist,self.toCon,self.fromCon)
        self.con.start()

    def start(self):
        '''开启 把showlist传过去，functionlist得到 的线程'''
        Thread(target=self.sent_showlist).start()
        Thread(target=self.get_function).start()

    def sent_showlist(self):
        pre_showlist=self.showlist.copy()
        while 1:
            now_showlist=self.showlist.copy()
            if not pre_showlist==now_showlist:
                self.toCon.put(now_showlist)
                pre_showlist=now_showlist
            else:
                time.sleep(0.1)

    def get_function(self):
        while 1:
            function_text=self.fromCon.get()
            Thread(target=self.run_function,args=(function_text,)).start()

    def run_function(self,function_text):
        share=self.share
        exec(function_text)
        print('完成运行'+function_text)



#endregion





