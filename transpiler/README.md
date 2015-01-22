# Installation
There are two major components, the main python component and the antlrconverter.  Before using the antlrconverter, you have to build it using "mvn install" inside it's directory.  

# Running
The code to be run goes inside the /transpiler/code.slng file.  After that, use "make all" in order to transpile and run the code.

# Components
antlrconverter - Converts code.slng into code.json for more computer readable alternative to code
transpiler.py - Main transpiling file.  It contains most code for directly interpreting the code.json file and uses the other python files
common.py - Some common functions used between the various files
expr.py - Contains the pyparsing grammar used to handle expressions
hypergraph.py - Contains the main hypergraph code and various hypergraph functions
compose.py - Implements most of the language specific output code and methods
