# coding:utf-8
from tkinter import *
import os
import sys
import time
import pycurl
import configparser
import re
import socket
import certifi
from ftplib import FTP
import threading
import check_ping_p,check_port_p,ping_health,port_health,speed_health,get_ipinfo,mail2admin,Info2html,longping
from tkinter import messagebox

#用于测试带宽用的自定义线程，目的是限时
class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        self.result = check_bandwidth()
    def get_result(self):
        return self.result

def returnmsg2gui(myobject,func,start_msg):
    print(start_msg,end='')
    #刷新前端GUI的检测过程
    myobject.l_check_ing['text']+=start_msg
    parameter = func
    #parameter[0]为返回执行结果（Done or Error）
    myobject.l_check_ing['text']+='%s\n'%parameter[1]
    #parameter[1]为返回执行数据（业务数据）
    print(parameter[1])
    return parameter[0]

def check_tracert(tracert_dst_ips,tracert_timeout):
    try:
        response_list=[]
        #拼接命令、执行命令
        def do_tracert(dst_ip):
            cmd = "tracert -d -w %s -4 -h 20 %s"%(tracert_timeout,dst_ip)
            response = os.popen(cmd).readlines()
            ip_re=re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
            for line in response:
                ip=ip_re.search(line)
                if ip:
                    ip_dict={ip.group(0):None}
                    ping_res = re.findall(r"[\d]{1,3} ms|[\d]{1,3} 毫秒",line)
                    if ping_res:
                        #将延迟结果内容以斜杠分割后展示
                        ping_res = " / ".join(ping_res)
                        ip_dict[ip.group(0)] = ping_res
                    response_list.append(ip_dict)
        #这个检查目前还没实现多线程的返回结果，用多线程并发它只是为了控制timeout值
        thlist=[]
        for dst_ip in tracert_dst_ips:
            th = threading.Thread(target = do_tracert,args=(dst_ip,))
            thlist.append(th)
        for th in thlist:
            th.start()
        for th in thlist:
            th.join(40)
        #response_list as below:
        #["dst_ip1",{"1.1.1.1":"1ms / 3ms / 5ms"},{"2.2.2.2":"11ms / 31ms / 51ms"}]
        return response_list,"[Done]"
    except:
        return None,"[Error]:路由跟踪失败"

def check_bandwidth():
    gui.l_check_ing['text']+= '下载带宽检测中------'
    print("下载带宽检测中------",end='')
    try:
        ftpuser = cf.items("ftpcheck")[0][1]
        #ftppasswd = cf.items("ftpcheck")[1][1]
        ftpserver = cf.items("ftpcheck")[1][1]
        ftp=FTP()                                       #设置变量
        #ftp.set_debuglevel(2)                          #打开调试级别2，显示详细信息
        #下载测试
        ftp.connect(ftpserver,21)                   #连接的ftp sever和端口
        ftp.login(ftpuser,"infra#123!")                #连接的用户名，密码
        #print(ftp.getwelcome())                    #打印出欢迎信息
        #ftp.cmd("xxx/xxx")                         #进入远程目录
        bufsize=1024                                #设置的缓冲区大小
        #download_filename = os.path.join(base_dir,"download-server.txt")    #需要下载的文件
        download_filename = "download-server.txt"
        upload_filename = os.path.join(base_dir,"upload-server.txt").encode('gbk')

        #upload_filename="upload-server.txt"
        down_file_handle=open(upload_filename,"wb").write #以写模式在本地打开文件

        t1=time.time()                              #计时开始
        ftp.retrbinary("RETR %s"%download_filename,down_file_handle,bufsize) #接收服务器上文件并写入本地文件
        file_size=os.path.getsize(upload_filename)

        t2=time.time()                              #计时结束
        timediff=t2-t1                              #计算下载用时
        ftp.set_debuglevel(0)                       #关闭调试模式
        #计算下载速率
        download_speed=file_size*8/timediff
        del down_file_handle
        gui.l_check_ing['text']+= '[Done]\n'
        print("[Done]")
    except:
        gui.l_check_ing['text'] += '[Error]:下载带宽检测失败\n'
        print("[Error]:下载带宽检测失败")
        #print("[Error]:"+e)
        download_speed=None
    gui.l_check_ing['text']+= '上传带宽检测中------'
    print("上传带宽检测中------",end='')
    #上传测试
    try:
        up_file_handle=open(upload_filename, "rb")
        ftp.cwd("upload")
        t1=time.time()
        ftp.storbinary("STOR %s"%time.time(), up_file_handle)
        t2=time.time()
        timediff=t2-t1
        up_file_handle.close()
        #计算上传速率
        up_speed=file_size*8/timediff
        ftp.quit()#退出ftp
        gui.l_check_ing['text']+= '[Done]\n'
        print("[Done]")
    except:
        gui.l_check_ing['text']+= '[Error]:上传带宽检测失败\n'
        print("[Error]:上传带宽检测失败")
        up_speed=None

    #定义一个返回用的空列表
    ftpreturnlist=[]
    ftpreturnlist.append(download_speed)
    ftpreturnlist.append(up_speed)
    #返回最终结果
    print("带宽测试完成--------[Done]")
    return ftpreturnlist

