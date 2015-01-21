import json
import hypergraph
from expr import exprParser
from compose import Composer
from common import *

def typeGraph(t, code):
    g = hypergraph.Hypergraph()
    definition = code['types'][t]
    g.nodes = {hypergraph.Node(name=p['binding'],graph=g) for p in definition['properties']}
    for p in definition['properties']:
        if 'expression' in p:
            expr = p['binding'] + "=" + p['expression']
            edgeVars = exprParser.parse(expr,equation=True,returnVars=True)
            edgeNodes = {hypergraph.Node(name=n,graph=g) for n in edgeVars}
            for n in edgeNodes:
                if n not in g.nodes and '(' not in n.name: Error(n.name + ' is not defined in type ' + t)
            g.edges.add(hypergraph.Edge(nodes=frozenset(edgeNodes),equation=expr))
    return g

def getSubEdge(expr, varGraph):
    parse = exprParser.parse(expr,equation=True,returnVars=True)
    nodes = set()
    for e in parse:
        if '.' in e:
            nodes.add(varGraph.fromDotRef(e))
        else:
            nodes.add(hypergraph.Node(name=e,graph=varGraph))
    edge = hypergraph.Edge(nodes=frozenset(nodes),equation=expr)
    return edge
    

def getVarGraph(variables,code,typeGraphs):
    g = hypergraph.Hypergraph()
    varGraphs = {v:hypergraph.NodeGraph(name=v,graph=typeGraphs[code['vars'][v]['type']],parent=g) for v in variables}
    g.nodes = set(varGraphs.values())
    for v in variables:
        for prop,expr in code['vars'][v]['expressions'].items():
            fullExpr = v + "." + prop + "=" + expr
            edge = getSubEdge(fullExpr,g)
            if varGraphs[v].graph.getNode(prop) is None: Error("Variable " + v + " does not have property " + prop)
            g.edges.add(edge)
    return g

def fileParse(f, varGraph, comp):
    if f['input']:
        exp_iter = iter(f['expressions'])
        for e in exp_iter:
            if type(e) is str:
                ref = comp.fileReadNumber(f['filename'])
                n = hypergraph.Node(name=ref,graph=varGraph)
                varGraph.nodes.add(n)
                fullExpr = ref + "=" + e
                edge = getSubEdge(fullExpr,varGraph)
                varGraph.edges.add(edge)
            else:
                terminator = next(exp_iter)
                ref = comp.fileReadUntil(f['filename'],terminator)
                n = hypergraph.Node(name=ref,graph=varGraph)
                varGraph.nodes.add(n)
                fullExpr = ref + "=" + e['prop']
                edge = getSubEdge(fullExpr,varGraph)
                varGraph.edges.add(edge)
        for i in range(len(f['expressions'])):
            e = f['expressions'][i]
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
