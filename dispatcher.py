#!/usr/bin/env python
"""Simple server that listens on port 6000 and echos back every input to the client.

Connect to it with:
  telnet localhost 6000

Terminate the connection by terminating telnet (typically Ctrl-] and then 'quit').
"""
from gevent.server import StreamServer
from gevent.socket import *
import xml.etree.cElementTree as ET

def InitConfig(file_name):
  tree = ET.ElementTree(file=file_name)
  root = tree.getroot()
  ip = root.find('server').attrib['ip']
  port = root.find('server').attrib['port']
  servers = {}
  conns = []
  targets = root.find('targets')
  for target in targets:
    servers[target.attrib['name']] = (target.attrib['ip'], target.attrib['port'])
    sock = socket(AF_INET,SOCK_STREAM)
    try:
      sock.connect((target.attrib['ip'], int(target.attrib['port'])))
    except error as e:
      if e.errno != 111:
        raise e
      print 'Can not connect to %s' % target.attrib['ip']
    else:
      conns.append(sock)

  return ip, port, servers, conns

IP, Port, Targets, Conns = InitConfig("config.xml")
Port = int(Port)

def handle(sock, address):
  global Conns
  while True:
    line = sock.recv(65535)
    if not line:
      print("client disconnected")
      break
    if line.strip().lower() == 'quit':
      print("client quit")
      break
    for conn in Conns:
      conn.sendall(line)
  sock.close()


if __name__ == '__main__':
    # to make the server use SSL, pass certfile and keyfile arguments to the constructor
    server = StreamServer((IP, Port), handle)
    # to start the server asynchronously, use its start() method;
    # we use blocking serve_forever() here because we have no other jobs
    if Conns:
      print('Starting dispatcher server on port %s' % Port)
      server.serve_forever()
