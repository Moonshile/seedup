import urllib
import threading
import _thread
import time
import random
from urllib import request
from urllib import parse
from collections import deque
from bs4 import BeautifulSoup
import re

#request任务队列
request_tasks=deque([])
#paser任务队列
parse_tasks=deque([])
#save存储队列
save_tasks=deque([])
#主线程工作是否完成
exitFlag0 = False
exitFlag1 = False

def parseHtml(str): #解析获取的html文件并将结果写入文件
    soup=BeautifulSoup(open(str,encoding='UTF-8'),'lxml')
    #print(soup.find('ul',id='houseList'))
    ul=soup.find('ul',id='houseList')
    for li in ul.find_all('li',class_='clearfix'):
        f_title=li.find('div',class_='txt').h3.a.get_text()
        f_title_small=li.find('div',class_='txt').h4.a.get_text()
        f_size=li.find('div',class_='detail').p.find_all('span')[0].get_text()
        f_floor=li.find('div',class_='detail').p.find_all('span')[1].get_text()
        f_structure=li.find('div',class_='detail').p.find_all('span')[2].get_text()
        f_distance=li.find('div',class_='detail').find_all('p')[1].span.get_text()
        f_tags=[]
        for tags in li.find('p',class_='room_tags').find_all('span'):
            f_tags.append(tags.get_text())
        if li.find('p',class_='room_tags').find('a'):
            f_tags.append(li.find('p',class_='room_tags').find('a').get_text())
        #f_price=li.find('div',class_='priceDetail').find_all('span',class_='num')  #获取价格
        f_result.write(f_title+','+f_title_small+','+f_size+','+f_floor+','+f_structure+','+f_distance+','+'|'.join(f_tags))
        f_result.write('\n')
        
def getpage():  #根据url获取下载网页    
    tempid=1;
    while ((not exitFlag0) or (len(request_tasks)!=0)):
        flag=True
        queueLock.acquire()
        if len(request_tasks)!=0:
            url=request_tasks.popleft()
            print('删除队列'+url)
        else:
            flag=False
            print('队列为空')
            
        queueLock.release()           
        if flag:           
            user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            headers={'User-Agent':user_agent}
            req=request.Request(url,headers=headers)
            res=urllib.request.urlopen(req)
            filename='data'+str(tempid)+'.html'
            f=open(filename,'wb')
            f.write(res.read())
            f.close()            
            parse_tasks.append(filename)
            print(parse_tasks)
            print('网页'+str(tempid)+'下载完成！')
            parseHtml('data'+str(tempid)+'.html') #解析html并写入文件
            tempid+=1
            time.sleep(round(random.random(),2))
        else:            
            time.sleep(0.1)
    print("下载线程结束！")
    exitFlag1=True
    print(parse_tasks)
    f_result.close()

def getpageNum(url):
    #下载链接
    user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    headers={'User-Agent':user_agent}
    req=request.Request(url,headers=headers)
    res=urllib.request.urlopen(req)
    #解析页码
    flag=False
    numsoup=BeautifulSoup(res,'lxml')
    if numsoup.find('div',id='page'):
        for child in numsoup.find_all('span'):
            if re.match(r'共(.*)页',child.get_text()):
                flag=True
                matchgroup = re.match(r'共(.*)页',child.get_text())
                num=matchgroup.group(1)
                return int(num)
        if flag==False:
            return 1
    else:
        return 1
        


area=urllib.parse.quote_plus(input("请输入您要查询的区域：\n"))
#获取查询的地址页面数量
urlp='http://www.ziroom.com/z/nl/z2.html?qwd='+area
pageNum=getpageNum(urlp)
queueLock = threading.Lock()

#开启网页下载解析线程
try:
    _thread.start_new_thread(getpage,()) 
    #_thread.start_new_thread(parseHtml,())
except:
    print('无法启动访问和下载线程！')
    
f_result=open('result.csv','a+')

#构造urls，测试用13个网页，搜索城市：北京
for i in range(1,pageNum+1):
    url='http://www.ziroom.com/z/nl/z2.html?qwd='+area+'&p='+str(i)
    queueLock.acquire()
    request_tasks.append(url)
    print('添加队列'+url)
    queueLock.release()
    time.sleep(0.1)
exitFlag0 = True

#print(request_tasks)


