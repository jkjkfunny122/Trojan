import os
import socket
class tools:
    port = 9999
    boardcast_code = 'VERIFY:CTL'
    version = 'Client 84205-indev'
    exit_byte = b'C00E'
    
    def get_args(text:str):
        arg = text.split(" ")
        return arg
    
    def pause():
        os.system("pause")
        
    def collect_data(conn:socket.socket,size: int):
        data = b''
        while size > 0:
            recv_size = 0
            if size >= 1024:
                recv_size = 1024
            elif size < 1024:
                recv_size = size
            
            data_recv = conn.recv(recv_size)
            if len(data_recv) == recv_size:
                data += data_recv
                size -= recv_size
            else:
                return False
                
        return data