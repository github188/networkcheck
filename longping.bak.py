import os
import sys
import time
import xlrd
from xlwt import *
from xlutils.copy import copy
from xlrd import open_workbook
import ping_health

def dolongping(obj,ipaddr):
	row = 1
	column = 0
	while True:
		# 可定义退出条件
		# if row == 10:
		# 	break
		cmd = "ping -4 -w 1000 %s -n %s"%(ipaddr,3)
		response = os.popen(cmd).readlines()
		returndict = {"packet_loss":None,"res_min":None,"res_max":None,"res_arvg":None,"route_jitter":None}
		ttllist=[]
		for line in response:
			if "TTL" in line:
				try:
					ttl = line.split("TTL=")[1].strip()
					if not ttl in ttllist:
						ttllist.append(ttl)
				except:
					pass
			if "%" in line:
				try:
					packet_loss = line.rsplit("%")[0].split("(")[1]
					returndict['packet_loss'] = packet_loss
					#returnlist.append(packet_loss)
				except:
					packet_loss=None
			if line.count("ms") == 3 and line.count("=") == 3:
				res_min,res_max,res_arvg=return_ms(line)
				returndict['res_min'] = res_min
				returndict['res_max'] = res_max
				returndict['res_arvg'] = res_arvg

		for i in returndict:
			if returndict[i]:
				pass
			else:
				pass
				#returndict[i] = "信息获取失败"
		
		if ttllist:
			if len(ttllist) > 1:
				returndict['route_jitter'] = 1
			else:
				returndict['route_jitter'] = 0
		
		logtime = time.strftime("%H:%M:%S",time.localtime())
		#print(returndict)

		file = open_workbook('longpingdata.xls',formatting_info=True)
		r_sheet = file.sheet_by_index(0)
		cpfile = copy(file)

		table = cpfile.get_sheet(0)
		title = ["监测时间","丢包率","最小延迟","最大延迟","平均延迟","路由抖动"]
		fornum=0
		for i in title:
			table.write(0,fornum,i)
			fornum+=1
		#print(help(table.write))
		table.write(row, 0,logtime)
		table.write(row, 1,returndict['packet_loss'])
		table.write(row, 2,returndict['res_min'])
		table.write(row, 3,returndict['res_max'])
		table.write(row, 4,returndict['res_arvg'])
		table.write(row, 5,returndict['route_jitter'])
		cpfile.save("longpingdata.xls")
		obj.l_longping_loss_r['text'] = returndict['packet_loss']+"%" if returndict['packet_loss'] else "信息获取失败"
		obj.l_longping_res_r['text'] = "%sms"%returndict['res_arvg'] if returndict['res_arvg'] else "信息获取失败"
		if returndict['route_jitter'] or isinstance(returndict['route_jitter'],int):
			#print(returndict['route_jitter'])
			if returndict['route_jitter'] == 0:
				obj.l_longping_jab_r['text'] = "无抖动"
			else:
				obj.l_longping_jab_r['text'] = "有抖动"

		####
		thisobj_ls_res_jt = ping_health.together(ping_health.get_loss(returndict),ping_health.get_responese(returndict),ping_health.get_jitter(returndict))
		if thisobj_ls_res_jt:
			if thisobj_ls_res_jt >= 80:
				# obj.l_signal_r["fg"]="green"
				# obj.l_signal_r["text"] = "优"
				obj.l_signal['text'] = "||||"
			elif 60 <= thisobj_ls_res_jt < 80:
				# obj.l_signal_r["fg"]="blue"
				# obj.l_signal_r["text"] = "良"
				obj.l_signal['text'] = "|||"
			elif 30 <= thisobj_ls_res_jt < 60:
				obj.l_signal['text'] = "||"
			elif thisobj_ls_res_jt == None or thisobj_ls_res_jt == 0:
				obj.l_signal['text'] = "×"
			else:
				obj.l_signal['text'] = "获取失败"
		row+=1
		#time.sleep(0.5)

def return_ms(line):
	reslist=[]
	for i in range(3):
		try:
			reslist.append(line.split("ms")[i].split("=")[1].strip())
		except:
			reslist.append(None)
	return reslist


if __name__ == "__main__":
	aa=1
	dolongping(aa,"baidu.com")