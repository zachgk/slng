import string

class Composer:

    def __init__(self):
        self.var = -1
        self.refs = 0
        self.imports = ""
        self.outputs = []
        self.includes = set()
        self.files = dict()

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

    def getFile(self, filename, io):
        if filename not in self.files: 
            self.files[filename] = (self.varDispenser(),io)
        return self.files[filename]

    def output(self, source, s):
        print(s)
        self.outputs.append(source + " << " + str(s) + " << endl")

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
            return "".join([line(f[1] + " " + f[0] + "('" + v + "')") for v,f in files.items()])
        def lines(l):
            return "".join([line(s) for s in l])
        def block(head,body):
            return head+"{\n"+body+"}"

        c = ""
        c+= forceLines(self.includes)
        c+= line("using namespace std")
        main = fileDeclarations(self.files) + lines(self.outputs) + line("return 0")
        c+= block("int main()",main)
        return c

    def composeFile(self, filename):
        with open(filename, 'w') as f:
            f.write(self.compose())
