#!/usr/bin/env python

"""This is the Controller Starter Code for ECE50863 Lab Project 1
Author: Xin Du
Email: du201@purdue.edu
Last Modified Date: December 9th, 2021
"""

import sys
from datetime import datetime
import socket
from collections import defaultdict
import heapq
import time

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
    # main part of dijkstas
    while heap:
        distance, u = heapq.heappop(heap)

        if distance > dist[u]: # get rid of = just >?
            continue # already found better

        for v, cost in graph[u]:
            # u makes a shorter path to v then update v 
            if distance + cost < dist[v]:
                dist[v] = distance + cost
                heapq.heappush(heap, (distance + cost, v))
                prev[v] = u 

    #need to make a routing table from src to each node i think
    

    #idrk lets get back to this later idrk
    next_hop = {}

    for i in range(num):

        if i == src:
            next_hop[i] = src

        elif dist[i] == infin:
            next_hop[i] = -1
        
        else:
            curr = i
            # while prev[curr] != src:
            while curr in prev and prev[curr] is not None and prev[curr] != src: # make sure that it not none just inc ase
                curr = prev[curr]
            next_hop[i] = curr

    return dist, next_hop


def make_new_graph(og_cost, link_alive):
    g = defaultdict(list)
    for (a, b), cost in og_cost.items():
        if link_alive.get((a, b), True): 
            g[a].append((b, cost))
            g[b].append((a, cost))

    return g

def push_routes(sock, switch_addr, graph, num_switches, dead_switches):
    routing_table = []
    per_switch_routes = {}

    for src in range(num_switches):
        if src in dead_switches:
            continue

        dist, next_hop = dijkstras(graph, src, num_switches)
        per_switch_routes[src] = (dist, next_hop)

        # <Switch ID>,<Dest ID>:<Next Hop>,<Shortest distance>
        for dest in range(num_switches):
            routing_table.append([src, dest, next_hop[dest], dist[dest]])

    routing_table_update(routing_table)

    for src in range(num_switches):
        if src not in switch_addr:
            continue
        if src in dead_switches:
            continue


        dist, next_hop = per_switch_routes[src]
        resp = []
        resp.append(str(src))
        for dest in range(num_switches):
            resp.append(f"{dest} {next_hop[dest]}")

        payload = "\n".join(resp)
        sock.sendto(payload.encode('utf-8'), switch_addr[src])

