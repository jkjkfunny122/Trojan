import threading
class task:
    last_queue = 0
    tasks = {}
    # errors = []
    
    lock = threading.Lock()
    
    def __init__(self,target,arg_s,name: str | None=None,data = ''):
        if name is None:
            name = ''
            
        self.name = name
        self.data = data
        self.queue = task.get_queue()
        
        self.task = task.create(target,arg_s,self.queue)
        if isinstance(self.task,threading.Thread):
            self.task.daemon = True
            print("Task: task created.")
        else:
            self.task = None
            print("Failed: create task failed.")
    
    def destroy(self):
        if task.delete_task(self.queue):
            return True
        else:
            return False
    
    def check(self):
        if task.find_task(self.queue) == -1:
            return False
        else:
            return True
        
    @classmethod
    def get_queue(cls):
        with cls.lock:
            my_queue = cls.last_queue
            cls.last_queue += 1
            return my_queue
    
    @classmethod
    def create(cls,target_s,arg_s: tuple,queue: int):
        task_var = {}
        task_var["task"] = threading.Thread(target=target_s,args=arg_s)
        cls.tasks[queue] = task_var
        
        return task_var["task"]
    
    @classmethod
    def find_task(cls,queue:int):
        with cls.lock:
            if queue in cls.tasks:
                return cls.tasks[queue]
            else:
                return -1
    
    @classmethod
    def delete_task(cls,queue:int):
        with cls.lock:
            if queue in cls.tasks:
                del cls.tasks[queue]
                return True
            else:
                return False
    
    @classmethod
    def destroy_all(cls):
        for key, item in list(cls.tasks.items()):
            if cls.delete_task(key):
                print("Task: deleted task queue " + str(key))
            else:
                print("Failed: can't delete task queue " + str(key))
                