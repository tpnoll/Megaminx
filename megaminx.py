#   Representing the Megaminx 
#   Last Updated: 9/13/23

#   Refrences:
#   https://docs.python.org/3/library/tkinter.html
#       Import library and create the frame
#   https://www.geeksforgeeks.org/python-tkinter-create-different-shapes-using-canvas-class/
#       How to draw a polygon with points and colors and pack it to a canvas

from tkinter import *
from tkinter import ttk
import math
import random
import copy
import time

#Import the solver
import astar

#Global variable for color selection
selected_color = 6

#THIS CLASS WAS WRITTEN BY BING AI 8/30/23 at 9:22pm
#Prompt: I am programming a GUI using Tkinter. Write a function for a button. This button should be a square of a solid color and have no text inside. When this button is clicked it should open a new window that allows the user to select one of 12 colors which are also displayed as a set of colored squares. When a new color is selected, it should close the new window and change the color of the original button to the color that was selected.
class ColorButton:
    def __init__(self, master, colors):
        self.master = master
        self.color = 'yellow'
        self.color_options = colors
        self.create_button()

    def create_button(self):
        self.button_canvas = Canvas(self.master, width=50, height=50)
        self.button_canvas.pack()
        self.button_canvas.create_rectangle(0, 0, 50, 50, fill=self.color, outline='')
        self.button_canvas.bind('<Button-1>', lambda event: self.show_color_options())

    def show_color_options(self):
        self.color_window = Toplevel(self.master)
        canvas = Canvas(self.color_window, width=200, height=200)
        canvas.pack()
        x, y = 0, 0
        for color in self.color_options:
            canvas.create_rectangle(x, y, x+50, y+50, fill=color, outline='', tags=color)
            x += 50
            if x >= 200:
                x = 0
                y += 50
            canvas.tag_bind(color, '<Button-1>', lambda event, c=color: self.change_color(c))

    def change_color(self, color):
        self.color = color
        self.button_canvas.delete('all')
        self.button_canvas.create_rectangle(0, 0, 50, 50, fill=self.color, outline='')
        self.color_window.destroy()
        global selected_color
        selected_color = self.color_options.index(color)
#The Above class was written by Bing AI 8/30/23 at 9:22pm

#Object representing a sticker - Used for GUI only
class Piece:
    def __init__(self, type, color, point_arr):
        self.type = type
        self.color = color
        self.point_arr = point_arr

#Object for representing a face - Used for GUI only   
class Face:
    def __init__(self, color, cx, cy, r):
        self.color = color
        self.cx = cx
        self.cy = cy
        self.r = r
        self.pieces = []
        
        #Create point lists for first two pieces
        corner, edge = create_pentagon_segment(cx, cy, r)
        
        #Create the first two piece objects
        new_piece = Piece("corner", color, corner)
        self.pieces.append(new_piece)
        
        new_piece = Piece("edge", color, edge)
        self.pieces.append(new_piece)
        
        #Create the remaining 8 piece objects to complete the pentagon
        for i in range(8):
            new_piece = Piece(self.pieces[i].type, color, rotate(self.pieces[i].point_arr, cx, cy, 72))
            self.pieces.append(new_piece)
            
        #Create an extra piece for the center pentagon
        pentagon_points = []
        for i in range(len(self.pieces)):
            pentagon_points.append(self.pieces[i].point_arr[0])
            pentagon_points.append(self.pieces[i].point_arr[1])
        new_piece = Piece("center", color, pentagon_points)
        self.pieces.append(new_piece)
        
    #Rotate points on the screen, this is not a face rotation!    
    def rotate(self, t):
        #For every piece
        for p in range(len(self.pieces)):
            self.pieces[p].point_arr = rotate(self.pieces[p].point_arr, self.cx, self.cy, t)

