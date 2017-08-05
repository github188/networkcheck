import os
import re
import subprocess
import platform
import CCI_nw_checker

def get_gw():
	try:
		cmd = "route print 0.0.0.0"
		res = os.popen(cmd).readlines()
		for i in res:
			if "0.0.0.0" in i:
				return i.split()[2],"[Done]"
		return None,"[Error]:Gateway信息获取失败"
	except:
		return None,"[Error]:Gateway信息获取失败"

def get_route():
	try:
		returnmessage=""
		cmd = "route print -4"
		res = os.popen(cmd).readlines()
		ip_re=re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
		for i in res:
			ip = ip_re.search(i)
			if ip:
				returnmessage += "%s\n"%i
		if returnmessage:
			return returnmessage,"[Done]"
		else:
			return returnmessage,"[Error]:获取路由信息失败"
	except:
		return returnmessage,"[Error]:获取路由信息失败"

def get_dns():
	try:
		output = subprocess.Popen(["ipconfig", "/all"], stdout=subprocess.PIPE).communicate()[0].decode("gbk")
		dns_server_re = re.compile("DNS.*"+r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
		dns_server_match  = dns_server_re.search(output)
		if dns_server_match:
			dns_server = dns_server_match.group(0).split(":")[1].strip()
			return dns_server,"[Done]"
		else:
			return None,"[Error]:DNS信息取得失败"
	except:
		return None,"[Error]:DNS信息取得失败"

def get_os():
	try:
		return platform.platform(),"[Done]"
	except:
		return None,"[Error]:OS版本信息获取失败"

if __name__=="__main__":
	print(get_route()[0])