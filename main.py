from typing import List, Optional

import re
import random
import time
import urllib
import urllib.request
import urllib.parse
import pymysql

from fastapi import FastAPI, Body, Header
from sshtunnel import SSHTunnelForwarder

app = FastAPI()

# 伪装用Header
my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

# def connectMysql():
#     # 打开数据库连接
#     db = pymysql.connect(host="localhost", user="root",
#                          password="5400018sss", database="szfc")
#     # 使用 cursor() 方法创建一个游标对象 cursor
#     return db.cursor()


# 搜索批次信息


@app.post("/apicc/searchPc")
def searchPc(
    name: Optional[str] = Body("", embed=True),
    rangeMap: Optional[str] = Body("", embed=True),
    organization: Optional[str] = Body("", embed=True)
):
    try:
        # 获取随机码及查询校验密钥
        firstUrl = "http://spf.szfcweb.com/szfcweb/DataSerach/SaleInfoProListIndex.aspx"
        # 随机选择一个Header伪装成浏览器
        response = urllib.request.Request(firstUrl)
        response.add_header('User-Agent', random.choice(my_headers))
        resp = urllib.request.urlopen(response)
        # 随机码
        code = re.search(
            r'(\([a-z0-9]+\([a-z0-9]+\)\))', resp.geturl(), re.I).group()
        # 查询校验密钥
        resp = resp.read().decode('utf-8')
        __VIEWSTATE = re.search(
            r'(id="__VIEWSTATE" value="[a-z0-9=+/]+)', resp, re.I).group().replace('id="__VIEWSTATE" value="', "")
        __VIEWSTATEGENERATOR = re.search(
            r'(id="__VIEWSTATEGENERATOR" value="[a-z0-9]+)', resp, re.I).group().replace('id="__VIEWSTATEGENERATOR" value="', "")
        __EVENTVALIDATION = re.search(
            r'(id="__EVENTVALIDATION" value="[a-z0-9=+/]+)', resp, re.I).group().replace('id="__EVENTVALIDATION" value="', "")
        time.sleep(1)
        # 获取批次信息
        sUrl = "http://spf.szfcweb.com/szfcweb/%s/DataSerach/SaleInfoProListIndex.aspx" % code
        req = urllib.request.Request(sUrl)
        req.add_header('User-Agent', random.choice(my_headers))
        req.add_header(
            'Referer', "http://spf.szfcweb.com/szfcweb/%s/DataSerach/SaleInfoProListIndex.aspx" % code)
        req.data = urllib.parse.urlencode({
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "__EVENTVALIDATION": __EVENTVALIDATION,
            "ctl00$MainContent$txt_Pro": name,
            "ctl00$MainContent$ddl_RD_CODE": rangeMap,
            "ctl00$MainContent$txt_Com": organization,
            "ctl00$MainContent$bt_select": "查询"
        }).encode('utf-8')
        # 批次信息
        pcResp = urllib.request.urlopen(req).read().decode('utf-8')
        pcCode = re.findall(r'(SPJ_ID=[a-z0-9-]+)', pcResp, re.I | re.M)
        pcName = re.findall(
            r'(>[\u4e00-\u9fa50-9（）]+</a></td><td)', pcResp, re.I | re.M)
        pcOrganization = re.findall(
            r'(false;\">[\u4e00-\u9fa50-9（）]+<)', pcResp, re.I | re.M)
        pcInfo = []
        for index, pc in enumerate(pcCode):
            pcInfo.append({
                "name": pcName[index].replace("</a></td><td", "").replace(">", ""),
                "organization": pcOrganization[index].replace("false;\">", "").replace("<", ""),
                "code": pc.replace("SPJ_ID=", "")
            })
        return {
            "message": "",
            "code": 0,
            "data": pcInfo,
            "VCode": code
        }
    except Exception as err:
        print(err)
        return {
            "message": "服务器错误",
            "code": -1
        }

# 搜索楼栋信息


