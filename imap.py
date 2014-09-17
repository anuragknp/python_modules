#!/usr/bin/python
from __future__ import unicode_literals
import gevent.monkey
gevent.monkey.patch_all()

from imapclient import IMAPClient
import array
import gevent
import urllib2
import time
import email

HOST = 'imap-mail.outlook.com'
USERNAME = 'XXXX@ssss.com'
ssl = True

def crawl(pid):
    response = urllib2.urlopen('http://127.0.0.1').read()
    s = time.time()
    gevent.sleep(20)
    print('Process %s: %s' % (pid, time.time() - s))


def printmail(mail):
    body = ""
    plaintextbody = ""
    for part in mail.walk():
#       print part.get_payload(decode=True)
        print part.get_content_type()
        if part.is_multipart():
            continue
        if part.get_content_type() == 'text/html':
            body = "\n" + part.get_payload(decode=True) + "\n"
        if part.get_content_type() == 'text/plain':
            plaintextbody = "\n" + part.get_payload(decode=True) + "\n"    
    print body
    print "plain text"
    print plaintextbody
    print

def fetchmail(pid):
	server = IMAPClient(HOST, use_uid=True, ssl=ssl)
#        server.debug = 5;
	server.login(USERNAME, 'xxxx')
	select_info = server.select_folder('INBOX', readonly=True)
	print('%d messages in INBOX' % select_info['EXISTS'])
	messages = server.search(['SUBJECT aaaa'])
	print("%d messages that aren't deleted" % len(messages))
	print()
	print("Messages:")
        print messages
        response = server.fetch(messages, ['BODY.PEEK[1]', 'RFC822.HEADER'])
	for msgid, data in response.iteritems():
#            print data;
	    print data['BODY[1]']
            print data['RFC822.HEADER']
            #msg = email.message_from_string(msg_string)
            #printmail(msg);
            break;
        print "Done"
    

def init():
    threads = []
    for i in range(1,2):
        threads.append(gevent.spawn(fetchmail, i))
    gevent.joinall(threads)

init()

