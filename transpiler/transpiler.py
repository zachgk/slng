import json
from hypergraph import *

def typeGraph(t, code):
    g = Hypergraph()
    definition = code['types'][t]
    g.nodes = {p['binding'] for p in definition['properties']}
    for p in definition['properties']:
        if 'expression' in p:
            g.addEdge( {p['binding']}.union({x for x in g.nodes if x in p['expression'] }),2 )
    return g

def getVarGraph(variables,code,typeGraphs):
    g = Hypergraph()
    varGraphs = {v:Subgraph(typeGraphs[code['vars'][v]['type']],g).setName(v) for v in variables}
    g.nodes = set(varGraphs.values())
    for v in variables:
        e = set()
        for x in variables:
            if (x+'.') in list(code['vars'][v]['expressions'].values())[0]:
                e.add(varGraphs[x])
        if(len(e)>0):
            e.add(varGraphs[v])
            g.addEdge(e,2)
    return g

def evaluate(expr):
    return expr

with open('code.json') as f:
    code = json.loads(f.readline())
    variables = code['vars'].keys()
    types = code['types'].keys()
    typeGraphs = {t:typeGraph(t,code) for t in types}
    varGraph= getVarGraph(variables,code,typeGraphs)
    print(varGraph.tree(varGraph.getNode('c')))
    for o in code['output']:
        print(evaluate(o))
