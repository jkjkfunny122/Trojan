import socket
import server
import tools
import header
import pickle
import struct
import control
import task
import time

class client:
    name = 'client'
    addr = None
    connect = None
    in_use = {}
    
    @classmethod
    def inuse(cls,queue: int,name_process:str | None=None):
        if name_process is None:
            name_process = ''

        cls.in_use[queue] = {'queue':queue,'name':name_process}
    
    @classmethod
    def unuse(cls,queue:int):
        if queue in cls.in_use:
            del cls.in_use[queue]
    
    @classmethod
    def entry(cls,cmmd:list):
        while True:
            if not cls.addr is None and isinstance(cls.addr,tuple):
                name_conn = cls.addr[0]
            else:
                name_conn = 'null'
            
            cmmd = input(f"@{control.control.hostname} > {name_conn}> ")
            
            if cmmd == 'select':
                cls.select()
            elif cmmd == 'disconnect':
                cls.dis_connect()
                break
            elif cmmd == 'destroy':
                cls.destroy_connect()
                break
            elif cmmd == 'version':
                cls.version()
            elif cmmd == 'exit':
                break
            else:
                print(f'unknow command.')
    
    @classmethod
    def select(cls):
        if not cls.connect == None:
            print("Failed: this object is already connected.")
            return False
        
        print("\n ------------- CONNECTION LIST -------------")
        for key, item in server.server.connections.items():
            print('=> ' + str(key))
        print(" ------------- END CONNECTION LIST -------------")
        selected = input('SELECT IP> ')
        
        if selected in server.server.connections:
            cls.connect = server.server.connections[selected]["conn"]
            cls.addr = server.server.connections[selected]["addr"]
            if isinstance(cls.connect,socket.socket):
                print("Client: connected.")
                return True
            else:
                print("Failed: connect failed.")
                
        else:
            print("Failed: not found that ip in list.")
        
        return False
    
    @classmethod
    def destroy_using_tasks(cls):
        remove_key = []
        for key,item in cls.in_use.items():
            remove_key.append(key)
            print(f'Remove process: {item['name']}')
        
        for i in remove_key:
            task.task.delete_task(i)
        
        print(f'Removed {len(remove_key)} process')
    
    @classmethod
    def destroy_connect(cls):
        cls.destroy_using_tasks()
        cls.check_server()
        
        if isinstance(cls.connect,socket.socket):
            print("Client: disconnected.")
            server.server.destroy_connection(cls.addr[0])
            cls.connect = None
            cls.addr = None
            return True
        else:
            if cls.connect == None:
                print("Failed: it's not connect yet.")
            else:
                print("Failed: Can't disconnect object isn't socket")
            
            return False
        
    @classmethod
    def dis_connect(cls):
        cls.check_server()
        
        if len(cls.in_use) > 0:
            print("Connect is using please close the process.")
            return 0
        
        if isinstance(cls.connect,socket.socket):
            print("Client: disconnected.")
            cls.connect = None
            cls.addr = None
            return True
        else:
            if cls.connect == None:
                print("Failed: it's not connect yet.")
            else:
                print("Failed: Can't disconnect object isn't socket")
            
            return False
    
    @classmethod
    def check_server(cls):
        if isinstance(cls.addr,tuple):
            if len(cls.addr) == 2:
                if cls.addr[0] in server.server.connections:
                    if isinstance(cls.connect,socket.socket):
                        try:
                            cls.connect.sendall(b'')
                            return True
                        except Exception as e:
                            print("Failed: Socket closed")
                            server.server.destroy_connection(cls.addr[0])
        
        print(f'Stopping relative process.')
        cls.destroy_using_tasks()
        time.sleep(3)
        cls.addr = None
        cls.connect = None
        return False 
    
    @classmethod
    def version(cls):
        if not cls.check_server():
            print("test_send: Socket is closed.")
            return 0
        
        if not isinstance(cls.connect,socket.socket):
            print("test_send: Error data type.")
            return 0
        
        header_object = header.header()
        header_object.insert_key('cmmd','info_script')
        header_object.insert_key('arg','version')
        
        header_pack = pickle.dumps(header_object.get_header())
        size = len(header_pack)
        size = struct.pack('>I',size)
        cls.connect.sendall(size)
        cls.connect.sendall(header_pack)
        
        size_data = cls.connect.recv(4)
        if len(size_data) == 4:
            size = struct.unpack('>I',size_data)[0]
            data = tools.tools.collect_data(cls.connect,size)
            data_unpack = pickle.loads(data)
            
            print(f"Client version: {data_unpack['data']['version']}")
    
    @classmethod
    def socket_send(cls,bytes):
        if not cls.check_server():
            return False
        
        if isinstance(cls.connect,socket.socket):
            try:
                cls.connect.sendall(bytes)
                return True
            except Exception as e:
                print(f'Error: {str(e)}')
                return False
    
    @classmethod
    def socket_recv(cls,recv_size: int):
        if not cls.check_server():
            return False
        
        if isinstance(cls.connect,socket.socket):
            try:
                data = cls.connect.recv(recv_size)
                return data
            except Exception as e:
                print(f'Error: {str(e)}')
                return False