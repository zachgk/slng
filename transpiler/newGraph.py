from collections import deque, namedtuple
from expr import *
from common import *
import re

def absEdge(edge, path):
    nodes = set()
    for n in edge.nodes:
        if type(n) is NodeRef:
            nodes.add(n)
        elif type(n) is Node:
            nodes.add(NodeRef(n,path))
        else:
            Error("unknown type of node for neighbors: " + str(type(n)))
    return edge._replace(nodes=frozenset(nodes))

def neighborEdges(nodeRef):
    parentage = set()
    path = tuple(nodeRef.parents)
    for i in range(len(path)):
        last = path[-1]
        path = path[:-1]
        parentage = parentage.union({absEdge(e,path) for e in last.graph.edges if nodeRef in e.nodes})
    ne = {absEdge(e,nodeRef.parents) for e in nodeRef.node.graph.edges if nodeRef.node in e.nodes}
    return parentage.union(ne)

def neighbors(nodeRef):
    edges = neighborEdges(nodeRef)
    nodes = {n for e in edges for n in e.nodes}
    nodes.discard(nodeRef)
    return nodes
    
def tree(nodeRef):
    visited = {nodeRef}
    queue = deque([(nodeRef,list())])
    t = {nodeRef: dict()}
    while len(queue) > 0:
        nr, path = queue.popleft()
        nbrs = neighbors(nr)
        nbrs = nbrs.difference(visited)
        visited = visited.union(nbrs)
        lt = t
        for p in path: lt = lt[p]
        lt[nr] = dict()
        newPath = path.copy()
        newPath.append(nr)
        for n in nbrs:
            queue.append((n,newPath))
    return t

def getSubs(nodeRef):
    s = nodeRef.node.name
    subs = [s]
    path = tuple(nodeRef.parents)
    for i in range(len(path)):
        last = path[-1]
        path = path[:-1]
        s = last.nodeGraph.name + '.' + s
        subs.append(s)
    full = subs[-1]
    return {x:full for x in subs[:-1] }

def treeCompute(nodeRef):
    t = tree(nodeRef)
    res = treeComputeRec(nodeRef,t)
    if res is None: Error("Could not compute " + str(nodeRef))
    return res

def treeComputeRec(root, tree):
    ne = neighborEdges(root)
    rootCycles = {e for e in ne if len(e.nodes)==1}
    if len(rootCycles) > 0:
        return list(rootCycles)[0].equation
    else:
        for r,t in tree.items():
            rec = treeComputeRec(r,t)
            if rec is not None:
                edge = [e for e in ne if r in e.nodes and root in e.nodes][0]
                exprs = {rec,edge.equation}
                subs = dict( list(getSubs(r).items()) + list(getSubs(root).items()) )
                return exprParser.solve(exprs,root,subs=subs)
    return None


class Hypergraph:
    def __init__(self):
        self.nodes = set()
        self.edges = set()

Node = namedtuple('Node', 'graph name')
Edge = namedtuple('Edge', 'nodes equation')
NodeRef = namedtuple('NodeRef', 'node parents')
NodeGraph = namedtuple('NodeGraph','name graph parent')
RefParent = namedtuple('RefParent','graph nodeGraph')

h = Hypergraph()
a = Node(graph=h,name='a')
b = Node(graph=h,name='b')
c = Node(graph=h,name='c')
d = Node(graph=h,name='d')
h.nodes.add(a)
h.nodes.add(b)
h.nodes.add(c)
h.nodes.add(d)

e1 = Edge(nodes=frozenset({a,b}),equation='a=2*b')
e2 = Edge(nodes=frozenset({a,c}),equation='c=4*a')
e3 = Edge(nodes=frozenset({b,d}),equation='d=4*b')
h.edges.add(e1)
h.edges.add(e2)
h.edges.add(e3)

i = Hypergraph()
j = Hypergraph()
x = Node(graph=i,name='x')
y = Node(graph=i,name='y')
z = Node(graph=i,name='z')
e4 = Edge(nodes=frozenset({x,y}),equation='x=9*y')
e5 = Edge(nodes=frozenset({x,z}),equation='x=2*z')
i.edges.add(e4)
i.edges.add(e5)

m = Node(graph=j,name='m')
n = Node(graph=j,name='n')
e6 = Edge(nodes=frozenset({m,n}),equation='m=3*n')
j.edges.add(e6)

xyz = NodeGraph(name='xyz',graph=i,parent=h)
e7 = Edge(nodes=frozenset({a,NodeRef(node=x,parents=(RefParent(h,xyz),))}),equation='a=2*x')
h.nodes.add(xyz)
h.edges.add(e7)

selfEdge = Edge(nodes=frozenset({z}),equation='z=5')
i.edges.add(selfEdge)

aRef = NodeRef(node=a,parents=tuple() )
print(treeCompute(aRef))

xRef = NodeRef(node=x,parents=(RefParent(h,xyz),))
# print(neighborEdges(xRef))
