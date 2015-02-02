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
    private String parseGroup(superLangParser.GroupContext group){
        if(group.SET() != null) {
           return "set";
        } else {
           return "";
        }
    }

    private JSONArray parseExprLines(List<superLangParser.ExprLineContext> lines) {
        JSONArray expressions = new JSONArray();
        for(superLangParser.ExprLineContext e:lines) {
            if(e.expression() != null) {
                expressions.add(e.expression().getText());
            } else {
                JSONObject fileLineObj = new JSONObject();
                if(e.loop().propLoop() != null) {
                    fileLineObj.put("prop", e.loop().propLoop().prop().getText());
                } else {
                    fileLineObj.put("loopVar", e.loop().objLoop().LowerName(1).getText());
                    fileLineObj.put("loopRef", e.loop().objLoop().LowerName(0).getText());
                    fileLineObj.put("expressions", parseExprLines(e.loop().objLoop().exprLine()));

                }
                expressions.add(fileLineObj);
            }
        }
        return expressions;
    }

    public JSONObject convert(InputStream is) throws Exception{
        ANTLRInputStream in = new ANTLRInputStream(is);
        superLangLexer l = new superLangLexer(in);
        superLangParser p = new superLangParser(new CommonTokenStream(l));

        final JSONObject prog = new JSONObject();
        final JSONObject types = new JSONObject();
        final JSONObject vars = new JSONObject();
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
                            property.put("group",parseGroup(bctx.dataType().group()));
                            property.put("type", typeParts[typeParts.length-1]);
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
                var.put("type", ctx.construction().UpperName().getText());
                var.put("group", parseGroup(ctx.group()));
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
                file.put("expressions", parseExprLines(ctx.exprLines().exprLine()));
                files.add(file);
            }

            @Override
            public void exitOutput(superLangParser.OutputContext ctx) {
                prog.put("output", parseExprLines(ctx.exprLines().exprLine()));
            }
        });
        p.program();
        if(types.size() > 0) prog.put("types", types);
        if(vars.size() > 0) prog.put("vars", vars);
        if(files.size() > 0) prog.put("files",files);
        return prog;
    }

}
