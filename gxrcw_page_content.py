#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: DavidHuang
@license: Apache Licence 
@contact: 506605454@qq.com
@site: http://www.davidHuang.com
@software: PyCharm
@file: gxrcw_page_content.py
@time: 2016/10/23 22:11
"""
from bs4 import BeautifulSoup
import urllib2
import random
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import re
import pymysql.cursors
import time
import socket

user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"
]


class PageDetail():
    def __init__(self, page_num):
        self.page_num = page_num
        pass

    def open_page(self, page_url):
        # 随机取user_agent 防止被禁止访问
        headers = {'User-Agent': user_agent[random.randint(0, 9)]}
        req = urllib2.Request(page_url, headers=headers)
        print '正在爬取页面...'
        content = None
        try:
            response = urllib2.urlopen(req, timeout=10)
            if response:
                content = response.read()
                response.close()
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                print 'Error code:', e.code
            elif hasattr(e, 'reason'):
                print 'Reason:', e.reason
        except socket.timeout as e:
            print '请求超时。。。休息一下。。'
            print type(e)  # catched
            time.sleep(5)

        finally:
            pass
        if content is not None:
            return content
        else:
            self.open_page(page_url)

    def find_content(self, page_content):
        soup = BeautifulSoup(page_content, "html.parser")
        contents = soup.select("#content > div.gsR_con > table > tbody > tr > td")
        company = soup.find("a", href=re.compile('\?EnterpriseId+=[^\s]*'))
        gz_info_txt = soup.find("div", class_="gz_info_txt")
        position_name = soup.find('h1', id="positionName")
        return contents, company, gz_info_txt, position_name

    def inser_data_base(self, data):
        connection = pymysql.connect(host="localhost", user="root", password="506605454", db="zhaopin",
                                     charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                sql = "insert into `page_content`(`SALARY`,`PROFESSIONAL`,`COMPANY`," \
                      "`EDUCATION`,`WORK_EXPERIENCE`," \
                      "`AGE`,`MAJOR`,`CONTENT_INFO`,`WEB_SIDE`,`ADDR`,`HIRE_TIME`)" \
                      " VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, data)

                connection.commit()
                print '存储数据库...'
        except Exception as e:
            print e
        finally:
            connection.close()

    def fetch_craw_link(self, page_index):
        connection = pymysql.connect(host="localhost", user="root", password="506605454", db="zhaopin",
                                     charset='utf8mb4')
        result = None
        try:
            with connection.cursor() as cursor:
                sql = "select `LINK` from `title_link` LIMIT %s,%s "
                cursor.execute(sql, (page_index, self.page_num))
                result = cursor.fetchall()
                result = list(result)
                print '存储数据库...'
        except Exception as e:
            print e
        finally:
            connection.close()
        if result is not None:
            return result
        else:
            return None

    def clear_data(self, page_content):
        table_data, company_data, gz_info_txts, position_name_d = self.find_content(page_content)

        if len(table_data):
            education = table_data[1].text.strip()
            salary = table_data[2].text.strip()
            work_experience = table_data[3].text.strip()
            addr = table_data[4].text.strip()
            major = table_data[6].text.strip()
            age = table_data[8].text.strip()
            hire_time = table_data[13].text.strip()
            page_detail = (
                salary, position_name_d.text.strip(),
                company_data.text.strip(), education,
                work_experience, age, major,
                gz_info_txts.text.strip(), "广西人才网",
                addr, hire_time)
            return page_detail
        else:
            return None

#
# url = "http://www.gxrc.com/WebPage/JobDetail.aspx?EnterpriseID=1499792&PositionId=2668140"
#
# if __name__ == '__main__':
#     page = PageDetail(5)
#     # content = page.open_page(url).decode('gbk')
#     # page_clear_data = page.clear_data(content)
#     # page.inser_data_base(page_clear_data)
#     # page.fetch_craw_link(0)[0][0]
#     for i in page.fetch_craw_link(0):
#         print i[0]