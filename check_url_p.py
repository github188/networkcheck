import pycurl
import certifi
import threading
class Mycallback:
    def __init__(self):
        self.contents = ''
    def callback(self,curl):
        curl=str(curl)
        self.contents = self.contents + curl
def check_url():
    #定义一个返回用的空字典
    returndict={}
    try:
        urls = ["https://huiyi.citycloud.com.cn"]
        #urls = cf.items("webcheck")[0][1].split(",")
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
            #except Exception as e:
                #print(e)
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
    #except Exception as e:
        #print(e)
        return None,"[Error]:Http/Https检测出错"

if __name__=="__main__":
    print(check_url())