#用户检查Http连接的类，此类只是为了pycurl用的
class Mycallback:
    def __init__(self):
        self.contents = ''
    def callback(self,curl):
        curl=str(curl)
        self.contents = self.contents + curl
#Http连接检测方法
def check_url():
    #定义一个返回用的空字典
    returndict={}
    try:
        urls = cf.items("webcheck")[0][1].split(",")
        def do_access(url):
            t = Mycallback()
            c = pycurl.Curl()
            c.setopt(pycurl.WRITEFUNCTION,t.callback)
            c.setopt(pycurl.CAINFO, certifi.where())
            c.setopt(pycurl.ENCODING, 'gzip')
            c.setopt(pycurl.URL,url)
            #连接超时10秒
            c.setopt(pycurl.CONNECTTIMEOUT, 10)
            #访问超时10秒
            c.setopt(pycurl.TIMEOUT, 10)
            #尝试连接
            try:
                c.perform()
                returnurlres=(c.getinfo(c.HTTP_CODE),"%sms"%(int(c.getinfo(c.NAMELOOKUP_TIME)*1000)),"%sms"%(int(c.getinfo(c.CONNECT_TIME)*1000)),"%sms"%(int(c.getinfo(c.PRETRANSFER_TIME)*1000)),"%sms"%(int(c.getinfo(c.STARTTRANSFER_TIME)*1000)),"%sms"%(int(c.getinfo(c.TOTAL_TIME)*1000)),"%sbytes"%int(c.getinfo(c.SIZE_DOWNLOAD)),"%sbytes"%c.getinfo(c.HEADER_SIZE),"%sbps"%int(c.getinfo(c.SPEED_DOWNLOAD)))
                returndict[url]=returnurlres
            except:
                #如果连接失败，则各项内容为：http/https连接失败
                print(url+": 连接失败")
                tempstr = "连接失败或访问超时"
                returnurlres=(tempstr,tempstr,tempstr,tempstr,tempstr,tempstr,tempstr,tempstr,tempstr)
                returndict[url]=returnurlres
        thlist = []
        for url in urls:
            th = threading.Thread(target = do_access,args=(url,))
            thlist.append(th)
        for th in thlist:
            th.start()
        for th in thlist:
            th.join(60)
        #最终返回检测结果字典，字典格式为{"URL地址1"：（指标1，指标2，...）,"URL地址2"：（指标1，指标2，...）}
        return returndict,"[Done]"
    except:
        return None,"[Error]:Http/Https检测出错"

#日志记录函数
def logger(messages):
    try:
        #获取日志记录用的日期
        date=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        #清楚html标签
        result,num = re.subn('</?\w+[^>]*>',"\n",messages)
        result=result.split("\n")
        new_messages=""
        for line in result:
            line = line.strip()
            if line == "":
                continue
            new_messages+=line+"\n"
        #写入日志
        log = open(reportfile,"w")
        log.writelines(date+"\n")
        log.writelines(new_messages)
        log.close()
        return None,'[Done]'
    except:
        return None,'[Error]:报告制作出错'

#检查邮箱地址有效性
def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

def validip(ip):  
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')  
    if p.match(ip):  
        return True  
    else:  
        return False 

def open_resault_reportfile():
    report_log = "%s/check.log"%base_dir
    def do_open_resault_reportfile():
        os.system(report_log)
    if os.path.exists(report_log):
        th = threading.Thread(target = do_open_resault_reportfile,args=())
        th.setDaemon(True)
        th.start()
    else:
        messagebox.showerror("错误","结果日志不存在，请重新检查")

