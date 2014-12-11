# Slng

## Examples
Contains various examples of potential usage of slng.  The examples are not necessarily completed.

## Transpiler
The transpiler converts from slng.

The first step is to convert it into a json format using the antlrconverter.  To set up the antlrconverter, run "make rebuild" inside that folder.  After that, running make inside the transpiler folder will convert code.slng into the corresponding code.json.  

The main transpiler code is inside transpiler.py.  
