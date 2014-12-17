class Composer:

    def __init__(self):
        self.imports = ""
        self.outputs = []
        self.includes = set()

    def include(self, s):
        self.includes.add("#include " + s)

    def output(self, s):
        self.include("<iostream>")
        self.outputs.append("cout << " + str(s) + " << endl")

    def compose(self):
        def line(s):
            return s+";\n"
        def forceLines(l):
            return "".join(s + "\n" for s in l)
        def lines(l):
            return "".join([line(s) for s in l])
        def block(head,body):
            return head+"{\n"+body+"}"

        c = ""
        c+= forceLines(self.includes)
        c+= line("using namespace std")
        main = lines(self.outputs) + line("return 0")
        c+= block("int main()",main)
        return c

    def composeFile(self, filename):
        with open(filename, 'w') as f:
            f.write(self.compose())
