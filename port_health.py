

def together(portdict):
	ng_port_list=[]
	if portdict:
		sum_ok = 0
		for i in portdict:
			if portdict[i] == "OK":
				sum_ok += 1

			else:
				ng_port_list.append(i)
		port_health = int(sum_ok / len(portdict) * 100)

		return port_health,ng_port_list
	else:
		return None,None

if __name__=="__main__":
	print(together({'114.80.138.131:22': 'NG', 'huiyi.citycloud.com.cn:80': 'OK', '114.114.114.114:53': 'OK'}))
