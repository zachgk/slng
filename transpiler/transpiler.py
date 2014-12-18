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
            g.addEdge( {p['binding']}.union({x for x in g.nodes if x in p['expression'] }),expr )
    return g

def getVarGraph(variables,code,typeGraphs):
    g = Hypergraph()
    varGraphs = {v:Subgraph(typeGraphs[code['vars'][v]['type']],g).setName(v) for v in variables}
    g.nodes = set(varGraphs.values())
    for v in variables:
        for prop,expr in code['vars'][v]['expressions'].items():
            e = set()
            for x in variables:
                if (x+'.') in expr:
                    e.add(varGraphs[x])
            e.add(varGraphs[v])
            if prop not in varGraphs[v].graph.nodes: Error("Variable " + v + " does not have property " + prop)
            fullExpr = v + "." + prop + "=" + expr
            g.addEdge(e,fullExpr)
    return g

def fileParse(f, varGraph):
    if f['input']:
        for e in f['expressions']:    
            pass
    if f['output']:
        for e in f['expressions']:    
            comp.fileOutput(f['filename'],N(exprParser.parse(e, main=varGraph)))

with open('code.json') as f:
    comp = Composer()
    code = json.loads(f.readline())
    variables = code['vars'].keys()
    types = code['types'].keys()
    typeGraphs = {t:typeGraph(t,code) for t in types}
    varGraph= getVarGraph(variables,code,typeGraphs)
    if 'files' in code:
        for f in code['files']:
            fileParse(f,varGraph)
    if 'output' in code:
        for o in code['output']:
            comp.output(N(exprParser.parse(o, main=varGraph)))
    comp.composeFile("code.cpp")
