import socket
import pickle

import cv2

from ultralytics import YOLO

def server_tcp():
    # get the hostname
    host = "10.38.151.146"
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    model = YOLO('yolov8n.pt')  # load a pretrained YOLOv8n detection model

    data = b''
    payload_size = struct.calcsize("L") 

    while True:
        # Retrieve message size
        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Extract frame
        frame = pickle.loads(frame_data)
        model(frame)  # predict on an image

    # # configure how many client the server can listen simultaneously
    # server_socket.listen(2)
    # conn, address = server_socket.accept()  # accept new connection
    # print("Connection from: " + str(address))
    # while True:
    #     # receive data stream. it won't accept data packet greater than 1024 bytes
    #     data = conn.recv(40000).decode()
    #     if not data:
    #         # if data is not received break
    #         break
    #     print("from connected user: ", len(data))
    #     model(data)  # predict on an image

        # data = input(' -> ')
        # conn.send(data.encode())  # send data to the client

    conn.close()  # close the connection


if __name__ == '__main__':
    server_tcp()