/**
 * Created by Zach Kimberg on 11/29/14.
 */

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import org.antlr.v4.runtime.*;
import org.apache.commons.lang.StringUtils;

import java.io.InputStream;
import java.util.List;

public class Converter {
    public JSONObject convert(InputStream is) throws Exception{
        ANTLRInputStream in = new ANTLRInputStream(is);
        superLangLexer l = new superLangLexer(in);
        superLangParser p = new superLangParser(new CommonTokenStream(l));

        final JSONObject prog = new JSONObject();
        final JSONObject types = new JSONObject();
        final JSONObject vars = new JSONObject();
        final JSONArray output = new JSONArray();
        final JSONArray files = new JSONArray();

        p.addParseListener(new superLangBaseListener() {

            @Override
            public void exitTypeDeclaration(superLangParser.TypeDeclarationContext ctx) {
                JSONObject type = new JSONObject();
                String name = ctx.UpperName().getText();
                type.put("type", name);
                List<superLangParser.BindingDeclarationContext> bindings = ctx.bindingDeclaration();
                if(bindings.size() > 0) {
                    JSONArray properties = new JSONArray();
                    for(superLangParser.BindingDeclarationContext bctx : bindings) {
                        JSONObject property = new JSONObject();
                        property.put("binding",bctx.LowerName().getText());
                        if(bctx.expression() != null) property.put("expression",bctx.expression().getText());
                        if(bctx.dataType() != null){
                            String[] typeParts = StringUtils.split(bctx.dataType().getText());
                            if(typeParts.length == 1) {
                                property.put("type",typeParts[0]);
                            } else {
                                property.put("group",typeParts[0]);
                                property.put("type",typeParts[1]);
                            }
                        }
                        properties.add(property);
                    }
                    type.put("properties",properties);
                }
                types.put(name,type);
            }

            @Override
            public void exitVarDeclaration(superLangParser.VarDeclarationContext ctx) {
                JSONObject var = new JSONObject();
                String name = ctx.LowerName().getText();
                var.put("name",name);
                var.put("name", ctx.construction().UpperName().getText());
                JSONObject expressions = new JSONObject();
                for (superLangParser.AssignmentDeclarationContext param : ctx.construction().params().assignmentDeclaration()) {
                    expressions.put(param.LowerName().getText(),param.expression().getText());
                }
                var.put("expressions",expressions);
                vars.put(name,var);
            }

            @Override
            public void exitFileDeclaration(superLangParser.FileDeclarationContext ctx) {
                JSONObject file = new JSONObject();
                JSONArray expressions = new JSONArray();
                file.put("filename",ctx.filename().getText());
                file.put("type",ctx.UpperName(0).getText());
                file.put("input",true);
                file.put("output",true);
                for(int i=1; i<ctx.UpperName().size(); i++){
                    String t = ctx.UpperName(i).getText();
                    switch(t) {
                        case "Input":
                            file.put("output",false);
                            break;
                        case "Output":
                            file.put("input",false);
                            break;
                        default:
                            file.put(t,true);
                    }
                }
                for(superLangParser.FileLineContext e:ctx.fileLine()) {
                    if(e.expression() != null) {
                        expressions.add(e.expression().getText());
                    } else {
                        JSONObject fileLineObj = new JSONObject();
                        fileLineObj.put("prop", e.loop().prop().getText());
                        expressions.add(fileLineObj);
                    }
                }
                file.put("expressions",expressions);
                files.add(file);
            }

            @Override
            public void exitOutput(superLangParser.OutputContext ctx) {
                for(superLangParser.ExpressionContext o:ctx.expression()) {
                    output.add(o.getText());
                }
            }
        });
        p.program();
        if(types.size() > 0) prog.put("types", types);
        if(vars.size() > 0) prog.put("vars", vars);
        if(output.size() > 0) prog.put("output",output);
        if(files.size() > 0) prog.put("files",files);
        return prog;
    }
}
