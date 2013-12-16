#!/usr/bin/python
import gevent.monkey
gevent.monkey.patch_socket()

from gevent.pool import Pool
import gevent
import urllib2
import time
pool = Pool(10000)

def crawl(pid):
    print('started %s' % (pid))
    url = 'http://localhost:6000/' + str(pid);
    print url
    response = urllib2.urlopen(url).read();
    st = time.time();
    print('Process %s: %s' % (pid, (time.time() - st)))
    

def asynchronous():
   for i in range(1,10000):
     pool.spawn(crawl, i)
   pool.join()

asynchronous();
