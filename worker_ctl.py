import threading

class Worker:
    lock = threading.Lock()
    total_quece = 0
    buffer = []
    err_throw = []
    
    @classmethod
    def get_quece(cls):
        quece = cls.total_quece
        cls.total_quece += 1
        return quece
    
    @classmethod
    def search_quece(cls,quece: int):
        with cls.lock:
            result = []
            for i in range(len(cls.buffer)):
                if cls.buffer[i][0] == quece:
                    result = cls.buffer[i]
                    break
        
        return result
    
    @classmethod
    def delete_quece(cls,quece: int):
        with cls.lock:
            result = []
            for i in range(len(cls.buffer)):
                if cls.buffer[i][0] == quece:
                    result = cls.buffer.pop(i)
                    break
        
        return result
    
    @classmethod
    def update_quece(cls,data: str,quece: int):
        with cls.lock:
            cls.buffer.append([quece,data])

    @classmethod
    def throw_err(cls,msg:str,func:str):
        with cls.lock:
            cls.err_throw.append([func,msg])
            
    @classmethod
    def get_throw_err(cls):
        with cls.lock:
            if len(cls.err_throw) > 0:
                err_msg = ""
                for i in cls.err_throw:
                    err_msg += "FROM :" + i[0] + " | THROW " + i[1] + "\n"
                
                # cls.err_throw = []
                return err_msg
            else:
                return ""

