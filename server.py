#-*- coding:utf-8 -*-
#__author__:zhouy83
import SocketServer
import cnocr
import sys,json
reload(sys)
sys.setdefaultencoding('utf-8')
class Myserver(SocketServer.BaseRequestHandler):
    def handle(self):
        print('服务端启动')
        while True:
            conn=self.request
            print(self.client_address)
            while True:
                # try:
                #     data=conn.recv(1024)
                # except Exception:
                #     break
                data = conn.recv(1024)
                if data=='exit': break
                data=str(data)
                # data.encode('utf-8')
                print(data)
                print('waiting....')
                if len(data)>=1:
                    image_file=data.split('#')[-2]
                    type=data.split('#')[-1]
                    print(image_file)
                    print(type)
                    result_data=cnocr.run(image_file,type)
                    result_data=json.dumps(result_data,ensure_ascii=False)
                    conn.sendall(bytes(result_data))

            conn.close()

if __name__=='__main__':
    sever=SocketServer.ThreadingTCPServer(('127.0.0.1',8091),Myserver)
    sever.serve_forever()