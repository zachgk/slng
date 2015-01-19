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
    | fileDeclaration
    | NL
    ;

typeDeclaration
    : TYPE SPACE UpperName (INDENT bindingDeclaration* DEDENT)?;

varDeclaration
    : (LET SPACE)? LowerName EQUALS construction NL;

fileDeclaration
    : FILE SPACE (UpperName SPACE)+ filename INDENT (fileLine NL)* DEDENT;

fileLine
    : (expression | loop);

output
    : OUTPUT INDENT (expression NL)* DEDENT;
    
bindingDeclaration
    : LowerName COLON (expression | dataType)  NL;

assignmentDeclaration
    : LowerName EQUALS (expression | construction);

construction
    : UpperName params;

params
    : OPEN_PAREN (assignmentDeclaration (COMMA assignmentDeclaration)* )? CLOSE_PAREN;

expression
    : (prop | INT | PLUS | TIMES | MINUS | DIVIDE | POWER | OPEN_PAREN | CLOSE_PAREN | LowerName | UpperName | STRING )+;

loop
    : OPEN_SQUARE prop CLOSE_SQUARE;

dataType
    : (SET SPACE)? (NUMBER | VECTOR);

prop
    : LowerName DOT LowerName;

filename
    : word (DOT word)+;

word
    : UpperName | LowerName;

STRING: '"' [-0-9a-zA-Z: ]* '"';
LET: 'Let';
TYPE: 'Type';
NUMBER: 'Number';
VECTOR: 'Vector';
OUTPUT: 'Output';
FILE: 'File';
SET: 'Set';

TIMES: '*';
PLUS: '+';
DIVIDE: '/';
MINUS: '-';
POWER: '^';

OPEN_PAREN: '(';
CLOSE_PAREN: ')';
OPEN_SQUARE: '[';
CLOSE_SQUARE: ']';
DOT: '.';

EQUALS: ' '* '=' ' '*;
COLON: ' '* ':' ' '*;
COMMA: ' '* ',' ' '*;
SPACE: ' ';

UpperName
    : UPPER_CHAR CHAR*;

LowerName
    : LOWER_CHAR CHAR*;

INT
    : DIGIT+;


fragment UPPER_CHAR: [A-Z];
fragment LOWER_CHAR: [a-z];
fragment CHAR: [a-zA-Z];
fragment DIGIT: [0-9];
