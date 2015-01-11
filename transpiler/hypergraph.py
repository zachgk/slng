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
                rootSubs= list(getSubs(root).items())
                rSubs = list(getSubs(r).items())
                subs = dict(rootSubs + rSubs)
                if len(rootSubs) > 0:
                    goal = rootSubs[0][1]
                else:
                    goal = root.node.name
                return exprParser.solve(exprs,goal,subs=subs)
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
