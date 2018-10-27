class Node:
  def __init__(self, name='node'):
    self.name = name
    self.in_connections = []
    self.out_connections = []
  def __str__(self):
    return self.name
  def __repr__(self):
    return self.name

class Battery(Node):
  def __init__(self, voltage, name='node'):
    self.voltage = voltage
    Node.__init__(self, name)
  

class Resistor(Node):
  def __init__(self, resistance, name='node'):
    self.resistance = resistance
    Node.__init__(self, name)
  
class Junction(Node):
  pass