class CheckGUI:
    def __init__(self,master):
        frame = Frame(master)
        frame.grid()
        fm1 = LabelFrame(frame, width=350, height=600, text='输入信息(*标记的是必填内容)')
        fm1.grid(row=0,column=0,rowspan=3)
        fm1.grid_propagate(0)
        fm2 = LabelFrame(frame, width=350, height=300, text='初诊结果')
        fm2.grid(row=3,column=0)
        fm2.grid_propagate(0)

        fm5 = LabelFrame(frame, width=350, height=150, text='自定义测试IP列表')
        fm5.grid(row=0,column=1)
        fm5.grid_propagate(0)

        fm6 = LabelFrame(frame, width=350, height=150, text='信号稳定监测')
        fm6.grid(row=1,column=1)
        fm6.grid_propagate(0)

        fm4 = LabelFrame(frame, width=350, height=300, text='检测日志')
        fm4.grid(row=2,column=1)
        fm4.grid_propagate(0)

        fm3 = LabelFrame(frame, width=350, height=300, text='建议')
        fm3.grid(row=3,column=1)
        fm3.grid_propagate(0)

        self.l_username = Label(fm1, text="联系人姓名*",width=15,fg='red')
        self.l_username.grid(row=0,column=0)
        self.s_username = StringVar()
        self.e_username = Entry(fm1, textvariable = self.s_username)
        self.s_username.set("")
        self.e_username.grid(row=0,column=1,pady=4)

        self.l_phone = Label(fm1, text="联系人电话*",fg='red')
        self.l_phone.grid(row=1,column=0)
        self.s_phone = StringVar()
        self.e_phone = Entry(fm1, textvariable = self.s_phone)
        self.s_phone.set("")
        self.e_phone.grid(row=1,column=1,pady=4)

        self.l_email = Label(fm1, text="联系人邮箱*",fg='red')
        self.l_email.grid(row=2,column=0)
        self.s_email = StringVar()
        self.e_email = Entry(fm1, textvariable = self.s_email)
        self.s_email.set("")
        self.e_email.grid(row=2,column=1,pady=4)

        self.l_comyname = Label(fm1, text="组织/企业名称*",fg='red')
        self.l_comyname.grid(row=3,column=0)
        self.s_comyname = StringVar()
        self.e_comyname = Entry(fm1, textvariable = self.s_comyname)
        self.s_comyname.set("")
        self.e_comyname.grid(row=3,column=1,pady=4)

        self.l_mtype = Label(fm1, text="您的设备型号")
        self.l_mtype.grid(row=4,column=0)
        self.s_mtype = StringVar()
        self.e_mtype = Entry(fm1, textvariable = self.s_mtype)
        self.s_mtype.set("")
        self.e_mtype.grid(row=4,column=1,pady=4)

        self.l_msernum = Label(fm1, text="使用设备序列号")
        self.l_msernum.grid(row=5,column=0)
        self.s_msernum = StringVar()
        self.e_msernum = Entry(fm1, textvariable = self.s_msernum)
        self.s_msernum.set("")
        self.e_msernum.grid(row=5,column=1,pady=4)

        self.l_software = Label(fm1, text="您使用的软件名称")
        self.l_software.grid(row=6,column=0)
        self.s_software = StringVar()
        self.e_software = Entry(fm1, textvariable = self.s_software)
        self.s_software.set("")
        self.e_software.grid(row=6,column=1,pady=4)

        self.l_ping = Label(fm5, text="添加检测的IP地址，如：8.8.8.8 (最多添加5个)",font=("", 7,""))
        self.l_ping.grid(row=0,column=0,columnspan=2)
        self.s_ping = StringVar()
        self.e_ping = Entry(fm5, textvariable = self.s_ping)
        self.s_ping.set("")
        self.e_ping.grid(row=1,column=0,pady=4,padx=0,sticky='W')        

        self.b_addip = Button(fm5, text="添加",command=self.addip,width=4)
        self.b_addip.grid(row=1,column=1,padx=0,sticky='E')

        self.l_addip_list = Label(fm5, text="",font=("",7,))
        self.l_addip_list.grid(row=2,column=0,sticky='E')

        self.b_addip = Button(fm5, text="清空",command=self.resetip,width=4)
        self.b_addip.grid(row=1,column=2,padx=0,sticky='W')

        self.l_trouble = Label(fm1, text="情况描述*",fg='red',width=15)
        self.l_trouble.grid(row=9,column=0)
        self.t_trouble = Text(fm1,width=10,height=8)
        self.t_trouble.grid(row=9,column=1,columnspan=2,sticky='WENS')

        #logo
        self.p_logo = PhotoImage(file="cci.png")
        self.l_logo = Label(fm1, image=self.p_logo)
        self.l_logo.grid(row=13,column=0,pady=4,rowspan=2)

        #作者\版本号 
        self.l_author = Label(fm1, text="作者:金阳华;许子恒",width=20,font=("",7,))
        self.l_author.grid(row=15,column=1,sticky='WENS',pady=10)  

        self.toadmin = IntVar()
        self.toself = IntVar()
        self.c_sendmail= Checkbutton(fm1, text='发送给服务商',variable = self.toadmin,onvalue = 1,offvalue = 0)
        self.c_sendmail.grid(row=11,column=0,pady=4)
        self.c_sendmail.select()

        self.c_sendmail2= Checkbutton(fm1, text='发送给自己',variable = self.toself,onvalue = 1,offvalue = 0)
        self.c_sendmail2.grid(row=11,column=1,pady=4)
        self.c_sendmail2.select()

        self.b_check = Button(fm1, text="开始检查",command=self.main,width=20,height=1)
        self.b_check.grid(row=12,column=1)

        self.b_exit = Button(fm1, text="退出程序",width=20,height=1, command=self.gui_exit)
        self.b_exit.grid(row=13, column=1)

        self.b_watch_log = Button(fm1, text="查看结果报告",width=20,height=1, command=open_resault_reportfile)
        self.b_watch_log.grid(row=14, column=1)
        self.b_watch_log['state'] = "disabled"

        #frame#2
        self.l_traf_up = Label(fm2, text="上传带宽：",width=15,anchor="w")
        self.l_traf_up.grid(row=0,column=0,sticky='W')

        self.l_traf_up_r = Label(fm2, text="",width=17,font=("微软雅黑", 9, "bold"))
        self.l_traf_up_r.grid(row=0,column=1)

        self.l_traf_down = Label(fm2, text="下载带宽：",width=15,anchor="w")
        self.l_traf_down.grid(row=1,column=0,sticky='W')

        self.l_traf_down_r = Label(fm2, text="",width=17,font=("微软雅黑", 9, "bold"))
        self.l_traf_down_r.grid(row=1,column=1)

        self.l_loss = Label(fm2, text="网络稳定性：",width=15,anchor="w")
        self.l_loss.grid(row=2,column=0,sticky='W')

        self.l_loss_r = Label(fm2, text="",width=17,font=("", 9, "bold"),wraplength=200,justify="left")
        self.l_loss_r.grid(row=2,column=1)

        self.l_command = Label(fm2, text="评分=(1-丢包率)*0.7+(220-延迟)/2*0.3+(100-抖动)*0.2",font=("", 7, ""),justify="left",wraplength=320)
        self.l_command.grid(row=3,column=0,columnspan=2,sticky='W')

        self.l_port = Label(fm2, text="端口测试结果：",width=15,anchor="w")
        self.l_port.grid(row=4,column=0,sticky='W')

        self.l_port_r = Label(fm2, text="",width=30,justify="right",font=("", 9, ""))
        self.l_port_r.grid(row=5,column=0,rowspan=3,columnspan=2,sticky="e")

        try:
            monitorIPs = cf.items("pingcheck")[0][1]
            for i in monitorIPs.split(","):
                if i.split(":")[1] == "CCI-Expressway-E":
                    self.monitorIP = i.split(":")[0]
        except:
            self.monitorIP = ""
        self.longping = IntVar()
        self.c_longping= Checkbutton(fm6, text='监测 %s'%self.monitorIP,variable = self.longping,onvalue = 1,offvalue = 0)
        self.c_longping.grid(row=0,column=0,pady=4)

        self.b_longpingstop = Button(fm6, text="停止\n监测",command=self.stoplongping,width=6,height=2,font=("", 8, ""))
        self.b_longpingstop.grid(row=0,column=1,padx=0,sticky='E')

        self.b_longpingreport = Button(fm6, text="查看\n报告",command=self.longpingreport,width=6,height=2,font=("", 8, ""))
        self.b_longpingreport.grid(row=0,column=2,padx=0,sticky='E')

        self.l_longping_loss = Label(fm6, text="丢包率:",font=("", 8, ""),justify="left")
        self.l_longping_loss.grid(row=1,column=0,sticky='W')

        self.l_longping_loss_r = Label(fm6, text="",font=("", 8, ""),justify="left")
        self.l_longping_loss_r.grid(row=1,column=1,sticky='W')

        self.l_longping_res = Label(fm6, text="平均延迟:",font=("", 8, ""),justify="left")
        self.l_longping_res.grid(row=2,column=0,sticky='W')

        self.l_longping_res_r = Label(fm6, text=":",font=("", 8, ""),justify="left",anchor="w")
        self.l_longping_res_r.grid(row=2,column=1,sticky='W')

        self.l_longping_jab = Label(fm6, text="路由抖动:",font=("", 8, ""),justify="left")
        self.l_longping_jab.grid(row=3,column=0,sticky='W')

        self.l_longping_jab_r = Label(fm6, text="",font=("", 8, ""),justify="left",anchor="w")
        self.l_longping_jab_r.grid(row=3,column=1,sticky='W')
        self.b_longpingreport['state'] = 'disabled'
        self.b_longpingstop['state'] = 'disabled'
        self.l_signal = Label(fm6, text="信号:",font=("", 8, ""),justify="left")
        self.l_signal.grid(row=4,column=0,sticky='W')

        self.l_signal_r = Label(fm6,text="",anchor="w")#width=10,height=10,image=self.p_signal)
        self.l_signal_r.grid(row=4,column=1,sticky='WENS')

        #frame#3
        self.l_addvance = Label(fm3, text="",justify="left",wraplength=330)
        self.l_addvance.grid(row=0,columnspan=2, rowspan=6)

        #frame#4
        self.l_check_ing = Label(fm4, text="",justify="left",wraplength=330,font=("", 8, ""))
        self.l_check_ing.grid(row=0,columnspan=2, rowspan=10,sticky='WENS')

    def resetip(self):
        self.l_addip_list['text'] = ""


    def addip(self):
        if self.l_addip_list['text'].count('\n') < 5:
            if self.s_ping.get() != "":
                if self.s_ping.get() not in self.l_addip_list['text']:
                    if validip(self.s_ping.get()):
                        if self.l_addip_list['text'] == "":
                            self.l_addip_list['text'] += self.s_ping.get()
                        else:
                            self.l_addip_list['text'] += "\n"+self.s_ping.get()
                        self.s_ping.set("")
                        root.update()
                    else:
                        messagebox.showerror("错误","IP地址不合规")
                else:
                    messagebox.showerror("错误","不能添加重复IP地址")
            else:
                messagebox.showerror("错误","亲，别输空值")
        else:
            messagebox.showerror("错误","最多只能加5个")

    def gui_exit(self):
        root.quit()
        root.destroy()

    #主程序
    def main(self):
        #清空历史记录
        def do_main(thisobj):
            thisobj.b_longpingreport['state'] = 'disabled'
            thisobj.b_longpingstop['state'] = 'disabled'
            thisobj.l_check_ing['text'] = ""
            thisobj.l_addvance['text'] = ""
            thisobj.l_port_r['text'] = ""
            thisobj.l_traf_down_r['text'] = ""
            thisobj.l_traf_up_r['text'] = ""
            thisobj.l_loss_r['text'] = ""
            thisobj.b_watch_log['state'] = "disabled"
            thisobj.l_longping_loss_r['text'] = ""
            thisobj.l_longping_res_r['text'] = ""
            thisobj.l_longping_jab_r['text'] = ""
            thisobj.l_signal_r['text'] = ""
            #判断情况描述是否正确输入：
            if len(thisobj.t_trouble.get('0.0',END)) == 1:
                #用户没有输入情况描述，中止程序，提示用户
                messagebox.showerror("输入错误","请填如带“*”的必填项")
                return None
                #判断必选内容是否齐全
            if "" in (thisobj.s_username.get(),thisobj.s_phone.get(),thisobj.s_email.get(),thisobj.s_comyname.get()):
                #不齐全就返回空，让用户重填
                messagebox.showerror("输入错误","请填如带“*”的必填项")
                return None

            #检查邮箱有效性
            if not validateEmail(thisobj.s_email.get()):
                messagebox.showerror("输入错误","请输入有效的邮箱地址")
                #不齐全就返回空，让用户重填
                return None

            #检查添加检查平PING地址的有效合规性
            if thisobj.s_ping.get():
                if not validip(thisobj.s_ping.get()):
                    messagebox.showerror("输入错误","输入的IP地址有错误")
                    return None

            #数据齐全，且邮箱有效就进行赋值
            username = thisobj.s_username.get()                                     #用户姓名
            phone = thisobj.s_phone.get()                                           #用户联系方式
            email = thisobj.s_email.get()                                           #联系人邮箱
            compname = thisobj.s_comyname.get()                                     #公司名
            trouble = thisobj.t_trouble.get('0.0',END).replace("\n","")             #情况描述
            #以下为可选内容
            machinetype = thisobj.s_mtype.get()                                     #机器型号
            serialnumber = thisobj.s_msernum.get()                                  #设备序列号
            softwarename = thisobj.s_software.get()                                 #软件名
            add_ping = thisobj.s_ping.get()                                         #自定义ping地址
            #add_port = thisobj.s_port.get()                                         #自定义端口检查地址
            userinfo=[trouble,username,phone,email,compname,machinetype,serialnumber,softwarename]
            thisobj.l_check_ing['text'] += "开始检查,请不要关闭cmd命令行窗口,\n检查过程大约耗时2分钟,请耐心等待。\n"
            #记录开始时间
            start_time2log = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            start_time = time.time()
            #将检查按钮设置成不可点击状态（防止用户多次点击造成队列拥堵）
            thisobj.b_check['state'] = 'disabled'

            #-------------获取基本网络信息---------------------
            #获取OS版本
            os_ver = returnmsg2gui(thisobj,get_ipinfo.get_os(),'OS版本信息获取中----')
            #获取用户网关
            user_gw = returnmsg2gui(thisobj,get_ipinfo.get_gw(),'网关信息获取中------')
            #获取用户DNS服务器信息
            user_dns = returnmsg2gui(thisobj,get_ipinfo.get_dns(),'DNS信息获取中-------')
            #获取用户路由表
            user_route = returnmsg2gui(thisobj,get_ipinfo.get_route(),'路由信息获取中------')
            #----------------------------------------------------

            try:
            #获取ping检测用的信息，如IP地址，Ping的次数
                ips = cf.items("pingcheck")[0][1].split(",")
            except:
                print("ping检测ip列表取得失败")
                ips = []
            try:
                ping_count = cf.items("pingcheck")[1][1].strip()

            except:
                print("ping检测次数取得失败")
                ping_count = 10
            #添加用户自定义监控项
            if thisobj.l_addip_list['text']:
                addiplist = thisobj.l_addip_list['text'].split("\n")
                for addips in addiplist:
                    addips += ":用户自定义IP"
                    ips.append(addips)
            try:
                #获取检测对象的信息，IP地址，端口号
                ip_ports = cf.items("portcheck")[0][1].split(",")
            except:
                print("ping检测次数取得失败")
                ip_ports = []

            #将thisobj输入的IP添如ping监控列表
            #获取跟踪路由信息
            tracert_conf = cf.items("tracert")
            #获取跟踪IP
            tracert_dst_ip = tracert_conf[0][1]
            tracert_dst_ips = tracert_dst_ip.split(";")
            #跟踪单节点timeout值
            tracert_timeout = tracert_conf[1][1]

            tracert = returnmsg2gui(thisobj,check_tracert(tracert_dst_ips,tracert_timeout),'路由跟踪获取中------')

            if tracert:
                #协作云域名解析出来的IP地址
                dnslookup = list(tracert[0].keys())[0]
                if len(tracert) > 2:

                    #用户网关的IP地址
                    client_gw = list(tracert[1])[0]+":用户网关"
                    #协作云的网关
                    server_gw = list(tracert[-2])[0]+":服务端网关"
                    ips.append(client_gw)
                    ips.append(server_gw)
                else:
                    client_gw,server_gw = None,None
                    print("路由跟踪检测--------[Error]:路由跟踪失败，或跟踪节点过少")
                tracert = tracert[1:]
            else:
                dnslookup,client_gw,server_gw = None,None,None
                print("路由跟踪检测--------[Error]:路由跟踪失败，或跟踪节点过少")

            #ping检测
            thisobj.l_check_ing['text']+= 'ICMP检测中----------'
            #获取用户Ping检测结果
            res_ping = check_ping_p.check_ping(ips,ping_count)
            thisobj.l_check_ing['text']+= '[Done]\n'
            #获取用户带宽测试结果
            check_bandwidth_th = MyThread()
            check_bandwidth_th.start()
            check_bandwidth_th.join(150)
            try:
                bandwidth = check_bandwidth_th.get_result()
            except:
                bandwidth = [None,None]
            #bandwidth = [111111.11,11111.23]
            #获取用户端口检测结果
            res_port = returnmsg2gui(thisobj,check_port_p.check_port(ip_ports),'端口检测中----------')
            #获取用户URL检测结果
            res_url = returnmsg2gui(thisobj,check_url(),'http/https检测中----')

            #获取用户网络信息，将ping、web、上传、下载、tcp端口检查后得到的结果，传入至info2html方法，生成邮件内容
            ##########计算pingXZY的丢包-延迟-抖动健康值####################
            ping_check_key_word = "CCI-Expressway-E"
            for r_ping in res_ping:
                if r_ping["command"] == ping_check_key_word:
                    thisobj_ls_res_jt = ping_health.together(ping_health.get_loss(r_ping),ping_health.get_responese(r_ping),ping_health.get_jitter(r_ping))
                    if thisobj_ls_res_jt:
                        if thisobj_ls_res_jt >= 80:
                            thisobj.l_loss_r["fg"]="green"
                            thisobj.l_loss_r["text"] = "优"
                        elif 60 <= thisobj_ls_res_jt < 80:
                            thisobj.l_loss_r["fg"]="blue"
                            thisobj.l_loss_r["text"] = "良"
                        else:
                            thisobj.l_loss_r["fg"]="red"
                            thisobj.l_loss_r["text"] = "可能有抖动"

                        thisobj.l_loss_r["text"] += "(%s)"%thisobj_ls_res_jt
                    else:
                        if isinstance(thisobj_ls_res_jt,int):
                            thisobj.l_loss_r["fg"]="red"
                            thisobj.l_loss_r["text"] = "不合格"
                            thisobj.l_loss_r["text"] += "(%s)"%thisobj_ls_res_jt
                        else:
                            thisobj.l_loss_r["text"] = "信息获取失败"
            ##########计算必要端口通信成功率###################################
            #返回的是一个健康度+NG的端口地址，list的0是健康度，1是NG内容

            thisobj_port,ng_ports = port_health.together(res_port)

            for port in ng_ports:
                thisobj.l_addvance["text"] += "-建议管理员打开%s的%s端口\n"%(port.split(":")[0],port.split(":")[1])

            if res_port:
                for rp in res_port:
                    thisobj.l_port_r["text"] += rp+":"+res_port[rp]+"\n"
            else:
                thisobj.l_port_r["text"] = "信息获取失败"

            ##############计算带宽健康率############
            if bandwidth[0]:
                download_band = speed_health.bandwidth_rank(bandwidth[0])
                r2gui_download = download_band.get_rank()
                thisobj.l_traf_down_r["text"] = download_band.bps2KMG()

                if r2gui_download:
                    if r2gui_download == "带宽不足":
                        thisobj.l_traf_down_r["fg"]="red"
                        thisobj.l_traf_down_r["text"] += "(带宽不足)"
                    elif r2gui_download == "带宽低":
                        thisobj.l_traf_down_r["fg"]="orange"
                        thisobj.l_traf_down_r["text"] += "(带宽低)"
                    elif r2gui_download == "带宽中等":
                        thisobj.l_traf_down_r["fg"]="blue"
                        thisobj.l_traf_down_r["text"] += "(带宽中等)"
                    elif r2gui_download == "带宽良好":
                        thisobj.l_traf_down_r["fg"]="green"
                        thisobj.l_traf_down_r["text"] += "(带宽良好)"
                    elif r2gui_download == "带宽通畅":
                        thisobj.l_traf_down_r["fg"]="green"
                        thisobj.l_traf_down_r["text"] += "(带宽通畅)"

            if bandwidth[1]:
                up_band = speed_health.bandwidth_rank(bandwidth[1])
                r2gui_upload = up_band.get_rank()
                thisobj.l_traf_up_r["text"] = up_band.bps2KMG()
                if r2gui_upload:
                    if r2gui_upload == "带宽不足":
                        thisobj.l_traf_up_r["fg"]="red"
                        thisobj.l_traf_up_r["text"] += "(带宽不足)"
                    elif r2gui_upload == "带宽低":
                        thisobj.l_traf_up_r["fg"]="orange"
                        thisobj.l_traf_up_r["text"] += "(带宽低)"
                    elif r2gui_upload == "带宽中等":
                        thisobj.l_traf_up_r["fg"]="blue"
                        thisobj.l_traf_up_r["text"] += "(带宽中等)"
                    elif r2gui_upload == "带宽良好":
                        thisobj.l_traf_up_r["fg"]="green"
                        thisobj.l_traf_up_r["text"] += "(带宽良好)"
                    elif r2gui_upload == "带宽通畅":
                        thisobj.l_traf_up_r["fg"]="green"
                        thisobj.l_traf_up_r["text"] += "(带宽通畅)"

                mode_advance = up_band.get_mode_addvance()
                if mode_advance:
                    thisobj.l_addvance["text"] += "-会议模式建议：\n%s"%mode_advance

            #定义邮件标题：设备型号+设备串号+用户联系方式+用户姓名 为标题
            subject=userinfo[2]+":"+userinfo[3]+userinfo[0]+":"+userinfo[1]+"--用户网络自检简报"

            #记录日志
            end_time2log = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

            #将测试结果信息放入message做html处理
            messages=Info2html.info2html(start_time2log,end_time2log,userinfo,os_ver,user_dns,user_gw,res_ping,bandwidth,res_port,res_url,tracert,dnslookup,user_route)
            #将测试结果记录做日志记录
            returnmsg2gui(thisobj,logger(messages),"报告制作中----------")

            #定义logger一个用于邮件的tolist
            mailtolist=[]
            #发送邮件
            #用户选择发给管理员
            if thisobj.toadmin.get():
                try:
                    adminaddress = cf.items("mail")[0][1]
                    print(adminaddress)
                    mailtolist.append(adminaddress)
                except:
                    pass
            #用户选择发给自己
            if thisobj.toself.get():
                mailtolist.append(email)
            if mailtolist:
                returnmsg2gui(thisobj,mail2admin.sendmail(mailtolist,subject,messages),"邮件发送中----------")

            #计算脚本用时
            end_time = time.time()
            cost_time_total_sec = end_time - start_time
            cost_time_min = int(cost_time_total_sec / 60)
            cost_time_sec = cost_time_total_sec % 60
            if cost_time_min == 0:
                cost_time = "%s秒"%round(cost_time_sec,1)
            else:
                cost_time = "%s分%s秒"%(cost_time_min,round(cost_time_sec,1))

            thisobj.l_check_ing['text']+= "常规检测完成。\n本次检查时间：%s\n"%cost_time
            print("常规检测完成。\n本次检查时间：%s\n"%cost_time)
            thisobj.b_watch_log['state'] = "active"
            #longping
            if thisobj.longping.get():
                thisobj.l_check_ing['text'] += "信号稳定监测开始......\n"
                print("信号稳定监测开始......")
                self.lp = longping.LongPing()
                self.lp.flag=0
                self.b_longpingstop['state'] = 'active'
                if self.monitorIP:
                    self.lp.dolongping(thisobj,self.monitorIP)
                else:
                    self.lp.dolongping(thisobj,"183.131.19.181")
            #将检查按钮恢复到可点击状态
            thisobj.b_check['state'] = 'active'
        mainth = threading.Thread(target=do_main,args=(self,))
        mainth.setDaemon(True)
        mainth.start()
    def stoplongping(self):
        self.lp.flag=1
        self.b_longpingreport['state'] = 'active'
    def longpingreport(self):
        xls_dir = os.path.split(os.path.realpath(sys.argv[0]))[0] + "\\logs\\longping\\"
        xlsfile = os.path.join(xls_dir,"longpingdata.xlsx")
        self.lp.trans2report()
        if os.path.exists(xlsfile):
            def openxlsfile():
                try:
                    os.system(xlsfile)
                except:
                    messagebox.showerror("错误","office版本不支持，或文件被占用。请正确安装office，或关闭已打开的xlsx文件")
            th = threading.Thread(target = openxlsfile ,args=())
            th.setDaemon(True)
            th.start()
        else:
            messagebox.showerror("错误","报告制作出错！")

if __name__=="__main__":
    version = "0.8.5.1"
    base_dir = os.path.split(os.path.realpath(sys.argv[0]))[0]
    configfile = os.path.join(base_dir,"check.conf")
    cf = configparser.ConfigParser()
    cf.read(configfile)
    #日志文件路径
    reportfile = os.path.join(base_dir,"check.log")
    root = Tk()
    root.title('CCI Network Checker %s'%version)
    root.columnconfigure(0, weight=100)
    root.rowconfigure(0, weight=1)
    gui = CheckGUI(root)
    root.mainloop()