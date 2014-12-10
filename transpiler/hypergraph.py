class Hypergraph:
    nodes = set()
    edges = set()

    def __str__(self): 
        return str((self.nodes,self.edges))

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

    def tree(self, start, nodes = -1, complete = False):
        neighbors = self.neighbors(start,complete=complete)

        if nodes != -1: neighbors = neighbors.intersection(nodes)
        else: nodes = self.nodes

        nodes = nodes.difference(neighbors)
        nodes.discard(start)

        tree = dict()
        for n in neighbors:
            x = self.tree(n,nodes=nodes,complete=complete)
            for k in x.keys():
                tree[k] = x[k]
        return {start: tree}
