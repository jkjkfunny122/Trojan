import cv2
import pickle
import commander
import network
import time
import struct
import threading
import copy

class camera:
    name = 'camera_remote'

    @classmethod
    def check_packet(cls):
        with commander.cmmd.lock:
            packets = copy.deepcopy(commander.cmmd.functions[cls.name]['packets'])
            commander.cmmd.functions[cls.name]['packets'] = []
        
        exit_ret = False
        respone = len(packets)
        
        for i in packets:
            if 'arg' in i:
                if i['arg'] == 'exit':
                    exit_ret = True
                    break
        
        return exit_ret, respone
    
    status_work = False
    
    @classmethod
    def entry(cls,packets: list):
        frame = 0
        cls.status_work = True
        for i in packets:
            if 'arg' in i:
                if i['arg'] == 'frame':
                    frame+=1
                    break
        
        if frame > 0:
            col_t = threading.Thread(target=cls.collect_buffer,args=())
            col_t.daemon = True
            col_t.start()
            
            cap_t = threading.Thread(target=cls.capture_send,args=())
            cap_t.daemon = True
            cap_t.start()
        
        while True:
            time.sleep(0.2)
            exit_ret ,res = cls.check_packet()
            if exit_ret:
                break
        
        cls.status_work = False
        commander.cmmd.functions[cls.name]['task'].destroy()
        
        with commander.cmmd.lock:
            commander.cmmd.functions[cls.name]['task'] = None
            
        print("exit camera")
        
    buffers = []
    
    lock = threading.Lock()
    
    @classmethod
    def capture_send(cls):
        buffer_rate = 30/1000 #s
        network__ = network.network
        err_count = 0
        while True:
            if err_count > 5:
                break
            
            start_time = time.time()
            with cls.lock:
                buffers = copy.deepcopy(cls.buffers)
                cls.buffers = []
                
            for i in buffers:
                if err_count > 5:
                    break
                if not network__.socket_send(i[0]):
                    err_count+=1
                    continue
                if not network__.socket_send(i[1]):
                    err_count+=1
                    continue
            
            eltime_work = buffer_rate - (time.time() - start_time)
            if eltime_work > 0:
                time.sleep(eltime_work)
        
        cls.status_work = False
    
    @classmethod
    def collect_buffer(cls):
        
        fps = 30
        el_fps = 1/fps
        cap = cv2.VideoCapture(0)
        
        err_count = 0
        
        while True:
            if not cls.status_work:
                break
            elif len(cls.buffers) > (fps*6):
                break
            elif err_count > 5:
                break
            
            start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                err_count+=1
                continue
            
            enimg_list = [int(cv2.IMWRITE_JPEG_QUALITY),70]
            result, enimg = cv2.imencode('.jpg',frame,enimg_list)
            
            enimg_pack = pickle.dumps(enimg)
            size_pack = struct.pack('>I',len(enimg_pack))
            
            cls.buffers.append([size_pack,enimg_pack])
            
            time_work = el_fps - (time.time() - start_time)
            if time_work > 0:
                time.sleep(time_work)
        
        cap.release()
        cls.status_work = False    