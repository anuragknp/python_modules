#!/usr/bin/python
import gevent.monkey
gevent.monkey.patch_socket()
from sqlite.ttypes import *
from sqlite import ServiceSQLite
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport
from thrift.transport import TSocket
from gevent.pool import Pool
import gevent
import urllib2
import time
pool = Pool(10000)

def crawl(pid):
    print('started %s' % (pid))
    stmt = []
    result = {};
    result['error'] = 0
    result['data'] = {};
    stmt.append(Statement(query_="SELECT * from message_folder order by account_id", bind_text_={}, bind_int64_={}, bind_result_={}));
    socket = TSocket.TSocket("127.0.0.1", 9601)
    transport = TTransport.TFramedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ServiceSQLite.Client(protocol)
    transport.open()
    res = client.ExecuteStatementArray(3,"message.cm", stmt, 1, False, 10,"test", 10);
    rows = res.result_set_array_[0].row_
    result['data']['list'] = []
    for index in range(0, len(rows)):
	item = rows[index];
        info = {}
        info['id'] = item.int64_value_['id'];
        info['folder_name'] = item.string_value_['name']
        info['folder_canonical_name'] = item.string_value_['canonical_name']
        result['data']['list'].append(info);
    transport.close()
    print result
    print "done"

def asynchronous():
   for i in range(1,2):
     pool.spawn(crawl, i)
   pool.join()

asynchronous();
