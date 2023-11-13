#   Solving the Megaminx 
#   Last Updated: 9/13/23

import copy
import math

#This is the function that gets called by megaminx.py
def enter_astar(logical_array, logical_faces):
    result, solve_stack = run_astar(logical_array, logical_faces)
        
    return solve_stack

#Node object for the search tree
class Node:
    def __init__(self, f, my_logical_array, my_parent, g, color_turned):
        self.f = f
        self.my_logical_array = my_logical_array
        self.my_parent = my_parent
        self.g = g
        self.color_turned = color_turned

#returns 1 if a logical array is solved, otherwise returns 0
def check_if_solved(logical_array):
    for i in range(len(logical_array)):
        if((logical_array[i].home_face != logical_array[i].current_face) or (logical_array[i].home_index != logical_array[i].current_index)):
            return 0
    return 1

#Print the path to get here
def print_path(node, solve_stack):
    if(node != 0):
        print_path(node.my_parent, solve_stack)
        solve_stack.append(node.color_turned) 
        return solve_stack

def calculate_hueristic(logical_array):
    mismatched_faces = 0
    
    #Count the number of stickers on the wrong face and divide by 15
    for i in range(len(logical_array)):
        if(logical_array[i].home_face != logical_array[i].current_face):
            mismatched_faces = mismatched_faces + 1
        
    return math.floor(mismatched_faces/15)

#To implement A* I refrenced the psuedo-code described by "geeksforgeeks" near the top of the following web page:
#https://www.geeksforgeeks.org/a-search-algorithm/
def run_astar(logical_array, logical_faces):
    
    print("\n---\nStarting solve using A*")
    
    #If its already solved we can return immediatly
    if(check_if_solved(logical_array)):
        return 1, [-1]

    #A* Search Algorithm
    loop_iterations = 0

    #1. Initialize the open and closed list
    open_list = []
    closed_list = []

    #2. Create the starting node and put it on the open list, this node gets a copy of the logical array that represents the current state of the toy
    new_node = Node(0, copy.deepcopy(logical_array), 0, 0, -1)
    open_list.append(new_node)

    #3. While the open list is not empty
    while(len(open_list) > 0):
   
        #4. Find the node on open list with the least f and assign it to q
        min_f = open_list[0].f
        q = open_list[0] #Remember in python we are just passing pointers to the object around,  so q is the same object not a copy
        
        for i in range(len(open_list)):
            if(open_list[i].f < min_f):
                    min_f = open_list[i].f
                    q = open_list[i]

        #5. Pop q off the open_list
        open_list.pop(open_list.index(q))
        
        #6. Generate Q's 12 children (One for each potential face rotation)
        successors = []
        for i in range(12):
            #Create a copy of the Q's my_logical_array
            child_logical_array = copy.deepcopy(q.my_logical_array)
            
            #Rotate the childs logical array around face i
            child_logical_array = logical_faces[i].rotate_counter_clockwise(child_logical_array) 
            
            #Create the child node, it's parent is q, its g value should be one more than the parent
            child_node = Node(0, child_logical_array, q, q.g + 1, i)
            successors.append(child_node)

        #7. Loop through each successor
        for i in range(len(successors)):
            dont_skip_child = 1
            
            #Check if the successor is solved, if it is stop the search
            if(check_if_solved(successors[i].my_logical_array)):
                print("A* Complete!\nNodes in open list = " + str(len(open_list)) + "\nNodes in closed list = " + str(len(closed_list)))
                
                #Retrace the solution and store it in a list
                solve_stack = []
                solve_stack = print_path(successors[i], solve_stack)
                
                return 1, solve_stack
                
            #Otherwise we need to do some more things
            else:
                #Calcualte the huerestic value for the child (for now I am using the dumbest huerestic imaginable)
                child_hueristic = calculate_hueristic(successors[i].my_logical_array);
                successors[i].f = child_hueristic + successors[i].g
                
                #If a node on the open list with the same logical array has a lower f than the child, skip this child
                for n in range(len(open_list)):
                    if((open_list[n].f < successors[i].f) and (open_list[n].my_logical_array == successors[i].my_logical_array)):
                        dont_skip_child = 0
                    
                #If a node on the closed list with the same logical array has a lower f than the child, skip this child
                for n in range(len(closed_list)):
                    if((closed_list[n].f < successors[i].f) and (closed_list[n].my_logical_array == successors[i].my_logical_array)):
                        dont_skip_child = 0
                
                #If the child was not skipped, add it to the open list
                if(dont_skip_child):
                    open_list.append(successors[i])
                    
        #Push q onto the closed list 
        closed_list.append(q)
