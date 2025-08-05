import socket
import task

class control:
    
    functions = {
        
    }
    
    @classmethod
    def add_function(cls,key:str,callback,daemon:bool | None=None):
        if daemon is None:
            daemon = True
        
        cls.functions[key] = {"callback": callback,"daemon":daemon,"task":None}
    
    hostname = socket.gethostname()
    
    @classmethod
    def sethostname(cls,hostname):
        cls.hostname = hostname
    
    @classmethod
    def run(cls):
        while True:
            cmmd = input(f"@{cls.hostname}> ")
            if cmmd == 'exit':
                break
            
            cmmd_arg = cmmd.split(' ')
            
            con = 0
            for key,item in cls.functions.items():
                if key == cmmd:
                    con+=1
                    if 'task' in cls.functions[key]:
                        if not cls.functions[key]['task'] is None:
                            task.task.delete_task(cls.functions[key]['task'].queue)
                            cls.functions[key]['task'] = None
                            break
                    
                    if item['daemon']:
                        cls.functions[key]['task'] = task.task(item['callback'],(cmmd_arg,),key)
                        cls.functions[key]['task'].task.start()
                        break
                    else:
                        try:
                            item['callback'](cmmd_arg)
                        except Exception as e:
                            print(f'Error controller: {e}')

            if con < 1:
                print(f'Unknow command {cmmd}.')