#Returns two arrays for two manually defined pentagon segments (A corner piece and an edge piece) - Used for GUI only
def create_pentagon_segment(x, y, r):
    corner_height = r
    corner_breadth = corner_height / math.tan(math.radians(55))
    corner = [x, y - r, x - corner_breadth, y - r - corner_height/2, x, y - r - corner_height, x + corner_breadth, y - r - corner_height/2]
    rotated_corner = rotate(corner, x, y, 72)
    edge = [corner[0], corner[1], rotated_corner[0], rotated_corner[1], rotated_corner[2], rotated_corner[3], corner[6], corner[7]]
    return corner, edge
    
#Return an array of points rotated t degrees clockwise - Used for GUI only
def rotate(point_arr, cx, cy, t):
    new_point_arr = []
    for index in range(len(point_arr) - 1):
        if((index + 1) % 2 == 1):
            x = point_arr[index] - cx
            y = point_arr[index + 1] - cy
            new_point_arr.append((x * math.cos(math.radians(t)) - y * math.sin(math.radians(t))) + cx)
            new_point_arr.append((y * math.cos(math.radians(t)) + x * math.sin(math.radians(t)))+cy)  
    return new_point_arr

#Pass center of one face, returns an array for centers of all other faces - Used for GUI only
def calc_face_places(cx, cy, r):
    centers = [cx, cy]
    half_side = 2 * r * math.cos(math.radians(54))
    deltax = (2 * half_side * math.sin(math.radians(54)))
    deltay = 2 * ((2 * r) - (half_side * math.cos(math.radians(54))))

    temp_arr = [cx + deltax, cy - deltay]
    centers = centers + temp_arr
    for i in range(4):
        temp_arr = rotate(temp_arr, cx, cy, 72)
        centers = centers + temp_arr
    
    new_centers = []
    for i in range(len(centers)):
        if(((i + 1) % 2) != 0):
            new_centers.append(centers[i])
        else:
            new_centers.append(centers[i] - 300)
            
    centers = centers + new_centers
    return centers

#Logical Representations : These are the classes and functions that represent the megaminx and handle rotations, they are distinct in case the GUI needs to be swapped out

#Logical representation of a sticker
class Logical_Piece:
    def __init__(self, flat_index, home_face, home_index):
        self.flat_index = flat_index    #Position in the array of 120 pieces (for easy refrence)
        self.home_face = home_face      #Where the piece belongs 
        self.home_index = home_index
        self.current_face = home_face   #Where the piece actually is
        self.current_index = home_index

