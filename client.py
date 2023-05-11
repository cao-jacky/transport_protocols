import socket
import cv2
import pickle
import struct

import numpy as np

import time

import sys

resolutions_dict = {
    '4k': '4k_60fps.webm',
    '2k': '1440p_60fps.webm',
    '1080p': '1080p_60fps.webm',
    '720p': '720p_60fps.webm',
    '480p': '480p_30fps.webm',
    '360p': '360p_30fps.webm',
    '240p': '240p_30fps.mp4',
    '144p': '144p_30fps.mp4'
}

def client_tcp(video_file, results_file_name):
    # client_results = input("Client results file name: ")
    results_file = open(f'results/{results_file_name}.txt', "w")

    host = "10.38.151.146"
    port = 5000 

    client_socket = socket.socket()
    client_socket.connect((host, port)) 

    print(f'[{time.time_ns()/1000}] Loading video')
    input_video = cv2.VideoCapture(f'input_videos/{video_file}')
    print(f'[{time.time_ns()/1000}] Loaded video')

    count = 0
    success = 1

    while success:
        # vidObj object calls read
        # function extract frames
        print(f'[{time.time_ns()/1000}] Loading frame')
        load_start = int(time.time_ns()/1000)
        success, image = input_video.read()
        load_end = int(time.time_ns()/1000)
        results_file.write(f'[{time.time_ns()/1000}] Frame {count} loaded in {load_end-load_start} ms\n')

        print(f'[{time.time_ns()/1000}] Pickling Frame {count}')
        pickle_start = int(time.time_ns()/1000)
        data = pickle.dumps(image, protocol=5)
        pickle_end = int(time.time_ns()/1000)

        pickle_len = len(data)
        print(f'[{time.time_ns()/1000}] Pickled Frame {count} which has length {pickle_len} B')
        results_file.write(f'[{time.time_ns()/1000}] Pickled Frame {count} which has length {pickle_len} B\n')
        results_file.write(f'[{time.time_ns()/1000}] Frame {count} pickled in {pickle_end-pickle_start} ms\n')

        total_packets = int(np.ceil(pickle_len / 16384))
        print(f'[{time.time_ns()/1000}] Total number of packets to transmit is {total_packets}')
        results_file.write(f'[{time.time_ns()/1000}] Total number of packets to transmit is {total_packets}\n')

        message_size = struct.pack("L", pickle_len)

        send_start = int(time.time_ns()/1000)
        client_socket.send(message_size + data)  # send message
        send_end = int(time.time_ns()/1000)
        results_file.write(f'[{time.time_ns()/1000}] Frame {count} sent in {send_end-send_start} ms\n')

        recv = client_socket.recv(1024).decode()  # receive response
        response_start = int(time.time_ns()/1000)

        results_file.write(f'[{time.time_ns()/1000}] Frame {count} response received in {response_start-send_end} ms\n')

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

def client_udp(video_file, results_file_name):
    # client_results = input("Client results file name: ")
    results_file = open(f'results/{results_file_name}.txt', "w")

    host = "10.38.151.146"
    port = 5001

    print(f'[{time.time_ns()/1000}] Loading video')
    input_video = cv2.VideoCapture(f'input_videos/{video_file}')
    print(f'[{time.time_ns()/1000}] Loaded video')

    count = 0
    success = 1

    packet_size = 1024

    while success:
        # vidObj object calls read
        # function extract frames
        print(f'[{time.time_ns()/1000}] Loading frame')
        load_start = int(time.time_ns()/1000)
        success, image = input_video.read()
        load_end = int(time.time_ns()/1000)
        results_file.write(f'[{time.time_ns()/1000}] Frame {count} loaded in {load_end-load_start} ms\n')

        print(f'[{time.time_ns()/1000}] Pickling Frame {count}')
        pickle_start = int(time.time_ns()/1000)
        data = pickle.dumps(image, protocol=5)
        pickle_end = int(time.time_ns()/1000)

        pickle_len = len(data)
        pickle_len_bytes = pickle_len.to_bytes(4, 'little')
        print(f'[{time.time_ns()/1000}] Pickled Frame {count} which has length {pickle_len} B')
        results_file.write(f'[{time.time_ns()/1000}] Pickled Frame {count} which has length {pickle_len} B\n')
        results_file.write(f'[{time.time_ns()/1000}] Frame {count} pickled in {pickle_end-pickle_start} ms\n')

        total_packets = int(np.ceil(pickle_len / packet_size))
        total_pakcets_bytes = total_packets.to_bytes(4, 'little')

        print(f'[{time.time_ns()/1000}] Total number of packets to transmit is {total_packets}')
        results_file.write(f'[{time.time_ns()/1000}] Total number of packets to transmit is {total_packets}\n')

        message_size = struct.pack("L", pickle_len)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_addr = (host, port)

        curr_frame = count
        curr_frame_bytes = curr_frame.to_bytes(4, 'little')

        send_start = int(time.time_ns()/1000)
        bytes_count = 0
        curr_packet = 0
        while curr_packet < total_packets:
            packet_start = int(time.time_ns()/1000)
            img_part = data[bytes_count:bytes_count+packet_size]
            print(img_part)
            
            curr_packet_bytes = curr_packet.to_bytes(4, 'little')

            payload_size = packet_size + 16
            # data_to_send = bytearray(payload_size)

            data_to_send = curr_frame_bytes + curr_packet_bytes + total_pakcets_bytes + pickle_len_bytes + img_part
            sock.sendto(data_to_send, server_addr)
            packet_end = int(time.time_ns()/1000)
            results_file.write(f'[{time.time_ns()/1000}] Frame {count} sent packet {curr_packet} of {total_packets} in {packet_end-packet_start} ms\n')
            
            bytes_count += packet_size
            curr_packet += 1
        client_socket.send(message_size + data)  # send message
        send_end = int(time.time_ns()/1000)

        results_file.write(f'[{time.time_ns()/1000}] Frame {count} sent in {send_end-send_start} ms\n')

        recv = client_socket.recv(1024).decode()  # receive response
        response_start = int(time.time_ns()/1000)

        results_file.write(f'[{time.time_ns()/1000}] Frame {count} response received in {response_start-send_end} ms\n')

        print(count, pickle_len)
  
        count += 1



if __name__ == '__main__':
    protocol = sys.argv[1]
    selected_resolution = sys.argv[2]
    results_file_name = sys.argv[3]

    video_file = resolutions_dict[selected_resolution]

    if protocol == "tcp":
        client_tcp(video_file, results_file_name)
    elif protocol == "udp":
        client_udp(video_file, results_file_name)