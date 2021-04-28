import numpy as np
import astar
import tkinter as tk
from enum import Enum
from tkinter import messagebox



class PathButton(tk.Frame):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


  def change_color(self, color):
    self.config(background=color)


class CellState(Enum):
  TURNWALLON=1
  TURNWALLOFF = 0

class AStarApplet():
  def __init__(self, width = 50, height = 50, buttonSize =3):

    self.cellWidth=20
    self.cellHeight=20
    self.gridWidth = width
    self.gridHeight = height



    self.window = tk.Tk()
    self._coloredCells = set()
    self._state = None
    self.startP = (0,0)
    self.endP = (self.gridHeight-1, self.gridWidth-1)
    self.placeholderStartP = None


    self._aStarGrid = np.ones((self.gridHeight, self.gridWidth))
    self.asG = astar.AStarCalc(self._aStarGrid, start=self.startP, goal=self.endP, diagnoal = True)
    self._stop = False


    self._OPENCOLOR = '#FFFFFF'
    self._WALLCOLOR = '#000000'
    self._GOALCOLOR = '#FF0000'
    self._STARTCOLOR = '#90EE90'
    self._PATHCOLOR = '#008080'
    self._OPENSETCOLOR = '#FFFF00'
    self._CLOSEDSETCOLOR = '#0000FF'

    self.current_button = None

    topSideFrame = tk.Frame()
    tk.Label(width=10, height=2, text='A* Applet', master=topSideFrame).pack()
    topSideFrame.pack(side=tk.TOP)
    rightSideFrame = tk.Frame()
    self.runButton = tk.Button(width=7, text='Run', master=rightSideFrame)
    rightSideFrame.pack(side=tk.RIGHT)
    self.resetButton = tk.Button(width=7, text='Reset', master=rightSideFrame)
    self.clearButton = tk.Button(width=7, text='Clear', master=rightSideFrame)

    rightSideInt = tk.Frame(master=rightSideFrame, relief=tk.GROOVE)
    rightSideInt.pack()
    self.heightText = tk.StringVar()
    self.widthText = tk.StringVar()
    self.heightEntry = tk.Entry(width=5, master=rightSideInt, textvariable=self.heightText)
    self.widthEntry = tk.Entry(width=5, master=rightSideInt, textvariable=self.widthText)
    self.widthEntry.insert(tk.END,self.gridWidth)
    self.widthEntry.bind('<FocusOut>', lambda xx: self.updateColumns(self.widthText))
    self.heightEntry.insert(tk.END,self.gridHeight)
    self.heightEntry.bind('<FocusOut>', lambda xx: self.updateRows(self.heightText))

    tk.Label(width=10, text='Height', master=rightSideInt).pack()
    self.heightEntry.pack()
    tk.Label(width=10, text='Width', master=rightSideInt).pack()
    self.widthEntry.pack()
    self.runButton.pack()
    self.resetButton.pack()
    self.clearButton.pack()

    self.mapGrid = tk.Frame()



  def paint_set_open(self, node):
    coordinate = node.getCell()
    button = self.mapGrid.grid_slaves(coordinate[0], coordinate[1])[0]
    button.change_color(self._OPENSETCOLOR)
    self._coloredCells.add(button)

  def paint_set_closed(self, set):
    for i in set:
      self.paint_closed(i)

  def paint_closed(self, coordinate):
    self.mapGrid.grid_slaves(coordinate[0], coordinate[1])[0].change_color(self._CLOSEDSETCOLOR)
    self._coloredCells.add(self.mapGrid.grid_slaves(coordinate[0], coordinate[1])[0])

  def paint_path(self,coordinateSets):
    for coord in coordinateSets:
      self.mapGrid.grid_slaves(coord[0], coord[1])[0].change_color(self._PATHCOLOR)
      self._coloredCells.add(self.mapGrid.grid_slaves(coord[0], coord[1])[0])




  #Runs the A* Pathfinding function and updates the GUI accordingly.
  def runAstar(self):
    if self.startP == None or self.endP == None:
      tk.messagebox.showerror('No Start or Goal', 'Start point or end point not set')
      return
    self.runButton.config(state=tk.DISABLED)
    if self._stop:
      return

    path = self.asG.get_next_steps()
    opens = self.asG.getNewOpens()
    closed = self.asG.getNewClosed()
    for i in opens:
      self.paint_set_open(opens[i])
    self.paint_set_closed(closed)
    if path==-1:
      messagebox.showerror('Error', 'No path found')
      return
    elif path:
      self.paint_path(path)
      self.stop=False
      return

    #We add the delay for visual effects.
    self.window.after(20, lambda: self.runAstar())





  #Function that determines what happens when a button is clicked. This depends on what the current status of the button is.
  #Updates the grid on whether the selected cell is a wall or a path, and colors the cell accordingly.
  def gridButtonClick(self, event, row, col, button):
    if button.cget('background') == self._OPENCOLOR:
      self._aStarGrid[row, col] = 0
      self._state=CellState.TURNWALLON
      button.change_color(self._WALLCOLOR)
    elif button.cget('background') == self._WALLCOLOR:
      self._aStarGrid[row, col] = 1
      button.change_color(self._OPENCOLOR)
      self._state = CellState.TURNWALLOFF
    else:
      if button.cget('background') == self._STARTCOLOR:
        self.startP = None
      elif button.cget('background') == self._GOALCOLOR:
        self.endP = None
      self._aStarGrid[row, col] = 1
      button.change_color(self._OPENCOLOR)
      self._state = CellState.TURNWALLOFF


  #Because the enter event doesnt fire when the mouse is clicked, we create our own event.
  def drag(self, event):
      widget = event.widget.winfo_containing(event.x_root, event.y_root)
      if self.current_button != widget:
          self.current_button = widget
          self.current_button.event_generate("<<B1-PressedEnter>>")

  #This function is for the case when you click over one cell, and dont let go but go over multiple cells. If you turned a cell into a wall, it turns all cells the mouse went over into a wall. Keeps from having to click each tiny square.
  def gridButtonDrag(self, event, row, col, button):
    if self._state == CellState.TURNWALLON:
      self._aStarGrid[row, col] = 0
      button.change_color(self._WALLCOLOR)
    elif self._state == CellState.TURNWALLOFF:
      self._aStarGrid[row, col] = 1
      button.change_color(self._OPENCOLOR)



  #Double-right click changes the goal cell.
  def gridButtonDoubleClickR(self, event, row, col, button):
    if button.cget('background') == self._STARTCOLOR:

      #If it was a double click we revert the old start cell and change the 'new' start cell to a goal cell.

      self.startP = self.placeholderStartP
      if self.endP:
        self.mapGrid.grid_slaves(self.endP[0], self.endP[1])[0].change_color(self._OPENCOLOR)
      self.endP = (row, col)
      if self.startP:
        self.mapGrid.grid_slaves(self.startP[0], self.startP[1])[0].change_color(self._STARTCOLOR)
      button.change_color(self._GOALCOLOR)



  #Function that is called when right clicked. Changes the start cell.
  def gridButtonClickR(self, event, row, col, button):
    if button.cget('background') != self._STARTCOLOR and button.cget('background') != self._GOALCOLOR:

      #Changes the old start cell to a regular path cell.
      self._aStarGrid[row, col] = 1
      if self.startP:
        self.mapGrid.grid_slaves(self.startP[0], self.startP[1])[0].change_color(self._OPENCOLOR)
      #We remember the old start just in case this was supposed to be a double click and we can revert the start cell.
      self.placeholderStartP = self.startP
      self.startP = (row, col)
      button.change_color(self._STARTCOLOR)

  def resetStop(self):
    self._stop = False


  #Function that clears the grid of all excess colors
  def clearGrid(self):
    for button in self._coloredCells:
      button.change_color(self._OPENCOLOR)
    self.mapGrid.grid_slaves(self.startP[0], self.startP[1])[0].change_color(self._STARTCOLOR)
    self.mapGrid.grid_slaves(self.endP[0], self.endP[1])[0].change_color(self._GOALCOLOR)
    self._stop=True
    self._coloredCells = set()
    self.asG = astar.AStarCalc(self._aStarGrid, start=self.startP, goal=self.endP, diagnoal = True)
    self.runButton.config(state=tk.NORMAL)
    self.window.after(25, self.resetStop)

  def release(self,e):
    self._state=None
    self.current_button = None



  #Function that adds rows to the grid.
  def addRows(self, rowToAdd):
    self._aStarGrid=np.vstack((self._aStarGrid, np.ones((rowToAdd, self.gridWidth))))
    for i in range(self.gridHeight, self.gridHeight+rowToAdd):
      for j in range(self.gridWidth):
        button=self.createGridButton(i, j)
        button.change_color(self._OPENCOLOR)
    self.gridHeight += rowToAdd




  #Function that add columns to the grid.
  def addColumns(self, columnsToAdd):
    self._aStarGrid=np.hstack((self._aStarGrid, np.ones((self.gridHeight, columnsToAdd))))
    for i in range(self.gridHeight):
      for j in range(self.gridWidth, self.gridWidth+columnsToAdd):
        button=self.createGridButton(i, j)
        button.change_color(self._OPENCOLOR)
    self.gridWidth += columnsToAdd



  def resetStartAndEndIfNeeded(self):
    if self.startP[0] >= self.gridHeight:
      if self.endP == (0,0):
        self.startP = (0,1)
      else:
        self.startP = (0,0)
      self.mapGrid.grid_slaves(self.startP[0], self.startP[1])[0].change_color(self._STARTCOLOR)

    if self.endP[1] >= self.gridHeight:
      if self.startP == (self.gridHeight-1,self.gridWidth-1):
        self.endP = (self.gridHeight-1,self.gridWidth-2)
      else:
        self.endP = (self.gridHeight-1,self.gridWidth-1)
      self.mapGrid.grid_slaves(self.endP[0], self.endP[1])[0].change_color(self._GOALCOLOR)
    if self.startP[1] >= self.gridWidth:
      if self.endP == (0,0):
        self.startP = (0,1)
      else:
        self.startP = (0,0)
      self.mapGrid.grid_slaves(self.startP[0], self.startP[1])[0].change_color(self._STARTCOLOR)

    if self.endP[1] >= self.gridWidth:
      if self.startP == (self.gridHeight-1,self.gridWidth-1):
        self.endP = (self.gridHeight-1,self.gridWidth-2)
      else:
        self.endP = (self.gridHeight-1,self.gridWidth-1)
      self.mapGrid.grid_slaves(self.endP[0], self.endP[1])[0].change_color(self._GOALCOLOR)

  #Function that deletes excess rows from both the numpy array and grid.
  #Adjusts the start and goal points if necessary
  def removeRows(self, newMaxRow):
    self._aStarGrid = self._aStarGrid[0:newMaxRow, :]
    self.gridHeight = newMaxRow
    self.resetStartAndEndIfNeeded()
    for label in self.mapGrid.grid_slaves():
      if int(label.grid_info()["row"]) >=self.gridHeight:
        label.grid_forget()


  #Function that deletes excess columns from both the numpy array and grid.
  #Adjusts the start and goal points if necessary
  def removeColumns(self, newMaxCol):
    self._aStarGrid = self._aStarGrid[:, 0:newMaxCol]
    self.gridWidth = newMaxCol
    self.resetStartAndEndIfNeeded()
    for label in self.mapGrid.grid_slaves():
      if int(label.grid_info()["column"]) >=self.gridWidth:
        label.grid_forget()



  def updateRows(self, textV):
    text = textV.get()
    if text.isnumeric():
      row = int(text)
      if row == self.gridHeight:
        return
      elif row < self.gridHeight:
        self.removeRows(row)
      else:
        self.addRows(row-self.gridHeight)
    else:
      self.heightEntry.delete(0, tk.END)
      self.heightEntry.insert(0, str(self.gridHeight))

  def updateColumns(self, textV):
    text = textV.get()
    if text.isnumeric():
      col = int(text)
      if col == self.gridWidth:
        return
      elif col < self.gridWidth:
        self.removeColumns(col)
      else:
        self.addColumns(col-self.gridWidth)
    else:
      self.widthEntry.delete(0, tk.END)
      self.widthEntry.insert(0, str(self.gridWidth))

  #Function that creates the button to be put on frame.
  def createGridButton(self, row, column):
    button = PathButton(master=self.mapGrid, width=10, height=10)
    button.bind("<Button-1>", lambda e, row =row, column=column, button=button: self.gridButtonClick(e,row, column, button))
    button.bind("<Button-2>", lambda e, row =row, column=column,  button=button: self.gridButtonClickR(e,row, column, button))
    button.bind("<Button-3>", lambda e, row =row, column=column,  button=button: self.gridButtonClickR(e,row, column, button))
    button.bind("<Double-Button-2>", lambda e, row =row, column=column,  button=button: self.gridButtonDoubleClickR(e,row, column, button))
    button.bind("<Double-Button-3>", lambda e, row =row, column=column,  button=button: self.gridButtonDoubleClickR(e,row, column, button))
    button.bind("<B1-Motion>", self.drag)
    button.bind("<<B1-PressedEnter>>", lambda e, row =row, column=column,  button=button: self.gridButtonDrag(e,row, column, button))
    button.bind("<ButtonRelease-1>", self.release)
    button.grid(row =row, column=column, padx=1, pady=1)
    return button


  def drawGrid(self):
    for i in range(self.gridHeight):
      for j in range(self.gridWidth):
        button = self.createGridButton(i, j)
        if i == 0 and j == 0:
          button.change_color(self._STARTCOLOR)
        elif i == self.gridWidth-1 and j == self.gridHeight-1:
          button.change_color(self._GOALCOLOR)
        else:
          button.change_color(self._OPENCOLOR)

    col_count, row_count = self.mapGrid.grid_size()

    for col in range(col_count):
        self.mapGrid.grid_columnconfigure(col, minsize=10, weight=1)

    for row in range(row_count):
        self.mapGrid.grid_rowconfigure(row, minsize=10, weight=1)


    self.runButton.config(command=self.runAstar)
    self.clearButton.config(command=self.clearGrid)

    self.mapGrid.pack()

  def run(self):
    self.drawGrid()
    self.window.mainloop()
