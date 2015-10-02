import string
from sympy import *
from common import *
from expr import *


    

def compose(collector):
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

    def line(s):
        return s+";\n"
    def forceLines(l):
        return "".join(s + "\n" for s in l)
    def lines(l):
        return "".join([line(s) for s in l])
    def block(head,body):
        return head+"{\n"+body+"}\n"
    def include(s):
        return "#include " + s + "\n"

    def inputStream(stream, var):
        total = ""
        nonlocal includes, collector
        for item in stream:
            s = collector.refVars[item['ref']]
            if item['type'] == 'terminated':
                includes.add("<vector>")
                total+= line("vector<int> " + s)
                body = line("int temp")
                body += line(var + " >> temp")
                body += line("if(temp==" + item['terminator'][1:-1] + ") break")
                body += line(s + ".push_back(temp)")
                total+= block("while(true)",body)
            elif item['type'] == 'single':
                total+= line("double " + s)
                total+= line(var + " >> " + s)
            elif item['type'] == 'end':
                sub = inputStream(item['elements'], var)
                Error("END")
                total+=("while(!"+var+".eof())",body);
            else:
                Error('Unhandled input type: ' + item['type'])
        return total

    fileDeclarations = ""
    main = ""
    includes = set()
    for name, stream in collector.inputStreams.items():
        if name == "standard":
            var = "cin"
            includes.add("<iostream>")
        else:
            var = collector.varDispenser()
            fileDeclarations+=line('ifstream ' + var + '("' + name + '")')
            includes.add("<iostream>")
            includes.add("<fstream>")
        inputStream(stream, var)
    for name, outputStream in collector.outputStreams.items():
        if name == "standard":
            var = "cout"
            includes.add("<iostream>")
        else:
            var = collector.varDispenser()
            fileDeclarations+=line('ofstream ' + var + '("' + name + '")')
            includes.add("<iostream>")
            includes.add("<fstream>")
        for item in outputStream:
            pass
    Error("outputs")
    main += line("return 0")
    c = ""
    c+= "".join([include(i) for i in includes])
    c+= line("using namespace std")
    c+= block("int main()",main)
    return c
