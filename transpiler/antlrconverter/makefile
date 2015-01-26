CONVERTER = target/antlrconverter-1.0-SNAPSHOT-jar-with-dependencies.jar input.slng

output.json: $(CONVERTER) input.slng
	java -jar $(CONVERTER)

$(CONVERTER):
	mvn install

generate:
	mvn generate-sources
