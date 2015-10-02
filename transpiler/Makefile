code.exe: code.cpp
	g++ code.cpp -o code.exe
	./code.exe

code.cpp: code.json *.py
	python3 transpiler.py

code.json: code.slng
	cp code.slng antlrconverter/input.slng
	$(MAKE) -C antlrconverter    
	cp antlrconverter/output.json code.json


todo:
	grep -r "TODO" --exclude-dir antlrconverter --exclude-dir pyparsing --exclude makefile
	cat TODO.txt
