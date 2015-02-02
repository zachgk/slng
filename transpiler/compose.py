import string
from sympy import *
from common import *
from expr import *

class Composer:

    def __init__(self):
        self.var = -1
        self.refs = 0
        self.temps = 0
        self.imports = ""
        self.outputs = []
        self.includes = set()
        self.files = dict()
        self.fileInputStreams = dict()
        self.refVars = dict()

    def include(self, s):
        self.includes.add("#include " + s)

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

    def getFile(self, filename, io):
        if filename not in self.files: 
            self.files[filename] = (self.varDispenser(),io)
        return self.files[filename]

    def fileRead(self, filename, operation):
        self.fileInputStreams[f[0]].append(operation)
        return r
    
    def inputFile(self, filename, expressions):
        self.include("<iostream>")
        self.include("<fstream>")
        f = self.getFile(filename, "ifstream")
        if f[0] not in self.fileInputStreams:
            self.fileInputStreams[f[0]] = list()

    def readFile(self, operation):
        r = self.refDispenser()
        operation['ref'] = r
        v = self.varDispenser()
        self.refVars[r] = v
        return r, operation

    def readNumber(self):
        return {"type":"single"}
    
    def readUntil(self, terminator):
        self.include("<vector>")
        return {"type":"terminated","terminator":terminator}

    def readOver(self, elements):
        return {"type":"end", "elements": elements}

    def expression(self, expr):
        if isinstance(expr,Mul):
            return '*'.join([self.expression(e) for e in expr.as_ordered_factors()])
        elif isinstance(expr,Pow):
            self.include("<math.h>")
            e = expr.as_base_exp()
            return 'pow('+self.expression(e[0])+','+self.expression(e[1])+')'
        elif isinstance(expr,Integer):
            return str(expr)
        elif isinstance(expr,Symbol):
            s = expr.name
            if refExpr.match(s):
                return self.refVars[s]
            else:
                Error('Invalid symbol in output expression: ' + s)
        elif isinstance(expr, SetLength):
            return self.refVars[expr.args[0].name] + '.size()';
        elif isinstance(expr, SetSummation):
            self.include("<numeric>")
            s = self.refVars[expr.args[0].name]
            return "accumulate(" + s + ".begin()," + s + ".end(),0)"
        elif expr == pi:
            self.include("<math.h>")
            return 'M_PI'
        elif expr == S.Half:
            return '.5'
        else:
            Error("Unknown composed expression type: " + str(type(expr)))

    def output(self, source, s):
        self.outputs.append(source + " << " + self.expression(s) + " << endl")

    def standardOutput(self, s):
        self.include("<iostream>")
        self.output("cout",s)

    def fileOutput(self, filename, s):
        self.include("<iostream>")
        f = self.getFile(filename, "ofstream")
        self.output(f[0],s)

    def compose(self):
        def line(s):
            return s+";\n"
        def forceLines(l):
            return "".join(s + "\n" for s in l)
        def fileDeclarations(files):
            return "".join([line(f[1] + " " + f[0] + '("' + v + '")') for v,f in files.items()])
        def lines(l):
            return "".join([line(s) for s in l])
        def block(head,body):
            return head+"{\n"+body+"}\n"

        c = ""
        c+= forceLines(self.includes)
        c+= line("using namespace std")
        main = fileDeclarations(self.files)
        for fileVar,inputStream in self.fileInputStreams.items():
            for item in inputStream:
                s = self.refVars[item['ref']]
                if item['type'] == 'terminated':
                    main+= line("vector<int> " + s)
                    body = line("int temp")
                    body += line(fileVar + " >> temp")
                    body += line("if(temp==" + item['terminator'][1:-1] + ") break")
                    body += line(s + ".push_back(temp)")
                    main+= block("while(true)",body)
                elif item['type'] == 'single':
                    main+= line("double " + s)
                    main+= line(fileVar + " >> " + s)
                else:
                    Error('Unhandled input type: ' + item['type'])
        main += lines(self.outputs)
        main += line("return 0")
        c+= block("int main()",main)
        return c

    def composeFile(self, filename):
        with open(filename, 'w') as f:
            f.write(self.compose())
