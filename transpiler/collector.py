import string
from sympy import *
from common import *
from expr import *

class Collector:

    def __init__(self):
        self.var = -1
        self.refs = 0
        self.temps = 0
        self.imports = ""
        self.files = dict()
        self.inputStreams = dict()
        self.outputStreams = dict()
        self.refVars = dict()

    def varDispenser(self):
        def char(n):
            if n<26: return chr(n+97)
            return char(int(n/26))+chr(n%26+97)
        self.var+=1
        return char(self.var) 

    def refDispenser(self):
        self.refs+=1
        return "{" + str(self.refs) + "}"

    def tempDispenser(self):
        self.temps+=1
        return "<" + str(self.temps) + ">"

    def inputFile(self, filename, expressions):
        self.inputStreams[filename] = expressions

    def readFile(self, operation):
        r = self.refDispenser()
        operation['ref'] = r
        v = self.varDispenser()
        self.refVars[r] = v
        return r, operation

    def readNumber(self):
        return {"type":"single"}
    
    def readUntil(self, terminator):
        return {"type":"terminated","terminator":terminator}

    def readOver(self, elements):
        return {"type":"end", "elements": elements}

    def outExpr(self, expr):
        return {"type":"expr", "expr":expr}

    def outOver(self, elements):
        return {"type":"end", "elements": elements}

    def outputFile(self, expressions):
        self.outputStreams[filename] = expressions

    def outputStandard(self, expressions):
        self.outputStreams["standard"] = expressions

