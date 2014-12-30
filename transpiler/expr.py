from pyparsing import Word, alphas, nums, Forward, ZeroOrMore, Or, Literal, Group, Regex
from sympy import *
from common import *
import hypergraph
import logging


class exprParser:
    @staticmethod
    def parse(expression, equation=False, subs=dict(), main=None, returnVars=False):
        if not isinstance(expression,str): return expression

        varSet = set()

        lparen = Literal("(").suppress()
        rparen = Literal(")").suppress()
        equal = Literal("=").suppress()
        dot = Literal(".")
        spec = {
            "E": exp(1),
            "Pi": pi
        }

        def getSymbol(s):
            varSet.add(s) 
            if s in subs: s = subs[s]
            return symbols(s)

        integer = Word(nums).setParseAction( lambda t: [ int(t[0]) ] )
        decimal = Regex("[0-9]+\.[0-9]").setParseAction( lambda t: [float(t[0])])
        special = Regex("[A-Z][a-zA-Z]*").setParseAction( lambda t: [spec[t[0]]])
        var = Regex("[a-z][a-zA-Z]*").setParseAction( lambda t: [getSymbol(t[0])])
        prop = Regex("[a-z][a-zA-Z]*\.[a-z][a-zA-Z]*").setParseAction( lambda t: [getSymbol(t[0])])
        ref = Regex("\{[0-9]+\}").setParseAction( lambda t: [getSymbol(t[0])])

        opn = {
            "+": (lambda a,b: a+b ),
            "-": (lambda a,b: a-b ),
            "*": (lambda a,b: a*b ),
            "/": (lambda a,b: a/b ),
            "^": (lambda a,b: a**b )
        }
        ops = set(opn.keys())
        def opClean(t):
            if len(t)==1: return t
            return opClean([opn[t[1]](t[0],t[2])]+t[3:])

        if main is not None:
            def treeCompute(p):
                try:
                    split = p.split(".")
                    g = main.getNode(split[0])
                    comp = g.treeCompute(g.graph.getNode(split[1]))
                    res = solve(comp,symbols(p))
                    return res[0]
                except Exception as e:
                    logging.exception(e)
                    print("Error with tree Compute: ")
            prop = prop.setParseAction( lambda t: [treeCompute(t[0])])

        expr = Forward()
        paren = (lparen + expr + rparen).setParseAction( lambda s,l,t: t)
        atom = paren | decimal | integer | ref | prop | special | var
        multExpr = (atom + ZeroOrMore( Word("*/") + atom)).setParseAction( lambda s,l,t: opClean(t))
        expr << (multExpr + ZeroOrMore( Word("+-") + multExpr)).setParseAction( lambda s,l,t: opClean(t))
        equality = (expr + equal + expr).setParseAction( lambda s,l,t: Eq(t[0],t[1]) )

        if equation: res = equality.parseString(expression)[0]
        else: res = expr.parseString(expression)[0]

        if returnVars: return varSet
        else: return res

    @staticmethod
    def solve(equations, goal, subs=dict()):
        eq = [exprParser.parse(e, equation=True, subs=subs) for e in equations]
        if type(goal.graph) is hypergraph.Subgraph: g = goal.graph.name+"."+goal.name
        else: g = goal.name
        gs = symbols(g)
        res = solve(eq,dict=True)
        lres = [Eq(x,y) for x,y in res[-1].items()]
        fres = solve(lres,gs)
        return fres[gs]
