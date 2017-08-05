# coding:utf-8

import socket
import threading


def check_port(ip_ports):
    returndict={}
    def do_port_access(host,port,i):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host,port))
            sock.close
            #如果连接成功，则返回OK
            returndict[i]="OK"
        except:
            #如果连接失败，则返回NG
            returndict[i]="NG"
            sock.close()
    thlist=[]
    try:
        for i in ip_ports:
            #获取主机IP地址
            host=i.split(":")[0]
            #获取主机端口号
            port=i.split(":")[1]
            port=int(port)
            #进行端口连接测试
            th = threading.Thread(target=do_port_access,args=(host,port,i))
            thlist.append(th)
        for th in thlist:
            th.start()
        for th in thlist:
            th.join(40)
        return returndict,"[Done]"
    except:
        return None,"[Error]:端口检测出错"

if __name__=="__main__":
    print(check_port(["www.taobao.com:80","8.8.8.8:20"]))