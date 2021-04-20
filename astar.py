import numpy as np

class Node():
  def __init__(self, current, f=0, g=0, prev=(0,0)):
    self.f = f
    self.g = g
    self.h = f+g
    self.prev = prev
    self.current = current

  def get_h(self):
    return self.f+self.g

  def get_f(self):
    return self.f

  def set_f(self, f):
    self.f = f
    self.h = f+self.g

  def set_g(self, g):
    self.g = g
    self.h = g+self.f

  def setPrev(self, p):
    self.prev = p

  def getPrev(self):
    return self.prev

  def getCell(self):
    return self.current


class AStarCalc():
  def __init__(self, grid, start=(0,0), goal=(9,9)):
    self.grid = grid
    self.closed = {}
    self.start = start
    self.goal = goal
    self.currentNode = start
    self.open = {self.start: Node(start, f=0, g=abs(goal[0]-start[0])+abs(goal[1]-start[1]))}

  def calc_spaces(self):
    pass


  def calc_cell_value(self, cell):
    return




  def cell_is_wall(self, cell):
    if self.grid[cell] == '0':
      return True
    else:
      return False

  def calc_cell_to_goal(self, cell):
    return abs(cell[0]-self.goal[0])+abs(cell[1]-self.goal[1])


  def get_adjacent_open_spaces(self, cell):
    cells = [(cell[0]+1, cell[1]), (cell[0], cell[1]-1), (cell[0]-1, cell[1]), (cell[0], cell[1]+1)]
    if cell[0] == 0:
      cells.remove((cell[0]-1, cell[1]))
    elif cell[0] == self.grid.shape[0]-1:
      cells.remove((cell[0]+1, cell[1]))
    if cell[1] == 0:
      cells.remove((cell[0], cell[1]-1))
    elif cell[1] == self.grid.shape[1]-1:
      cells.remove((cell[0], cell[1]+1))
    retList = [c for c in cells if not self.cell_is_wall(c)]

    return retList

  def solvePath(self, c):
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


  def get_next_steps(self):
    target = 9999999999999999
    for c in self.open.values():
      if c.get_h() < target:
        self.currentNode = c.getCell()
        target = c.get_h()
    cs = self.get_adjacent_open_spaces(self.currentNode)
    for c in cs:
      newNode = Node(c, f=self.open[self.currentNode].get_f()+1, g=self.calc_cell_to_goal(self.currentNode), prev=self.currentNode)
      if c == self.goal:
        self.open[c] = Node(c, prev=self.currentNode)
        return self.solvePath(c)
      if c in self.open:
        if self.open[c].get_h() > newNode.get_h():
          self.open[c] = newNode
      elif c in self.closed:
        continue
      else:
        self.open[c] = newNode
    self.closed[self.currentNode] = self.open[self.currentNode]
    del self.open[self.currentNode]
    return None


  def getOpens(self):
    return self.open

  def getClosed(self):
    return self.closed