def main():
    K = 2
    TIMEOUT = 3 * K
    dead_switches = set()

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
    sock.settimeout(0.5)

    config_path = sys.argv[2]
    neighbors = defaultdict(list)
    graph = defaultdict(list)
    link_alive = {} # for topology updates: check if a link is good from both sides 
    og_cost = {}
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
            og_cost[(min(a, b), max(a, b))] = cost
            link_alive[(min(a, b), max(a, b))] = True

   
    # print(num_switches)
    #print(neighbors)
    switch_routes = {}
    routing_table = []
    reported_neighbors = defaultdict(dict) # for topology updates
    for src in range(num_switches):
        dist, next_hop = dijkstras(graph, src, num_switches)

        switch_routes[src] = (dist, next_hop)

        # <Switch ID>,<Dest ID>:<Next Hop>,<Shortest distance>
        for dest in range(num_switches):
            routing_table.append([src, dest, next_hop[dest], dist[dest]])


    bufsize = 8192
    switch_addr = {}
    last_heard = {}
    #response = "Register_Response"
    done = False

    while True:

        # try except for the timeout to check for dead switches

        try: # gets messsagse
            message, address = sock.recvfrom(bufsize)
            msg_str = message.decode('utf-8').strip()
            #print(msg_str)
        except socket.timeout: # no message received in timeout 
            # chek for dead switches
            current_time = time.monotonic()
            topology_changed = False

            for switch_id, last_heard_time in list(last_heard.items()):
                if current_time - last_heard_time > TIMEOUT:
                    if switch_id not in dead_switches:

                        dead_switches.add(switch_id)
                        topology_update_switch_dead(switch_id)
                        topology_changed = True

                        # get rid of all links from this switch
                        for nei in neighbors[switch_id]:
                            smaller, bigger = min(switch_id, nei), max(switch_id, nei)
                            
                            if link_alive.get((smaller, bigger), True):
                                topology_update_link_dead(smaller, bigger)
                                link_alive[(smaller, bigger)] = False
                            
                    del last_heard[switch_id]
                    if switch_id in switch_addr:
                        del switch_addr[switch_id]

            if topology_changed and done:
                new_graph = make_new_graph(og_cost, link_alive)
                push_routes(sock, switch_addr, new_graph, num_switches, dead_switches)    
            continue

        #msg_str = message.decode('utf-8').strip() # add a strip to get rid of any \n or similar things
        full = msg_str.split()

        if len(full) >= 2 and full[1] == "Register_Request":
            switch_id = int(full[0])

            if switch_id in dead_switches:
                dead_switches.remove(switch_id)
                topology_update_switch_alive(switch_id)

                for nei in neighbors[switch_id]:
                    smaller, bigger = min(switch_id, nei), max(switch_id, nei)
                    link_alive[(smaller, bigger)] = True
                    

            register_request_received(switch_id)
            switch_addr[switch_id] = address
            last_heard[switch_id] = time.monotonic()
        

            if not done and len(switch_addr) == num_switches:# dont proceed until all registered                    
                for s_id, addr in switch_addr.items():
                    tmp = []
                    tmp.append(str(len(neighbors[s_id])))
                    #routing_table_update(routing_table)
                    for nei in neighbors[s_id]:
                        nei_ip, nei_port = switch_addr[nei]
                        tmp.append(f"{nei} {nei_ip} {nei_port}")
                    
                    payload = "\n".join(tmp)
                    sock.sendto(payload.encode("utf-8"), addr)
                    register_response_sent(s_id)
                routing_table_update(routing_table)

                for src in range(num_switches): # ok so for ecah switch as the src i need to find enxt_hop and dist for each dest
                    dist, next_hop = switch_routes[src]
                    resp = []
                    resp.append(str(src))
                    for dest in range(num_switches): # no point in checking if src == dest
                        resp.append(f"{dest} {next_hop[dest]}")

                    payload = "\n".join(resp)
                    sock.sendto(payload.encode('utf-8'), switch_addr[src])
                    
                    
                done = True
                continue

            if done: 
                new_graph = make_new_graph(og_cost, link_alive)
                push_routes(sock, switch_addr, new_graph, num_switches, dead_switches)


            continue

        # topology_update 
        
        '''
        <switch_id>
        <neighbor_id> TRUE/FALSE
        '''
        lines = msg_str.splitlines()

        

        if len(lines) >= 2:
            switch_id = int(lines[0])
            if switch_id in dead_switches:
                continue
            last_heard[switch_id] = time.monotonic()

            topology_changed = False
            for line in lines[1:]:
                parts = line.split()
                if len(parts) == 2:
                    neighbor_id = int(parts[0])
                    status = parts[1].upper()

                    if status == "TRUE":
                        alive = True
                    elif status == "FALSE":
                        alive = False
                    else:
                        continue
                else:
                    continue
                

                # this part im not sure on double check this a lot of alives and deafult dict stuff here
                
                reported_neighbors[switch_id][neighbor_id] = alive
                smaller, bigger = min(switch_id, neighbor_id), max(switch_id, neighbor_id)
                
                if (smaller, bigger) not in og_cost:
                    continue 
                
                old_alive = link_alive.get((smaller, bigger), True) # default to true 
                other_alive = reported_neighbors[neighbor_id].get(switch_id, True) # default to true if we havent heard from the other side yet
    
                new_alive = alive and other_alive

                if old_alive != new_alive:
                    topology_changed = True
                    
                if old_alive and not new_alive:
                    topology_update_link_dead(smaller, bigger)

                link_alive[(smaller, bigger)] = new_alive # prolly use link alive to build a better graph for dijkstras and then update the routing table and send it to the switches when a link goes down or up

            if topology_changed and done:
                new_graph = make_new_graph(og_cost, link_alive)
                push_routes(sock, switch_addr, new_graph, num_switches, dead_switches)

            continue


            



if __name__ == "__main__":
    main()