#!/usr/bin/python
from gevent.server import StreamServer
import gevent.monkey
gevent.monkey.patch_socket()

# this handler will be run for each incoming connection in a dedicated greenlet
def echo(socket, address):
    str = socket.recv(1024)
    print ('New connection from %s:%s' % address)
    gevent.sleep(1);
    print ('Data %s' % str)
    socket.sendall('Welcome to the echo server! Type quit to exit.\r\n')
    


if __name__ == '__main__':
    # to make the server use SSL, pass certfile and keyfile arguments to the constructor
    server = StreamServer(('0.0.0.0', 6000), echo,spawn=1,backlog=1000)
    # to start the server asynchronously, use its start() method;
    # we use blocking serve_forever() here because we have no other jobs
    print ('Starting echo server on port 6000')
    server.serve_forever()