#Logical representation of a face
class Logical_Face:
    def __init__(self, id, inside_corner, inside_edge, outside_corner, outside_edge):
        self.id = id
        #These lists contain pointers to the logical array 
        self.inside_corner = inside_corner
        self.inside_edge = inside_edge
        self.outside_corner = outside_corner
        self.outside_edge = outside_edge
     
    #Rotations are done in 4 parts: Internal corners, Internal edges, External corners, External edges
    
    def rotate_clockwise(self, logical_array):
        
        #Isolate for A*
        rotated_array = copy.deepcopy(logical_array)
    
        #Rotate inside corner
        rotated_index = rotated_array[self.inside_corner[len(self.inside_corner) - 1]].current_index
        rotated_face = rotated_array[self.inside_corner[len(self.inside_corner) - 1]].current_face
        for i in reversed(range(1, len(self.inside_corner))):
            rotated_array[self.inside_corner[i]].current_index = rotated_array[self.inside_corner[i - 1]].current_index
            rotated_array[self.inside_corner[i]].current_face = rotated_array[self.inside_corner[i - 1]].current_face
        rotated_array[self.inside_corner[0]].current_index = rotated_index
        rotated_array[self.inside_corner[0]].current_face = rotated_face
        
        #Rotate inside edge
        rotated_index = rotated_array[self.inside_edge[len(self.inside_edge) - 1]].current_index
        rotated_face = rotated_array[self.inside_edge[len(self.inside_edge) - 1]].current_face
        for i in reversed(range(1, len(self.inside_edge))):
            rotated_array[self.inside_edge[i]].current_index = rotated_array[self.inside_edge[i - 1]].current_index
            rotated_array[self.inside_edge[i]].current_face = rotated_array[self.inside_edge[i - 1]].current_face
        rotated_array[self.inside_edge[0]].current_index = rotated_index
        rotated_array[self.inside_edge[0]].current_face = rotated_face
        
        #Rotate outside corner (Twice)
        for i in range(2):
            rotated_index = rotated_array[self.outside_corner[len(self.outside_corner) - 1]].current_index
            rotated_face = rotated_array[self.outside_corner[len(self.outside_corner) - 1]].current_face
            for i in reversed(range(1, len(self.outside_corner))):
                rotated_array[self.outside_corner[i]].current_index = rotated_array[self.outside_corner[i - 1]].current_index
                rotated_array[self.outside_corner[i]].current_face = rotated_array[self.outside_corner[i - 1]].current_face
            rotated_array[self.outside_corner[0]].current_index = rotated_index
            rotated_array[self.outside_corner[0]].current_face = rotated_face
        
        #Rotate outside edge
        rotated_index = rotated_array[self.outside_edge[len(self.outside_edge) - 1]].current_index
        rotated_face = rotated_array[self.outside_edge[len(self.outside_edge) - 1]].current_face
        for i in reversed(range(1, len(self.outside_edge))):
            rotated_array[self.outside_edge[i]].current_index = rotated_array[self.outside_edge[i - 1]].current_index
            rotated_array[self.outside_edge[i]].current_face = rotated_array[self.outside_edge[i - 1]].current_face
        rotated_array[self.outside_edge[0]].current_index = rotated_index
        rotated_array[self.outside_edge[0]].current_face = rotated_face
        
        return rotated_array
        
    def rotate_counter_clockwise(self, logical_array):
        
        #Isolate for A*
        rotated_array = copy.deepcopy(logical_array)
        
        #Rotate inside corner 
        temp_index = rotated_array[self.inside_corner[0]].current_index
        temp_face = rotated_array[self.inside_corner[0]].current_face
        for i in range(0, len(self.inside_corner) - 1):
            rotated_array[self.inside_corner[i]].current_index = rotated_array[self.inside_corner[i + 1]].current_index
            rotated_array[self.inside_corner[i]].current_face = rotated_array[self.inside_corner[i + 1]].current_face
        rotated_array[self.inside_corner[len(self.inside_corner) - 1]].current_index = temp_index
        rotated_array[self.inside_corner[len(self.inside_corner) - 1]].current_face = temp_face
        
        #Rotate inside edge
        temp_index = rotated_array[self.inside_edge[0]].current_index
        temp_face = rotated_array[self.inside_edge[0]].current_face
        for i in range(0, len(self.inside_edge) - 1):
            rotated_array[self.inside_edge[i]].current_index = rotated_array[self.inside_edge[i + 1]].current_index
            rotated_array[self.inside_edge[i]].current_face = rotated_array[self.inside_edge[i + 1]].current_face
        rotated_array[self.inside_edge[len(self.inside_edge) - 1]].current_index = temp_index
        rotated_array[self.inside_edge[len(self.inside_edge) - 1]].current_face = temp_face
        
        #Rotate outside corner (Twice)
        for i in range(2):
            temp_index = rotated_array[self.outside_corner[0]].current_index
            temp_face = rotated_array[self.outside_corner[0]].current_face
            for i in range(0, len(self.outside_corner) - 1):
                rotated_array[self.outside_corner[i]].current_index = rotated_array[self.outside_corner[i + 1]].current_index
                rotated_array[self.outside_corner[i]].current_face = rotated_array[self.outside_corner[i + 1]].current_face
            rotated_array[self.outside_corner[len(self.outside_corner) - 1]].current_index = temp_index
            rotated_array[self.outside_corner[len(self.outside_corner) - 1]].current_face = temp_face
            
        #Rotate outside edge
        temp_index = rotated_array[self.outside_edge[0]].current_index
        temp_face = rotated_array[self.outside_edge[0]].current_face
        for i in range(0, len(self.outside_edge) - 1):
            rotated_array[self.outside_edge[i]].current_index = rotated_array[self.outside_edge[i + 1]].current_index
            rotated_array[self.outside_edge[i]].current_face = rotated_array[self.outside_edge[i + 1]].current_face
        rotated_array[self.outside_edge[len(self.outside_edge) - 1]].current_index = temp_index
        rotated_array[self.outside_edge[len(self.outside_edge) - 1]].current_face = temp_face
        
        return rotated_array
            
