import pickle
import socket
import struct

import cv2

HOST = ''
PORT = 8089

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#print('Socket created')
s.bind((HOST, PORT))
#print('Socket bind complete')
s.listen(10)
#print('Socket now listening')

conn, addr = s.accept()

data = b''
payload_size = struct.calcsize("L")

video = cv2.VideoCapture(1, cv2.CAP_DSHOW)

while True:
    try:
        #########################
        ##sending server stream##
        #########################
        ret,ser=video.read()
        serverdata = pickle.dumps(ser)
        message_size = struct.pack("L", len(serverdata)) 
        conn.sendall(message_size + serverdata)

        #####################
        ##rcv client stream##
        #####################
    
        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0] 
        
        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)

        cv2.imshow('sender_frame', frame)
        if cv2.waitKey(1) == 13:
            print("you closed")
            conn.shutdown(2)    
            conn.close()
            cv2.destroyAllWindows()
            break
    except:
        cv2.destroyAllWindows()
        print("other person closed")  
        break

video.release()