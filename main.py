import network
import commander
import tools
import os

net = network.network
comm = commander.cmmd


#add function list
import info_script
comm.add_function(info_script.script.entry,info_script.script.name)
import camera
comm.add_function(camera.camera.entry,camera.camera.name)

# if isinstance(net.connect,network.socket.socket):
#     try:
#         net.connect.sendall(tools.tools.exit_byte)
#         net.connect.close()
#     except Exception as e:
#         print(f'Error: {str(e)}')
#         net.connect.close()

#start
net.start()
comm.entry()

while True:
    pass