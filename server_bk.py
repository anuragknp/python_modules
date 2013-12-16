#!/usr/bin/python
import gevent.monkey
gevent.monkey.patch_all()

from gevent.pool import Pool
from imapclient import IMAPClient
import array
import gevent
import urllib2
import time
import email
from email import parser
from sqlite.ttypes import *
from sqlite import ServiceSQLite
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport
from thrift.transport import TSocket
from cgi import parse_qs, escape
from gevent.pywsgi import WSGIServer

HOST = 'imap.gmail.com'
USERNAME = 'ashwintest94@gmail.com'
ssl = True
pool = Pool(10000)
server = IMAPClient(HOST, ssl=ssl)
server.login(USERNAME, 'qwerty16')
select_info = server.select_folder('[Gmail]/All Mail', readonly=True)

def fetchmailbody(mail_detail, result):
        result['error'] = 0
        result['data'] = {};
#        server.debug = 5;
        message = []
        message.append(mail_detail['uid'])
        body_section = 'BODY.PEEK[' + mail_detail['section_id'] + ']'
        body_field = 'BODY[' + mail_detail['section_id'] + ']'
        body_mime = 'BODY[' + mail_detail['section_id'] + '.MIME]'
        response = server.fetch(message, [str(body_section), 'RFC822.HEADER', str(body_mime)])
        result['data']['body'] = ""
        result['data']['is_html'] = 0
        for msgid, data in response.iteritems():
            print data
	    email_eml = str(data[str(body_mime)])  + str(data[str(body_field)])
	    print email_eml
	    mail = email.message_from_string(email_eml)		
	    for part in mail.walk():
		result['data']['body'] = "\n" + part.get_payload(decode=True) + "\n"
		if part.get_content_type() == 'text/html':
		    result['data']['is_html'] = int(1)
        	if part.get_content_type() == 'text/plain':
		    result['data']['is_html'] =	int(0)
	    parser = email.parser.HeaderParser()
            headers = parser.parsestr(str(data['RFC822.HEADER']))
            result['data']['from'] = headers['FROM']
            result['data']['to'] = headers['TO']
	    print type(result['data']['to'])
            result['data']['cc'] = headers['CC']
            result['data']['bcc'] = headers['BCC']
            result['data']['time'] = int(time.mktime(email.utils.parsedate(headers['DATE'])))
            result['data']['subject'] = headers['SUBJECT']

def fetchuidandsection(item_id,mail_detail):
    stmt = []
    s = Statement(query_="select uid,body_part from message_imap where id in (select id from map where item_id=?)", bind_text_={},bind_int64_={}, bind_result_={});
    s.bind_text_[1] = str(item_id[0])
    stmt.append(s);
    socket = TSocket.TSocket("127.0.0.1", 9601)
    transport = TTransport.TFramedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ServiceSQLite.Client(protocol)
    transport.open()
    res = client.ExecuteStatementArray(3,"message.cm", stmt, 1, False, 10,"test", 10);
    row = res.result_set_array_[0].row_
    if (len(row) == 1):
      mail_detail['uid'] = int(row[0].int64_value_['uid'])
      mail_detail['section_id'] = str(row[0].string_value_['body_part'])
    transport.close()

def getfolderlist(result):
    stmt = []
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

def sync(result, offset):
    print offset
    stmt = []
    result['error'] = 0
    result['data'] = {};
    s = Statement(query_="SELECT id,map.account_id,item_id,from_name,from_email,subject,message_thread.thread_id from map,message_thread where map.thread_id=message_thread.rowid limit ?, 10", bind_text_={}, bind_int64_={}, bind_result_={});
    s.bind_int64_[1] = offset;
    stmt.append(s);
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
        info['account_id'] = item.int64_value_['account_id'];
        info['item_id'] = item.string_value_['item_id']
        info['from_email'] = item.string_value_['from_email']
        info['subject'] = item.string_value_['subject']
        info['conversation_id'] = item.string_value_['thread_id']
        info['from_name'] = item.string_value_['from_name']
        result['data']['list'].append(info);
    transport.close()

def handle(env, start_response):
    result = {}
    params = ""
    try:
      length= int(env.get('CONTENT_LENGTH', '0'))
    except ValueError:
      length= 0
    if length!=0:
      body= env['wsgi.input'].read(length)
      params = parse_qs(body)
    if env['PATH_INFO'] == '/message/getfolderlist':
	start_response('200 OK', [('Content-Type', 'text/json')])
        getfolderlist(result)
        return [str(result)]
    if env['PATH_INFO'] == '/message/sync':
        start_response('200 OK', [('Content-Type', 'text/json')])
        sync(result,int(params.get(u'offset', u'0')[0]))
        return [str(result)]
    if env['PATH_INFO'] == '/message/get':
        item_id = params.get('item_id', "")
        maildetail = {}
        maildetail['uid'] = -1
        maildetail['section_id'] = ""
        fetchuidandsection(item_id,maildetail)
        fetchmailbody(maildetail,result)
        start_response('200 OK', [('Content-Type', 'text/json')])
	print type(result)
        return [str(result)]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print 'Serving on 6000...'
    WSGIServer(('', 6000), handle,spawn=pool).serve_forever()
