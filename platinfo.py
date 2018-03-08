# -*- coding: UTF-8 -*-


import re
import requests
import json
import mysql.connector
from bs4 import BeautifulSoup


DOWN_URL = 'https://www.wdzj.com/dangan/search?filter'


def downloadpage(url):
    return requests.get(url,headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}).content


def parsepage(html,index):
    print('完成第 %s 页' % index)
    soup = BeautifulSoup(html,"lxml")
    tul = soup.find('ul',class_ = 'terraceList')
    names = []
    rates = []
    allbalance = []
    createtime = []
    status = []

    for litag in tul.find_all('li',class_ = 'item'):
        names.append(litag.div.h2.a.get_text())
        rates.append(litag.find('label',class_ = 'biaotag').em.get_text())
        allbalance.append(re.split(r'[：万]', litag.find('a',class_ = 'itemConLeft').contents[3].get_text())[1].strip())
        createtime.append(re.split(r'：', litag.find('a',class_ = 'itemConLeft').contents[7].get_text())[1])
        itag = litag.find('h2').find('i')
        
        if itag == None:
            status.append(0) # 正常'dangan_icon ty'
        elif itag.get('class')[1] == 'txkn':
            status.append(1) # 提现困难
        elif itag.get('class')[1] == 'ty':
            status.append(2) # 停业
        elif itag.get('class')[1] == 'pl':
            status.append(3) # 跑路
        else:
            status.append(0) # 正常


    conn = mysql.connector.connect(user='root', password='123456', database='db')
    cursor = conn.cursor()

    for i in range(0,len(names)-1):
        cursor.execute('insert into platinfo (name,createtime,incomeRate,allbalance,status) values (%s, %s,%s, %s,%s) ', [names[i],createtime[i],rates[i],allbalance[i],status[i]])

    cursor.close()
    conn.commit()

    # nextpage = soup.find('div',class_ = 'terrace').find('a',class_ = 'pageindex')
    # if nextpage:
    #     pagenum = nextpage.get('currentnum')
    #     print('完成第 %s 页' % pagenum)
    #     return DOWN_URL + '&currentPage=' + pagenum
    # else:
    #     return None


def main():
    for i in range(1,242):
        url = DOWN_URL + '&currentPage=' + str(i)
        html = downloadpage(url)
        parsepage(html,i)

if __name__ == '__main__':
    main()