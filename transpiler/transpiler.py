import json
import hypergraph
from expr import exprParser
from compose import compose
from collector import Collector
from common import *

#TODO Move main graph functions to separate file
def typeGraph(t, code):
    g = hypergraph.Hypergraph()
    definition = code['types'][t]
    g.nodes = {hypergraph.Node(name=p['binding'],graph=g) for p in definition['properties']}
    for p in definition['properties']:
        if 'expression' in p:
            expr = p['binding'] + "=" + p['expression']
            edgeVars = exprParser.parse(expr,isEquation=True,returnVars=True)
            edgeNodes = {hypergraph.Node(name=n,graph=g) for n in edgeVars}
            for n in edgeNodes:
                if n not in g.nodes and '(' not in n.name: Error(n.name + ' is not defined in type ' + t)
            g.edges.add(hypergraph.Edge(nodes=frozenset(edgeNodes),equation=expr))
    return g

def getSubEdge(expr, varGraph, subs=dict()):
    parse = exprParser.parse(expr,isEquation=True,returnVars=True, subs=subs)
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


def addInputNode(op, refGraph, targetGraph, varGraph, refPath='', targetPath='', subs = dict()):
    if op['type'] == 'atom':
        n = hypergraph.Node(name=op['ref'], graph=refGraph)
        refGraph.nodes.add(n)
        target = applySubs(op['data'],subs)
        edgeExpr = refPath + op['ref'] + '=' + targetPath + target
        edge = getSubEdge(edgeExpr, varGraph)
        varGraph.edges.add(edge)
    elif op['over'] == 'type':
        subgraph = hypergraph.Hypergraph()
        n = hypergraph.NodeGraph(name=op['ref'], graph=subgraph, parent=refGraph)
        target = applySubs(op['loopVar'],subs)
        edgeExpr = refPath + op['ref'] + '=' + targetPath + target
        edge = getSubEdge(edgeExpr, varGraph)
        varGraph.nodes.add(n)
        varGraph.edges.add(edge)
        subs[op['loopRef']] = ''
        for el in op['elements']:
            addInputNode(el, subgraph, targetGraph.getNode(op['loopVar']), varGraph, refPath + op['ref'] + '.', targetPath + target + '.', subs)
    else:#op['over'] == 'prop'
        target = applySubs(op['elements'][0]['data'],subs)
        n = hypergraph.Node(name=target, graph=refGraph)
        refGraph.nodes.add(n)
        edgeExpr = refPath + target + '=' + targetPath + target
        edge = getSubEdge(edgeExpr, varGraph)
        varGraph.edges.add(edge)


#TODO Move exprline functions to separate file
#TODO check typeGraphs and other potential unused arguments in exprLine functions
#TODO Should not assume that the depth of a line['type'] is 1 (only contains an atom inside it)
def outputExprLines(expressions, varGraph, typeGraphs, collector):
    parsedLines = parseExprLines(expressions, varGraph, typeGraphs, collector)
    for line in parsedLines:
        if line['type'] == 'end':
            expr = exprParser.parse(line['elements'][0]['data'], main=varGraph, subs={line['loopRef']:line['loopVar']})
        else:
            expr = exprParser.parse(line['data'], main=varGraph)
        line['expression'] = expr
    return parsedLines


def inputExprLines(expressions, varGraph, typeGraphs, collector):
    parsedLines = parseExprLines(expressions, varGraph, typeGraphs, collector)
    for line in parsedLines:
        ref, op = collector.readFile(line)
        addInputNode(op, varGraph, varGraph, varGraph)
    return parsedLines

#TODO Rewrite the mechanism used to differentiate terminated/numbered and over prop/type
def parseExprLines(expressions, varGraph, typeGraphs, collector, parentGraph=None, subs=dict()):
    if parentGraph is None: parentGraph = varGraph
    stream = list()
    exp_iter = iter(expressions)
    for e in exp_iter:
        if type(e) is str:
            l = collector.readAtom(e)
            stream.append(l)
        else:
            if 'prop' in e: #is terminated
                terminator = next(exp_iter)
                elements = [collector.readAtom(e['prop'])]
                l = collector.readUntil(terminator, elements)
                l['over'] = 'prop'
                stream.append(l)
            else:
                subs[e['loopRef']] = e['loopVar']
                elements = parseExprLines(e['expressions'], varGraph, typeGraphs, collector, subs=subs)
                l = collector.readOver(elements)
                l['over'] = 'type'
                l['loopVar'] = e['loopVar']
                l['loopRef'] = e['loopRef']
                stream.append(l)
    return stream
    

def fileParse(f, varGraph, typeGraphs, collector):
    if f['input']:
        collector.inputFile(f['filename'], inputExprLines(f['expressions'], varGraph, typeGraphs, collector))
    if f['output']:
        for e in f['expressions']:    
            collector.outputFile(f['filename'], outputExprLines(f['expressions'], varGraph, typeGraphs, collector))

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
        collector.outputStandard(outputExprLines(code['output'], varGraph, typeGraphs, collector))
    cpp = compose(collector)
    with open("code.cpp", 'w') as f:
        f.write(cpp)