@app.get("/apicc/searchLou")
def searchLou(SPJ_ID: Optional[str] = None, code: Optional[str] = None):
    try:
        # 确认随机码
        sUrl = "http://spf.szfcweb.com/szfcweb/%s/DataSerach/SaleInfoBudingShow.aspx?SPJ_ID=%s" % (
            code, SPJ_ID)
        req = urllib.request.Request(sUrl)
        req.add_header('User-Agent', random.choice(my_headers))
        req.add_header(
            'Referer', "http://spf.szfcweb.com/szfcweb/%s/DataSerach/SaleInfoBudingShow.aspx?SPJ_ID=de4c23ba-8d04-402c-a6b0-d187588086a7" % code)
        # 楼信息
        louResp = urllib.request.urlopen(req).read().decode('utf-8')
        louCode = re.findall(r'(PBTAB_ID=[a-z0-9_]+)', louResp, re.I | re.M)
        louNum = re.findall(
            r'([0-9]+</a>(</font>)*</td><td>)', louResp, re.I | re.M)
        louInfo = []
        for index, lou in enumerate(louCode):
            strinfo = re.compile('</a>(</font>)*</td><td>', re.I)
            louInfo.append({
                "number": strinfo.sub('', louNum[index][0]),
                "code": lou.replace("PBTAB_ID=", "")
            })
        return {
            "message": "",
            "code": 0,
            "data": louInfo
        }
    except Exception as err:
        print(err)
        return {
            "message": "服务器错误",
            "code": -1
        }

# 搜索售卖信息


@app.get("/apicc/searchFw")
def searchFw(PBTAB_ID: Optional[str] = None, code: Optional[str] = None):
    try:
        loginBaiduUrl = "http://spf.szfcweb.com/szfcweb/%s/DataSerach/SaleInfoHouseShow.aspx?PBTAB_ID=%s&SPJ_ID=de4c23ba-8d04-402c-a6b0-d187588086a7" % (
            code, PBTAB_ID)
        req = urllib.request.Request(loginBaiduUrl)
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', random.choice(my_headers))
        req.add_header('Connection', 'Keep-Alive')
        req.add_header(
            'Referer', "http://spf.szfcweb.com/szfcweb/%s/DataSerach/SaleInfoBudingShow.aspx?SPJ_ID=de4c23ba-8d04-402c-a6b0-d187588086a7" % code)
        resp = urllib.request.urlopen(req)
        respInfo = resp.read().decode('utf-8')
        return {
            "message": "",
            "code": 0,
            "data": re.search(r'(<table cellspacing[\w\W]+\r\n\t</table>)', respInfo, re.I).group()
        }
    except Exception as err:
        print(err)
        return {
            "message": "服务器错误",
            "code": -1
        }


@app.get("/apicc/getLouData")
def getLouData(code: Optional[str] = None, date: Optional[str] = None):
    try:
        with SSHTunnelForwarder(
                ("47.92.100.56", 22),
                ssh_username="root",
                ssh_password="songbaixinA1",
                remote_bind_address=('127.0.0.1', 3306)
        ) as tunnel:
            db = pymysql.connect(host='127.0.0.1', port=tunnel.local_bind_port,
                                 user='root', password='5400018ss', database="szfc")
            cursor = db.cursor()
            # SQL 查询语句
            sql = "SELECT * FROM fw WHERE code = '%s' and date = '%s'" % (
                code, date)
            try:
                # 执行SQL语句
                cursor.execute(sql)
                # 获取记录列表
                result = cursor.fetchone()
                code = result[1]
                data = result[2]
                date = result[3]
                return {
                    "message": "",
                    "code": 0,
                    "data": data
                }
            except Exception as err:
                print("err: %s" % err)
    except Exception as err:
        print("err: %s" % err)
        return {
            "message": "服务器错误",
            "code": -1
        }


@app.post("/apicc/saveLouData")
def saveLouData(
        code: Optional[str] = Body("", embed=True),
        date: Optional[str] = Body("", embed=True),
        data: Optional[str] = Body("", embed=True)):
    try:
        with SSHTunnelForwarder(
                ("47.92.100.56", 22),
                ssh_username="root",
                ssh_password="songbaixinA1",
                remote_bind_address=('127.0.0.1', 3306)
        ) as tunnel:
            db = pymysql.connect(host='127.0.0.1', port=tunnel.local_bind_port,
                                 user='root', password='5400018ss', database="szfc")
            cursor = db.cursor()
            sql = "INSERT INTO fw(code, data, date) VALUES ('%s', '%s', '%s')" % (
                code, data, date)
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                cursor.connection.commit()
            except Exception as err:
                print(err)
                # 如果发生错误则回滚
                db.rollback()
            return {
                "message": "",
                "code": 0
            }
    except Exception as err:
        print(err)
        return {
            "message": "服务器错误",
            "code": -1
        }
