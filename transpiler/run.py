from hypergraph import *
h = Hypergraph()
h.nodes = {'a','b','c'}
h.addEdge({'a','b'},3)
h.addEdge({'a','b','c'},3)
print(h.tree('a'))
print(h.tree('a',complete=True))
