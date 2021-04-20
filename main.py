import numpy as np
import astar
import copy
import time
import sys
import tkinter as tk



window = tk.Tk()
text= tk.Label(width=20,height=1,text='owo')
text.pack()
button = tk.Button(width=5, height=5, text='test', bg='white', fg='black')
button.pack()
heightEntry = tk.Entry(width=20, fg='red', bg='blue')
widthEntry = tk.Entry(width=20, fg='red', bg='blue')
heightEntry.pack()
widthEntry.pack()


#Test code to ensure that A-Star algorithm is running as intended

fileName = 'map'
startSymbol = 'x'
goalSymbol = 'v'
with open(fileName) as f:
    charGrid = np.array(
        [[int(char) if char.isnumeric() else char for char in line]
         for line in f.read().splitlines()])

#Selects out the symbols for start and goal, and replaces them with 1s once complete.
start = np.where(charGrid == startSymbol)
start = tuple(zip(start[0], start[1]))
goal = np.where(charGrid == goalSymbol)
goal = tuple(zip(goal[0], goal[1]))
currentMap = copy.deepcopy(charGrid)

charGrid[start[0]] = 1
charGrid[goal[0]] = 1
print(start, goal)
asG = astar.AStarCalc(charGrid, start=start[0], goal=goal[0])
path = None
while not path:
    path = asG.get_next_steps()
    opens = asG.getOpens()
    closed = asG.getClosed()
    for i in opens:
        currentMap[i] = 'D'
    for i in closed:
        currentMap[i] = 'x'
    time.sleep(1)
    sys.stdout.write(str(currentMap))
    sys.stdout.flush()


#Highlight the final path with +
for p in path[::-1]:
    currentMap[p] = '+'

print(currentMap)
