import socket 
import main
import threading 
from queue import Queue


q = Queue()
output_q = Queue()
serverPort = 6699
bind_ip = "127.0.0.1" 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, serverPort))
server.listen(5)
 
 
def get_headers(line_list):
    headers = {}
    for line in line_list:
        new_line = line.decode('utf8')
        index = new_line.find(':')
        key = new_line[:index]
        value = new_line[index+1:].strip()
        headers[key] = value
    return headers

def server_thread(read_q,output_q):
    print('The server start to work!!')
    while True:
        client, addr = server.accept()
        print ("Accepted connection from: %s:%d" % (addr[0], addr[1]))
        try:
            sentence = client.recv(2048)
            line_list = sentence.split(b'\r\n')
            headers = get_headers(line_list)
            for i in line_list:
                print(i)
            input_sentence_byte=line_list[-3]
            input_sentence=str(input_sentence_byte,encoding='utf8')
            lenth = len(input_sentence)
            if len(input_sentence) != 0:      
                 read_q.put(input_sentence)        
                 outputdata = output_q.get()
            else:
                 outputdata = 'You do not input any sentence'
            print(outputdata)
            outputdata = produce_body(outputdata,lenth)
            header = ' HTTP/1.1 200 OK\r\n' \
                     'Connection: close\r\n' \
                     'Content-Type: ' + '*/*' + '\r\n' \
                                                 'Content-Length: %d\r\n\r\n' % (len(outputdata)) 
            client.send(header.encode()+outputdata.encode())
            client.close()
        except IOError:
            header = ' HTTP/1.1 404 Not Found'
            client.send(header.encode())    

def produce_body(outputdata,lenth) ->str:
    import random
    import os

    BOUNDARY = '----------------%s'%''.join(random.sample('0123456789abcdef',15))
    CRLF = '\r\n'
    L = []
    if lenth==0:     
        L.append('---'+BOUNDARY)
        L.append('Content-Disposition: form-data;name=sentence')
        L.append('')
        L.append(outputdata)
    else:
        out_dict = eval(outputdata)
        for key in out_dict:
            L.append('---'+ BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(str(out_dict[key]))
    L.append('--'+BOUNDARY+'--')
    L.append('')
    body = CRLF.join(L)
    content_type  = 'multipart/form-data; boundary = %s' % BOUNDARY
    return body



t1 = threading.Thread(target=main.evaluate_line_thread,args=(q,output_q,))
t2 = threading.Thread(target=server_thread,args=(q,output_q,))
t2.start()
t1.start()




