import json
import hypergraph
from expr import exprParser
from compose import compose
from collector import Collector
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

def getSubEdge(expr, varGraph, subs=dict()):
    parse = exprParser.parse(expr,equation=True,returnVars=True, subs=subs)
    nodes = set()
    for e in parse:
        if '.' in e:
            nodes.add(varGraph.fromDotRef(e))
        else:
            nodes.add(hypergraph.Node(name=e,graph=varGraph))
    edge = hypergraph.Edge(nodes=frozenset(nodes),equation=expr)
    expr = applySubs(expr, subs)
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


def parseOutputLines(expressions, varGraph, collector):
    stream = list()
    for e in expressions:
        if type(e) is str:
            print("fixed output stream")
            stream.append("1")
            # stream.append(collector.outExpr(exprParser.parse(e, main=varGraph)))
        else:
            if 'prop' in e:
                print(e)
                Error('Print list of elements')
            else:
                stream.append(collector.outOver(parseOutputLines(e['expressions'], varGraph, collector)))
    return stream

    

def parseExprLines(expressions, varGraph, typeGraphs, collector, parentGraph=None, subs=dict()):
    if parentGraph is None: parentGraph = varGraph
    stream = list()
    exp_iter = iter(expressions)
    for e in exp_iter:
        if type(e) is str:
            ref, op = collector.readFile(collector.readAtom())
            n = hypergraph.Node(name=ref,graph=parentGraph)
            parentGraph.nodes.add(n)
            fullExpr = ref + "=" + e
            edge = getSubEdge(fullExpr,varGraph, subs=subs)
            parentGraph.edges.add(edge)
            stream.append(op)
        else:
            if 'prop' in e:
                terminator = next(exp_iter)
                ref, op = collector.readFile(collector.readUntil(terminator))
                n = hypergraph.Node(name=ref,graph=parentGraph)
                parentGraph.nodes.add(n)
                fullExpr = ref + "=" + applySubs(e['prop'],subs)
                edge = getSubEdge(fullExpr,varGraph, subs=subs)
                parentGraph.edges.add(edge)
                stream.append(op)
            else:
                subs[e['loopRef']] = e['loopVar']
                elements = parseExprLines(e['expressions'], varGraph, typeGraphs, collector, subs=subs)
                print(e)
                print(elements)
                Error("Set parse")
                temp = collector.tempDispenser()
                tempGraph = parentGraph.getNode(e['loopVar']).graph
                tn = hypergraph.NodeGraph(name=temp, graph=tempGraph, parent=parentGraph)
                parentGraph.nodes.add(tn)
                g = hypergraph.Hypergraph()
                subs[e['loopRef']] = temp
                elements = parseExprLines(e['expressions'], varGraph, typeGraphs, collector, parentGraph=g, subs=subs)
                ref, op = collector.readFile(collector.readOver(elements))
                n = hypergraph.NodeGraph(name=ref, graph=g, parent=parentGraph)
                parentGraph.nodes.add(n)
                stream.append(op)
    return stream
    

def fileParse(f, varGraph, typeGraphs, collector):
    if f['input']:
        collector.inputFile(f['filename'], parseExprLines(f['expressions'], varGraph, typeGraphs, collector))
    if f['output']:
        for e in f['expressions']:    
            collector.outputFile(f['filename'], parseOutputLines(f['expressions'], varGraph, collector))

with open('code.json') as f:
    collector = Collector()
    code = json.loads(f.readline())
    variables = code['vars'].keys()
    types = code['types'].keys()
    typeGraphs = {t:typeGraph(t,code) for t in types}
    varGraph= getVarGraph(variables,code,typeGraphs)
    if 'files' in code:
        for f in code['files']:
            fileParse(f,varGraph, typeGraphs, collector)
    if 'output' in code:
        collector.outputStandard(parseOutputLines(code['output'], varGraph, collector))
    cpp = compose(collector)
    with open("code.cpp", 'w') as f:
        f.write(cpp)
