#!/usr/bin/python
import gevent.monkey
gevent.monkey.patch_socket()

from gevent.pool import Pool
import array
import gevent
import urllib2
import time
from cgi import parse_qs, escape
from gevent.pywsgi import WSGIServer
pool = Pool(10000)

def handle(env, start_response):
    if env['PATH_INFO'] == '/':
        try:
          length= int(env.get('CONTENT_LENGTH', '0'))
        except ValueError:
          length= 0
        if length!=0:
          body= env['wsgi.input'].read(length)
        print body
        d = parse_qs(body)
        request_json = str(d.get('item_id', {}))
        print request_json
        start_response('200 OK', [('Content-Type', 'text/json')])
        return [request_json]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print 'Serving on 6000...'
    WSGIServer(('', 6000), handle,spawn=pool).serve_forever()
