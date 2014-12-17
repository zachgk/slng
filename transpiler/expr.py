from pyparsing import Word, alphas, nums, Forward, ZeroOrMore, Or, Literal, Group, Regex
from sympy import *

class exprParser:
    @staticmethod
    def parse(expression, equation=False, subs=dict(), main=None):
        if not isinstance(expression,str): return expression
        lparen = Literal("(").suppress()
        rparen = Literal(")").suppress()
        equal = Literal("=").suppress()
        dot = Literal(".")
        spec = {
            "E": exp(1),
            "Pi": pi
        }

        def sub(s):
            if s in subs: return subs[s]
            else: return s

        integer = Word(nums).setParseAction( lambda s,l,t: [ int(t[0]) ] )
        decimal = Regex("[0-9]+\.[0-9]").setParseAction( lambda s,l,t: [float(t[0])])
        special = Regex("[A-Z][a-zA-Z]*").setParseAction( lambda s,l,t: [spec[t[0]]])
        var = Regex("[a-z][a-zA-Z]*").setParseAction( lambda s,l,t: [symbols(sub(t[0]))])
        prop = Regex("[a-z][a-zA-Z]*\.[a-z][a-zA-Z]*").setParseAction( lambda s,l,t: [symbols(t[0])])
        E = Literal("E").setParseAction( lambda s,l,t: [exp(1)] )

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
                split = p.split(".")
                g = main.getNode(split[0])
                comp = g.treeCompute(g.graph.getNode(split[1]))
                res = solve(comp,symbols(p))
                return res[0]
            prop = prop.setParseAction( lambda s,l,t: [treeCompute(t[0])])

        expr = Forward()
        paren = (lparen + expr + rparen).setParseAction( lambda s,l,t: t)
        atom = paren | decimal | integer | prop | special | var
        multExpr = (atom + ZeroOrMore( Word("*/") + atom)).setParseAction( lambda s,l,t: opClean(t))
        expr << (multExpr + ZeroOrMore( Word("+-") + multExpr)).setParseAction( lambda s,l,t: opClean(t))
        equality = (expr + equal + expr).setParseAction( lambda s,l,t: Eq(t[0],t[1]) )

        if equation: return equality.parseString(expression)[0]
        else: return expr.parseString(expression)[0]

    @staticmethod
    def solve(equations, goal, subs=dict()):
        eq = [exprParser.parse(e, equation=True, subs=subs) for e in equations]
        g = goal.graph.name+"."+goal.name
        gs = symbols(g)
        res = solve(eq,dict=True)
        gres = [r[gs] for r in res]
        if len(gres) == 1: return Eq(gres[0],gs)
        return Eq(gres[-1],gs)
