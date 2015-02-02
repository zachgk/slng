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
    : (LET SPACE)? LowerName EQUALS group construction NL;

fileDeclaration
    : FILE SPACE (UpperName SPACE)+ filename INDENT exprLines DEDENT;

exprLines
    : exprLine (NL exprLine)* NL?;

exprLine
    : (expression | loop);

output
    : OUTPUT INDENT exprLines DEDENT;
    
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
    : propLoop | objLoop;

propLoop
    : OPEN_SQUARE prop CLOSE_SQUARE;

objLoop
    : OPEN_SQUARE LowerName SPACE IN SPACE LowerName CLOSE_SQUARE INDENT (exprLine NL)* DEDENT;

dataType
    :  group (NUMBER | VECTOR);

group
    : (SET SPACE)?;

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
IN: 'In';

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
