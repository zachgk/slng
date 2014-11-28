import sys

from antlr4 import *

from antlr.superLangLexer import superLangLexer
from antlr.superLangParser import superLangParser
 
def main(argv):
    input = FileStream(argv[1])
    lexer = MyGrammarLexer(input)
    stream = CommonTokenStream(lexer)
    parser = MyGrammarParser(stream)
    tree = parser.StartRule()

if __name__ == '__main__':
    main(sys.argv)