#Update GUI piece objects to have the same color as their logical counterparts 
def update_gui_colors():
    canvas.delete("all")
    logical_index = 0
    for f in range(len(faces)):
        for p in range (len(faces[f].pieces)):
            if(p != 10):
                faces[f].pieces[p].color = colors[logical_array[logical_index].current_face]
                logical_index = logical_index + 1
            canvas.create_polygon(faces[f].pieces[p].point_arr, outline = "black", fill = faces[f].pieces[p].color, width = 2)
    canvas.update()            

#Rotate face selected_color clockwise or counter clockwise and update GUI
def do_rotate_face_clockwise():
    global logical_array
    logical_array = logical_faces[selected_color].rotate_clockwise(logical_array) 
    update_gui_colors()
    
def do_rotate_face_counter_clockwise():
    global logical_array
    logical_array = logical_faces[selected_color].rotate_counter_clockwise(logical_array) 
    update_gui_colors()

#Perform num_moves random rotations on the megaminx
def do_scramble(num_moves):
    global selected_color
    
    #Save the selected color to not interfere with the user's selection 
    saved_selected_color = selected_color
    
    last_color = -1
    last_rot = -1
    
    i = 0
    while i < num_moves:
        do_rot = 1
        selected_color = random.randint(0, 11)
        rot = random.randint(0, 1)
        
        #Prevent undo rotation on a face
        if((selected_color == last_color) & (rot != last_rot)):
            i = i - 1
            do_rot = 0
            
            
        last_color = selected_color
        last_rot = rot
        
        if(do_rot):
            if(rot):
                do_rotate_face_clockwise()
            else:
                #FOR A* I WANT TO ALWAYS SCRAMBLE CLOCKWISE
                #do_rotate_face_counter_clockwise()
                do_rotate_face_clockwise()               
        i = i + 1
    
    #Reset selected_color back to it's original value
    selected_color = saved_selected_color
        

#
#   MAIN
#

colors = ["white", "violet", "wheat3", "turquoise1", "purple", "green", "yellow", "seagreen1", "pink", "blue", "red", "orange"]

#Create a list containing 120 pieces with an explicit index (logical array)
global logical_array
logical_array = []
for f in range(12):
    for i in range(10):
        logical_piece = Logical_Piece(len(logical_array), f, i)
        logical_array.append(logical_piece)
        
#Stickers internal to a face are found automatically, but stickers external to a face that are still affected by a rotation are defined explicity here. The contents of the lists index the logical array. This could be found automatically but I can't be bothered to do any more geometry. 
white_outside_corner = [24,36,34,46,44,56,54,16,14,26]
white_outside_edge = [25,35,45,55,15]
violet_outside_corner = [54,52,90,98,82,80,28,26,2,0]
violet_outside_edge = [53,99,81,27,1]
wheat_outside_corner = [4,2,14,12,80,88,72,70,38,36]
wheat_outside_edge = [3,13,89,71,37]
turquoise_outside_corner = [6,4,24,22,70,78,112,110,48,46]
turquoise_outside_edge = [5,23,79,111,47]
purple_outside_corner = [8,6,34,32,110,118,102,100,58,56]
purple_outside_edge = [7,33,119,101,57]
green_outside_corner = [0,8,44,42,100,108,92,90,18,16]
green_outside_edge = [9,43,109,91,17]
yellow_outside_corner = [84,96,94,106,104,116,114,76,74,86]
yellow_outside_edge = [85,95,105,115,75]
mint_outside_corner = [30,38,22,20,88,86,62,60,114,112]
mint_outside_edge = [39,21,87,61,113]
pink_outside_corner = [64,62,74,72,20,28,12,10,98,96]
pink_outside_edge = [63,73,29,11,97]
blue_outside_corner = [66,64,84,82,10,18,52,50,108,106]
blue_outside_edge = [65,83,19,51,107]
red_outside_corner = [68,66,94,92,50,58,42,40,118,116]
red_outside_edge = [67,93,59,41,117]
orange_outside_corner = [60,68,104,102,40,48,32,30,78,76]
orange_outside_edge = [69,103,49,31,77]

