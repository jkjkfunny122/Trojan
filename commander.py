import network
import task
import threading

class cmmd:
    functions = {}
    
    lock = threading.Lock()
    my_task = None
    
    @classmethod
    def add_function(cls,entry_addr,name: str):
        cls.functions[name] = {"addr":entry_addr,"task":None,"packets":[]}
    
    @classmethod
    def packet_find(cls):
        packets = network.network.get_all_packets()
        remove_keys = []
        
        for key,item in packets.items():
            if 'cmmd' in item['data']:
                
                for key_f,item_f in cls.functions.items():
                    if item['data']['cmmd'] == key_f:
                        
                        if isinstance(cls.functions[key_f]['packets'] , list):
                            cls.functions[key_f]['packets'].append(item['data'])
                            remove_keys.append(key)
                        
                        if cls.functions[key_f]['task'] is None:
                            cls.functions[key_f]['task'] = task.task(cls.functions[key_f]['addr'],(cls.functions[key_f]['packets'],),name=key_f)
                            cls.functions[key_f]['task'].task.start()
        
        network.network.remove_packets(remove_keys)

    @classmethod
    def entry(cls):
        cls.my_task = task.task(cls.run,(),name='commander')
        cls.my_task.task.start()
        print('Cmmd is running')

    @classmethod
    def run(cls):
        while True:
            if task.task.find_task(cls.my_task.queue) == -1:
                break
            cls.packet_find()
        
        if not task.task.find_task(cls.my_task.queue) == -1:
            task.task.delete_task(cls.my_task.queue)
        cls.my_task = None