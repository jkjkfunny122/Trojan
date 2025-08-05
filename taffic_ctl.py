import socket
import os
import time

import phase

addr_client = []
port_ctl = 9166
ctl_code = "VERIFY: CTL"
client_code = "VERIFY: CLIENT"
        

def ScanClient(start: int ,end: int,start_address: list):
    global addr_client,port_ctl,ctl_code,client_code
    client_ip = []
    timeout = 1 #second
    time_start = time.time()
    
    if start > 255 or start < 1 or start > end or end > 255 or end < 1:
        return False
    
    for i in range(start,end+1):
        os.system("cls")
        print("Will finish in " + str((timeout*(end-start)) - int(time.time() - time_start)) + " seconds")
        
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.settimeout(timeout)
    
        address = ""
        for x in start_address:
            address = address + x + "."
        address = address + str(i)
        
        try:
            print("\ntry to connect (addr): " + address)
            sock.connect((address,port_ctl))
            sock.sendall(ctl_code.encode())
        except Exception as e:
            print("failed to connect")
            
            sock.close()
            continue
        
        try:
            sock_send = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock_send.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock_send.settimeout(timeout)
            sock_send.bind((address,port_ctl))
            sock_send.listen(1)
            
            conn, addr = sock_send.accept()
            data = conn.recv(len(client_code.encode()))
            if data.decode().find(client_code) >= 0:
                print("(FOUND) ADDR => " + addr[0])
                client_ip.append(addr[0])
        except Exception as e:
            print("failed to get recvice code from target. ERROR: " + str(e))
            
        finally:
            conn.close()
            sock_send.close()
        
    for x in client_ip:
        err = 0
        
        for i in addr_client:
            if i == x:
                err+=1
                break
        
        if err == 0:
            addr_client.append(x)
    
    return client_ip

arr = [["VERIFY","CTL"],["COMMAND","status"]]
print("ARRAY TO TEST")
print(arr)

header_text = phase.MakeHeaderText(arr)
print("\n To Text => \n" + header_text)
print("\n To Array => ")
print(phase.PhaseHeaderText(header_text))

print("CHECK")
print(arr == phase.PhaseHeaderText(header_text))