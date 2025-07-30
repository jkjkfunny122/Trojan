def MakeHeaderText(list_header: list):
    text = ""
    
    list_header.append(["SIGNAL","HEADER_PHASED"])
    
    for i in range(0,len(list_header)):
        if i > 0:
            text = text + "\n" + list_header[i][0] + ":" + list_header[i][1]
        else:
            text = text + list_header[i][0] + ":" + list_header[i][1]
            
    return text

def PhaseHeaderText(text: str):
    if text.find("SIGNAL:HEADER_PHASED") < 0:
        return []
    
    text_array = text.splitlines()
    header_list = []
    for subject in text_array:
        sub_arr = subject.split(":")
        header_list.append(sub_arr)
    
    return header_list

def GetSubject(arr: list,sub: str):
    for i in arr:
        if i[0] == sub:
            return i[1]
    
    return ""