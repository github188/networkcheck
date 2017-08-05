import speed_health

def info2html(start_time,end_time,userinfo,os_ver,dns,gw,check_ping,ftp,portcheck,check_url,tracert,dnslookup,route):


    #用户输入基本信息处理
    messages = "开始时间%s<br/>"%start_time
    messages += "结束时间%s<br/>"%end_time
    messages += "<b style='color:blue;'>[用户基本信息]</b><br/>"
    messages += "　　测试目的：　　%s<br/>"%userinfo[0]
    messages += "　　用户姓名：　　%s<br/>"%userinfo[1]
    messages += "　　用户联系方式：%s<br/>"%userinfo[2]
    messages += "　　用户邮箱地址：%s<br/>"%userinfo[3]
    messages += "　　组织/公司名：%s<br/>"%userinfo[4]
    messages += "　　用户设备型号：%s<br/>"%userinfo[5]
    messages += "　　用户设备串号：%s<br/>"%userinfo[6]
    messages += "　　软件名称：%s<br/>"%userinfo[7]

    #网络基本信息处理
    messages += "<b style='color:blue;'>[用户网络基本信息]</b><br/>"
    if os_ver:
        messages += "　　OS版本 ：   %s<br/>"%os_ver if os_ver else "　　OS版本 ：   信息获取失败<br/>"
    messages += "　　DNS服务器：   %s<br/>"%dns if dns else "　　DNS服务器：   信息获取失败<br/>"
    messages += "　　协作云解析IP：%s<br/>"%dnslookup if dnslookup else "　　协作云解析IP：   信息获取失败<br/>"
    messages += "　　网关地址 ：   %s<br/>"%gw if gw else "　　网关地址 ：   信息获取失败<br/>"

    if route:
        #内容中的\n在邮件中不能显示，所以需要将\n转换成html的换行符
        route = route.replace("\n\n","<br/>　　")
        messages += "<b style='color:blue;'>[用户网络路由]</b><br/>"
        messages += "　　%s<br/>"%route

    #路由跟踪
    if tracert:
        messages += "<b style='color:blue;'>[tracert路由跟踪]</b><br/>"
        node_id = 1
        for ip in tracert:
            for i in ip:
                messages += "　　%s：%s   :%s<br/>"%(node_id,i,ip[i])
                node_id += 1
    else:
        messages += "<b style='color:blue;'>[tracert路由跟踪]:Error:跟踪失败</b><br/>"

    #Ping检测结果处理
    messages += "<b style='color:blue;'>[Ping检查]</b><br/>"
    for x in check_ping:
        messages += "　<span style='color:#ff9224'>[Ping %s:%s]</span><br/>"%(x['ipaddr'],x['command'])

        messages += "　　丢包率：%s"%x['packet_loss']+r"%<br/>" if x['packet_loss'] else "　　丢包率：信息获取失败<br/>"
        messages += "　　最小延时：%sms<br/>"%x['res_min'] if x['res_min'] else "　　最小延时：信息获取失败或Ping失败<br/>"
        messages += "　　最大延时：%sms<br/>"%x['res_max'] if x['res_max'] else "　　最大延时：信息获取失败或Ping失败<br/>"
        messages += "　　平均延时：%sms<br/>"%x['res_arvg'] if x['res_arvg'] else "　　平均延时：信息获取失败或Ping失败<br/>"
        messages += "　　路由抖动：有抖动" if x['route_jitter'] else "　　路由抖动：无抖动<br/>"
    #web检测结果处理
    if check_url:
        messages += "<b style='color:blue;'>[URL访问检查]</b><br/>"
        for cu in check_url:
            messages += "　　<span style='color:#ff9224'>[%s]</span><br/>"%cu
            messages += "　　　　返回Code:　　%s<br/>"%check_url[cu][0]
            messages += "　　　　域名解析:　　%s<br/>"%check_url[cu][1]
            messages += "　　　　连接时间:　　%s<br/>"%check_url[cu][2]
            messages += "　　　　准备传输时间:%s<br/>"%check_url[cu][3]
            messages += "　　　　开始传输时间:%s<br/>"%check_url[cu][4]
            messages += "　　　　合计耗时:　　%s<br/>"%check_url[cu][5]
            messages += "　　　　下载容量:　　%s<br/>"%check_url[cu][6]
            messages += "　　　　包头容量:　　%s<br/>"%check_url[cu][7]
            messages += "　　　　下载速率:　　%s<br/>"%check_url[cu][8]
    else:
        messages += "<b style='color:blue;'>[URL访问检查:访问超时失败]</b><br/>"

    if ftp:
        #ftp检测结果处理
        messages += "<b style='color:blue;'>[FTP下载-上传速率检查]</b><br/>"

        if ftp[0]:
            down_ftp = speed_health.bps2KMG(ftp[0])
            messages += "　　下载速率:%s<br/>"%down_ftp
        else:
            messages +="　　下载速率:信息获取失败<br/>"
        if ftp[1]:
            up_ftp = speed_health.bps2KMG(ftp[1])
            messages += "　　上传速率:%s<br/>"%up_ftp
        else:
            messages +="　　上传速率:信息获取失败<br/>"
    else:
        messages += "<b style='color:blue;'>[FTP测速检查:超时失败]</b><br/>"
    #tcp端口检测处理
    messages += "<b style='color:blue;'>[端口检查]</b><br/>"
    for i in portcheck:
        messages += "　　%s:%s<br/>"%(i,portcheck[i])
    #返回整体结果（字符串）
    return messages