# coding:utf-8
import os
import sys
import time
import re
import threading



def return_ms(line):
    reslist=[]
    for i in range(3):
        try:
            reslist.append(line.split("ms")[i].split("=")[1].strip())
        except:
            reslist.append(None)
    return reslist

#["192.168.11.11:mynameisjack","1.1.1.1:xxxx"]
def check_ping(iplist,pingcount):
    #定义一个返回用的空list
    returnlists=[]
    def do_ping(item):
        ip = item.split(":")[0]
        #ip = "192.168.11.11"
        ip_command = item.split(":")[1]
        #ip_command = "mynameisjack"
        #returnlist=[ip,ip_command,]
        returndict={"ipaddr":ip,"command":ip_command,"packet_loss":None,"res_min":None,"res_max":None,"res_arvg":None,"jitter":None}
        ttllist=[]
        #执行命令
        cmd = "ping -4 -w 1000 %s -n %s"%(ip,pingcount)
        response = os.popen(cmd).readlines()

        for line in response:
            if "TTL" in line:
                try:
                    ttl = line.split("TTL=")[1].strip()
                    if not ttl in ttllist:
                    	ttllist.append(ttl)
                except:
                    pass
            if "%" in line:
                #丢包率
                try:
                    packet_loss = line.rsplit("%")[0].split("(")[1]
                    #returnlist.append(packet_loss)
                    returndict['packet_loss'] = packet_loss
                except:
                    returndict['packet_loss'] = None
            if line.count("ms") == 3 and line.count("=") == 3:
                res_min,res_max,res_arvg=return_ms(line)
                returndict['res_min'] = res_min
                returndict['res_max'] = res_max
                returndict['res_arvg'] = res_arvg
        if ttllist:
            if len(ttllist) > 1:
                returndict['route_jitter'] = 1
            else:            
                returndict['route_jitter'] = 0
        else:
        	returndict['route_jitter'] = "信息获取失败"
        returnlists.append(returndict)
    thlist=[]
    for ipitem in iplist:
        th = threading.Thread(target = do_ping,args=(ipitem,))
        thlist.append(th)
    for th in thlist:
        th.start()
    for th in thlist:
        #子线程等待时间为ping的次数*10（秒）如ping次数为5的话，等待时间则为50秒
        th.join(int(pingcount)*10)
    return returnlists