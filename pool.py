#!/usr/bin/python
import gevent.monkey
gevent.monkey.patch_socket()

from gevent.pool import Pool
import array
import gevent
import urllib2
import time
from gevent.server import StreamServer

pool = Pool(10)

def crawl(pid):
    v = [0 for x in range(1024*1024)]
    print('started %s' % (pid))
    response = urllib2.urlopen('http://127.0.0.1')
    result = response.read()
    s = time.time()
    #gevent.sleep(20)
    print('Process %s: %s' % (pid, (time.time() - s)))
    

def asynchronous():
    for i in range(1,5):
      for i in range(1,100):
          pool.spawn(crawl, i)
    pool.join()

def handlerequest(socket, address):
    socket.send("Hello from a telnet!\n")
    gevent.sleep(10);
    socket.close()

def handle(socket, address):
    pool.spawn(handlerequest, socket, address);

server = StreamServer(('127.0.0.1', 5000), handle)
server.serve_forever()
