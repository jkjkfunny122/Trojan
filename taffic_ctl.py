import socket
import cmd_ctl as CMD

# addr_client = []
# port_ctl = 9166
# host = str(socket.gethostname())

def main():
    
    while True:
        # throw_err = Worker.Worker.get_throw_err()
        # if not throw_err == "":
        #     print(throw_err)
            
        cmd = input(CMD.Cmd.prepare_input())
        CMD.Cmd.check(cmd)
        
main()