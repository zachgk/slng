/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

grammar superLang;

tokens { INDENT, DEDENT}

@lexer::header {
    import com.yuvalshavit.antlr4.DenterHelper;
}

@lexer::members {
    private final DenterHelper denter = new DenterHelper(NL, superLangParser.INDENT, superLangParser.DEDENT) {
        @Override
        public Token pullToken() {
            return superLangLexer.super.nextToken();
        }
    };

    @Override
    public Token nextToken() {
        return denter.nextToken();
    }
}
NL: ('\r'? '\n' ' '*);

program
    : statement+ EOF;

statement
    : typeDeclaration
    | varDeclaration
    | output
    | NL
    ;

typeDeclaration
    : TYPE SPACE UpperName (INDENT bindingDeclaration* DEDENT)?;

varDeclaration
    : (LET SPACE)? LowerName EQUALS construction NL;

output
    : OUTPUT SPACE expression NL;
    
bindingDeclaration
    : LowerName COLON (expression | dataType)  NL;

assignmentDeclaration
    : LowerName EQUALS (expression | construction);

construction
    : UpperName params;

params
    : OPEN_PAREN (assignmentDeclaration (COMMA assignmentDeclaration)* )? CLOSE_PAREN;

expression
    : (INT | PLUS | TIMES | MINUS | DIVIDE | POWER | LowerName | UpperName | prop)+;

dataType
    : NUMBER | VECTOR;

prop
    : LowerName DOT LowerName;

LET: 'Let';
TYPE: 'Type';
NUMBER: 'Number';
VECTOR: 'Vector';
OUTPUT: 'Output';

TIMES: '*';
PLUS: '+';
DIVIDE: '/';
MINUS: '-';
POWER: '^';

OPEN_PAREN: '(';
CLOSE_PAREN: ')';
DOT: '.';

EQUALS: ' '* '=' ' '*;
COLON: ' '* ':' ' '*;
COMMA: ' '* ',' ' '*;
SPACE: ' ';

UpperName
    : UPPER_CHAR CHAR+;

LowerName
    :CHAR+;

INT
    : DIGIT+;

fragment UPPER_CHAR: [A-Z];
fragment CHAR: [a-zA-Z];
fragment DIGIT: [0-9];
