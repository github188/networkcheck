import os
import sys
import time
import xlrd
from xlwt import *
from xlutils.copy import copy
from xlrd import open_workbook
import ping_health
import xlsxwriter

class LongPing:
	def __init__(self):
		self.longpingfilename='logs/longping/longpingdata.log'
		self.longpingexecl='%s.xlsx'%self.longpingfilename.split(".")[0]
		self.flag=0

	def trans2report(self):
		if os.path.exists(self.longpingexecl):
			os.remove(self.longpingexecl)
		workbook = xlsxwriter.Workbook(self.longpingexecl)
		worksheet = workbook.add_worksheet("data")
		bold = workbook.add_format({'bold': 1})
		headings = ["监测时间","丢包率","最小延迟","最大延迟","平均延迟","路由抖动"]
		format = workbook.add_format()
		format.set_text_wrap()
	    #worksheet.set_column('A:A', 10, format)
		worksheet.write_row('A1', headings, bold)
	    
		textfile = open(self.longpingfilename,'r')

		timelist=[]
		losslist=[]
		res_minlist=[]
		res_maxlist=[]
		res_arvglist=[]
		route_jitterlist=[]
		for line in textfile.readlines():
			write_time = line.strip().split(",")[0] if line.strip().split(",")[0] else None
			timelist.append(write_time)

			try:
				write_loss = int(line.strip().split(",")[1])
			except:
				write_loss = None
			losslist.append(write_loss)

			try:
				write_res_min = int(line.strip().split(",")[2])
			except:
				write_res_min = None
			res_minlist.append(write_res_min)

			try:
				write_res_max = int(line.strip().split(",")[3])
			except:
				write_res_max = None
			res_maxlist.append(write_res_max)

			try:
				write_res_arvg = int(line.strip().split(",")[4])
			except:
				write_res_arvg = None
			res_arvglist.append(write_res_arvg)

			try:
				write_route_jitter = int(line.strip().split(",")[5])
			except:
				write_route_jitter = None
			route_jitterlist.append(write_route_jitter)

		worksheet.write_column('A2', timelist)
		worksheet.write_column('B2', losslist)
		worksheet.write_column('C2', res_minlist)
		worksheet.write_column('D2', res_maxlist)
		worksheet.write_column('E2', res_arvglist)
		worksheet.write_column('F2', route_jitterlist)

		line_chart = workbook.add_chart({'type': 'line'})
		line_chart.add_series({
			'name': "=data!$B$1",
			'categories': '==data!$A$2:$A$%s'%str(len(timelist)+1),
			'values': '=data!$B$2:$B$%s'%str(len(losslist)+1),
			'data_label':{'value': True},
		})
	    # 添加图表标题和标签
		line_chart.set_title({'name': '丢包率'})
		line_chart.set_x_axis({'name': '监测时间'})
		line_chart.set_y_axis({'name': '丢包率（单位:%)'})

	    # 设置图表风格
		line_chart.set_style(11)
		line_chart.set_size({'width': 600, 'height': 250})
		line_chart.set_legend({'position': 'top'})
		worksheet.insert_chart('G1', line_chart, {'x_offset': 0, 'y_offset': 0})

	    #平均延时出图
		line_chart = workbook.add_chart({'type': 'line'})
		line_chart.add_series({
			'name': "=data!$E$1",
			'categories': '==data!$A$2:$A$%s'%str(len(timelist)+1),
			'values': '=data!$E$2:$E$%s'%str(len(res_arvglist)+1),
			'data_label':{'value': True},
	    })
		line_chart.set_title({'name': '延迟'})
		line_chart.set_x_axis({'name': '监测时间'})
		line_chart.set_y_axis({'name': '延迟（单位:ms)'})
		line_chart.set_style(11)
		line_chart.set_size({'width': 600, 'height': 250})
		line_chart.set_legend({'position': 'top'})
		worksheet.insert_chart('G14', line_chart, {'x_offset': 0, 'y_offset': 0})

	    #路由抖动
		line_chart = workbook.add_chart({'type': 'line'})
		line_chart.add_series({
			'name': "=data!$F$1",
			'categories': '==data!$A$2:$A$%s'%str(len(timelist)+1),
			'values': '=data!$F$2:$F$%s'%str(len(route_jitterlist)+1),
			'data_label':{'value': True},
		})
		line_chart.set_title({'name': '路由抖动'})
		line_chart.set_x_axis({'name': '监测时间'})
		line_chart.set_y_axis({'name': '1：抖动，0：无抖动'})
		line_chart.set_style(11)
		line_chart.set_size({'width': 600, 'height': 250})
		line_chart.set_legend({'position': 'top'})
		worksheet.insert_chart('G27', line_chart, {'x_offset': 0, 'y_offset': 0})
		workbook.close()

	def dolongping(self,obj,ipaddr):
		#row = 0
		if os.path.exists(self.longpingfilename):
			os.remove(self.longpingfilename)
		while True:
			if self.flag == 1:
				break
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

			if ttllist:
				if len(ttllist) > 1:
					returndict['route_jitter'] = 1
				else:
					returndict['route_jitter'] = 0
			
			logtime = time.strftime("%H:%M:%S",time.localtime())

			with open(self.longpingfilename,"a+") as logfile:
				logfile.writelines("%s,%s,%s,%s,%s,%s\n"%(logtime,returndict['packet_loss'],returndict['res_min'],returndict['res_max'],returndict['res_arvg'],returndict['route_jitter']))

			obj.l_longping_loss_r['text'] = returndict['packet_loss']+"%" if returndict['packet_loss'] else "信息获取失败"
			obj.l_longping_res_r['text'] = "%sms"%returndict['res_arvg'] if returndict['res_arvg'] else "信息获取失败"
			if returndict['route_jitter'] or isinstance(returndict['route_jitter'],int):

				if returndict['route_jitter'] == 0:
					obj.l_longping_jab_r['text'] = "无抖动"
				else:
					obj.l_longping_jab_r['text'] = "有抖动"

			###
			thisobj_ls_res_jt = ping_health.together(ping_health.get_loss(returndict),ping_health.get_responese(returndict),ping_health.get_jitter(returndict))
			if thisobj_ls_res_jt:
				if thisobj_ls_res_jt >= 80:
					obj.l_signal_r['text'] = "|||"
				elif 60 <= thisobj_ls_res_jt < 80:
					obj.l_signal_r['text'] = "||"
				elif 30 <= thisobj_ls_res_jt < 60:
					obj.l_signal_r['text'] = "|"
				else:
					obj.l_signal_r['text'] = "×"
			else:
				obj.l_signal_r['text'] = "×:获取失败"
			print("信号监测中...")
			time.sleep(1)

def return_ms(line):
	reslist=[]
	for i in range(3):
		try:
			reslist.append(line.split("ms")[i].split("=")[1].strip())
		except:
			reslist.append(None)
	return reslist


if __name__ == "__main__":
	pass