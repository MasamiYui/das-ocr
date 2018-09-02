#-*- coding:utf-8 -*-
#__author__:zhouy83
#date:2018/8/27
import socket

sk=socket.socket()
address=('127.0.0.1',8000)
sk.connect(address)
while True:
    question=raw_input(">>>").strip()
    if question=="exit":
        break
    sk.send(bytes(question))
    data=sk.recv(1024)
    print(str(data))
sk.close()
