import socket
import cv2
import pickle5 as pickle
import struct

def client_tcp():
    host = "10.38.151.146"
    port = 5000 

    client_socket = socket.socket()
    client_socket.connect((host, port)) 

    print("Loading video")
    input_video = cv2.VideoCapture("input_videos/4k_60fps.webm")
    print("Loaded video")

    count = 0
    success = 1
  
    while success:
        # vidObj object calls read
        # function extract frames
        print("Loading frame")
        success, image = input_video.read()
        print("Pickling frame")
        data = pickle.dump(image, protocol=5)
        print("Pickled frame")

        message_size = struct.pack("L", len(data))

        client_socket.send(message_size + data)  # send message

        print(count, len(data))
        # Saves the frames with frame-count
        # cv2.imwrite("frame%d.jpg" % count, image)
  
        count += 1

    # message = "test"  # take input

    # while message.lower().strip() != 'bye':
    #     client_socket.send(message.encode())  # send message
    #     data = client_socket.recv(1024).decode()  # receive response

    #     print('Received from server: ' + data)  # show in terminal

        # message = input(" -> ")  # again take input

    # client_socket.close()  # close the connection


if __name__ == '__main__':
    client_tcp()