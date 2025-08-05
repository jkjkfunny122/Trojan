import clientc
import cv2
import struct
import socket
import tools
import pickle
import numpy as np
import header
import control
import task
import time

class camera_remote:
    name = 'camera'
    task_queue = None
    
    @classmethod
    def entry(cls,cmmd):
        cls.task = control.control.functions[cls.name]['task']
        cls.task_queue = cls.task.queue
        clientc.client.inuse(cls.task_queue,cls.name)
        
        cls.frame_recv()
        
        clientc.client.unuse(cls.task_queue)
        cls.task.destroy()
        control.control.functions[cls.name]['task'] = None
        # tools.tools.show_popup('Camera Exit.')
        print('Camera exit.')
        
    @classmethod
    def frame_recv(cls):
        client__ = clientc.client

        h = header.header()
        h.insert_key('cmmd','camera_remote')
        h.insert_key('arg','frame')
        h_pack = pickle.dumps(h.get_header())
        h_size = len(h_pack)
        pack_size = struct.pack('>I',h_size)
        
        if not client__.socket_send(pack_size):
            print(f'Error: socket failed.')
        
        if not client__.socket_send(h_pack):
            print(f'Error: send socket is failed.')
        
        err_count = 0
        
        start_time = time.time()
        fps_count = 0
        while True:
            if not cls.task.check():
                break
            elif err_count > 5:
                print(f'Error: too many times.')
                break
            
            frame_size = client__.socket_recv(4)
            if frame_size == False:
                print(f'Error: socket.')
                break
            elif not len(frame_size) == 4:
                print(f'Error: packet')
                err_count+=1
                continue
            
            size = struct.unpack('>I',frame_size)[0]
            
            if size < 1:
                print(f'Error: packet')
                err_count+=1
                continue
            
            frame_data = b''
            
            while size > 0:
                recv_size = 0
                if size >= 1024:
                    recv_size = 1024
                elif size < 1024 and size > 0:
                    recv_size = size
                else:
                    break
                
                data_so = client__.socket_recv(recv_size)
                if data_so == False:
                    frame_data = b''
                    break
                elif len(data_so) < 1:
                    frame_data = b''
                    break
                
                frame_data += data_so
                size -= recv_size
                
            if len(frame_data) < 1:
                print(f'Error: packet')
                err_count+=1
                continue
            
            frame_unpack = pickle.loads(frame_data)
            frame = cv2.imdecode(frame_unpack,cv2.IMREAD_COLOR)
            
            fps_count += 1
            cv2.imshow(f'Camera IP: {client__.addr[0]}',frame)
            
            elpis = (time.time() - start_time)
            if elpis >= 1:
                print(f"FPS: {fps_count} | time: {elpis}")
                start_time = time.time()
                fps_count = 0
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
                
        h.insert_key('arg','exit')
        h_pack = pickle.dumps(h.get_header())
        h_size = len(h_pack)
        pack_size = struct.pack('>I',h_size)
        
        if client__.socket_send(pack_size):
            if not client__.socket_send(h_pack):
                print(f'Error: socket send.')
        else:
            print(f'Error: socket send.')
        
        # connect.setblocking(False)
        # try:
        #     while True:
        #         data = connect.recv(1024)
        #         if not data:
        #             break
        # except BlockingIOError:
        #     pass
            
        # connect.setblocking(True)
        cv2.destroyAllWindows()