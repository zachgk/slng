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

def getVarGraphEdges(variables,code):
    varGraphEdges = set()
    for v in variables:
        e = set()
        for x in variables:
            if (x+'.') in list(code['vars'][v]['expressions'].values())[0]:
                e.add(x)
        if(len(e)>0):
            e.add(v)
            varGraphEdges.add(frozenset(e))
    return varGraphEdges

def evaluate(expr):
    return expr

with open('code.json') as f:
    code = json.loads(f.readline())
    variables = code['vars'].keys()
    types = code['types'].keys()
    typeGraphs = {t:typeGraph(t,code) for t in types}
    varGraphEdges = getVarGraphEdges(variables,code)
    print(typeGraphs)
    print(varGraphEdges)
    for o in code['output']:
        print(evaluate(o))
