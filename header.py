import pickle
class header:
    admin_role = 'A00'
    client_role = 'C00'
    
    roles = {
        "admin": admin_role,
        "client": client_role
    }
    header_signal = 'header_signal'
    
    def __init__(self,controller: bool | None = None):
        
        if controller is None:
            controller = False
        
        self.header = {}
        if controller:
            self.role = header.admin_role
        else:
            self.role = header.client_role
        self.signal = header.header_signal
        
        self.header["role"] = self.role
        self.header["signal"] = self.signal
        self.header["data"] = {}
    
    @classmethod
    def check_header(cls,data_header:dict):
        if isinstance(data_header,dict):
            if len(data_header) == 3:
                if "role" in data_header and "signal" in data_header and "data" in data_header:
                    if data_header["signal"] == cls.header_signal:
                        
                        for key,value in cls.roles.items():
                            if data_header["role"] == value:
                                return True                            
                            
        
        return False
    
    def get_header(self):
        if header.check_header(self.header):
            return self.header
        
        print("Failed: Header isn't from header class.")
    
    def insert_key(self,key,value):
        self.header["data"][key] = value
        return True
    
    def del_key(self,key):
        if key in self.header["data"]:
            del self.header["data"][key]
            return True
        else:
            print("Failed: can't remove protected key.")
        return False