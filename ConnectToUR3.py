class ConnectToUR3:
    def __init__(self,TYPE = 'Client',HOST = "192.168.1.2", PORT = 30003):
        import socket
        if TYPE == 'Client':
            # Create & Connect as client to HOST with given IP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            print 'Connect to UR with LAN'
            print 'HOST: ' + HOST
            print 'PORT: ' + str(PORT)
        else:
            # Bind and Waiting for client connection
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((HOST, PORT))     
            self.s.listen(1)          
            self.sock, self.addr = self.s.accept()   

    def get_socket(self):
        # Returns socket
        return self.sock
        
    def close(self):
        # Closes socket
        import socket
        self.sock.close()
        
    def send(self, data):
        self.sock.send(data)
    
    def send_movej(self, data, a = 1, v = 1.5):
        import time
        tmp = "movej(" + str(data) + ", a = " + str(a) + ", v = " + str(v) +")" + "\n"
        print(tmp)
        print(time.time())
        self.sock.send(tmp.encode())
        
    def send_speedj(self, data, a = 1, t = 100):
        import time        
        tmp = "speedj(" + str(data) + ", a = " + str(a) + ", t_min = " + str(t) + ")" + "\n"
        print(tmp)
        print(time.time())
        self.sock.send(tmp.encode())
        
    def send_movel(self, data,a,v):
        import time        
        tmp = "movel(" + str(data) + ", a = " + str(a) + ", v = " + str(v) +")" + "\n"
        print(tmp)
        print(time.time())
        self.sock.send(tmp.encode())
 
