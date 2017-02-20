from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import StreamRequestHandler
import io,shutil  
import urllib,time
import getopt,string
import sql
import logging

LOG_FILE = '/home/mini/tempmessage/log.out'
class MyRequestHandler(BaseHTTPRequestHandler):
    assess = set()
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=LOG_FILE,
                filemode='w')
    def do_GET(self):
        self.process(2)

    def do_POST(self):
        self.process(1)
        
    def process(self,type):
        
        content =""
        if type==1:
            print 'read\n'
            datas = self.rfile.read(int(self.headers['content-length']))
            
            datas = urllib.unquote(datas).decode("utf-8", 'ignore')
            datas = transDicts(datas)#
            address = self.client_address[0]
            if datas.has_key('buffer'):
                logging.debug("ip_src: %s,canplay: %s , buffer :%s\n" %(address , datas['buffer'] , datas['buffer']))
            self.send_response(200)  
        if type==2:
            query = urllib.splitquery(self.path)
            if query[1]:
                params={}
                for pr in query[1].split('&'):
                    [name,param]=pr.split('=')
                    params[name]=param
                print params['buffer']
            address = self.client_address[0]
            if params['buffer']:
                
                logging.debug("ip_src: %s , canplay %s ,  buffer :%s\n" %(address , params['canplay'] , params['buffer'])) 
                if float(params['canplay']) < 20 and float(params['buffer']) < 1:
                    #alert
                    if address in  self.assess:
                    	pass
                    else :
                        _sql = '''INSERT INTO flow (ip_src , buffer , time) values (?, ? ,?)'''
                        data = [(address,params['buffer'] , 1)]
                        sql.save(self.conn, _sql, data)
                        self.assess.add(address)
            self.send_response(200)    

def transDicts(params):
    dicts={}
    if len(params)==0:
        return
    params = params.split('&')
    for param in params:
        dicts[param.split('=')[0]]=param.split('=')[1]
    return dicts