from collections import deque
from expr import *
import re

class Hypergraph:

    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def __str__(self): 
        return str((self.nodes,self.edges))

    def getNode(self, name):
        for n in self.nodes:
            if type(n) is Subgraph and n.name == name: return n
            elif n == name: return n
        return None
            

    def addEdge(self,nodes,data):
        self.edges.add((frozenset(nodes),data))

    def completelyConnected(self,nodes, edges=-1):
        if edges == -1: edges = self.edges
        links = {e for e in edges if frozenset(nodes)==e[0] }
        return len(links) == len(nodes)-1
        
    def neighborEdges(self, node, complete=False):
        neighbors = {e for e in self.edges if node in e[0]}
        if complete: return {e for e in neighbors if self.completelyConnected(e[0])}
        else: return neighbors

    def neighbors(self, node, complete=False):
        edges = self.neighborEdges(node,complete=complete)
        neighbors = set()
        for e in edges:
            neighbors = neighbors.union(e[0])
        neighbors.discard(node)
        return neighbors

    def tree(self, start, complete = False, graph=None):
        if graph is None: graph = self
        t = {Node(start,graph): dict() }
        nodes = {graph: self.nodes}
        queue = deque([(start,[],graph)])
        nodes[graph].discard(start)
        while(len(queue)>0):
            node, path, g = queue.popleft()
            neighbors = g.neighbors(node,complete=complete)
            neighbors = neighbors.intersection(nodes[g])
            nodes[g] = nodes[g].difference(neighbors)
            nodes[g].discard(node)
            lt = t
            for p in path: lt = lt[p]
            absNode = Node(node,g)
            lt[absNode] = dict()
            newPath = path.copy()
            newPath.append(absNode)
            for n in neighbors:
                if type(n) is Node:
                    queue.append( (n.name,newPath,n.graph) )
                    if n.graph not in nodes: nodes[n.graph] = n.graph.graph.nodes
                else:
                    queue.append( (n,newPath,g) )
        return t

    def treeCompute(self, start, graph=None):
        if graph is None: graph = self
        t = self.tree(start, complete=True, graph=graph)
        return self.treeComputeRec(Node(start,graph),t)

    def treeComputeRec(self, root, tree):
        ne = root.graph.neighborEdges(root.name,complete=False)
        rootCycles = {e for e in ne if e[0]==frozenset({root.name}) }
        if len(rootCycles) == 1:
            return list(rootCycles)[0][1]
        else:
            for r,t in tree.items():
                rec = self.treeComputeRec(r,t)
                if rec is not None:
                    edge = {e for e in ne if r.name in e[0] and root.name in e[0]}
                    exprs = {rec,list(edge)[0][1]}
                    subs = {
                        r.name: r.graph.name + "." + r.name,
                        root.name: root.graph.name + "." + root.name
                    }
                    return exprParser.solve(exprs,root,subs=subs)
        return None


class Subgraph:
    def __init__(self,graph,parent):
        self.graph = graph
        self.parent = parent

    def setName(self,name):
        self.name = name
        return self

    def addExternal(self,complete=False):
        edges = self.parent.neighborEdges(self,complete=complete)
        self.externalNodes = set()
        self.externalEdges = set()
        for e in edges:
            rexpr = re.compile(self.name + "\.[a-zA-Z]+")
            newNodes = {s[2:] for s in rexpr.findall(e[1]) }
            for n in e[0]:
                if n == self: continue
                elif type(n) is Subgraph:
                    rexpr = re.compile(n.name + "\.[a-zA-Z]+")
                    for x in rexpr.findall(e[1]):
                        newNodes.add(Node(x[2:],n))
                else:
                    newNodes.add(Node(n,self.parent))
            self.externalEdges.add((frozenset(newNodes),e[1]))
            self.externalNodes = self.externalNodes.union(newNodes)
        self.graph.edges = self.graph.edges.union(self.externalEdges)
        self.graph.nodes = self.graph.nodes.union(self.externalNodes)

    def removeExternal(self):
        self.graph.edges = self.graph.edges.difference(self.externalEdges)
        self.graph.nodes = self.graph.nodes.difference(self.externalNodes)
        

    def tree(self, start, complete=False):
        self.addExternal(complete=complete)
        t = self.graph.tree(start, complete=complete)
        self.removeExternal()
        return t

    def treeCompute(self, start):
        self.addExternal(complete=True)
        t = self.graph.treeCompute(start, graph=self)
        self.removeExternal()
        return t

    def neighbors(self, node, complete=False):
        self.addExternal(complete=complete)
        n = self.graph.neighbors(node,complete=complete)
        self.removeExternal()
        return n

    def neighborEdges(self, node, complete=False):
        self.addExternal(complete=complete)
        n = self.graph.neighborEdges(node,complete=complete)
        self.removeExternal()
        return n
        


class Node:
    def __init__(self, name, graph):
        self.name = name
        self.graph = graph
