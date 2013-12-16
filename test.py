#!/usr/bin/python
import gevent.monkey
gevent.monkey.patch_socket()

import array
import gevent
import urllib2
import time


def crawl(pid):
    v = [0 for x in range(1024*300)]
    response = urllib2.urlopen('http://127.0.0.1')
    result = response.read()
    s = time.time()
    gevent.sleep(20)
    print('Process %s: %s' % (pid, time.time() - s))
    

def init():
    threads = []
    for i in range(1,1000):
        threads.append(gevent.spawn(crawl, i))
    gevent.joinall(threads)

init()

