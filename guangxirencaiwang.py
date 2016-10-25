#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: DavidHuang
@license: Apache Licence 
@contact: 506605454@qq.com
@site: http://www.davidHuang.com
@software: PyCharm
@file: guangxirencaiwang.py
@time: 2016/10/22 11:50
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

basic_url = "http://s.gxrc.com/sJob"
kw_list = ['android']
kw_url = 'http://s.gxrc.com/sJob?schType=1&page=1&pageSize=20&orderType=0&listValue=1&keyword='


class Title():
    def __init__(self):

        pass
        # self.url = 'http://s.gxrc.com/sJob?schType=1&keyword=java&District=&PosType=&Industry='

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

    def get_title(self, page_content):
        soup = BeautifulSoup(page_content, "html.parser")
        title_links = soup.find_all('a', href=re.compile('&PositionId+=[^\s]*'))
        print '抓取标题链接...'
        print '共有%d个链接...', len(title_links)
        return title_links

    def insert_title_link(self, data):
        connection = pymysql.connect(host="localhost", user="root", password="506605454", db="zhaopin",
                                     charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                sql = "insert into `TITLE_LINK`(`TITLE`,`LINK`,`FROM`,`TYPE`) VALUE (%s,%s,%s,%s)"
                cursor.executemany(sql, data)
                connection.commit()
                print '存储数据库...'
        except Exception as e:
            print e
        finally:
            connection.close()

    def crawl_page_title(self, page_content, kw):
        data_list = []
        title_data = self.get_title(page_content)
        if len(title_data):
            for i in title_data:
                data_list.append((i.text, i['href'], '广西人才网', kw))
            if len(data_list):
                self.insert_title_link(data_list)

    def get_next_page_link(self, page_content):
        soup = BeautifulSoup(page_content, "html.parser")
        next_page_link = soup.find_all('a', text='下一页')
        print '获取下一页...'
        return next_page_link

    def begin(self, kw):
        print '开始抓取' + kw + '类招聘信息'
        url = kw_url + kw
        while True:
            page = self.open_page(url)
            self.crawl_page_title(page, kw)
            next_link = self.get_next_page_link(page)
            if len(next_link):
                page = self.open_page(basic_url + next_link[0]['href'])
                self.crawl_page_title(page, kw)
                url = basic_url + next_link[0]['href']
                time.sleep(2)
                print '休息一下,就两秒钟...'
            else:
                print '抓完了' + kw
                break


class Page():
    def __init__(self):
        pass




if __name__ == '__main__':
    title = Title()
    while len(kw_list):
        kw = kw_list.pop()
        title.begin(kw)
    print '已经没有关键词了，我睡啦'
