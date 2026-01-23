#!/usr/bin/env python

"""This is the Controller Starter Code for ECE50863 Lab Project 1
Author: Xin Du
Email: du201@purdue.edu
Last Modified Date: December 9th, 2021
"""

import sys
from datetime import date, datetime
import socket
from collections import defaultdict

# Please do not modify the name of the log file, otherwise you will lose points because the grader won't be able to find your log file
LOG_FILE = "Controller.log"

# Those are logging functions to help you follow the correct logging standard

# "Register Request" Format is below:
#
# Timestamp
# Register Request <Switch-ID>

def register_request_received(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Request {switch_id}\n")
    write_to_log(log)

# "Register Responses" Format is below (for every switch):
#
# Timestamp
# Register Response <Switch-ID>

def register_response_sent(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Response {switch_id}\n")
    write_to_log(log) 

# For the parameter "routing_table", it should be a list of lists in the form of [[...], [...], ...]. 
# Within each list in the outermost list, the first element is <Switch ID>. The second is <Dest ID>, and the third is <Next Hop>, and the fourth is <Shortest distance>
# "Routing Update" Format is below:
#
# Timestamp
# Routing Update 
# <Switch ID>,<Dest ID>:<Next Hop>,<Shortest distance>
# ...
# ...
# Routing Complete
#
# You should also include all of the Self routes in your routing_table argument -- e.g.,  Switch (ID = 4) should include the following entry: 		
# 4,4:4,0
# 0 indicates ‘zero‘ distance
#
# For switches that can’t be reached, the next hop and shortest distance should be ‘-1’ and ‘9999’ respectively. (9999 means infinite distance so that that switch can’t be reached)
#  E.g, If switch=4 cannot reach switch=5, the following should be printed
#  4,5:-1,9999
#
# For any switch that has been killed, do not include the routes that are going out from that switch. 
# One example can be found in the sample log in starter code. 
# After switch 1 is killed, the routing update from the controller does not have routes from switch 1 to other switches.

def routing_table_update(routing_table):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append("Routing Update\n")
    for row in routing_table:
        log.append(f"{row[0]},{row[1]}:{row[2]},{row[3]}\n")
    log.append("Routing Complete\n")
    write_to_log(log)

# "Topology Update: Link Dead" Format is below: (Note: We do not require you to print out Link Alive log in this project)
#
#  Timestamp
#  Link Dead <Switch ID 1>,<Switch ID 2>

def topology_update_link_dead(switch_id_1, switch_id_2):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Link Dead {switch_id_1},{switch_id_2}\n")
    write_to_log(log) 

# "Topology Update: Switch Dead" Format is below:
#
#  Timestamp
#  Switch Dead <Switch ID>

def topology_update_switch_dead(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Switch Dead {switch_id}\n")
    write_to_log(log) 

# "Topology Update: Switch Alive" Format is below:
#
#  Timestamp
#  Switch Alive <Switch ID>

def topology_update_switch_alive(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Switch Alive {switch_id}\n")
    write_to_log(log) 

def write_to_log(log):
    with open(LOG_FILE, 'a+') as log_file:
        log_file.write("\n\n")
        # Write to log
        log_file.writelines(log)

def dijkstras(graph, src: int, num):
    # graph adj list
    # source ncode


    #ok needs to return a routing table 
    '''
    The routing algorithm used by the controller to compute paths is Dijkstra’s shortest path
    algorithm. Specifically, of all possible paths between the source and destination, the path with the
    shortest “distance” is chosen. The distance of a path is the sum of all the links’ distances on the
    path


    ROUTING TABLE
    according to google routing table has a destination nexthop and cost 

    i guess next hop is the next node it has to go to on its path to its destination if no direct connect

    minHeap E log V prolly 
    '''

    # For the self-entry the total distance is 0. If a
    # switch can’t be reached from the current switch, then the next hop is set to -1 and the distance
    # is set to 9999

    infin = 9999 # unreached

    heap = [(0, src)]
    prev = { src : None } # prev node for the next hop stuff 
    
    dist = {}

    for i in range(num):
        dist[i] = infin

    dist[src] = 0


    # algos heappop logn E * logV time complex
    while heap:
        distance, node = heapq.heappop(heap)

        if distance >= dist[node]:
            continue # already found better

        if distance + dist[]


    

    
def main():
    #Check for number of arguments and exit if host/port not provided
    num_args = len(sys.argv)
    if num_args < 3:
        print ("Usage: python controller.py <port> <config file>\n")
        sys.exit(1)

    '''
    argv[1] = controller port
    argv[2] = config file path
    '''
    
    # Write your code below or elsewhere in this file
    ip = "127.0.0.1"
    port = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))

    config_path = sys.argv[2]
    neighbors = defaultdict(list)
    graph = defaultdict(list)
    with open(config_path, 'r') as file:
        num_switches = int(file.readline().strip())

        for line in file:
            line = line.strip()
            if not line: continue

            a, b, cost = line.split()
            
            a = int(a)
            b = int(b)
            cost = int(cost)

            neighbors[a].append(b)
            neighbors[b].append(a) #bidrectional

            graph[a].append((b, cost))
            graph[b].append((a, cost))
   
    # print(num_switches)
    #print(neighbors)

    bufsize = 1024
    switch_addr = {}
    #response = "Register_Response"
    done = False

    while True:
        message, address = sock.recvfrom(bufsize)
        msg_str = message.decode('utf-8').strip() # add a strip to get rid of any \n or similar things
        full = msg_str.split()

        if len(full) >= 2:
            switch_id = int(full[0])
            token = full[1]

            if token == "Register_Request":
                register_request_received(switch_id)
                switch_addr[switch_id] = address
                if not done and len(switch_addr) == num_switches:
                    for s_id, addr in switch_addr.items():
                        tmp = []
                        tmp.append(str(len(neighbors[s_id])))

                        for nei in neighbors[s_id]:
                            nei_ip, nei_port = switch_addr[nei]
                            tmp.append(f"{nei} {nei_ip} {nei_port}")
                        
                        payload = "\n".join(tmp)
                        sock.sendto(payload.encode("utf-8"), addr)
                        register_response_sent(s_id)
                    done = True







    

if __name__ == "__main__":
    main()