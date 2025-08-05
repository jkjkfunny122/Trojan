import server
import tools
import os
import header
import socket
import control

hostname = socket.gethostname()

server_class = server.server
controller_class = control.control

server_class.start()

controller_class.add_function('server',server_class.entry,False)
import clientc
controller_class.add_function(clientc.client.name,clientc.client.entry,False)
import camera
controller_class.add_function(camera.camera_remote.name,camera.camera_remote.entry)

control.control.run()

server_class.stop()