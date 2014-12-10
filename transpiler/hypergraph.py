from collections import deque

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

    def tree(self, start, complete = False):
        t = {start: dict() }
        nodes = {self: self.nodes}
        queue = deque([(start,[],self)])
        nodes[self].discard(start)
        while(len(queue)>0):
            node, path, g = queue.popleft()
            neighbors = g.neighbors(node,complete=complete)
            neighbors = neighbors.intersection(nodes[g])
            nodes[g] = nodes[g].difference(neighbors)
            nodes[g].discard(node)
            lt = t
            for p in path: lt = lt[p]
            lt[node] = dict()
            newPath = path.copy()
            newPath.append(node)
            for n in neighbors:
                queue.append( (n,newPath,g) )
        return t


class Subgraph:
    def __init__(self,graph,parent):
        self.graph = graph
        self.parent = parent

    def setName(self,name):
        self.name = name
        return self
