import numpy as np
from sympy import Matrix
from node import Resistor, Battery, Junction
class Circuit:
  def __init__(self, components):
    self.components = list(components) # TODO put junctions at the end
    self.current_count = len([0 for i in self.components if not isinstance(i, Junction)])
    self.equiv_vecs = []
    self.loop_vecs = []
    self.junction_vecs = []
  def add_connection(self, component_from, component_to):
    if component_from not in self.components or component_to not in self.components:
      raise Exception
    component_from.out_connections.append(component_to)
    component_to.in_connections.append(component_from)
    # if neither is a junction, they should have the same current
    if not isinstance(component_from, Junction) and not isinstance(component_to, Junction):
      vec = np.zeros(self.current_count+1)
      vec[self.components.index(component_from)] = -1
      vec[self.components.index(component_to)] = 1
      self.equiv_vecs.append(vec)
  def add_connections(self, connections):
    for f, t in connections:
      self.add_connection(f, t)
  def to_undirected_adjacency_list(self):
    adj_list = [[] for i in range(len(self.components))]
    for i in range(len(self.components)):
      for connected_component in self.components[i].in_connections:
        adj_list[i].append(self.components.index(connected_component))
      for connected_component in self.components[i].out_connections:
        adj_list[i].append(self.components.index(connected_component))
    return adj_list
  def find_loops(self):
    adj_list = self.to_undirected_adjacency_list()
    root = 0
    loops = []
    def dfs(current_node, past_nodes, adj_list):
      past_nodes.append(current_node)
      # print past_nodes
      for next_node in adj_list[current_node]:
        if next_node not in past_nodes:
          dfs(next_node, past_nodes, adj_list) 
      if root in adj_list[current_node] and len(past_nodes) > 2:
        loops.append(map(lambda i: self.components[i], past_nodes))
      past_nodes.remove(current_node)
    dfs(root, [], adj_list)
    return loops
  def load_loop_equations(self):
    for loop in self.find_loops():
      vec = np.zeros(self.current_count+1)
      for i in range(len(loop)):
        if isinstance(loop[i], Resistor):
          if loop[i-1] in loop[i].in_connections: # if loop goes in same direction as current
            vec[self.components.index(loop[i])] = loop[i].resistance
          else:
            vec[self.components.index(loop[i])] = -loop[i].resistance
            pass# voltage drop is positive
        elif isinstance(loop[i], Battery):
          if loop[i-1] in loop[i].in_connections: # if loop goes in same direction as current
            vec[-1] += loop[i].voltage
          else:
            vec[-1] -= loop[i].voltage
            pass# voltage drop is positive
      self.loop_vecs.append(vec)
  def load_junction_equations(self):
    for junction in self.components:
      if isinstance(junction, Junction):
        vec = np.zeros(self.current_count+1)
        for in_comp in junction.in_connections:
          vec[self.components.index(in_comp)] = -1
        for out_comp in junction.out_connections:
          vec[self.components.index(out_comp)] = 1
        self.junction_vecs.append(vec)
  def solve(self):
    self.load_loop_equations()
    self.load_junction_equations()
    rref_mat, pivots = Matrix(self.junction_vecs + self.equiv_vecs + self.loop_vecs).rref()
    for i in range(self.current_count):
      print '%s has current %.3f'%(self.components[i], rref_mat[i,-1])
def main():
  b1 = Battery(10, name='battery_1')
  b2 = Battery(20, name='battery_2')
  r1 = Resistor(1, name='r1')
  r2 = Resistor(2, name='r2')
  r3 = Resistor(3, name='r3')
  # assume junctions at the end
  jb = Junction(name='junction_b')
  ja = Junction(name='junction_a')
  circuit = Circuit([b1,b2,r1,r2,r3,ja,jb])
  circuit.add_connections([
    (b1, r1),
    (r1, ja),
    (b2, r2),
    (r2, ja),
    (ja, r3),
    (r3, jb),
    (jb, b2), 
    (jb, b1)
  ])
  circuit.solve()


main()
