import worker_ctl as Worker
import socket
import os
import threading
import phase
import cv2
import numpy as np
import time
import struct

class ClientM:
    clients = []
    last_id = 0

    @classmethod
    def update(cls,client_ip:str,data:list):
        client_id = cls.last_id
        cls.last_id += 1
        
        cls.clients.append([client_id,client_ip,data])
        return client_id

    @classmethod
    def search(cls,client_id):
        for i in cls.clients:
            if i[0] == client_id:
                return i
        
        return []
    
    @classmethod
    def edit(cls,client_id:int,client_ip:str,data:list):
        client = cls.search(client_id)
        if len(client) > 0:
            cls.clients.remove(client)
            
            cls.clients.append(client_id,client_ip,data)
            
            print("\nEdit client result")
            for i in client:
                print(i)
    
    @classmethod
    def delete(cls,client_id:int):
        for i in reversed(range(len(cls.clients))):
            if cls.clients[i][0] == client_id:
                return cls.clients.pop(i)
class Cmd:
    client_addr = []
    host = str(socket.gethostname())
    port = 9166
    
    @classmethod
    def SendHeader(cls,header:str,target_addr:str,for_wait:bool):
    
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock.connect((target_addr,cls.port))
            sock.sendall(header.encode())
        
    @classmethod
    def prepare_input(cls):
        return "\n"+cls.host+" > "
    
    def findCommand(cmd:str,text:str):
        if cmd.find(text,0,len(text)) == 0:
            return True
        else:
            return False
        
    def getArgs(cmd:str):
        cmd_list = cmd.split(" ")
        del cmd_list[0]
        return cmd_list
    
    def unpack_image(conn: socket.socket,size: int):
        buffer = b""
        while size >= 1:
            recv_size = 1024
            if (size - recv_size) <= 1024:
                recv_size = size
            
            if recv_size <= 0:
                break
            
            data = conn.recv(recv_size)
            buffer += data
            size -= len(data)
        return buffer

    # ================================ COMMAND PROGRESS ============================
    
    @classmethod
    def scanWork(cls,start:int,end:int,start_address:list,quece:int):    
        try:
            Worker.Worker.update_quece("scanWork",quece)
            client_ip = []
            timeout = 1 #second
            time_start = time.time()
            # print("Will finish in " + str((timeout*(end-start)) - int(time.time() - time_start)) + " seconds")
    
            for i in range(start,end+1):
                if Worker.Worker.search_quece(quece) == []:
                    break
                
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                sock.settimeout(timeout)
    
                address = ""
                for x in start_address:
                    address = address + x + "."
                    
                address = address + str(i)
        
                try:
                    # print("\ntry to connect (addr): " + address)
                    sock.connect((address,cls.port))
                    ctl_code = phase.MakeHeaderText([["VERIFY","CTL"],["COMMAND","reply"]])
                    sock.sendall(ctl_code.encode())
                except Exception as e:
                    # print("failed to connect")
                    if address in cls.client_addr:
                        cls.client_addr.remove(address)
                    sock.close()
                    continue
                
                # conn = None
                try:
                    sock_send = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sock_send.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                    # sock_send.settimeout(timeout)
                    sock_send.bind(('0.0.0.0',cls.port))
                    sock_send.listen(1)
            
                    conn, addr = sock_send.accept()
                    data = conn.recv(1024)
                    list_data = phase.PhaseHeaderText(data.decode())
                    if phase.GetSubject(list_data,"VERIFY") == "CLIENT":
                        # print("(FOUND) REPLY")
                        # print("RELASE VERSION -> " + phase.GetSubject(list_data,"RELASE"))
                        
                        client_ip.append(addr[0])
                        if not addr[0] in cls.client_addr:
                            cls.client_addr.append(addr[0])
                except Exception as e:
                    # print("ERROR: " + str(e) + "\nAt line: " + str(e.__traceback__))
                    Worker.Worker.throw_err(str(e),"Scan")
                finally:
                    conn.close()
                    sock_send.close()
            
            print("\nSCAN RESULT: ")
            for i in cls.client_addr:
                print("ADDRESS => ", i)
        except Exception as e:
            # print("Error: " + str(e))
            Worker.Worker.throw_err(str(e),"Scan")
        
        Worker.Worker.delete_quece(quece)
    
    scan_quece = 0
    
    @classmethod
    def scan(cls,start:int,end:int,ip:str):
        try:
            
            search = Worker.Worker.search_quece(cls.scan_quece)
            if "scanWork" in search:
                prefer = input("You old scan is still progress do you want to cancel it? [Y=YES,N=NO] = ")
                if prefer == "Y" or prefer == "y":
                    Worker.Worker.delete_quece(cls.scan_quece)
                else:
                    return 0
            
            start_address = ip.split(".")
            if "x" in start_address:
                start_address.remove("x")
    
            if start > 255 or start < 1 or start > end or end > 255 or end < 1:
                return False
            
            cls.scan_quece = Worker.Worker.get_quece()
            new_thread = threading.Thread(target=Cmd.scanWork,args=(start,end,start_address,cls.scan_quece))
            new_thread.start()
        except Exception as e:
            Worker.Worker.throw_err("Error: " + str(e),"scan")
        
    def shutdown(cmd: str):
        try:
            args = Cmd.getArgs(cmd)
            client_addr = args[0]
            header_text = phase.MakeHeaderText([["VERIFY","CTL"],["COMMAND","shutdown"]])
            Cmd.SendHeader(header_text,client_addr,False)
        except Exception as e:
            print("Error: "+ str(e))

    @classmethod
    def cameraWorker(cls,arg_addr: str,quece: int):
        # time.sleep(60)
        try:
            Worker.Worker.update_quece("camera",quece)
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                sock.connect((arg_addr,cls.port))
                header = [['VERIFY','CTL'],['COMMAND','streamcam']]
                header_text = phase.MakeHeaderText(header)
                sock.sendall(header_text.encode())
            
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                sock.settimeout(30)
                sock.bind(('0.0.0.0',cls.port))
                sock.listen(1)
                
                err = 0
                
                while True:
                    if not err == 0:
                        break
                    
                    worker_status = Worker.Worker.search_quece(quece)
                    if len(worker_status) == 0:
                        break
                    
                    conn, addr = sock.accept()
                    
                    # if not addr[0] == cls.client_addr:
                    #     conn.close()
                    #     if input("want to end thread [Y = YES,N = NO]: ") == "Y":
                    #         break
                    #     continue
                    
                    try:
                        while True:
                            worker_status = Worker.Worker.search_quece(quece)
                            if len(worker_status) == 0:
                                break
                            data_size = conn.recv(4)
                            if not data_size or len(data_size) < 4:
                                break
                            
                            size = struct.unpack('>I', data_size)[0]
                            if size == 0:
                                err+=1
                                break
                            buffer_frame = Cmd.unpack_image(conn,size)
                            image = cv2.imdecode(np.frombuffer(buffer_frame, dtype=np.uint8), cv2.IMREAD_COLOR)
                        
                            cv2.imshow('Client camera IP: ' + arg_addr,image)
                            # cv2.waitKey(5)
                        
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                Worker.Worker.delete_quece(quece)
                                err+= 1
                                break
                        
                    except Exception as e:
                        # print("\nError: " + str(e))
                        # print(Cmd.prepare_input())
                        Worker.Worker.throw_err(str(e),"camera")            
                    finally:
                        conn.close()
                        cv2.destroyAllWindows()

        except Exception as e:
            # print("\nError: " + str(e))
            Worker.Worker.throw_err(str(e),"camera")
        finally:
            # print("\nCamera: end connect to "+ str(addr_client))
            # print(Cmd.prepare_input())
            # Worker.Worker.throw_err("End work from quece id " + str(quece),"camera")
            Worker.Worker.delete_quece(quece)
            row = 0    
            if [quece,arg_addr] in cls.camera_works:
                cls.camera_works.remove([quece,arg_addr])
    
    camera_works = []
    # camera_quece = 0
        
    @classmethod    
    def camera(cls,cmd: str):
        args = cls.getArgs(cmd)
        
        try:
            if args[0] == "--workers":
                # if args[1] == "queces":
                print("\nQUECES")
                for i in cls.camera_works:
                    print("QUECE: " + str(i[0]) + " | IP: " + str(i[1]))
            elif args[0] == "--connect":
                # Worker.delete_quece(cls.camera_quece)
                camera_quece = Worker.Worker.get_quece()
                cls.camera_works.append([camera_quece,args[1]])
                camShowThread = threading.Thread(target=Cmd.cameraWorker,args=(args[1],camera_quece))
                camShowThread.start()
            elif args[0] == "--disconnect":
                addr = args[1]
                row = 0    
                for i in cls.camera_works:
                    if i[1] == addr:
                        Worker.Worker.delete_quece(i[0])
                        row+=1
                
                    if row < 1:
                        print("Not found connect ip " + str(addr)+" working.")
            else:
                print("Not found command.")
                # Worker.delete_quece(cls.camera_quece)
        # Cmd.cameraWorker(args[0],0)
        except Exception as e:
            print("ERROR: " + str(e))
            
    def thread_edit(cmd: str):
        args = Cmd.getArgs(cmd)
        if len(args) > 0:
            if args[0] == "--list":
                    print("\nThread quece\n")
                    queces = Worker.Worker.buffer
                    for info in queces:
                        print("QUECE: " + str(info[0]) + " | STATUS: " + str(info[1]))
            elif args[0] == "--quece":
                try:
                    quece_id = int(args[1])
                    if args[2] == "--del":
                        quece_del = Worker.Worker.delete_quece(quece_id)
                        if quece_del == []:
                            print("Not found quece.")
                except Exception as e:
                    print("ERROR: " + str(e))
            elif args[0] == "--error":
                error_log = Worker.Worker.get_throw_err()
                print(error_log)
    
    @classmethod
    def client(cls,cmd):
        args = Cmd.getArgs(cmd)
        if len(args) > 0:
            if args[0] == "--list":
                print("\nLIST CLIENT")
                for addr in cls.client_addr:
                    print("ADDRESS: " + addr)
            elif args[0] == "--scan":
                try:
                    # print("test")
                    start = int(args[1])
                    end = int(args[2])
                    ip_pattle = args[3]
                    cls.scan(start,end,ip_pattle)
                except Exception as e:
                    print("Wrong input args.")
        else:
            err_msg = "Error args"
            
    @classmethod
    def captureWorker(cls,arg_addr: str,quece: int,size_window:float):
        # time.sleep(60)
        try:
            Worker.Worker.update_quece("capture",quece)
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                sock.connect((arg_addr,cls.port))
                header = [['VERIFY','CTL'],['COMMAND','streamonitor'],['MONITOR','0']]
                header_text = phase.MakeHeaderText(header)
                sock.sendall(header_text.encode())
            
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                sock.settimeout(30)
                sock.bind(('0.0.0.0',cls.port))
                sock.listen(1)
                
                err = 0
                
                while True:
                    if not err == 0:
                        break
                    
                    worker_status = Worker.Worker.search_quece(quece)
                    if len(worker_status) == 0:
                        break
                    
                    conn, addr = sock.accept()
                    
                    # if not addr[0] == cls.client_addr:
                    #     conn.close()
                    #     if input("want to end thread [Y = YES,N = NO]: ") == "Y":
                    #         break
                    #     continue
                    
                    try:
                        while True:
                            worker_status = Worker.Worker.search_quece(quece)
                            if len(worker_status) == 0:
                                break
                            data_size = conn.recv(4)
                            if not data_size or len(data_size) < 4:
                                break
                            
                            size = struct.unpack('>I', data_size)[0]
                            if size == 0:
                                err+=1
                                break
                            buffer_frame = Cmd.unpack_image(conn,size)
                            image = cv2.imdecode(np.frombuffer(buffer_frame, dtype=np.uint8), cv2.IMREAD_COLOR)
                            resized_img = cv2.resize(image, (0,0), fx=size_window,fy=size_window)
                            cv2.imshow('Client monitor IP: ' + arg_addr,resized_img)
                            # cv2.waitKey(5)
                        
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                Worker.Worker.delete_quece(quece)
                                err+= 1
                                break
                        
                    except Exception as e:
                        # print("\nError: " + str(e))
                        # print(Cmd.prepare_input())
                        Worker.Worker.throw_err(str(e),"capture")            
                    finally:
                        conn.close()
                        cv2.destroyAllWindows()

        except Exception as e:
            # print("\nError: " + str(e))
            Worker.Worker.throw_err(str(e),"capture")
        finally:
            # print("\nCamera: end connect to "+ str(addr_client))
            # print(Cmd.prepare_input())
            # Worker.Worker.throw_err("End work from quece id " + str(quece),"camera")
            Worker.Worker.delete_quece(quece)
            # if [quece,arg_addr] in cls.camera_works:
            #     cls.camera_works.remove([quece,arg_addr])
    
    def capture(cmd:str):
        try:
            args = Cmd.getArgs(cmd)
            if args[0] == "--connect":
                des_addr = args[1] 
                if len(args) > 2:
                    if args[2] == "--size":
                        size = float(args[3])
                quece = Worker.Worker.get_quece()
                CaptureThread = threading.Thread(target=Cmd.captureWorker,args=(des_addr,quece,size))
                CaptureThread.start()
                
        except Exception as e:
            print("ERROR: " + str(e))
            Worker.Worker.throw_err(str(e),"capture")
        
    # ===================== COMMAND PROGRESS =============================
    
    def check(cmd: str):
        err_msg = ""
        
        if Cmd.findCommand(cmd,"exit"):
            os._exit(1)
        elif Cmd.findCommand(cmd,"shutdown"):
            Cmd.shutdown(cmd)
        elif Cmd.findCommand(cmd,"camera"):
            Cmd.camera(cmd)
        elif Cmd.findCommand(cmd,"client"):
            Cmd.client(cmd)
        elif Cmd.findCommand(cmd,"thread"):
            Cmd.thread_edit(cmd)
        elif Cmd.findCommand(cmd,"capture"):
            Cmd.capture(cmd)
        else:
            err_msg = "Not found '" + cmd + "' command"
        
        if err_msg != "":
            print(err_msg)