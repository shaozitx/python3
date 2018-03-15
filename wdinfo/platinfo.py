# -*- coding: UTF-8 -*-


import re
import requests
import json
import mysql.connector
from bs4 import BeautifulSoup


DOWN_URL = 'https://www.wdzj.com/dangan/search?filter'
DOWN360_URL = 'https://www.rong360.com/licai-p2p/pingtai/rating'
DOWNTY_URL = 'http://www.p2peye.com/shuju/ptsj/'
DB_NAME = 'db'

def downloadpage(url):
    return requests.get(url,headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}).content


# 360数据初始化
def parser360page(url):
    html = downloadpage(url)
    soup = BeautifulSoup(html,"lxml")
    div1 = soup.find("div",class_ = 'loan-des wrap-clear')
    bankname = div1.contents[3].contents[8].get_text()
    createtime = div1.contents[1].contents[5].get_text()
    registerm = div1.contents[1].contents[2].get_text()
    print(createtime)
    r = re.match(r"(\d{4})(.*?)(\d{2})(.*?)(\d{2})(.*?)",createtime)
    createtime = r.group(1) +"-"+ r.group(3) +"-"+ r.group(5)
    div2 = soup.find('div',class_ = 'loan-msg-cons tab-cons')
    if div2:
        platdes = div2.contents[1].contents[2].get_text()
    else:
        platdes = ''
    
    return bankname,platdes,createtime,registerm

def r360info():
    html = downloadpage(DOWN360_URL)
    soup = BeautifulSoup(html,"lxml")
    tbodytag = soup.find("tbody",id = 'ui_product_list_tbody')

    # 连接数据库
    conn = mysql.connector.connect(user='root', password='123456', database=DB_NAME)
    cursor = conn.cursor()
    names = []
    banknames = []
    platdess = []
    createtimes = []
    registerms = []
    for trtag in tbodytag.find_all('tr'):
        names.append(trtag.find('td',class_ = 'pt_name').a.get_text())
        bankname,platdes,createtime,registerm = parser360page(trtag.get('click-url'))
        banknames.append(bankname)
        platdess.append(platdes)
        createtimes.append(createtime)
        registerms.append(registerm)

    for i in range(0,len(names)-1):
        cursor.execute('UPDATE platinfo set createtime = %s , bankname = %s , platdes = %s , registercapital = %s WHERE `name` = %s', [createtimes[i],banknames[i],platdess[i],registerms[i],names[i]])

    cursor.close()
    conn.commit()
        

# 天眼数据初始化
def wdtyinfo():
    html = downloadpage(DOWNTY_URL)
    soup = BeautifulSoup(html,"lxml")
    tbodytag = soup.find('tbody')
    name = []
    turnover = []
    incomeRate = []
    loannum = []
    loanPeriod = []
    pinvestnum = []
    fuload = []
    allbalance = []
    flowincome = []
    for trtag in tbodytag.find_all("tr"):
        name.append(trtag.find("td",class_ = 'name').a.get_text().strip())
        print(trtag.find("td",class_ = 'name').a.get_text().strip())
        turnover.append(trtag.find("td",class_ = 'total').get_text().strip())
        incomeRate.append(trtag.find("td",class_ = 'rate').get_text().strip())
        loannum.append(trtag.find("td",class_ = 'pnum').get_text().strip())
        loanPeriod.append(trtag.find("td",class_ = 'cycle').get_text().strip())
        pinvestnum.append(trtag.find("td",class_ = 'p1num').get_text().strip())
        fuload.append(trtag.find("td",class_ = 'fuload').get_text().strip())
        allbalance.append(trtag.find("td",class_ = 'alltotal').get_text().strip())
        flowincome.append(trtag.find("td",class_ = 'capital').get_text().strip())
    
    conn = mysql.connector.connect(user='root', password='123456', database=DB_NAME)
    cursor = conn.cursor()
    for i in range(0,len(name)):
        cursor.execute('UPDATE  platinfo set  turnover=%s,incomeRate=%s,loannum=%s,loanPeriod=%s,pinvestnum=%s,fuload=%s,allbalance=%s,flowincome=%s WHERE name=%s', [turnover[i],incomeRate[i],loannum[i],loanPeriod[i],pinvestnum[i],fuload[i],allbalance[i],flowincome[i],name[i]])

    cursor.close()
    conn.commit()



# 数据初始化
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


    conn = mysql.connector.connect(user='root', password='123456', database=DB_NAME)
    cursor = conn.cursor()

    for i in range(0,len(names)):
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

# 数据初始化
def datainit():
    for i in range(1,242):
        url = DOWN_URL + '&currentPage=' + str(i)
        html = downloadpage(url)
        parsepage(html,i)


def main():
    # datainit()
    # r360info()
    wdtyinfo()
    
if __name__ == '__main__':
    main()













