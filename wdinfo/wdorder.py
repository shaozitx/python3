# -*- coding: UTF-8 -*-


import re
import requests
import json
import mysql.connector
from bs4 import BeautifulSoup

WDTY_URL = 'http://www.p2peye.com/rating'
R360_URL = 'https://www.rong360.com/licai-p2p/pingtai/rating'
WDZJ_URL = 'https://www.wdzj.com/dangan/search?filter=e1&sort=3'
DB_NAME = 'db'
NAMES = []


def downloadpage(url):
    return requests.get(url,headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}).content

def wdtyorder():
    html = downloadpage(WDTY_URL)
    soup = BeautifulSoup(html,"lxml")
    tbodytag = soup.find_all("script")

    i = 0
    orders = []
    for trtag in tbodytag:
        i = i + 1
        if i == 7:
            r = re.match(r'(.*?)(\[\{.*?\}\])(.*?)',trtag.get_text().strip())
            test=re.sub('\'','\"',r.group(2))
            orders = json.loads(test)

    wdtydict = {}
    i = 0
    for loads in orders:
        i = i + 1
        wdtydict[loads["plat_name"]] = i

    conn = mysql.connector.connect(user='root', password='123456', database=DB_NAME)
    cursor = conn.cursor()
    
    for k,v in wdtydict.items():
        cursor.execute('UPDATE platinfo set torder = %s WHERE `name` = %s', [v,k])

    cursor.close()
    conn.commit()


def r360order():
    html = downloadpage(R360_URL)
    soup = BeautifulSoup(html,"lxml")
    tbodytag = soup.find("tbody",id = 'ui_product_list_tbody')
    pdict = {}
    for trtag in tbodytag.find_all('tr'):
        pdict[trtag.td.a.get_text()] = trtag.find("td",class_ = 'pingji').get_text().replace(' ','').strip()     
    
    conn = mysql.connector.connect(user='root', password='123456', database=DB_NAME)
    cursor = conn.cursor()
    for k,v in pdict.items():
        cursor.execute('UPDATE platinfo set rorder = %s WHERE `name` = %s', [v,k])

    cursor.close()
    conn.commit()


def wdzjorder():


    allnames = []
    for i in range(1,77):
        url = WDZJ_URL + '&currentPage='+str(i)
        for name in parsewdzj(url,i):
            allnames.append(name)

    conn = mysql.connector.connect(user='root', password='123456', database=DB_NAME)
    cursor = conn.cursor()
    for i in range(0,len(allnames)):
        cursor.execute('UPDATE platinfo set worder = %s WHERE `name` = %s', [i+1,allnames[i]])

    cursor.close()
    conn.commit()


def parsewdzj(url,index):
    print('这是第%s页'%index)
    html = downloadpage(WDZJ_URL)
    soup = BeautifulSoup(html,"lxml")
    tbodytag = soup.find("ul",class_ = 'terraceList')
    names = []
    for litag in tbodytag.find_all('li',class_ = 'item'):
        names.append(litag.div.h2.a.get_text())
    return names
    

def main():
    # wdtyorder()
    r360order()
    # wdzjorder()

    
    
    



if __name__ == '__main__':
    main()