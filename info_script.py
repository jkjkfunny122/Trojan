import time
import network
import struct
import task
import socket
import header
import tools
import pickle
import struct
import commander

class script:
    name = 'info_script'    
    packets = None
    
    @classmethod
    def entry(cls,packets: list):
        cls.packets = packets
        cls.run()
        
    @classmethod
    def run(cls):
        if task.task.find_task(commander.cmmd.functions['info_script']['task'].queue) == -1:
            return 0
            
        my_packets = cls.packets.copy()
            
        with commander.cmmd.lock:
            commander.cmmd.functions[cls.name]['packets'] = []
                
        for i in my_packets:
            if 'arg' in i:
                if i['arg'] == 'version':
                    h = header.header()
                    h.insert_key('cmmd_reply',cls.name)
                    h.insert_key('version',tools.tools.version)
                    
                    if isinstance(network.network.connect,socket.socket):
                        data = pickle.dumps(h.get_header())
                        size = len(data)
                        size_pack = struct.pack('>I',size)
        
                        network.network.connect.sendall(size_pack)
                        network.network.connect.sendall(data)
                        
                    print('respone version')
        
        task.task.delete_task(commander.cmmd.functions['info_script']['task'].queue)
        commander.cmmd.functions['info_script']['task'] = None