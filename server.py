import socket
import pickle
import struct

import cv2

from ultralytics import YOLO

import json
import datetime

import sys

def server_tcp(results_file_name):
    # server_results = input("Server results file name: ")
    results_file = open(f'results/{results_file_name}.txt', "w")

    # get the hostname
    host = "10.38.151.146"
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    server_socket.bind((host, port))  # bind host address and port together

    model = YOLO('yolov8n.pt')  # load a pretrained YOLOv8n detection model

    # model("tcp://10.38.151.146:2000\?listen")

    data = b''
    payload_size = struct.calcsize("L") 

    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection

    while True:
        # Retrieve message size
        while len(data) < payload_size:
            data += conn.recv(1024)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += conn.recv(1024)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Extract frame
        frame = pickle.loads(frame_data)
        results = model(frame)  # predict on an image

        results_final = []
        for result in results:
            curr_res_speed  = result.speed
            print(curr_res_speed)
            results_file.write(json.dumps(curr_res_speed)+'\n')

            curr_res_boxes  = result.boxes

            curr_res_class  = curr_res_boxes.cls

            curr_res_names = []
            for class_name in curr_res_class:
                curr_res_names.append(model.names[int(class_name)])
            
            curr_res_bb     = curr_res_boxes.xywhn
            curr_res_conf   = curr_res_boxes.conf

            curr_res = {
                'classes': curr_res_class.tolist(),
                'names': curr_res_names,
                'bb': curr_res_bb.tolist(),
                'conf': curr_res_conf.tolist()
            }

            result_struct = {
                # 'client_id': client_id,
                # 'frame_no': frame_no,
                'results': curr_res
            }

            results_final.append(result_struct)

        # return results as JSON
        results_to_client = {
            "dataType": "results", 
            "data": results_final
        }

        results_json = json.dumps(results_to_client)
        rj_len = len(results_json)
        print((f'Results JSON has size {rj_len} B'))
        results_file.write(f'Results JSON has size {rj_len} B\n')
        conn.send(results_json.encode())


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

def server_udp(results_file_name):
    # server_results = input("Server results file name: ")
    results_file = open(f'results/{results_file_name}.txt', "w")

    model = YOLO('yolov8n.pt')  # load a pretrained YOLOv8n detection model

    host = "10.38.151.146"
    port   = 5001

    buffer_size  = 1024

    # Create a datagram socket and bind IP and port
    udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_server_socket.bind((host, port))

    image_data = b''
    payload_size = struct.calcsize("L") 

    # Listen for incoming datagrams
    while(True):
        bytes_address_pair = udp_server_socket.recvfrom(buffer_size)

        data = bytes_address_pair[0]
        address = bytes_address_pair[1]

        curr_frame_number = int.from_bytes(data[0:4], "little") 
        curr_packet_number = int.from_bytes(data[4:8], "little")
        total_num_packets = int.from_bytes(data[8:12], "little")
        pickle_size = int.from_bytes(data[12:16], "little")

        sent_image_data = data[16:buffer_size+16]

        if curr_packet_number == 0:
            image_data = bytearray(pickle_size)

        # append sent image data into the image_data array 
        if curr_packet_number+1 == total_num_packets:
            # final_size = pickle_size
            # # final_size = buffer_size - (pickle_size - len(image_data))
            # print(pickle_size, final_size, len(image_data))
            image_data[buffer_size*curr_packet_number:pickle_size] = sent_image_data
        else:
            image_data[buffer_size*curr_packet_number:buffer_size] = sent_image_data
        print(curr_frame_number, curr_packet_number, total_num_packets)

        if curr_packet_number+1 == total_num_packets:
            # Extract frame
            print(len(image_data))
            # print(image_data)
            frame = pickle.loads(image_data)
            results = model(frame)  # predict on an image

            results_final = []
            for result in results:
                curr_res_speed  = result.speed
                print(curr_res_speed)
                results_file.write(json.dumps(curr_res_speed)+'\n')

                curr_res_boxes  = result.boxes

                curr_res_class  = curr_res_boxes.cls

                curr_res_names = []
                for class_name in curr_res_class:
                    curr_res_names.append(model.names[int(class_name)])
                
                curr_res_bb     = curr_res_boxes.xywhn
                curr_res_conf   = curr_res_boxes.conf

                curr_res = {
                    'classes': curr_res_class.tolist(),
                    'names': curr_res_names,
                    'bb': curr_res_bb.tolist(),
                    'conf': curr_res_conf.tolist()
                }

                result_struct = {
                    # 'client_id': client_id,
                    # 'frame_no': frame_no,
                    'results': curr_res
                }

                results_final.append(result_struct)

            # return results as JSON
            results_to_client = {
                "dataType": "results", 
                "data": results_final
            }

            results_json = json.dumps(results_to_client)
            rj_len = len(results_json)
            print((f'Results JSON has size {rj_len} B'))
            results_file.write(f'Results JSON has size {rj_len} B\n')
            udp_server_socket.sendto(results_json, address)

if __name__ == '__main__':

    protocol = sys.argv[1]
    results_file_name = sys.argv[2]

    if protocol == "tcp":
        server_tcp(results_file_name)
    elif protocol == "udp":
        server_udp(results_file_name)