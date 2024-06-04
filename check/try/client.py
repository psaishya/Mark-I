import cv2
import numpy as np
import socket
import sys
import pickle
import struct

video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('localhost',8089))
data = b''
payload_size = struct.calcsize("L")  # unsigned long integer

while True:
    try:
        ######################
        ##send client stream##
        ###################### 

        ret,frame=video.read()
        clientdata = pickle.dumps(frame)
        message_size = struct.pack("L", len(clientdata)) 
        clientsocket.sendall(message_size + clientdata)

        #####################
        ##rcv server stream##
        #####################   

        while len(data) < payload_size:
            data += clientsocket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0] 

        while len(data) < msg_size:
            data += clientsocket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)
        cv2.imshow('receiver_frame', frame)

        if cv2.waitKey(1) == 27:
            print("you closed")
            clientsocket.shutdown(2)    
            clientsocket.close()
            cv2.destroyAllWindows()
            break
    except :
        cv2.destroyAllWindows()
        print("other person closed")     
        break    
      
video.release()