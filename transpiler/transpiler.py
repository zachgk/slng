import json
from hypergraph import *
from expr import exprParser
from compose import Composer
from common import *

def typeGraph(t, code):
    g = Hypergraph()
    definition = code['types'][t]
    g.nodes = {p['binding'] for p in definition['properties']}
    for p in definition['properties']:
        if 'expression' in p:
            expr = p['binding'] + "=" + p['expression']
            edge = exprParser.parse(p['expression'],returnVars=True)
            if not edge.issubset(g.nodes): Error(str(edge.difference(g.nodes)) + " are not defined in Type " + t)
            edge.add(p['binding'])
            g.addEdge(edge ,expr )
    return g

def getSubEdge(expr, varGraph):
    parse = exprParser.parse(expr,returnVars=True)
    edgeSplit = {tuple(e.split(".")) for e in parse}
    edgeParts = {e for e in edgeSplit if e[0] in variables}
    edge = {Node(x[1],varGraph.getNode(x[0])) for x in edgeSplit}
    return edge
    

def getVarGraph(variables,code,typeGraphs):
    g = Hypergraph()
    varGraphs = {v:Subgraph(typeGraphs[code['vars'][v]['type']],g).setName(v) for v in variables}
    g.nodes = set(varGraphs.values())
    for v in variables:
        for prop,expr in code['vars'][v]['expressions'].items():
            edge = getSubEdge(expr,g)
            edge.add(Node(v,g))
            if prop not in varGraphs[v].graph.nodes: Error("Variable " + v + " does not have property " + prop)
            fullExpr = v + "." + prop + "=" + expr
            g.addEdge(edge,fullExpr)
    return g

def fileParse(f, varGraph, comp):
    if f['input']:
        for e in f['expressions']:    
            ref = comp.refDispenser()
            fullExpr = ref + "=" + e
            edge = getSubEdge(e,varGraph)
            n = Node(ref,varGraph)
            edge.add(n)
            varGraph.nodes.add(n)
            varGraph.addEdge(edge,fullExpr)
    if f['output']:
        for e in f['expressions']:    
            comp.fileOutput(f['filename'],exprParser.parse(e, main=varGraph))

with open('code.json') as f:
    comp = Composer()
    code = json.loads(f.readline())
    variables = code['vars'].keys()
    types = code['types'].keys()
    typeGraphs = {t:typeGraph(t,code) for t in types}
    varGraph= getVarGraph(variables,code,typeGraphs)
    if 'files' in code:
        for f in code['files']:
            fileParse(f,varGraph, comp)
    if 'output' in code:
        for o in code['output']:
            comp.standardOutput(exprParser.parse(o, main=varGraph))
    comp.composeFile("code.cpp")
