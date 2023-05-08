import socket
import cv2
import pickle
import struct

import numpy as np

import time

def client_tcp():
    client_results = input("Client results file name: ")
    results_file = open(f'results/{client_results}.txt', "a")

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
        load_start = int(time.time_ns()/1000)
        success, image = input_video.read()
        load_end = int(time.time_ns()/1000)
        results_file.write(f'Frame {count} loaded in {load_end-load_start} ms')

        print(f'Pickling Frame {count}')
        pickle_start = int(time.time_ns()/1000)
        data = pickle.dumps(image, protocol=5)
        pickle_end = int(time.time_ns()/1000)

        pickle_len = len(data)
        print(f'Pickled Frame {count} which has length {pickle_len} B')
        results_file.write(f'Pickled Frame {count} which has length {pickle_len} B')
        results_file.write(f'Frame {count} pickled in {pickle_end-pickle_start} ms')

        total_packets = int(np.ceil(pickle_len / 16384))
        print(f'Total number of packets to transmit is {total_packets}')
        results_file.write(f'Total number of packets to transmit is {total_packets}')

        message_size = struct.pack("L", pickle_len)

        send_start = int(time.time_ns()/1000)
        client_socket.send(message_size + data)  # send message
        send_end = int(time.time_ns()/1000)
        results_file.write(f'Frame {count} sent in {send_end-send_start} ms')

        recv = client_socket.recv(1024).decode()  # receive response
        response_start = int(time.time_ns()/1000)

        results_file.write(f'Frame {count} response received in {response_start-send_end} ms')

        print(count, pickle_len)
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