import task
import tools
import socket
import time
import threading
import struct
import header
import pickle
import clientc
import control

class server:
    connections = {}
    port = 9999
    bind_task = None
    broadcast_task = None
    cc_task = None
    ip_broadcast = '192.168.1.255'
    
    lock = threading.Lock()
    
    @classmethod
    def entry(cls,cmmd):
        while True:
            cm = input(f'@{control.control.hostname} > server > ')
            if cm == 'start':
                cls.start()
            elif cm == 'stop':
                cls.stop()
            elif cm == 'boardcast':
                print(f'BROADCAST IP LIST \n(1) 255.255.255.255 for global\n(2) <broadcast> for global\n(3) 192.168.x.255 for subnet')
                cls.ip_broadcast = str(input(f'@{control.control.hostname} > server > broadcast >'))
                print(f'Change broadcast ip to {cls.ip_broadcast}')
            elif cm == 'exit':
                break
            else:
                print(f'Unknow command "{cm}".')
                
    
    @classmethod
    def start(cls):
        if cls.broadcast_task is None:
            cls.broadcast_task = task.task(cls.broadcast,(),'broadcast')
            if isinstance(cls.broadcast_task.task,threading.Thread):
                # cls.broadcast_task.task.daemon = False
                cls.broadcast_task.task.start() 
                print("SUCCESSFULLY: create broadcast process.")
            else:
                print("Failed: to create broadcast task.")
        else:
            print("FAILED: create broadcast process.")
            
        if cls.bind_task is None:
            cls.bind_task = task.task(cls.bind,(),'bind')
            if isinstance(cls.bind_task.task,threading.Thread): 
                # cls.bind_task.task.daemon = False
                cls.bind_task.task.start()
                print("SUCCESSFULLY: create bind process.")
            else:
                print("Failed: to create bind task.")
        else:
            print("FAILED: create bind process.")
        
        if cls.cc_task is None:
            cls.cc_task = task.task(cls.connections_checker,(),'connections_checker')
            if isinstance(cls.cc_task.task,threading.Thread):
                # cls.cc_task.task.daemon = False 
                cls.cc_task.task.start()
                print("SUCCESSFULLY: create connections_checker process.")
            else:
                print("Failed: to create connections_checker task.")
        else:
            print("FAILED: create connections_checker process.")
        
    @classmethod
    def stop(cls):
        if not cls.bind_task is None and not cls.broadcast_task is None and not cls.cc_task is None:
            if task.task.delete_task(cls.broadcast_task.queue):
                print("Server: success delete broadcast task.")
            else:
                print("FAILED: Failed to closed broadcast process.")
                
            time.sleep(5)
            
            cls.destroy_all_connection()
            
            if task.task.delete_task(cls.bind_task.queue):
                print("Server: success delete bind task.")
            else:
                print("FAILED: Failed to closed bind process.")
    
            if task.task.delete_task(cls.cc_task.queue):
                print("Server: success delete connections_checker task.")
            else:
                print("FAILED: Failed to closed connections_checker process.")

            cls.bind_task = None
            cls.broadcast_task = None
            cls.cc_task = None
        else:
            print("FAILED: task is not running")
    
    @classmethod
    def bind(cls):
        queue = cls.bind_task.queue
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock.bind(('0.0.0.0',cls.port))
            sock.listen(1)
            
            try:
                while True:
                    if task.task.find_task(queue) == -1:
                        break
                    
                    conn, addr = sock.accept()
                    if not addr[0] in cls.connections:
                        tools.tools.show_popup(f"Connect by: {addr[0]}")
                        conn.settimeout(10)
                        
                        try:
                            size_data = conn.recv(4)
                            if len(size_data) == 4:
                                size_unpack = struct.unpack(">I",size_data)[0]
                                raw_data = tools.tools.collect_data(conn,size_unpack)
                                header_data = pickle.loads(raw_data)
                                
                                # print(f'Size: {size_unpack}')
                                # print(f'Recv_size: {len(raw_data)}')
                                # print("Data: " + str(header_data))
                                
                                if header.header.check_header(header_data):
                                    # conn.sendall(tools.tools.boardcast_code.encode())
                                    cls.connections[addr[0]] = {"conn":conn,"addr":addr}
                                else:
                                    conn.sendall(tools.tools.exit_byte)
                                    conn.close()
                                    
                        except Exception as e:
                            conn.close()
                            print('In side Error: ' + str(e))
                    elif addr[0] in cls.connections:
                        conn.sendall(tools.tools.exit_byte)
                        conn.close()
                        
                                
                        
            except Exception as e:
                print('Error out side: ' + str(e))
                
        task.task.delete_task(queue)
        # cls.bind_task = None
            
    @classmethod
    def broadcast(cls):
        cooldown = 3 #delay for second
        queue = cls.broadcast_task.queue
        
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
            
            while True:
                if task.task.find_task(queue) == -1:
                    break
                time.sleep(cooldown)
                sock.sendto(tools.tools.boardcast_code.encode(),(cls.ip_broadcast,cls.port))
        
        task.task.delete_task(queue)
        # cls.broadcast_task = None
    
    @classmethod
    def connections_checker(cls):
        queue = cls.cc_task.queue
        while True:
            if task.task.find_task(queue) == -1:
                break
            time.sleep(10)
            with cls.lock:
                for key, value in list(cls.connections.items()):
                    if task.task.find_task(queue) == -1:
                        break
                    if isinstance(value["conn"],socket.socket):
                        conn = value["conn"]
                        conn.settimeout(1)
                        try:
                            conn.sendall(b'')
                            conn.settimeout(10)
                        except socket.error:
                            if clientc.client.addr == key:
                                clientc.client.check_server()
                            del cls.connections[key]
                            print(f'{key} Disconnected.')
                    else:
                        if clientc.client.addr == key:
                            clientc.client.check_server()
                        del cls.connections[key]
                        print(f'{key} Disconnected.')
        
        task.task.delete_task(queue)
        # cls.cc_task = None
    
    @classmethod
    def destroy_connection(cls,connect_key):
        if connect_key in cls.connections:
            if 'conn' in cls.connections[connect_key]:
                if isinstance(cls.connections[connect_key]['conn'],socket.socket):
                    try:
                        cls.connections[connect_key]['conn'].sendall(tools.tools.exit_byte)
                    except Exception as e:
                        print(f"Error: {str(e)}")
                    finally:
                        cls.connections[connect_key]['conn'].close()
                        del cls.connections[connect_key]
                    return True
        
        return False

    @classmethod
    def destroy_all_connection(cls):
        remove_key = []
        for key,item in cls.connections.items():
            remove_key.append(key)
            
        for i in remove_key:
            cls.destroy_connection(i)
            
        return len(remove_key)