outside_corners = [white_outside_corner, violet_outside_corner, wheat_outside_corner,turquoise_outside_corner,purple_outside_corner,green_outside_corner,yellow_outside_corner,mint_outside_corner,pink_outside_corner,blue_outside_corner,red_outside_corner,orange_outside_corner]
outside_edges = [white_outside_edge, violet_outside_edge, wheat_outside_edge,turquoise_outside_edge,purple_outside_edge,green_outside_edge,yellow_outside_edge,mint_outside_edge,pink_outside_edge,blue_outside_edge,red_outside_edge,orange_outside_edge]

#Create a list containing the twelve logical faces with refrences to the stickers they affect
logical_faces = []
for f in range(12):
    inside_corner = []
    inside_edge = []
    for i in range(10):
        index = f*10 + i
        if((index % 2) == 0):
            inside_corner.append(index)
        else:
            inside_edge.append(index)
    logical_face = Logical_Face(f, inside_corner, inside_edge, outside_corners[f], outside_edges[f])
    logical_faces.append(logical_face) 

#Calls enter_astar (Because tkinter buttons are confusing)
def dial_astar():
    global logical_array
    solve_stack = astar.enter_astar(logical_array, logical_faces)

    print("\nThe following steps will solve the puzzle:")
    for i in range(1, len(solve_stack)):
        print(str(i) + ". perform a clockwise rotation on face " + str(solve_stack[i]))
        time.sleep(2)
        logical_array = logical_faces[solve_stack[i]].rotate_counter_clockwise(logical_array) 
        update_gui_colors() 
    
#Create 12 faces for the GUI and rotate them correctly on the screen
faces = []
centers = calc_face_places(500, 500, 30)
for i in range(len(centers)):
    if(((i + 1) % 2) != 0):
        temp_face = Face(colors[int(i/2)], centers[i], centers[i + 1], 30)
        if((i > 0) & (i < 12)):
            temp_face.rotate(-36 + 72*((i/2)%12))
        elif(i > 12):
            temp_face.rotate(-108 + 72*((i/2)%12))
        faces.append(temp_face)
         
#Initialize the window
root = Tk()
frame = ttk.Frame(root, padding=10)
canvas = Canvas()

#Make the color of the GUI pieces match those of the logical pieces
update_gui_colors()  

canvas.pack(fill = BOTH, expand = 1)

#Buttons for manual user control
button = ttk.Button(root, text="Rotate Clockwise", command=do_rotate_face_clockwise)
button.place(x=1100, y=130)
button = ttk.Button(root, text="Rotate Counter Clockwise", command=do_rotate_face_counter_clockwise)
button.place(x=1100, y=170)

label = Label(root, text="Select color to rotate:")
label.place(x=1100, y=100)

label = Label(root, text="# Random Rotations:")
label.place(x=1100, y=210)

input_box = Entry(root)
input_box.place(x=1100, y=230)

num_scrambles = 10
button = ttk.Button(root, text="Scramble", command=lambda: do_scramble(int(input_box.get())))
button.place(x=1100, y=260)

button = ttk.Button(root, text="Solve using A*", command=dial_astar)
button.place(x=1100, y=370)

#User color selection 
frame = Frame(root)
frame.place(x=1250, y=100)

style = ttk.Style()
for color in colors:
    style.configure(f'{color}.TButton', background=color)
app = ColorButton(frame, colors)

root.mainloop()