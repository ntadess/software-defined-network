#!/usr/bin/env python

"""This is the Switch Starter Code for ECE50863 Lab Project 1
Author: Xin Du
Email: du201@purdue.edu
Last Modified Date: December 9th, 2021
"""

import sys
from datetime import date, datetime
import socket
import time
import threading

# Please do not modify the name of the log file, otherwise you will lose points because the grader won't be able to find your log file
LOG_FILE = "switch#.log" # The log file for switches are switch#.log, where # is the id of that switch (i.e. switch0.log, switch1.log). The code for replacing # with a real number has been given to you in the main function.

# Those are logging functions to help you follow the correct logging standard

# "Register Request" Format is below:
#
# Timestamp
# Register Request Sent

def register_request_sent():
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Request Sent\n")
    write_to_log(log)

# "Register Response" Format is below:
#
# Timestamp
# Register Response Received

def register_response_received():
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Response received\n")
    write_to_log(log) 

# For the parameter "routing_table", it should be a list of lists in the form of [[...], [...], ...]. 
# Within each list in the outermost list, the first element is <Switch ID>. The second is <Dest ID>, and the third is <Next Hop>.
# "Routing Update" Format is below:
#
# Timestamp
# Routing Update 
# <Switch ID>,<Dest ID>:<Next Hop>
# ...
# ...
# Routing Complete
# 
# You should also include all of the Self routes in your routing_table argument -- e.g.,  Switch (ID = 4) should include the following entry: 		
# 4,4:4

def routing_table_update(routing_table):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append("Routing Update\n")
    for row in routing_table:
        log.append(f"{row[0]},{row[1]}:{row[2]}\n")
    log.append("Routing Complete\n")
    write_to_log(log)

# "Unresponsive/Dead Neighbor Detected" Format is below:
#
# Timestamp
# Neighbor Dead <Neighbor ID>

def neighbor_dead(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Neighbor Dead {switch_id}\n")
    write_to_log(log) 

# "Unresponsive/Dead Neighbor comes back online" Format is below:
#
# Timestamp
# Neighbor Alive <Neighbor ID>

def neighbor_alive(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Neighbor Alive {switch_id}\n")
    write_to_log(log) 

def write_to_log(log):
    with open(LOG_FILE, 'a+') as log_file:
        log_file.write("\n\n")
        # Write to log
        log_file.writelines(log)

def main():
    K = 2 # Keep-Alive in seconds
    TIMEOUT = 3 * K

    global LOG_FILE


    

    #Check for number of arguments and exit if host/port not provided
    num_args = len(sys.argv)
    failed_neighbor_id = None 
    if num_args >= 6:
        if sys.argv[4] == '-f':
            failed_neighbor_id = int(sys.argv[5])
        else:
            failed_neighbor_id = None

    if num_args < 4:
        print ("switch.py <Id_self> <Controller hostname> <Controller Port>\n")
        sys.exit(1)

    my_id = int(sys.argv[1])
    LOG_FILE = 'switch' + str(my_id) + ".log" 

    # Write your code below or elsewhere in this file
    controller_hostname = sys.argv[2]
    controller_port = int(sys.argv[3])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg = f"{my_id} Register_Request"
    sock.sendto(msg.encode("utf-8"), (controller_hostname, controller_port))
    register_request_sent()
    bufsize = 8192 # maube 1024 too small ta said make it big 
    message, address = sock.recvfrom(bufsize)
    payload = message.decode('utf-8').strip()

    register_response_received()

    tmp = payload.strip().splitlines()
    num = int(tmp[0])
    
    nei_to_addr = {}
    nei_alive = {}
    nei_heard = {}

    for line in tmp[1:1 + num]:
        nei_id, nei_ip, nei_port = line.split()
        nei_id = int(nei_id)
        nei_port = int(nei_port)
        nei_to_addr[nei_id] = (nei_ip, nei_port)
        nei_alive[nei_id] = True
        nei_heard[nei_id] = time.monotonic()

    if failed_neighbor_id is not None and failed_neighbor_id in nei_alive:
        nei_alive[failed_neighbor_id] = False
        #nei_heard[failed_neighbor_id] = -1  # will never be updated
    
    lock = threading.Lock()
    def recv_loop(): # locks needed around nei_alive and nei_heard
        while True:

            # TWO TYPES OF MESSAGES
            # KEEP ALIVE AND ROUTE UPDTAE
            # must support the -f <neighbor_ID> flag to simulate a neighbor failure
            # python switch.py <id> <controller_host> <controller_port> -f <neighbor-id>

            message, address = sock.recvfrom(bufsize)

            #decode payload get the rotuing table

            #list of lists in the form of [[...], [...], ...]. 
            # Within each list in the outermost list, the first element is <Switch ID>. The second is <Dest ID>, and the third is <Next Hop>.
            payload = message.decode('utf-8').strip()
            detect = payload.split()

            if len(detect) == 2 and detect[1] == "KEEP_ALIVE":
                #format is like <switch-ID> KEEP_ALIVE acordingto the thing
                send_id = int(detect[0])

                if failed_neighbor_id is not None and send_id == failed_neighbor_id:
                    # ignore it cuz thats the one link we are told failed or
                    continue

                now = time.monotonic()

                lock.acquire()
                if send_id in nei_alive and not nei_alive[send_id]: # dead to alive 
                    # "Unresponsive/Dead Neighbor comes back online" Format is below:
                    
                    nei_alive[send_id] = True
                    
                    neighbor_alive(send_id) # log it

                
                nei_heard[send_id] = now
                lock.release()

                continue
                    
                
            ######## top updates logic for that
            tmp = payload.splitlines()
            ''' 
            format is 
            switch_id
            dest next_hop


            '''
            #print(tmp)
            s_id = int(tmp[0])
            routing_table = [] # log it in given format

            # do i need a s_id == current_id check??
            if s_id != my_id:
                continue
            
            for line in tmp[1:]:
                dest, next_hop = line.split()
                dest = int(dest)
                next_hop = int(next_hop)
                routing_table.append([s_id, dest, next_hop])
            
            routing_table_update(routing_table)



        


    def timer_loop():
        while True: # timer loop 
            now = time.monotonic()

            for nei_id in nei_to_addr: # locks needed around nei_to_addr? nvm no i dont its read only
                lock.acquire()
                if nei_alive[nei_id] and now - nei_heard[nei_id] > TIMEOUT:
                    # neighbor dead
                    nei_alive[nei_id] = False # i need locks around nei_alive and nei_heard
                    
                    neighbor_dead(nei_id) # log it

                if nei_alive[nei_id]:
                    # send keep alive
                    msg = f"{my_id} KEEP_ALIVE"
                    sock.sendto(msg.encode("utf-8"), nei_to_addr[nei_id])
                lock.release()
            time.sleep(K)

    t_recv = threading.Thread(target=recv_loop, daemon=True)
    t_timer = threading.Thread(target=timer_loop, daemon=True)
    t_recv.start()
    t_timer.start()


    while True:
        time.sleep(60)

    






if __name__ == "__main__":
    main()