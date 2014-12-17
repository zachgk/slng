default:
	python3 transpiler.py
	g++ code.cpp -o code.exe
	./code.exe

convert:
	cp code.slng antlrconverter/input.slng
	$(MAKE) -C antlrconverter    
	cp antlrconverter/output.json code.json
