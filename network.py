import socket
import task
import tools
import struct
import pickle
import header
import threading

class network:
    broadcast_task = None
    connect_task = None
    
    target_ip = ''
    
    @classmethod
    def start(cls):
        if not cls.broadcast_task is None:
            print("Failed: Broadcast task is running.")
            return False
        
        cls.broadcast_task = task.task(cls.broadcast,())
        # cls.broadcast_task.task.daemon = False
        cls.broadcast_task.task.start()
        print("Network: start wait for server.")
        
    @classmethod
    def broadcast(cls):
        if not isinstance(cls.broadcast_task,task.task):
            return 0
        
        queue = cls.broadcast_task.queue
        
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock.bind(('0.0.0.0',tools.tools.port))
            size = len(tools.tools.boardcast_code.encode())
            
            while True:
                data , addr = sock.recvfrom(size)
                if len(data) == size:
                    if data.decode() == tools.tools.boardcast_code:
                        print("Connect from: " + addr[0])
                        cls.target_ip = addr[0]
                        cls.connect_task = task.task(cls.connect_tcp,())
                        # cls.connect_task.task.daemon = False
                        cls.connect_task.task.start()
                        break
        
        task.task.delete_task(queue)
        cls.broadcast_task = None
    
    lpacket_id = 0
    recv_data = {} #search your recv here
    # send_data = False #if want to send data change it to True and network will ignore bind function
    connect = None #connect take it and use it for send data to des

    @classmethod
    def socket_send(cls,bytes):
        if isinstance(cls.connect,socket.socket):
            try:
                cls.connect.sendall(bytes)
                return True
            except Exception as e:
                return False
        else:
            return False
    
    connect_lock = threading.Lock()
    recv_lock = threading.Lock()
        
    @classmethod
    def connect_tcp(cls):
        queue = cls.connect_task.queue
        ip = cls.target_ip
        
        #dev hook bypass loopback
        if ip == '192.168.56.1':
            ip = '192.168.1.22'
            
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            try:
                with cls.connect_lock:
                    cls.connect = sock
                
                sock.settimeout(10)
                sock.connect((ip,tools.tools.port))
                print("Connect: connected.")
                header_data = header.header()
                header_data.insert_key('version',tools.tools.version)
                
                data = pickle.dumps(header_data.get_header())
                size_wel = struct.pack(">I",len(data))
                sock.sendall(size_wel)
                sock.sendall(data)
                
                while True:
                    try:
                        data_size = sock.recv(4)
                    except socket.timeout:
                        try:
                            sock.sendall(b'')
                        except socket.timeout:
                            print(f'Error: timeout.')
                            continue 
                        except Exception as e:
                            break
                        
                        continue
                    except Exception:
                        sock.close()
                        break
                        
                    if data_size == b'C00E':
                        sock.close()
                        print("\nClose connect.")
                        break
                    
                    if len(data_size) == 4:
                        size = struct.unpack(">I",data_size)[0]
                        data = tools.tools.collect_data(sock,size)
                        if len(data) == 0:
                            continue
                        packet = pickle.loads(data)
                        
                        if header.header.check_header(packet):
                            print(f"From {ip} \n Packet : {packet}")
                            with cls.recv_lock:
                                cls.recv_data[cls.get_packet_id()] = packet
                
            except Exception as e:
                print("Failed: can't connect")
                cls.target_ip = ''
        
        with cls.connect_lock:
            cls.connect = None
        
        task.task.delete_task(queue)
        cls.connect_task = None
        cls.start()
    
    @classmethod
    def get_packet_id(cls):
        id = cls.lpacket_id
        cls.lpacket_id += 1
        return id
    
    @classmethod
    def get_all_packets(cls):
        return cls.recv_data.copy()
    
    @classmethod
    def remove_packets(cls,key: list):
        with cls.recv_lock:
            for i in key:
                if i in cls.recv_data:
                    del cls.recv_data[i]