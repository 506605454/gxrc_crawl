#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: DavidHuang
@license: Apache Licence 
@contact: 506605454@qq.com
@site: http://www.davidHuang.com
@software: PyCharm
@file: thread_crawl.py
@time: 2016/10/24 22:11
"""
import threading
import time
import thread
import Queue
import gxrcw_page_content as gx

queueLock = threading.Lock()
workQueue = Queue.Queue(100)
threadID = 1
exitFlag = 0
threads = []


class MyThread(threading.Thread):
    def __init__(self, threadID, name, q, page):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.page = page

    def run(self):
        self.process_data(self.name, self.q)
        pass

    def process_data(self, thread_name, q):
        while not exitFlag:
            queueLock.acquire()
            if not workQueue.empty():
                link = q.get()
                print link
                queueLock.release()
                print thread_name + " 开始爬 ", link
                content = self.page.open_page(link)
                if content is not None:
                    content = content.decode('gbk')
                    page_clear_data = self.page.clear_data(content)
                    if page_clear_data is not None:
                        page.inser_data_base(page_clear_data)
                        print thread_name, " 已经爬完一条。"

                    else:
                        print "该页面已不存在。。。"
                    time.sleep(2)
                else:
                    pass
            else:
                queueLock.release()


if __name__ == '__main__':
    page = gx.PageDetail(80)
    page_index = 0
    for t in range(1, 80):
        string_name = "爬虫小朋友%d" % t
        thread = MyThread(threadID, string_name, workQueue, page)
        thread.start()
        threads.append(thread)
        threadID += 1
    while True:
        if workQueue.empty():
            queueLock.acquire()
            print "数据操作锁住填充数据"
            links = page.fetch_craw_link(page_index)
            if not len(links):
                print '数据库已经没有数据，爬虫结束，大家辛苦了'
                queueLock.release()
                break
            for l in links:
                workQueue.put(l[0])
            page_index += 80
            print "释放锁 给线程操作数据"
            queueLock.release()
    exitFlag = 1
    for t in threads:
        t.join()
    print "程序结束,恭喜发财。"
