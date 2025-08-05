import os
import socket
import threading
from tkinter import Tk, messagebox

class tools:
    port = 9999
    boardcast_code = 'VERIFY:CTL'
    version = 'Server 842025-indev'
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
                return b''
                
        return data
    
    def show_popup(msg):
        def popup():
            root = Tk()
            root.withdraw()
            messagebox.showinfo("แจ้งเตือน", msg)
            root.destroy()
        t = threading.Thread(target=popup)
        t.daemon = True
        t.start()