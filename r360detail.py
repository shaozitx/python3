# -*- coding: UTF-8 -*-


import requests
import mysql.connector
from bs4 import BeautifulSoup
import re

DOWNLOAD_URL = 'https://www.rong360.com/licai-p2p/pingtai/rating'

def downloadpage(url):
    return requests.get(url,headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}).content


def parsepage(url):
    html = downloadpage(url)
    soup = BeautifulSoup(html,"lxml")
    div1 = soup.find("div",class_ = 'loan-des wrap-clear')
    bankname = div1.contents[3].contents[8].get_text()
    createtime = div1.contents[1].contents[5].get_text()
    print(createtime)
    r = re.match(r"(\d{4})(.*?)(\d{2})(.*?)(\d{2})(.*?)",createtime)
    createtime = r.group(1) +"-"+ r.group(3) +"-"+ r.group(5)
    div2 = soup.find('div',class_ = 'loan-msg-cons tab-cons')
    if div2:
        platdes = div2.contents[1].contents[2].get_text()
    else:
        platdes = ''
    
    return bankname,platdes,createtime


def main():

    html = downloadpage(DOWNLOAD_URL)
    soup = BeautifulSoup(html,"lxml")
    tbodytag = soup.find("tbody",id = 'ui_product_list_tbody')

    # 连接数据库
    conn = mysql.connector.connect(user='root', password='123456', database='db')
    cursor = conn.cursor()
    names = []
    banknames = []
    platdess = []
    createtimes = []
    for trtag in tbodytag.find_all('tr'):
        names.append(trtag.find('td',class_ = 'pt_name').a.get_text())
        bankname,platdes,createtime = parsepage(trtag.get('click-url'))
        banknames.append(bankname)
        platdess.append(platdes)
        createtimes.append(createtime)

    for i in range(1,len(names)-1):
        cursor.execute('UPDATE platinfo set createtime = %s , bankname = %s , platdes = %s WHERE `name` = %s', [createtimes[i],banknames[i],platdess[i],names[i]])

    cursor.close()
    conn.commit()
        



if __name__ == '__main__':
    main()