
pinglist=['192.168.11.254','command','0','10','20','19']


def get_slow_node_list(pinglist):
	returnlist = []
	for p in pinglist:
		result = together(get_loss(p),get_responese(p),get_jitter(p))
		if result < 80:
			returnlist.append(p[0])
	return returnlist

def get_loss(pinglist):
	#loss = pinglist[2]
	loss = pinglist['packet_loss']
	loss_health = 100-int(loss) if loss else None
	return loss_health

def get_responese(pinglist):
	responese_health = 100
	#responese =  pinglist[5]
	responese = pinglist['res_arvg']
	if responese:
		responese = int(responese)
		if responese <= 20:
			return responese_health
		elif responese >= 220:
			responese_health = 0
			return responese_health
		else:
			responese_health = (220-int(responese))/2
			return int(responese_health)

def get_jitter(pinglist):
	jitter_health = 100
	j_min = pinglist['res_min']
	#print(j_min)
	j_max = pinglist['res_max']
	#print(j_max)
	if j_min and j_max:
		jitter = int(j_max) - int(j_min)
		#print(jitter)
		if jitter >= 100:
			jitter_health = 0
			return jitter_health
		else:
			jitter_health = int(100 - jitter)
			#print("****%s"%jitter_health)
			return jitter_health
	else:
		jitter_health = None

def together(loss,response,jitter):
	result = 0
	if not isinstance(loss,int) or not isinstance(response,int):
		#loss或者response为空，就不计算 结果
		return None
	elif not jitter:
		#jitter为空,只计算loss和response的结果
		result = int(loss*0.7 + response*0.3)
		#print("****%s"%result)
	else:
		result = int(loss*0.5 + response*0.3 + jitter*0.2)
		#print("****%s:%s:%s:%s"%(loss,response,jitter,result))
	return result

if __name__=="__main__":
	x=get_loss(pinglist)
	print(x)
	y=get_responese(pinglist)
	print(y)
	z=get_jitter(pinglist)
	print(z)
	print(together(x,y,z))

