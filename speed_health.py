def bps2KMG(up_down_speed):
    up_down_speed = int(up_down_speed)
    if pow(1024,2) > up_down_speed >= 1024:
        up_down_speed = str(round(up_down_speed/1024,2))+" kbps"
    elif pow(1024,3) > up_down_speed >= pow(1024,2):
        up_down_speed = str(round(up_down_speed/pow(1024,2),2))+" Mbps"
    elif pow(1024,4) > up_down_speed >= pow(1024,3):
        up_down_speed = str(round(up_down_speed/pow(1024,3),2))+" Gbps"
    else:
        up_down_speed=str(round(up_down_speed,2))+" bps"
    return up_down_speed

class bandwidth_rank:
	def __init__(self,inputbandwidth):
		self.bandwidth = inputbandwidth

	def get_rank(self):
		if self.bandwidth < 125*1024:
			return "带宽不足"
		elif self.bandwidth <= 256*1024:
			return "带宽低"
		elif self.bandwidth <= 384*1024:
			return "带宽中等"
		elif self.bandwidth <= 1000*1024:
			return "带宽良好"
		else:
			return "带宽通畅"

	def bps2KMG(self):
	    if pow(1024,2) > self.bandwidth >= 1024:
	        returnbandwidth = str(round(self.bandwidth/1024,2))+" kbps"
	    elif pow(1024,3) > self.bandwidth >= pow(1024,2):
	        returnbandwidth = str(round(self.bandwidth/pow(1024,2),2))+" Mbps"
	    #elif pow(1024,4) > self.bandwidth >= pow(1024,3):
	    elif self.bandwidth >= pow(1024,3):
	        returnbandwidth = str(round(self.bandwidth/pow(1024,3),2))+" Gbps"
	    else:
	        returnbandwidth = str(round(self.bandwidth,2))+" bps"
	    return returnbandwidth

	def get_mode_addvance(self):
		if isinstance(self.bandwidth,float) or isinstance(self.bandwidth,int):
			bandwidth_adv=self.bps2KMG()
			rank_a="带宽：%s，可选用蓝光1080p。"%bandwidth_adv
			rank_b="带宽：%s，可选用超清720p。"%bandwidth_adv
			rank_c="带宽：%s，可选用高清480p。"%bandwidth_adv
			rank_d="带宽：%s，可选用标清270p。"%bandwidth_adv
			rank_e="带宽：%s，只建议开音声会议。"%bandwidth_adv
			#带宽小于125kbps
			if self.bandwidth < 125*1024:
				return rank_e
			elif self.bandwidth <= 256*1024:
				return rank_d
			elif self.bandwidth <= 384*1024:
				return rank_c
			elif self.bandwidth <= 1000*1024:
				return rank_b
			else:
				return rank_a
		else:
			return None


if __name__=="__main__":
	a = bandwidth_rank(None)








