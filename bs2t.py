#coding=utf-8

#
# Better Server Selection Tool
#
# Author: Pandarison##gmail.com
#
# 使用方法: python bs2t.py
#

import cookielib, urllib2, urllib
import json, time
import os, re, threading

debug = False

def requestIPs(host):
      try:
            #cookie
            cookieJar = cookielib.LWPCookieJar()  
            cookie_support = urllib2.HTTPCookieProcessor(cookieJar)  
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)  
            urllib2.install_opener(opener)

            #服务器地址
            urlServer = 'http://tools.fastweb.com.cn/index.php/Index/Mdig'
            urlServerData = 'http://tools.fastweb.com.cn/index.php/Index/sendMdig'
            urlServerResult = 'http://tools.fastweb.com.cn/index.php/Index/getMdigResultOne'
            #header  
            headers = {'User-Agent' : 'Mozilla/4.0', 'Referer' : '******'}  

            #打开主页面
            urllib2.urlopen(urlServer)  

            

            ##发送PING请求

            #Post数据 
            postData = {
                  'query_type':'A',
                  'domain_name':host,
                  'city':'6,7,8,1,2,3,4,5,15,27,28,29,30,31,22,23,24,25,26,16,17,18,9,10,11,12,13,14,19,20,21,32,33,34,36,37',
                  'isp':'1,2,3,5,8,12',
                  'rand':'5244'
            }   
            postData = urllib.urlencode(postData)  

            # POST
            if debug: print '正在提交请求.'
            request = urllib2.Request(urlServerData, postData, headers)  
            response = urllib2.urlopen(request)
            responseData = json.loads(response.read())

            if responseData['status'] == 1:
                  if debug: print '请求已提交.'
                  task_id = responseData['data']['task_id']
                  view_ids = responseData['data']['view_ids']
                  _from = responseData['data']['from']
                  result_id = 0
                  ipList = []
                  print '等待服务器返回数据.'
                  #每隔1.5秒检查返回结果
                  while True:
                        time.sleep(1.5)
                        #Post数据 
                        postData = {
                              'task_id':task_id,
                              'view_ids':view_ids,
                              'from':_from,
                              'query_type':'A',
                              'result_id':result_id
                        }   
                        postData = urllib.urlencode(postData)

                        # POST
                        request = urllib2.Request(urlServerResult, postData, headers)  
                        response = urllib2.urlopen(request)
                        responseData = json.loads(response.read())
                        

                        if responseData['status']==1 and responseData['info']=='0':
                              result_id = responseData['data']['result_id']
                              if type(responseData['data']) != dict: continue
                              for x in responseData['data'].values():
                                    for y in x:
                                          if type(y) != dict: continue
                                          if y['type']=='a':
                                                i = y['result'].index('(')
                                                ip = y['result'][:i]
                                                if not ip in ipList: 
                                                      ipList.append(ip)
                              if debug: print '已取得部分数据，继续等待. (%d条IP数据)' % len(ipList)
                        elif responseData['status']==0 and responseData['info']=='1':
                              print 'IP列表获取成功.'
                              return ipList
                        elif responseData['status']==1 and responseData['info']=='1':
                              raise Exception('获取IP列表过程中出现错误.')
                        else:
                              if debug: print '继续等待服务器返回数据.'
            else:
                  raise Exception(responseData['info'])
      except Exception, e:
            print '无法获取IP列表'
            raise e
count = [0]
total = [0]
def doPing(ip, rank, currentTh):
      try:
            cmd = 'ping -c 4 -q [ip]'.replace('[ip]', ip)
            rst = os.popen(cmd).read()
            rst = re.compile('min/avg/max/stddev.*?(\d*\.\d*)/(\d*\.\d*)/(\d*\.\d*)/(\d*\.\d*)').findall(rst)
            if rst != []:
                  rank[ip] = rst
            else:
                  rst = "无法连接."
            count[0] = count[0]+1
            if debug: print "(%d/%d)"%(count[0],total[0]), cmd, rst
            currentTh[0] = currentTh[0]-1
      except Exception, e:
            raise e

def requestSpeed(ipList, thLimit, rank):
      currentTh = [0]
      count[0] = 0
      total[0] = len(ipList)
      while True:
            time.sleep(0.1)
            if currentTh[0] >= thLimit: continue
            if len(ipList)==0:
                  break
            ip = ipList.pop()
            currentTh[0] = currentTh[0]+1
            dm = threading.Thread(target=doPing,args=(ip, rank, currentTh))
            dm.start()
      while True:
            if currentTh[0] == 0:
                  break

ip = raw_input('请输入域名(不含http://): ')
d = raw_input('是否开启调试(Y/Other): ')
c = raw_input('请输入Ping并发数: ')
c = int(c)
if d == 'Y' or d == 'y': debug = True
      
ipList = requestIPs(ip)
rank = {}
dm = threading.Thread(target=requestSpeed,args=(ipList, c, rank))
dm.setDaemon(False)
dm.start()
dm.join()

if rank == {}:
      print "所有IP地址都无法Ping通."
      exit()

rank = sorted(rank.items(), cmp=lambda x,y: cmp(float(x[1][0][1]), float(y[1][0][1])))
print '==================================='
print '可连接的服务器地址(按速度排序):'

for x in rank:
      print "%s    %s ms" %(x[0], x[1][0][1])
print '==================================='
cmd = 'ping -c 4 -q [ip]'.replace('[ip]', ip)
rst = os.popen(cmd).read()
if rst.find(rank[0][0]) >= 0:
      print "最快的IP地址和系统当前使用的服务器IP地址一致，不建议进行任何操作"
else:
      print "建议的服务器IP如下，请将下面一行添加到hosts文件中，或者路由器的DNS重定向中."
      print "%s %s" %(rank[0][0], ip)
print '==================================='

