import socket
import time
import os
import phase
import threading

# addr_ctl = ""
port_ctl = 9166

def PrepareCtl():
    global port_ctl
    result = []
    
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind(('0.0.0.0',port_ctl))
        sock.listen(1)
        
        print("waiting for ctl..")
        conn, addr = sock.accept()
        
        data = conn.recv(1024)
        header = phase.PhaseHeaderText(data.decode())
        
        if not header == []:
            
            if phase.GetSubject(header,"VERIFY") == "CTL":
                result = header 
        else:
            print("Error package!")
                        
    except Exception as e:
        print("unexcept error: " + str(e))
    finally:
        conn.close()
        sock.close()
    
    return result

def main():
    x = 1
    return 0