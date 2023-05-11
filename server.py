import socket
import pickle
import struct

import cv2

from ultralytics import YOLO

import json
import datetime

def server_tcp():
    server_results = input("Server results file name: ")
    results_file = open(f'results/{server_results}.txt', "w")

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
            data += conn.recv(16384)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += conn.recv(16384)

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


if __name__ == '__main__':
    server_tcp()