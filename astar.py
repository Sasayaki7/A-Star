import numpy as np

#Node object that keeps track of the f, g, h values of each point and the node that it came from
class Node():

  #Constructor. We define h in here as well, and provide default values for f and g.
  def __init__(self, current, f=0, g=0, prev=(0,0)):
    #f, g and h are all made private because if any of these are set from the outside it can mess up the value of h
    self._f = f
    self._g = g
    self._h = f+g
    self.prev = prev
    self.current = current

  def get_h(self):
    return self._h

  def get_f(self):
    return self._f

  #Changes the f value.
  def set_f(self, f):
    self._f = f
    #Because the h value is reliant on f, we change this in the method as well
    self._h = f+self._g

  #Changes the g value
  def set_g(self, g):
    self._g = g
    #Because the h value is reliant on g, we change this as well in this method
    self._h = g+self._f

  def get_g(self):
    return self._g

  def setPrev(self, p):
    self.prev = p

  def getPrev(self):
    return self.prev

  def getCell(self):
    return self.current

#The A Star Calculator is an object that runs the calculation, one at a time.
class AStarCalc():
  def __init__(self, grid, start=(0,0), goal=(9,9), diagnoal = False):
    self.grid = grid
    self.closed = {}
    self.start = start
    self.changedClosed={}
    self.changedOpen = {}
    self.goal = goal
    self.diagnoal = diagnoal
    self.currentNode = start
    self.open = {self.start: Node(start, f=0, g=abs(goal[0]-start[0])+abs(goal[1]-start[1]))}


  #Checks if the cell is a wall, and returns a boolean value.
  def cell_is_wall(self, cell):
    if self.grid[cell] == 0:
      return True
    else:
      return False


  #Calculates the distance between two cells, multiplied by 5. If diagnoals are valid, each diagnoal distance is considered 7.
  def calc_cell_dists(self, cell1, cell2):
    if self.diagnoal:
      diag = min(abs(cell1[0]-cell2[0]), abs(cell1[1]-cell2[1]))
      return diag*7+(max(abs(cell1[0]-cell2[0]), abs(cell1[1]-cell2[1]))-diag)*5
    else:
      return (abs(cell1[0]-cell2[0])+abs(cell1[1]-cell2[1]))*5


  def calc_cell_to_goal(self, cell):
    return self.calc_cell_dists(cell, self.goal)


  #Checks cells adjacent to the cell specified in parameter, and returns all cells which are open to explore in a list.
  def get_adjacent_open_spaces(self, cell):
    cells = [(cell[0]+1, cell[1]), (cell[0], cell[1]-1), (cell[0]-1, cell[1]), (cell[0], cell[1]+1)]
    if self.diagnoal:
      cells+=[(cell[0]+1, cell[1]+1), (cell[0]+1, cell[1]-1), (cell[0]-1, cell[1]+1), (cell[0]-1, cell[1]-1)]


    #If the current cell is at the edge of the grid, we remove some cells that correspond to out-of-grid situations. There are four cases so there are 4 if statements.
    if cell[0] == 0:
      cells.remove((cell[0]-1, cell[1]))
      #If diagnoal cells are included, we have to remove them as well if they're invalid.
      if self.diagnoal:
        cells.remove((cell[0]-1, cell[1]+1))
        cells.remove((cell[0]-1, cell[1]-1))

    elif cell[0] == self.grid.shape[0]-1:
      cells.remove((cell[0]+1, cell[1]))
      if self.diagnoal:
        cells.remove((cell[0]+1, cell[1]+1))
        cells.remove((cell[0]+1, cell[1]-1))

    if cell[1] == 0:
      cells.remove((cell[0], cell[1]-1))
      if (cell[0]-1, cell[1]-1) in cells:
        cells.remove((cell[0]-1, cell[1]-1))
      if (cell[0]+1, cell[1]-1) in cells:
        cells.remove((cell[0]+1, cell[1]-1))

    elif cell[1] == self.grid.shape[1]-1:
      cells.remove((cell[0], cell[1]+1))
      if (cell[0]-1, cell[1]-1) in cells:
        cells.remove((cell[0]-1, cell[1]+1))
      if (cell[0]+1, cell[1]-1) in cells:
        cells.remove((cell[0]+1, cell[1]+1))


    #If the cell is a wall, we also remove it from consideration
    retList = [c for c in cells if not self.cell_is_wall(c)]

    return retList


  #Function that traces its path from the start all the way up to the current cell, in reverse order. Returns a list of all cells visited
  def traceBack(self, c):
    cell = c
    l = [cell]
    while cell != self.start:
      if cell in self.open:
        cell = self.open[cell].getPrev()
        l.append(cell)
      else:
        cell = self.closed[cell].getPrev()
        l.append(cell)
    return l


  #Function that determines the cell with the lowest h-value. If a tie, the cell with the lowest g-value is considered.
  def get_lowest_h_cell(self):
    target = 9999999999999999
    for c in self.open.values():
      if c.get_h() < target:
        self.currentNode = c.getCell()
        target = c.get_h()

      #If h values are the same, lower g value gets priority
      elif c.get_h() == target and self.open[self.currentNode].get_g() > c.get_g():
          self.currentNode = c.getCell()
    return self.currentNode


  #A function that checks one set of cells in the open Set, checks adjacent cells if they are open, calculate h values, and adds current cell in closed set. Also keeps track of the latest changes in the open/closed sets for visual purposes.
  def get_next_steps(self):
    if len(self.open.keys()) == 0:
      return -1
    self.get_lowest_h_cell()
    self.changedOpen = {}
    self.changedClosed = {}

    #Get all the adjacent cells to the lowest h-value cell and iterates through them
    cs = self.get_adjacent_open_spaces(self.currentNode)
    for c in cs:

      #Creates a new node with the given information
      newNode = Node(c, f=self.open[self.currentNode].get_f()+self.calc_cell_dists(self.currentNode, c), g=self.calc_cell_to_goal(c), prev=self.currentNode)

      #If its the goal we return the entire tracing up to that node.
      if c == self.goal:
        self.open[c] = Node(c, prev=self.currentNode)
        return self.traceBack(c)

      #If the cell has been previously opened we make sure that we didn't get to it in a lower-cost fashion
      if c in self.open:
        if self.open[c].get_h() > newNode.get_h():
          self.open[c] = newNode

      #IF the cell has already been closed we ignore it. Otherwise we add it to the set of cells (and newcell)
      elif c in self.closed:
        continue
      else:
        self.open[c] = newNode
        self.changedOpen[c] = newNode

    #Then we add the node we investigated into the closed set, and remove the node from the open set.
    self.closed[self.currentNode] = self.open[self.currentNode]
    self.changedClosed[self.currentNode] = self.open[self.currentNode]
    del self.open[self.currentNode]
    return None

  def run(self):
    pass

  def getOpens(self):
    return self.open

  def getClosed(self):
    return self.closed

  def getNewOpens(self):
    return self.changedOpen

  def getNewClosed(self):
    return self.changedClosed
